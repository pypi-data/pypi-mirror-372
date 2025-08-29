import unittest
from feyn.insights import KernelShap
from feyn.insights._shap._explainermodel import ExplainerModel

import numpy as np
import pandas as pd

from .. import quickmodels

from os.path import dirname
filepath = dirname(__file__)

class TestKernelShap(unittest.TestCase):

    def setUp(self):
        data = pd.read_csv(f'{filepath}/simple_data.csv')
        data['extra'] = 42

        self.shap_values = data[['shap_x', 'shap_y']].values

        # Shuffle the columns to make sure we test things that are indexed weird
        self.data = data.loc[:, ['extra', 'y', 'z', 'x']]
        self.coef = [1, 3]

    def test_combination_matrix(self):
        expected = np.array([[1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1]])
        em = ExplainerModel(2, bg_data={'x': np.array([1])})

        assert (expected == em.X).all()

    def test_explainer_unwrap(self):
        expected = np.array([[1, 4], [2, 5], [3, 6]])
        unwrapped = ExplainerModel._unwrap_np_dict({
                                        'x': np.array([1, 2, 3]),
                                        'y': np.array([4, 5, 6])
        })

        assert (expected == unwrapped).all()

    def test_against_established_baseline(self):
        graph = quickmodels.get_fixed_model()

        IKS = KernelShap(graph, self.data)
        values = IKS.SHAP(self.data)

        values = pd.DataFrame(values, columns=self.data.columns)

        for i, row in values.iterrows():
            self.assertEqual(0, row['z'])
            self.assertEqual(0, row['extra'])
            shap_values = row[['x', 'y']].values

            self.assert_somewhat_equal(shap_values, self.shap_values[i])

    def test_using_numpy_dicts(self):
        graph = quickmodels.get_fixed_model()

        data_dict = {col: self.data[col].values for col in self.data.columns}
        IKS = KernelShap(graph, data_dict)
        values = IKS.SHAP(data_dict)

        values = pd.DataFrame(values, columns=self.data.columns)

        for i, row in values.iterrows():
            self.assertEqual(0, row['z'])
            self.assertEqual(0, row['extra'])
            shap_values = row[['x', 'y']].values

            self.assert_somewhat_equal(shap_values, self.shap_values[i])

    def test_max_samples(self):
        graph = quickmodels.get_fixed_model()

        IKS = KernelShap(graph, self.data, max_samples=1000)
        self.assertEqual(len(self.data), IKS.explainer_model.no_samples, "sample size should be equal to or smaller than data size")

        IKS = KernelShap(graph, self.data, max_samples=1)
        self.assertEqual(1, IKS.explainer_model.no_samples, "sample size should be equal to or smaller than data size")

    def test_single_sample(self):
        graph = quickmodels.get_fixed_model()

        IKS = KernelShap(graph, self.data)
        values = IKS.SHAP(self.data.loc[5:5])

        # To make it easier to validate the results...
        values = pd.DataFrame(values, columns=self.data.columns)
        self.assertEqual(1, len(values))

        self.assertEqual(0, values['z'][0])
        self.assertEqual(0, values['extra'][0])
        shap_values = values[['x', 'y']].values[0]

        self.assert_somewhat_equal(shap_values, self.shap_values[5], epsilon=0.001)

    def test_multi_cat_model(self):
        model = quickmodels.get_simple_binary_model(['x', 'cat'], 'target', stypes={'cat': 'cat'})

        self.data['cat'] = 'badger'

        baseline = model.predict(self.data).mean()
        expected_shap_values = model.predict(self.data) - baseline

        IKS = KernelShap(model, self.data)
        values = IKS.SHAP(self.data.iloc[0:1])
        self.assertEqual(1, len(values))

        values = pd.DataFrame(values, columns=self.data.columns)

        shap_values = values[['x', 'cat']].values[0]
        self.assertAlmostEqual(expected_shap_values[0], shap_values[0])


    def test_single_feature_models(self):
        model = quickmodels.get_unary_model(['x'], 'target')
        baseline = model.predict(self.data).mean()
        expected_shap_values = model.predict(self.data) - baseline

        IKS = KernelShap(model, self.data)
        values = IKS.SHAP(self.data.iloc[0:1])

        values = pd.DataFrame(values, columns=self.data.columns)
        self.assertEqual(1, len(values))

        self.assertEqual(0, values['z'][0])
        self.assertEqual(0, values['extra'][0])
        shap_values = values[['x']].values[0]

        self.assertAlmostEqual(expected_shap_values[0], shap_values[0])

    def test_many_feature_models(self):
        model = quickmodels.get_unary_model(['x'], 'target')

        baseline = model.predict(self.data).mean()
        # Only expect one feature to matter
        expected_shap_values = model.predict(self.data) - baseline

        IKS = KernelShap(model, self.data)
        values = IKS.SHAP(self.data.iloc[0:1])

        values = pd.DataFrame(values, columns=self.data.columns)

        # Please be virtually 0 for unused features
        self.assertAlmostEqual(0, abs(values['z'][0]))
        self.assertAlmostEqual(0, abs(values['extra'][0]))
        self.assertAlmostEqual(0, abs(values['y'][0]))

        shap_values = values[['x']].values[0]

        self.assertAlmostEqual(expected_shap_values[0], shap_values[0])

    def assert_somewhat_equal(self, expected, actual, epsilon=0.01):
        for i, act in enumerate(actual):
            assert(abs(act - expected[i]) <= epsilon)
