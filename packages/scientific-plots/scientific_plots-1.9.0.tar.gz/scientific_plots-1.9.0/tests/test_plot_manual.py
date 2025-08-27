#!/usr/bin/env python3
"""
Test the design of the created plots by eye and by hand. For this, the plots
are placed in a persistent directory.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from pytest import mark
from numpy import linspace, meshgrid
from scientific_plots.default_plots import (
    two_plots, three_axis_plots, plot, plot_surface,
    plot_colormap)
from scientific_plots.plot_settings import apply_styles
from scientific_plots.types_ import Vector


LOCATION = Path("tests/plots/test_plot.pdf")
LOCATION2 = Path("tests/plots/test_plot2.pdf")
LOCATION3 = Path("tests/plots/test_plot3.pdf")
LOCATION4 = Path("tests/plots/test_plot_surface.pdf")
LOCATION5 = Path("tests/plots/test_plot_fallback.pdf")
LOCATION6 = Path("tests/plots/test_plot_colormap.pdf")


@mark.use_style
def test_two_plots() -> None:
    """Test the creation of a twin-plot."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    filename = LOCATION
    filename.parent.mkdir(exist_ok=True)
    two_plots(x_test, y_test1, "plot1",
              x_test, y_test2, "plot2",
              "$p$ distance [m]",
              r"$\dot{m} = \frac{a}{b}$ leakage [$\mu$g/s]",
              filename)
    assert filename.exists()


@mark.use_style
def test_three_plots() -> None:
    """Test the creation of a plot with three y axis."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    y_test3: Vector = x_test**3 + 1
    filename = LOCATION2
    filename.parent.mkdir(exist_ok=True)
    three_axis_plots(
        x_test, y_test1, "1.",
        x_test, y_test2, "2.",
        x_test, y_test3, "3.",
        "x", "y1", "y2", "y3",
        filename, color=(3, 4, 5))
    assert filename.exists()


@mark.use_style
def test_skip_color() -> None:
    """Test the skipping of a color in the cycle."""
    x_test: Vector = linspace(1., 2., 100)
    y_test1: Vector = x_test**2
    filename = LOCATION3
    filename.parent.mkdir(exist_ok=True)
    plot(x_test, y_test1, "$x_2$", r"$\sqrt{y_c}$", filename, cycler=1)
    assert filename.exists()


@mark.use_style
def test_two_d_plot() -> None:
    """Test the creation of a two dimensional surface plot."""
    x_test: Vector = linspace(-10, 10, 300)
    y_test: Vector = linspace(-10, 10, 300)
    x_test_grid, y_test_grid = meshgrid(
        x_test, y_test)
    z_grid = x_test_grid**2 - y_test_grid
    filename = LOCATION4
    filename.parent.mkdir(exist_ok=True)
    plot_surface(
        x_test_grid, y_test_grid, z_grid,
        "x-label", "y-label", "z-label",
        LOCATION4)
    assert filename.exists()


@mark.use_style
def test_contour_plot() -> None:
    """Test the creation of a two dimensional surface plot."""
    x_test: Vector = linspace(-10, 10, 300)
    y_test: Vector = linspace(-10, 10, 300)
    x_test_grid, y_test_grid = meshgrid(
        x_test, y_test)
    z_grid = x_test_grid**2 - y_test_grid
    filename = LOCATION6
    filename.parent.mkdir(exist_ok=True)
    plot_colormap(
        x_test_grid, y_test_grid, z_grid,
        "x-label", "y-label", "z-label",
        filename)
    assert filename.exists()


@mark.use_style
def test_fallback() -> None:
    """Test plot creation using the fallback-style."""
    filename = LOCATION4
    filename.parent.mkdir(exist_ok=True)

    x_test: Vector = linspace(-10, 10, 100)
    y_test = x_test**2 * .1**x_test

    @apply_styles(_fallback=True)
    def simple_plot() -> None:
        """Create a simple plot."""
        plt.plot(x_test, y_test, label="test")
        plt.xlabel("$p$ [bar]")
        plt.ylabel(r"$\sqrt{y_c}$ [1/m]")
        plt.legend()
        plt.gca().set_yscale("log")
        plt.tight_layout()
        plt.savefig(LOCATION5)

    simple_plot()

    assert filename.exists()
