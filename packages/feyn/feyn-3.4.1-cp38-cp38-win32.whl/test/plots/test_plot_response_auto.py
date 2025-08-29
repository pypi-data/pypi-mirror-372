import unittest

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from .. import quickmodels
from feyn.plots._auto import plot_model_response_auto
import feyn


class TestPlotResponseAuto(unittest.TestCase):
    def tearDown(self):
        plt.close()

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
        ax = plot_model_response_auto(model, test_df)
        self.assertIsNotNone(ax)
        self.assertTrue(isinstance(ax, Axes))

    def test_plots_response_1d_with_only_one_feature(self):
        test_df = pd.DataFrame(
            {
                "a": list(range(5)),
                "output": list(range(5)),
            }
        )
        model = quickmodels.get_unary_model(["a"], "output")
        axes = plot_model_response_auto(model, test_df)

        self.assertIsNotNone(axes)
        self.assertTrue(isinstance(axes, tuple))
        self.assertEqual(len(axes), 3)

    def test_plot_works_for_more_than_two_features_and_auto_fixes(self):
        num_observations = 5
        model = quickmodels.get_ternary_model(["a", "b", "c"], "output")
        assert model is not None
        test_df = pd.DataFrame(
            {
                "a": list(range(num_observations)),
                "b": list(range(num_observations)),
                "c": list(range(num_observations)),
                "output": list(range(num_observations)),
            }
        )

        # Run plot function
        ax = plot_model_response_auto(model, test_df)
        self.assertIsNotNone(ax)
        self.assertTrue(isinstance(ax, Axes))

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
        std = test_df.c.std() / 2

        for text in legend_texts:
            print(text)
        self.assertTrue(
            any(
                (
                    text.get_text() == f"a: {2:.2f} (± {std:.2f})"
                    or text.get_text() == f"b: {2:.2f} (± {std:.2f})"
                    or text.get_text() == f"c: {2:.2f} (± {std:.2f})"
                )
                for text in legend_texts
            )
        )

    def test_plot_automatically_fixes_categorical(self):
        num_observations = 5
        # model = quickmodels.get_ternary_model(["a", "b", "c"], "output")
        # assert model is not None
        test_df = pd.DataFrame(
            {
                "a": [str(i % 2) for i in range(num_observations)],
                "b": [str(i % 2) for i in range(num_observations)],
                "c": [str(i % 2) for i in range(num_observations)],
                "output": list(range(num_observations)),
            }
        )
        ql = feyn.QLattice(1)

        # Categoricals in 2d plot requires models to be trained
        models = ql.auto_run(
            test_df, "output", n_epochs=1, query_string="add('a', multiply('b', 'c'))"
        )
        model = models[0]

        # Run plot function
        ax = plot_model_response_auto(model, test_df)
        self.assertIsNotNone(ax)
        self.assertTrue(isinstance(ax, Axes))

        # The Text object is a little weird to navigate, but this should work!
        legend_texts = ax.get_legend().texts

        # Three headers, a spacer and the fixed value
        self.assertEqual(5, len(legend_texts))

        # First three objects should be a header, and describe the two scatter series
        # (just to document the different behaviour from plots with no fixed values)
        self.assertEqual("Actual output:", legend_texts[0].get_text())
        self.assertEqual("Outside fixed values", legend_texts[1].get_text())
        self.assertEqual("Within fixed values (± σ/2)", legend_texts[2].get_text())

        # One of the texts should contain the feature name and its fixed value
        for text in legend_texts:
            print(text)

        self.assertTrue(
            any(
                (
                    text.get_text() == f"a: 0"
                    or text.get_text() == f"b: 0"
                    or text.get_text() == f"c: 0"
                )
                for text in legend_texts
            )
        )
