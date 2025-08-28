"""
Analysis module for LRDBench.

This module provides various estimators for analyzing long-range dependence
in time series data using both temporal and spectral methods.
"""

# Auto-optimized estimator system
from lrdbench.analysis.auto_optimized_estimator import AutoOptimizedEstimator

# Standard DFA (fallback)
from lrdbench.analysis.temporal.dfa.dfa_estimator import DFAEstimator

# Import submodules
from . import temporal
from . import spectral

__all__ = [
    # Auto-optimized estimator system
    "AutoOptimizedEstimator",
    
    # Standard estimators
    "DFAEstimator",
    
    # Submodules
    "temporal",
    "spectral",
]
