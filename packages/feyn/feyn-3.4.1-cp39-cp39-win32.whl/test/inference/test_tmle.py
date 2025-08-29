import unittest
import pytest

from feyn.inference import TMLE

import numpy as np
import pandas as pd
import feyn
from feyn._base_reporting_mixin import BaseReportingMixin

from os.path import dirname
filepath = dirname(__file__)


class TestTMLE(unittest.TestCase):

    def setUp(self):
        self.data = {'x': np.array([1, 0, 1, 0]),  # exposure variable
                     'y': np.array([1.5, 0.5, 1.5, 0.5]),  # confounding variable
                     'z': np.array([5.7, 1.2, 5.3, 1.7])}  # output variable

        self.outcome_graph = Fake_outcomeModel()
        self.exposure_graph = Fake_exposureModel()

        self.general_result = TMLE(self.data, self.outcome_graph, self.exposure_graph)
        self.general_result.ATE()

    # Checking for errors:
    def test_outcome_graph_attr_error(self):
        # Setup
        out_graph = 'banana'

        # Execute and Assert
        with self.assertRaises(AttributeError):
            TMLE(self.data, out_graph, self.exposure_graph)

    def test_exposure_graph_attr_error(self):
        # Setup
        expo_graph = 'banana'

        # Result
        with self.assertRaises(AttributeError):
            TMLE(self.data, self.outcome_graph, expo_graph)

    def test_outside_boundary_probability_error(self):
        # Setup
        intruder_list = [-3.4, 0., 2.3, 1.]
        pi_1, pi_0 = [], []
        for value in intruder_list:
            temp_arr = np.array([value, 0.5, 0.6])
            pi_1.append(temp_arr)
            pi_0.append(1 - temp_arr)

        tmle = TMLE(self.data, self.outcome_graph, self.exposure_graph)

        # Result
        for i in range(len(pi_1)):
            with self.assertRaises(ValueError):
                tmle._predefined_covariates(pi_1[i], pi_0[i])

    def test_GLM_error(self):
        # Setup
        data_t = self.data.copy()
        data_t['z'] = np.array([5.5, 1.5, 5.5, 1.5])

        # Result
        with self.assertRaises(Exception):
            tmle = TMLE(data_t, self.outcome_graph, self.exposure_graph)

    # Test if it works with pandas data:
    def test_data_as_pandas(self):
        # Setup
        data_p = pd.DataFrame(self.data)
        tmle = TMLE(data_p, self.outcome_graph, self.exposure_graph)

        # Execute
        tmle.ATE()

        # Result
        assert(tmle.ate == pytest.approx(1.0249, 1e-3))

    # Test some outputs:
    def test_ate(self):
        # Assert
        assert(self.general_result.ate == pytest.approx(1.0249, 1.e-3))  # ATE should be equal to 1.0249 to a sigfinicance of 10^-3

    def test_ate_se(self):
        # Assert
        assert(self.general_result.ate_se == pytest.approx(0.1381, 1.e-3))


class Fake_outcomeModel(feyn.Model, BaseReportingMixin):

    def __init__(self) -> None:
        pass

    def predict(self, X) -> np.ndarray:
        return 3 * X['y'] + X['x']

    @property
    def target(self) -> str:
        return 'z'

    @property
    def features(self):
        return ['x', 'y']


class Fake_exposureModel(feyn.Model, BaseReportingMixin):

    def __init__(self) -> None:
        pass

    def predict(self, X) -> np.ndarray:
        return (X['y'] - 0.45) * 0.90

    @property
    def target(self) -> str:
        return 'x'

    @property
    def features(self):
        return ['y']
