"""
A collection of loss functions for use with feyn.

The loss funtions can be specified as arguments to the `feyn.fit_models` method. A good choice of loss function can sometimes speed up the training. For most uses the default loss function, `squared_error` is a fine choice.

Note: Data scientist with experience from other frameworks may be used to thinking that the loss function is very significant. In practice it matters less in QLattices, for reasons that have to do with the large range of initial parameters for models.
"""
from ._lossfunctions import (
    binary_cross_entropy,
    absolute_error,
    squared_error,
    _get_loss_function,
)

# Backward compatibility
categorical_cross_entropy = binary_cross_entropy

__all__ = [
    "binary_cross_entropy",
    "absolute_error",
    "squared_error",
    "categorical_cross_entropy",
]
