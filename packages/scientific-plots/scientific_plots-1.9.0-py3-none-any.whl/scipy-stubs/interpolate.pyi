"""Stub-file for scipy.interpolate. It also contains the typings of the used
functions."""
from __future__ import annotations

from typing import Callable, Optional, TypeVar, Union, overload, Literal

from scientific_plots.types_ import Matrix, Vector, Tensor

Input = TypeVar("Input", float, Matrix, Vector, Tensor)


def interp1d(x: Vector, y: Vector, fill_value: Optional[str] = "")\
    -> Callable[[Input], Input]: ...


class UnivariateSpline():
    """This class contains the spline-object of scipy."""

    def __init__(self, x: Vector, y: Vector,
                 k: int = 3, s: Optional[int] = None,
                 ext: Union[Literal[0], Literal[1], Literal[2], Literal[3],
                            Literal["extrapolate"], Literal["zeros"],
                            Literal["raise"], Literal["const"], str]
                 = "extrapolate",
                 check_finite: bool = False) -> None: ...

    def __call__(self, x: Input) -> Input: ...

    def derivative(self) -> UnivariateSpline: ...

    def roots(self) -> Vector: ...


class RectBivariateSpline:
    """This class contains a 2D spline of a surface."""

    def __init__(
        self,
        x: Union[Vector, list[float]],
        y: Union[Vector, list[float]],
        z: Union[Matrix, list[list[float]], list[Vector]],
        bbox: Optional[tuple[float, float, float, float]] = None,
        kx: int = 3,
        ky: int = 3,
        s: Optional[float] = 0) -> None: ...

    @overload
    def __call__(self,
                 x: Input,
                 y: Input,
                 dx: int = 0, dy: int = 0, *,
                 grid: Literal[False]) -> Input: ...

    @overload
    def __call__(self,
                 x: Union[Vector, list[float]],
                 y: Union[Vector, list[float]],
                 dx: int = 0, dy: int = 0, *,
                 grid: Literal[True]) -> Matrix: ...

    @overload
    def __call__(self,
                 x: Union[Vector, list[float]],
                 y: Union[Vector, list[float]],
                 dx: int = 0, dy: int = 0) -> Matrix: ...

    def integral(self,
                 xa: float, xb: float,
                 ya: float, yb: float) -> float: ...

    def ev(
        self, xi: Input, yi: Input, dx: Optional[int] = None,
        dy: Optional[int] = None) -> Input: ...

    def get_coeffs(self) -> list[float]: ...


class CubicSpline:
    """Types for the cubic spline function in scipy."""
    def __init__(
        self,
        x: Union[Vector, list[float]],
        y: Union[Vector, list[float]],
        axis: Optional[int] = 0,
        bc_type: Optional[Union[str, tuple[float, float]]] = None,
        extrapolate: Optional[Union[str, bool]] = None) -> None: ...

    def __call__(self, x: Input, nu: int = 0,
                 extrapolate: Optional[Union[bool, str]] = None) -> Input: ...

    def derivative(self) -> CubicSpline: ...

    def integrate(self,
                  a: float, b: float,
                  extrapolate: Optional[Union[str, bool]] = None) -> float: ...


def griddata(
    points: Matrix, values: Union[Vector, float, complex],
    xi: Union[Matrix, tuple[Vector, ...]], method: str = "linear",
    fill_value: float = float("nan"), rescale: bool = False
    ) -> Matrix: ...
