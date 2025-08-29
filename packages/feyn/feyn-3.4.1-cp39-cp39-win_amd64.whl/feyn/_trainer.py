from typing import Iterable, List, Optional

import numpy as np
from pandas import DataFrame

from feyn import Model

from feyn._criteria import aic, bic, wide_parsimony, _sort_by_readability, _sort_by_structural_diversity
from feyn._qepler import qeplertrainer
from feyn._typings import check_types


@check_types()
def fit_models(
    models: List[Model],
    data: DataFrame,
    loss_function: Optional[str] = None,
    criterion: Optional[str] = None,
    n_samples: Optional[int] = None,
    sample_weights: Optional[Iterable[float]] = None,
    threads: int = 4,
    immutable: bool = False,
) -> List[Model]:
    """Fit a list of models on some data and return a list of fitted models. The return list will be sorted in ascending order by either the loss function or one of the criteria.

    The n_samples parameter controls how many samples are used to train each model. The default behavior is to fit each model once with each sample in the dataset, unless the set is smaller than 10000, in which case the dataset will be upsampled to 10000 samples before fitting.

    The samples are shuffled randomly before fitting to avoid issues with the Stochastic Gradient Descent algorithm.


    Arguments:
        models {List[feyn.Model]} -- A list of feyn models to be fitted.
        data {[type]} -- Data used in fitting each model.

    Keyword Arguments:
        loss_function {Optional[str]} -- The loss function to optimize models for. Can be "squared_error", "absolute_error" or "binary_cross_entropy"
        criterion {Optional[str]} -- Sort by information criterion rather than loss. Either "aic", "bic" or None (loss). (default: {None})
        n_samples {Optional[int]} -- The number of samples to fit each model with. (default: {None})
        sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
        threads {int} -- Number of concurrent threads to use for fitting. (default: {4})
        immutable {bool} -- If True, create a copy of each model and fit those, leaving the originals untouched. This increases runtime. (default: {False})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if there are no samples
        ValueError: if data and sample_weights is not same size
        ValueError: if the loss function is unknown.
        ValueError: if inputs contain a mix of classifiers and regressors

    Returns:
        List[feyn.Model] -- A list of fitted feyn models.
    """
    if len(models) == 0:
        return models

    data_length = len(data)

    if n_samples is None:
        n_samples = max(20000, data_length)
    if n_samples <= 0:
        raise ValueError("More than 0 samples are required for fitting models.")

    if immutable:
        models = [m.copy() for m in models]

    out_specs = set(m.fnames[0] for m in models)
    if len(out_specs) > 1:
        raise ValueError("Input models contain both classifiers and regressors.")

    if loss_function is None:
        if out_specs == {"out-lr:1"}:
            loss_function = "binary_cross_entropy"
        else:
            loss_function = "squared_error"

    losses_list, params_list = qeplertrainer.fit_models(models, data, n_samples, loss_function, sample_weights, threads)

    for ix, m in enumerate(models):
        loss = losses_list[ix]
        params = params_list[ix]

        m.loss_value = loss
        
        m.loss_values.append(loss)

        paramcount = m._paramcount # This is an expensive calculation, so only do it once

        m.bic = bic(m.loss_value, paramcount, data_length, m.kind)
        m.aic = aic(m.loss_value, paramcount, data_length, m.kind)
        m.wide_parsimony = wide_parsimony(m.loss_value, paramcount, data_length,
                                                        len(data.columns), len(m.inputs), m.kind)
        m._sample_count += n_samples
        m.age += 1

        m.params = params

    models = [model for model in models if np.isfinite(model.loss_value)]

    if criterion == "bic":
        models.sort(key=lambda m: m.bic, reverse=False)
    elif criterion == "aic":
        models.sort(key=lambda m: m.aic, reverse=False)
    elif criterion == "wide_parsimony":
        models.sort(key=lambda m: m.wide_parsimony, reverse=False)
    elif criterion == "structural_diversity":
        models = _sort_by_structural_diversity(models)
    elif criterion == "readability":
        models = _sort_by_readability(models, n_samples)
    elif criterion is None:
        models.sort(key=lambda m: m.loss_value, reverse=False)
    else:
        raise Exception(
            "Unknown information criterion %s. Must be 'aic', 'bic' or None)"
            % criterion
        )

    return models
