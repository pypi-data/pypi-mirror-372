import numpy as np
import matplotlib.pyplot as plt
from ICIW_Plots import cm2inch
from typing import Optional
import warnings

np.random.seed(19680801)
hist_data = np.random.randn(1_500)


def make_square_subplots(
    fig,
    ax_width: float,
    ax_layout: tuple[int, int] = (1, 1),
    v_sep: float = 0.05,
    h_sep: float = 0.05,
    sharex: bool = False,
    sharey: bool = False,
    share_xlabel: bool = False,
    share_ylabel: bool = False,
    xlabel=None,
    ylabel=None,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    **kwargs,
):
    fig_width = float(fig.get_figwidth())
    fig_height = float(fig.get_figheight())

    n_rows, n_cols = ax_layout
    n_row_skips = n_rows - 1
    n_col_skips = n_cols - 1
    subplots_width = (n_cols * ax_width) + (n_col_skips * h_sep)
    subplots_height = (n_rows * ax_width) + (n_row_skips * v_sep)

    x_label_array = ax_array = np.full((n_rows, n_cols), None)
    y_label_array = ax_array = np.full((n_rows, n_cols), None)

    if xlabel is None:
        warnings.warn("Unscientific behavior. No xlabel provided.")
    else:
        given_x_label_array = np.asarray(xlabel)
        match given_x_label_array.shape:
            case ():
                if sharex:
                    x_label_array[-1, :] = given_x_label_array
                else:
                    x_label_array[:, :] = given_x_label_array
            case (n_xlabel_cols,):
                if n_xlabel_cols != n_cols:
                    raise ValueError(
                        f"xlabel must be a single str, 2D array or 1D array of shape (n_cols,).\nYou provided {n_xlabel_cols} labels for the {n_cols} columns."
                    )
                if sharex:
                    x_label_array[-1, :] = given_x_label_array
                else:
                    x_label_array = np.tile(
                        given_x_label_array.reshape(1, -1), (n_rows, 1)
                    )
                print(x_label_array)
            case (n_xlabel_rows, n_xlabel_cols):
                if n_xlabel_rows != n_rows or n_xlabel_cols != n_cols:
                    raise ValueError(
                        f"xlabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\n You provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                x_label_array[:, :] = given_x_label_array

    if ylabel is None:
        warnings.warn("Unscientific behavior. No ylabel provided.")
    else:
        given_y_label_array = np.asarray(ylabel)
        match given_y_label_array.shape:
            case ():
                if sharey:
                    y_label_array[:, 0] = given_y_label_array
                else:
                    y_label_array[:, :] = given_y_label_array
            case (n_ylabel_rows,):
                if n_ylabel_rows != n_rows:
                    raise ValueError(
                        f"ylabel must be a single str, 2D array or 1D array of shape (n_rows,).\nYou provided {n_ylabel_rows} labels for the {n_rows} rows."
                    )
                if sharey:
                    y_label_array[:, 0] = given_y_label_array
                else:
                    y_label_array = np.tile(
                        given_y_label_array.reshape(-1, 1), (1, n_cols)
                    )
            case (n_ylabel_rows, n_ylabel_cols):
                if n_ylabel_rows != n_rows or n_ylabel_cols != n_cols:
                    raise ValueError(
                        f"ylabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\nYou provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                if sharey:
                    raise ValueError("Cannot share y-axis with 2D array of y-labels.")
                y_label_array[:, :] = given_y_label_array

    if left_h is None:
        if subplots_width >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep or fig_height."
            )
        else:
            left_h = (fig_width - subplots_width) / 2
    else:
        if subplots_width + left_h >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep, left_h or fig_height."
            )

    if bottom_v is None:
        if subplots_height >= fig_height:
            raise ValueError(
                "Axes heights exceed figure height. Try adjusting v_sep or fig_width."
            )
        else:
            bottom_v = (fig_height - subplots_height) / 2
    else:
        if subplots_height + bottom_v >= fig_height:
            raise ValueError(
                "Axes heights exceed figure height. Try adjusting v_sep, bottom_v or fig_width."
            )

    # this is the fractional distance subplots and border
    h_frac = left_h / fig_width
    v_frac = bottom_v / fig_height

    # This is the distance between two subplots expressed relative to their average axes width. So
    h_space = v_sep / ax_width
    w_space = h_sep / ax_width

    subplots_width_frac = subplots_width / fig_width
    subplots_height_frac = subplots_height / fig_height

    total_height_frac = subplots_height_frac + v_frac
    total_width_frac = subplots_width_frac + h_frac

    gs = fig.add_gridspec(
        nrows=n_rows,
        ncols=n_cols,
        left=h_frac,
        right=total_width_frac,
        top=total_height_frac,
        bottom=v_frac,
        wspace=w_space,
        hspace=h_space,
    )

    ax_array = np.empty((n_rows, n_cols), dtype=object)
    sharey_ax = None
    sharex_ax = None

    for i in range(n_rows):
        for j in range(n_cols):
            if sharey:
                sharey_ax = ax_array[i, 0]
            if sharex:
                sharex_ax = ax_array[0, j]

            ax_array[i, j] = fig.add_subplot(
                gs[i, j],
                sharey=sharey_ax,
                sharex=sharex_ax,
            )
            ax_array[i, j].set(
                xlabel=x_label_array[i, j],
                ylabel=y_label_array[i, j],
                **kwargs,
            )

    return ax_array


fig = plt.figure(figsize=(19 * cm2inch, 7 * cm2inch))
ax_array = make_square_subplots(
    fig,
    ax_width=5.5 * cm2inch,
    ax_layout=(1, 3),
    h_sep=1 * cm2inch,
    xlabel="a",
    ylabel=[["b", "c", "d"]],
)


ax_array[0, 0].bar(["a", "b", "c"], [5, 7, 9])
ax_array[0, 1].plot([1, 2, 3])
ax_array[0, 0].bar(["a", "b", "c"], [5, 7, 9])

plt.show()
