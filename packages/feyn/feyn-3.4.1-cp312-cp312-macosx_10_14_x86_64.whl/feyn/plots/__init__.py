"""
This module contains functions to help plotting evaluation metrics for feyn and other models.
"""

from ._plots import (
    plot_confusion_matrix,
    plot_segmented_loss,
    plot_regression,
    plot_residuals,
)
from ._model_response_2d import plot_model_response_2d
from ._model_response import plot_model_response_1d
from ._model_summary import plot_model_summary, plot_model_signal
from ._graph_flow import plot_activation_flow
from ._set_style import abzu_mplstyle
from ._themes import Theme
from ._probability_plot import plot_probability_scores
from ._roc_curve import plot_roc_curve
from ._pr_curve import plot_pr_curve

from ._auto import plot_model_response_auto

from . import interactive


__all__ = [
    "plot_confusion_matrix",
    "plot_segmented_loss",
    "plot_regression",
    "plot_residuals",
    "plot_model_response_auto",
    "plot_model_response_2d",
    "plot_model_response_1d",
    "plot_model_summary",
    "plot_model_signal",
    "plot_activation_flow",
    "Theme",
    "plot_probability_scores",
    "plot_roc_curve",
]
