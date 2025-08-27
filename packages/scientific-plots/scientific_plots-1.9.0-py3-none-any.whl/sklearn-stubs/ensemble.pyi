#!/usr/bin/env python3
"""
Typing stubs for sklearn.ensemble.
"""
from __future__ import annotations

from typing import Optional, Union, List, Dict, TypeVar
from scientific_plots.types_ import Matrix, Vector as Vector_


Vector = TypeVar("Vector", bound=Union[Vector_, Matrix])


class IsolationForest:
    def __init__(self, 
                 n_estimators: int = 100, 
                 max_samples: Union[int, float, str] = 'auto', 
                 contamination: Union[float, str] = 'auto', 
                 max_features: float = 1.0, 
                 bootstrap: bool = False, 
                 n_jobs: Optional[int] = None, 
                 behaviour: str = 'deprecated', 
                 random_state: Optional[int] = None, 
                 verbose: int = 0, 
                 warm_start: bool = False) -> None: ...
    
    def fit(self, 
            X: Vector, 
            y: Optional[Vector] = None, 
            sample_weight: Optional[Vector] = None) -> 'IsolationForest': ...
    
    def predict(self, X: Vector) -> Vector: ...
    
    def fit_predict(self, 
                    X: Vector, 
                    y: Optional[Vector] = None, 
                    sample_weight: Optional[Vector] = None) -> Vector: ...
    
    def decision_function(self, X: Vector) -> Vector: ...
    
    def score_samples(self, X: Vector) -> Vector: ...
    
    def get_params(self, 
                   deep: bool = True) -> Dict[str, 
                                            Union[int, float, str, bool, None]]: ...
    
    def set_params(self, params: dict[str, float]) -> IsolationForest: ...

    # Additional methods for compatibility with BaseEstimator and OutlierMixin
    def __getstate__(self) -> dict[str, float]: ...
    def __setstate__(self, state: dict[str, float]) -> None: ...

    # Properties
    @property
    def estimators_(self) -> List[float]: ...

    @property
    def estimators_samples_(self) -> List[float]: ...

    @property
    def max_samples_(self) -> int: ...

    @property
    def offset_(self) -> float: ...
