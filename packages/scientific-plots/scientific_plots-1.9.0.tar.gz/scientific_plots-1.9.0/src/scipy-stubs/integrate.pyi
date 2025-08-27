"""Integration-methods in scipy. This module contains their typing and can be
used for static type-checking."""
from typing import Callable, Tuple, Any, TypeVar, Optional

from scientific_plots.types_ import Matrix, Vector, Tensor

Input = TypeVar("Input", float, Matrix, Vector, Tensor,
                list[float])


def romberg(func: Callable[[Input], Input], x_min: float, x_max: float,
            tol: float = 1e-30,
            rtol: float = 1e-30,
            divmax: int = 15) -> float: ...


def quad(func: Callable[..., Input], xmin: float, xmax: float,
         limit: int = 50, epsabs: float = 1.49e-8, epsrel: float = 1.49e-8,
         args: Optional[tuple[float, ...]] = None)\
    -> Tuple[float, Any]: ...


def dblquad(func: Callable[[Input, Input], Input], a: float, b: float,
            gfun: Callable[[Input], Input],
            hfun: Callable[[Input], Input]) -> Tuple[float, Any]: ...


def simps(y: Input, x: Optional[Input] = None, dx: int = 1, axis: int = -1,
          even: str = "avg") -> float: ...


def trapz(y: Input, x: Optional[Input] = None, dx: float = 1, axis: int = -1)\
        -> float: ...
