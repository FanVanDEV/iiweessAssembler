import unittest
from unittest.mock import Mock, MagicMock
from main import Entrepreneur


class TestEntrepreneur(unittest.TestCase):
    def setUp(self):
        self.memory = Mock()
        self.memory.dump = MagicMock(return_value=[0, 0, 0, 0])
        self.memory.read = MagicMock(return_value="00000010")

        self.registers = Mock()
        self.registers.read = MagicMock(return_value="00000001")
        self.registers.write = MagicMock()

        self.binary_file = "test_binary_file.txt"
        self.result_file = "test_result_file.txt"
        with open(self.binary_file, "w") as f:
            f.write("0x10 0x01 0x02 0x03\n")

        self.memory_range = (0, 4)

    def tearDown(self):
        import os
        os.remove(self.binary_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)

    def test_const_load(self):
        entrepreneur = Entrepreneur(
            self.binary_file, self.result_file, self.memory, self.registers, self.memory_range
        )

        # Симулируем инструкцию CONST_LOAD
        entrepreneur.instructions = "001000000000001010"  # A=1, B=0, C=10
        entrepreneur.execute()

        self.registers.write.assert_called_with(0, "1010")  # C=10 в бинарном виде

    def test_memory_read(self):
        entrepreneur = Entrepreneur(
            self.binary_file, self.result_file, self.memory, self.registers, self.memory_range
        )

        # Симулируем инструкцию MEMORY_READ
        entrepreneur.instructions = "1110000100000000"  # A=7, B=1, C=0
        entrepreneur.execute()

        self.memory.read.assert_called_with("00000001")  # Регистр C=1
        self.registers.write.assert_called_with(1, "00000010")  # Записано значение 2 из памяти

    def test_memory_write(self):
        entrepreneur = Entrepreneur(
            self.binary_file, self.result_file, self.memory, self.registers, self.memory_range
        )

        # Симулируем инструкцию MEMORY_WRITE
        entrepreneur.instructions = "010000000000000000000000000000000010000000000000"  # A=2, B=1, C=0
        entrepreneur.execute()

        self.registers.read.assert_called_with(0)  # Чтение значения из регистра C
        self.memory.write.assert_called_with(1, "00000001")  # Запись значения в память

    def test_mul(self):
        entrepreneur = Entrepreneur(
            self.binary_file, self.result_file, self.memory, self.registers, self.memory_range
        )

        # Симулируем инструкцию MUL
        entrepreneur.instructions = "011000010000000010"  # A=3, B=1, C=0, D=2
        entrepreneur.execute()

        self.registers.read.assert_called_with(0)  # Чтение регистра C
        self.memory.read.assert_called_with(2)  # Чтение памяти D
        self.registers.write.assert_called_with(1, "10")  # Результат 1 * 2 = 2

    def test_commit(self):
        entrepreneur = Entrepreneur(
            self.binary_file, self.result_file, self.memory, self.registers, self.memory_range
        )

        entrepreneur.commit()

        with open(self.result_file, "r") as f:
            result_data = f.read()
        expected_output = "memory_cell_0: 0\nmemory_cell_1: 0\nmemory_cell_2: 0\nmemory_cell_3: 0\n"
        self.assertEqual(result_data, expected_output)


if __name__ == "__main__":
    unittest.main()
