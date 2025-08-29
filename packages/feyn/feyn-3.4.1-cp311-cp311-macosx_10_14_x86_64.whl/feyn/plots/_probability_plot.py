from typing import Iterable, Optional, Union, List
import numpy as np
import matplotlib.pyplot as plt
from feyn._validation import (
    _validate_bool_values,
    _validate_prob_values,
)

from matplotlib.axes import Axes
from feyn._typings import check_types
from feyn.plots._plots import _save_plot
from feyn.plots import Theme


def _pos_neg_classes(y_true, y_pred):
    """Finds the probability distribution
    of the positive and negative classes.
    Order of truth and prediction matters.

    Arguments:
        y_true {np.array} -- Expected values (Truth)
        y_pred {np.array} -- Predicted values
    """

    # Hits and non-hits
    hits = y_pred[np.round(y_pred) == y_true]  # TP and TN
    non_hits = y_pred[np.round(y_pred) != y_true]  # FP and FN

    # Positive and Negative classes:
    pos_class = np.append(
        hits[np.round(hits) == 1], non_hits[np.round(non_hits) == 0]
    )  # TP and FN
    neg_class = np.append(
        hits[np.round(hits) == 0], non_hits[np.round(non_hits) == 1]
    )  # TN and FP

    return pos_class, neg_class


def _hist_args_styler(data, nbins):
    """Styler for histograms. It gives them
    an edge and transparency.

    Arguments:
        data {array_like} -- data array
        nbins {int} -- number of bins
    """
    range_t = (np.min(data), np.max(data))
    bin_edges = np.histogram_bin_edges(data, bins=nbins, range=range_t)

    h_args = {
        "bins": bin_edges,
        "range": range_t,
        "edgecolor": Theme.color("dark"),
        "lw": 1.5,
        "alpha": 0.7,
    }

    return h_args


@check_types()
def plot_probability_scores(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[float],
    nbins: int = 10,
    title: str = "Predicted Probabilities",
    legend: List[str] = ["Positive Class", "Negative Class"],
    legend_loc: Optional[str] = "upper center",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
    **kwargs,
) -> Union[Axes, str]:
    """Plots the histogram of predicted probability scores in binary
    classification problems, highlighting the negative and
    positive classes. Order of truth and prediction matters.

    Arguments:
        y_true {array_like} -- Expected values (Truth)
        y_pred {array_like} -- Predicted values

    Keyword Arguments:
        nbins {int} -- number of bins (default: {10})
        title {str} -- plot title (default: {''})
        legend {List[str]} -- labels to use in the legend for the positive and negative class (default: ["Positive Class", "Negative Class"])
        legend_loc {str} -- the location (mpl style) to use for the label. If None, legend is hidden
        ax {Axes} -- axes object (default: {None})
        figsize {tuple} -- size of figure when <ax> is None (default: {None})
        filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})
        kwargs -- histogram kwargs (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_true is not bool-like (boolean or 0/1).
        ValueError: if y_pred is not bool-like (boolean or 0/1).
        ValueError: if y_pred and y_true are not same size.
        ValueError: If fewer than two labels are supplied for the legend.

    Returns:
        Union[matplotlib.axes.Axes, str] -- The axes to plot or path to where plot is saved when filename is specified
    """

    if not _validate_bool_values(y_true):
        raise ValueError("y_true must be an iterable of booleans or 0s and 1s")

    if not _validate_prob_values(y_pred):
        raise ValueError("y_true must be an iterable of floats between 0 and 1")

    if not len(y_pred) == len(y_true):
        raise ValueError("The lengths of y_pred and y_true do not match")

    if not len(legend) == 2:
        raise ValueError(
            "The legend must have exactly 2 labels supplied for the negative and positive class."
        )

    y_pred = np.array(list(y_pred))

    pos_class, neg_class = _pos_neg_classes(y_true, y_pred)
    if not kwargs:
        unip_data = np.linspace(0.0, 1.0, 100)
        kwargs = _hist_args_styler(unip_data, nbins)

    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax: Axes = fig.add_subplot()
    else:
        fig = None

    diverging_colors = Theme._get_current().cmaps["feyn-diverging"]
    col_neg, col_pos = diverging_colors[0], diverging_colors[-1]

    ax.hist(neg_class, label=legend[1], color=col_neg, **kwargs)
    ax.hist(pos_class, label=legend[0], color=col_pos, **kwargs)

    if legend_loc is not None:
        ax.legend(loc=legend_loc, fontsize=12)
    ax.set_ylabel("Number of occurrences", fontsize=14)
    ax.set_xlabel("Probability Score", fontsize=14)
    ax.set_title(title, fontsize=14)

    if filename:
        return _save_plot(
            plot_probability_scores,
            filename,
            fig,
            y_true=y_true,
            y_pred=y_pred,
            title=title,
            nbins=nbins,
            **kwargs,
        )

    return ax
