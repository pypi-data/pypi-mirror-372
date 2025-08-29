import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .. import quickmodels

from feyn.plots import plot_pr_curve


class TestPRCurve(unittest.TestCase):
    def setUp(self):
        self.actuals = np.array([1, 0, 0, 1, 1])
        self.preds = np.array([0.6, 0.9, 0.2, 0.8, 0.2])
        self.threshold = 0.5

    def tearDown(self):
        plt.close()

    def test_plot_pr_curve(self):
        ax = plot_pr_curve(self.actuals, self.preds)
        self.assertIsNotNone(ax)

    def test_plot_pr_curve_through_classifier(self):
        model = quickmodels.get_simple_binary_model(
            ["age", "smoker"], "insurable", stypes={"insurable": "b"}
        )
        data = get_dataframe()
        model.predict = lambda data: [0.5] * len(data)
        model.plot_pr_curve(data)

    def test_plot_pr_curve_through_regressor_returns_error(self):
        model = quickmodels.get_simple_binary_model(
            ["age", "smoker"], "insurable", stypes={"insurable": "f"}
        )
        data = get_dataframe()
        model.predict = lambda data: [0.5] * len(data)

        with self.assertRaises(TypeError) as ex:
            model.plot_pr_curve(data)

        self.assertEqual(
            str(ex.exception),
            "A precision-recall curve can only be plotted for a classification model. This model is of type regression.",
        )

    def test_plot_pr_curve_w_threshold(self):
        ax = plot_pr_curve(self.actuals, self.preds, self.threshold)
        self.assertIsNotNone(ax)


class TestPRCurveValueErrorValidation(unittest.TestCase):
    def setUp(self):
        self.y_true = [True, False, True, False]
        self.y_pred = [0.85, 0.46, 0.25, 0.5]

    def tearDown(self):
        plt.close()

    def test_y_validation(self):
        with self.subTest("When y has values outside of [0, 1] interval"):
            with self.assertRaises(ValueError):
                y_true = np.arange(4)
                plot_pr_curve(y_true, self.y_pred)

            with self.assertRaises(ValueError):
                y_pred = np.arange(4)
                plot_pr_curve(self.y_true, y_pred)

        with self.subTest("When y_true has more than 2 distinct classes"):
            with self.assertRaises(ValueError):
                y_true = np.linspace(0.0, 1.0, num=4)
                plot_pr_curve(y_true, self.y_pred)

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            threshold = -1.5
            plot_pr_curve(self.y_true, self.y_pred, threshold=threshold)


class TestPRCurveTypeErrorValidation(unittest.TestCase):
    def setUp(self):
        self.y_true = [True, False, True, False]
        self.y_pred = [0.85, 0.46, 0.25, 0.5]

    def tearDown(self):
        plt.close()

    def test_ax_validation(self):
        with self.assertRaises(TypeError):
            ax = plt.figure()
            plot_pr_curve(self.y_true, self.y_pred, ax=ax)

    def test_threshold_validation(self):
        with self.subTest("When threshold is neither float or int"):
            with self.assertRaises(TypeError):
                threshold = "banana"
                plot_pr_curve(self.y_true, self.y_pred, threshold=threshold)

    def test_y_validation(self):
        with self.subTest("When y is not iterable"):
            with self.assertRaises(TypeError):
                y_true = 1
                plot_pr_curve(y_true, self.y_pred)

            with self.assertRaises(TypeError):
                y_pred = 1
                plot_pr_curve(self.y_true, y_pred)

        with self.subTest("when y is an iterable with non-float, int or bool values"):
            with self.assertRaises(TypeError):
                y_true = ["banana", "phone", "is", "weird"]
                plot_pr_curve(y_true, self.y_pred)

            with self.assertRaises(TypeError):
                y_pred = ["banana", "phone", "is", "weird"]
                plot_pr_curve(self.y_true, y_pred)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.linspace(0.0, 0.5, 5)),
            "smoker": np.linspace(0.0, 0.5, 5),
            "insurable": [0, 1, 0, 1, 0],
        }
    )
