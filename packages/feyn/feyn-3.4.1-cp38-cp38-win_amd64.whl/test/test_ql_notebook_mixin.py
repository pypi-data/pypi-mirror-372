import unittest
import pytest

import pandas as pd
from feyn._qlattice import QLattice
from feyn._ql_notebook_mixin import QLatticeNotebookMixin


class ClassUnderTest(QLattice, QLatticeNotebookMixin):
    """This class is necessary to load the mixin, as it only loads in notebook contexts otherwise."""

    def expand_auto_run(self, *args, **kwargs):
        """Override this because we don't want to create notebook cells.
        The inner function we want to test is supposed to be used in a wrapped context.
        """
        return self._auto_run_decomposition_inner(*args, **kwargs)


class TestModel(unittest.TestCase):

    def test_expand_auto_run(self):

        with self.subTest("Test that it runs and produces code lines"):
            ql = ClassUnderTest()
            code_lines = ql.expand_auto_run()

            assert code_lines is not None

            imports = ["# Dependencies\n", "import feyn\n", "\n"]
            assert code_lines[: len(imports)] == imports

        with self.subTest("Test that it assigns positional arguments given"):
            ql = ClassUnderTest()
            df = pd.DataFrame()
            output = "output_value"
            code_lines = ql.expand_auto_run(df, output)

            assert code_lines is not None

            first_lines = ["# Dependencies\n", "import feyn\n", "\n"]
            first_lines += ["# Parameters\n"]

            parameter_start = len(first_lines)

            ql_expected = "ql = feyn.QLattice()\n"
            data_expected = "data = df\n"
            output_expected = "output_name = output\n"

            self.assertEqual(
                ql_expected,
                code_lines[parameter_start],
                "self should be reassigned to ql",
            )
            self.assertEqual(
                data_expected,
                code_lines[parameter_start + 1],
                "Data should be assigned to outer variable name",
            )
            self.assertEqual(
                output_expected,
                code_lines[parameter_start + 2],
                "output_name should be assigned to outer variable name",
            )

        with self.subTest("Test that it assigns the random seed if it's given"):
            ql = ClassUnderTest(42)
            df = pd.DataFrame()
            output = "output_value"
            code_lines = ql.expand_auto_run(df, output)

            assert code_lines is not None

            first_lines = ["# Dependencies\n", "import feyn\n", "\n"]
            first_lines += ["# Parameters\n"]

            parameter_start = len(first_lines)

            ql_expected = "ql = feyn.QLattice(42)\n"

            self.assertEqual(
                ql_expected,
                code_lines[parameter_start],
                "self should be reassigned to ql",
            )

        with self.subTest(
            "Test that it assigns any positional argument given inline (except DataFrames)"
        ):
            ql = ClassUnderTest()
            code_lines = ql.expand_auto_run(pd.DataFrame(), "test_output_value", 42)

            assert code_lines is not None

            first_lines = ["# Dependencies\n", "import feyn\n", "\n"]
            first_lines += ["# Parameters\n"]

            parameter_start = len(first_lines)

            ql_expected = "ql = feyn.QLattice()\n"
            data_expected = "data = None\n"
            output_expected = 'output_name = "test_output_value"\n'
            kind_expected = "kind = 42\n"

            self.assertEqual(
                ql_expected,
                code_lines[parameter_start],
                "self should be reassigned to ql",
            )
            self.assertEqual(
                data_expected,
                code_lines[parameter_start + 1],
                "Data should be assigned to None",
            )
            self.assertEqual(
                output_expected,
                code_lines[parameter_start + 2],
                "output_name should be assigned to its value",
            )
            self.assertEqual(
                kind_expected,
                code_lines[parameter_start + 3],
                "kind should be assigned to its value",
            )

        with self.subTest("Test that it assigns kwargs arguments"):
            ql = ClassUnderTest()
            current_models = []
            crit = "test_criterion"
            code_lines = ql.expand_auto_run(
                n_epochs=42, criterion=crit, starting_models=current_models
            )

            assert code_lines is not None

            n_epochs_expected = "n_epochs = 42\n"
            criterion_expected = "criterion = crit\n"
            starting_models_expected = "starting_models = current_models\n"

            for line in code_lines:
                if line.startswith("n_epochs ="):
                    self.assertEqual(
                        n_epochs_expected, line, "n_epochs should be assigned"
                    )
                if line.startswith("criterion ="):
                    self.assertEqual(
                        criterion_expected, line, "criterion should be assigned"
                    )
                if line.startswith("starting_models ="):
                    self.assertEqual(
                        starting_models_expected,
                        line,
                        "starting_models should be assigned",
                    )

        with self.subTest("Test that it has its limitations due to frame magic"):
            ql = ClassUnderTest()
            unrelated_variable = 420
            code_lines = ql.expand_auto_run(unrelated_variable)

            assert code_lines is not None

            first_lines = ["# Dependencies\n", "import feyn\n", "\n"]
            first_lines += ["# Parameters\n"]

            parameter_start = len(first_lines)

            data_expected = "data = unrelated_variable\n"

            self.assertEqual(
                data_expected,
                code_lines[parameter_start + 1],
                "Data gets assigned to unrelated variable name",
            )

        with self.subTest(
            "Test that it strips function declaration, self, return and docs"
        ):
            ql = ClassUnderTest()
            code_lines = ql.expand_auto_run()

            assert all("@check_types" not in line for line in code_lines)
            assert all("def auto_run" not in line for line in code_lines)
            assert all("return" not in line for line in code_lines)
            assert all("self" not in line for line in code_lines)

            docs = ql.auto_run.__doc__.split("\n")

            for d in docs:
                if d.lstrip() == "":
                    continue
                for line in code_lines:
                    assert d not in line, f"expected '{d}' to not be in '{line}'"

        with self.subTest("Test that important assignments happen and aren't stripped"):
            ql = ClassUnderTest()
            code_lines = ql.expand_auto_run()

            count = 0
            for line in code_lines:
                if "best = feyn.get_diverse_models" in line:
                    count += 1
            self.assertEqual(
                2,
                count,
                "best should be assigned to get_diverse_models (not stripped by return stripping)",
            )

    @pytest.mark.integration
    def test_expand_auto_run_evaluates(self):
        ql = ClassUnderTest()
        train = pd.DataFrame({"x": [0, 1, 2, 3, 4, 5], "y": [0, 1, 2, 3, 4, 5]})
        code_lines = ql.expand_auto_run(train, "y", n_epochs=1, max_complexity=5)

        code = "".join(code_lines)
        try:
            exec(code)
            assert True
        except Exception as e:
            self.fail(f"Caught exception during evaluation: {e}")
