import unittest
import tempfile
import os

import coverage
import yaml

from main import Assembler


class TestAssembler(unittest.TestCase):

    def setUp(self):
        self.input_file = tempfile.NamedTemporaryFile(delete=False)
        self.binary_file = tempfile.NamedTemporaryFile(delete=False)
        self.log_file = tempfile.NamedTemporaryFile(delete=False)
        self.input_file.close()
        self.binary_file.close()
        self.log_file.close()

    def tearDown(self):
        os.remove(self.input_file.name)
        os.remove(self.binary_file.name)
        os.remove(self.log_file.name)

    def test_parse_word_valid(self):
        assembler = Assembler(self.input_file.name, self.binary_file.name, self.log_file.name)
        assembler.parse_word("CONST_LOAD 1 2 3")
        self.assertEqual(assembler.instructions, [(1, 2, 3, None)])

    def test_parse_word_invalid_command(self):
        assembler = Assembler(self.input_file.name, self.binary_file.name, self.log_file.name)
        with self.assertRaises(ValueError) as context:
            assembler.parse_word("INVALID 1 2 3")
        self.assertIn("The command INVALID is not recognized", str(context.exception))

    def test_run(self):
        with open(self.input_file.name, 'w') as f:
            f.write("CONST_LOAD 1 0 1\nMEMORY_WRITE 2 0 0\nCONST_LOAD 1 4 5\nMUL 3 0 4 0\nMEMORY_READ 7 2 0")

        assembler = Assembler(self.input_file.name, self.binary_file.name, self.log_file.name)
        assembler.run()

        self.assertEqual(assembler.instructions,
                         [(1, 0, 1, None),
                          (2, 0, 0, None),
                          (1, 4, 5, None),
                          (3, 0, 4, 0),
                          (7, 2, 0, None)])

        with open(self.binary_file.name, 'r') as f:
            binary_content = f.read()
        self.assertTrue(binary_content.strip())

        with open(self.log_file.name, 'r') as f:
            log_data = yaml.safe_load(f)
        self.assertEqual(log_data, {'instruction_0': {'a': 1, 'b': 0, 'c': 1, 'd': None},
                                    'instruction_1': {'a': 2, 'b': 0, 'c': 0, 'd': None},
                                    'instruction_2': {'a': 1, 'b': 4, 'c': 5, 'd': None},
                                    'instruction_3': {'a': 3, 'b': 0, 'c': 4, 'd': 0},
                                    'instruction_4': {'a': 7, 'b': 2, 'c': 0, 'd': None}})

    def test_commit_binary(self):
        assembler = Assembler(self.input_file.name, self.binary_file.name, self.log_file.name)
        assembler.instructions = [(1, 2, 3, None)]
        assembler.commit_binary()

        with open(self.binary_file.name, 'r') as f:
            binary_content = f.read()
        self.assertTrue(binary_content.strip())

    def test_commit_log(self):
        assembler = Assembler(self.input_file.name, self.binary_file.name, self.log_file.name)
        assembler.instructions = [(1, 2, 3, None), (3, 4, 5, 6)]
        assembler.commit_log()

        with open(self.log_file.name, 'r') as f:
            log_data = yaml.safe_load(f)
        self.assertEqual(log_data, {
            "instruction_0": {"a": 1, "b": 2, "c": 3, "d": None},
            "instruction_1": {"a": 3, "b": 4, "c": 5, "d": 6}
        })


if __name__ == '__main__':
    cov = coverage.Coverage()
    cov.start()

    unittest.main()

    cov.stop()
    cov.save()

    cov.html_report(directory=os.path.join(os.getcwd(), "coverage_report"))
