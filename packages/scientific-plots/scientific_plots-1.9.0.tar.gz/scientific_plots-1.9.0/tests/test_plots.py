#!/usr/bin/python
"""this set of unit-tests test the creation of plots by
'python-module'"""
from os import remove
from os.path import exists
from pathlib import Path

import numpy as np
from numpy import linspace
from pytest import mark

from scientific_plots.types_ import Vector
from scientific_plots.plot_settings import read_data_plot
from scientific_plots.default_plots import (
    plot, two_plots, two_axis_plots, plot_surface)


@mark.use_style
def test_default_plot(tmp_path: Path) -> None:
    """
    test the default plot creation by 'plot'
    """
    x_test: Vector = linspace(1., 100., 100)
    y_test: Vector = x_test**2

    x_label = "x-values"
    y_label = "y-values"
    filename = Path(".test_plot.tmp.pdf")
    filename2 = Path(".test_plot.tmp.png")
    plot(x_test, y_test, x_label, y_label, tmp_path / filename)
    assert exists(tmp_path / filename)

    # test data-plot creation
    assert exists(tmp_path / (filename.stem + ".csv"))
    data = read_data_plot(tmp_path / (filename.stem + ".csv"))
    assert data
    assert (list(data.values())[0][0] == x_test).all()
    assert (list(data.values())[0][1] == y_test).all()

    # remove plot to test another
    remove(tmp_path / filename)

    # logarithmic plot
    plot(x_test, y_test, x_label, y_label, tmp_path / filename, logscale=True)
    assert exists(tmp_path / filename)
    subfolder = ["sans_serif", "grayscale", "journal", "presentation"]
    for folder in subfolder:
        assert (
            exists(tmp_path / folder / filename)
            or exists(tmp_path / folder / filename2))


@mark.use_style
def test_default_plot_nan(tmp_path: Path) -> None:
    """
    Test the default plot creation by 'plot', if there are data points with
    nan.
    """
    x_test: Vector = linspace(2., 100., 50)
    y_test: Vector = x_test**2

    y_test[4] = np.nan
    y_test[6] = np.nan

    x_label = "x-values-nan"
    y_label = "y-values-nan"
    filename = Path(".test_plot_nan.tmp.pdf")
    plot(x_test, y_test, x_label, y_label, tmp_path / filename)
    assert exists(tmp_path / filename)


@mark.use_style
def test_two_plots(tmp_path: Path) -> None:
    """Test the creation of a twin-plot."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    filename = ".test_plot.tmp.pdf"
    two_plots(x_test, y_test1, "plot1",
              x_test, y_test2, "plot2",
              "x", "y",
              tmp_path / filename)
    assert exists(tmp_path / filename)


@mark.use_style
def test_twinx_plots(tmp_path: Path) -> None:
    """Test the creation of a twin-plot."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    filename = ".test_twin_plot.tmp.pdf"
    two_axis_plots(
        x_test, y_test1, "plot1",
        x_test, y_test2, "plot2",
        "x", "y", "y2",
        tmp_path / filename)
    assert exists(tmp_path / filename)

    remove(tmp_path / filename)
    # tick-plot
    two_axis_plots(
        x_test, y_test1, "plot1",
        x_test, y_test2, "plot2",
        "x", "y", "y2",
        tmp_path / filename,
        ticks=([1., 10.], ["a", "b"]))
    assert exists(tmp_path / filename)


@mark.use_style
def test_two_d_plot(tmp_path: Path) -> None:
    """Test the creation of a two dimensional surface plot."""
    x_test: Vector = linspace(1, 1e8, 1000)
    y_test: Vector = linspace(1, 1e8, 1000)
    x_test_grid, y_test_grid = np.meshgrid(
        x_test, y_test)
    z_grid = x_test_grid**2 + y_test_grid
    filename = Path(".test_two_d_plot.tmp.pdf")
    plot_surface(
        x_test_grid, y_test_grid, z_grid,
        "x-label", "y-label", "z-label",
        tmp_path / filename,
        log_scale=True)
    assert exists(tmp_path / filename)
