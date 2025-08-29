import unittest

import feyn
from . import quickmodels


class TestExcludeFunctions(unittest.TestCase):
    def setUp(self):
        self.test_models = [
            quickmodels.get_unary_model(["x"], "y", fname=fname)
            for fname in ["gaussian:1", "exp:1", "log:1"]
        ]
        self.test_models.append(
            quickmodels.get_specific_model(["x", "z"], "y", "gaussian('x', 'z')")
        )

    def test_exclude_single_function_filter(self):
        f = feyn.filters.ExcludeFunctions("gaussian:1")
        self.assertEqual(3, len(list(filter(f, self.test_models))))

        with self.subTest(
            "Works for blanket excluding functions when not providing arity."
        ):
            f = feyn.filters.ExcludeFunctions("gaussian")
            self.assertEqual(2, len(list(filter(f, self.test_models))))

    def test_multiple_function_exclusion(self):
        f = feyn.filters.ExcludeFunctions(["gaussian:1", "exp:1"])
        self.assertEqual(2, len(list(filter(f, self.test_models))))

        with self.subTest("Raises if only some functions have arity provided."):
            with self.assertRaises(ValueError) as ctx:
                f = feyn.filters.ExcludeFunctions(["gaussian:1", "exp"])

            self.assertEqual(
                str(ctx.exception),
                "If providing an arity for the function, all functions must have provided arity",
            )


class TestComplexity(unittest.TestCase):
    def test_complexity_filter(self):
        test_models = [
            quickmodels.get_unary_model(["x"], "y", fname=fname)
            for fname in ["gaussian:1", "exp:1"]
        ]

        test_models += [quickmodels.get_simple_binary_model(["x", "y"], "z")]

        f = feyn.filters.Complexity(3)
        self.assertEqual(1, len(list(filter(f, test_models))))


class TestContainsInput(unittest.TestCase):
    def test_contains_filter(self):
        models = [
            quickmodels.get_simple_binary_model(["x", name], "y")
            for name in ["cheese", "kase", "ost"]
        ]

        f = feyn.filters.ContainsInputs("kase")
        self.assertEqual(1, len(list(filter(f, models))))


class TestContainsFunctions(unittest.TestCase):
    def test_contains_filter(self):
        test_models = [
            quickmodels.get_unary_model(["x"], "y", fname=fname)
            for fname in ["gaussian:1", "exp:1", "log:1"]
        ]

        test_models += [
            quickmodels.get_complicated_binary_model(["x", "y"], "z", fname)
            for fname in ["exp:1", "log:1"]
        ]

        with self.subTest("Check for model built with single function."):
            f = feyn.filters.ContainsFunctions("log")
            self.assertEqual(1, len(list(filter(f, test_models))))

        with self.subTest("Works when providing arity."):
            f = feyn.filters.ContainsFunctions("log:1")
            self.assertEqual(1, len(list(filter(f, test_models))))

        with self.subTest("Check for model built with list of functions."):
            f = feyn.filters.ContainsFunctions(["add", "exp"])
            self.assertEqual(1, len(list(filter(f, test_models))))

        with self.subTest("Raises if only some functions have arity provided."):

            with self.assertRaises(ValueError) as ctx:
                f = feyn.filters.ContainsFunctions(["add:2", "exp"])

            self.assertEqual(
                str(ctx.exception),
                "If providing an arity for the function, all functions must have provided arity",
            )
