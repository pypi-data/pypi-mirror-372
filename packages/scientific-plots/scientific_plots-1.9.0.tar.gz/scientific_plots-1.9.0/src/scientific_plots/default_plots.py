#!/usr/bin/env python3
# pylint: disable=too-many-locals,too-many-arguments
"""
This module contains a few functions, which can be used to
generate plots quickly and with useful defaults"""
from __future__ import annotations
from pathlib import Path
from functools import wraps
from typing import TypeVar, List, Tuple, Union, Callable, Optional
from warnings import warn, filterwarnings, catch_warnings
from textwrap import dedent

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
import numpy as np
from numpy import amin, amax

from .plot_settings import apply_styles, rwth_cycle
from .types_ import Vector, Matrix

mpl.use("Agg")

In = TypeVar("In", List[float], Tuple[float],
             Vector)

# pylint: disable=invalid-name
In2D = TypeVar("In2D", List[List[float]], List[Vector], Tuple[Vector],
               Matrix)


def fix_inputs(input_1: In, input_2: In)\
        -> tuple[Vector, Vector]:
    """
    Remove nans and infinities from the input vectors.

    Parameters
    ---------
    input_1, input_2:
        X/Y-axis data of plot

    Returns
    ------
    New vectors x and y with nans removed.
    """
    if len(input_1) != len(input_2):
        raise ValueError(
            "The sizes of the input vectors are not the same.")
    nan_count = np.count_nonzero(np.isnan(input_2))
    inf_count = np.count_nonzero(np.isinf(input_2))
    if nan_count != 0 or inf_count != 0:
        new_input_1 = np.empty(len(input_1)-nan_count-inf_count)
        new_input_2 = np.empty(len(new_input_1))
        position = 0
        for x_input, y_input in zip(input_1, input_2):
            if not np.isnan(y_input) or np.isinf(y_input):
                new_input_1[position] = x_input
                new_input_2[position] = y_input
                position += 1
        return new_input_1, new_input_2

    return np.array(input_1), np.array(input_2)


def check_inputs(input_1: In, input_2: In, label_1: str, label_2: str)\
        -> bool:
    """
    Check the input vectors to see, if they are large enough.

    Parameters
    ---------
    input_1, input_2:
        X/Y-axis data of plot

    label_1, label_2:
        Labels of the X/Y axis

    Returns
    ------
    True, if the plot can be created.
    """
    if len(input_1) <= 1 or len(input_2) <= 1:
        warn(
            "There are not enough points in the following plots:"
            f"label1: {label_1} label2: {label_2}. It cannot be drawn.")
        return False

    if min(input_1) == max(input_1):
        warn(
            "The area of the x-axis is not large enough in the following plot:"
            f"label1: {label_1} label2: {label_2}. It cannot be drawn.")
        return False

    if min(input_2) == max(input_2):
        warn(
            "The area of the y-axis is not large enough in the following plot:"
            f"label1: {label_1} label2: {label_2}. It cannot be drawn.")
        return False

    infinity = np.isinf(input_1).any() or np.isinf(input_2).any()
    if infinity:
        warn(dedent(f"""There are infinities in the data of the following plot:
             label1: {label_1}, label2: {label_2}. It cannot be drawn."""),
             RuntimeWarning)
        return False

    nan = np.isnan(input_1).any() or np.isnan(input_2).any()
    if nan:
        warn(dedent(f"""There are nans in the data of the following plot:
             label1: {label_1}, label2: {label_2}. It cannot be drawn."""),
             RuntimeWarning)
        return False

    return True


