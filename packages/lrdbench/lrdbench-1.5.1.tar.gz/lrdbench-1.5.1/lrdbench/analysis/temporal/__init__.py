"""
Temporal analysis estimators for LRDBench.

This module provides various temporal estimators for analyzing long-range dependence
in time series data.
"""

# Auto-optimized estimators (working ones)
from lrdbench.analysis.auto_optimized_estimator import AutoRSEstimator as RSEstimator
from lrdbench.analysis.auto_optimized_estimator import AutoDMAEstimator as DMAEstimator
from lrdbench.analysis.auto_optimized_estimator import AutoHiguchiEstimator as HiguchiEstimator

# Standard DFA (NUMBA version has issues)
from lrdbench.analysis.temporal.dfa.dfa_estimator import DFAEstimator

# Import individual modules for direct access
from .rs import rs_estimator
from .dma import dma_estimator
from .dfa import dfa_estimator
from .higuchi import higuchi_estimator

__all__ = [
    "RSEstimator",
    "DMAEstimator", 
    "DFAEstimator",
    "HiguchiEstimator",
    "rs_estimator",
    "dma_estimator",
    "dfa_estimator",
    "higuchi_estimator",
]
