import unittest
import logging

import numpy as np
import pandas as pd

from feyn.metrics import calculate_mi, get_mutual_information
from test.quickmodels import get_simple_binary_model, get_identity_model


class TestMI(unittest.TestCase):
    def setUp(self):
        self.data_dict = {
            "z": np.random.random(4),
            "y": np.array(["a", "a", "b", "b"]),
            "x": np.array([4, 3, 1, 5]),
        }
        ix = [1, 2, 3, 4]
        self.df = pd.DataFrame(self.data_dict, index=ix)
        self.model = get_simple_binary_model(["x", "y"], "z", stypes={"y": "c"})

    def test_mutual_information_np_array(self):
        actual = 0.6931471805599452
        pred = calculate_mi([self.df.x, self.df.y])

        self.assertEqual(pred, actual)

    def test_mutual_information_pd_series_num_ix_wo_0(self):
        actual = 0.6931471805599452
        pred = calculate_mi([self.df.loc[:, "x"], self.df.loc[:, "y"]])
        self.assertEqual(pred, actual)

    def test_mutual_information_cont(self):
        np.random.seed(42)
        X = np.random.random((1000,))
        Y = np.random.random((1000,))
        pred = calculate_mi([X, Y], float_bins=3)
        self.assertAlmostEqual(pred, 0, places=2)

    def test_get_mutual_informatino_identity_model(self):
        model = get_identity_model()

        x = np.random.randint(0, 10, 10)

        data = pd.DataFrame({"x": x, "y": x})

        test_mi = get_mutual_information(model, data)

        # This relies on knowing the steps in indentity_model
        actual_mi_0 = calculate_mi([x, x * 0.5 - 0.5])
        actual_mi_1 = calculate_mi([x, x])

        self.assertTrue(np.allclose(test_mi, [actual_mi_1, actual_mi_0]))

    def test_get_mutual_information_raises_deprecation_warning_with_np_dict(self):
        with self.assertLogs("feyn.metrics._metrics", logging.WARNING) as logs:
            mutual = get_mutual_information(self.model, self.data_dict)
            self.assertTrue(
                any(["Deprecation: using Iterables" in log for log in logs.output])
            )

        self.assertIsNotNone(mutual)

    def test_get_mutual_information_works_with_pd_dataframe(self):
        corr = get_mutual_information(self.model, self.df)
        self.assertIsNotNone(corr)
        self.assertEqual(
            len(corr),
            len(self.model),
            "Should return a correlation value for each node in the model",
        )

    def test_data_validation(self):
        self.df.drop("x", axis=1, inplace=True)

        with self.assertRaises(ValueError) as ex:
            get_mutual_information(self.model, self.df)

        self.assertEqual(str(ex.exception), "Input 'x' not found in data.")
