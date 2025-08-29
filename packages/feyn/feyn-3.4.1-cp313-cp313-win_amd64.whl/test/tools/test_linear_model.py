import numpy as np
import pandas as pd
import unittest

from feyn.tools._linear_model import LinearRegression

class TestLinearModel(unittest.TestCase):
    def setUp(self):
        columns = ['x', 'y', 'z']
        data = np.array([
                [0.0,0.9580983248992215,2.8742949746976647],
                [0.1111111111111111,0.043144590390047144,0.24054488228125254],
                [0.2222222222222222,0.6730362544412105,2.241330985545854],
                [0.3333333333333333,0.6390147413645756,2.2503775574270604],
                [0.4444444444444444,0.35831378863779606,1.5193858103578326],
                [0.5555555555555556,0.4588934755427997,1.9322359821839548],
                [0.6666666666666666,0.14873218040843805,1.112863207891981],
                [0.7777777777777777,0.7509113234375118,3.030511748090313],
                [0.8888888888888888,0.9205461414036025,3.6505273130996962],
                [1.0,0.30628971682882544,1.9188691504864763],
        ])

        self.df = pd.DataFrame(data, columns=columns)

        self.coef = [1, 3]

    def test_lr_against_baseline(self):
        lr = LinearRegression(fit_intercept=False)
        X = self.df[['x', 'y']]
        y = self.df['z']

        lr.fit(X.values, y.values)
        predictions = lr.predict(X.values)

        self.assert_somewhat_equal(predictions, y)
        self.assert_somewhat_equal(lr.coef, self.coef)

    def assert_somewhat_equal(self, expected, actual, epsilon=0.01):
        for i, act in enumerate(actual):
            assert(abs(act - expected[i]) <= epsilon)
