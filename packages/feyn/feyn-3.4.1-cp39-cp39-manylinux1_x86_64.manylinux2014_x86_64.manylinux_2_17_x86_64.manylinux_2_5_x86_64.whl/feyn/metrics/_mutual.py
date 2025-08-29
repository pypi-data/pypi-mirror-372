"""
Code for calculating the mutual information (MI)
between several random variables.
"""

import pandas as pd
import numpy as np
from functools import reduce

from typing import Iterable, List, Optional, Tuple


def calculate_mi(rv_samples: List[Iterable], float_bins: Optional[int] = None) -> float:
    """
    Numpy-based implementation of mutual information for n random variables.
    This can be used for both categorical (discrete) and continuous variables,
    you can have as many as you want of each, in any position in the iterable.

    Arguments:
        rv_samples {Iterable[Iterable]} -- Samples from random variables given inside an iterable.
        In the traditional ML sense, these would be the data of the inputs.

    Keyword Arguments:
        float_bins {Union[Tuple[int], int]} -- Number of bins in which to count numerical random variables.
        If None is given, numerical variables are divided in equally spaced bins given by max{min{n_samples/3, 10}, 2}.

    Returns:
        float -- The mutual information between the input random variables.
    """

    if float_bins is None:
        float_bins = _float_discretization(len(rv_samples[0]))

    # Construct samples and bins
    bins = []
    rv_input = []

    for rv in rv_samples:
        sample_rv, sample_bins = _mi_inputs(rv, float_bins)
        bins.append(sample_bins)
        rv_input.append(sample_rv)

    joint_dist = _normalize_hist(np.histogramdd(rv_input, bins=bins)[0])

    marginals = [_integrate_to(joint_dist, i) for i in range(joint_dist.ndim)]
    outer_dist = _normalize_hist(_nd_outer(*marginals))

    nz_idx = np.nonzero(joint_dist)
    nz_joint = joint_dist[nz_idx]
    nz_outer = outer_dist[nz_idx]

    return np.sum(nz_joint * (np.log(nz_joint) - np.log(nz_outer)))


def _calculate_mi_for_output(
    samples: Iterable, output_mi: Iterable, output_bins: Iterable
) -> np.array:
    sample_rv, sample_bins = _mi_inputs(samples)

    joint_dist = _normalize_hist(
        np.histogramdd([sample_rv, output_mi], bins=[sample_bins, output_bins])[0]
    )

    marginals = [_integrate_to(joint_dist, i) for i in range(joint_dist.ndim)]
    outer_dist = _normalize_hist(_nd_outer(*marginals))

    nz_idx = np.nonzero(joint_dist)
    nz_joint = joint_dist[nz_idx]
    nz_outer = outer_dist[nz_idx]

    return np.sum(nz_joint * (np.log(nz_joint) - np.log(nz_outer)))


def calculate_mi_for_output(df: pd.DataFrame, output_name: str) -> pd.DataFrame:
    """Calculates the mutual information between each column of the DataFrame and the output column.

    Arguments:
        df {pd.DataFrame} -- DataFrame
        output_name {str} -- Name of the output column

    Returns:
        pd.DataFrame -- A DataFrame containing the mutual information between each input and the output
    """
    output_mi, output_bins = _mi_inputs(df[output_name])

    inputs = df.columns[df.columns != output_name].values

    return df[inputs].apply(
        lambda col: _calculate_mi_for_output(col, output_mi, output_bins), axis=0
    )


def _mi_inputs(samples: Iterable, float_bins: int = 5) -> Tuple[List, int]:
    if type(samples).__name__ == "Series":
        sample = samples.iloc[0]
    else:
        sample = samples[0]

    if isinstance(sample, float) and sample != int(sample):
        return samples, float_bins
    else:
        if isinstance(sample, (np.integer, int, float, np.float64)):
            return samples, len(np.unique(samples)) + 1
        else:
            return _encode(samples)


def _float_discretization(n_samples):
    """
    Calculate the discretization of continuous inputs by cutting the range of values in q equally spaced intervals,
    where q = max{min{n_samples / 3, 10}, 2}.
    """
    return int(np.maximum(np.minimum(n_samples / 3, 10), 2))


def _nd_outer(*vecs):
    """
    Calculate the outer product of n vectors, given as positional arguments. Return an n-dimensional array as a result.
    """
    return reduce(np.multiply.outer, vecs)


def _integrate_to(arr, axis):
    """
    Given an n-dim array arr and an axis, sum all other axes to that one.
    """
    all_axes = range(arr.ndim)
    sum_these = tuple(ax for ax in all_axes if ax != axis)
    return arr.sum(axis=sum_these)


def _normalize_hist(arr):
    """
    Given an n-d array arr that represents a histogram, move from talking about counts to talking about probabilities (not probability densities).
    """
    return arr / arr.sum()


def _encode(discrete_rv):
    """
    Encode a 1D discrete random variable that does not contain integers to one that does.
    """
    uniq, codes = np.unique(discrete_rv, return_inverse=True)
    return codes, len(uniq)
