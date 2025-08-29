"""Helper functions that may make it easier to interact with feyn."""

import logging
import numpy as np

from pandas import DataFrame
from typing import List, Iterable, Tuple

import feyn

_logger = logging.getLogger(__name__)


def _get_strata_indices(df: DataFrame, stratify_cols: List[str]) -> List[List[int]]:
    """Returns a list of strata, where each stratum is a list of indices"""
    if stratify_cols is None or len(stratify_cols) == 0:
        # If no stratification columns are specified, return the entire dataset as a single stratum
        return [(None, df.index.to_numpy())]
    elif len(stratify_cols) == 1:
        # If only one stratification column is specified, return a list of strata
        return [
            (name, stratum.index.to_numpy())
            for name, stratum in df.groupby(stratify_cols[0], dropna=False)
        ]
    else:
        # If multiple stratification columns are specified, return a list of strata
        return [
            (name, stratum.index.to_numpy())
            for name, stratum in df.groupby(stratify_cols, dropna=False)
        ]


def _stratified_split(
    data: DataFrame, ratios: List[float], stratify_cols: List[str], random_state: int
):
    """Returns a list of stratified subsets, where each subset is a list of indices"""
    rng = np.random.default_rng(seed=random_state)

    n_subsets = len(ratios)
    subsets = [[] for _ in range(n_subsets)]

    # Normalize the ratios
    ratios = np.array(ratios) / sum(ratios)

    # Get the stratified indices
    strata = _get_strata_indices(data, stratify_cols)

    # Validate that each stratum has enough samples to split into subsets
    _validate_strata(strata, ratios, stratify_cols)

    # Loop through each stratum combination and split them by the ratios
    for _, stratum in strata:
        # Shuffle the indices of the current stratum
        rng.shuffle(stratum)

        # Compute the sizes of each subset, ensuring each subset gets a fair share of each stratum
        subset_sizes = [round(len(stratum) * ratio) for ratio in ratios]

        # Adjust a random subset size to ensure that the sum of the subset sizes equals the size of the stratum
        size_diff = len(stratum) - sum(subset_sizes)
        subset_sizes = _adjust_random_subset(size_diff, subset_sizes, rng)

        # Compute the locations to split the data at based on the ratioed subsets
        locs = np.cumsum(subset_sizes[:-1])

        # Split the indices into subsets at those locations
        indices = np.split(stratum, locs)

        # Append the indices to their respective subsets
        for i in range(n_subsets):
            subsets[i].extend(indices[i])

    _validate_ratios(subsets, ratios)

    return subsets


def _adjust_random_subset(size_diff, subset_sizes, rng):
    _logger.debug(f"Subset sizes prior to adjustment: {str(subset_sizes)}.")

    max_retries = np.abs(size_diff) + 1

    while size_diff != 0:
        _logger.debug(f"Current sum difference from stratum length: {size_diff}")
        candidates = []

        # Try to to the full adjustment
        adjustment = size_diff
        while len(candidates) == 0:
            for i, size in enumerate(subset_sizes):
                # Ensure only subsets larger than the size difference sample get reduced if the difference requires taking away samples from a set.
                if (size + adjustment) > 0:
                    candidates.append((i, size))

            # If no candidates were found, halve the adjustment, rounded down and try again
            if len(candidates) == 0:
                prev_adj = adjustment
                adjustment = adjustment // 2

                if prev_adj == adjustment or adjustment == 0:
                    # We can't reduce the adjustment further - this means there are not enough samples to go around.
                    raise ValueError(
                        f"Not enough samples to distribute into {len(subset_sizes)} subsets"
                    )

                _logger.debug(
                    f"No single subset large enough to make up the difference in split sizes, reducing difference to adjust more sets. New adjustment: {adjustment}"
                )

        _logger.debug(f"Subsets qualified for adjustment: {str(candidates)}")

        # Choose a random candidate to adjust
        n_candidates = len(candidates)
        choice = int(n_candidates * rng.random())

        # Perform the adjustment to the chosen candidate
        _logger.debug(f"Adjusting subset {str(choice)}")
        subset_sizes[candidates[choice][0]] += adjustment

        # Recompute the size difference and go through another iteration if there's still something to make up for
        size_diff = size_diff - adjustment

        # Failsafe, shouldn't happen.
        if max_retries == 0:
            raise RuntimeError(
                "Unexpected error while distributing samples, try different parameters."
            )
        max_retries = max_retries - 1

    _logger.debug(f"Subset sizes after adjustment: {str(subset_sizes)}.")
    return subset_sizes


