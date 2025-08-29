from typing import Optional
import logging

from feyn import Model

from ._compatibility import detect_notebook


def show_model(
    model: Model,
    label: Optional[str] = None,
    update_display: bool = False,
    filename: Optional[str] = None,
    show_sources: bool = False
):
    """Updates the display in a python notebook with the graph representation of a model

    Arguments:
        model {Model} -- The model to display.

    Keyword Arguments:
        label {Optional[str]} -- A label to add to the rendering of the model (default is None).
        update_display {bool} -- Clear output and rerender figure (defaults to False).
        filename {Optional[str]} -- The filename to use for saving the plot as html (defaults to None).
        show_sources {bool} -- Whether to show the ordering of the sources in the model - for debug purposes (defaults to False).
    """

    if filename:
        model.savefig(filename)

    if detect_notebook():
        from IPython.display import display, HTML, clear_output

        svg = _render_svg(model, label, show_sources)
        display(HTML(svg))
        if update_display:
            clear_output(wait=True)
    else:
        status = f"{model.loss_value}"
        if label is not None:
            status = label
        logging.getLogger(__name__).info(status)


def _render_svg(model: Model, label: str = None, show_sources: bool = False):
    """Renders the graph representation of feyn models as SVG."""
    from feyn.plots._svg_toolkit import SVGGraphToolkit

    gtk = SVGGraphToolkit()
    gtk.add_graph(model, label=label, show_sources=show_sources)
    return gtk.render()

def layout_2d(m):
    depths = m.depths()
    res = [None] * len(m)

    # The layout puts the root node to the right, so we need to reverse the x locations
    depths = [max(depths)- d for d in depths]

    groupbydepth = {}
    for ix, depth in enumerate(depths):
        groupbydepth.setdefault(depth,[]).append(ix)


    for d, indices_at_d in groupbydepth.items():
        sz = len(indices_at_d)
        y_center = (sz - 1) / 2
        for y, ix in enumerate(indices_at_d):
            res[ix] = (d, y - y_center)

    return res
