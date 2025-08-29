import numpy as np
from typing import Iterable

from feyn.metrics._linear import calculate_pc


def _rankdata(X: Iterable):
    arr = np.copy(X)

    # arr[sorter] returns arr sorted
    sorter = np.argsort(arr)

    inv = np.zeros(sorter.size, dtype=np.intp)

    # returns the ranks of each value in arr. For example if arr = [2,3,1,3] then this returns [1,2,0,3]
    inv[sorter] = np.arange(sorter.size, dtype=np.intp)

    # sorts arr
    arr = arr[sorter]

    # returns True if it's value is not equal to it's left neighbour
    # For example if arr = [1,2,3,3] then obs = [True, True, True, False]
    obs = np.r_[True, arr[1:] != arr[:-1]]

    dense = obs.cumsum()[inv]

    # cumulative counts of each unique value. For example if arr = [1,2,3,3] then count = [0,1,2,4]
    count = np.r_[np.nonzero(obs)[0], len(obs)]

    return 0.5 * (count[dense] + count[dense - 1] + 1)


def calculate_spear(X: Iterable, Y: Iterable):
    """Calculate the Spearson's correlation coefficient
    for data sampled from two random variables X and Y.

    Arguments:
        X {Iterable} -- First 1D vector of random data.
        Y {Iterable} -- First 1D vector of random data.

    Returns:
        float -- The correlation coefficient.
    """

    rnkX = _rankdata(X)
    rnkY = _rankdata(Y)

    return calculate_pc(rnkX, rnkY)
