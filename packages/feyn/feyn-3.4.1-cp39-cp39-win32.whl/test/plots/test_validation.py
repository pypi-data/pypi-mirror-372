import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

from feyn.plots._plots import (
    plot_residuals,
    plot_regression,
)
from feyn.plots._model_response_2d import plot_model_response_2d
from feyn.plots._model_summary import plot_model_summary

from ..classes import ErrorTestCase
from .. import quickmodels

def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )


class TestPartial2dValueErrorValidation(ErrorTestCase):
    def setUp(self):
        self.data = get_dataframe()

        self.model = quickmodels.get_simple_binary_model(["age","smoker"], "insurable")
        self.model_3_inputs = quickmodels.get_ternary_model(["age","smoker","children"], "insurable")

    def tearDown(self):
        plt.close()

    def test_model_number_of_inputs_validation(self):
        with self.assertRaisesAndContainsMessage(ValueError, "inputs"):
            model = quickmodels.get_unary_model(["age"], "insurable")
            plot_model_response_2d(model, self.data)

    def test_fixed(self):
        with self.subTest("ValueError when too many keys in fixed"):
            with self.assertRaisesAndContainsMessage(ValueError, "fixed"):
                fixed = {"age": 1}
                plot_model_response_2d(self.model, self.data, fixed=fixed)

        with self.subTest(
            "ValueError when fixed contains a key not in the model input"
        ):
            with self.assertRaisesAndContainsMessage(ValueError, "not an input"):
                fixed = {"fruit": 2}
                plot_model_response_2d(self.model_3_inputs, self.data, fixed=fixed)

        with self.subTest("Value Error when not enough keys in fixed"):
            with self.assertRaisesAndContainsMessage(ValueError, "non-fixed inputs should be exactly two."):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    plot_model_response_2d(self.model_3_inputs, self.data)


class TestResidualsValueValidation(ErrorTestCase):
    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            y_true = [0, 1, 0]
            y_pred = [0, 1, 0]
            plot_residuals(y_true, y_pred)

            model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
            data = get_dataframe()
            model.plot_residuals(data)

    def test_y_validation(self):
        with self.assertRaisesAndContainsMessage(ValueError, "same size"):
            y_true = [0, 1, 0]
            y_pred = [0, 1]
            plot_residuals(y_true, y_pred)


class TestRegressionValueValidation(ErrorTestCase):
    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            y_true = [0, 1, 0]
            y_pred = [0, 1, 0]
            plot_regression(y_true, y_pred)

            model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
            data = get_dataframe()
            model.plot_regression(data)

    def test_y_validation(self):
        with self.assertRaisesAndContainsMessage(ValueError, "same size"):
            y_true = [0, 1, 0]
            y_pred = [0, 1, 0, 1]
            plot_regression(y_true, y_pred)


class TestPartial2dValidation(ErrorTestCase):
    def setUp(self):
        self.data = get_dataframe()
        self.model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
        self.model_3_inputs = quickmodels.get_ternary_model(["age", "smoker", "children"], "insurable")

    def tearDown(self):
        plt.close()

    def test_model_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("model"):
            model = "hello"
            plot_model_response_2d(model, self.data)

    def test_data_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("data"):
            data = "hello"
            plot_model_response_2d(self.model, data)

    def test_resolution_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("resolution"):
            resolution = 3.4
            plot_model_response_2d(self.model, self.data, resolution=resolution)

    def test_fixed_validation(self):
        with self.subTest("TypeError when fixed is not a dictionary"):
            with self.assertRaisesTypeErrorAndContainsParam("fixed"):
                fixed = "hello"
                plot_model_response_2d(self.model, self.data, fixed=fixed)


class TestResidualsTypeValidation(ErrorTestCase):
    def tearDown(self):
        plt.close()

    def test_y_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("y_true"):
            y_true = ["a", "b", "c", "d"]
            y_pred = [0.23, 0.44, 0.56, 0.87]
            plot_residuals(y_true, y_pred)

        with self.assertRaisesTypeErrorAndContainsParam("y_pred"):
            y_true = np.linspace(0.0, 1.0, 4)
            y_pred = ["T", "F", False, True]
            plot_residuals(y_true, y_pred)

    def test_ax_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("ax"):
            ax = plt.figure()
            plot_residuals([1], [1], ax=ax)


class TestRegressionTypeValidation(ErrorTestCase):
    def setUp(self):
        self.y_true = np.linspace(0.0, 1.0, 4)
        self.y_pred = [0.23, 0.44, 0.56, 0.87]

    def tearDown(self):
        plt.close()

    def test_y_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("y_true"):
            y_true = ["a", "b", "c", "d"]
            plot_regression(y_true, self.y_pred)

        with self.assertRaisesTypeErrorAndContainsParam("y_pred"):
            y_pred = ["T", "F", False, True]
            plot_regression(self.y_true, y_pred)

    def test_ax_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("ax"):
            ax = plt.figure()
            plot_regression(self.y_true, self.y_pred, ax=ax)


class TestModelSummaryValidation(ErrorTestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(['age', 'smoker', 'children'], 'insurable')
        self.data = get_dataframe()

    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            plot_model_summary(self.model, self.data)
            self.model.plot(self.data)
            self.model.plot_signal(self.data)

    def test_model_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("model"):
            model = {"nodes": {"id": 0, "spec": "add"}}
            plot_model_summary(model, self.data)

    def test_compare_data(self):
        with self.subTest("Allows single dataframe"):
            plot_model_summary(self.model, self.data, compare_data=self.data)
        with self.subTest("Allows list of dataframes"):
            plot_model_summary(
                self.model, self.data, compare_data=[self.data, self.data]
            )
        with self.subTest("Disallows non-dataframes"):
            with self.assertRaisesTypeErrorAndContainsParam("compare_data"):
                plot_model_summary(self.model, self.data, compare_data=np.array(10))

    def test_labels_validation(self):
        with self.subTest("When labels is not iterable"):
            with self.assertRaisesTypeErrorAndContainsParam("labels"):
                labels = 42
                plot_model_summary(self.model, self.data, labels=labels)

        with self.subTest("When labels is an iterable with non-string values"):
            with self.assertRaisesTypeErrorAndContainsParam("labels"):
                labels = [4, 2]
                plot_model_summary(self.model, self.data, labels=labels)
