import unittest
import logging

import numpy as np
import pandas as pd

from feyn.metrics import get_pearson_correlations

from test.quickmodels import get_simple_binary_model


class TestPearsonCorrelation(unittest.TestCase):
    def setUp(self):
        self.data_dict = {
            "z": np.random.random(5),
            "y": np.random.random(5),
            "x": np.random.random(5),
        }
        self.df = pd.DataFrame(self.data_dict)
        self.model = get_simple_binary_model(["x", "y"], "z")

    def test_raises_deprecation_warning_with_np_dict(self):
        with self.assertLogs("feyn.metrics._metrics", logging.WARNING) as logs:
            corr = get_pearson_correlations(self.model, self.data_dict)
            self.assertTrue(
                any(["Deprecation: using Iterables" in log for log in logs.output])
            )

        self.assertIsNotNone(corr)

    def test_works_with_pd_dataframe(self):
        corr = get_pearson_correlations(self.model, self.df)
        self.assertIsNotNone(corr)
        self.assertEqual(
            len(corr),
            len(self.model),
            "Should return a correlation value for each node in the model",
        )

    def test_data_validation(self):
        self.df.drop("x", axis=1, inplace=True)

        with self.assertRaises(ValueError) as ex:
            get_pearson_correlations(self.model, self.df)

        self.assertEqual(str(ex.exception), "Input 'x' not found in data.")
