import feyn
import numpy as np
import matplotlib.pyplot as plt
from feyn.plots._model_response import (
    _determine_categories,
    _input_constraints_to_their_value_combinations,
    _initialize_plots,
    _append_xyaxes,
    _initialize_histograms,
    _determine_by_input,
    _determine_legend,
    _compute_model_response_to_data_series,
    _process_data_to_plot,
    _update_plots_with_data,
    _update_histograms_with_data,
    _redrawing_plots,
    _redrawing_histograms,
)
from typing import Iterable, Union, Dict
from contextlib import contextmanager

from pandas import DataFrame


@contextmanager
def _set_backend():
    import matplotlib

    backend = matplotlib.get_backend()
    try:
        yield matplotlib.use("svg")
    finally:
        matplotlib.use(backend)


def interactive_model_response_1d(
    model: feyn.Model,
    data: DataFrame,
    input_constraints: Dict[str, Union[Iterable, float, str]] = None,
):
    """Plot an interactive version of the feyn.plots.plot_model_response_1d (model.plot_response_1d),
        that allows you to change the response variable `by`.

    Arguments:
        model {feyn.Model} -- The model to calculate the response for
        data {DataFrame} -- The data to be analyzed

    Keyword Arguments:
        input_constraints {dict} -- The constraints on the remaining model inputs (default: {None})
    """

    from ipywidgets.widgets import interactive
    from IPython.display import display

    cat_list = _determine_categories(model)
    free_inputs = _get_free_inputs(model.inputs, input_constraints)
    by0 = free_inputs[0]
    fixed_combinations = _input_constraints_to_their_value_combinations(
        data[model.inputs], by0, input_constraints, cat_list
    )

    with _set_backend():
        fig, ax = plt.subplots(figsize=(8, 8))
        actuals_plot, prediction_plots = _initialize_plots(ax, fixed_combinations)

        ax, ax_top, ax_right = _append_xyaxes(ax)
        top_histogram, right_histogram = _initialize_histograms(ax_top, ax_right)

    def _update(**kwargs):
        by = kwargs.pop("by")
        is_categorical = by in cat_list

        by_input = _determine_by_input(data, by, is_categorical)

        fixed_combinations = _input_constraints_to_their_value_combinations(
            data[model.inputs], by, input_constraints, cat_list
        )

        legend_title, fixed_labels = _determine_legend(fixed_combinations)

        pred_axes_list = _compute_model_response_to_data_series(
            model, by, by_input, fixed_combinations
        )
        actual_axes = [data[by], data[model.output].astype("float64")]

        pred_axes_list, actual_axes, ticks_loc, ranges = _process_data_to_plot(
            actual_axes, pred_axes_list, by_input, is_categorical
        )

        _update_plots_with_data(
            actual_axes,
            pred_axes_list,
            fixed_labels,
            is_categorical,
            actuals_plot,
            prediction_plots,
        )
        _update_histograms_with_data(actual_axes, top_histogram, right_histogram)

        axes_labels = [by, f"Predicted {model.output}"]
        _redrawing_plots(ax, axes_labels, ticks_loc, by_input, is_categorical)
        _redrawing_histograms(ax_top, ax_right)

        ax.legend(title=legend_title, loc="center left", bbox_to_anchor=(1.35, 0.5))

        ax.set_xlim(*ranges[0])
        ax.set_ylim(*ranges[1])

        display(fig)

    kwargs = {}
    kwargs["by"] = free_inputs

    return interactive(_update, **kwargs)


def _get_free_inputs(model_inputs, input_constraints):
    if input_constraints is None:
        input_constraints = {}
    free_inputs = list(set(model_inputs) - set(input_constraints.keys()))

    return free_inputs
