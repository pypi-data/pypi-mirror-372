"""Stub-Files for the Hurst-Module."""
from typing import Any, Tuple, Optional

from scientific_plots.types_ import Vector


def compute_Hc(x: Vector, kind: Optional[str] = "change",
               simplified: bool = True)\
    -> Tuple[float, Any, Any]: ...
