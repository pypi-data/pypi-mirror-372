import unittest

import pandas as pd
import numpy as np

from feyn.plots._graph_flow import plot_activation_flow

from .. import quickmodels


class TestPlotActivationFlow(unittest.TestCase):
    def setUp(self):
        self.model = quickmodels.get_unary_model(["age"], "insurable")
        self.data = pd.DataFrame({"age": [1, 2, 3], "insurable": [0, 1, 1]})
        self.sample = pd.DataFrame({"age": [12], "insurable": [0]})

    def test_when_data_is_DataFrame(self):
        self.assertIsNotNone(plot_activation_flow(self.model, self.data, self.sample))

    def test_sample_is_Series(self):
        sample = pd.Series({"age": 5})
        self.assertIsNotNone(plot_activation_flow(self.model, self.data, sample))

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            model = quickmodels.get_unary_model(["age"], "insurable")
            data = get_dataframe()
            model.plot_flow(data, data.iloc[0:1])


class TestActivationFlowValidation(unittest.TestCase):
    def setUp(self):
        self.model = quickmodels.get_unary_model(["age"], "insurable")
        self.data = get_dataframe()
        self.sample = self.data.iloc[0:1].copy()

    def test_model_validation(self):
        with self.assertRaises(TypeError):
            model = {"banana": "phone"}
            plot_activation_flow(model, self.data, self.sample)

    def test_data_validation(self):
        with self.assertRaises(TypeError):
            data = {"lost": [4, 8, 15, 16, 23, 42]}
            plot_activation_flow(self.model, data, self.sample)

    def test_sample_validation(self):
        with self.assertRaises(TypeError):
            sample = {"x": 2, "y": 0.75, "cat": "e"}
            plot_activation_flow(self.model, self.data, sample)

    def test_data_column_validation(self):
        self.data.drop("age", axis=1, inplace=True)
        with self.assertRaises(ValueError) as ex:
            plot_activation_flow(self.model, self.data, self.sample)
        self.assertEqual(str(ex.exception), "Input 'age' not found in data.")

    def test_no_output_data_column_validation(self):
        self.data.drop("insurable", axis=1, inplace=True)
        res = plot_activation_flow(self.model, self.data, self.sample)

        self.assertIsNotNone(res)

    def test_sample_input_column_validation(self):
        self.sample.drop("age", axis=1, inplace=True)
        with self.assertRaises(ValueError) as ex:
            plot_activation_flow(self.model, self.data, self.sample)
        self.assertEqual(str(ex.exception), "Input 'age' not found in data.")


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
