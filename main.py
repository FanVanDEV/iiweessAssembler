import argparse

import yaml

WORD_LENGTH = 6 * 8


def to_bin(number, bits):
    if (number > 2 ** bits - 1) or (number < 0):
        raise ValueError(f'Provided number is not valid.')
    return bin(number)[2:].zfill(bits)


def from_hex(raw_bytes):
    parsed_bytes = ' '.join(raw_bytes).replace('0x', '').replace(' ', '')

    value_map = {
        '0': '0000', '1': '0001', '2': '0010',
        '3': '0011', '4': '0100', '5': '0101',
        '6': '0110', '7': '0111', '8': '1000',
        '9': '1001', 'A': '1010', 'B': '1011',
        'C': '1100', 'D': '1101', 'E': '1110',
        'F': '1111'
    }

    return ''.join([value_map[s] for s in parsed_bytes])


class Registers:
    def __init__(self, size):
        self.registers = [0] * size

    def read(self, reg_index):
        if 0 <= reg_index < len(self.registers):
            return self.registers[reg_index]
        raise ValueError(f"Invalid register index: {reg_index}")

    def write(self, reg_index, value):
        if 0 <= reg_index < len(self.registers):
            self.registers[reg_index] = value
        else:
            raise ValueError(f"Invalid register index: {reg_index}")


class Memory:
    def __init__(self, size):
        self.memory = [0] * size
        self.size = size

    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def write(self, address, value):
        if 0 <= address < self.size:
            self.memory[address] = value
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def dump(self, start, end):
        if 0 <= start < end <= self.size:
            return self.memory[start:end]
        else:
            raise ValueError(f"Invalid memory range: {start}-{end}")


class Assembler:
    def __init__(self, input_file, binary_file, log_file):
        self.input_file = input_file
        self.binary_file = binary_file
        self.log_file = log_file

        self.instructions = []
        self.COMMANDS = {
            "CONST_LOAD": 1,
            "MEMORY_READ": 7,
            "MEMORY_WRITE": 2,
            "MUL": 3
        }

    def run(self):
        with open(self.input_file, 'r') as f:
            for word in f:
                if not word.strip():
                    continue

                self.parse_word(word.strip())

        self.commit_binary()
        self.commit_log()

    def parse_word(self, word):
        parts = word.split()
        command, a, b = parts[0].upper(), int(parts[1]), int(parts[2])
        c, d = int(parts[3]), None

        if len(parts) > 4:
            d = int(parts[4])

        if command in self.COMMANDS and self.COMMANDS[command] == a:
            self.instructions.append((a, b, c, d))
            return

        raise ValueError(f'The command {command} is not recognized')

    def commit_binary(self):
        with open(self.binary_file, 'w') as f:
            for a, b, c, d in self.instructions:
                a_field = to_bin(a, 3)
                b_field = to_bin(b, 5)
                c_field = to_bin(c, 5)

                if a == 1:
                    c_field = to_bin(c, 12)
                    instruction = a_field + b_field + c_field
                elif a == 7:
                    instruction = a_field + b_field + c_field
                elif a == 2:
                    b_field = to_bin(b, 32)
                    instruction = a_field + b_field + c_field
                elif a == 3:
                    d_field = to_bin(d, 32)

                    instruction = a_field + b_field + c_field + d_field

                instruction = instruction + "0" * (WORD_LENGTH - len(instruction))

                instruction_parts = []
                for i in range(0, len(instruction), 8):
                    part = instruction[i:i + 8]
                    hex_value = hex(int(part, 2))[2:].upper()
                    instruction_parts.append(hex_value.zfill(2))

                for byte in instruction_parts:
                    f.write(f'0x{byte} ')
                f.write('\n')

    def commit_log(self):
        log_data = {}
        for idx, (a, b, c, d) in enumerate(self.instructions):
            log_data[f"instruction_{idx}"] = {
                "a": a,
                "b": b,
                "c": c,
                "d": d
            }

        with open(self.log_file, 'w') as file:
            yaml.dump(log_data, file, default_flow_style=False)


class Entrepreneur:
    def __init__(self, binary_file, result_file, memory, registers, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range

        self.memory = memory
        self.registers = registers

        self.instructions = ''

    def run(self):
        raw_instructions = []

        with open(self.binary_file, 'r') as f:
            for word in f:
                instruction = word.strip()
                raw_instructions.append(instruction)
        self.instructions = from_hex(raw_instructions)

        self.execute()
        self.commit()

    def execute(self):
        i = 0
        while i < len(self.instructions):
            a = int(self.instructions[i:i + 3], 2)
            i += 3

            if a == 1:
                b = int(self.instructions[i:i + 5], 2)
                i += 5
                c = int(self.instructions[i:i + 12], 2)
                i += 12

                self.const_load(b, c)

                i += WORD_LENGTH - (3 + 5 + 12)

            elif a == 7:
                b = int(self.instructions[i:i + 5], 2)
                i += 5
                c = int(self.instructions[i:i + 5], 2)
                i += 5

                self.memory_read(b, c)
                i += WORD_LENGTH - (3 + 5 + 5)

            elif a == 2:
                b = int(self.instructions[i:i + 32], 2)
                i += 32
                c = int(self.instructions[i:i + 5], 2)
                i += 5

                self.memory_write(b, c)
                i += WORD_LENGTH - (3 + 32 + 5)

            elif a == 3:
                b = int(self.instructions[i:i + 5], 2)
                i += 5
                c = int(self.instructions[i:i + 5], 2)
                i += 5
                d = int(self.instructions[i:i + 32], 2)
                i += 32

                self.mul(b, c, d)
                i += WORD_LENGTH - (3 + 5 + 5 + 32)

            else:
                raise ValueError(f'The command {a} is not recognized')

    def commit(self):
        dump = self.memory.dump(*self.memory_range)
        result_data = {f"memory_cell_{i}": value for i, value in enumerate(dump)}

        with open(self.result_file, 'w') as file:
            for cell, value in result_data.items():
                file.write(f"{cell}: {value}\n")

    def const_load(self, b, c):
        self.registers.write(b, bin(c)[2:])

    def memory_read(self, b, c):
        value = self.memory.read(self.registers.read(c))
        self.registers.write(b, value)

    def memory_write(self, b, c):
        value = self.registers.read(c)
        self.memory.write(b, value)

    def mul(self, b, c, d):
        one = self.registers.read(c)
        two = self.memory.read(d)

        self.registers.write(b, bin(int(one, 2) * int(two, 2))[2:])


class VirtualMachine:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range

        self.memory = Memory(1024)
        self.registers = Registers(1024)

    def run(self):
        ent = Entrepreneur(self.binary_file, self.result_file, self.memory, self.registers, self.memory_range)
        ent.run()


def main():
    parser = argparse.ArgumentParser(description="Assembler for VM.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input file.")
    parser.add_argument("-b", "--binary", required=True, help="Path to the binary file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    parser.add_argument("-s", "--start", required=True, help="Start index for memory dump.")
    parser.add_argument("-e", "--end", required=True, help="End index for memory dump.")
    parser.add_argument("-l", "--log", required=True, help="Path to the log file.")
    args = parser.parse_args()

    assembler = Assembler(args.input, args.binary, args.log)
    assembler.run()

    vm = VirtualMachine(args.binary, args.output, (int(args.start), int(args.end)))
    vm.run()


if __name__ == "__main__":
    main()
