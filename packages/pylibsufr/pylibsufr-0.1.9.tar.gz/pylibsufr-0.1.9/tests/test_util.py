import unittest

from pylibsufr import read_sequence_file

class TestUtil(unittest.TestCase):

    def test_read_sequence_file(self):
        file = "data/inputs/2.fa"
        sequence_delimeter = ord('N')
        res = read_sequence_file(file, sequence_delimeter)
        self.assertEqual(res.seq(), b"ACGTacgtNacgtACGT$")
        self.assertEqual(res.start_positions(), [0, 9])
        self.assertEqual(res.sequence_names(), ["ABC", "DEF"])

if __name__ == '__main__':
    unittest.main()