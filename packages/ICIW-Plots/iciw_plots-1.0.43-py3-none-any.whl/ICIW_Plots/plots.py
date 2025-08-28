import matplotlib.pyplot as plt
from typing import Optional


def rangeframe(x, y, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_bounds(min(y), max(y))
    ax.spines["bottom"].set_bounds(min(x), max(x))
    ax.scatter(x, y, **kwargs)
    return ax
