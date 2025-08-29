import numpy as np
from io import BytesIO
from pandas import DataFrame
from typing import Iterable, Optional, Union, List
import matplotlib.pyplot as plt

import feyn
from feyn.plots._svg_toolkit import SVGGraphToolkit
from feyn.tools._display import HTML, SVG

from feyn.metrics import (
    get_pearson_correlations,
    get_mutual_information,
    get_spearmans_correlations,
    get_summary_information,
)

from feyn._typings import check_types


@check_types()
def plot_model_summary(
    model: feyn.Model,
    dataframe: DataFrame,
    compare_data: Optional[Union[DataFrame, List[DataFrame]]] = None,
    labels: Optional[Iterable[str]] = None,
    filename: Optional[str] = None,
) -> HTML:
    """
    Plot a model and summary metrics for the provided feyn.Model and DataFrame with performance plots underneath.

    Arguments:
        model {feyn.Model}   -- A feyn.Model we want to describe given some data.
        dataframe {DataFrame} -- A Pandas DataFrame for showing metrics.

    Keyword Arguments:
        compare_data {Optional[Union[DataFrame, List[DataFrame]]]} -- A Pandas DataFrame or list of DataFrames for showing additional metrics. (default: {None})
        labels {Optional[Iterable[str]]} - A list of labels to use instead of the default labels. Should match length of comparison data + 1.
        filename {Optional[str]} - The filename to use for saving the plot as html.

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if the name of the correlation function is not understood.
        ValueError: if invalid dataframes are passed.
        ValueError: If columns needed for the model are not present in the data.

    Returns:
        HTML -- HTML of the model summary.
    """
    gtk = SVGGraphToolkit()
    gtk.add_graph(model, show_loss=False)

    compare_data = _sanitize_data_inputs(compare_data)
    labels = _create_labels(labels, [dataframe] + compare_data)

    gtk = _calculate_and_add_summary_information(
        gtk, model, dataframe, compare_data, labels
    )
    gtk = gtk.add_input_table(model)

    output_html = gtk._repr_html_()
    for label, data in zip(labels, [dataframe] + compare_data):
        header_html = _html_header(label)
        fig_html = _performance_plots(model, data)
        output_html += header_html + fig_html

    html = HTML(output_html)
    if filename:
        return html.save(filename)

    return html


def _sanitize_data_inputs(compare_data):
    if compare_data is None:
        compare_data = []

    # Wrap in a list to allow multiple comparisons
    if not isinstance(compare_data, list):
        compare_data = [compare_data]

    return compare_data


@check_types()
def plot_model_signal(
    model: feyn.Model,
    dataframe: DataFrame,
    corr_func: Optional[str] = None,
    filename: Optional[str] = None,
) -> SVG:
    """
    Plot a model displaying the signal path for the provided feyn.Model and DataFrame.

    Arguments:
        model {feyn.Model}   -- A feyn.Model we want to describe given some data.
        dataframe {DataFrame} -- A Pandas DataFrame for showing metrics.

    Keyword Arguments:
        corr_func {Optional[str]} -- A name for the correlation function to use as the node signal, either 'mutual_information', 'pearson' or 'spearman' are available. (default: {None} defaults to 'pearson')
        filename {Optional[str]} - The filename to use for saving the plot as svg.

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if the name of the correlation function is not understood.
        ValueError: if invalid dataframe is passed.
        ValueError: If columns needed for the model are not present in the data.

    Returns:
        Union[SVG, str] -- SVG of the model signal or path to where the file is saved when filename is specified.
    """
    if corr_func is None:
        corr_func = "pearson"

    signal_func, legend = _get_corr_func(corr_func)

    node_signal = signal_func(model, dataframe)

    if _is_mutual_information(corr_func):
        node_signal = np.abs(node_signal)
        color_range = node_signal
        cmap = "feyn-highlight"
        colorbar_labels = ["low", "high"]
    elif _is_pearson(corr_func) or _is_spearman(corr_func):
        color_range = [-1, 1]
        cmap = "feyn-signal"
        colorbar_labels = ["-1", "0", "+1"]

    gtk = SVGGraphToolkit()
    gtk.add_graph(model, show_loss=False).color_nodes(
        by=node_signal, crange=color_range, cmap=cmap
    ).label_nodes([np.round(sig, 2) for sig in node_signal]).add_colorbars(
        legend, color_text=colorbar_labels, cmap=cmap
    )

    svg = SVG(gtk.render())
    if filename:
        return svg.save(filename)

    return svg


