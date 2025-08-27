"""This is a stub-file for scipy.special. It contains the typing for needed
function and allows the type-checker to work."""

from typing import TypeVar

from scientific_plots.types_ import Matrix, Vector, Tensor


Input = TypeVar("Input", float, Matrix, Vector, Tensor)


def expi(x: Input) -> Input: ...


def i0(x: Input) -> Input: ...


def erf(x: Input) -> Input: ...
