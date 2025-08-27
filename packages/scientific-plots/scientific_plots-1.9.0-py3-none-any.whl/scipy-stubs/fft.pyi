"""This module contains the typing-stubs for the fft-module of scipy. They are
needed for type-checking by mypy."""
from typing import Tuple, TypeVar

from scientific_plots.types_ import Matrix, Vector


def fft(x: Vector) -> Vector: ...


def rfft(x: Vector) -> Vector: ...


def fft2(x: Matrix, s: Tuple[int, ...]) -> Matrix: ...


def rfft2(x: Matrix, s: Tuple[int, ...]) -> Matrix: ...


SmallDimension = TypeVar("SmallDimension", Matrix, Vector)


def fftshift(x: SmallDimension) -> SmallDimension: ...


def fftfreq(n: int, d: float = 1.0) -> Vector: ...


def rfftfreq(n: int, d: float = 1.0) -> Vector: ...