def get_ylims(
        X: In, Y: In,
        xlim: Optional[tuple[float, float]] = None,
        logscale: bool = False) -> tuple[float, float]:
    """
    Calculate the optimised limits in y-direction.
    """
    if xlim is not None:
        X_plot = np.array(X)
        Y_plot = np.array(Y)[
            np.logical_and(X_plot >= xlim[0], X_plot <= xlim[1])]
    else:
        Y_plot = Y

    if logscale:
        ylim = (
            min(Y_plot) * 0.97, max(Y_plot) * 1.02)
    else:
        ylim = (
            min(Y_plot) - (max(Y_plot) - min(Y_plot)) * 0.02,
            max(Y_plot) + (max(Y_plot) - min(Y_plot)) * 0.02)
    return ylim


# pylint: disable=too-many-positional-arguments
def set_lims(
        X: In, Y: In,
        logscale: bool = False,
        single_log: bool = False,
        single_log_y: bool = False,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None) -> None:
    """
    Set the limits of the current figure to the preferred values, and also
    consider the given manual limits.
    """
    if xlim is None:
        xlim = (min(X), max(X))

    if ylim is None:
        ylim = get_ylims(
            X, Y, xlim=xlim, logscale=(logscale or single_log_y))

    if logscale:
        plt.xscale("log")
        plt.yscale("log")
    elif single_log:
        plt.xscale("log")
    elif single_log_y:
        plt.yscale("log")

    plt.xlim(*xlim)
    plt.ylim(*ylim)


# pylint: disable=too-many-positional-arguments
@apply_styles
def plot_fit(X: In, Y: In,
             fit_function: Callable[..., float],
             xlabel: str, ylabel: str, filename: Union[str, Path], *,
             args: Optional[Tuple[float]] = None,
             logscale: bool = False,
             single_log: bool = False,
             single_log_y: bool = False,
             xlim: Optional[Tuple[float, float]] = None,
             ylim: Optional[Tuple[float, float]] = None) -> None:
    """Creates a plot of data and a fit and saves it to 'filename'."""
    X, Y = fix_inputs(X, Y)  # type: ignore
    if not check_inputs(
            X, Y, xlabel, ylabel):
        return

    n_fit = 1000

    @wraps(fit_function)
    def _fit_function(x: float) -> float:
        """This is the function, which has been fitted"""
        if args is not None:
            return fit_function(x, *args)
        return fit_function(x)

    plt.plot(X, Y, label="data")
    X_fit = [
        min(X) + (max(X) - min(X)) * i / (n_fit - 1) for i in range(n_fit)]

    Y_fit = [_fit_function(x) for x in X_fit]
    plt.plot(X_fit, Y_fit, label="fit")  # type: ignore

    set_lims(
        X, Y, logscale=logscale, single_log=single_log,
        single_log_y=single_log_y,
        xlim=xlim, ylim=ylim)
    if logscale:
        plt.xscale("log")
        plt.yscale("log")
    plt.xlim(min(X), max(X))
    if logscale:
        plt.ylim(min(Y) * 0.97, max(Y) * 1.02)
    else:
        plt.ylim(
            min(Y) - (max(Y) - min(Y)) * 0.02,
            max(Y) + (max(Y) - min(Y)) * 0.02
        )
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# pylint: disable=too-many-positional-arguments
@apply_styles(three_d=False)
def plot_colormap(X: In2D, Y: In2D, Z: In2D,
                  xlabel: str, ylabel: str, zlabel: str,
                  filename: Union[str, Path], *,
                  log_scale: bool = False,
                  colorscheme: str = "rwth_gradient_simple",
                  xlim: Optional[Tuple[float, float]] = None,
                  ylim: Optional[Tuple[float, float]] = None,
                  n_contour: int = 100) -> None:
    """
    Create a 2D color-plot of the given surface. Use the given color-scheme as
    an indicator of the z-level.
    """
    if not check_inputs(
            np.array(X).flatten(),
            np.array(Z).flatten(), xlabel, zlabel):
        return

    _, ax = plt.subplots()
    if log_scale:
        plt.contourf(X, Y, Z, levels=n_contour, cmap=colorscheme,
                     norm=LogNorm())
    else:
        plt.contourf(X, Y, Z, levels=n_contour, cmap=colorscheme)
    chbar = plt.colorbar()

    if xlim is not None:
        plt.xlim(*xlim)
    if ylim is not None:
        plt.xlim(*ylim)

    if log_scale:
        plt.xscale("log")
        plt.yscale("log")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    chbar.set_label(zlabel)

    ax.set_aspect(
        "equal", adjustable="box")

    plt.tight_layout()
    plt.savefig(
        filename)
    plt.close("all")


