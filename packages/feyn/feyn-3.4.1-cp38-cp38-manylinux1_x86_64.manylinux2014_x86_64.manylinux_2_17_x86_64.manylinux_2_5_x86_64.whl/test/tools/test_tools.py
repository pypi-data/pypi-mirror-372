import unittest

import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal

from feyn.tools import split
from feyn.tools._data._data import _stratified_split, _adjust_random_subset


class TestTools(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "A": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                "B": [1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                "C": [1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            }
        )

    def test_split(self):
        data = {"a": np.array(range(10)), "b": np.array(range(10))}

        with self.subTest("Can split dict of arrays"):
            with self.assertLogs("feyn.tools._data", level="WARNING") as logger:
                s1, s2 = split(data, ratio=[4, 1])

                # We should get 8 out of 10 samples in the first bucket
                self.assertEqual(len(s1["a"]), 8)
                # Order is preserved across the columns
                assert_array_equal(s1["a"], s1["b"])

                # We should get 2 out of 10 samples in the second bucket
                self.assertEqual(len(s2["a"]), 2)
                assert_array_equal(s2["a"], s2["b"])

                self.assertEqual(
                    logger.output,
                    [
                        "WARNING:feyn.tools._data._data:Deprecation: using dicts of numpy arrays are deprecated and will be removed in future versions of Feyn."
                    ],
                )

        with self.subTest("Can split pandas"):
            df = pd.DataFrame(data)
            s1, s2 = split(df, ratio=[4, 1])

            # We should get 8 out of 10 samples in the first bucket
            self.assertEqual(len(s1), 8)

            # We should get 2 out of 10 samples in the second bucket
            self.assertEqual(len(s2), 2)

    def test_stratification(self):
        with self.subTest("Splitting without stratification"):
            subsets = split(self.df, [0.6, 0.4], [])
            total_size = sum([len(subset) for subset in subsets])
            self.assertEqual(total_size, len(self.df))

        with self.subTest("Splitting into multiple subsets"):
            subsets = split(self.df, [0.5, 0.3, 0.2], [])
            total_size = sum([len(subset) for subset in subsets])
            self.assertEqual(total_size, len(self.df))

        with self.subTest("Stratifying on a single column"):
            subsets = split(self.df, [0.7, 0.3], ["A"])
            total_size = sum([len(subset) for subset in subsets])
            self.assertEqual(total_size, len(self.df))

        with self.subTest("Stratifying on multiple columns"):
            subsets = split(self.df, [0.5, 0.3, 0.2], ["A", "B"])
            total_size = sum([len(subset) for subset in subsets])
            self.assertEqual(total_size, len(self.df))

        with self.subTest("Splitting works for many subsets"):
            subsets = split(self.df, [1, 1, 1, 1, 1, 1], ["A"])
            total_size = sum([len(subset) for subset in subsets])
            self.assertEqual(total_size, len(self.df))

        with self.subTest("Stratification maintains the ratios"):
            even_df = pd.DataFrame(
                {
                    "A": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                    "B": [1, 1, 1, 0, 0, 0, 1, 1, 0, 0],
                }
            )

            subsets = _stratified_split(even_df, [0.8, 0.2], ["A"], None)
            stratified_counts = even_df["A"].value_counts(normalize=True)
            for subset in subsets:
                subset_df = even_df.loc[subset]
                subset_counts = subset_df["A"].value_counts(normalize=True)
                for val in stratified_counts.index:
                    self.assertAlmostEqual(
                        stratified_counts[val], subset_counts[val], delta=0.1
                    )

        with self.subTest(
            "The random seed works in producing consistent, repeated results"
        ):
            subsets1 = _stratified_split(self.df, [0.6, 0.4], ["A"], random_state=42)
            subsets2 = _stratified_split(self.df, [0.6, 0.4], ["A"], random_state=42)
            self.assertListEqual(subsets1, subsets2)

            subsets3 = _stratified_split(self.df, [0.6, 0.4], ["A"], random_state=123)
            self.assertNotEqual(subsets1, subsets3)

    def test_different_ratios(self):
        splits = [(0.9, 0.1), (0.8, 0.2), (0.7, 0.3), (0.6, 0.4), (0.5, 0.5)]

        def do_test(train, test):
            subsets = split(self.df, [train, test], ["A"])
            self.assertAlmostEqual(len(subsets[0]) / len(self.df), train, delta=0.1)
            self.assertAlmostEqual(len(subsets[1]) / len(self.df), test, delta=0.1)

        for train, test in splits:
            do_test(train, test)

    def test_out_of_bounds_splits(self):
        with self.subTest(
            "If one of the splits has all the samples, the random distributor avoids empty or negative subsets"
        ):
            subsets = split(self.df, [0.6, 0.1, 0.1, 0.1, 0.1], ["A"], random_state=42)
            total_size = sum([len(subset) for subset in subsets])

            self.assertEqual(total_size, len(self.df))
            self.assertTrue(not any([len(subset) == 0 for subset in subsets]))

        with self.subTest(
            "If more splits share the majority of samples, the random distributor will reduce two subsets rather than one to bring down the difference"
        ):
            subsets = split(self.df, [1, 1, 1, 1], ["A"], random_state=42)
            total_size = sum([len(subset) for subset in subsets])

            self.assertEqual(total_size, len(self.df))
            self.assertTrue(not any([len(subset) == 0 for subset in subsets]))

    def test_nan_values_distribute_propertionally(self):
        self.df = pd.DataFrame(
            {
                "A": np.arange(10),
                "B": [pd.NA, 1, pd.NA, 0, 1, pd.NA, 1, 0, pd.NA, 1],
            }
        )
        subsets = split(self.df, [0.75, 0.25], ["B"], None)

        nan_count_train = subsets[0]["B"].isna().sum()
        nan_count_test = subsets[1]["B"].isna().sum()

        self.assertEqual(nan_count_train, 3)
        self.assertEqual(nan_count_test, 1)

    def test_adjust_random_subset(self):
        rng = np.random.default_rng(seed=None)

        with self.subTest(
            "_adjust_random_subset should adjust the one possible subset"
        ):
            subsets = [4, 1, 1, 1]
            size_diff = -1

            expected = [3, 1, 1, 1]
            actual = _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(actual, expected)

        with self.subTest(
            "_adjust_random_subset should adjust the two possible subsets"
        ):
            subsets = [2, 1, 2, 1]
            size_diff = -2

            expected = [1, 1, 1, 1]
            actual = _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(actual, expected)

        with self.subTest(
            "_adjust_random_subset should adjust one set by 2 and one by 1"
        ):
            subsets = [3, 1, 2, 1]
            size_diff = -3

            expected = [1, 1, 1, 1]
            actual = _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(actual, expected)

        with self.subTest("_adjust_random_subset should adjust three sets by 1"):
            subsets = [2, 2, 2, 1]
            size_diff = -3

            expected = [1, 1, 1, 1]
            actual = _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(actual, expected)

        with self.subTest(
            "_adjust_random_subset should work with arbitrarily large numbers"
        ):
            subsets = [400, 350, 150, 100]
            size_diff = -500

            expected = [150, 100, 150, 100]
            actual = _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(actual, expected)

        with self.subTest("_adjust_random_subset should also work for adding to a set"):
            subsets = [2, 2, 2, 2]
            size_diff = 2

            expected_sum = 10
            actual = sum(_adjust_random_subset(size_diff, subsets, rng))

            self.assertEqual(actual, expected_sum)

        with self.subTest(
            "_adjust_random_subset raises if the problem can't be solved"
        ):
            subsets = [1, 1, 1, 1]
            size_diff = -1

            with self.assertRaises(ValueError) as ex:
                _adjust_random_subset(size_diff, subsets, rng)
            self.assertEqual(
                str(ex.exception), "Not enough samples to distribute into 4 subsets"
            )

        with self.subTest(
            "_adjust_random_subset returns the subsets if no adjustment needs to be made"
        ):
            subsets = [1, 1, 1, 1]
            size_diff = 0

            actual = _adjust_random_subset(size_diff, subsets, rng)
            self.assertEqual(subsets, actual)

    def test_warnings_and_exceptions(self):
        self.df = pd.DataFrame(
            {
                "A": [0, 1, 0, 1, 0, 1],
                "B": [1, 1, 1, 0, 0, 0],
            }
        )

        self.tiny_df = pd.DataFrame({"A": [0, 1, 0], "B": [1, 1, 0]})

        with self.subTest(
            "_adjust_random_subset raises if no subsets can be reduced to meet the size"
        ):
            with self.assertRaises(ValueError) as ex:
                subsets = [1, 1, 1]
                size_diff = -1
                rng = np.random.default_rng(seed=None)

                _adjust_random_subset(size_diff, subsets, rng)

            self.assertEqual(
                str(ex.exception), "Not enough samples to distribute into 3 subsets"
            )

        with self.subTest(
            "Producing more splits than the data supports results in an error raised"
        ):
            with self.assertRaises(ValueError):
                split(self.tiny_df, [1, 1, 1, 1], [], random_state=42)

        with self.subTest(
            "Stratifying on a column that has insufficient samples for subsets"
        ):
            with self.assertRaises(ValueError) as ex:
                subsets = split(self.df, [1, 1, 1], ["A", "B"])
                total_size = sum([len(subset) for subset in subsets])
                self.assertEqual(total_size, len(self.df))

            self.assertTrue(
                str(ex.exception).startswith(
                    "Not enough samples in stratum ['A', 'B']: "
                ),
                # "Not enough samples in stratum ['A', 'B']: (np.int64(0), np.int64(0)) to stratify into 3 sets",
            )

        with self.subTest(
            "Specifying ratios that result in unexpected splits for the data produces a warning"
        ):
            with self.assertLogs("feyn.tools._data", level="WARNING") as logger:
                subsets = split(self.df, [0.8, 0.1, 0.1], ["A"], random_state=42)
                total_size = sum([len(subset) for subset in subsets])
                self.assertEqual(total_size, len(self.df))

            self.assertEqual(
                logger.output,
                [
                    "WARNING:feyn.tools._data._data:The sample count in one of the subsets deviates from expected ratio by 0.133. Do you have enough data to split?",
                ],
            )
