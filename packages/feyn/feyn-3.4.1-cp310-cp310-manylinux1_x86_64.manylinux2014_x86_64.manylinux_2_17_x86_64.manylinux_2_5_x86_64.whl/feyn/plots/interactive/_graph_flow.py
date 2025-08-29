import numpy as np
from pandas import DataFrame, Series
import feyn
import typing

from ._utils import _get_ranges
from feyn.plots._graph_flow import plot_activation_flow


def interactive_activation_flow(model: feyn.Model, data: DataFrame):
    """
    EXPERIMENTAL: For IPython kernels only.
    Interactively plot a model displaying the flow of activations.

    Requires installing ipywidgets, and enabling the extension in jupyter notebook or jupyter lab.
    Jupyter notebook: jupyter nbextension enable --py widgetsnbextension
    Jupyter lab: jupyter labextension install @jupyter-widgets/jupyterlab-manager

    Arguments:
        model {feyn.Model} -- A feyn.Model we want to describe given some data.
        data {DataFrame} -- A Pandas DataFrame to compute on.

    Returns:
        SVG -- SVG of the model summary.
    """
    import ipywidgets as widgets

    ranges = _get_ranges(model, data)

    def flow(**kwargs):
        for key in kwargs:
            kwargs[key] = np.array(kwargs[key])

        sample = Series(kwargs)
        return plot_activation_flow(model, data, sample)

    return widgets.interact(flow, **ranges)