# pylint: disable=too-many-positional-arguments
@apply_styles(three_d=True)
def plot_surface(X: In2D, Y: In2D, Z: In2D,
                 xlabel: str, ylabel: str, zlabel: str,
                 filename: Union[str, Path], *,
                 log_scale: bool = False,
                 set_z_lim: bool = True,
                 colorscheme: str = "rwth_gradient_simple",
                 figsize: Tuple[float, float] = (4.33, 3.5),
                 labelpad: Optional[float] = None,
                 nbins: Optional[int] = None,
                 xlim: Optional[Tuple[float, float]] = None,
                 ylim: Optional[Tuple[float, float]] = None,
                 zlim: Optional[Tuple[float, float]] = None,
                 linewidth: float = 0,
                 antialiased: bool = True,
                 rcount: int = 200, ccount: int = 200) -> None:
    """create a 2D surface plot of meshgrid-like valued Xs, Ys and Zs"""
    # pylint: disable=too-many-branches
    if not check_inputs(
            np.array(X).flatten(),
            np.array(Z).flatten(), xlabel, zlabel):
        return

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    fig.subplots_adjust(left=-0.02, right=0.75, bottom=0.15, top=0.98)
    ax.plot_surface(X, Y, Z, cmap=colorscheme,
                    rcount=rcount, ccount=ccount,
                    linewidth=linewidth, antialiased=antialiased)
    ax.set_box_aspect(aspect=None, zoom=.8)

    if labelpad is None:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel, rotation=90)
    else:
        ax.set_xlabel(xlabel, labelpad=labelpad)
        ax.set_ylabel(ylabel, labelpad=labelpad)
        ax.set_zlabel(zlabel, rotation=90, labelpad=labelpad)

    assert ax.zaxis is not None

    if xlim is None:
        ax.set_xlim(amin(X), amax(X))  # type: ignore
    else:
        ax.set_xlim(*xlim)
    if ylim is None:
        ax.set_ylim(amin(Y), amax(Y))  # type: ignore
    else:
        ax.set_ylim(*ylim)

    if set_z_lim:
        if not log_scale:
            ax.set_zlim(
                amin(Z) - (amax(Z) - amin(Z)) * 0.02,  # type: ignore
                amax(Z) + (amax(Z) - amin(Z)) * 0.02  # type: ignore
            )
        else:
            ax.set_zlim(
                amin(Z) * 0.97, amax(Z) * 1.02)  # type: ignore
    if zlim is not None:
        ax.set_zlim(*zlim)

    if log_scale:
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_zscale("log")

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.xaxis.pane.set_alpha(0.3)
    ax.yaxis.pane.set_alpha(0.3)
    ax.zaxis.pane.set_alpha(0.3)

    if nbins is not None:
        ax.xaxis.set_major_locator(
            MaxNLocator(nbins)
        )
        ax.yaxis.set_major_locator(
            MaxNLocator(nbins)
        )

    fig.set_size_inches(*figsize)

    with catch_warnings():
        filterwarnings("ignore", message=".*Tight layout")
        plt.tight_layout()
        plt.savefig(filename)

    plt.close()


