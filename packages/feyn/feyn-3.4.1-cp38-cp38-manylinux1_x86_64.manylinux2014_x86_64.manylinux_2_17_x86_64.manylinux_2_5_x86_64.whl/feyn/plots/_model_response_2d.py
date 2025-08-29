"""
Functions for creating a 2D response plot of an Abzu model.
"""

from typing import Dict, Union, Optional, Any
import logging

import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from matplotlib.axes import Axes

import feyn
from feyn._typings import check_types
from feyn.plots._plots import _save_plot
from feyn._validation import _validate_data_columns_for_model
from ._themes import Theme
from feyn.plots._mpl import (
    DualMarker,
    NoMarker,
    custom_marker_handlers,
)


def _has_duplicate_category(model):
    cat_found = {}
    for elem in model:
        if elem.fname == "in-cat:0":
            if cat_found.get(elem.name, False):
                return True

            cat_found[elem.name] = True

    return False


@check_types()
def plot_model_response_2d(
    model: feyn.Model,
    data: DataFrame,
    fixed: Optional[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    resolution: int = 1000,
    cmap: str = "feyn-diverging",
    figsize: Optional[tuple] = None,
    filename: Optional[str] = None,
) -> Union[Axes, str]:
    """
    Visualize the response of a model to numerical inputs. Works for both classification and regression problems. The plot comes in two parts:

    1. A colored background indicating the response of the model in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the model.
    2. Scatter-plotted data on top of the background. In a classification scenario, green corresponds to positive class, and pink corresponds to the negative class.

    For regression, the color gradient shows the true distribution of the output value.
    Two sizes are used in the scatterplot:
    - Larger dots correspond to the data that matches the values in fixed. (inclusive within one half of the standard deviation)
    - Smaller dots have data different from the values in fixed. (outside one half of the standard deviation)

    Arguments:
        model {feyn.Model} -- The feyn Model we want to plot the response.
        data {DataFrame} -- The data that will be scattered in the model.

    Keyword Arguments:
        fixed {Optional[Dict[str, Any]]} -- Dictionary with values we fix in the model. The key is an input name in the model and the value is a number that the input is fixed to. (default: {None})
        ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
        resolution {int} -- The resolution at which we sample the 2D input space for the background. (default: {1000})
        figsize {Optional[tuple]} -- Size of figure when <ax> is None. (default: {None})
        filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if the model input names minus the fixed value names are more than two, meaning that you need to fix more values to reduce the dimensionality and make a 2D plot possible.
        ValueError: if fixed contains a name not in the model inputs.
        ValueError: If columns needed for the model are not present in the data.

    Returns:
        Union[Axes, str]: Axes object or path to where plot is saved when filename is specified
    """
    _validate_data_columns_for_model(model, data)

    if _has_duplicate_category(model):
        logging.getLogger(__name__).warning(
            "The plotted boundary in the case of multiple inputs for the same category is unreliable and should not be used."
        )

    if len(model.inputs) < 2:
        raise ValueError(
            "model needs at least two inputs. Plot_response_1d is better suited for models with a single input"
        )

    fixed = {} if fixed is None else fixed
    _validate_fixed(model, fixed)

    pp2d = PartialPlot2D(model, data, fixed, resolution)

    if ax is None:
        plot_colorbar = True
        fig, ax = plt.subplots(figsize=figsize)
    else:
        plot_colorbar = False
        fig = None

    # Plot background
    vmin, vmax = (None, None)
    if "lr" in model[0].fname:
        vmin, vmax = (0, 1)

    im = ax.imshow(
        pp2d.synth_pred.reshape((resolution, resolution)),
        alpha=0.4,
        origin="lower",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )

    # Set up axes ticks and labels
    check_length = lambda label: len(str(label)) > 4
    ax.set_xticks(pp2d.x_ticks * pp2d.a_x + pp2d.b_x)
    ax.set_xticklabels(
        pp2d.x_labels,
        rotation=(
            "vertical"
            if (any(map(check_length, pp2d.x_labels)) | (len(pp2d.x_labels) > 5))
            else None
        ),
    )

    ax.set_yticks(pp2d.y_ticks * pp2d.a_y + pp2d.b_y)
    ax.set_yticklabels(pp2d.y_labels)

    ax.set_xlabel(pp2d.x_name)
    ax.set_ylabel(pp2d.y_name)

    # Scatter data
    available_data = pp2d.data[pp2d.available_index]
    missing_data = pp2d.data[~pp2d.available_index]

    categorical_names = [n for n, _ in pp2d.categoricals]
    if pp2d.x_name in categorical_names:
        available_x = available_data[pp2d.x_name + "_num"] * pp2d.a_x + pp2d.b_x
        missing_x = missing_data[pp2d.x_name + "_num"] * pp2d.a_x + pp2d.b_x
    else:
        available_x = available_data[pp2d.x_name] * pp2d.a_x + pp2d.b_x
        missing_x = missing_data[pp2d.x_name] * pp2d.a_x + pp2d.b_x

    if pp2d.y_name in categorical_names:
        available_y = available_data[pp2d.y_name + "_num"] * pp2d.a_y + pp2d.b_y
        missing_y = missing_data[pp2d.y_name + "_num"] * pp2d.a_y + pp2d.b_y
    else:
        available_y = available_data[pp2d.y_name] * pp2d.a_y + pp2d.b_y
        missing_y = missing_data[pp2d.y_name] * pp2d.a_y + pp2d.b_y

    # Output within half a standard deviation of data[model.output]
    ax.scatter(
        available_x,
        available_y,
        c=available_data[model.output],
        cmap=cmap,
        s=30,
        alpha=0.9,
        edgecolor=feyn.Theme.color("dark"),
        linewidths=0.25,
        vmin=vmin,
        vmax=vmax
    )

    # Output outside of data[model.output]
    ax.scatter(
        missing_x,
        missing_y,
        c=missing_data[model.output],
        cmap=cmap,
        s=6,
        alpha=0.2,
        edgecolor=feyn.Theme.color("dark"),
        linewidths=0.25,
        vmin=vmin,
        vmax=vmax
    )

    # Add colorbar
    if plot_colorbar:
        fig.colorbar(im, ax=ax, label=f"Predicted {model.output}")

    # Only add fixed legend if there are samples inside/outside the fixed values.
    if len(fixed) > 0:
        # Create custom legend items
        legend_items = [
            NoMarker(),
            DualMarker(".", cmap),
            DualMarker("o", cmap),
            NoMarker(),
        ] + [NoMarker()] * len(fixed.keys())

        fixed_labels = []
        for key, value in fixed.items():
            if isinstance(value, str):
                fixed_labels.append(f"{key}: {value}")
            else:
                fixed_labels.append(f"{key}: {value:.2f} (± {pp2d.fixed_std[key]:.2f})")

        legend_labels = [
            f"Actual {model.output}:",
            "Outside fixed values",
            "Within fixed values (± σ/2)",
            "",
        ] + fixed_labels
    else:
        legend_items = [
            DualMarker("o", cmap),
        ]
        legend_labels = [f"Actual {model.output}"]

    ax.legend(
        handles=legend_items,
        labels=legend_labels,
        loc="center left",
        bbox_to_anchor=(1.35, 0.5),
        handler_map=custom_marker_handlers(),
    )

    if filename:
        return _save_plot(
            plot_model_response_2d,
            filename,
            fig,
            model=model,
            data=data,
            fixed=fixed,
            resolution=resolution,
        )

    return ax


class PartialPlot2D:
    """
    Class to help with organizing a partial 2D plot.
    """

    def __init__(
        self,
        model: feyn.Model,
        data: "DataFrame",
        fixed: Optional[Dict[str, Union[int, float]]] = None,
        resolution: int = 1000,
    ) -> None:
        # Inputs
        self.model = model
        self.data = data.copy()
        self.fixed = {} if fixed is None else fixed
        self.resolution = resolution

        # Other constants
        self.n_labels = 7
        self.categoricals = []

        all_inputs = set(filter(None, model.names[1:]))
        plot = sorted(list(all_inputs.difference(self.fixed.keys())))
        self.x_name, self.y_name = plot
        self.x_idx = model.names.index(self.x_name)
        self.y_idx = model.names.index(self.y_name)

        # set self.{}_ticks and self.{}_labels for x and y
        # And figure out scaling parameters for the data
        self._labels_ticks()

        # Add numerical data for categorical registers
        self._numdat_for_categoricals()

        # Replace categorical x and y with numerical registers in self.model
        self._replace_registers()

        # Generate data for the background
        self.synth_pred = self._synthetic_prediction()

        # TODO: Consider having the std user-specified in the future
        # Calculate standard deviations for later use in _relevant_scatter and legend.
        self.fixed_std = {
            key: self.data[key].std() / 2 if not isinstance(value, str) else value
            for key, value in self.fixed.items()
        }

        # Generate boolean index for which data to include in the scatter
        self.available_index = self._relevant_scatter()

    def _relevant_scatter(self):
        """Select data to use in a scatterplot."""
        available_data = np.ones(len(self.data), dtype=bool)
        for key, value in self.fixed.items():
            if not isinstance(value, str):
                std = self.fixed_std[key]
                lower = value - std
                upper = value + std
                new_constraint = (self.data[key] >= lower) & (self.data[key] < upper)
                available_data &= new_constraint
            else:
                available_data &= self.data[key] == value

        return available_data

    def _synthetic_prediction(self):
        """
        Perform prediction on dense synthetic data in the range of x and y.
        """
        min_x, max_x = self.x_ticks[0], self.x_ticks[-1]
        min_y, max_y = self.y_ticks[0], self.y_ticks[-1]

        # 5% of the range to extend each border of the image.
        adjust_x = (max_x - min_x) * 0.05
        adjust_y = (max_y - min_y) * 0.05

        # Constants for scaling
        self.a_x = self.resolution / (max_x - min_x + 2 * adjust_x)
        self.b_x = -self.a_x * (min_x - adjust_x)
        self.a_y = self.resolution / (max_y - min_y + 2 * adjust_y)
        self.b_y = -self.a_y * (min_y - adjust_y)

        x_coords, y_coords = np.meshgrid(
            np.linspace(min_x - adjust_x, max_x + adjust_x, self.resolution),
            np.linspace(min_y - adjust_y, max_y + adjust_y, self.resolution),
        )
        synth_data = {self.x_name: x_coords.flatten(), self.y_name: y_coords.flatten()}
        ssize = len(synth_data[self.x_name])
        synth_data.update(
            {fname: np.full((ssize,), value) for fname, value in self.fixed.items()}
        )

        return self.model.predict(synth_data)

    def _replace_registers(self):
        """
        Replace categorical registers in the targeted 2D space
        with LR register.
        """

        new_fnames = []
        new_params = []
        for idx, elem in enumerate(self.model):
            param = elem.params
            fname = elem.fname
            xy_input = idx == self.x_idx or idx == self.y_idx
            if "categories" in param and xy_input:
                new_params.append(
                    {"scale": 1, "scale_offset": 0, "w": 1, "bias": param["bias"]}
                )
                new_fnames.append("in-linear:0")
            else:
                new_params.append(param.copy())
                new_fnames.append(fname)

        self.model = feyn.Model(self.model._program.copy(), new_fnames, new_params)

    def _numdat_for_categoricals(self):
        """
        Add numerical data for categorical registers.
        Used in the scatterplot.
        """
        for name, state in self.categoricals:
            weights_dict = dict(state["categories"])
            self.data[name + "_num"] = self.data[name].apply(
                lambda c, w=weights_dict: w[c]
            )

    def _labels_ticks(self):
        """Figure out axes labels and ticks."""

        x_fname, x_state = (
            self.model.fnames[self.x_idx],
            self.model.params[self.x_idx].copy(),
        )
        y_fname, y_state = (
            self.model.fnames[self.y_idx],
            self.model.params[self.y_idx].copy(),
        )

        def _term_to_range(term_fname, term_state, term_name):
            if term_fname == "in-cat:0":
                self.categoricals.append((term_name, term_state))
                cats = sorted(term_state["categories"][:], key=lambda x: x[1])
                labels, ticks = zip(*cats)
                return labels, np.array(ticks)

            min_val, max_val = self.data[term_name].min(), self.data[term_name].max()
            labels = np.linspace(min_val, max_val, self.n_labels)

            return ["{:g}".format(float("{:.2g}".format(i))) for i in labels], labels

        self.y_labels, self.y_ticks = _term_to_range(y_fname, y_state, self.y_name)
        self.x_labels, self.x_ticks = _term_to_range(x_fname, x_state, self.x_name)


def _validate_fixed(model, fixed):
    if fixed:
        if not all(key in model.inputs for key in fixed.keys()):
            raise ValueError("Fixed contains a name that is not an input to the model")

    if not len(model.inputs) - len(fixed) == 2:
        raise ValueError("The amount of non-fixed inputs should be exactly two.")
