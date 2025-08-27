#!/usr/bin/env python
"""
Stub-file for usage with matplot-lib. This file registers color-maps for later
usage.
"""
from typing import Union

from .colors import LinearSegmentedColormap, ListedColormap


def register_cmap(name: str, cmap: Union[LinearSegmentedColormap,
                  ListedColormap]) -> None: ...


class ColormapRegistry:
    """Container for colormaps."""
    def register(
        self,
        cmap: Union[LinearSegmentedColormap, ListedColormap])\
        -> None: ...
