import unittest

from lark import Tree

from feyn._query import Parser


class TestFeynQueryParsing(unittest.TestCase):
    def setUp(self):
        pass

    def test_special_opcode_meanings(self):
        self.assertEqual(Parser._translate_ast(Tree("register_any", [])), "?")
        self.assertEqual(Parser._translate_ast(Tree("interact1", [])), "func:1")
        self.assertEqual(Parser._translate_ast(Tree("interact2", [])), "func:2")
        self.assertEqual(Parser._translate_ast(Tree("wildcard", [])), "_")
        self.assertEqual(Parser._translate_ast(Tree("exclude", [])), "!")

    def test_wildcard_parsing(self):
        with self.subTest("Wildcard with no parameters"):
            query = "_"
            _, qcodes = Parser.query_to_codes("out", query)
            self.assertEqual(["out", "_", 30], qcodes[:3])

        with self.subTest("Wildcard requiring input presence"):
            query = "_['x']"
            _, qcodes = Parser.query_to_codes("out", query)
            self.assertEqual(["out", "_", "x", 30], qcodes[:4])

        with self.subTest("Wildcard disallowing input presence"):
            query = "_[!'x']"
            _, qcodes = Parser.query_to_codes("out", query)
            self.assertEqual(["out", "_", "!", "x", 30], qcodes[:5])

        with self.subTest("Wildcard requesting at most 9 edges"):
            query = "_[9]"
            _, qcodes = Parser.query_to_codes("out", query)
            self.assertEqual(["out", "_", 9], qcodes[:3])

        with self.subTest("Complicated wildcard query"):
            query = "_['x', !'y', 3]"
            _, qcodes = Parser.query_to_codes("out", query)
            self.assertEqual(["out", "_", "x", "!", "y", 3], qcodes[:6])

    def test_expected_query_program(self):
        query1 = "'y' * _[!'z', 2] + 'x'"
        _, qcodes1 = Parser.query_to_codes("out", query1)

        expected_seq = ["out", "add:2", "multiply:2", "y", "_", "!", "z", 2, "x"]
        self.assertEqual(expected_seq, qcodes1[:9])

        query2 = "func('x') * log('y' + ?)"
        _, qcodes2 = Parser.query_to_codes("out", query2)

        expected_seq = ["out", "multiply:2", "func:1", "x", "log:1", "add:2", "y", "?"]
        self.assertEqual(expected_seq, qcodes2[:8])

    def test_query_complexity(self):
        n1, _ = Parser.query_to_codes("out", "func('x')")
        n2, _ = Parser.query_to_codes("out", "'x' + func('y')")
        n3, _ = Parser.query_to_codes("out", "_['x', 'y']")
        n4, _ = Parser.query_to_codes("out", "_['x', 'y', !'z']")

        self.assertEqual(n1, 2)
        self.assertEqual(n2, 4)
        self.assertEqual(n3, 2)
        self.assertEqual(n4, 2)

    def test_wildcard_complexity(self):
        with self.assertRaises(ValueError):
            Parser.query_to_codes("out", "_['x', 'y', 1]")

        try:
            Parser.query_to_codes("out", "_['x', 'y', 2]")
        except ValueError:
            self.fail("Wildcard raised unexpected ValueError.")

    def test_wildcard_inconsistency(self):
        with self.assertRaises(ValueError):
            Parser.query_to_codes("out", "_['x', !'x']")

        try:
            Parser.query_to_codes("out", "_['x', !'y']")
        except ValueError:
            self.fail("Wildcard raised unexpected ValueError.")
