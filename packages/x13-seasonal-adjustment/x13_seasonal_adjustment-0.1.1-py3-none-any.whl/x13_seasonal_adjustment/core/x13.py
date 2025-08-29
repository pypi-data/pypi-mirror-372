"""
Ana X13 Seasonal Adjustment sınıfı.
"""

from typing import Optional, Union, Tuple, Dict, Any, List
import pandas as pd
import numpy as np
import warnings
from sklearn.base import BaseEstimator, TransformerMixin

from .result import SeasonalAdjustmentResult
from .decomposition import SeasonalDecomposition
from ..arima.auto_arima import AutoARIMA
from ..tests.seasonality_tests import SeasonalityTests
from ..utils.validation import validate_time_series
from ..utils.preprocessing import preprocess_series


class X13SeasonalAdjustment(BaseEstimator, TransformerMixin):
    """
    X13-ARIMA-SEATS mevsimsellikten arındırma ana sınıfı.
    
    Bu sınıf, ABD Sayım Bürosu'nun X13-ARIMA-SEATS programının metodolojisini 
    takip ederek zaman serilerindeki mevsimsellik etkilerini tespit eder ve arındırır.
    
    Parameters:
        freq (str): Veri frekansı ('M' = Aylık, 'Q' = Çeyreklik, 'A' = Yıllık)
        transform (str): Logaritmik dönüşüm ('auto', 'log', 'none')
        outlier_detection (bool): Aykırı değer tespiti yapılsın mı?
        outlier_types (List[str]): Tespit edilecek aykırı değer tipleri
        trading_day (bool): İş günü etkisi modellenir mi?
        easter (bool): Paskalya etkisi modellenir mi?
        arima_order (Union[Tuple, str]): ARIMA model sırası veya 'auto'
        seasonal_arima_order (Union[Tuple, str]): Mevsimsel ARIMA sırası
        max_seasonal_ma (int): Maksimum mevsimsel MA sırası
        x11_mode (str): X11 dekompozisyon modu ('multiplicative', 'additive', 'auto')
        forecast_maxlead (int): Maksimum öngörü uzunluğu
        backcast_maxlead (int): Maksimum geçmiş öngörü uzunluğu
    """
    
    def __init__(
        self,
        freq: str = 'M',
        transform: str = 'auto',
        outlier_detection: bool = True,
        outlier_types: List[str] = None,
        trading_day: bool = True,
        easter: bool = True,
        arima_order: Union[Tuple[int, int, int], str] = 'auto',
        seasonal_arima_order: Union[Tuple[int, int, int], str] = 'auto',
        max_seasonal_ma: int = 2,
        x11_mode: str = 'auto',
        forecast_maxlead: int = 12,
        backcast_maxlead: int = 12,
        **kwargs
    ):
        self.freq = freq
        self.transform = transform
        self.outlier_detection = outlier_detection
        self.outlier_types = outlier_types or ['AO', 'LS', 'TC']
        self.trading_day = trading_day
        self.easter = easter
        self.arima_order = arima_order
        self.seasonal_arima_order = seasonal_arima_order
        self.max_seasonal_ma = max_seasonal_ma
        self.x11_mode = x11_mode
        self.forecast_maxlead = forecast_maxlead
        self.backcast_maxlead = backcast_maxlead
        
        # İç değişkenler
        self._is_fitted = False
        self._arima_model = None
        self._seasonal_decomposer = None
        self._seasonality_tester = None
        self._original_series = None
        self._preprocessing_info = None
    
    def _validate_parameters(self) -> None:
        """Parametre doğrulaması yapar."""
        valid_freqs = ['M', 'Q', 'A', 'D', 'W']
        if self.freq not in valid_freqs:
            raise ValueError(f"freq '{self.freq}' geçersiz. Geçerli değerler: {valid_freqs}")
        
        valid_transforms = ['auto', 'log', 'none']
        if self.transform not in valid_transforms:
            raise ValueError(f"transform '{self.transform}' geçersiz. Geçerli değerler: {valid_transforms}")
        
        valid_x11_modes = ['auto', 'multiplicative', 'additive']
        if self.x11_mode not in valid_x11_modes:
            raise ValueError(f"x11_mode '{self.x11_mode}' geçersiz. Geçerli değerler: {valid_x11_modes}")
        
        valid_outlier_types = ['AO', 'LS', 'TC', 'SO']
        for otype in self.outlier_types:
            if otype not in valid_outlier_types:
                raise ValueError(f"Aykırı değer tipi '{otype}' geçersiz. Geçerli değerler: {valid_outlier_types}")
    
    def _determine_seasonal_period(self, series: pd.Series) -> int:
        """Frekansa göre mevsimsel dönem uzunluğunu belirler."""
        freq_to_period = {
            'M': 12,   # Aylık
            'Q': 4,    # Çeyreklik  
            'A': 1,    # Yıllık
            'D': 365,  # Günlük
            'W': 52    # Haftalık
        }
        return freq_to_period.get(self.freq, 12)
    
    def _determine_transform(self, series: pd.Series) -> str:
        """Otomatik logaritmik dönüşüm kararı verir."""
        if self.transform != 'auto':
            return self.transform
        
        # Coefficient of variation kullanarak karar ver
        cv = np.std(series) / np.mean(series)
        
        # Log-level test
        if cv > 0.2:  # Yüksek variasyon
            return 'log'
        else:
            return 'none'
    
    def _apply_transform(self, series: pd.Series, transform_type: str) -> Tuple[pd.Series, Dict]:
        """Veri dönüşümü uygular."""
        transform_info = {'type': transform_type}
        
        if transform_type == 'log':
            if (series <= 0).any():
                warnings.warn("Negatif değerler logaritmik dönüşüm için düzeltiliyor")
                min_val = series.min()
                shift = abs(min_val) + 1 if min_val <= 0 else 0
                series = series + shift
                transform_info['shift'] = shift
            
            transformed = np.log(series)
            transform_info['applied'] = True
        else:
            transformed = series.copy()
            transform_info['applied'] = False
        
        return transformed, transform_info
    
    def _reverse_transform(self, series: pd.Series, transform_info: Dict) -> pd.Series:
        """Dönüşümü tersine çevirir."""
        if not transform_info.get('applied', False):
            return series
        
        # Log dönüşümünü tersine çevir
        result = np.exp(series)
        
        # Shift varsa tersine çevir
        if 'shift' in transform_info:
            result = result - transform_info['shift']
        
        return result
    
    def fit(self, X: Union[pd.Series, pd.DataFrame], y=None) -> 'X13SeasonalAdjustment':
        """
        X13 modelini eğitir.
        
        Args:
            X (Union[pd.Series, pd.DataFrame]): Zaman serisi verisi
            y: İgnore edilir (sklearn uyumluluğu için)
            
        Returns:
            X13SeasonalAdjustment: Eğitilmiş model
        """
        self._validate_parameters()
        
        # Veriyi doğrula ve hazırla
        series = validate_time_series(X, freq=self.freq)
        self._original_series = series.copy()
        
        # Ön işleme
        preprocessed_series, self._preprocessing_info = preprocess_series(
            series, 
            handle_missing=True,
            detect_outliers=self.outlier_detection
        )
        
        # Mevsimsellik tespiti
        self._seasonality_tester = SeasonalityTests(
            seasonal_period=self._determine_seasonal_period(series)
        )
        seasonality_result = self._seasonality_tester.run_all_tests(preprocessed_series)
        
        if not seasonality_result.has_seasonality:
            warnings.warn("Seride belirgin mevsimsellik tespit edilmedi. Sonuçlar güvenilir olmayabilir.")
        
        # Dönüşüm belirle ve uygula
        transform_type = self._determine_transform(preprocessed_series)
        transformed_series, transform_info = self._apply_transform(preprocessed_series, transform_type)
        self._preprocessing_info['transform'] = transform_info
        
        # ARIMA modeli eğit
        self._arima_model = AutoARIMA(
            seasonal_period=self._determine_seasonal_period(series),
            max_p=3, max_q=3, max_P=2, max_Q=2,
            max_d=2, max_D=1,
            information_criterion='aicc',
            seasonal=True
        )
        
        self._arima_model.fit(transformed_series)
        
        # Mevsimsel dekompozitör hazırla
        self._seasonal_decomposer = SeasonalDecomposition(
            mode=self.x11_mode,
            seasonal_period=self._determine_seasonal_period(series),
            arima_model=self._arima_model,
            forecast_maxlead=self.forecast_maxlead,
            backcast_maxlead=self.backcast_maxlead
        )
        
        self._is_fitted = True
        return self
    
    def transform(self, X: Union[pd.Series, pd.DataFrame]) -> SeasonalAdjustmentResult:
        """
        Mevsimsellikten arındırma işlemini gerçekleştirir.
        
        Args:
            X (Union[pd.Series, pd.DataFrame]): Zaman serisi verisi
            
        Returns:
            SeasonalAdjustmentResult: Mevsimsellikten arındırma sonuçları
        """
        if not self._is_fitted:
            raise ValueError("Model henüz eğitilmemiş. Önce fit() metodunu çağırın.")
        
        series = validate_time_series(X, freq=self.freq)
        
        # Aynı ön işleme adımlarını uygula
        preprocessed_series, _ = preprocess_series(
            series,
            handle_missing=True,
            outlier_info=self._preprocessing_info.get('outliers')
        )
        
        # Dönüşüm uygula
        transform_info = self._preprocessing_info['transform']
        transformed_series, _ = self._apply_transform(preprocessed_series, transform_info['type'])
        
        # Mevsimsel dekompozisyon
        decomposition_result = self._seasonal_decomposer.decompose(transformed_series)
        
        # Sonuçları orijinal ölçeğe çevir
        seasonally_adjusted = self._reverse_transform(
            decomposition_result['seasonally_adjusted'], 
            transform_info
        )
        trend = self._reverse_transform(decomposition_result['trend'], transform_info)
        
        # Mevsimsel faktörleri ve düzensiz bileşeni hesapla
        if transform_info['type'] == 'log':
            # Çarpımsal model
            seasonal_factors = decomposition_result['seasonal'] 
            irregular = decomposition_result['irregular']
        else:
            # Toplamsal model  
            seasonal_factors = decomposition_result['seasonal']
            irregular = decomposition_result['irregular']
        
        # Mevsimsellik ve trend gücünü hesapla
        seasonality_strength = self._calculate_seasonality_strength(
            series, seasonal_factors
        )
        trend_strength = self._calculate_trend_strength(series, trend)
        
        # Kalite ölçütlerini hesapla
        quality_measures = self._calculate_quality_measures(
            series, seasonally_adjusted, seasonal_factors, irregular
        )
        
        # ARIMA model bilgileri
        arima_info = {
            'order': self._arima_model.order_,
            'seasonal_order': self._arima_model.seasonal_order_,
            'aic': self._arima_model.aic_,
            'bic': self._arima_model.bic_,
        }
        
        return SeasonalAdjustmentResult(
            original=series,
            seasonally_adjusted=seasonally_adjusted,
            seasonal_factors=seasonal_factors,
            trend=trend,
            irregular=irregular,
            seasonality_strength=seasonality_strength,
            trend_strength=trend_strength,
            trading_day_factors=decomposition_result.get('trading_day'),
            easter_factors=decomposition_result.get('easter'),
            outliers=self._preprocessing_info.get('outliers'),
            arima_model_info=arima_info,
            quality_measures=quality_measures
        )
    
    def fit_transform(self, X: Union[pd.Series, pd.DataFrame], y=None) -> SeasonalAdjustmentResult:
        """
        Modeli eğitir ve dönüştürür.
        
        Args:
            X (Union[pd.Series, pd.DataFrame]): Zaman serisi verisi
            y: İgnore edilir
            
        Returns:
            SeasonalAdjustmentResult: Mevsimsellikten arındırma sonuçları
        """
        return self.fit(X, y).transform(X)
    
    def _calculate_seasonality_strength(self, original: pd.Series, seasonal: pd.Series) -> float:
        """Mevsimsellik gücünü hesaplar."""
        seasonal_var = np.var(seasonal)
        total_var = np.var(original)
        
        if total_var == 0:
            return 0.0
        
        return min(1.0, max(0.0, seasonal_var / total_var))
    
    def _calculate_trend_strength(self, original: pd.Series, trend: pd.Series) -> float:
        """Trend gücünü hesaplar."""
        detrended = original - trend
        detrended_var = np.var(detrended)
        total_var = np.var(original)
        
        if total_var == 0:
            return 0.0
        
        return min(1.0, max(0.0, 1 - (detrended_var / total_var)))
    
    def _calculate_quality_measures(
        self, 
        original: pd.Series, 
        seasonally_adjusted: pd.Series,
        seasonal: pd.Series,
        irregular: pd.Series
    ) -> Dict[str, float]:
        """X13 kalite ölçütlerini hesaplar (M ve Q istatistikleri)."""
        quality = {}
        
        # M1 - Contribution of the irregular to the variance of the stationary portion
        if len(irregular) > 12:
            m1 = np.var(irregular) / np.var(seasonally_adjusted)
            quality['M1'] = m1
        
        # M7 - Amount of month-to-month change in the irregular component
        if len(irregular) > 1:
            irregular_diff = irregular.diff().dropna()
            if len(irregular_diff) > 0:
                m7 = np.std(irregular_diff) / np.std(irregular)
                quality['M7'] = m7
        
        # Q - Overall quality measure
        m_stats = [v for k, v in quality.items() if k.startswith('M')]
        if m_stats:
            quality['Q'] = np.mean(m_stats)
        
        return quality
    
    def forecast(self, steps: int = 12) -> pd.Series:
        """
        Mevsimsellikten arındırılmış seri için öngörü yapar.
        
        Args:
            steps (int): Öngörü adım sayısı
            
        Returns:
            pd.Series: Öngörü değerleri
        """
        if not self._is_fitted:
            raise ValueError("Model henüz eğitilmemiş.")
        
        return self._arima_model.forecast(steps=steps)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Model özetini döndürür.
        
        Returns:
            Dict[str, Any]: Model bilgileri
        """
        if not self._is_fitted:
            raise ValueError("Model henüz eğitilmemiş.")
        
        summary = {
            'parameters': {
                'freq': self.freq,
                'transform': self.transform,
                'outlier_detection': self.outlier_detection,
                'trading_day': self.trading_day,
                'easter': self.easter,
            },
            'arima_model': {
                'order': self._arima_model.order_,
                'seasonal_order': self._arima_model.seasonal_order_,
                'aic': self._arima_model.aic_,
                'bic': self._arima_model.bic_,
            },
            'preprocessing': self._preprocessing_info,
        }
        
        return summary