@apply_styles
def plot(X: In, Y: In, xlabel: str, ylabel: str,
         filename: Union[Path, str], *, logscale: bool = False,
         ylim: Optional[tuple[float, float]] = None,
         yticks: bool = True, cycler: int = 0,
         xlim: Optional[tuple[float, float]] = None,
         single_log: bool = False,
         single_log_y: bool = False) -> None:
    """Create a simple 1D plot"""
    X, Y = fix_inputs(X, Y)  # type: ignore
    if not check_inputs(
            X, Y, xlabel, ylabel):
        return
    if len(X) <= 1 or len(Y) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    if cycler > 0:
        for _ in range(cycler):
            plt.plot([], [])

    set_lims(
        X, Y, logscale=logscale, single_log=single_log,
        single_log_y=single_log_y,
        xlim=xlim, ylim=ylim)

    plt.plot(X, Y, linestyle="-")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if not yticks:
        plt.yticks([])
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


@apply_styles
def two_plots(x1: In, y1: In, label1: str,
              x2: In, y2: In, label2: str,
              xlabel: str, ylabel: str,
              filename: Union[Path, str], *,
              logscale: bool = False, cycle: int = 0,
              color: tuple[int, int] = (0, 1),
              outer: bool = False,
              single_log: bool = False,
              single_log_y: bool = False,
              xlim: Optional[Tuple[float, float]] = None,
              ylim: Optional[Tuple[float, float]] = None,
              inner_y: bool = False,
              half_y: bool = False) -> None:
    """Create a simple 1D plot with two different graphs inside of a single
    plot and a single y-axis.

    Keyword arguments:
    cycle -- skip this many colours in the colour-wheel before plotting
    color -- use these indeces in the colour-wheel when creating a plot
    outer -- use the outer limits on the x-axis rather than the inner limit
    inner_y -- Use the tighter definition for the limits on the y-axis
    half_y -- Use the upper upper limit but the upper lower limit
    """
    x1, y1 = fix_inputs(x1, y1)  # type: ignore
    x2, y2 = fix_inputs(x2, y2)  # type: ignore

    if not (
            check_inputs(x1, y1, xlabel, label1)
            or check_inputs(x2, y2, xlabel, label2)):
        return
    if len(x1) <= 1 or len(y1) <= 1 or len(y2) <= 1 or len(x2) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    if cycle > 0:
        color = (color[0] + cycle, color[1] + cycle)

    # access colour
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    try:
        linestyle = prop_cycle.by_key()["linestyle"]
    except KeyError:
        linestyle = rwth_cycle.by_key()["linestyle"]
    colors = prop_cycle.by_key()["color"]

    if max(color) >= len(colors):
        colors += colors
        linestyle += linestyle

    plt.plot(x1, y1, label=label1,
             color=colors[color[0]],
             linestyle=linestyle[0])

    plt.plot(x2, y2, label=label2,
             color=colors[color[1]],
             linestyle=linestyle[1])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if xlim is not None:
        pass
    elif outer:
        xlim = (min(*x1, *x2),
                max(*x1, *x2))
    else:
        xlim = (max(min(x1), min(x2)),
                min(max(x1), max(x2)))

    plt.xlim(*xlim)

    if ylim is None:
        ylim1 = get_ylims(
            x1, y1, xlim=xlim,
            logscale=(logscale or single_log_y))

        ylim2 = get_ylims(
            x2, y2, xlim=xlim,
            logscale=(logscale or single_log_y))

        if inner_y:
            plt.ylim(
                max(ylim1[0], ylim2[0]),
                min(ylim1[1], ylim2[1]))
        elif half_y:
            plt.ylim(
                max(ylim1[0], ylim2[0]),
                max(ylim1[1], ylim2[1]))
        else:
            plt.ylim(
                min(ylim1[0], ylim2[0]),
                max(ylim1[1], ylim2[1]))
    else:
        plt.ylim(*ylim)

    if logscale or single_log:
        plt.xscale("log")

    if logscale or single_log_y:
        plt.yscale("log")

    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


