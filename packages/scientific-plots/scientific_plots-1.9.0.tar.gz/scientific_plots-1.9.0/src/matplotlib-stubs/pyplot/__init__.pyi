#!/usr/bin/env python
"""
This are the typing-stubs for "matplotlib.pyplot".
They are needed for a testing using mypy.
"""
from __future__ import annotations
from typing import (
    Optional, Tuple, Iterable, Union, TypeVar, List, TypedDict, Any,
    overload)
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Generator

from ..ticker import Locator
from ..figure import Figure
from .. import colors, RCParams

from scientific_plots.types_ import Vector, Matrix


In = TypeVar("In", List[float], Tuple[float],
             Vector, List[Any])

In2D = TypeVar("In2D", list[list[float]], list[Vector], tuple[Vector],
               Matrix)


def set_cmap(color: Union[colors.ListedColormap,
                          str,
                          colors.LinearSegmentedColormap]) -> None: ...


def savefig(
    filename: Union[Path, str],
    dpi: Optional[int] = None,
    bbox_inches: Optional[Union[tuple[float, float], str]] = None)\
        -> None: ...


def tight_layout() -> None: ...


class Label:
    def set_fontname(self, fontname: str) -> None: ...

    def set_fontsize(self, fontsize: int) -> None: ...

    def set_text(self, text: str) -> None: ...

    def get_text(self) -> str: ...

    def set_color(self, color: str) -> None: ...


class Line:
    def set_linewidth(self, width: int) -> None: ...

    def set_label(self, label: str) -> None: ...

    def get_label(self) -> Label: ...

    def __add__(self, other: Line) -> list[Line]: ...

    def get_xdata(self) -> Vector: ...

    def get_ydata(self) -> Vector: ...

    def get_color(self) -> str: ...

    def set_data(self, *args: Any) -> None: ...

    def set_drawstyle(self, style: str) -> None: ...

    def get_data(self, orig: bool = True) -> tuple[Vector, Vector]: ...


class Legend:
    texts: Tuple[Label, ...]


class Pane:
    def set_alpha(
        self,
        input_: float) -> None: ...


class Axis:
    label: Label
    labelpad: float
    pane: Pane

    def set_ticks_position(self, position: str) -> None: ...

    def set_tick_params(self, pad: Optional[float] = None,
                        direction: str = "", color: str = "")\
        -> None: ...

    def set_major_formatter(self, format_str: str) -> None: ...

    def set_major_locator(self, locator: Locator) -> None: ...

    def clear(self) -> None: ...

    def set_label_text(self, label: str) -> None: ...

    def get_label(self) -> str: ...


class Spine:
    """Spine-class of axes."""

    def set_color(self, color: str) -> None: ...

    def set_linewidth(self, width: float) -> None: ...

    def set_visible(self, visible: bool) -> None: ...

    def set_position(self, value: tuple[str, float]) -> None: ...


class Patch:
    """Patch class contained in axes."""

    def set_visible(self, value: bool) -> None: ...


class Axes:
    xaxis: Axis
    yaxis: Axis
    zaxis: Optional[Axis]
    axes: Iterable[Axis]
    dist: float = 10

    spines: dict[str, Spine]

    patch: Patch

    figure: Figure

    def set_yticks(self, ticks: list[float]) -> None: ...

    def set_yticklabels(self, labels: list[str]) -> None: ...

    def get_xticklabels(self) -> Iterable[Label]: ...

    def get_yticklabels(self) -> Iterable[Label]: ...

    def get_zticklabels(self) -> Iterable[Label]: ...

    def get_lines(self) -> Iterable[Line]: ...

    def get_legend(self) -> Legend: ...

    def set_xlabel(self, label: str,
                   linespacing: Optional[float] = None,
                   rotation: Optional[float] = None,
                   labelpad: Optional[float] = None,
                   color: Optional[str] = None) -> None: ...

    def set_ylabel(self, label: str,
                   linespacing: Optional[float] = None,
                   rotation: Optional[float] = None,
                   labelpad: Optional[float] = None,
                   color: Optional[str] = None) -> None: ...

    def set_zlabel(self, label: str,
                   linespacing: Optional[float] = None,
                   rotation: Optional[float] = None,
                   labelpad: Optional[float] = None,
                   color: Optional[str] = None) -> None: ...

    def set_xlim(self, min_: float, max_: float) -> None: ...

    def set_ylim(self, min_: float, max_: float) -> None: ...

    def set_zlim(self, min_: float, max_: float) -> None: ...

    def set_xscale(self, scale: str) -> None: ...

    def set_yscale(self, scale: str) -> None: ...

    def set_zscale(self, scale: str) -> None: ...

    def plot_surface(self, X: In2D, Y: In2D, Z: In2D, *,
                     cmap: str = "", alpha: Optional[float] = None,
                     ccount: int = 50, rcount: int = 50,
                     antialiased: bool = False,
                     linewidth: float = 1) -> None: ...

    def scatter(self, X: In, Y: In, Z: In,
                cmap: Union[str, colors.ColorMap] = "jet") -> None: ...

    def plot_trisurf(self, X: In, Y: In, Z: In,
                     cmap: Union[str, colors.ColorMap] = "jet")\
        -> None: ...

    @overload
    def plot(self, X: In2D, Y: In2D, Z: In2D,
             fmt: Optional[str] = None, *,
             label: Optional[str] = None,
             color: Optional[str] = None, linestyle: Optional[str] = None,
             alpha: Optional[float] = None)\
        -> list[Line]: ...

    @overload
    def plot(self, X: In, Y: In, fmt: Optional[str] = None, *,
             label: Optional[str] = None,
             color: Optional[str] = None, linestyle: Optional[str] = None,
             alpha: Optional[float] = None)\
        -> list[Line]: ...

    def twinx(self) -> Axes: ...

    def get_ylabel(self) -> str: ...

    def get_xlabel(self) -> str: ...

    def set_frame_on(self, value: bool) -> str: ...

    def tick_params(self, axis: str = "x",
                    colors: str = "") -> None: ...

    def ticklabel_format(
        self,
        useLocale: bool = False, useMathText: bool = False) -> None: ...

    def set_box_aspect(
        self,
        aspect: Optional[str] = None, zoom: float = 1.)\
        -> None: ...

    def legend(
        self,
        handles: Optional[Union[list[Line], list[str]]] = None,
        labels: Optional[list[str]] = None) -> None: ...

    def set(
        self, **kwargs: Any) -> None: ...

    def set_title(self, label: str, loc: Optional[str] = None) -> None: ...

    def grid(self, visible: Optional[bool] = None, which: str = "major")\
        -> None: ...

    def hist(
        self, x: Union[Vector, Matrix],
        bins: Optional[Union[int, Vector, str]] = None,
        range: Optional[tuple[float, float]] = None,
        density: bool = False, weights: Optional[Vector] = None,
        cumulative: bool = False, bottom: Optional[float] = None,
        histtype: str = "bar", align: str = "mid",
        orientation: str = "vertical", log: bool = False,
        color: Optional[str] = None, label: Optional[str] = None,
        stacked: bool = False) -> None: ...

    def relim(self) -> None: ...

    def autoscale_view(self) -> None: ...

    def draw(self) -> None: ...

    def pause(self, time: float) -> None: ...

    def axvline(
        self, x: float = 0, ymin: float = 0, ymax: float = 1) -> None: ...

    def set_aspect(
        self,
        aspect: str, adjustable: Optional[str] = None) -> None: ...


