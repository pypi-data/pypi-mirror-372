import unittest

import pandas as pd

from .. import quickmodels
from feyn.plots._model_response_2d import plot_model_response_2d


class TestPlotResponse2d(unittest.TestCase):
    def test_plot_function_runs(self):
        """Test that the function can be run without raising an error"""
        # Setup
        num_observations = 5
        model = quickmodels.get_simple_binary_model(["a", "b"], "output")
        assert model is not None
        test_df = pd.DataFrame(
            {
                "a": list(range(num_observations)),
                "b": list(range(num_observations)),
                "output": list(range(num_observations)),
            }
        )

        # Run plot function
        ax = plot_model_response_2d(model, test_df)
        self.assertIsNotNone(ax)

        ## plot legend should just contain the actuals, since it has no fixed values
        legend_texts = ax.get_legend().texts

        self.assertEqual(1, len(legend_texts))
        self.assertEqual(legend_texts[0].get_text(), f"Actual {model.output}")

    def test_plot_legend_contains_fixed_values(self):
        num_observations = 5
        model = quickmodels.get_ternary_model(["a", "b", "fixed_value"], "output")
        assert model is not None
        test_df = pd.DataFrame(
            {
                "a": list(range(num_observations)),
                "b": list(range(num_observations)),
                "fixed_value": list(range(num_observations)),
                "output": list(range(num_observations)),
            }
        )

        # Run plot function
        ax = plot_model_response_2d(model, test_df, fixed={"fixed_value": 3})
        self.assertIsNotNone(ax)

        # The Text object is a little weird to navigate, but this should work!
        legend_texts = ax.get_legend().texts

        # Three headers, a spacer and the fixed value
        self.assertEqual(5, len(legend_texts))

        # First three objects should be a header, and describe the two scatter series
        # (just to document the different behaviour from plots with no fixed values)
        self.assertEqual("Actual output:", legend_texts[0].get_text())
        self.assertEqual("Outside fixed values", legend_texts[1].get_text())
        self.assertEqual("Within fixed values (± σ/2)", legend_texts[2].get_text())

        # One of the texts should contain the feature name and its fixed value with the std. in parenthesis
        # The text should also contain the std in parens
        std = test_df.fixed_value.std() / 2
        self.assertTrue(
            any(
                text.get_text() == f"fixed_value: {3:.2f} (± {std:.2f})"
                for text in legend_texts
            )
        )

    def test_plot_legend_does_not_show_std_for_categorical_fixed(self):
        num_observations = 5
        model = quickmodels.get_ternary_model(
            ["a", "b", "fixed_cat"], "output", stypes={"fixed_cat": "c"}
        )
        assert model is not None
        test_df = pd.DataFrame(
            {
                "a": list(range(num_observations)),
                "b": list(range(num_observations)),
                "fixed_cat": list(f"c{x}" for x in range(num_observations)),
                "output": list(range(num_observations)),
            }
        )

        # Run plot function
        ax = plot_model_response_2d(model, test_df, fixed={"fixed_cat": "c3"})
        self.assertIsNotNone(ax)

        # The Text object is a little weird to navigate, but this should work!
        legend_texts = ax.get_legend().texts

        # One of the texts should contain the feature name and its fixed value
        self.assertTrue(
            any(text.get_text() == "fixed_cat: c3" for text in legend_texts)
        )

    def test_plot_function_raises_if_needed_data_columns_not_present(self):
        # Setup
        num_observations = 5
        model = quickmodels.get_simple_binary_model(["a", "b"], "output")
        test_df = pd.DataFrame(
            {
                "b": list(range(num_observations)),
                "output": list(range(num_observations)),
            }
        )

        # Run plot function
        with self.assertRaises(ValueError) as ex:
            plot_model_response_2d(model, test_df)

        self.assertEqual(str(ex.exception), "Input 'a' not found in data.")
