#!/usr/bin/env python
"""
Stub-files for scipy.signal. This module contains the type-annotations for
scipy's library for fourier-transformations and signal analysis.
"""
from typing import Tuple, Optional, Union, overload, TypeVar, Any

from scientific_plots.types_ import Vector, Matrix, Tensor


Input = TypeVar("Input", Vector, Matrix, Tensor)


def welch(
    Y: Union[Vector, list[float]],
    fs: Optional[float] = None,
    scaling: str = "density",
    window: Optional[str] = "hamming",
    nperseg: int = 10,
    detrend: bool = False) -> Tuple[Vector, Vector]: ...


def periodogram(
    Y: Union[Vector, list[float]],
    fs: Optional[float] = None,
    scaling: str = "density",
    window: Optional[str] = "hamming",
    detrend: bool = False) -> Tuple[Vector, Vector]: ...


Single = Union[Vector, list[float], tuple[float, ...]]
Double = Union[
    tuple[Vector, Vector], tuple[list[float], list[float]],
    tuple[tuple[float, ...], tuple[float, ...]]]


@overload
def savgol_filter(
    x: Single, window_length: Union[int, float], polyorder: int,
    deriv: Optional[int] = None, delta: Optional[float] = None,
    mode: str = "nearest") -> Vector: ...


@overload
def savgol_filter(
    x: Double, window_length: Union[int, float], polyorder: int,
    deriv: Optional[int] = None, delta: Optional[float] = None,
    mode: str = "nearest")\
        -> tuple[Vector, Vector]: ...


def sosfilt(
    sos: Single, x: Input,
    axis: int = -1, zi: Optional[Single] = None,
    padtype: Optional[str] = "odd", padlen: Optional[int] = None)\
        -> Input: ...


def sosfiltfilt(
    sos: Single, x: Input,
    axis: int = -1, zi: Optional[Single] = None,
    padtype: Optional[str] = "odd", padlen: Optional[int] = None)\
        -> Input: ...


def butter(
    N: int, Wn: Single, btype: str = "low", analog: bool = False,
    output: str = "ba", fs: Optional[float] = None) -> Vector: ...


def wiener(
    im: Input,
    noise: Optional[float] = None,
    mysize: Optional[Union[int, Vector]] = None) -> Input: ...


def sosfreqz(sos: Any,
             worN: Optional[Union[int, Vector]] = 512, 
             whole: bool = False, 
             fs: Optional[float] = None)\
	-> tuple[Vector, Vector]: ...
