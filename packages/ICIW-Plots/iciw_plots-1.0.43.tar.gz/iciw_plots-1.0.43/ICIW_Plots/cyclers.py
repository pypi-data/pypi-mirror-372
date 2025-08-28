from cycler import cycler, Cycler
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap
import numpy as np
import warnings
from typing import Union, Literal

symbols = ["o", "d", "^", "x"]
linestyles = ["-", "--", "-.", ":"]

dash_tuple = tuple[int, tuple[int, int, int, int]]
Linestyle = Union[Literal["-", "--", "-.", ":"], dash_tuple]


def ICIW_colormap_cycler(
    colormap: str | Colormap, num_plots: int, start: float = 0.1, stop: float = 0.9
) -> Cycler:
    """Generates a color cycler from an given colormap. For available options see :
     https://matplotlib.org/stable/tutorials/colors/colormaps.html

    Parameters
    ----------
    colormap : str
        see https://matplotlib.org/stable/tutorials/colors/colormaps.html
    num_plots : int
        Number of unique colors to sample
    start : float, optional
        lower bound, by default 0.1
    stop : float, optional
        upper bound, by default 0.9

    Returns
    -------
    cycler
        plt.cycler to use in a context manager
    """
    if isinstance(colormap, str):
        cmap = plt.get_cmap(colormap)
    else:
        cmap = colormap
    _cycler = cycler("color", cmap(np.linspace(start, stop, num_plots)))
    return _cycler


def ICIW_symbol_cycler(num_plots: int, sym_list: list[str] = symbols) -> Cycler:
    """Generates a marker cycler from s given symlist.

    Parameters
    ----------
    num_plots : int
        number of destinct symbol markers to use
    sym_list : list[str], optional
        set of symbol markers to use, by default ["o", "d", "^", "x"] so no more than 4 unique linestyles can be created.

    Returns
    -------
    Cycler
        plt.cycler to use in a context manager
    """

    if num_plots > len(sym_list):
        warnings.warn(
            f"Attempted to use more unique symbols than in sym_list: \n len:{len(sym_list)} | {sym_list} \n Falling back to using all available symbols."
        )
        _cycler = cycler("marker", sym_list)
    else:
        _cycler = cycler("marker", sym_list[:num_plots])
    return _cycler


def ICIW_linestyle_cycler(
    num_plots: int, ls_list: list[Linestyle] = linestyles
) -> Cycler:
    """Generates a linestyle cycler from a given list of linestyles.
        For more information see: https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html.

    Parameters
    ----------
    num_plots : int
        number of destinct linestyles to use.
    sym_list : list[Linestyles], optional
        Set of linestyles to use,
        either a string from ["-", "--", "-.", ":"] or a tuple of the form (dash_length, (dash_gap, space_gap)).
        By default ["-", "--", "-.", ":"] so no more than 4 unique linestyles can be created.

    Returns
    -------
    Cycler
        plt.cycler to use in a context manager
    """

    if num_plots > len(ls_list):
        warnings.warn(
            f"Attempted to use more unique symbols than in sym_list: \n len:{len(ls_list)} | {ls_list} \n Falling back to using all available symbols."
        )
        _cycler = cycler("linestyle", ls_list)
    else:
        _cycler = cycler("linestyle", ls_list[:num_plots])
    return _cycler
