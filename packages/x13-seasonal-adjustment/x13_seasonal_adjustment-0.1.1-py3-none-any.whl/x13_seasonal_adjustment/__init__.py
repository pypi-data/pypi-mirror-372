"""
X13 Seasonal Adjustment Library

Türkiye'de geliştirilen kapsamlı X13-ARIMA-SEATS mevsimsellikten arındırma kütüphanesi.

Bu kütüphane, zaman serisi verilerindeki mevsimsellik etkilerini tespit etmek ve 
bunları arındırmak için X13-ARIMA-SEATS algoritmasının Python implementasyonunu sağlar.

Temel Kullanım:
    >>> import pandas as pd
    >>> from x13_seasonal_adjustment import X13SeasonalAdjustment
    >>> 
    >>> # Veri yükle
    >>> data = pd.Series([100, 110, 95, 105, 120, 108, 90, 98, 125, 115, 88, 102])
    >>> 
    >>> # Mevsimsellikten arındır
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

__version__ = "0.1.1"
__author__ = "Gardash Abbasov"
__email__ = "gardash.abbasov@gmail.com"

__all__ = [
    "X13SeasonalAdjustment",
    "SeasonalAdjustmentResult", 
    "SeasonalityTests",
    "AutoARIMA",
    "QualityDiagnostics",
]
