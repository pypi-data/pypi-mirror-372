import unittest

from feyn._program import Program


class TestProgram(unittest.TestCase):

    def test_init_invalid_program_only_output(self):
        with self.assertRaises(ValueError):
            Program([10000], qid=1)

    def test_len(self):
        with self.subTest("A single terminal has length 2"):
            ncodes = ["y", "x"] + ["add:2"]*10
            program = Program(ncodes, qid=1)
            self.assertEqual(len(program), 2)

        with self.subTest("A single unary has length 3"):
            ncodes =  ["y", "exp:1", "x"] + [0]*10
            program = Program(ncodes, qid=1)
            self.assertEqual(len(program), 3)

        with self.subTest("A single arity 2 has length 3"):
            ncodes = ["y", "add:2", "x1", "x2"] + ["add:2"]*10
            program = Program(ncodes, qid=1)
            self.assertEqual(len(program), 4)

        with self.subTest("A more complex program"):
            ncodes = ["y", "gaussian:2","gaussian:2","gaussian:1","x1","x2","x3"] + ["add:2"]*10
            program = Program(ncodes, qid=1)
            self.assertEqual(len(program), 7)

        with self.subTest("Nonsensical tail gets cut off"):
            # This part creates a completed graph from output to inputs
            valid_program = ["y", "add:2", "x1", "x2"]

            # The rest here is just remains coming from the QLattice that
            # with proper mutations in the valid program could end up geting
            # connected to the graph later.
            rest = ["x2", "x2", "y"]

            ncodes = valid_program + rest + ["add:2"]*10

            program = Program(ncodes, qid=1)
            self.assertEqual(len(program), 4)

    def test_program_parent(self):
        program = Program(["y", "exp:1", "add:2", "exp:1", "x1", "add:2", "x2", "x3"]+["add:2"]*10, qid=1)
        expected_parent_ixs = [0, 0, 1, 2, 3, 2, 5, 5]
        parent_ixs = [program.find_parent(ix) for ix in range(8)]
        self.assertEqual(expected_parent_ixs, parent_ixs)
