import unittest

from feyn.metrics._diversity import levenshtein_distance, tree_edit_distance
from test import quickmodels


class TestDiversity(unittest.TestCase):
    def setUp(self):
        inputs = list("abcde")
        output = "output"

        # Model m5 and m6 have the same structure as the example in the paper by Zhang and Shasha 1989 on tree edit distance algorithm
        self.m1 = quickmodels.get_specific_model(inputs, output, "(inverse('a'*'b'))+'c'")
        self.m2 = quickmodels.get_specific_model(inputs, output, "('a'+'c') + 'b'")
        self.m3 = quickmodels.get_specific_model(inputs, output, "'a'+'a'")
        self.m4 = quickmodels.get_specific_model(inputs, output, "'b'*'c'")
        self.m5 = quickmodels.get_specific_model(inputs, output, "('a'*inverse('b'))+'e'")
        self.m6 = quickmodels.get_specific_model(inputs, output, "inverse('a'*'b')+'e'")

    def test_levenshtein_distance(self):
        distance = levenshtein_distance(self.m1, self.m2)
        self.assertEqual(distance, 4)

    def test_tree_edit_distance(self):
        self.assertEqual(tree_edit_distance(self.m1, self.m2), 4)
        self.assertEqual(tree_edit_distance(self.m3, self.m4), 3)
        self.assertEqual(tree_edit_distance(self.m5, self.m6), 2) # Same example as in paper
