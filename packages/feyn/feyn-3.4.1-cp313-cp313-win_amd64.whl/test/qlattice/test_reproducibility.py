import unittest

import pandas as pd
import feyn


class TestSeedReproducibility(unittest.TestCase):

    def setUp(self) -> None:
        self.data = pd.DataFrame(
            {
                'cat': ['C', 'A', 'T'],
                'num': [1, 2, 3],
                'y': [42, 23, 16]
            }
        )

    def test_sample_models_numerical_inputs(self):
        ql = feyn.QLattice(random_seed = 8363)

        first_models = ql.sample_models(
            input_names=['num'],
            output_name='y'
        )

        ql = feyn.QLattice(random_seed = 8363)
        second_models = ql.sample_models(
            input_names=['num'],
            output_name='y'
        )

        self.assertEqual(first_models, second_models)

    def test_sample_models_categorical_inputs(self):
        ql = feyn.QLattice()
        stypes = {'cat': 'c'}

        ql.reset(8363)
        first_models = ql.sample_models(
            input_names=['cat'],
            output_name='y',
            stypes=stypes
        )

        ql.reset(8363)
        second_models = ql.sample_models(
            input_names=['cat'],
            output_name='y',
            stypes=stypes
        )

        self.assertEqual(first_models, second_models)

    def test_sample_models_mixed_inputs(self):
        ql = feyn.QLattice()
        stypes = {'cat': 'c'}

        ql.reset(8363)
        first_models = ql.sample_models(
            input_names=['num', 'cat'],
            output_name='y',
            stypes=stypes
        )

        ql.reset(8363)
        second_models = ql.sample_models(
            input_names=['num', 'cat'],
            output_name='y',
            stypes=stypes
        )

        self.assertEqual(first_models, second_models)

    def test_fit_models_numerical_inputs(self):
        ql = feyn.QLattice(random_seed=8363)

        first_models = []
        for _ in range(2):
            first_models += ql.sample_models(
                input_names=['num'],
                output_name='y'
            )[:10]
            first_models = feyn.fit_models(first_models, self.data)

        ql = feyn.QLattice(random_seed=8363)
        second_models = []
        for _ in range(2):
            second_models += ql.sample_models(
                input_names=['num'],
                output_name='y'
            )[:10]
            second_models = feyn.fit_models(second_models, self.data)

        self.assertEqual(first_models, second_models)

    def test_fit_models_categorical_inputs(self):
        ql = feyn.QLattice(random_seed=8363)
        stypes = {'cat': 'c'}

        first_models = []
        for _ in range(2):
            first_models += ql.sample_models(
                input_names=['cat'],
                output_name='y',
                stypes=stypes
            )[:10]
            first_models = feyn.fit_models(first_models, self.data)

        ql = feyn.QLattice(random_seed=8363)
        second_models = []
        for _ in range(2):
            second_models += ql.sample_models(
                input_names=['cat'],
                output_name='y',
                stypes=stypes
            )[:10]
            second_models = feyn.fit_models(second_models, self.data)

        self.assertEqual(first_models, second_models)

    def test_fit_models_mixed_inputs(self):
        ql = feyn.QLattice(random_seed=8363)
        stypes = {'cat': 'c'}

        first_models = []
        for _ in range(2):
            first_models += ql.sample_models(
                input_names=self.data.columns,
                output_name='y',
                stypes=stypes
            )[:10]
            first_models = feyn.fit_models(first_models, self.data)

        ql = feyn.QLattice(random_seed=8363)
        second_models = []
        for _ in range(2):
            second_models += ql.sample_models(
                input_names=self.data.columns,
                output_name='y',
                stypes=stypes
            )[:10]
            second_models = feyn.fit_models(second_models, self.data)

        self.assertEqual(first_models, second_models)
