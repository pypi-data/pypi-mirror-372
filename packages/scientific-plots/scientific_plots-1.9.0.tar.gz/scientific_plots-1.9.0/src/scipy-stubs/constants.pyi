#!/usr/bin/env python3
"""
Stub file for sciypy-constants.
"""
from typing import Dict, Tuple

pi: float
golden: float
golden_ratio: float
N_A: float
Avogadro: float
Boltzmann: float
gas_constant: float


def value(key: str) -> float: ...


def unit(key: str) -> str: ...


def precision(key: str) -> float: ...


physical_constants: Dict[str, Tuple[float, str, float]]