def _validate_ratios(subsets, ratios, threshold=0.1):
    sizes = [len(subset) for subset in subsets]
    total_size = sum(sizes)

    subset_ratios = [size / total_size for size in sizes]
    for split, sr in enumerate(subset_ratios):
        if np.abs(sr - ratios[split]) > threshold:
            _logger.warning(
                f"The sample count in one of the subsets deviates from expected ratio by {np.abs(sr - ratios[split]):.3f}. Do you have enough data to split?"
            )


def _validate_strata(
    data_strata: List[Tuple[str, Iterable]],
    ratios: List[float],
    stratify_cols: List[str],
):
    n_ratios = len(ratios)
    for name, stratum in data_strata:
        # Check if stratum has enough samples to split into n sets
        if len(stratum) < n_ratios:
            if name is not None:
                raise ValueError(
                    f"Not enough samples in stratum {stratify_cols}: {name} to stratify into {n_ratios} sets"
                )
            else:
                raise ValueError(
                    f"Not enough samples in data to split into {n_ratios} sets"
                )


def split(
    data: DataFrame,
    ratio: List[float] = [0.75, 0.25],
    stratify: List[str] = None,
    random_state: int = None,
) -> List[DataFrame]:
    """
    Split datasets into randomized subsets.

    This function is used to split a dataset into random subsets - typically training and test data.

    The input dataset should be either a pandas DataFrames or a dictionary of numpy arrays. The ratio parameter controls how the data is split, and how many subsets it is split into. The ratio list is normalised before splitting, so [1., 1.] results in a 50/50 split, [1., 1., 1.] in an equal 3-way split, etc.

    By providing a list of column names to the stratify parameter, you can also choose to stratify the splits according to one or more columns.

    Example: Split data in the ratio 2:1 into train and test data
    >>> train, test = feyn.tools.split(data, [2,1])

    Example: Split data in to train, test and validation data. 80% training data and 10% validation and holdout data each
    >>> train, validation, holdout = feyn.tools.split(data, [.8, .1, .1])

    Arguments:
        data {DataFrame} -- The data to split.

    Keyword Arguments:
        ratio {List[float]} -- The size ratio of the resulting subsets. (default: {[0.75, 0.25]})
        stratify {List[str]} -- The names of columns to stratify by. (default: {None})
        random_state {int} -- The random state of the split (integer) (default: {None})

    Returns:
        List[DataFrame] -- A list of the subsets of the dataset.

    Raises:
        ValueError -- If not enough samples remain in the data or a stratum of the data to split into the number of subsets required

    Warnings:
        If the resulting subsets are not reasonably within the provided ratios, indicating a dataset that is too small or stratifications that has too few samples.
    """
    if type(data).__name__ != "DataFrame":
        # upconvert to a DataFrame before creating stratified indices
        _logger.warning(
            "Deprecation: using dicts of numpy arrays are deprecated and will be removed in future versions of Feyn."
        )
        data = DataFrame(data)

    subset_indices = _stratified_split(data, ratio, stratify, random_state)

    result = []
    for indices in subset_indices:
        result.append(data.loc[indices])

    return result


def _select_top_inputs(df: DataFrame, output_name: str, n: int = 25):
    """Selects the top `n` most important inputs based on mutual information.

    Arguments:
        df {DataFrame} -- The dataframe to select inputs for.
        output_name {str} -- The output to measure against.

    Keyword Arguments:
        n {int} -- Max amount of inputs to include in result (default: {25}).

    Returns:
        list -- List of top inputs according to mutual information sorted by importance.
    """
    res = {}
    # Compute mutual information
    for input in df.columns:
        if input == output_name:
            continue
        v = df[[input, output_name]].values.T
        mi = feyn.metrics.calculate_mi(v, float_bins=5)
        res[input] = mi

    # Sort by mutual information
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}

    return list(res)[:n] + [output_name]


def estimate_priors(df: DataFrame, output_name: str, floor: float = 0.1):
    """Computes prior probabilities for each input based on mutual information.
    The prior probability of an input denotes the initial belief of its importance in predicting the output before fitting a model.
    The higher the prior probability the more important the corresponding feature is believed to be.

    Arguments:
        df {DataFrame} -- The dataframe to calculate priors for.
        output_name {str} -- The output to measure against.

    Keyword Arguments:
        floor {float} -- The minimum value for the priors (default: {0.1}).

    Returns:
        dict -- a dictionary of feature names and their computed priors.
    """

    inputs = df.columns[df.columns != output_name].values

    res = feyn.metrics.calculate_mi_for_output(df, output_name)
    res = np.array(res)

    sorted_index = (-res).argsort()  # note: (-res).argsort() is just reverse argsort
    res = 1 - np.arange(len(res)) / 100
    res[res < floor] = floor

    return dict(zip(inputs[sorted_index], res))
