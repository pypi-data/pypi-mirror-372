"""
X13 Seasonal Adjustment Library

Comprehensive X13-ARIMA-SEATS seasonal adjustment library for Python.

This library provides a Python implementation of the X13-ARIMA-SEATS algorithm
for detecting and removing seasonal effects from time series data.

Basic Usage:
    >>> import pandas as pd
    >>> from x13_seasonal_adjustment import X13SeasonalAdjustment
    >>> 
    >>> # Load data
    >>> data = pd.Series([100, 110, 95, 105, 120, 108, 90, 98, 125, 115, 88, 102])
    >>> 
    >>> # Apply seasonal adjustment
    >>> x13 = X13SeasonalAdjustment()
    >>> result = x13.fit_transform(data)
    >>> 
    >>> print(result.seasonally_adjusted)
"""

from .core.x13 import X13SeasonalAdjustment
from .core.result import SeasonalAdjustmentResult
from .tests.seasonality_tests import SeasonalityTests
from .arima.auto_arima import AutoARIMA
from .diagnostics.quality import QualityDiagnostics

__version__ = "0.1.3"
__author__ = "Gardash Abbasov"
__email__ = "gardash.abbasov@gmail.com"

__all__ = [
    "X13SeasonalAdjustment",
    "SeasonalAdjustmentResult", 
    "SeasonalityTests",
    "AutoARIMA",
    "QualityDiagnostics",
]
