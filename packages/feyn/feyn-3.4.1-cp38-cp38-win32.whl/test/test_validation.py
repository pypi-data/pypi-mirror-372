import numpy as np
import pandas as pd

from feyn import QLattice, fit_models, prune_models, get_diverse_models
from feyn._validation import (
    _validate_categorical_stypes,
    _validate_bool_values,
    _validate_category_number,
)

from .classes import ErrorTestCase
from . import quickmodels


class TestSampleModelsValueErrors(ErrorTestCase):
    def setUp(self):
        self.ql = QLattice()
        self.input_names = ["hello", "hola"]
        self.output_name = "apples"

    def test_input_names_raise_value_error_if_empty_list(self):
        with self.assertRaises(ValueError) as ctx:
            input_names = []
            self.ql.sample_models(input_names, self.output_name, max_complexity=1)
        self.assertEqual("input_names cannot be empty.", str(ctx.exception))

    def test_max_complexity_raises_value_error_when_negative(self):
        with self.assertRaisesAndContainsMessage(ValueError, "max_complexity"):
            mc = -10
            self.ql.sample_models(self.input_names, self.output_name, max_complexity=mc)

    def test_kind_validation(self):
        with self.assertRaisesAndContainsMessage(ValueError, "kind"):
            kind = "hello"
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                kind=kind,
                max_complexity=1,
            )

    def test_function_names_raises_value_error_on_bad_function_names(self):
        with self.assertRaisesAndContainsMessage(
            ValueError, "not a valid function name"
        ):
            fnames = ["multiply", "hello"]
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                function_names=fnames,
            )


class TestPruneModelsValueErrorValidation(ErrorTestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(["x", "y"], "z")

    def test_keep_n_raises_valueerror_when_negative(self):
        with self.assertRaisesAndContainsMessage(ValueError, "keep_n"):
            keep_n = -5
            prune_models([self.model], keep_n=keep_n)

    def test_robust_against_empty_list_of_models(self):
        models = prune_models([])
        assert models == []


class TestBestDiverseModelsValueErrorValidation(ErrorTestCase):
    def test_robust_against_empty_list_of_models(self):
        models = get_diverse_models([])
        assert models == []


class TestSampleModelsTypeErrors(ErrorTestCase):
    def setUp(self):
        self.ql = QLattice()
        self.input_names = ["hello", "hola"]
        self.output_name = "apples"

    def test_input_names_validation(self):
        with self.subTest("TypeError if input_names is not an iterable"):
            with self.assertRaisesTypeErrorAndContainsParam("input_names"):
                input_names = 45
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

        with self.subTest("TypeError if input_names is iterable with mix of strings"):
            with self.assertRaisesTypeErrorAndContainsParam("input_names"):
                input_names = [45, "hello"]
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

        with self.subTest("ValueError if input_names contains duplicates"):
            with self.assertRaisesAndContainsMessage(ValueError, "input_names"):
                input_names = ["smoker", "smoker", "smoker"]
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

    def test_output_name_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("output_name"):
            output_name = 42
            self.ql.sample_models(self.input_names, output_name, max_complexity=1)

    def test_max_complexity_validation(self):
        with self.subTest("TypeError if max_complexity is not a integer"):
            with self.assertRaisesTypeErrorAndContainsParam("max_complexity"):
                mc = 3.5
                self.ql.sample_models(
                    self.input_names, self.output_name, max_complexity=mc
                )

    def test_query_string_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("query_string"):
            query_str = 42
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                query_string=query_str,
            )

    def test_function_names_validation(self):
        with self.subTest("TypeError when function names is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("function_names"):
                fnames = "hello"

                self.ql.sample_models(
                    input_names=self.input_names,
                    output_name=self.output_name,
                    max_complexity=1,
                    function_names=fnames,
                )

        with self.subTest("TypeError when function names is not a list of strings"):
            with self.assertRaisesTypeErrorAndContainsParam("function_names"):
                fnames = [42, "hello"]

                self.ql.sample_models(
                    input_names=self.input_names,
                    output_name=self.output_name,
                    max_complexity=1,
                    function_names=fnames,
                )

    def test_stypes_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("stypes"):
            stypes = {"hello": 3}

            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                stypes=stypes,
            )


