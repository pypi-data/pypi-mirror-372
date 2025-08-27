#!/usr/bin/env python
"""
This are the stubs for the submodule "style" of matplotlib.pyplot.
"""
from contextlib import contextmanager
from collections.abc import Generator


def use(style: str = "default") -> None: ...


@contextmanager
def context(style: str) -> Generator[None, None, None]: ...
