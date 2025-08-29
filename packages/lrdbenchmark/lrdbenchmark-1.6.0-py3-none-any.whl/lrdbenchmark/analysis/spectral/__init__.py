"""
Spectral analysis estimators for LRDBench.

This module provides various spectral estimators for analyzing long-range dependence
in time series data using frequency domain methods.
"""

# Auto-optimized estimators (working ones)
from lrdbench.analysis.auto_optimized_estimator import AutoGPHEstimator as GPHEstimator
from lrdbench.analysis.auto_optimized_estimator import AutoPeriodogramEstimator as PeriodogramEstimator
from lrdbench.analysis.auto_optimized_estimator import AutoWhittleEstimator as WhittleEstimator

# Import individual modules for direct access
from .gph import gph_estimator
from .periodogram import periodogram_estimator
from .whittle import whittle_estimator

__all__ = [
    "GPHEstimator",
    "PeriodogramEstimator",
    "WhittleEstimator",
    "gph_estimator",
    "periodogram_estimator",
    "whittle_estimator",
]
