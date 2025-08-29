import unittest

import numpy as np
import pandas as pd

from .. import quickmodels

class TestModelActivations(unittest.TestCase):

    def test_computes_activations_dict(self):
        model = quickmodels.get_identity_model()

        x = np.array([1,2,3,4])
        activations = model._get_activations({"x": x})
        np.testing.assert_array_equal(activations[1], x*.5-.5)
        np.testing.assert_array_equal(activations[0], x)

    def test_activations_df(self):
        model = quickmodels.get_identity_model()

        x = np.array([1,2,3,4])
        df = pd.DataFrame({"x": x})

        activations = model._get_activations(df)
        np.testing.assert_array_equal(activations[1], x*.5-.5)
        np.testing.assert_array_equal(activations[0], x)

    def test_activations_df_row(self):
        model = quickmodels.get_identity_model()

        x = np.array([1,2,3,4])
        df = pd.DataFrame({"x": x})

        activations = model._get_activations(df.loc[1])
        np.testing.assert_array_equal(activations[1], x[1]*.5-.5)
        np.testing.assert_array_equal(activations[0], x[1])
