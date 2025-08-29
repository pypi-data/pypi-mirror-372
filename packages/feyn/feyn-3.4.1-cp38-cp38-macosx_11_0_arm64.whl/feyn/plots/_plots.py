"""Various helper functions to compute and plot metrics."""
import itertools
import os

import matplotlib.pyplot as plt
import numpy as np

from typing import Optional, Iterable, Union, List
import feyn.losses
import feyn.metrics
import feyn
import pandas as pd

from matplotlib.axes import Axes

from ._themes import Theme
from feyn._validation import _validate_bool_values
from feyn._typings import check_types
from feyn.reference import BaseReferenceModel
from feyn.tools._linear_model import LinearRegression

# Sets the default theme and triggers matplotlib stylings
Theme.set_theme()


@check_types()
def plot_confusion_matrix(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[Union[bool, float]],
    labels: Optional[Iterable] = None,
    title: str = "Confusion matrix",
    color_map: str = "feyn-primary",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
) -> Union[Axes, str]:
    """
    Compute and plot a Confusion Matrix.

    Arguments:
        y_true -- Expected values (Truth) as boolean or 0/1 values.
        y_pred -- Predicted values, rounded as boolean or 0/1 values.
        labels -- List of labels to index the matrix
        title -- Title of the plot.
        color_map -- Color map from matplotlib to use for the matrix
        ax -- matplotlib axes object to draw to, default None
        figsize -- Size of figure when <ax> is None, default None
        filename -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used, default None

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_true is not bool-like (bool or 0/1).
        ValueError: if y_pred is not bool-like (bool or 0/1).
        ValueError: if y_true and y_pred are not same size.

    Returns:
        Union[matplotlib.axes.Axes, str] -- matplotlib confusion matrix or path to where plot is saved when filename is specified
    """

    if not _validate_bool_values(y_true):
        raise ValueError("y_true must be an iterable of booleans or 0s and 1s")

    if not _validate_bool_values(y_pred):
        raise ValueError("y_pred must be an iterable of booleans or 0s and 1s")

    if not len(y_true) == len(y_pred):
        raise ValueError(
            f"the lengths of y_true {len(y_true)} and y_pred {len(y_pred)} do not match."
        )

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    if labels is None:
        labels = np.union1d(y_pred, y_true)

    y_true = np.array(list(y_true))
    y_pred = np.array(list(y_pred))

    cm = feyn.metrics.confusion_matrix(y_true, y_pred)

    ax.set_title(title)
    tick_marks = range(len(labels))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=45)

    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)

    thresh = (cm.max() + cm.min()) / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(
            j,
            i,
            format(cm[i, j], "d"),
            horizontalalignment="center",
            color=Theme.color("light") if cm[i, j] > thresh else Theme.color("dark"),
        )

    ax.set_ylabel("Expected")
    ax.set_xlabel("Predicted")

    img = ax.imshow(cm, interpolation="nearest", cmap=color_map)
    plt.colorbar(img, ax=ax)

    if filename:
        return _save_plot(
            plot_confusion_matrix, filename, fig, y_true=y_true, y_pred=y_pred
        )

    return ax


@check_types()
def plot_segmented_loss(
    model: Union[feyn.Model, BaseReferenceModel],
    data: pd.DataFrame,
    by: Optional[str] = None,
    loss_function: str = "squared_error",
    title: str = "Segmented Loss",
    legend: List[str] = ["Samples in bin", "Mean loss for bin"],
    legend_loc: Optional[str] = "lower right",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
) -> Union[List[Axes], str]:
    """
    Plot the loss by segment of a dataset.

    This plot is useful to evaluate how a model performs on different subsets of the data.

    Example:
    > models = qlattice.sample_models(["age","smoker","heartrate"], output="heartrate")
    > models = feyn.fit_models(models, data)
    > best = models[0]
    > feyn.plots.plot_segmented_loss(best, data, by="smoker")

    This will plot a histogram of the model loss for smokers and non-smokers separately, which can help evaluate wheter the model has better performance for euther of the smoker sub-populations.

    You can use any column in the dataset as the `by` parameter. If you use a numerical column, the data will be binned automatically.

    Arguments:
        model -- The model to plot.
        data -- The dataset to measure the loss on.

    Keyword Arguments:
        by -- The column in the dataset to segment by.
        loss_function -- The loss function to compute for each segmnent,
        title -- Title of the plot.
        legend {List[str]} -- legend to use on the plot for bins and loss line (default: ["Samples in bin", "Mean loss for bin"])
        legend_loc {str} -- the location (mpl style) to use for the legend. If None, legend is hidden
        ax -- matplotlib axes object to draw to
        figsize -- Size of figure when <ax> is None, default None
        filename -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used, default None

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if by is not in data.
        ValueError: If columns needed for the model are not present in the data.
        ValueError: If fewer than two labels are supplied for the legend.

    Returns:
        Union[List[matplotlib.axes.Axes], str] -- the axes for plotting or path to where plot is saved when filename is specified
    """
    if by is None:
        by = model.output

    if not len(legend) == 2:
        raise ValueError("The legend must have exactly 2 string labels supplied.")

    bins, cnts, statistic = feyn.metrics.segmented_loss(model, data, by, loss_function)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    ax.set_title(title)

    ax.set_xlabel(f"Segmented by {by}")
    ax.set_ylabel("Number of samples")

    if type(bins[0]) == tuple:
        bins = [(e[0] + e[1]) / 2 for e in bins]
        w = 0.8 * (bins[1] - bins[0])
        ax.bar(bins, height=cnts, width=w, label=legend[0])
    else:
        ax.bar(bins, height=cnts, label=legend[0])

    ax2 = ax.twinx()
    ax2.set_ylabel("Loss")
    ax2.plot(bins, statistic, c=Theme.color("accent"), marker="o", label=legend[1])
    ax2.set_ylim(bottom=0)

    if legend_loc is not None:
        bar, bar_labels = ax.get_legend_handles_labels()
        loss, loss_labels = ax2.get_legend_handles_labels()
        ax2.legend(bar + loss, bar_labels + loss_labels, loc=legend_loc, fontsize=12)

    if filename:
        return _save_plot(
            plot_segmented_loss,
            filename,
            fig,
            model=model,
            data=data,
            by=by,
            loss_function=loss_function,
            title=title,
        )

    return ax, ax2


