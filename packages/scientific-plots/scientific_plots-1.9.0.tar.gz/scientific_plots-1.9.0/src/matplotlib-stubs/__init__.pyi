#!/usr/bin/env python
"""
These are the stub-files for matplot-lib. This stub-module also contains the
sub-modules, which are sometimes needed when using matplot-lib functions. This
stub-file provides the types, so mypy can use static-type-checking on scripts
or modules, which use matplot-lib. No function is implemented in this folder.
"""
from __future__ import annotations
from typing import Union, overload, Literal

from cycler import cycler

from .cm import ColormapRegistry


def use(backend: str) -> None: ...


def rc(object_: str, **kwargs: Union[
        str,
        bool,
        dict[str, int],
        int]) -> None: ...


class RCParams:
    """Default parameters of the creation of plots in matplot-lib."""

    def update(self, params: Union[dict[str,
                                        Union[int, list[float], str,
                                              tuple[float, float]]
                                        ],
                                   RCParams]) -> None: ...

    def __setitem__(self, key: str, value: Union[list[str],
                                                 int,
                                                 str,
                                                 tuple[float, float],
                                                 cycler])\
        -> None: ...

    @overload
    def __getitem__(self, key: Literal["axes.prop_cycle"]) -> cycler: ...

    @overload
    def __getitem__(self, key: str) -> Union[list[str], cycler]: ...


rcParams: RCParams


rcParamsDefault: RCParams


colormaps: ColormapRegistry
