#!/usr/bin/python
"""This file contains the unit-tests for utilities in python_module"""
from os import remove
from pathlib import Path

from scientific_plots.utilities import write_file, read_file, running_average


def test_average() -> None:
    """test the running average"""
    x_test = [1. for _ in range(100)]
    for i in range(1, 10):
        assert running_average(x_test, i) == x_test


def test_read_write(tmp_path: Path) -> None:
    """test the read and the write functions of the utilities"""
    x_list = list(float(x) for x in range(20))
    y_list = [x**2 for x in x_list]
    filename = ".test.tmp"
    write_file(tmp_path / filename, x_list, y_list)
    x_new, y_new = read_file(tmp_path / filename)
    remove(tmp_path / filename)
    assert x_list == x_new
    assert y_list == y_new
