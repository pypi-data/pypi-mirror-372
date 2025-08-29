import unittest
import random

import numpy as np
import pandas as pd

from feyn import QLattice, fit_models, prune_models

from test import quickmodels


class TestQLattice(unittest.TestCase):
    def test_can_sample_classification_models_from_qlattice(self):
        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"], "charges", kind="classification", max_complexity=2
        )

        self.assertTrue(models)
        self.assertEqual(models[0].kind, "classification")

    def test_can_sample_regression_models_from_qlattice(self):
        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"], "charges", kind="regression", max_complexity=2
        )

        self.assertTrue(models)
        self.assertEqual(models[0].kind, "regression")

    def test_empty_dic_can_be_passed_to_stypes(self):
        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"],
            "charges",
            kind="regression",
            max_complexity=2,
            stypes={},
        )

        self.assertTrue(models)

    def test_uses_output_stype_to_determine_model_kind(self):
        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"],
            "charges",
            stypes={"charges": "b"},
            max_complexity=2,
        )

        self.assertTrue(models)
        self.assertEqual(models[0].kind, "classification")

        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"],
            "charges",
            stypes={"charges": "f"},
            max_complexity=2,
        )

        self.assertTrue(models)
        self.assertEqual(models[0].kind, "regression")

    def test_sample_models_defaults_to_regression_if_no_stype_is_given_for_auto_kind(
        self,
    ):
        ql = QLattice()
        models = ql.sample_models(
            ["age", "smoker", "sex"],
            "charges",
            max_complexity=2,
        )

        self.assertTrue(models)
        self.assertEqual(models[0].kind, "regression")

    def test_fit_models(self):
        models = [quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")]

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        with self.subTest("Can fit with default arguments and increment sample_count"):
            fit_models(models, data, n_samples=4)
            self.assertEqual(models[0]._sample_count, 4)

        with self.subTest("Can fit with named loss function"):
            fit_models(models, data, loss_function="absolute_error", n_samples=4)

        with self.subTest("Can fit with sample weights as list of floats"):
            fit_models(models, data, sample_weights=[1.0, 2.0, 3.0, 4.0], n_samples=4)

        with self.subTest("Can fit with sample weights as np.array"):
            fit_models(
                models, data, sample_weights=np.array([1.0, 2.0, 3.0, 4.0]), n_samples=4
            )

    def test_auto_run_all_parameters(self):
        """Run auto_run with all parameters specified"""

        ql = QLattice()

        data = pd.DataFrame(
            {
                "age": np.array([1, 2, 3]),
                "smoker": np.array([0, 0, 1]),
                "insurable": np.array([0, 0.2, 0.4]),
            }
        )
        stypes = {"smoker": "c"}

        starting_models = [
            quickmodels.get_specific_model(
                inputs=["age", "smoker"],
                output="insurable",
                equation="'age'+('age'*'smoker')",
            )
        ]

        models = ql.auto_run(
            data=data,
            output_name="insurable",
            kind="regression",
            stypes=stypes,
            n_epochs=1,
            threads=4,
            max_complexity=5,
            query_string="'age' + 'smoker'",
            loss_function="absolute_error",
            criterion="aic",
            sample_weights=[random.random() for _ in range(len(data))],
            function_names=["add", "multiply", "sqrt", "gaussian"],
            starting_models=starting_models,
        )
        self.assertTrue(models)

    def test_lattice_auto_run_validates_data(self):
        ql = QLattice()

        data = pd.DataFrame(
            {
                "age": np.array([1, 2, 3]),
                "smoker": np.array([0, 0, 1]),
                "insurable": np.array([0, 0.2, 0.4]),
            }
        )
        with self.assertRaises(ValueError):
            models = ql.auto_run(
                data, "insurable", "classification", max_complexity=2, n_epochs=1
            )

    def test_prune_keep_n_as_npint_raises(self):
        ql = QLattice()

        models = [quickmodels.get_simple_binary_model(["x", "y"], "z")]
        keep_n = np.int_(5)
        with self.assertRaises(TypeError):
            prune_models(models, keep_n=keep_n)

    def test_reproducible_auto_run(self):
        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array(["no", "yes", "no", "yes"]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )
        stypes = {"smoker": "c"}
        ql = QLattice(random_seed=31)

        first_models = ql.auto_run(
            data,
            "insurable",
            stypes=stypes,
            max_complexity=3,
            n_epochs=1,
            query_string="'age' * 'smoker'",
        )

        ql = QLattice(random_seed=31)
        second_models = ql.auto_run(
            data,
            "insurable",
            stypes=stypes,
            max_complexity=3,
            n_epochs=1,
            query_string="'age' * 'smoker'",
        )

        self.assertEqual(first_models, second_models)

    def test_update_lattice_with_models(self):
        ql = QLattice()

        models = ql.sample_models(
            ["age", "smoker", "insurable"], "insurable", max_complexity=2
        )

        with self.subTest("Can update with several models"):
            ql.update(models[:10])

        with self.subTest("Can update with empty list"):
            ql.update([])

    def test_can_sample_models_with_any_column_as_output(self):
        columns = ["age", "smoker"]
        for target in columns:
            ql = QLattice()
            models = ql.sample_models(columns, target, max_complexity=2)
            self.assertTrue(models)

    def test_can_sample_models_with_function_names(self):
        ql = QLattice()

        columns = ["age", "smoker"]
        fnames = ["exp", "log"]

        models = ql.sample_models(
            columns, "smoker", max_complexity=2, function_names=fnames
        )
        self.assertTrue(models)

    def test_can_sample_models_with_gaussian(self):
        ql = QLattice()

        columns = ["age", "smoker"]
        fnames = ["gaussian"]

        models = ql.sample_models(
            columns, "smoker", max_complexity=2, function_names=fnames
        )
        self.assertTrue(models)

    def test_can_sample_models_with_query(self):
        ql = QLattice()

        models = ql.sample_models(
            list("xy"), "out", max_complexity=3, query_string="'x' + 'y'"
        )

        expected_seq = ["add:2", "x", "y"]
        self.assertTrue(expected_seq, models[0]._program[:3])

    def test_sample_models_ignores_skipped_stypes(self):
        ql = QLattice()

        models = ql.sample_models(
            list("xy"), "out", max_complexity=3, stypes={"y": "skip"}
        )

        self.assertFalse(any(map(lambda m: "y" in m.inputs, models)))

    def test_cant_sample_models_with_complex_query(self):
        ql = QLattice()

        with self.assertRaises(ValueError):
            _ = ql.sample_models(
                list("xy"), "out", max_complexity=3, query_string="'x' + func('y')"
            )

    def test_model_fitting(self):
        ql = QLattice()

        models = ql.sample_models(
            ["age", "smoker", "insurable"],
            "insurable",
            max_complexity=2,
            kind="classification",
        )[:5]

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        with self.subTest("Fitted list is sorted by loss"):
            fitted_models = fit_models(models, data, n_samples=4)
            explicitly_sorted = sorted(
                [m.loss_value for m in fitted_models], reverse=False
            )
            fitted_losses = [m.loss_value for m in fitted_models]
            for esl, fl in zip(explicitly_sorted, fitted_losses):
                self.assertAlmostEqual(esl, fl)

        with self.subTest("Can provide the name of a loss function"):
            fitted_with_ae = fit_models(
                models, data, loss_function="absolute_error", n_samples=4
            )
            explicitly_sorted = sorted(
                [m.loss_value for m in fitted_with_ae], reverse=False
            )
            fitted_losses = [m.loss_value for m in fitted_with_ae]
            for esl, fl in zip(explicitly_sorted, fitted_losses):
                self.assertAlmostEqual(esl, fl)

    def test_DataFrame_as_input_names(self):
        ql = QLattice()

        input_names = pd.DataFrame(
            {"smoker": [1, 2, 3, 4], "age": [5, 6, 7, 10], "target": [6, 8, 10, 12]}
        )
        output_name = "target"

        models = ql.sample_models(input_names, output_name)
        self.assertIsNotNone(models[0])

    def test_raise_on_invalid_column_names_with_colons(self):
        ql = QLattice()
        df = pd.DataFrame()
        df["weird:feature"] = [1]
        df["y"] = [2]

        regex = "Input names with a colon"

        with self.assertRaisesRegex(ValueError, regex):
            ql.auto_run(df, "y")

        with self.assertRaisesRegex(ValueError, regex):
            ql.sample_models(df, "y")