@check_types()
def plot_regression(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    title: str = "Actuals vs Predictions",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
) -> Union[Axes, str]:
    """This plots this true values on the x-axis and the predicted values on the y-axis.
    On top of the plot is the line of equality y=x.
    The closer the scattered values are to the line the better the predictions.
    The line of best fit between y_true and y_pred is also calculated and plotted. This line should be close to the line y=x

    Arguments:
        y_true {Iterable} -- True values
        y_pred {Iterable} -- Predicted values

    Keyword Arguments:
        title {str} -- (default: {"Actuals vs Predictions"})
        ax {AxesSubplot} -- (default: {None})
        figsize {tuple} -- Size of figure when <ax> is None (default: {None})
        filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_pred and y_true are not same size.

    Returns:
        Union[AxesSubplot, str] -- Scatter plot of y_pred and y_true with line of best fit and line of equality or path to where plot is saved when filename is specified
    """
    if not len(y_true) == len(y_pred):
        raise ValueError("y_pred and y_true must be the same size")

    y_true = np.array(list(y_true))

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    ax.scatter(y_true, y_pred)

    lin_reg = LinearRegression()
    lin_reg.fit(X=y_true.reshape(-1, 1), y=y_pred)
    coef = lin_reg.coef_[0]
    bias = lin_reg.intercept_

    mini = np.min([np.min(y_true), np.min(y_pred)])
    maxi = np.max([np.max(y_true), np.max(y_pred)])

    min_max_pred = lin_reg.predict(X=np.array([mini, maxi]).reshape(-1, 1))

    # Line of equality
    ax.plot([mini, maxi], [mini, maxi], ls="--", lw=1, label="line of equality")

    # Line of best fit of y_pred vs y_true
    ax.plot(
        [mini, maxi],
        min_max_pred,
        ls="--",
        lw=1,
        label=f"least squares: {coef:.2f}X + {bias:.2f}",
    )

    ax.set_title(title)
    ax.set_xlabel("Actuals")
    ax.set_ylabel("Predictions")
    ax.legend()

    if filename:
        return _save_plot(
            plot_regression,
            filename,
            fig,
            y_true=y_true,
            y_pred=y_pred,
            title=title,
        )

    return ax


@check_types()
def plot_residuals(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    title: str = "Residual plot",
    ax: Optional[Axes] = None,
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
) -> Union[Axes, str]:
    """This plots the predicted values against the residuals (y_true - y_pred).

    Arguments:
        y_true {Iterable} -- True values
        y_pred {Iterable} -- Predicted values

    Keyword Arguments:
        title {str} -- (default: {"Residual plot"})
        ax {Axes} -- (default: {None})
        figsize {tuple} -- Size of figure when <ax> is None (default: {None})
        filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_pred and y_true are not same size.

    Returns:
        Union[AxesSubplot, str] -- Scatter plot of residuals against predicted values or path to where plot is saved when filename is specified
    """
    if not len(y_true) == len(y_pred):
        raise ValueError("y_pred and y_true must be the same size")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    y_true = np.array(list(y_true))
    y_pred = np.array(list(y_pred))

    residuals = y_true - y_pred

    ax.scatter(y_pred, residuals)
    ax.axhline(lw=1, ls="--")
    ax.set_title(title)
    ax.set_xlabel("Predictions")
    ax.set_ylabel("Residuals")

    if filename:
        return _save_plot(
            plot_residuals, filename, fig, y_true=y_true, y_pred=y_pred, title=title
        )

    return ax


def _save_plot(plotting_function, filename, figure=None, **kwargs) -> str:
    filename, file_ext = os.path.splitext(filename)
    file_ext = file_ext or ".png"
    filename = filename + file_ext

    if figure:
        figure.savefig(filename, dpi=300, bbox_inches="tight")

    # Axes are coupled with figures so to save only the plot we need to redraw it in a new figure
    else:
        saving_fig, saving_ax = plt.subplots()
        plotting_function(ax=saving_ax, **kwargs)
        saving_fig.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close(saving_fig)

    return os.path.abspath(filename)