def figure(figsize: Optional[Tuple[float, float]] = None) -> Figure: ...


def close(fig: Union[Figure, str, None] = None) -> None: ...


def gcf() -> Figure: ...


def gca() -> Axes: ...


def xscale(scale: str) -> None: ...


def yscale(scale: str) -> None: ...


def plot(X: In, Y: In, label: Optional[str] = None,
         linestyle: str = "default",
         color: Optional[str] = None) -> list[Line]: ...


def xlim(min_: float, max_: float) -> None: ...


def ylim(min_: float, max_: float) -> None: ...


def xlabel(label: str) -> None: ...


def ylabel(label: str) -> None: ...


def legend(lines: Optional[list[Line]] = None,
           labels: Optional[list[Label]] = None) -> None: ...


def xticks(ticks: list[float],
           labels: Optional[list[str]] = None) -> None: ...


def yticks(ticks: list[float],
           labels: Optional[list[str]] = None) -> None: ...


class Style:
    """Styling of mpl."""

    def use(self, style: str) -> None: ...

    @contextmanager
    def context(self, style: Union[str, list[str]])\
        -> Generator[None, None, None]: ...


style: Style


def subplots(
    figsize: Tuple[float, float] = (10, 5)) -> Tuple[Figure, Axes]: ...


def show() -> None: ...


def ion() -> None: ...


def pause(t: float) -> None: ...


def clf() -> None: ...


def imshow(frame: int, cmap: Union[colors.ColorMap, str] = "default")\
        -> None: ...


def locator_params(
    *,
    nbins: int = 1,
    axis: str = "x") -> None: ...


rcParams: RCParams


class _ArrowProps(TypedDict):
    """Properties of an arrow."""
    arrowstyle: str
    shrinkA: float
    shrinkB: float


def annotate(
    text: str = "",
    s: str = "",
    xy: Optional[tuple[float, float]] = None,
    xytext: Optional[tuple[float, float]] = None,
    arrowprops: Optional[_ArrowProps] = None) -> None: ...


def text(x: float, y: float, text: str) -> None: ...

def axes(arg: Optional[tuple[str, str, str, str]] = None,
         label: str = "", projection: Optional[str] = None,
         polar: bool = False, sharex: Optional[Axes] = None,
         sharey: Optional[Axes] = None) -> Axes: ...


def subplot(
    *args: Any,
    label: str = "", projection: Optional[str] = None,
    polar: bool = False, sharex: Optional[Axes] = None,
    sharey: Optional[Axes] = None) -> Axes: ...


def grid(visible: Optional[bool] = None, which: str = "major")\
    -> None: ...

def title(text: str) -> None: ...

def axvline(x: float = 0, ymin: float = 0, ymax: float = 1) -> None: ...

def fill_between(
    x: In, y1: In, y2: Union[In, float] = 0,
    where: Union[None, In] = None, alpha: Optional[float] = None,
    color: Union[None, str, Tuple[float, float, float]] = None,
    facecolor: Union[None, str, Tuple[float, float, float]] = None,
    edgecolor: Union[
        None, str, Tuple[float, float, float]] = None) -> None: ...


def contourf(
    x: In2D, y: In2D, z: In2D, levels: int = 10,
    cmap: str = "default",
    norm: Optional[colors.Normalize] = None) -> None: ...


class Colorbar:
    """Colorbar class for use with contour plots."""
    ax: Axes

    def set_label(self, label: str) -> None: ...


def colorbar() -> Colorbar: ...
