import unittest
import warnings
import numpy as np
import pandas as pd

from feyn import fit_models

from test import quickmodels

import pytest


@pytest.mark.filterwarnings("ignore:ComplexWarning")
class TestQLattice(unittest.TestCase):

    def setUp(self):

        self.data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

    def set_input_dtype(self, data, type):
        output_type = data[data.columns[-1]].dtype
        for col in data.columns[:-1]:
            data[col] = data[col].astype(type)
            self.assertEqual(data[col].dtype, type)

        self.assertEqual(data[data.columns[-1]].dtype, output_type)

        return data

    def test_fit_models(self):
        models = [quickmodels.get_simple_binary_model(["age", "smoker"], "insurable")]

        with self.subTest("Can fit dtype int8"):
            self.data = self.set_input_dtype(self.data, "int8")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype uint8"):
            self.data = self.set_input_dtype(self.data, "uint8")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype bool"):
            self.data = self.set_input_dtype(self.data, "bool")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype int16"):
            self.data = self.set_input_dtype(self.data, "int16")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype int32"):
            self.data = self.set_input_dtype(self.data, "int32")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype float32"):
            self.data = self.set_input_dtype(self.data, "float32")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can fit dtype float64"):
            self.data = self.set_input_dtype(self.data, "float64")
            fit_models(models, self.data, n_samples=4)

        with self.subTest("Can not fit dtype float16"):
            self.data = self.set_input_dtype(self.data, "float16")
            with self.assertRaises(ValueError) as ctx:
                fit_models(models, self.data, n_samples=4)

            self.assertEqual(str(ctx.exception), "Data contains unsupported dtypes")

        with self.subTest("Can not fit dtype uint16"):
            self.data = self.set_input_dtype(self.data, "uint16")
            with self.assertRaises(ValueError) as ctx:
                fit_models(models, self.data, n_samples=4)

            self.assertEqual(str(ctx.exception), "Data contains unsupported dtypes")

        with self.subTest("Can not fit dtype uint32"):
            self.data = self.set_input_dtype(self.data, "uint32")
            with self.assertRaises(ValueError) as ctx:
                fit_models(models, self.data, n_samples=4)

            self.assertEqual(str(ctx.exception), "Data contains unsupported dtypes")

        with self.subTest("Can not fit dtype uint64"):
            self.data = self.set_input_dtype(self.data, "uint64")
            with self.assertRaises(ValueError) as ctx:
                fit_models(models, self.data, n_samples=4)

            self.assertEqual(str(ctx.exception), "Data contains unsupported dtypes")

        with self.subTest("Can not fit dtype float96/128"):
            self.data = self.set_input_dtype(self.data, "longdouble")
            with self.assertRaises(ValueError) as ctx:
                fit_models(models, self.data, n_samples=4)

            self.assertEqual(str(ctx.exception), "Data contains unsupported dtypes")
