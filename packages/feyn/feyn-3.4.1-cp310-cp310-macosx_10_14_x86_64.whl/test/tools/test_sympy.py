import unittest

from feyn.tools import sympify_model, get_sympy_substitutions

from feyn.tools._sympy import _signif

import numpy as np
import sympy

from .. import quickmodels


class TestTools(unittest.TestCase):
    def setUp(self) -> None:
        self.data = dict(
            {
                "age": np.array([20, 40, 20, 20, 40, 20]),
                "smoker": np.array([0, 1, 1, 0, 1, 0]),
                "sex": np.array(["yes", "no", "yes", "no", "yes", "no"]),
                "charges": np.array([10000, 20101, 10001, 20101, 20100, 10101]),
            }
        )

    def test_signif(self):
        digits = 6

        with self.subTest(
            "Can round floats to significant digits (rather than decimal points)"
        ):
            num = 12345.12345

            expected = 12345.1
            actual = _signif(num, digits)

            self.assertEqual(expected, actual, "Expected signif to round properly")

        with self.subTest("Can round scientific notation as well as floats"):
            from sympy import sympify

            num = sympify(f"{12345.12345:10e}")

            expected = round(sympy.Float(12345.1), 1)
            actual = _signif(num, digits)

            assert isinstance(actual, sympy.Float)
            self.assertEqual(expected, actual, "Expected signif to round properly")

        with self.subTest("Can round integers to significant digits"):
            num = 1234

            expected = 1230
            actual = _signif(num, 3)
            self.assertEqual(expected, actual, "Expected signif to round properly")

    def test_predict_sympy_all(self):
        model = quickmodels.get_simple_binary_model(["age", "smoker"], "charges")

        expected = model.predict(self.data)

        signif = 15

        symp = sympify_model(model, symbolic_lr=True, signif=signif)

        actual = _predict_sympy_all(symp, self.data, model, signif)
        for e, a in zip(expected, actual):
            np.testing.assert_almost_equal(e, a, decimal=signif - 5)

    def test_predict_sympy_all_with_cat_expansion(self):
        model = quickmodels.get_simple_binary_model(["age", "smoker"], "charges")

        expected = model.predict(self.data)

        signif = 15

        symp = sympify_model(model, symbolic_lr=True, signif=signif, symbolic_cat=False)

        actual = _predict_sympy_all(symp, self.data, model, signif, symbolic_cat=False)
        for e, a in zip(expected, actual):
            np.testing.assert_almost_equal(e, a, decimal=signif - 5)

    def test_weightless_sympy(self):
        model = quickmodels.get_simple_binary_model(["age", "smoker"], "charges")

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "age + smoker" == str(symp)

    def test_sympy_underscores_get_replaced(self):
        model = quickmodels.get_simple_binary_model(["age_age", "sex"], "charges")
        self.data["age_age"] = self.data["age"]
        del self.data["age"]

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "ageage + sex" == str(symp)

    def test_sympy_symboliclr_false(self):
        model = quickmodels.get_simple_binary_model(
            ["age", "sex"], "charges", stypes={"charges": "b"}
        )

        symp = sympify_model(model, symbolic_lr=False, include_weights=False)

        assert "logreg(age + sex)" == str(symp)

    def test_sympy_symboliclr_true(self):
        model = quickmodels.get_simple_binary_model(
            ["age", "sex"], "charges", stypes={"charges": "b"}
        )

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "1/(exp(-age - sex) + 1)" == str(symp)

    def test_special_characters(self):
        model = quickmodels.get_simple_binary_model(
            ["a2+4/5-7~", "sex reg.*(not_verified)"], "charges", stypes={"charges": "b"}
        )

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "1/(exp(-a2+4/5-7~ - sex reg.*(notverified)) + 1)" == str(symp)

    def test_numerical_input_names(self):
        model = quickmodels.get_simple_binary_model(
            ["245", "357"], "1337", stypes={"357": "c"}
        )

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "245 + 357_cat" == str(symp)

    def test_duplicate_category_names(self):
        model = quickmodels.get_simple_binary_model(
            ["357", "357"], "1337", stypes={"357": "c"}
        )

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert "357_2cat + 357_3cat" == str(symp)


def _predict_sympy_all(expr, samples, model, signif=15, symbolic_cat=True):
    predictions = []

    length = len(next(iter(samples.values())))
    for i in range(length):
        sample = {key: values[i] for key, values in samples.items()}
        substitutions = get_sympy_substitutions(
            model, sample, symbolic_cat=symbolic_cat
        )
        prediction = expr.evalf(n=signif, subs=substitutions)
        predictions.append(prediction)

    return predictions
