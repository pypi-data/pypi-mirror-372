from typing import List
import feyn
import functools
import sys


fname_to_complexity = {
    "exp:1": 4,
    "gaussian:1": 5,
    "inverse:1": 2,
    "linear:1": 1,
    "log:1": 4,
    "sqrt:1": 4,
    "squared:1": 2,
    "tanh:1": 5,
    "add:2": 1,
    "gaussian:2": 6,
    "multiply:2": 2,
    "in-cat:0": 0,
    "in-linear:0": 0,
    "out-linear:1": 0,
    "out-lr:1": 0,
}


def _compute_height(ix: int, model: feyn.Model):
    p = model._program
    arity = p.arity_at(ix)

    if arity == 0:
        return 0
    elif arity == 1:
        return 1 + _compute_height(ix + 1, model)
    elif arity == 2:
        return 1 + min(
            _compute_height(ix + 1, model),
            _compute_height(p.find_end(ix + 1), model)
        )
    else:
        raise ValueError()


def _compute_model_readability_score(model: feyn.Model):
    score = functools.reduce(
        lambda acc, ix:
        acc + _compute_height(ix, model) * fname_to_complexity[model.fnames[ix]],
        range(len(model)),
        0,
    )
    return score


def _sort_by_readability(models: List[feyn.Model], n_samples: int):
    def _combined_score(model: feyn.Model):
        if model.loss_value is None:
            return sys.maxsize
        else:
            return n_samples * model.loss_value + model.readability

    for m in models:
        m.readability = _compute_model_readability_score(m)

    models = sorted(models, key=_combined_score, reverse=False)

    return models
