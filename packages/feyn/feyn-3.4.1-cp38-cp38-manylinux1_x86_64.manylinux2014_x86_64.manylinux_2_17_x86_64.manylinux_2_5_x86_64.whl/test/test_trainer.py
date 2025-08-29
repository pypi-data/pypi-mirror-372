import unittest

import numpy as np
import pandas as pd

import feyn

from . import quickmodels
from feyn._qepler import qeplertrainer

class TestTrainer(unittest.TestCase):

    def test_fit_initializes_scale(self):
        model = quickmodels.get_unary_model(["input"], "y")
        # Should not raise
        losses, params = qeplertrainer.fit_models([model], pd.DataFrame({
                "input": np.array([42, 0, 100, 50]),
                "y": np.array([0.1, 0.3, 0.2, 0.9])
            }), 10000, loss="squared_error")

        input_element = params[0][2]

        self.assertEqual(input_element["scale"], .02)
        self.assertEqual(params[0][0]["scale"], 0.4)

    def test_fit_utilizes_sample_weights_for_loss(self):
        def compute_loss(sample_weights):
            model = quickmodels.get_identity_model(["input"], "y")
            model[0].params.update({"scale": 1.0, "scale_offset": 0.0, "w":1.0, "bias": 0, "detect_scale": 0, "qepler_init": 1})
            model[1].params.update({"scale": 1.0, "scale_offset": 0.0, "w":1.0, "bias": 0, "detect_scale": 0, "qepler_init": 1})

            model_losses, _ = qeplertrainer.fit_models([model], pd.DataFrame({
                    "input": np.array([10, 1]),
                    "y": np.array([2, 2])
                }), 2, sample_weights=sample_weights, loss="absolute_error")

            return model_losses[0]

        self.assertEqual(0.5, compute_loss(sample_weights=[0, 1]))
        self.assertEqual(4.0, compute_loss(sample_weights=[1, 0]))

    def test_fit_models_checks_output_stypes(self):
        regression_model = quickmodels.get_unary_model()
        classification_model = quickmodels.get_unary_model(stypes={"y": "b"})
        data = pd.DataFrame.from_dict({
            "x": np.array([1, 2, 3]),
            "y": np.array([0.3, 0.2, 0.5]),
        })

        with self.assertRaises(ValueError):
            feyn.fit_models([regression_model, classification_model], data)

        feyn.fit_models([regression_model], data)
        feyn.fit_models([classification_model], data)

    def test_fit_models_works_with_pandas_arrays(self):
        data = pd.DataFrame.from_dict({
            "x": np.array([1, 2, 3]),
            "c": np.array(list("abc")),
            "y": np.array([0.3, 0.2, 0.5]),
        })
        data = data.convert_dtypes()

        with self.subTest("Numerical model works"):
            regression_model = quickmodels.get_unary_model(inputs=["x"])
            feyn.fit_models([regression_model], data)

        with self.subTest("Categorical model works"):
            regression_model = quickmodels.get_unary_model(inputs=["c"], stypes={"c": "cat"})
            feyn.fit_models([regression_model], data)

        with self.subTest("Works with PyArrow backed string types"):
            data['c'] = data['c'].astype('string[pyarrow]')
            regression_model = quickmodels.get_unary_model(inputs=["c"], stypes={"c": "cat"})
            feyn.fit_models([regression_model], data)