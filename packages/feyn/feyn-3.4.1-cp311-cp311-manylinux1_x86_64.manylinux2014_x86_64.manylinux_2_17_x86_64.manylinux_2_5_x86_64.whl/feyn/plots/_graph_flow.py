import numpy as np
from pandas import DataFrame, Series
import feyn

from typing import Union, Optional
from feyn._typings import check_types

from feyn.plots._svg_toolkit import SVGGraphToolkit
from feyn.tools._display import SVG
from feyn._validation import _validate_data_columns_for_model


def _get_min_max(model, data):
    activations = model._get_activations(data)

    minval = min(0, activations.min())
    maxval = max(0, activations.max())

    return minval, maxval


@check_types()
def plot_activation_flow(
    model: feyn.Model,
    data: DataFrame,
    sample: Union[DataFrame, Series],
    filename: Optional[str] = None,
) -> SVG:
    """
    Plot a model of a model displaying the flow of activations.

    Arguments:
        model {feyn.Model}   -- A feyn.Model we want to describe given some data.
        data {DataFrame} -- A Pandas DataFrame to compute on.
        sample {Iterable} - The single sample you want to visualize.
        filename {Optional[str]} - The filename to use for saving the plot as svg.

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: If columns needed for the model are not present in the data or sample.

    Returns:
        SVG -- SVG of the model activation flow.
    """
    _validate_data_columns_for_model(model, data, output=False)
    _validate_data_columns_for_model(model, sample, output=False)

    if isinstance(sample, DataFrame) and len(sample) > 1:
        raise ValueError(
            f"There are {len(sample)} rows in 'sample'. Only the activation flow for a single row can be plotted."
        )

    gtk = SVGGraphToolkit()

    # NOTE: Consider doing range [0,1] for classification
    # and min/max of prediction for regression to keep colors focused on output
    minmax = _get_min_max(model, data)

    activations = model._get_activations(sample)
    activations = np.round(np.squeeze(activations), 2)

    gtk.add_graph(model, label="Displaying activation of individual nodes")
    gtk.label_nodes(activations)
    gtk.color_nodes(by=activations, crange=minmax)
    gtk.add_colorbars(label="Activation strength")

    svg = SVG(gtk._repr_html_())
    if filename:
        return svg.save(filename)

    return svg
