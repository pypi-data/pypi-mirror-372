#!/usr/bin/env python
"""
This test-file contains test for the behaviour of new types, which are defined
in the python module. Numpy-arrays often create errors, when they are used by
static type checkers, because the multiplication sometimes returns a
NoReturn-type.
"""
import numpy as np

from scientific_plots.types_ import Matrix


def test_static_checking() -> None:
    """Test matrix-multiplications."""
    N = 20
    M = 31
    x: Matrix = np.random.rand(N, M)
    z = x**2 + x*x  # type: ignore
    # the type-checkings needs to be ignored, because we cannot use
    # numpy-version 1.21, where proper type-checking is introduced. This is due
    # to a dependency of numba.
    assert z is not None
