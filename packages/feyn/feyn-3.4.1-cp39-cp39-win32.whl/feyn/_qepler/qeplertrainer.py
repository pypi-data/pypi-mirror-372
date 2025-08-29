from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
import itertools
import typing

from typing import Dict, Iterable, List, Optional

import numpy as np
from pandas import DataFrame
from pandas.api.types import is_string_dtype, is_extension_array_dtype

import feyn
from feyn._typings import check_types
from . import pandas_lru_cache
import _qepler


@check_types()
def fit_models(
    models: List[feyn.Model],
    data: DataFrame,
    n_samples: int,
    loss: str,
    sample_weights: Optional[Iterable[float]] = None,
    threads: int = 4,
) -> typing.Tuple[List[float], List[Dict]]:
    """Fit a list of models on some data and return a list of fitted models. The return list will be sorted in ascending order by either the loss function or one of the criteria.

    The n_samples parameter controls how many samples are used to train each model. The default behavior is to fit each model once with each sample in the dataset, unless the set is smaller than 10000, in which case the dataset will be upsampled to 10000 samples before fitting.

    The samples are shuffled randomly before fitting to avoid issues with the Stochastic Gradient Descent algorithm.


    Arguments:
        models {List[feyn.Model]} -- A list of feyn models to be fitted.
        data {[type]} -- Data used in fitting each model.

    Keyword Arguments:
        n_samples {Optional[int]} -- The number of samples to fit each model with. (default: {None})
        loss {str} -- The name of the loss function to optimize models for.
        sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
        threads {int} -- Number of concurrent threads to use for fitting. (default: {4})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if there are no samples
        ValueError: if data and sample_weights is not same size
        ValueError: if the loss function is unknown.

    Returns:
        List[typing.Tuple[float, Dict]] -- A list of fitted feyn models.
    """
    if len(models) == 0:
        return models

    sampled_data, sample_weights = _resample_data(data, sample_weights, n_samples)

    # FIX: This replaces the independent scale compuation done on _qepler.interactions.
    # But computes scales on the non upsampled set, might behave slitghly different.
    _initialize_scales_in_params(models, data)
    output = models[0].names[0]

    new_losses = [None] * len(models)
    new_params = [None] * len(models)
    _counter = itertools.count()

    qepler_models = [
        _qepler.Model(
            dnames=m.names,
            fnames=m.fnames,
            params=m.params,
            sample_count=m._sample_count,
            loss=loss,
        )
        for m in models
    ]

    def fitting_thread():
        nonlocal _counter
        while True:
            ix = next(_counter)
            if ix >= len(qepler_models):
                return

            qm = qepler_models[ix]
            new_losses[ix], new_params[ix] = qm._fit(
                xarray=sampled_data,
                yarray=sampled_data[output],
                sample_weights=sample_weights,
            )

    if threads > 1:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(fitting_thread) for _ in range(threads)]
            done, _ = wait(futures, return_when=FIRST_EXCEPTION)

            # Propagate exceptions raised in the threads
            for task in done:
                task.result()
    else:
        fitting_thread()

    return new_losses, new_params


def _resample_data(df: DataFrame, sample_weights, n_samples):
    # Magic support for pandas DataFrame
    data = {}
    for col in df.columns:
        if isinstance(df[col].values, np.ndarray):
            data[col] = df[col].values
        elif is_extension_array_dtype(df[col]) and not is_string_dtype(df[col]):
            data[col] = df[col].array._data
        else:
            data[col] = df[col].to_numpy()

    n_data_rows = len(next(iter(data.values())))

    # Create a sequence of indices from the permutated data of length n_samples
    permutation = np.random.permutation(n_samples) % n_data_rows
    data = {key: values[permutation] for key, values in data.items()}

    if sample_weights is not None:
        s_size = len(sample_weights)
        if not s_size == n_data_rows:
            raise ValueError(
                f"The sizes of data ({n_data_rows}) and sample_weights ({s_size}) do not match."
            )
        # Normalise the sample_weights
        sample_weights = np.multiply(list(sample_weights), 1 / max(sample_weights))
        # Also permute the sample_weights
        sample_weights = sample_weights[permutation]

    return data, sample_weights


def _initialize_scales_in_params(models: List[feyn.Model], data: DataFrame):
    in_scales, out_scales = _compute_scales(data)
    for m in models:
        for ix, fname in enumerate(m.fnames):
            if "qepler_init" in m.params[ix]:
                continue

            if fname == "in-linear:0":
                m.params[ix].update(in_scales[m.names[ix]])
            if fname == "out-linear:1":
                m.params[ix].update(out_scales[m.names[ix]])

        m.params[ix]["qepler_init"] = 1


def _compute_scales(data: DataFrame):
    in_scales = {}
    out_scales = {}
    numeric_columns = data.select_dtypes(include=[np.number]).columns.values
    for col in numeric_columns:
        max_val = data[col].max()
        min_val = data[col].min()
        mean = data[col].mean()
        in_scales[col] = {
            "scale": 2.0 / (max_val - min_val) if max_val > min_val else 1.0,
            "scale_offset": mean,
            "detect_scale": 0,
        }
        out_scales[col] = {
            "scale": (max_val - min_val) / 2.0 if max_val > min_val else 1.0,
            "scale_offset": 0.0,
            "detect_scale": 0,
        }

    for col in data.select_dtypes(include=[np.bool_]).columns.values:
        out_scales[col] = in_scales[col] = {
            "scale": 1,
            "scale_offset": 0.0,
            "detect_scale": 0,
        }

    return in_scales, out_scales
