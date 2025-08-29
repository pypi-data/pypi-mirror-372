import matplotlib.pyplot as plt
from typing import Iterable, Optional, Union
import numpy as np

from matplotlib.axes import Axes
from ._themes import Theme
from feyn._validation import (
    _validate_prob_values,
    _validate_bool_values,
)
from feyn.metrics import precision_recall, accuracy_score, f1_score
from feyn._typings import check_types
from feyn.plots._plots import _save_plot


@check_types()
def plot_pr_curve(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[float],
    threshold: Optional[float] = None,
    title: str = "Precision-Recall curve",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
    **kwargs,
) -> Union[Axes, str]:
    """
    Plot a precision-recall curve for a classification model.

    A precision-recall curve, or PR curve, is an illustration of the diagnostic ability of a binary classifier which is commonly used with imbalanced classes.

    Arguments:
        y_true -- Expected values (Truth).
        y_pred -- Predicted values.
        threshold -- Plots a point on the PR curve of the precision and recall at the given threshold. Default is None
        title -- Title of the plot.
        ax -- matplotlib axes object to draw to, default None
        figsize -- size of figure when <ax> is None, default None
        filename -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used, default is None
        **kwargs -- additional keyword arguments to pass to Axes.plot function

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: When y_true is not boolean (or 0/1).
        ValueError: When y_true and y_pred do not have same shape.
        ValueError: When threshold is not between 0 and 1.

    Returns:
        Union[matplotlib.axes.Axes, str] -- Axes or path to where plot is saved when filename is specified
    """

    if not _validate_bool_values(y_true):
        raise ValueError("true values must be an iterable of booleans or 0s and 1s")

    if not _validate_prob_values(y_pred):
        raise ValueError("predictions must be an iterable of floats between 0 and 1")

    if not len(y_pred) == len(y_true):
        raise ValueError("The lengths of predictions and true values do not match")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    import sklearn.metrics

    precision_, recall_, _ = sklearn.metrics.precision_recall_curve(y_true, y_pred)
    average_precision = sklearn.metrics.average_precision_score(y_true, y_pred)
    random_performance = np.sum(
        np.where(y_true, np.ones(len(y_true)), np.zeros(len(y_true)))
    ) / len(y_true)

    ax.set_title(title)

    if threshold is not None:
        if threshold > 1 or 0 > threshold:
            raise ValueError("threshold must be between 0 and 1")

        y_pred_rounded = y_pred >= threshold

        precision, recall = precision_recall(y_true, y_pred_rounded)
        accuracy = accuracy_score(y_true, y_pred_rounded)
        f1 = f1_score(y_true, y_pred_rounded)

        ax.vlines(x=recall, ymin=0, ymax=precision, ls="--", lw=1.5)
        ax.hlines(y=precision, xmin=0, xmax=recall, ls="--", lw=1.5)
        ax.scatter(recall, precision, marker="o", s=50, c="k")
        ax.annotate(
            text=f"({recall:.2f}, {precision:.2f})",
            xy=(recall, precision),
            xytext=(3, -10),
            textcoords="offset points",
        )

        text_str = "\n".join(
            (
                f"Threshold: {threshold: .2f}",
                f"Accuracy: {accuracy: .2f}",
                f"F1 score: {f1: .2f}",
                f"Precision: {precision: .2f}",
                f"Recall: {recall: .2f}",
            )
        )
        props = dict(boxstyle="round", facecolor="white", alpha=0.5)
        ax.text(0.975, 0.05, text_str, bbox=props, ha="right")

    else:
        if "label" in kwargs:
            kwargs["label"] += f" AP = {average_precision:0.2f}"
        else:
            kwargs["label"] = f"AP = {average_precision:0.2f}"

    ax.plot(recall_, precision_, **kwargs)

    if threshold is None:
        ax.legend(loc="lower right")

    ax.plot(
        [0, 1],
        [random_performance, random_performance],
        "--",
        c=Theme.color("dark"),
        lw=1.3,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")

    if filename:
        return _save_plot(
            plot_pr_curve,
            filename,
            fig,
            y_true=y_true,
            y_pred=y_pred,
            threshold=threshold,
            title=title,
            **kwargs,
        )

    return ax
