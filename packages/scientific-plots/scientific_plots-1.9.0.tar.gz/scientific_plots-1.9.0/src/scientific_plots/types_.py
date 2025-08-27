#!/usr/env python
# pylint: disable=unsubscriptable-object
"""This module contains the types, which can be used for static
type-checking in Python_Module."""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Any

import numpy as np
from pytest import FixtureRequest

if TYPE_CHECKING:
    NTensor = np.ndarray[Tuple[int, int, int, int], np.dtype[np.float64]]
    Tensor = np.ndarray[Tuple[int, int, int], np.dtype[np.float64]]
    Matrix = np.ndarray[Tuple[int, int], np.dtype[np.float64]]
    Vector = np.ndarray[Tuple[int], np.dtype[np.float64]]
else:
    NTensor = np.ndarray
    Tensor = np.ndarray
    Matrix = np.ndarray
    Vector = np.ndarray


class Request(FixtureRequest):
    """This is the pytest-fixture request plus the missing attribute 'param'.
    It contains the given parameters to this object and thus this fixture."""
    param: Any
