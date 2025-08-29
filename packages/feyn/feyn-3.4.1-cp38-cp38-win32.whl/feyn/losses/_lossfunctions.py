from typing import Callable, Optional, Union

import numpy as np


def absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute the absolute error loss.

    Arguments:
        y_true -- Ground truth (correct) values.
        y_pred -- Predicted values.

    Returns:
        nd.array -- The losses as an array of floats.
    """
    return np.abs(y_true - y_pred)


def squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute the squared error loss.

    This is the default loss function used in fitting and sampling models from the QLattice.

    Arguments:
        y_true -- Ground truth (correct) values.
        y_pred -- Predicted values.

    Returns:
        nd.array -- The losses as an array of floats.
    """

    # Some models may prodce very large/small predictions. This can result in an overflow which we ignore.
    # Models that behave like this will perform bad and be discarded by the trainer
    with np.errstate(over="ignore"):
        err = y_pred - y_true
        return (
            err ** 2
        )  # Don't use np.power for squaring. It is very slow for some reason



def binary_cross_entropy(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute the cross entropy loss between the labels and predictions.

    This is a good alternative choice for binary classification problems. If cannot be used for fitting models with output data that is not binary. Doing so will result in a RuntimeError.

    Arguments:
        y_true -- Ground truth (correct) values.
        y_pred -- Predicted values.

    Returns:
        nd.array -- The losses as an array of floats.
    """
    epsilon = 1e-7
    y_pred = np.clip(y_pred, epsilon, 1.0 - epsilon)
    y_true = y_true.astype(int)

    if (y_true > 1).any() or (y_true < 0).any():
        raise RuntimeError(
            "Binary cross entropy loss function requires boolean truth values"
        )

    return -y_true * np.log(y_pred) - (1 - y_true) * np.log(1 - y_pred)



def _get_loss_function(loss_name: str) -> Callable:
    if loss_name == "absolute_error":
        return absolute_error
    if loss_name == "squared_error":
        return squared_error
    if loss_name == "binary_cross_entropy":
        return binary_cross_entropy

    raise ValueError("Unknown loss provided")
