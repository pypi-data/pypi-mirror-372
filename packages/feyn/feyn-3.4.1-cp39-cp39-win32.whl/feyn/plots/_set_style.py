"""
Export plt.style function with relative path knowledge of
an Abzu/Feyn-specific color theme based on our branding.
"""
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from numpy import array, loadtxt
from os.path import dirname, realpath

STYLE_LOC = realpath(dirname(__file__))

def abzu_mplstyle() -> None:
    """
    Set matplotlib to use the Abzu mplstyle.
    In jupyter, use in a separate cell.
    """

    cm.register_cmap(name="abzu", cmap=_get_abzu_full_cmap())
    cm.register_cmap(name="abzu-partial", cmap=_get_abzu_partial_cmap())
    plt.style.use(["default", STYLE_LOC+"/abzu.mplstyle"])

def _get_abzu_full_cmap() -> ListedColormap:
    """
    Internal function to make the full Abzu colormap available
    outside of setting the matplotlib style.
    """

    return ListedColormap(loadtxt(STYLE_LOC+"/abzu_full.txt"))

def _get_abzu_partial_cmap() -> ListedColormap:
    """
    Internal function to make the partial Abzu colormap available
    outside of setting the matplotlib style.
    """

    return ListedColormap(loadtxt(STYLE_LOC+"/abzu_partial.txt"))
