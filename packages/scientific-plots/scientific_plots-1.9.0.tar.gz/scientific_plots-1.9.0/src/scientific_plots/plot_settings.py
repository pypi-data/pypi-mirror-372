#!/usr/bin/env python3
"""
This module contains the settings for the various plots.
Plots can be created using the 'figure' deocorator from this module.
Multiple plots for various cases will be created and saved to
the hard drive
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import copy, deepcopy
import csv
from functools import wraps
import locale
from pathlib import Path
import re
import sys
from textwrap import dedent
from typing import Callable, Generator, Optional, Union, overload
from warnings import catch_warnings, simplefilter, warn

import numpy as np

from cycler import cycler
import matplotlib as mpl
from matplotlib import colors
import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes
import mpl_toolkits
import scienceplots  # noqa: F401  # pylint: disable=unused-import

from .types_ import Vector
from .utilities import translate

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

mpl.use("Agg")
plt.rcParams["axes.unicode_minus"] = False

SPINE_COLOR = "black"
FIGSIZE = (3.15, 2.35)
FIGSIZE_SLIM = (3.15, 2.1)
FIGSIZE_SMALL = (2.2, 2.1)

PREVIEW = False  # Generate only one set of plots, don't create the whole set

_savefig = copy(plt.savefig)  # backup the old save-function


def linestyles() -> Generator[str, None, None]:
    """get the line-stiles as an iterator"""
    yield "-"
    yield "dotted"
    yield "--"
    yield "-."


rwth_colorlist: list[tuple[int, int, int]] = [(0, 84, 159), (246, 168, 0),
                                              (161, 16, 53), (0, 97, 101)]
rwth_cmap = colors.ListedColormap(rwth_colorlist, name="rwth_list")
mpl.colormaps.register(rwth_cmap)

rwth_hex_colors = ["#00549F", "#F6A800", "#A11035", "#006165",
                   "#57AB27", "#E30066"]

rwth_cycle = (
    cycler(color=rwth_hex_colors)
    + cycler(linestyle=["-", "--", "-.", "dotted",
                        (0, (3, 1, 1, 1, 1, 1)),
                        (0, (3, 5, 1, 5))]))

rwth_gradient: dict[str, tuple[tuple[float, float, float],
                               tuple[float, float, float]]] = {
    "red": ((0.0, 0.0, 0.0), (1.0, 142 / 255, 142 / 255)),
    "green": ((0.0, 84 / 255.0, 84 / 255), (1.0, 186 / 255, 186 / 255)),
    "blue": ((0.0, 159 / 255, 159 / 255), (1.0, 229 / 255, 229 / 255)),
}


def make_colormap(seq: list[tuple[tuple[Optional[float], ...],
                                  float,
                                  tuple[Optional[float], ...]]],
                  name: str = "rwth_gradient")\
        -> colors.LinearSegmentedColormap:
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    cdict: dict[str, list[tuple[float,
                                Optional[float],
                                Optional[float]
                                ]
                          ]] =\
        {"red": [], "green": [], "blue": []}
    for item in seq:
        red_1, green_1, blue_1 = item[0]
        red_2, green_2, blue_2 = item[2]

        cdict["red"].append((item[1], red_1, red_2))
        cdict["green"].append((item[1], green_1, green_2))
        cdict["blue"].append((item[1], blue_1, blue_2))
    return colors.LinearSegmentedColormap(name, cdict)


def partial_rgb(*x: float) -> tuple[float, ...]:
    """return the rgb value as a fraction of 1"""
    return tuple(v / 255.0 for v in x)


hks_44 = partial_rgb(0.0, 84.0, 159.0)
hks_44_75 = partial_rgb(64.0, 127.0, 183.0)
rwth_orange = partial_rgb(246.0, 168.0, 0.0)
rwth_orange_75 = partial_rgb(250.0, 190.0, 80.0)
rwth_gelb = partial_rgb(255.0, 237.0, 0.0)
rwth_magenta = partial_rgb(227.0, 0.0, 102.0)
rwth_bordeux = partial_rgb(161.0, 16.0, 53.0)


rwth_gradient_map = make_colormap(
    [
        ((None, None, None), 0., hks_44),
        (hks_44_75, 0.33, hks_44_75),
        (rwth_orange, 0.66, rwth_orange),
        (rwth_bordeux, 1., (None, None, None))
    ]
)
rwth_gradient_map_simple = make_colormap(
    [
        ((None, None, None), 0., hks_44),
        (rwth_orange, 1., (None, None, None))
    ],
    name="rwth_gradient_simple")

mpl.colormaps.register(rwth_gradient_map)
mpl.colormaps.register(rwth_gradient_map_simple)


def germanify_between(string: str, reverse: bool = False) -> str:
    """Only apply the German translation to strings
    outside of math areas indicated by dollar sings ($)"""
    match = re.search(r"\$(.*?)\$", string)
    if match:
        before = str(string[:match.start()])
        between = str(match.group(0))
        after = str(string[match.end():])
    else:
        before = ""
        between = ""
        after = string

    match = re.search(r"\[.*?\]$", string)
    if match:
        bracket = match.group(0)
        bracket_start = after.find(bracket)
        before_bracket = after[:bracket_start]
        after_bracket = after[bracket_start + len(bracket):]
    else:
        bracket = ""
        before_bracket = after
        after_bracket = ""

    return translate(before, reverse=reverse)\
        + between + translate(before_bracket, reverse=reverse)\
        + bracket + translate(after_bracket, reverse=reverse)


def _germanify(ax: Axes, reverse: bool = False) -> None:
    """
    translate a figure from english to german.
    The direction can be reversed, if reverse it set to True
    Use the decorator instead
    """

    for axi in ax.figure.axes:
        try:
            axi.ticklabel_format(
                useLocale=True)
        except AttributeError:
            pass
        items = [
            axi.xaxis.label,
            axi.yaxis.label,
            *axi.get_xticklabels(),
            *axi.get_yticklabels(),
        ]
        try:
            if axi.zaxis is not None:
                items.append(axi.zaxis.label)
                items += [*axi.get_zticklabels()]
        except AttributeError:
            pass
        if axi.get_legend():
            items += [*axi.get_legend().texts]
        for item in items:
            if r"$" in item.get_text():
                item.set_text(
                    germanify_between(
                        item.get_text(), reverse=reverse))
            item.set_text(translate(item.get_text(),
                                    reverse=reverse))
    try:
        plt.tight_layout()
    except IndexError:
        pass


@contextmanager
def germanify(ax: Axes,
              reverse: bool = False) -> Generator[None, None, None]:
    """
    Translate the plot to german and reverse
    the translation in the other direction. If reverse is set to false, no
    reversal of the translation will be applied.
    """
    old_locale = locale.getlocale(locale.LC_NUMERIC)
    try:
        try:
            locale.setlocale(locale.LC_ALL, "de_DE")
            locale.setlocale(locale.LC_NUMERIC, "de_DE")
        except locale.Error:
            # locale not available
            pass
        plt.rcParams["axes.formatter.use_locale"] = True
        _germanify(ax)
        yield
    except Exception as e:
        print("Translation of the plot has failed")
        print(e)
        raise
    finally:
        try:
            locale.setlocale(locale.LC_ALL, old_locale)
            locale.setlocale(locale.LC_ALL, old_locale)
        except locale.Error:
            pass
        plt.rcParams["axes.formatter.use_locale"] = False
        if reverse:
            _germanify(ax, reverse=True)


def data_plot(filename: Union[str, Path]) -> None:
    """
    Write the data, which is to be plotted, into a txt-file in csv-format.
    """
    # pylint: disable=W0613
    if isinstance(filename, str):
        file_ = Path(filename)
    else:
        file_ = filename
    file_ = file_.parent / (file_.stem + ".csv")
    ax = plt.gca()
    try:
        with open(file_, "w", encoding="utf-8", newline="") as data_file:
            writer = csv.writer(data_file)
            for line in ax.get_lines():
                writer.writerow(
                    [line.get_label(), ax.get_ylabel(), ax.get_xlabel()])
                writer.writerow(line.get_xdata())
                writer.writerow(line.get_ydata())
    except PermissionError as e:
        print(f"Data-file could not be written for {filename}.")
        print(e)


def read_data_plot(filename: Union[str, Path])\
        -> dict[str, tuple[Vector, Vector]]:
    """Read and parse the csv-data-files, which have been generated by the
    'data_plot'-function."""
    data: dict[str, tuple[Vector, Vector]] = {}
    with open(filename, "r", newline="", encoding="utf-8") as file_:
        reader = csv.reader(file_)
        title: str = ""
        x_data: Optional[Vector] = None
        for i, row in enumerate(reader):
            if i % 3 == 0:
                title = row[0]
            elif i % 3 == 1:
                x_data = np.array(row, dtype=float)
            else:
                y_data: Vector
                y_data = np.array(row, dtype=float)
                assert x_data is not None
                assert title
                data[title] = (x_data, y_data)
    return data


@contextmanager
def presentation_figure(figsize: tuple[float, float] = (4, 3)) ->\
        Generator[Axes, None, None]:
    """context manager to open an close the file.
    default seaborn-like plot"""
    fig, ax = plt.subplots(figsize=figsize)
    mpl.rcParams["text.latex.preamble"] = [
        r"\usepackage{helvet}",  # set the normal font here
        r"\usepackage{sansmath}",  # load up the sansmath so that math
        # -> helvet
        r"\sansmath",  # <- tricky! -- gotta actually tell tex to use!
    ]
    mpl.rc("font", family="sans-serif")
    mpl.rc("text", usetex=False)
    font = {"size": 30}

    mpl.rc("font", **font)
    plt.set_cmap("rwth_list")
    try:
        yield ax
    except Exception as e:
        print("creation of plot failed")
        print(e)
        raise
    finally:
        plt.close(fig)
        plt.close("all")
        mpl.rcParams.update(mpl.rcParamsDefault)
        plt.style.use("default")


old_save = plt.savefig


def try_save(filename: Path,
             dpi: Optional[int] = None,
             bbox_inches: Optional[Union[str, tuple[float, float]]] = None, *,
             small: bool = False,
             slim: bool = False) -> None:
    """Try to save the current figure to the given path, if it is not possible,
    try to save it under a different name.
    If small is set to true, also create
    a smaller version of the given plot.
    If slim is set to true, a slightly slimmer version
    of the plot is created."""

    def alternative_save(
            figsize: tuple[float, float] = FIGSIZE,
            subfolder: str = "small") -> None:
        """
        Create additional saves of the given figsize and save these new figures
        into subfolder of given names. This function can be used to create
        additional plots of different sizes without a large overhead.
        """
        fig = deepcopy(plt.gcf())
        fig.set_size_inches(*figsize)
        with catch_warnings(record=True) as warning:
            simplefilter("always")
            fig.tight_layout()
            if warning:
                if issubclass(warning[-1].category, UserWarning):
                    plt.close(fig)
                    return
        folder = filename.parent / subfolder
        folder.mkdir(exist_ok=True)
        try:
            fig.savefig(
                folder
                / filename.name, dpi=dpi, bbox_inches=bbox_inches)
        except PermissionError:
            fig.savefig(
                folder
                / (filename.stem + "_" + filename.suffix),
                dpi=dpi, bbox_inches=bbox_inches)
        plt.close(fig)

    try:
        old_save(filename, dpi=dpi, bbox_inches=bbox_inches)
    except PermissionError:
        old_save(filename.parent / (filename.stem + "_" + filename.suffix),
                 dpi=dpi, bbox_inches=bbox_inches)

    if small:
        alternative_save(
            figsize=FIGSIZE_SMALL,
            subfolder="small")

    if slim:
        alternative_save(
            figsize=FIGSIZE_SLIM,
            subfolder="slim")


def new_save_simple(subfolder: Union[str, Path] = "", suffix: str = "", *,
                    german: bool = False, png: bool = True,
                    pdf: bool = True, small: bool = False,
                    slim: bool = False)\
        -> Callable[..., None]:
    """
    Return a new save function, which saves the file to a new given name in pdf
    format, and also creates a png version.
    If the argument "german" is set to true, also create German language
    version of the plots.
    """

    @wraps(old_save)
    def savefig_(filename: Union[Path, str],
                 dpi: Optional[int] = None,
                 bbox_inches: Optional[
                     Union[tuple[float, float], str]] = None) -> None:
        """Save the plot to this location as pdf and png."""
        if isinstance(filename, str):
            filename = Path(filename)
        if filename.parent == Path("."):
            warn(
                f"The filename {filename} in 'savefig' does "
                f"not contain a subfolder (i.e. 'subfolder/{filename})! "
                "Many files might be created onto the top level.")

        if subfolder:
            (filename.parent / subfolder).mkdir(exist_ok=True)
            new_path_pdf = filename.parent / subfolder / (
                filename.stem + suffix + ".pdf")
            new_path_png = filename.parent / subfolder / (
                filename.stem + suffix + ".png")
        else:
            new_path_pdf = filename.parent / (
                filename.stem + suffix + ".pdf")
            new_path_png = filename.parent / (
                filename.stem + suffix + ".png")

        # save the data
        data_path = filename.parent / (
            filename.stem + ".dat")

        if not data_path.exists():
            data_plot(data_path)

        try:
            plt.tight_layout()
        except IndexError:
            pass
        # save the figure
        if pdf:
            try_save(new_path_pdf, bbox_inches=bbox_inches,
                     small=small, slim=slim)
        if png:
            try_save(new_path_png, bbox_inches=bbox_inches,
                     dpi=dpi, small=small, slim=slim)

        if german:
            with germanify(plt.gca()):
                if pdf:
                    try_save(
                        new_path_pdf.parent
                        / (new_path_pdf.stem + "_german.pdf"),
                        bbox_inches=bbox_inches, small=small,
                        slim=slim)
                if png:
                    try_save(
                        new_path_png.parent
                        / (new_path_png.stem + "_german.png"),
                        bbox_inches=bbox_inches, dpi=dpi, small=small,
                        slim=slim)

    return savefig_


def presentation_settings() -> None:
    """Change the settings of rcParams for presentations."""
    # increase size
    fig = plt.gcf()
    fig.set_size_inches(8, 6)
    mpl.rcParams["font.size"] = 24
    mpl.rcParams["axes.titlesize"] = 24
    mpl.rcParams["axes.labelsize"] = 24
    # mpl.rcParams["axes.location"] = "left"
    mpl.rcParams["lines.linewidth"] = 3
    mpl.rcParams["lines.markersize"] = 10
    mpl.rcParams["xtick.labelsize"] = 18
    mpl.rcParams["ytick.labelsize"] = 18
    mpl.rcParams["figure.figsize"] = (10, 6)
    mpl.rcParams["figure.titlesize"] = 24

    mpl.rcParams["font.family"] = "sans-serif"


def set_rwth_colors(three_d: bool = False) -> None:
    """Apply the RWTH CD colors to matplotlib."""
    mpl.rcParams["text.usetex"] = False
    mpl.rcParams["axes.prop_cycle"] = rwth_cycle
    if three_d:
        plt.set_cmap("rwth_gradient")
    else:
        plt.set_cmap("rwth_list")


def set_serif() -> None:
    """Set the plot to use a style with serifs."""
    mpl.rcParams["font.family"] = "serif"
    mpl.rcParams["font.serif"] = [
        "stix2", "stix", "cmr10", "Computer Modern Roman", "Times New Roman"]
    mpl.rcParams["mathtext.fontset"] = "stix"
    mpl.rcParams["axes.formatter.use_mathtext"] = True


def set_sans_serif() -> None:
    """Set matplotlib to use a sans-serif font."""
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [
        "Arial", "Helvetica", "DejaVu Sans"]


class ThreeDPlotException(Exception):
    """This exception is called when a 3D plot is drawn. This is used to exit
    the plotting function with the science-style."""


class FallBackException(Exception):
    """This is excaption is thrown when the fallback-style is selected.
    Only for debug purposes."""


def check_3d(three_d: bool) -> None:
    """This function checks if the current plot is a 3d plot. In that case, an
    exception is thrown, which can be used to stop the creation of the default
    plot."""
    if three_d:
        raise ThreeDPlotException
    if isinstance(plt.gca(), mpl_toolkits.mplot3d.axes3d.Axes3D):
        raise ThreeDPlotException


Params = ParamSpec("Params")


def supress_warnings(plot_function: Callable[Params, None])\
        -> Callable[Params, None]:
    """Print only the first appearance of any type of warning shown
    in the function."""

    @wraps(plot_function)
    def wrapped_function(
            *args: Params.args, **kwargs: Params.kwargs) -> None:
        """Wrapped function without all of the warnings."""
        with catch_warnings():
            simplefilter("once")
            plot_function(*args, **kwargs)

    return wrapped_function


def supress_all_warnings(plot_function: Callable[Params, None])\
        -> Callable[Params, None]:
    """Supress all warnings given by the called function."""
    @wraps(plot_function)
    def wrapped_function(
            *args: Params.args, **kwargs: Params.kwargs) -> None:
        """Wrapped function without all of the warnings."""
        with catch_warnings():
            simplefilter("ignore")
            plot_function(*args, **kwargs)

    return wrapped_function


@overload
def apply_styles(plot_function: Callable[Params, None], *,
                 three_d: bool = False,
                 _fallback: bool = False) -> Callable[Params, None]:
    ...


@overload
def apply_styles(plot_function: None, *, three_d: bool = False,
                 _fallback: bool = False)\
        -> Callable[[Callable[Params, None]], Callable[Params, None]]:
    ...


@overload
def apply_styles(*, three_d: bool = False,
                 _fallback: bool = False)\
        -> Callable[[Callable[Params, None]], Callable[Params, None]]:
    ...


def apply_styles(plot_function: Optional[Callable[Params, None]] = None, *,
                 three_d: bool = False, _fallback: bool = False)\
        -> Union[Callable[[Callable[Params, None]],
                          Callable[Params, None]],
                 Callable[Params, None]]:
    """
    Apply the newly defined styles to a function, which creates a plot.
    The new plots are saved into different subdirectories and multiple
    variants of every plot will be created.

    Arguments
    --------
    three_d: Use this option for 3D-plots.
    fallback: Switch directly to the fallback-style (for debug).
    """
    # pylint: disable=too-many-statements

    def _decorator(_plot_function: Callable[Params, None])\
            -> Callable[Params, None]:
        """This is the  actual decorator. Thus, the outer function
        'apply_styles' is actually a decorator-factory."""

        @wraps(_plot_function)
        @supress_warnings
        def new_plot_function(*args: Params.args,
                              **kwargs: Params.kwargs) -> None:
            """
            New plotting function, with applied styles.
            """
            # default plot
            plt.set_cmap("rwth_list")
            plt.savefig = new_save_simple(png=False)
            _plot_function(*args, **kwargs)

            if PREVIEW:
                return

            errors = (OSError, FileNotFoundError, ThreeDPlotException,
                      FallBackException)

            @supress_all_warnings
            def journal() -> None:
                """Create a plot for journals."""
                set_rwth_colors(three_d)
                set_serif()
                plt.savefig = new_save_simple("journal", png=False,
                                              small=not three_d)
                _plot_function(*args, **kwargs)
                plt.close("all")

            @supress_all_warnings
            def sans_serif() -> None:
                """
                Create a plot for journals with sans-serif-fonts.
                """
                set_rwth_colors(three_d)
                set_sans_serif()
                plt.savefig = new_save_simple("sans_serif", german=True,
                                              small=not three_d)
                _plot_function(*args, **kwargs)
                plt.close("all")

            @supress_all_warnings
            def grayscale() -> None:
                """
                Create a plot in grayscales for disserations.
                """
                mpl.rcParams["text.usetex"] = False
                set_serif()
                if three_d:
                    plt.set_cmap("Greys")
                    new_kwargs = copy(kwargs)
                    new_kwargs["colorscheme"] = "Greys"
                    plt.savefig = new_save_simple("grayscale", png=True,
                                                  small=False,
                                                  slim=True)
                else:
                    new_kwargs = kwargs
                    plt.savefig = new_save_simple("grayscale", png=False,
                                                  small=True,
                                                  slim=True)
                _plot_function(*args, **new_kwargs)
                plt.close("all")

            @supress_all_warnings
            def presentation() -> None:
                """
                Create a plot for presentations.
                """
                if three_d:
                    new_kwargs = copy(kwargs)
                    new_kwargs["figsize"] = (9, 7)
                    new_kwargs["labelpad"] = 20
                    new_kwargs["nbins"] = 5
                else:
                    new_kwargs = kwargs
                set_rwth_colors(three_d)
                presentation_settings()
                set_sans_serif()
                plt.savefig = new_save_simple("presentation",
                                              german=True, pdf=False)
                _plot_function(*args, **new_kwargs)
                plt.close("all")

            try:
                plt.close("all")

                check_3d(three_d)
                if _fallback:
                    raise FallBackException

                plt.close("all")

                # journal
                with plt.style.context(["science", "ieee"]):
                    journal()

                # sans-serif
                with plt.style.context(["science", "ieee", "nature"]):
                    sans_serif()

                # grayscale
                with plt.style.context(["science", "ieee", "grayscale"]):
                    grayscale()

                # presentation
                with plt.style.context(["science", "ieee"]):
                    presentation()

            except errors:
                if not three_d:
                    warn(dedent(""""Could not found style 'science'.
                                The package was probably installed incorrectly.
                                Using a fallback-style."""), ImportWarning)

                plt.close("all")
                # journal
                with plt.style.context("fast"):
                    if not three_d:
                        mpl.rcParams["figure.figsize"] = FIGSIZE
                        mpl.rcParams["font.size"] = 8
                    journal()

                # sans-serif
                with plt.style.context("fast"):
                    if not three_d:
                        mpl.rcParams["figure.figsize"] = FIGSIZE
                        mpl.rcParams["font.size"] = 8
                    sans_serif()

                # grayscale
                with plt.style.context("grayscale"):
                    if not three_d:
                        mpl.rcParams["figure.figsize"] = FIGSIZE
                        mpl.rcParams["font.size"] = 8
                    grayscale()

                # presentation
                with plt.style.context("fast"):
                    presentation()

            except (ValueError, RuntimeError):
                warn(dedent(
                    f"""Some plots with alternative styles
                    could not be
                    created for {_plot_function.__name__}."""),
                     ImportWarning)

            plt.savefig = old_save

        return new_plot_function

    if plot_function is not None:
        return _decorator(plot_function)

    assert plot_function is None
    return _decorator
