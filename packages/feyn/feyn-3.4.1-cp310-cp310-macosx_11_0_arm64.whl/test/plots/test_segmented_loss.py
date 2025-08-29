import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from feyn.reference import ConstantModel
from feyn.plots import plot_segmented_loss

from .. import quickmodels


class TestSegmentedLoss(unittest.TestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
        self.data = pd.DataFrame(
            {"age": [1, 2, 3], "smoker": [0, 0, 1], "insurable": [0, 1, 1]}
        )

    def tearDown(self):
        plt.close()

    def test_feyn_model(self):
        ax, ax2 = plot_segmented_loss(self.model, self.data)
        self.assertIsNotNone(ax)
        self.assertIsNotNone(ax2)

    def test_reference_model(self):
        model = ConstantModel("insurable", 1)
        ax, ax2 = plot_segmented_loss(model, self.data)
        self.assertIsNotNone(ax)
        self.assertIsNotNone(ax2)

    def test_validate_provide_custom_legend_labels(self):
        ax, ax2 = plot_segmented_loss(self.model, self.data, legend=["Hello", "World"])
        self.assertIsNotNone(ax)
        self.assertIsNotNone(ax2)

        # The Text object is a little weird to navigate, but this should work!
        self.assertEqual(ax2.get_legend().texts[0].get_text(), "Hello")
        self.assertEqual(ax2.get_legend().texts[1].get_text(), "World")


class TestSegmentedLossValidation(unittest.TestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
        self.data = get_dataframe()

    def tearDown(self):
        plt.close()

    def test_by_validation(self):
        with self.subTest("When `by` is not in data"):
            with self.assertRaises(ValueError) as ex:
                by = "banana"
                plot_segmented_loss(self.model, self.data, by=by)
            self.assertEqual(str(ex.exception), "Argument `by`='banana' not in data.")

    def test_data_validation(self):
        self.data.drop("age", axis=1, inplace=True)

        with self.assertRaises(ValueError) as ex:
            plot_segmented_loss(self.model, self.data)

        self.assertEqual(str(ex.exception), "Input 'age' not found in data.")

    def test_validation_legend_count(self):
        with self.assertRaises(ValueError):
            plot_segmented_loss(self.model, self.data, legend=["Only one label"])


class TestSegmentedLossTypeErrorValidation(unittest.TestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")
        self.data = get_dataframe()

    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            plot_segmented_loss(self.model, self.data)
            self.model.plot_segmented_loss(self.data)

    def test_model_validation(self):
        with self.assertRaises(TypeError):
            model = "banana"
            plot_segmented_loss(model, self.data)

    def test_data_validation(self):
        with self.assertRaises(TypeError):
            data = {"banana": "phone"}
            plot_segmented_loss(self.model, data)

    def test_by_validation(self):
        with self.subTest("When `by` is not a string"):
            with self.assertRaises(TypeError):
                by = 42
                plot_segmented_loss(self.model, self.data, by=by)

    def test_ax_validation(self):
        with self.assertRaises(TypeError):
            ax = plt.figure()
            plot_segmented_loss(self.model, self.data, ax=ax)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
