#!/usr/bin/env python3
"""
Typing stubs for skimage.filters.
"""
from typing import Optional, Union, Any
from scientific_plots.types_ import Matrix, Vector


def butterworth(
    image: Matrix,
    cutoff_frequency_ratio: float,
    order: int = 4,
    high_pass: bool = False,
    squared_butterworth: bool = False,
    npad: Optional[int] = None) -> Matrix: ...