class TestFitModelsValidation(ErrorTestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "apples": [1, 2, 3, 4],
                "bananas": ["a", "nice", "cat", "input"],
                "target": [0, 1, 0, 0],
            }
        )
        self.model = quickmodels.get_simple_binary_model(["x", "y"], "z")
        self.n_samples = 3

    def test_models_validation(self):
        with self.subTest("TypeError when models is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                fit_models(self.model, self.data, n_samples=self.n_samples)

        with self.subTest("TypeError when models is not a list of feyn.models"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                models = ["hello"]
                fit_models(models, self.data)

    def test_data_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("data"):
            data = {"a": np.array([1, 2, 3]), "target": np.array([0, 1, 1])}
            fit_models([self.model], data, n_samples=self.n_samples)

    def test_n_samples_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("n_samples"):
            n_samples = 5.5
            fit_models([self.model], self.data, n_samples=n_samples)

    def test_sample_weights_validation(self):
        with self.subTest("TypeError when sample weights is not an iterable of floats"):
            with self.assertRaisesTypeErrorAndContainsParam("sample_weights"):
                fit_models(
                    [self.model],
                    self.data,
                    n_samples=self.n_samples,
                    sample_weights=[3.0, "hello"],
                )

        with self.subTest(
            "ValueError when length of sample weights does not match length of data"
        ):
            with self.assertRaisesAndContainsMessage(ValueError, "sample_weights"):
                fit_models(
                    [self.model],
                    self.data,
                    n_samples=self.n_samples,
                    sample_weights=[1.0],
                )

    def test_threads_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("threads"):
            threads = 4.5
            fit_models(
                [self.model], self.data, n_samples=self.n_samples, threads=threads
            )

    def test_immutable_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("immutable"):
            immutable = 42
            fit_models(
                [self.model], self.data, n_samples=self.n_samples, immutable=immutable
            )


class TestPruneModelsTypeErrorValidation(ErrorTestCase):
    def setUp(self):
        self.model = quickmodels.get_simple_binary_model(["x", "y"], "z")

    def test_models_validation(self):
        with self.subTest("TypeError when models is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                prune_models(self.model)

        with self.subTest("TypeError when models is not a list of feyn.models"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                models = ["hello"]
                prune_models(models)

    def test_keep_n_validation(self):
        with self.subTest("TypeError when keep_n is not an integer"):
            with self.assertRaisesTypeErrorAndContainsParam("keep_n"):
                keep_n = 5.5
                prune_models([self.model], keep_n=keep_n)


class TestUpdateValidation(ErrorTestCase):
    def setUp(self):
        self.ql = QLattice()
        self.ql.reset()

    def test_update_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("models"):
            models = ["bananas"]
            self.ql.update(models)


class TestDataValidation(ErrorTestCase):
    def test_validate_stype_categorical(self):
        df = pd.DataFrame({"A": ["test"]})
        with self.subTest(
            "ValueError when data object column is not specified as categorical in stypes"
        ):
            stypes = {}
            with self.assertRaisesAndContainsMessage(ValueError, "stypes"):
                _validate_categorical_stypes(df, stypes=stypes)

        with self.subTest("Success case"):
            stypes = {"A": "c"}
            _validate_categorical_stypes(df, stypes=stypes)

    def test_regression_target_non_numerical_values(self):
        from feyn._validation import _validate_regression_output_non_numerical_values

        df = pd.DataFrame({"target": [1, "banana"]})
        with self.subTest(
            "ValueError when target column has non-numerical values in a regression case"
        ):
            with self.assertRaisesAndContainsMessage(ValueError, "target"):
                _validate_regression_output_non_numerical_values(df, "target")

    def test_validate_bool_values(self):
        df = pd.DataFrame({"target": [0, 0.123, 0.7, 1]})
        with self.subTest("ValueError when target is not bool"):
            self.assertFalse(_validate_bool_values(df["target"]))

        df = pd.DataFrame({"target": [0, 0.0, False, 1, 1.0, True]})
        with self.subTest("Success"):
            self.assertTrue(_validate_bool_values(df["target"]))

    def test_validate_category_number(self):
        df = pd.DataFrame({"target": [0, 0, 0, 0]})
        with self.subTest("ValueError must contain exactly two categories"):
            self.assertFalse(_validate_category_number(df["target"]))

        df = pd.DataFrame({"target": [0, 0, 1, 1, 0, 1]})
        with self.subTest("Success"):
            self.assertTrue(_validate_category_number(df["target"]))

    def test_validate_nan_values(self):
        from feyn._validation import validate_data

        with self.subTest("Success if Nan value is in a categorical input"):
            df = pd.DataFrame({"x": [None, "a", "b"], "y": [1, 2, 3]})
            self.assertIsNone(
                validate_data(df, kind="regression", output_name="y", stypes={"x": "c"})
            )

        with self.subTest("ValueError if Nan value is in a numerical input"):
            df = pd.DataFrame({"x": [None, 1, 2], "y": [1, 2, 3]})
            with self.assertRaisesAndContainsMessage(ValueError, "Nan values"):
                validate_data(df, kind="regression", output_name="y")

        with self.subTest("ValueError if Nan value is in a boolean input"):
            df = pd.DataFrame({"x": [None, 1, 0], "y": [1, 2, 3]})
            with self.assertRaisesAndContainsMessage(ValueError, "Nan values"):
                validate_data(df, kind="auto", stypes={"y": "f"}, output_name="y")

        with self.subTest("ValueError if Nan value is in a boolean output"):
            df = pd.DataFrame({"x": [None, 1, 0], "y": [1, 2, 3]})
            with self.assertRaisesAndContainsMessage(
                ValueError, "x must be an iterable of booleans or 0s and 1s"
            ):
                validate_data(df, kind="auto", stypes={"x": "b"}, output_name="x")

        with self.subTest(
            "ValueError if Nan value is in a boolean output using kind=auto with no stypes given"
        ):
            df = pd.DataFrame({"x": [None, 1, 0], "y": [1, 2, 3]})
            with self.assertRaisesAndContainsMessage(ValueError, "Nan values"):
                validate_data(df, kind="auto", output_name="x")

    def test_data_missing_columns(self):
        from feyn._validation import _validate_data_columns_for_model
        from test.quickmodels import get_simple_binary_model

        self.df = pd.DataFrame({"x": [3, 2, 1], "y": [1, 2, 3], "z": [4, 4, 4]})
        self.model = get_simple_binary_model(["x", "y"], "z")

        with self.subTest("Success if dataframe contains the columns in the model"):
            self.assertTrue(_validate_data_columns_for_model(self.model, self.df))

        with self.subTest(
            "No ValueError if output not in dataframe and output = False"
        ):
            df = pd.DataFrame({"x": [3, 2, 1], "y": [1, 2, 3]})

            res = _validate_data_columns_for_model(self.model, df, output=False)
            self.assertTrue(res)

        with self.subTest("ValueError if output not in dataframe"):
            df = pd.DataFrame({"x": [3, 2, 1], "y": [1, 2, 3]})

            with self.assertRaisesAndContainsMessage(
                ValueError, "Output 'z' not found in data."
            ):
                _validate_data_columns_for_model(self.model, df)

        with self.subTest("ValueError if either input not in dataframe"):
            df = pd.DataFrame({"x": [3, 2, 1], "z": [4, 4, 4]})

            with self.assertRaisesAndContainsMessage(
                ValueError, "Input 'y' not found in data."
            ):
                _validate_data_columns_for_model(self.model, df)

            df = pd.DataFrame({"y": [1, 2, 3], "z": [4, 4, 4]})
            with self.assertRaisesAndContainsMessage(
                ValueError, "Input 'x' not found in data."
            ):
                _validate_data_columns_for_model(self.model, df)

        with self.subTest("ValueError if input or output not in pandas series"):
            df = pd.DataFrame({"x": [3, 2, 1], "z": [4, 4, 4]})
            series = df.iloc[0:1]
            self.assertTrue(type(series).__name__, "Series")

            with self.assertRaisesAndContainsMessage(
                ValueError, "Input 'y' not found in data."
            ):
                _validate_data_columns_for_model(self.model, series)

            df = pd.DataFrame({"x": [3, 2, 1], "y": [1, 2, 3]})
            series = df.iloc[0:1]
            self.assertTrue(type(series).__name__, "Series")

            with self.assertRaisesAndContainsMessage(
                ValueError, "Output 'z' not found in data."
            ):
                _validate_data_columns_for_model(self.model, series)