@apply_styles
def three_plots(x1: In, y1: In, label1: str,
                x2: In, y2: In, label2: str,
                x3: In, y3: In, label3: str,
                xlabel: str, ylabel: str,
                filename: Union[Path, str], *,
                logscale: bool = False,
                xmin: Optional[float] = None,
                xmax: Optional[float] = None) -> None:
    """Create a simple 1D plot with three different graphs inside of a single
    plot and a single y-axis."""
    x1, y1 = fix_inputs(x1, y1)  # type: ignore
    x2, y2 = fix_inputs(x2, y2)  # type: ignore
    x3, y3 = fix_inputs(x3, y3)  # type: ignore
    if not (
            check_inputs(x1, y1, xlabel, label1)
            or check_inputs(x2, y3, xlabel, label1)
            or check_inputs(x3, y3, xlabel, label3)):
        return

    if any(len(x) <= 1 for x in (x1, x2, y1, y2, x3, y3)):
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    plt.plot(x1, y1, label=label1)
    plt.plot(x2, y2, label=label2, linestyle="dashed")
    plt.plot(x3, y3, label=label3, linestyle="dotted")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    min_ = min(*y1, *y2, *y3)
    max_ = max(*y1, *y2, *y3)
    if not logscale:
        plt.ylim(
            min_ - (max_ - min_) * 0.02,
            max_ + (max_ - min_) * 0.02
        )
    else:
        plt.xscale("log")
        plt.yscale("log")
        plt.ylim(
            min_ * 0.97, max_ * 1.02)
    if xmin is not None and xmax is not None:
        plt.xlim(xmin, xmax)
    else:
        plt.xlim(min(x1), max(x1))
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


@apply_styles
def two_axis_plots(x1: In, y1: In, label1: str,
                   x2: In, y2: In, label2: str,
                   xlabel: str, ylabel: str,
                   ylabel2: str,
                   filename: Union[Path, str], *,
                   ticks: Optional[Tuple[List[float], List[str]]] = None,
                   xlim: Optional[Tuple[float, float]] = None,
                   color: Tuple[int, int] = (0, 1))\
        -> None:
    """Create a simple 1D plot with two different graphs inside of a single
    plot with two y-axis.
    The variable "ticks" sets costum y-ticks on the second y-axis. The first
    argument gives the position of the ticks and the second argument gives the
    values to be shown.
    Color selects the indeces of the chosen color-wheel, which should be taken
    for the different plots. The default is (1,2)."""
    x1, y1 = fix_inputs(x1, y1)  # type: ignore
    x2, y2 = fix_inputs(x2, y2)  # type: ignore
    if not check_inputs(
            y1, y2, label1, label2):
        return
    if len(x1) <= 1 or len(y1) <= 1 or len(y2) <= 1 or len(x2) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # access colour
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    try:
        linestyle = prop_cycle.by_key()["linestyle"]
    except KeyError:
        linestyle = rwth_cycle.by_key()["linestyle"]
    colors = prop_cycle.by_key()["color"]

    if max(color) >= len(colors):
        colors += colors
        linestyle += linestyle

    # first plot
    lines = ax1.plot(x1, y1, label=label1,
                     color=colors[color[0]],
                     linestyle=linestyle[0])
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_ylim(
        min(y1) - (max(y1) - min(y1)) * 0.02,
        max(y1) + (max(y1) - min(y1)) * 0.02
    )

    # second plot
    ax2 = ax1.twinx()
    lines += ax2.plot(x2, y2, label=label2,
                      color=colors[color[1]],
                      linestyle=linestyle[1])
    ax2.set_ylabel(ylabel2)
    ax2.set_ylim(
        min(y2) - (max(y2) - min(y2)) * 0.02,
        max(y2) + (max(y2) - min(y2)) * 0.02
    )

    # general settings
    if xlim is None:
        plt.xlim(min(x1), max(x1))
    else:
        plt.xlim(*xlim)
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    # ticks
    if ticks is not None:
        ax2.set_yticks(ticks[0])
        ax2.set_yticklabels(ticks[1])
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def make_invisible(ax: plt.Axes) -> None:
    """Make all patch spines invisible."""
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)


