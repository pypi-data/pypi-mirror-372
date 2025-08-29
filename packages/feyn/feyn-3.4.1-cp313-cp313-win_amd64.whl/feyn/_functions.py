import numpy as np

# TODO: This breaks some qepler philosophies, the model needs to know what trainer
# was used to replicate the function protections of that trainer.
import _qepler


def cat_func(params, vcat):
    cat_weights = dict(params["categories"])
    return np.array([cat_weights.get(c, 0.0) for c in vcat]) + params["bias"]


def in_linear_func(params, v):
    if not np.isfinite(v).all():
        raise ValueError("nan values in input")
    return (v - params["scale_offset"]) * params["scale"] * params["w"] + params["bias"]


def exp_protected(params, v):
    ix_bad = v > _qepler.EXP_MAX
    v[ix_bad] = _qepler.EXP_MAX
    return np.exp(v)


def inverse_protected(params, v):
    ix_bad = np.abs(v) < _qepler.DIVISOR_ABSMIN
    ix_bad_pos = ix_bad & (v > 0)
    ix_bad_neg = ix_bad & (v <= 0)
    v[ix_bad_pos] = _qepler.DIVISOR_ABSMIN
    v[ix_bad_neg] = -_qepler.DIVISOR_ABSMIN
    return 1 / v


def log_protected(params, v):
    ix_bad = v < _qepler.LOG_MIN
    v[ix_bad] = _qepler.LOG_MIN
    return np.log(v)


def sqrt_protected(params, v):
    ix_bad = v < _qepler.SQRT_MIN
    v[ix_bad] = _qepler.SQRT_MIN
    return np.sqrt(v)


def squared_protected(params, v):
    ix_bad = v > _qepler.SQUARED_MAX
    v[ix_bad] = _qepler.SQUARED_MAX
    return v * v


FNAME_MAP = {
    "in-cat:0": {"paramcount": 0, "func": cat_func},
    "in-linear:0": {"paramcount": 0, "func": in_linear_func},
    "out-linear:1": {
        "paramcount": 0,
        "func": lambda params, v: (v * params["w"] + params["bias"]) * params["scale"],
    },
    "out-lr:1": {
        "paramcount": 0,
        "func": lambda params, v: 1 / (1 + np.exp(-(v * params["w"] + params["bias"]))),
    },
    "exp:1": {
        "paramcount": 1,
        "func": lambda params, v: np.exp(v),
        "func_protected": exp_protected,
    },
    "gaussian:1": {"paramcount": 3, "func": lambda params, v: np.exp(-(v * v / 0.5))},
    "inverse:1": {
        "paramcount": 1,
        "func": lambda params, v: 1 / v,
        "func_protected": inverse_protected,
    },
    "linear:1": {
        "paramcount": 2,
        "func": lambda params, v: v * params["w"] + params["bias"],
    },
    "log:1": {
        "paramcount": 1,
        "func": lambda params, v: np.log(v),
        "func_protected": log_protected,
    },
    "sqrt:1": {
        "paramcount": 1,
        "func": lambda params, v: np.sqrt(v),
        "func_protected": sqrt_protected,
    },
    "squared:1": {
        "paramcount": 1,
        "func": lambda params, v: v * v,
        "func_protected": squared_protected,
    },
    "tanh:1": {"paramcount": 1, "func": lambda params, v: np.tanh(v)},
    "add:2": {"paramcount": 1, "func": lambda params, v1, v2: v1 + v2},
    "gaussian:2": {
        "paramcount": 4,
        "func": lambda params, v1, v2: np.exp(-(v1 * v1 / 0.5 + v2 * v2 / 0.5)),
    },
    "multiply:2": {"paramcount": 2, "func": lambda params, v1, v2: v1 * v2},
}

FNAMES = [fname for fname in FNAME_MAP if "-" not in fname]


MIGRATION_CODES_TO_FNAME_MAP = {
    1000: "exp:1",
    1001: "gaussian:1",
    1002: "inverse:1",
    1003: "linear:1",
    1004: "log:1",
    1005: "sqrt:1",
    1006: "squared:1",
    1007: "tanh:1",
    2000: "add:2",
    2001: "gaussian:2",
    2002: "multiply:2",
}

MIGRATION_FNAME_TO_FNAME_MAP = {
    "out:lr": "out-lr:1",
    "out:linear": "out-linear:1",
    "in:linear": "in-linear:0",
    "in:cat": "in-cat:0",
}