def _calculate_and_add_summary_information(gtk, model, dataframe, compare_data, labels):
    summary = get_summary_information(model, dataframe)
    gtk.add_summary_information(summary, labels[0])
    if compare_data is not None:
        for l_idx, cdata in enumerate(compare_data):
            compare_summary = get_summary_information(model, cdata)
            gtk.add_summary_information(compare_summary, labels[l_idx + 1], short=True)

    return gtk


def _create_labels(labels, target_list):
    if labels is None:
        labels = ["Training Metrics", "Test"]

    # Magically add labels to match if a sufficient amount is not provided
    if len(labels) != len(target_list):
        # Append labels for differences only
        labels += [f"Comp. {i}" for i in range(len(labels), len(target_list))]

    return labels


def _is_pearson(corr_func):
    return corr_func in ["pearson", "pearsons"]


def _is_mutual_information(corr_func):
    return corr_func in ["mi", "mutual_information", "mutual information"]


def _is_spearman(corr_func):
    return corr_func in ["spearman", "spearmans"]


def _get_corr_func(corr_func):
    if _is_mutual_information(corr_func):
        signal_func = get_mutual_information
        legend = "Mutual Information"
    elif _is_pearson(corr_func):
        signal_func = get_pearson_correlations
        legend = "Pearson correlation"
    elif _is_spearman(corr_func):
        signal_func = get_spearmans_correlations
        legend = "Spearman's correlation"
    else:
        raise ValueError("Correlation function name not understood.")
    return signal_func, legend


def _performance_plots(model: feyn.Model, dataframe: DataFrame):
    class_plots = [
        model.plot_roc_curve,
        model.plot_confusion_matrix,
    ]

    reg_plots = [
        model.plot_regression,
        model.plot_residuals,
    ]

    if model.kind == "classification":
        fig = _create_figure_of_plots(dataframe, class_plots)
    elif model.kind == "regression":
        fig = _create_figure_of_plots(dataframe, reg_plots)
    else:
        raise TypeError("Model kind has to be either classification and regression")

    plt.tight_layout()
    fig_html = _fig_to_html(fig)
    plt.close(fig)

    return fig_html


def _create_figure_of_plots(dataframe, plots):
    rows, columns = _determine_format(len(plots))
    figsize = _determine_figsize(rows, columns)

    fig = plt.figure(figsize=figsize)

    for i, plot in enumerate(plots):
        mpl_index = i + 1
        ax = plt.subplot(rows, columns, mpl_index)
        plot(data=dataframe, ax=ax)

    return fig


def _determine_format(n):
    from math import ceil

    rows = ceil(n / 2)
    columns = 2
    if n < 2:
        columns = 1
    return (rows, columns)


def _determine_figsize(rows, columns):
    height = 3.5 * rows
    width = 8
    if columns < 2:
        width = 4
    return (width, height)


def _fig_to_html(fig):
    import base64

    figfile = BytesIO()
    fig.savefig(figfile, format="png")
    fig_base64 = base64.b64encode(figfile.getvalue()).decode()
    fig_html = f"<img style='width:auto' src='data:image/png;base64,{fig_base64}'/>"
    return fig_html


def _html_header(text):
    return f"<h4 style='font-family:monospace; margin-bottom:5px; font-weight: normal; text-decoration: underline '>{text}</h4>"


def save_model_summaries(models: List[feyn.Model], filename: str, **kwargs):
    html_str_total = ""
    for i, model in enumerate(models):
        html_str_total += f"<h1>Model Summary {i+1}</h1>"
        html_str_total += plot_model_summary(model, **kwargs).data
        html_str_total += "<br />"

    with open(filename, "w") as fd:
        fd.write(html_str_total)

    return "Model summary plots saved successfully"
