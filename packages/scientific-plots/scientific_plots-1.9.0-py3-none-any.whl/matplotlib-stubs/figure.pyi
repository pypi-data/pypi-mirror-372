#!/usr/bin/env python
"""This is the stub for the figure-type in matplot-lib."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Iterable, Any, Union

from .pyplot import Axes


class Canvas:
    """Canvas, which contains the figure."""

    def draw(self) -> None: ...

    def fush_events(self) -> None: ...


class Figure:

    axes: Iterable[Axes]

    canvas: Canvas

    def __init__(
        self, figsize: Optional[Tuple[float, float]] = None) -> None: ...

    def gca(self) -> Axes: ...

    def set_size_inches(self, x: float, y: float) -> None: ...

    def subplots_adjust(self, bottom: Optional[float] = None,
                        right: Optional[float] = None,
                        left: Optional[float] = None,
                        top: Optional[float] = None,
                        ) -> None: ...

    def add_subplot(self, position: int = 111,
                    projection: str = "2d") -> Axes: ...

    def set_label(self, label: str) -> None: ...

    def text(self, x: float, y: float, s: str) -> None: ...

    def legend(self, *args: Any, **kwargs: Any) -> None: ...

    def savefig(
        self, fname: Union[str, Path], *,
        dpi: Union[str, float, int, None] = "figure",
        bbox_inches: Optional[Union[tuple[float, float], str]] = None,
        pad_inches: float = 0.1, backend: Optional[str] = None
        ) -> None: ...

    def tight_layout(self) -> None: ...
