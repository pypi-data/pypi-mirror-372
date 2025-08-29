import unittest
import logging

import pandas as pd
import numpy as np

from feyn.metrics._spearman import _rankdata
from feyn.metrics import get_spearmans_correlations
from test.quickmodels import get_simple_binary_model


class TestSpear(unittest.TestCase):
    def setUp(self):
        self.data_dict = {
            "z": np.random.random(5),
            "y": np.random.random(5),
            "x": np.random.random(5),
        }
        self.df = pd.DataFrame(self.data_dict)
        self.model = get_simple_binary_model(["x", "y"], "z")

    def test_rankdata(self):
        test_ls = np.array([10, 14, 14, 6, 7, 7, 12, 7])
        actual = np.array([5.0, 7.5, 7.5, 1.0, 3.0, 3.0, 6.0, 3.0])

        rnk_test_ls = _rankdata(test_ls)

        for i in range(len(test_ls)):
            assert rnk_test_ls[i] == actual[i]

    def test_get_spearmans_correlations(self):
        corr = get_spearmans_correlations(self.model, self.df)

        self.assertIsNotNone(corr)
        self.assertEqual(
            len(corr),
            len(self.model),
            "Should return a correlation value for each node in the model",
        )

    def test_get_spearmans_correlations_data_validation(self):
        self.df.drop("x", axis=1, inplace=True)

        with self.assertRaises(ValueError) as ex:
            get_spearmans_correlations(self.model, self.df)

        self.assertEqual(str(ex.exception), "Input 'x' not found in data.")

    def test_get_spearmans_correlations_deprecation_warning(self):
        with self.assertLogs("feyn.metrics._metrics", logging.WARNING) as logs:
            get_spearmans_correlations(self.model, self.data_dict)

            self.assertTrue(
                any(["Deprecation: using Iterables" in log for log in logs.output])
            )
