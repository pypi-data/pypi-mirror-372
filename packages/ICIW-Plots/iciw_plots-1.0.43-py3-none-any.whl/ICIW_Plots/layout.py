from typing import Optional
import numpy as np
import numpy.typing as npt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec, matplotlib.figure
from mpl_toolkits.axes_grid1 import Divider, Size
import warnings


def make_square_ax(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> matplotlib.axes.Axes:
    """Makes a square axes of fixed size in a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in
    ax_width : float
        width of the square axes.
    left_h : Optional[float], optional
        Distance of the left axis to the figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    bottom_v : Optional[float], optional
        Distance of the lower axis to the bottom figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    xlabel : Optional[str], optional
        Label for the x-axis, by default None
    ylabel : Optional[str], optional
        Label for the y-axis, by default None
    **kwargs
        Additional keyword arguments like scales, limits etc. for the axes.

    Returns
    -------
    matplotlib.axes.Axes
        axes plaxed in the figure

    Raises
    ------
    ValueError
        if position is not valid.
    UnscientificWarning
        if no xlabel or ylabel is provided. Thanks Simon.
    """
    fig_width, fig_height = fig.get_size_inches()

    if left_h is None:
        left_h = (fig_width - ax_width) / 2
    if bottom_v is None:
        bottom_v = (fig_height - ax_width) / 2

    if ax_width + left_h >= fig_width:
        raise ValueError("Axes width exceeds figure width")
    if ax_width + bottom_v >= fig_height:
        raise ValueError("Axes height exceeds figure height")

    top_v = fig_height - ax_width - bottom_v
    right_h = fig_width - ax_width - left_h
    h = [Size.Fixed(left_h), Size.Scaled(1), Size.Fixed(right_h)]
    v = [Size.Fixed(bottom_v), Size.Scaled(1), Size.Fixed(top_v)]
    div = Divider(fig, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
    ax = fig.add_axes(div.get_position(), axes_locator=div.new_locator(nx=1, ny=1))

    if xlabel is not None:
        ax.set_xlabel(xlabel)
    else:
        warnings.warn("Unscientific behavior. No xlabel provided.")

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    else:
        warnings.warn("Unscientific behavior. No ylabel provided.")

    ax.set(**kwargs)
    return ax


def make_rect_ax(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    ax_height: float,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> matplotlib.axes.Axes:
    """Makes a rectangular axes of fixed size in a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in.
    ax_width : float
        width of the axes.
    ax_height : float
        height of the axes.
    left_h : Optional[float], optional
        Distance of the left axis to the figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    bottom_v : Optional[float], optional
        Distance of the lower axis to the bottom figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    xlabel : Optional[str], optional
        Label for the x-axis, by default None
    ylabel : Optional[str], optional
        Label for the y-axis, by default None
    **kwargs
        Additional keyword arguments like scales, limits etc. for the axes.

    Returns
    -------
    matplotlib.axes.Axes
        axes plaxed in the figure

    Raises
    ------
    ValueError
        if position is not valid.
    UnscientificWarning
        if no xlabel or ylabel is provided. Thanks Simon.
    """
    fig_width, fig_height = fig.get_size_inches()

    if left_h is None:
        left_h = (fig_width - ax_width) / 2
    if bottom_v is None:
        bottom_v = (fig_height - ax_height) / 2

    if ax_width + left_h >= fig_width:
        raise ValueError("Axes width exceeds figure width")
    if ax_height + bottom_v >= fig_height:
        raise ValueError("Axes height exceeds figure height")

    top_v = fig_height - ax_height - bottom_v
    right_h = fig_width - ax_width - left_h
    h = [Size.Fixed(left_h), Size.Scaled(1), Size.Fixed(right_h)]
    v = [Size.Fixed(bottom_v), Size.Scaled(1), Size.Fixed(top_v)]
    div = Divider(fig, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
    ax = fig.add_axes(div.get_position(), axes_locator=div.new_locator(nx=1, ny=1))

    if xlabel is not None:
        ax.set_xlabel(xlabel)
    else:
        warnings.warn("Unscientific behavior. No xlabel provided.")

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    else:
        warnings.warn("Unscientific behavior. No ylabel provided.")

    ax.set(**kwargs)

    return ax


def make_square_subplots(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    ax_layout: tuple[int, int] = (1, 1),
    v_sep: float = 0.05,
    h_sep: float = 0.05,
    sharex: bool = False,
    sharey: bool = False,
    sharelabel: bool = False,
    xlabel: Optional[str | npt.ArrayLike] = None,
    ylabel: Optional[str | npt.ArrayLike] = None,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    **kwargs,
) -> npt.NDArray[matplotlib.axes.Axes]:
    """Places a grid of square subplots in an existing figure offixed size.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in.
    ax_width : float
        width and height of the square axes.
    ax_layout : tuple[int, int], optional
        size of the axes grid in (rows, columns), by default (1, 1)
    v_sep : float, optional
        vertical separator between axes atop one another, by default 0.05
    h_sep : float, optional
        horizonta separator between axes next to one another, by default 0.05
    sharex : bool, optional
        whether axes on top of eachother share one x axes, by default False
    sharey : bool, optional
        whether axes next to eachother share one y axes, by default False
    sharelabel : bool, optional
        whether to share the labels of the shared axes, by default False
    xlabel, ylabel : Optional[str | npt.ArrayLike], optional
        label or labels for the axes. Can be one of the following:
        * `None` - no label
        * a single `str` - every subplot will get the same x/y label
        * a 1D `npt.ArrayLike` - every column/row will get the same x/y label
        * a 2D `npt.ArrayLike` - every subplot will get its own x/y label
        If `sharex` or `sharey` is `True`, only the last row/column (the shared axis) will get the label.
        By default None
    left_h : Optional[float], optional
        _description_, by default None
    bottom_v : Optional[float], optional
        _description_, by default None

    Returns
    -------
    npt.NDArray[matplotlib.axes.Axes]
        The axes grid in the figure.

    Raises
    ------
    ValueError
    """
    fig_width = float(fig.get_figwidth())
    fig_height = float(fig.get_figheight())

    n_rows, n_cols = ax_layout
    n_row_skips = n_rows - 1
    n_col_skips = n_cols - 1
    subplots_width = (n_cols * ax_width) + (n_col_skips * h_sep)
    subplots_height = (n_rows * ax_width) + (n_row_skips * v_sep)

    # every subplot can possibly have a different label
    x_label_array = ax_array = np.full((n_rows, n_cols), None)
    y_label_array = ax_array = np.full((n_rows, n_cols), None)

    # set all xlabels
    if xlabel is None:
        warnings.warn("Unscientific behavior. No xlabel provided.")
    else:
        # convert to numpy array
        given_x_label_array = np.asarray(xlabel)
        match given_x_label_array.shape:
            case ():  # single str - every subplot same xlabel
                if sharex:
                    x_label_array[-1, :] = given_x_label_array
                else:
                    x_label_array[:, :] = given_x_label_array
            case (n_xlabel_cols,):  # 1D array - every column same xlabel
                # check if number of labels matches number of columns
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
            case (n_xlabel_rows, n_xlabel_cols):  # 2D array - every subplot own xlabel
                # check if label layout matches axes layout
                if n_xlabel_rows != n_rows or n_xlabel_cols != n_cols:
                    raise ValueError(
                        f"xlabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\n You provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                if sharex:
                    raise ValueError("Cannot share x-axis with 2D array of x-labels.")
                # set every subplot xlabel explicitly
                x_label_array[:, :] = given_x_label_array

    # set all ylabels
    if ylabel is None:
        warnings.warn("Unscientific behavior. No ylabel provided.")
    else:
        given_y_label_array = np.asarray(ylabel)
        match given_y_label_array.shape:
            case ():  # single str - every subplot same ylabel
                if sharey:
                    y_label_array[:, 0] = given_y_label_array
                else:
                    y_label_array[:, :] = given_y_label_array
            case (n_ylabel_rows,):  # 1D array - every row same ylabel
                # check if number of labels matches number of rows
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
            case (n_ylabel_rows, n_ylabel_cols):  # 2D array - every subplot own ylabel
                # check if label layout matches axes layout
                if n_ylabel_rows != n_rows or n_ylabel_cols != n_cols:
                    raise ValueError(
                        f"ylabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\nYou provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                if sharey:
                    raise ValueError("Cannot share y-axis with 2D array of y-labels.")
                y_label_array[:, :] = given_y_label_array

    if left_h is None:
        # center the subplots
        if subplots_width >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep or fig_height."
            )
        else:
            left_h = (fig_width - subplots_width) / 2
    else:
        # use the given left_h
        if subplots_width + left_h >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep, left_h or fig_height."
            )

    if bottom_v is None:
        # center the subplots
        if subplots_height >= fig_height:
            raise ValueError(
                "Axes heights exceed figure height. Try adjusting v_sep or fig_width."
            )
        else:
            bottom_v = (fig_height - subplots_height) / 2
    else:
        # use the given bottom_v
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

    for row in range(n_rows):
        for col in range(n_cols):
            if sharey:
                sharey_ax = ax_array[row, 0]
            if sharex:
                sharex_ax = ax_array[0, col]

            ax_array[row, col] = fig.add_subplot(
                gs[row, col],
                sharey=sharey_ax,
                sharex=sharex_ax,
            )
            ax_array[row, col].set(
                xlabel=x_label_array[row, col],
                ylabel=y_label_array[row, col],
                **kwargs,
            )

            if sharey and sharelabel:
                if col != 0:
                    plt.setp(ax_array[row, col].get_yticklabels(), visible=False)
            if sharex and sharelabel:
                if row != n_rows - 1:
                    plt.setp(ax_array[row, col].get_xticklabels(), visible=False)

    return ax_array


def make_rect_subplots(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    ax_height: float,
    ax_layout: tuple[int, int] = (1, 1),
    v_sep: float = 0.05,
    h_sep: float = 0.05,
    sharex: bool = False,
    sharey: bool = False,
    sharelabel: bool = False,
    xlabel: Optional[str | npt.ArrayLike] = None,
    ylabel: Optional[str | npt.ArrayLike] = None,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    **kwargs,
) -> npt.NDArray[matplotlib.axes.Axes]:
    """Places a grid of square subplots in an existing figure offixed size.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in.
    ax_width : float
        width and height of the square axes.
    ax_layout : tuple[int, int], optional
        size of the axes grid in (rows, columns), by default (1, 1)
    v_sep : float, optional
        vertical separator between axes atop one another, by default 0.05
    h_sep : float, optional
        horizonta separator between axes next to one another, by default 0.05
    sharex : bool, optional
        whether axes on top of eachother share one x axes, by default False
    sharey : bool, optional
        whether axes next to eachother share one y axes, by default False
    sharelabel : bool, optional
        whether to share the labels of the shared axes, by default False
    xlabel, ylabel : Optional[str | npt.ArrayLike], optional
        label or labels for the axes. Can be one of the following:
        * `None` - no label
        * a single `str` - every subplot will get the same x/y label
        * a 1D `npt.ArrayLike` - every column/row will get the same x/y label
        * a 2D `npt.ArrayLike` - every subplot will get its own x/y label
        If `sharex` or `sharey` is `True`, only the last row/column (the shared axis) will get the label.
        By default None
    left_h : Optional[float], optional
        _description_, by default None
    bottom_v : Optional[float], optional
        _description_, by default None

    Returns
    -------
    npt.NDArray[matplotlib.axes.Axes]
        The axes grid in the figure.

    Raises
    ------
    ValueError
    """
    fig_width = float(fig.get_figwidth())
    fig_height = float(fig.get_figheight())

    n_rows, n_cols = ax_layout
    n_row_skips = n_rows - 1
    n_col_skips = n_cols - 1
    subplots_width = (n_cols * ax_width) + (n_col_skips * h_sep)
    subplots_height = (n_rows * ax_height) + (n_row_skips * v_sep)

    # every subplot can possibly have a different label
    x_label_array = np.full((n_rows, n_cols), None)
    y_label_array = np.full((n_rows, n_cols), None)
    ax_array = np.full((n_rows, n_cols), None)

    # set all xlabels
    if xlabel is None:
        warnings.warn("Unscientific behavior. No xlabel provided.")
    else:
        # convert to numpy array
        given_x_label_array = np.asarray(xlabel)
        match given_x_label_array.shape:
            case ():  # single str - every subplot same xlabel
                if sharex:
                    x_label_array[-1, :] = given_x_label_array
                else:
                    x_label_array[:, :] = given_x_label_array
            case (n_xlabel_cols,):  # 1D array - every column same xlabel
                # check if number of labels matches number of columns
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
            case (n_xlabel_rows, n_xlabel_cols):  # 2D array - every subplot own xlabel
                # check if label layout matches axes layout
                if n_xlabel_rows != n_rows or n_xlabel_cols != n_cols:
                    raise ValueError(
                        f"xlabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\n You provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                if sharex:
                    raise ValueError("Cannot share x-axis with 2D array of x-labels.")
                # set every subplot xlabel explicitly
                x_label_array[:, :] = given_x_label_array

    # set all ylabels
    if ylabel is None:
        warnings.warn("Unscientific behavior. No ylabel provided.")
    else:
        given_y_label_array = np.asarray(ylabel)
        match given_y_label_array.shape:
            case ():  # single str - every subplot same ylabel
                if sharey:
                    y_label_array[:, 0] = given_y_label_array
                else:
                    y_label_array[:, :] = given_y_label_array
            case (n_ylabel_rows,):  # 1D array - every row same ylabel
                # check if number of labels matches number of rows
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
            case (n_ylabel_rows, n_ylabel_cols):  # 2D array - every subplot own ylabel
                # check if label layout matches axes layout
                if n_ylabel_rows != n_rows or n_ylabel_cols != n_cols:
                    raise ValueError(
                        f"ylabel must be a single str, 1D array or 2D array of shape (n_rows, n_cols).\nYou provided a {given_x_label_array.shape} label array for the {ax_layout} axes layout."
                    )
                if sharey:
                    raise ValueError("Cannot share y-axis with 2D array of y-labels.")
                y_label_array[:, :] = given_y_label_array

    if left_h is None:
        # center the subplots
        if subplots_width >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep or fig_height."
            )
        else:
            left_h = (fig_width - subplots_width) / 2
    else:
        # use the given left_h
        if subplots_width + left_h >= fig_width:
            raise ValueError(
                "Axes widths exceed figure width. Try adjusting h_sep, left_h or fig_height."
            )

    if bottom_v is None:
        # center the subplots
        if subplots_height >= fig_height:
            raise ValueError(
                "Axes heights exceed figure height. Try adjusting v_sep or fig_width."
            )
        else:
            bottom_v = (fig_height - subplots_height) / 2
    else:
        # use the given bottom_v
        if subplots_height + bottom_v >= fig_height:
            raise ValueError(
                "Axes heights exceed figure height. Try adjusting v_sep, bottom_v or fig_width."
            )

    # this is the fractional distance subplots and border
    h_frac = left_h / fig_width
    v_frac = bottom_v / fig_height

    # This is the distance between two subplots expressed relative to their average axes width. So
    h_space = v_sep / ax_height
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

    for row in range(n_rows):
        for col in range(n_cols):
            if sharey:
                sharey_ax = ax_array[row, 0]
            if sharex:
                sharex_ax = ax_array[0, col]

            ax_array[row, col] = fig.add_subplot(
                gs[row, col],
                sharey=sharey_ax,
                sharex=sharex_ax,
            )
            ax_array[row, col].set(
                xlabel=x_label_array[row, col],
                ylabel=y_label_array[row, col],
                **kwargs,
            )

            if sharey and sharelabel:
                if col != 0:
                    plt.setp(ax_array[row, col].get_yticklabels(), visible=False)
            if sharex and sharelabel:
                if row != n_rows - 1:
                    plt.setp(ax_array[row, col].get_xticklabels(), visible=False)

    return ax_array