@apply_styles
def three_axis_plots(x1: In, y1: In, label1: str,
                     x2: In, y2: In, label2: str,
                     x3: In, y3: In, label3: str,
                     xlabel: str, ylabel: str,
                     ylabel2: str, ylabel3: str,
                     filename: Union[Path, str], *,
                     ticks: Optional[Tuple[List[float], List[str]]] = None,
                     xlim: Optional[Tuple[float, float]] = None,
                     color: Tuple[int, int, int] = (0, 1, 2),
                     legend: bool = True)\
        -> None:
    """Create a simple 1D plot with two different graphs inside of a single
    plot with two y-axis.
    The variable "ticks" sets costum y-ticks on the second y-axis. The first
    argument gives the position of the ticks and the second argument gives the
    values to be shown.
    Color selects the indeces of the chosen color-wheel, which should be taken
    for the different plots. The default is (1,2)."""
    # pylint: disable=R0915
    x1, y1 = fix_inputs(x1, y1)  # type: ignore
    x2, y2 = fix_inputs(x2, y2)  # type: ignore
    x3, y3 = fix_inputs(x3, y3)  # type: ignore
    if not check_inputs(
            y1, y2, label1, label2):
        return
    if not check_inputs(
            x3, y3, xlabel, label3):
        return

    if len(x1) <= 1 or len(y1) <= 1 or len(y2) <= 1 or len(x2) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")
    assert len(color) == 3

    fig, ax1 = plt.subplots()
    fig.subplots_adjust(right=0.75)
    # access colour
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    try:
        linestyle = prop_cycle.by_key()["linestyle"]
    except KeyError:
        linestyle = rwth_cycle.by_key()["linestyle"]
    colors = prop_cycle.by_key()["color"]

    if max(color) >= len(colors):
        colors += colors
        linestyle += linestyle

    # first plot
    lines = ax1.plot(x1, y1, label=label1,
                     color=colors[color[0]],
                     linestyle=linestyle[0])
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_ylim(
        min(y1) - (max(y1) - min(y1)) * 0.02,
        max(y1) + (max(y1) - min(y1)) * 0.02
    )
    ax1.yaxis.label.set_color(colors[color[0]])
    ax1.tick_params(axis="y", colors=colors[color[0]])

    # second plot
    ax2 = ax1.twinx()
    lines += ax2.plot(x2, y2, label=label2,
                      color=colors[color[1]],
                      linestyle=linestyle[1])
    ax2.set_ylabel(ylabel2)
    ax2.set_ylim(
        min(y2) - (max(y2) - min(y2)) * 0.02,
        max(y2) + (max(y2) - min(y2)) * 0.02
    )
    ax2.yaxis.label.set_color(colors[color[1]])
    ax2.tick_params(axis="y", colors=colors[color[1]])

    # third plot
    ax3 = ax1.twinx()
    make_invisible(ax3)
    ax3.spines["right"].set_position(("axes", 1.25))
    ax3.spines["right"].set_visible(True)
    lines += ax3.plot(x3, y3, label=label3,
                      color=colors[color[2]],
                      linestyle=linestyle[2])
    ax3.set_ylabel(ylabel3)
    ax3.set_ylim(
        min(y3) - (max(y3) - min(y3)) * 0.02,
        max(y3) + (max(y3) - min(y3)) * 0.02
    )
    ax3.yaxis.label.set_color(colors[color[2]])
    ax3.tick_params(axis="y", colors=colors[color[2]])

    # general settings
    if xlim is None:
        plt.xlim(min(x1), max(x1))
    else:
        plt.xlim(*xlim)
    labels = [line.get_label() for line in lines]
    if legend:
        plt.legend(lines, labels)
    # ticks
    if ticks is not None:
        ax2.set_yticks(ticks[0])
        ax2.set_yticklabels(ticks[1])
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
