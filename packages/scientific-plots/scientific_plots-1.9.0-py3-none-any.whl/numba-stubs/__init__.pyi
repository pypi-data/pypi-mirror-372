"""This is a stub-file for the numba-module for numeric python calculations. It
contains the typing for the used functions and functionals. This allows for a
type-checking using mypy."""

from typing import (
    Callable, TypeVar, Iterable, Iterator, Optional, Any)
from contextlib import contextmanager

from functools import wraps


Out = TypeVar("Out")


def jit(parallel: bool = False, nopython: bool = True, nogil: bool = False,
        cache: bool = False, fastmath: bool = False)\
        -> Callable[[Callable[..., Out]], Callable[..., Out]]:
    """This are the types of the decorator jit.
    Decorators with arguments return function, that takes a function as an
    argument. E.g. they return a decorator without parameters."""

    def decorator(func: Callable[..., Out]) -> Callable[..., Out]:
        """This is the unparametrized decorator"""

        @wraps(func)
        def wrapped_fun(*args: Any, **kwargs: Any) -> Out: ...

        return wrapped_fun

    return decorator


def prange(i: int) -> Iterable[int]: ...


@contextmanager
def objmode(**kwargs: Optional[str]) -> Iterator[None]: ...
