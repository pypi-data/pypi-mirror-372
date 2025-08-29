import unittest

import numpy as np
import pandas as pd

from feyn.metrics._normalization import normalized_mi


class TestNormalization(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.data_dict = {
            "x": np.random.random(4),
            "y": np.random.random(4),
        }
        ix = [1, 2, 3, 4]
        self.df = pd.DataFrame(self.data_dict, index=ix)

    def test_redundancy(self):
        expected = 0.3836885465963443
        actual = normalized_mi(self.df.x, self.df.y, method="redundancy")

        self.assertAlmostEqual(actual, expected)

        expected = 1.0
        actual = normalized_mi(self.df.x, self.df.x, method="redundancy")

        self.assertAlmostEqual(actual, expected)

    def test_normalised(self):
        expected = 0.3836885465963443
        actual = normalized_mi(self.df.x, self.df.y, method="norm")

        self.assertAlmostEqual(actual, expected)

        expected = 1.0
        actual = normalized_mi(self.df.x, self.df.x, method="norm")

        self.assertAlmostEqual(actual, expected)

    def test_total_correlation(self):
        expected = 0.3836885465963443
        actual = normalized_mi(self.df.x, self.df.y, method="total_correlation")

        self.assertAlmostEqual(actual, expected)

        expected = 1.0
        actual = normalized_mi(self.df.x, self.df.x, method="total_correlation")

        self.assertAlmostEqual(actual, expected)
