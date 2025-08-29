import unittest

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .. import quickmodels

from feyn.plots._model_response import (
    _determine_fixed_values,
    _cleanse_fixed_values,
    _inputs_not_by_or_in_fixed,
    _input_constraints_to_their_value_combinations,
    _expand_fixed_value_combinations,
    _determine_by_input,
    _determine_max_char_len,
    _legend_table,
    _determine_legend,
    _determine_spacing_of_cols,
    _get_data_ranges,
    _set_partials_data,
    _set_top_hist_data,
    _set_right_hist_data,
    _get_histogram_data,
    _get_histogram_bin_width,
    plot_model_response_1d,
)


class TestPlotResponse1d(unittest.TestCase):
    def setUp(self) -> None:
        self.data_4inputs = {
            "x1": [0, 1, 2, 3, 4, 5],
            "x2": [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "x3": [10, 11, 12, 13, 14, 15],
            "cat": ["apples", "apples", "pears", "oranges", "oranges", "apples"],
        }

        self.data_3inputs = self.data_4inputs.copy()
        self.data_3inputs.pop("x3")
        self.cat_list = ["cat"]
        self.by = "x2"

    def test_determine_fixed_values(self):

        with self.subTest("Assigns median if fixed is none and more than 3 keys"):
            fixed = None
            expected = {"x1": [2.5], "x3": [12.5], "cat": "apples"}
            actual = _determine_fixed_values(
                pd.DataFrame(self.data_4inputs), self.by, fixed, self.cat_list
            )

            self.assertEqual(actual, expected)

        with self.subTest("Assigns median for inputs not fixed and more than 3 keys"):
            fixed = {"x1": 0}
            expected = {"x1": 0, "x3": [12.5], "cat": "apples"}
            actual = _determine_fixed_values(
                pd.DataFrame(self.data_4inputs), self.by, fixed, self.cat_list
            )

            self.assertEqual(actual, expected)

        with self.subTest(
            "Assigns top 3 occuring categories for categoricals not fixed and 3 keys"
        ):
            fixed = {"x1": 4}
            expected = {"x1": 4, "cat": ["apples"]}
            actual = _determine_fixed_values(
                pd.DataFrame(self.data_3inputs), self.by, fixed, self.cat_list
            )

            self.assertTrue(all(actual["cat"] == expected["cat"]))

        with self.subTest("Assignes quartiles for inputs not fixed and 3 keys"):
            fixed = {"cat": "apples"}
            expected = {"x1": [2.5], "cat": "apples"}
            actual = _determine_fixed_values(
                pd.DataFrame(self.data_3inputs), self.by, fixed, self.cat_list
            )
            self.assertEqual(actual, expected)

    def test_inputs_not_by_or_in_fixed(self):

        input_list = ["x1", "x2", "x3", "x4"]
        fixed = {"x1": None}
        by = "x2"
        expected = ["x3", "x4"]
        actual = _inputs_not_by_or_in_fixed(input_list, fixed, by)
        self.assertEqual(set(actual), set(expected))

    def test_cleanse_fixed_values(self):

        with self.subTest("If float is passed then turned into list"):
            fixed = {"a": 4}
            expected = {"a": [4]}
            actual = _cleanse_fixed_values(fixed)
            self.assertEqual(actual, expected)

        with self.subTest("If string is passed then turned into list"):
            fixed = {"a": "apples"}
            expected = {"a": ["apples"]}
            actual = _cleanse_fixed_values(fixed)
            self.assertEqual(actual, expected)

        with self.subTest("If list is passed then nothing is done"):
            fixed = {"a": ["b", 4, "c"]}
            expected = fixed
            actual = _cleanse_fixed_values(fixed)
            self.assertEqual(actual, expected)

    def test_expand_fixed_value_combinations(self):

        fixed = {"a": [2, 3], "b": [5, 6]}
        expected = [
            {"a": 2, "b": 5},
            {"a": 2, "b": 6},
            {"a": 3, "b": 5},
            {"a": 3, "b": 6},
        ]
        actual = _expand_fixed_value_combinations(fixed)
        self.assertEqual(actual, expected)

    def test_determine_by_input(self):

        with self.subTest(
            "If by is numerical then linspace between min and max is returned"
        ):
            expected = np.linspace(0, 0.5, 100)
            actual = _determine_by_input(
                pd.DataFrame(self.data_4inputs), self.by, is_categorical=False
            )
            self.assertTrue(all(actual == expected))

        with self.subTest("If by is categorical then all unique categories are passed"):
            expected = ["apples", "oranges", "pears"]
            actual = _determine_by_input(
                pd.DataFrame(self.data_4inputs), "cat", is_categorical=True
            )
            self.assertTrue(all(actual == expected))

    def test_get_data_ranges(self):
        with self.subTest(
            "Takes the minimum and maximum of both sets, and adds a padding"
        ):
            axis_1 = [np.arange(0, 10 + 1), np.arange(0, 5 + 1)]
            axis_2 = [np.arange(5, 15 + 1), np.arange(-5, 2 + 1)]

            # Hardcoded for illustrative purposes
            min1, max1 = 0, 15
            min2, max2 = -5, 5

            diffs = [max1 - min1, max2 - (min2)]
            paddings = [diffs[0] * 0.05, diffs[1] * 0.05]

            expecteds = (min1 - paddings[0], max1 + paddings[0]), (
                min2 - paddings[1],
                max2 + paddings[1],
            )
            actuals = _get_data_ranges(axis_1, axis_2, [])

            for expected, actual in zip(expecteds, actuals):
                self.assertAlmostEqual(expected[0], actual[0])
                self.assertAlmostEqual(expected[1], actual[1])

    def test_legend(self):
        partials = [
            {"x1": 1.23, "x2": "apples", "x3": 123.456},
            {"x1": 987, "x2": "bananas", "x3": 100100},
        ]
        with self.subTest("Partial dictionary mapped to 2d np.array"):
            expected = np.array(
                [
                    ["x1", "x2", "x3"],
                    ["1.23", "apples", "1.23e+02"],
                    ["9.87e+02", "bananas", "1e+05"],
                ]
            )
            actual = _legend_table(partials)
            np.testing.assert_array_equal(actual, expected)

        with self.subTest("Find maximum character length in 1d np.array"):
            arr = np.array(
                ["potatoes", "a really long string", "a little bit longer string"]
            )
            expected = 26
            actual = _determine_max_char_len(arr)
            self.assertEqual(expected, actual)

        with self.subTest("Determine spacing of columns in 2d np.array"):
            mat = np.array(
                [
                    ["a", "a really long string", "shorter string"],
                    ["a quite long string", "tiny", "b"],
                    ["tiny string", "another big long string", "c"],
                ]
            )
            expected = np.array([22, 26, 14])
            actual = _determine_spacing_of_cols(mat, buffer=3)
            np.testing.assert_array_equal(expected, actual)

        with self.subTest("Partial dictionary mapped to formatted strings"):
            expected_title = np.array(
                [" " * 5 + "x1" + " " * 9 + "x2" + " " * 8 + "x3" + " " * 6]
            )
            expected_labels = np.array(
                [
                    "1.23" + " " * 7 + "apples" + " " * 4 + "1.23e+02",
                    "9.87e+02" + " " * 3 + "bananas" + " " * 3 + "1e+05" + " " * 3,
                ],
            )

            actual_title, actual_labels = _determine_legend(partials, buffer=3)
            np.testing.assert_array_equal(expected_title, actual_title)
            np.testing.assert_array_equal(expected_labels, actual_labels)

    def test_set_partials_data(self):
        fixed_labels = ["banana plot"]
        x = np.linspace(0, 1, 5)
        y = 2 * x
        axes = [x, y]

        with self.subTest("Numerical data is set to initialized plots"):
            ax = plt.subplot()
            plots = [ax.plot(0, 0)[0]]
            _set_partials_data([axes], fixed_labels, plots, reverse_axis=False)

            expected_x, expected_y = x, y
            actual_x, actual_y = plots[0].get_data()
            np.testing.assert_array_almost_equal(expected_x, actual_x)
            np.testing.assert_array_almost_equal(expected_y, actual_y)

        with self.subTest("Revert the axis"):
            ax = plt.subplot()
            plots = [ax.plot(0, 0)[0]]
            _set_partials_data([axes], fixed_labels, plots, reverse_axis=True)

            expected_x, expected_y = y, x
            actual_x, actual_y = plots[0].get_data()
            np.testing.assert_array_almost_equal(expected_x, actual_x)
            np.testing.assert_array_almost_equal(expected_y, actual_y)

    def test_set_hist_data(self):
        x = np.array([0, 13, 31])
        bin_locations = np.array(
            [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0,
                16.0,
                17.0,
                18.0,
                19.0,
                20.0,
                21.0,
                22.0,
                23.0,
                24.0,
                25.0,
                26.0,
                27.0,
                28.0,
                29.0,
                30.0,
            ]
        )
        value_counts = np.array(
            [
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
            ]
        )
        bar_width = 0.85

        with self.subTest("Setting data to initialized top histogram"):
            ax = plt.subplot()
            initial_hist_data = _get_histogram_data(0)
            hist_top = ax.bar(*initial_hist_data)

            expected_x = bin_locations.copy()
            expected_height = value_counts.copy()
            expected_width = bar_width

            _set_top_hist_data(hist_top, x)

            actual_x = np.array([bar.get_x() for bar in hist_top])
            actual_height = np.array([bar.get_height() for bar in hist_top])
            actual_width = hist_top[0].get_width()
            np.testing.assert_array_almost_equal(expected_x, actual_x)
            np.testing.assert_array_equal(expected_height, actual_height)
            self.assertAlmostEqual(expected_width, actual_width)

        with self.subTest("Setting data to initialized right histogram"):
            ax = plt.subplot()
            initial_hist_data = _get_histogram_data(0)
            hist_right = ax.barh(*initial_hist_data)

            expected_y = bin_locations.copy()
            expected_width = value_counts.copy()
            expected_height = bar_width

            _set_right_hist_data(hist_right, x)

            actual_y = np.array([bar.get_y() for bar in hist_right])
            actual_width = np.array([bar.get_width() for bar in hist_right])
            actual_height = hist_right[0].get_height()
            np.testing.assert_array_almost_equal(expected_y, actual_y)
            np.testing.assert_array_equal(expected_width, actual_width)
            self.assertAlmostEqual(expected_height, actual_height)

        with self.subTest("Getting count values and bins of histogram"):
            expected_bins = bin_locations.copy()
            expected_counts = value_counts.copy()
            actual_bins, actual_counts = _get_histogram_data(x)

            np.testing.assert_array_almost_equal(expected_bins, actual_bins)
            np.testing.assert_array_equal(expected_counts, actual_counts)

        with self.subTest("Getting histogram bin width"):
            expected_width = bar_width
            actual_width = _get_histogram_bin_width(bin_locations)
            self.assertAlmostEqual(expected_width, actual_width)

    def test_validate_model_with_single_input(self):
        data = pd.DataFrame({"age": [1, 2, 3], "insurable": [0, 2, 1]})
        model = quickmodels.get_unary_model(["age"], "insurable")
        ax = plot_model_response_1d(model, data, "age")
        self.assertIsNotNone(ax)

    def test_validate_model_with_bool_values_in_target(self):
        data = pd.DataFrame({"age": [1, 2, 3], "insurable": [True, False, False]})
        model = quickmodels.get_unary_model(["age"], "insurable")
        ax = plot_model_response_1d(model, data, by="age")
        self.assertIsNotNone(ax)

    def test_model_with_boolean_inputs(self):
        data = pd.DataFrame(
            {
                "a": [True, True, False, True, False],
                "b": [True, False, True, False, False],
                "y": [1, 2, 3, 4, 5],
            }
        )
        model = quickmodels.get_simple_binary_model(["a", "b"], "y")
        ax = plot_model_response_1d(model, data, "a")
        self.assertIsNotNone(ax)

    def test_yticks_with_numerical_target(self):
        data = pd.DataFrame({"age": [-100, 0, 300], "insurable": [-1, -2, 3]})
        model = quickmodels.get_unary_model(["age"], "insurable", fname="linear:1")
        model[0].params.update({"scale": 1, "w": 1, "bias": 0})
        model[1].params.update({"scale": 1, "w": 1, "bias": 0})
        model[2].params.update({"scale": 1, "w": 1, "bias": 0})

        ax, ax_top, ax_right = plot_model_response_1d(model, data, "age")
        actual_ticks = list(ax.get_yticks())
        expected_ticks = [-150, -100, -50, 0, 50, 100, 150, 200, 250, 300, 350]
        self.assertEqual(actual_ticks, expected_ticks)

    def test_yticks_when_by_is_cat(self):
        data = pd.DataFrame(
            {"age": ["young", "middle_age", "old"], "insurable": [0, 1, 2]}
        )
        model = quickmodels.get_unary_model(["age"], "insurable", stypes={"age": "c"})
        ax, ax_top, ax_right = plot_model_response_1d(model, data, "age")
        actual_ticks = list(ax.get_yticks())
        expected_ticks = list(np.linspace(0, 1, 3))
        self.assertListEqual(actual_ticks, expected_ticks)

    def test_ylim_when_by_is_cat_with_num_categories(self):
        data = pd.DataFrame({"age": [1, 2, 3], "insurable": [0, 2, 1]})
        model = quickmodels.get_unary_model(["age"], "insurable", stypes={"age": "c"})
        ax, ax_top, ax_right = plot_model_response_1d(model, data, "age")
        actual_ylim = ax.get_ylim()
        expected_ylim = (-0.05, 1.05)
        self.assertEqual(actual_ylim, expected_ylim)


class TestPlotModelResponse1dValueErrorValidation(unittest.TestCase):
    def setUp(self):
        self.data = get_dataframe()
        self.model = quickmodels.get_unary_model(["age"], "insurable")
        self.by = "age"

    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            plot_model_response_1d(self.model, self.data, self.by)
            self.model.plot_response_1d(self.data, self.by)

    def test_data_validation(self):
        with self.subTest("ValueError if data does not contain output of model"):
            with self.assertRaises(ValueError):
                data = pd.DataFrame(
                    {
                        "age": [1, 2, 3],
                    }
                )
                plot_model_response_1d(self.model, data, self.by)

    def test_by_validation(self):
        with self.subTest("ValueError if by is not in data.columns"):
            with self.assertRaises(ValueError):
                by = "smoker"
                plot_model_response_1d(self.model, self.data, by)

        with self.subTest("ValueError if by is not in the inputs of the model"):
            with self.assertRaises(ValueError):
                by = "insurable"
                plot_model_response_1d(self.model, self.data, by)

    def test_input_constraints_validation(self):
        with self.subTest("ValueError if by is in input_contraints"):
            with self.assertRaises(ValueError):
                input_contraints = {"age": 1}
                plot_model_response_1d(self.model, self.data, self.by, input_contraints)

        with self.subTest("ValueError if input_contrains contains a name not in data"):
            with self.assertRaises(ValueError):
                input_contraints = {"banana": 1}
                plot_model_response_1d(self.model, self.data, self.by, input_contraints)


class TestPlotModelResponse1dValidation(unittest.TestCase):
    def setUp(self):
        self.data = get_dataframe()
        self.model = quickmodels.get_unary_model(["age"], "insurable")
        self.by = "age"

    def tearDown(self):
        plt.close()

    def test_model_validation(self):
        with self.assertRaises(TypeError):
            model = "hello"
            plot_model_response_1d(model, self.data, self.by)

    def test_data_validation(self):
        with self.subTest("TypeError when data is not a DataFrame"):
            with self.assertRaises(TypeError):
                data = "hello"
                plot_model_response_1d(self.model, data, self.by)

    def test_by_validation(self):
        with self.subTest("Type error if by is not a string"):
            with self.assertRaises(TypeError):
                by = 42
                plot_model_response_1d(self.model, self.data, by)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
