#!/usr/bin/env python3
"""
Stubs for matplotlib-ticker.
"""
from __future__ import annotations

from typing import Callable, Any


def StrMethodFormatter(format_str: str) -> str: ...


def FuncFormatter(func: Callable[[float, Any], str]) -> None: ...


class Locator:
    """Base class for locators."""


class MaxNLocator(Locator):
    """N ticks on an axis."""
    nbins: int

    def __init__(self, nbins: int): ...


class AutoLocator(Locator):
    """Autolocator."""
    nbins: int

    def __init__(self, nbins: int): ...
