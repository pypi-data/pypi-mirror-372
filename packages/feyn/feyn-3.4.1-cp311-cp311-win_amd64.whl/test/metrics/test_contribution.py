import unittest

import numpy as np
import pandas as pd

from feyn.metrics._contribution import (
    get_ranked_contributors,
    _get_parent_indices,
    _get_input_indices,
    _recurse_significance,
)
from test.quickmodels import get_simple_binary_model, get_quaternary_model

from pytest import mark


@mark.focus
class TestContribution(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.data_dict = {
            "x": [1, 2, 3, 4],
            "y": np.random.random(4),
            "z": [2, 4, 6, 8],
        }
        ix = [1, 2, 3, 4]
        self.df = pd.DataFrame(self.data_dict, index=ix)

        self.model = get_simple_binary_model(["x", "y"], "z", stypes={"y": "c"})

    def test_get_ranked_contributors(self):
        rank = get_ranked_contributors(self.model, self.df)

        self.assertEqual(rank[0], "x")
        self.assertEqual(rank[1], "y")

    def test_get_parent_indices(self):
        pidx = _get_parent_indices(self.model)
        expected = [None, 0, 1, 1]

        self.assertEqual(pidx, expected)

        complex_model = get_quaternary_model(["a", "b", "c", "d"], "z")
        pidx = _get_parent_indices(complex_model)
        expected = [None, 0, 1, 2, 3, 3, 2, 1]

        self.assertEqual(pidx, expected)

    def test_get_input_indices(self):
        pidx = _get_input_indices(self.model)
        expected = [2, 3]

        self.assertEqual(pidx, expected)

        complex_model = get_quaternary_model(["a", "b", "c", "d"], "z")
        pidx = _get_input_indices(complex_model)
        expected = [4, 5, 6, 7]

        self.assertEqual(pidx, expected)

    def test_recurse_significance(self):
        inputs = [2, 3]
        parents = [None, 0, 1, 1]
        contributions = [1, 0.5, 0.3, 0.8]

        input_1 = _recurse_significance(self.model, inputs[0], parents, contributions)
        expected = 0.15

        self.assertEqual(input_1, expected)

        input_2 = _recurse_significance(self.model, inputs[1], parents, contributions)
        expected = 0.4

        self.assertEqual(input_2, expected)
