#!/usr/bin/env python
"""
Stubs for scipy.stats. Here are type-annotations for scipy's
linear-regression-like methods.
"""
from typing import Tuple, Union

from scientific_plots.types_ import Vector


Input = Union[Vector, list[float]]


def linregress(x: Input, y: Input) -> Tuple[float, float]: ...
