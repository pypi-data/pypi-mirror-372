import unittest
import math

import numpy as np
import pandas as pd

from feyn.tools._data._types import (
    SeriesStatistics,
    infer_stypes,
    log_type_warnings,
    remove_skipped_inputs,
    HighCardinalityMessage,
    NotSupportedMessage,
    RedundancyMessage,
)


def _warnings_contains_string(warnings, msg):
    return any(lambda w: msg in w.message for w in warnings)


def _warnings_contains_msgtype(warnings, msgtype):
    return any(lambda w: isinstance(w, msgtype) for w in warnings)


class TestLogTypeWarnings(unittest.TestCase):
    def test_logs_warnings(self):
        with self.subTest("Logs all the messages"):
            log = log_type_warnings(
                [
                    HighCardinalityMessage("Test log 1"),
                    NotSupportedMessage("Test log 2"),
                    RedundancyMessage("Test log 3"),
                ]
            )
            with self.assertLogs("feyn.tools._data._types") as logs:
                log()
                self.assertEqual(len(logs.records), 3)
                self.assertTrue("WARNING" in logs.output[0])
                self.assertTrue("INFO" in logs.output[1])
                self.assertTrue("INFO" in logs.output[2])

        with self.subTest("Only logs warnings once if not in a notebook"):
            log = log_type_warnings([HighCardinalityMessage("Test log")])
            log._is_notebook = False
            with self.assertLogs("feyn.tools._data._types") as logs:
                log()
                log()
                self.assertEqual(len(logs.records), 1)

        with self.subTest("Logs warnings every time if in a notebook"):
            log = log_type_warnings([HighCardinalityMessage("Test log")])
            log._is_notebook = True
            with self.assertLogs("feyn.tools._data._types") as logs:
                log()
                log()
                self.assertEqual(len(logs.records), 2)


class TestTypeInference(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "binary_output": [0, 1] * 8,
                "binary": [False, True] * 8,
                "cat_binary": ["False", "True"] * 8,
                "ID": np.arange(16),
                "Timestamp": [f"2024-02-{inc+1}" for inc in np.arange(16)],
                "Numeric": [int(v * 10) for v in np.random.random(16)],
                "Float": np.random.random(16),
                "HighCardinalCat": [str(v) for v in np.random.random(16)],
                "Cat": [str(v) for v in np.random.random(4)] * 4,
                "NominalNumeric": [i for i in np.arange(4)] * 4,
                "NaNContent": [i for i in np.arange(6)] * 2
                + [pd.NA] * 4,  # To go to 16
                "AllNaN": [pd.NA] * 16,
                "Mixed": ["String", 1, 3.0, pd.NA] * 4,
                "MixedNumeric": [v for v in np.arange(8)]
                + [v for v in np.random.random(8)],
            }
        )

    def test_remove_skipped_inputs(self):
        stypes = {
            "ID": "skip",
            "binary": "c",
            "Numeric": "f",
            "NotAnActualInput": "skip",
        }
        input_names = self.df.columns
        new_input_names, new_stypes = remove_skipped_inputs(input_names, stypes)

        self.assertEqual(
            len(new_input_names), len(input_names) - 1
        )  # Should only remove the skipped inputs

        self.assertTrue("ID" not in new_input_names)
        self.assertTrue("ID" not in new_stypes)

    def test_infer_stypes(self):
        stypes, warnings = infer_stypes(self.df, "binary_output", capture_warnings=True)

        self.assertTrue(_warnings_contains_msgtype(warnings, RedundancyMessage))
        self.assertTrue(_warnings_contains_msgtype(warnings, NotSupportedMessage))
        self.assertTrue(_warnings_contains_msgtype(warnings, HighCardinalityMessage))

        with self.subTest("Can detect binary output column"):
            self.assertEqual("b", stypes["binary_output"])

        with self.subTest("Can detect numeric binary input column, assigns f"):
            self.assertEqual("f", stypes["binary"])

        with self.subTest("Can detect non-numeric binary input column, assigns c"):
            self.assertEqual("c", stypes["cat_binary"])

        with self.subTest("Can detect and skip ID-like columns"):
            self.assertEqual("skip", stypes["ID"])
            self.assertTrue(
                _warnings_contains_string(warnings, "Column 'ID' looks like an ID")
            )

        with self.subTest("Can detect and skip Timestamp-like columns"):
            self.assertEqual("skip", stypes["Timestamp"])

            self.assertTrue(
                _warnings_contains_string(
                    warnings, "Column 'Timestamp' looks like a timestamp"
                )
            )

        with self.subTest("Can detect numeric columns"):
            self.assertEqual("f", stypes["Numeric"])

        with self.subTest("Can detect float columns"):
            self.assertEqual("f", stypes["Float"])

        with self.subTest("Can detect categorical string and numeric columns"):
            self.assertEqual("c", stypes["Cat"])
            self.assertEqual("c", stypes["HighCardinalCat"])
            self.assertEqual("c", stypes["NominalNumeric"])

        with self.subTest("Warns about high cardinality"):
            self.assertTrue(
                _warnings_contains_string(
                    warnings, "Column 'HighCardinalCat' has high cardinality"
                )
            )

        with self.subTest("Works for NaN content"):
            self.assertEqual("f", stypes["NaNContent"])

        with self.subTest("Works for all NaN"):
            self.assertEqual("c", stypes["AllNaN"])

        with self.subTest("Can detect and skip Mixed inputs"):
            self.assertEqual("skip", stypes["Mixed"])

        with self.subTest("Can detect mixed numeric inputs and assign continuous"):
            self.assertEqual("f", stypes["MixedNumeric"])


