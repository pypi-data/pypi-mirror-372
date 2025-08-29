import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from .._themes import Theme


class DualMarkerHandler(HandlerBase):
    def create_artists(
        self,
        legend,
        orig_handle,
        xdescent,
        ydescent,
        width,
        height,
        fontsize,
        trans,
    ):
        # Create two separate markers
        m1 = plt.Line2D(
            [xdescent + width / 3],
            [height / 2 - ydescent],
            linestyle=orig_handle.linestyle,
            marker=orig_handle.marker,
            color=orig_handle.color_one,
            markeredgecolor=orig_handle.edge_color,
            markeredgewidth=0.25,
        )
        m2 = plt.Line2D(
            [xdescent + 2 * width / 3],
            [height / 2 - ydescent],
            linestyle=orig_handle.linestyle,
            marker=orig_handle.marker,
            color=orig_handle.color_two,
            markeredgecolor=orig_handle.edge_color,
            markeredgewidth=0.25,
        )
        return [m1, m2]


class NoMarkerHandler(HandlerBase):
    def create_artists(
        self,
        legend,
        orig_handle,
        xdescent,
        ydescent,
        width,
        height,
        fontsize,
        trans,
    ):
        m1 = plt.Line2D(
            [xdescent + width / 3],
            [height / 2 - ydescent],
            linestyle=orig_handle.linestyle,
            marker=orig_handle.marker,
            color=orig_handle.color,
        )
        return [m1]


class NoMarker:
    marker = ""
    color = Theme.color("dark")
    linestyle = "None"


from matplotlib import colormaps


class DualMarker:
    def __init__(self, marker, cmap=None, colors=None):
        """Create a dual marker with two colors.

        Arguments:
            marker {str} -- The marker to use

        Keyword Arguments:
            cmap {str} -- The colormap to pick the two colors from. If None, uses color list instead. (default: {None})
            colors {List[str]} -- The list of colors to pick the two colors from. Only used if cmap is None (default: {None})
        """
        self.marker = marker
        if cmap is not None:
            cm = colormaps.get_cmap(cmap)
            self.color_one = cm(0)
            self.color_two = cm(1.0)
        else:
            self.color_one = colors[0]
            self.color_two = colors[1]
        self.linestyle = "None"
        self.edge_color = Theme.color("dark")


def custom_marker_handlers():
    return {DualMarker: DualMarkerHandler(), NoMarker: NoMarkerHandler()}
