import pytest
import unittest
from numpy.testing import assert_array_almost_equal

from feyn.metrics import get_posterior_probabilities

class TestPosterior(unittest.TestCase):

    def test_posterior_probs(self):
        list_bic = [1,2]
        actuals = get_posterior_probabilities(list_bic)
        expected = [0.6224593312018546, 0.37754066879814546]
        assert_array_almost_equal(actuals, expected)
