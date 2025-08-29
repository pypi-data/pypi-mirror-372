import numpy as np

from ._structural import _sort_by_structural_diversity, _compute_average_structural_diversity_difference_scores
from ._clustering import _assign_qcells_by_clustering
from ._bootstrap import _assign_qcells_by_bootstrap
from ._readability import _sort_by_readability, _compute_height
from ..tools import kind_to_output_stype

__all__ = [
    "bic",
    "aic",
    "wide_parsimony"
]


def bic(loss_value: float, param_count: int, n_samples: int, kind: str) -> float:
    out_type = kind_to_output_stype(kind)
    if out_type == "f":
        ans = n_samples * np.log(loss_value + 1e-7) + param_count * np.log(n_samples)
    elif out_type == "b":
        ans = n_samples * loss_value * 2 + param_count * np.log(n_samples)
    else:
        raise ValueError()

    return ans


def aic(loss_value: float, param_count: int, n_samples: int, kind: str) -> float:
    out_type = kind_to_output_stype(kind)
    if out_type == "f":
        ans = n_samples * np.log(loss_value + 1e-7) + param_count * 2
    elif out_type == "b":
        ans = n_samples * loss_value * 2 + param_count * 2
    else:
        raise ValueError()

    return ans


def wide_parsimony(loss_value: float, param_count: int, n_samples: int, n_features: int,
                   n_inputs: int, kind: str) -> float:
    out_type = kind_to_output_stype(kind)
    if out_type == "f":
        ans = (n_samples * np.log(loss_value + 1e-7) + param_count * np.log(n_samples)
               + n_inputs * (n_features / n_samples))
    elif out_type == "b":
        ans = (n_samples * loss_value * 2 + param_count * np.log(n_samples)
               + n_inputs * (n_features / n_samples))
    else:
        raise ValueError()

    return ans
