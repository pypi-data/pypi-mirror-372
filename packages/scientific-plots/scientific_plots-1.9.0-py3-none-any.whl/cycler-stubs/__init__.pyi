#!/usr/bin/env python3
"""
Type hints for the cyler class, which is included in matplotlib and used for
property cycles.
"""
from __future__ import annotations

from typing import Union, Any


class cycler:
    """Property cycle."""
    
    def __init__(
        self,
        color: Union[None,
                     list[tuple[float, float, float]],
                     list[str]] = None,
        linestyle: Union[None,
                         list[Union[str, tuple[int, tuple[int, ...]]]],
                         tuple[int, tuple[int, ...]]] = None): ...

    def __add__(self, other: cycler) -> cycler: ...

    def __mul__(self, other: cycler) -> cycler: ...

    def by_key(self) -> dict[str, Any]: ...
