import unittest

import numpy as np
import pandas as pd

from feyn.tools import estimate_priors


class TestPriors(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "age": np.array([20, 40, 20, 20, 40, 20]),
            "smoker": np.array([0, 1, 1, 0, 1, 0]),
            "sex": np.array(["yes", "no", "yes", "no", "yes", "no"]),
            "charges": np.array([10000, 20101, 10001, 20101, 20100, 10101]),
            "extra": np.array([0, 1, 1, 0, 1, 0]),
        })
        self.output_name = "smoker"

    def test_estimate_priors(self):
        result = estimate_priors(self.data, self.output_name)
        self.assertEqual(set(result.keys()), set(["age", "sex", "charges", "extra"]))
        self.assertTrue(self.output_name not in result)
        self.assertTrue(all(0 <= v <= 1 for v in result.values()))

    def test_estimate_priors_select_top_inputs(self):
        selected_features = estimate_priors(self.data, self.output_name)
        self.assertEqual("extra", list(selected_features.keys())[0])
