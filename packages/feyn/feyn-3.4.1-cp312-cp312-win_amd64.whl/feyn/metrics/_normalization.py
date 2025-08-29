from feyn.metrics import calculate_mi
from typing import Iterable

# Note: Strehl and Ghosh (2002) has a normalised MI variant as NMI(p_km) = MI(p_km)/sqrt(H(k))*sqrt(H(m))


def _normalized_redundancy(d1, d2):
    I = calculate_mi([d1, d2])
    H1, H2 = _entropy(d1), _entropy(d2)

    redundancy = I / (H1 + H2)
    r_max = min(H1, H2) / (H1 + H2)

    if r_max == 0:
        return redundancy

    return redundancy / r_max


def _entropy(X):
    # As a simple hack, the entropy of a variable is the same as the mutual information with itself
    return calculate_mi([X, X])


def _normalized_total_correlation(d1, d2):
    I = calculate_mi([d1, d2])

    H1, H2 = _entropy(d1), _entropy(d2)
    return I / min(H1, H2)


def normalized_mi(d1: Iterable, d2: Iterable, method="redundancy"):
    """Get the normalized mutual information between two distributions.

    Arguments:
        d1 {Iterable} -- distribution 1
        d2 {Iterable} -- distribution 2

    Keyword Arguments:
        method {str} -- The method to use for normalisation. Options are "norm", "redundancy" and "total_correlation" (default: {"redundancy"})

    Returns:
        float -- The normalised mutual information score
    """
    if method == "norm":
        I = calculate_mi([d1, d2])
        return I / _entropy(d2)
    elif method == "redundancy":
        return _normalized_redundancy(d1, d2)
    elif method == "total_correlation":
        return _normalized_total_correlation(d1, d2)
    else:
        return calculate_mi([d1, d2])
