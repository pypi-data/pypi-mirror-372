import unittest

from feyn.plots._model_summary import _get_corr_func, _sanitize_data_inputs, _create_labels
from feyn.metrics import get_mutual_information, get_spearmans_correlations, get_pearson_correlations

import pandas as pd
import numpy as np

class TestModelSummary(unittest.TestCase):

    def test_create_labels(self):
        with self.subTest('Assigns default labels if None'):
            actual = _create_labels(None, [])
            expected = ['Training Metrics', 'Test']
            self.assertEqual(expected, actual)

        with self.subTest('Assigns default labels if None and adds numbered labels for additional dataframes.'):
            dataframes = ["Fake dataframe", "Fake dataframe 2", "Fake dataframe 3"]
            actual = _create_labels(None, dataframes)
            expected = ['Training Metrics', 'Test', 'Comp. 2']
            self.assertEqual(expected, actual)

        with self.subTest('Assigns numbered labels for additional dataframes if label list is shorter than dataframes'):
            dataframes = ["Fake dataframe", "Fake dataframe 2", "Fake dataframe 3"]
            actual = _create_labels(['Train'], dataframes)
            expected = ['Train', 'Comp. 1', 'Comp. 2']
            self.assertEqual(expected, actual)


    def test_validate_data_inputs(self):
        with self.subTest("Converts single dataframe inputs into list of dataframes"):
            df = pd.DataFrame()
            actual = _sanitize_data_inputs(df)
            self.assertEqual([df], actual)

        with self.subTest("Doesn't touch a list of dataframe inputs"):
            df = [pd.DataFrame()]
            actual = _sanitize_data_inputs(df)
            self.assertEqual(df, actual)

        with self.subTest("Allows list of multiple dataframe inputs"):
            df = [pd.DataFrame(), pd.DataFrame()]
            actual = _sanitize_data_inputs(df)
            self.assertEqual(df, actual)

        with self.subTest("returns empty list if none is provided"):
            df = None
            actual = _sanitize_data_inputs(df)
            self.assertEqual([], actual)

    def test_get_corr_func_returns_correct_function(self):
        with self.subTest("mutual information"):
            corr_func = 'mutual information'
            actual, _ = _get_corr_func(corr_func)
            expected = get_mutual_information

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("mutual_information"):
            corr_func = 'mutual_information'
            actual, _ = _get_corr_func(corr_func)
            expected = get_mutual_information

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("mi"):
            corr_func = 'mi'
            actual, _ = _get_corr_func(corr_func)
            expected = get_mutual_information
            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("pearson"):
            corr_func = 'pearson'
            actual, _ = _get_corr_func(corr_func)
            expected = get_pearson_correlations

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("pearsons"):
            corr_func = 'pearsons'
            actual, _ = _get_corr_func(corr_func)
            expected = get_pearson_correlations

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("spearman"):
            corr_func = 'spearman'
            actual, _ = _get_corr_func(corr_func)
            expected = get_spearmans_correlations

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("spearmans"):
            corr_func = 'spearman'
            actual, _ = _get_corr_func(corr_func)
            expected = get_spearmans_correlations

            self.assertEqual(expected.__name__, actual.__name__)

        with self.subTest("unknown"):
            corr_func = 'unknown'
            with self.assertRaises(ValueError):
                _get_corr_func(corr_func)
