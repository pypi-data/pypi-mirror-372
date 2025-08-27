#!/usr/bin/env python
"""This contains the animation module of matplotlib."""
from typing import Callable

from .figure import Figure


class FuncAnimation:
    """Animation class for matplotlib-plots."""

    def __init__(self, fig: Figure,
                 update: Callable[[int], None],
                 frames: int = 10,
                 repeat: bool = False) -> None: ...
