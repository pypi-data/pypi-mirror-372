import unittest
import pytest

from feyn.insights import FeatureImportanceTable
import feyn
import pandas as pd
import numpy as np

from os.path import dirname
filepath = dirname(__file__)

from .. import quickmodels

class TestImportanceTable(unittest.TestCase):

    def setUp(self):
        self.data = pd.read_csv(f'{filepath}/simple_data.csv')
        self.data['extra'] = 42

        self.graph = quickmodels.get_fixed_model()

        self.shap_values = self.data[['shap_x', 'shap_y']].values

        self.coef = [1, 3]

    def test_that_it_runs(self):
        table = FeatureImportanceTable(self.graph, self.data)
        assert table is not None, "Heatmap should be computed"

    def test_get_importances(self):
        # Most of this will be tested in KernelSHAP, but let's see if it does what we expect:
        importances, bg_importances = FeatureImportanceTable._get_importances(self.graph, self.data, None, 100)

        # Both are computed on the same dataset, so should be the same
        # All used features should have a shap value
        assert self.np_float_equal(importances[:,:2], self.shap_values)
        assert self.np_float_equal(bg_importances[:,:2], self.shap_values)

        # And all unused features should be 0
        assert (importances[:,2:] == 0).all()
        assert (bg_importances[:,2:] == 0).all()

    def xtest_get_importances_max_ref_low(self):
        """
        I'm sorry if I'm flaky.
        I really should be not equal between arrays, but sometimes SHAP might get lucky to be within float comparison limits?
        """
        # Most of this will be tested in KernelSHAP, but let's see if it does what we expect:
        importances, bg_importances = FeatureImportanceTable._get_importances(self.graph, self.data, self.data, 1)

        # Background importances is now computed for a single sample, so we only get one row back
        assert bg_importances.shape == (1, 6)
        # And it should be different from the importances (due to imprecision)
        assert self.np_float_equal(bg_importances[:1,:2], importances[:1,:2], 0.01) == False

        # And all unused features should still be 0
        assert (bg_importances[:,2:] == 0).all()

    def test_calculate_max_value_no_bg_data(self):
        faux_importances = np.array([[1, 3, 5, 2, 4]])

        absmax = FeatureImportanceTable._calculate_max_value(faux_importances, None, None)
        assert absmax == faux_importances.max()

    def test_calculate_max_value_with_bg_data(self):
        faux_bg_data = np.array([[1, 2, 3, 4, 5]])
        faux_importances, faux_bg_importances = np.array([[1, 3, 5, 2, 4]]), np.array([[-10, -5, 0, 5, 7]])

        absmax = FeatureImportanceTable._calculate_max_value(faux_importances, faux_bg_importances, faux_bg_data)
        assert absmax == np.abs(faux_bg_importances.min())

    def test_calculate_max_value_with_bg_data_lower_refs(self):
        faux_bg_data = np.array([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]])
        faux_importances, faux_bg_importances = np.array([[1, 3, 5, 2, 4]]), np.array([[-10, -5, 0, 5, 7]])

        absmax = FeatureImportanceTable._calculate_max_value(faux_importances, faux_bg_importances, faux_bg_data)

        # Using less of the bg_data to compute absmax results in adding the standard deviation for visual purposes
        std_dev = np.vstack([faux_importances, faux_bg_importances]).std()
        assert absmax == (np.abs(faux_bg_importances.min()) + std_dev)

    def np_float_equal(self, expected, actual, epsilon=0.01):
        return (expected - actual <= 0.01).all()
