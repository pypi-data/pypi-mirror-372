from typing import Tuple, List
import pytest

import feyn
import unittest

from . import quickmodels
from feyn._selection import _canonical_compare


class TestPruning(unittest.TestCase):
    def setUp(self):
        self.test_model = quickmodels.get_unary_model(["bmi"], "sex")
        self.test_models = [self.test_model] * 3

    def test_duplicates_are_pruned(self):
        hashset = set(hash(m) for m in self.test_models)
        pruned = feyn.prune_models(self.test_models)
        self.assertEqual(len(pruned), len(hashset))

    def test_keeping_no_more_than_n_models(self):
        unique_models = quickmodels.get_n_unique_models(20)
        pruned_models = feyn.prune_models(unique_models, keep_n=5)
        self.assertEqual(5, len(pruned_models))


class TestCanonicalCompare(unittest.TestCase):
    def setUp(self):
        self.test_model = quickmodels.get_simple_binary_model(["x", "y"], output="z")
        self.next_model = quickmodels.get_simple_binary_model(["x", "z"], output="y")

    def test_canonical_compare(self):

        with self.subTest("Canonically comparing the same model should return true"):
            models = [self.test_model] * 2
            actual = _canonical_compare(models[0], models[1])
            self.assertTrue(actual)

        with self.subTest("Canonically comparing different models should return False"):
            models = [self.test_model, self.next_model]
            actual = _canonical_compare(models[0], models[1])
            self.assertFalse(actual)