class TestSeriesStatistics(unittest.TestCase):
    def test_is_binary(self):
        with self.subTest("Returns true for numeric binary columns"):
            stats = SeriesStatistics(pd.Series([0, 1] * 8))
            is_binary = stats._is_binary()

            self.assertTrue(is_binary)

        with self.subTest("Returns true for non-numeric binary columns"):
            stats = SeriesStatistics(pd.Series(["Hello", "World"] * 8))
            is_binary = stats._is_binary()

            self.assertTrue(is_binary)

        with self.subTest("Returns false for non-binary columns"):
            stats = SeriesStatistics(pd.Series([0, 1, 2] * 8))
            is_binary = stats._is_binary()

            self.assertFalse(is_binary)

    def test_is_constant(self):
        above_threshold = 11
        below_threshold = 10
        with self.subTest("Returns true for series with only one value"):
            stats = SeriesStatistics(pd.Series([100] * above_threshold))
            is_constant = stats._is_constant()

            self.assertTrue(is_constant)

            stats = SeriesStatistics(pd.Series(["100"] * above_threshold))
            is_constant = stats._is_constant()

            self.assertTrue(is_constant)

        with self.subTest("Returns false for series with more than one value"):
            stats = SeriesStatistics(pd.Series(["Hello", "World"] * above_threshold))
            is_constant = stats._is_constant()

            self.assertFalse(is_constant)

        with self.subTest(
            "Returns false for series with only one value if the series is smaller than 10"
        ):
            stats = SeriesStatistics(pd.Series(["Hello"] * below_threshold))
            is_constant = stats._is_constant()

            self.assertFalse(is_constant)

    def test_is_likely_ordinal_and_nominal(self):
        ord_threshold = lambda l: round(math.log2(l))

        def get_series(l, extra=0):
            thresh = ord_threshold(l) + extra
            multiplier = math.ceil(l / thresh)
            series = np.tile(np.arange(thresh), multiplier)[0:l]

            self.assertEqual(len(series), l)
            return pd.Series(series)

        with self.subTest(
            "Returns true for series with fewer or equal distinct values than the threshold"
        ):
            stats = SeriesStatistics(get_series(10))
            is_likely_ordinal = stats._is_likely_ordinal()

            self.assertTrue(is_likely_ordinal)
            is_likely_nominal = stats._is_likely_nominal()
            self.assertTrue(is_likely_nominal)

        with self.subTest(
            "Returns false for series with more distinct values than the threshold"
        ):
            stats = SeriesStatistics(get_series(10, 1))
            is_likely_ordinal = stats._is_likely_ordinal()

            self.assertFalse(is_likely_ordinal)
            is_likely_nominal = stats._is_likely_nominal()
            self.assertFalse(is_likely_nominal)

    def test_is_continuous(self):
        with self.subTest("Returns true for series with floats"):
            stats = SeriesStatistics(pd.Series([1.0, 2.0, 3.3]))
            is_continuous = stats._is_continuous()

            self.assertTrue(is_continuous)

        with self.subTest("Returns true for series with just one float"):
            stats = SeriesStatistics(pd.Series([1, 2, 3.3]))
            is_continuous = stats._is_continuous()

            self.assertTrue(is_continuous)

        with self.subTest("Returns false for series without floats"):
            stats = SeriesStatistics(pd.Series([1, 2, 3]))
            is_continuous = stats._is_continuous()

            self.assertFalse(is_continuous)

        with self.subTest("Returns false for series with string floats"):
            stats = SeriesStatistics(pd.Series(["1.1, 2.2, 3.3"]))
            is_continuous = stats._is_continuous()

            self.assertFalse(is_continuous)

    def test_is_ID_like(self):
        above_threshold = 11
        below_threshold = 10
        with self.subTest(
            "Returns true for series with all distinct values if larger than the threshold"
        ):
            stats = SeriesStatistics(pd.Series(np.arange(above_threshold)))
            is_ID_like = stats._is_ID_like()

            self.assertTrue(is_ID_like)

        with self.subTest(
            "Returns true for series with all distinct values if larger than the threshold, ignoring NaNs"
        ):
            stats = SeriesStatistics(
                pd.Series(np.append(np.arange(above_threshold), [pd.NA, pd.NA]))
            )
            is_ID_like = stats._is_ID_like()

            self.assertTrue(is_ID_like)

        with self.subTest(
            "Returns false for series with all distinct values if smaller than the threshold"
        ):
            stats = SeriesStatistics(pd.Series(np.arange(below_threshold)))
            is_ID_like = stats._is_ID_like()

            self.assertFalse(is_ID_like)

        with self.subTest("Returns false for series with repeat values"):
            stats = SeriesStatistics(
                pd.Series(np.append(np.arange(above_threshold), [0, 1]))
            )
            is_ID_like = stats._is_ID_like()

            self.assertFalse(is_ID_like)

    def test_is_high_cardinality(self):
        def get_series(l, unique_ratio):
            uniques = math.ceil((l * unique_ratio))
            series = np.tile(np.arange(uniques), int(l / unique_ratio))[0:l]
            self.assertEqual(len(series), l)
            self.assertEqual(len(np.unique(series)), uniques)
            return series

        with self.subTest("Returns true for series with a unique ratio over 0.5"):
            series = get_series(10, 0.51)

            stats = SeriesStatistics(pd.Series(series))
            is_high_cardinality = stats._is_high_cardinality()

            self.assertTrue(is_high_cardinality)

        with self.subTest(
            "Returns true for series with a unique ratio over 0.5, ignoring NaNs"
        ):
            non_nan = get_series(10, 0.51)
            series = np.append(non_nan, [pd.NA, pd.NA])

            stats = SeriesStatistics(pd.Series(series))

            is_high_cardinality = stats._is_high_cardinality()

            self.assertTrue(is_high_cardinality)

        with self.subTest("Returns true for series with more than 50 unique values"):
            uniques = 51
            stats = SeriesStatistics(
                pd.Series(np.append(np.arange(uniques), [pd.NA, pd.NA]))
            )
            is_high_cardinality = stats._is_high_cardinality()

            self.assertTrue(is_high_cardinality)

        with self.subTest(
            "Returns false for series below the ratio of 0.5 (ignoring NaNs)"
        ):
            non_nan = get_series(10, 0.5)
            self.assertEqual(len(np.unique(non_nan)), 5)
            series = np.append(non_nan, [pd.NA, pd.NA])

            stats = SeriesStatistics(pd.Series(series))
            is_high_cardinality = stats._is_high_cardinality()

            self.assertFalse(is_high_cardinality)

    def test_is_string_type(self):
        with self.subTest("Returns true for series with strings"):
            series = ["Hey", "Planet"]

            stats = SeriesStatistics(pd.Series(series))
            is_string_type = stats._is_string_type()

            self.assertTrue(is_string_type)

            series = ["Hey", "Planet", 0]

            stats = SeriesStatistics(pd.Series(series))
            is_string_type = stats._is_string_type()

            self.assertTrue(is_string_type)

        with self.subTest("Returns false for series without strings"):
            series = [0, 1]

            stats = SeriesStatistics(pd.Series(series))
            is_string_type = stats._is_string_type()

            self.assertFalse(is_string_type)

    def test_is_numerical(self):
        with self.subTest("Returns true for series with numbers"):
            series = [0, 1, 2]

            stats = SeriesStatistics(pd.Series(series))
            is_numerical = stats._is_numerical()

            self.assertTrue(is_numerical)

            series = [0.1, 0.2, 0.3]

            stats = SeriesStatistics(pd.Series(series))
            is_numerical = stats._is_numerical()

            self.assertTrue(is_numerical)

            series = [0.1, 2, 0.3]

            stats = SeriesStatistics(pd.Series(series))
            is_numerical = stats._is_numerical()

            self.assertTrue(is_numerical)

        with self.subTest("Returns false for series without numbers"):
            series = ["No numbers", pd.NA]

            stats = SeriesStatistics(pd.Series(series))
            is_numerical = stats._is_numerical()

            self.assertFalse(is_numerical)

        with self.subTest("Returns false for mixed number/string series"):
            series = ["No numbers", 1]

            stats = SeriesStatistics(pd.Series(series))
            is_numerical = stats._is_numerical()

            self.assertFalse(is_numerical)

    def test_is_categorical(self):
        with self.subTest("Returns true for series with categorical dtype"):
            series = ["Cat 1", "Cat 2"]

            stats = SeriesStatistics(pd.Series(series).astype("category"))
            is_categorical = stats._is_categorical()

            self.assertTrue(is_categorical)

            series = [1, 2, 3]

            stats = SeriesStatistics(pd.Series(series).astype("category"))
            is_categorical = stats._is_categorical()

            self.assertTrue(is_categorical)

        with self.subTest("Returns false for series that are not categorical"):
            series = [1, 2, 3]

            stats = SeriesStatistics(pd.Series(series))
            is_categorical = stats._is_categorical()

            self.assertFalse(is_categorical)

    def test_is_mixed_type(self):
        with self.subTest("Returns true for series with mixed types with non-integers"):
            series = ["Hello", 1]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertTrue(is_mixed_type)

            series = ["Hello", 1.0]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertTrue(is_mixed_type)

        with self.subTest(
            "Returns false for series that are not mixed, or have mixed numericals only"
        ):
            series = [1, 2, 3]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertFalse(is_mixed_type)

            series = [1.0, 2.0, 3.0]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertFalse(is_mixed_type)

            series = ["Hello", "World"]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertFalse(is_mixed_type)

            series = [1, 2.0, 3]

            stats = SeriesStatistics(pd.Series(series))
            is_mixed_type = stats._is_mixed_type()

            self.assertFalse(is_mixed_type)

    def test_is_likely_datetime(self):
        with self.subTest("Returns true for series that look like an ISO datetime"):
            series = ["2024-02-23 11:42:03"]

            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertTrue(is_datetime)

            series = ["2024-02-23 11:42:03+01:00"]

            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertTrue(is_datetime)

        with self.subTest("Returns false for series that look like a timedelta"):
            series = ["3 days 00:00:00"]

            stats = SeriesStatistics(pd.Series(series))
            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

        with self.subTest("Returns false for series that are not strictly timedelta"):
            series = ["3 days"]

            stats = SeriesStatistics(pd.Series(series))
            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

        with self.subTest("Returns false for series that don't look like dates"):
            series = ["Totally not a date"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

        with self.subTest("Returns false for non-iso dates"):
            series = ["23/2/2024"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()
            self.assertFalse(is_datetime)

            series = ["23-2-24"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()
            self.assertFalse(is_datetime)

        with self.subTest(
            "Returns false for categoricals that are not intended as dates"
        ):
            series = ["February"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["2024"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["Monday"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["Q1 2024"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["2024 Feb"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["21"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["42.69"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)

            series = ["23 Feb 2024"]
            stats = SeriesStatistics(pd.Series(series))

            is_datetime = stats._is_likely_datetime()

            self.assertFalse(is_datetime)
