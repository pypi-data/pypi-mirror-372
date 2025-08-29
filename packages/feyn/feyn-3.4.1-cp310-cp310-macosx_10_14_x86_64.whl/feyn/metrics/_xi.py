import numpy as np

def _calculate_xi_correlation(x:np.ndarray, y:np.ndarray) -> float:
    """ Calculate the Xi correlation coefficient
    between arrays x and y.

    Arguments:
        x {np.ndarray} -- First 1D data array.
        y {np.ndarray} -- First 1D data array.

    Returns:
        float -- The correlation coefficient.
    """
    size = len(x)
    y_ranks = x[y.argsort()].argsort()
    acc = sum(abs(y_ranks[1:] - y_ranks[:-1]))
    return 1 - (3 * acc) / (size ** 2 - 1)
