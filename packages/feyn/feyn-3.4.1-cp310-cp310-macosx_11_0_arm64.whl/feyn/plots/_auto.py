from feyn import Model
from feyn.plots import plot_model_response_1d, plot_model_response_2d
from feyn.metrics._contribution import get_ranked_contributors

from pandas import DataFrame
from typing import Tuple, Optional, Union

from matplotlib.axes import Axes


def plot_model_response_auto(
    model: Model,
    data: DataFrame,
    ax: Optional[Axes] = None,
    figsize: Optional[Tuple[int, int]] = None,
    filename: Optional[str] = None,
) -> Union[Axes, Tuple[Axes, Axes, Axes], str]:
    """Plot the response plot by automatically determining the most interesting inputs to display and which to fix.
    Calls the functions plot_model_response_1d or plot_model_response_2d depending on number of inputs in the model.

    Arguments:
        model {feyn.Model} -- The model to plot for
        data {pandas.DataFrame} -- The dataset to plot for

    Keyword Arguments:
        ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the plot. (default: {None})
        figsize {Optional[Tuple[int, int]]} -- A matplotlib compatible figsize tuple (i.e. (8, 8)) (default: {None})
        filename {Optional[str]} -- Path to save plot. If no extension is given then .png is used (default: {None})

    Returns:
        Union[Axes, Tuple[Axes, Axes, Axes], str] -- Singular Axes if the plot returns a 2d response plot, Axes Tuple with 3 elements for the 1d plot or the filepath if filename was given.
    """
    title = "Partial model response"

    if len(model.inputs) == 1:
        if figsize is None:
            figsize = (8, 8)

        if filename is not None:
            return plot_model_response_1d(
                model, data, ax=ax, figsize=figsize, filename=filename
            )

        ax1, ax2, ax3 = plot_model_response_1d(model, data, ax=ax, figsize=figsize)
        ax2.set_title(title)
        return (ax1, ax2, ax3)
    elif len(model.inputs) == 2:
        if filename is not None:
            return plot_model_response_2d(
                model, data, ax=ax, figsize=figsize, filename=filename
            )

        ax = plot_model_response_2d(model, data, ax=ax, figsize=figsize)
        ax.set_title(title)
        return ax
    else:
        rank = get_ranked_contributors(model, data)
        fixed_values = {}
        for key in rank[2:]:
            for el in model:
                if el.name == key:
                    if "cat" in el.fname:
                        fixed_values[key] = data[key].mode()[0]
                    else:
                        fixed_values[key] = data[key].median()
                    break

        if filename is not None:
            return plot_model_response_2d(
                model,
                data,
                ax=ax,
                fixed=fixed_values,
                figsize=figsize,
                filename=filename,
            )

        ax = plot_model_response_2d(
            model, data, ax=ax, fixed=fixed_values, figsize=figsize
        )
        ax.set_title(title)

        return ax
