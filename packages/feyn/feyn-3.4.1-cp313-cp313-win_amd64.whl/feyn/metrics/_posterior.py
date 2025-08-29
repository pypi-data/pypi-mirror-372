import numpy as np
from typing import Iterable, List


def get_posterior_probabilities(list_bic: Iterable[float]) -> List[float]:
    """Get posterior probabilities from a list of BICs

    Arguments:
        list_bic {Iterable[float]} -- The list of BICs

    Raises:
        TypeError: if inputs don't match the correct type.

    Returns:
        List[float] -- Posterior probabilities
    """

    array_bic = np.array(list(list_bic), dtype=np.longdouble)
    max_bic = array_bic.max()
    array_bic = array_bic - max_bic
    array_bic = np.where(array_bic > 100, 100, array_bic)

    return [np.exp(-(1 / 2) * bic) / sum(np.exp(-(1 / 2) * array_bic)) for bic in array_bic]

