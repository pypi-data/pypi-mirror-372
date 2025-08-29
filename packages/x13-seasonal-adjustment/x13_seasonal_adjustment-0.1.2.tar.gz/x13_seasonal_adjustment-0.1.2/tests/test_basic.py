"""
Temel X13 seasonal adjustment testleri.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime

# Test edilecek modülleri import et
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from x13_seasonal_adjustment import (
    X13SeasonalAdjustment, 
    SeasonalAdjustmentResult, 
    SeasonalityTests,
    AutoARIMA,
    QualityDiagnostics
)


@pytest.fixture
def sample_monthly_data():
    """Örnek aylık zaman serisi oluşturur."""
    dates = pd.date_range(start='2020-01-01', periods=60, freq='M')
    
    # Trend + seasonality + noise
    trend = 100 + np.linspace(0, 20, 60)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(60) / 12)
    noise = np.random.normal(0, 2, 60)
    
    data = trend + seasonal + noise
    return pd.Series(data, index=dates, name='test_data')


@pytest.fixture 
def sample_quarterly_data():
    """Örnek çeyreklik zaman serisi oluşturur."""
    dates = pd.date_range(start='2020-01-01', periods=20, freq='Q')
    
    # Quarterly seasonality
    trend = 100 + np.linspace(0, 10, 20)
    seasonal = 5 * np.sin(2 * np.pi * np.arange(20) / 4)
    noise = np.random.normal(0, 1, 20)
    
    data = trend + seasonal + noise
    return pd.Series(data, index=dates, name='quarterly_data')


class TestX13SeasonalAdjustment:
    """X13SeasonalAdjustment sınıfı için testler."""
    
    def test_initialization(self):
        """X13 sınıfının başlatılması testi."""
        x13 = X13SeasonalAdjustment()
        
        assert x13.freq == 'M'
        assert x13.transform == 'auto'
        assert x13.outlier_detection == True
        assert x13._is_fitted == False
    
    def test_initialization_with_params(self):
        """Parametreli başlatma testi."""
        x13 = X13SeasonalAdjustment(
            freq='Q',
            transform='log',
            outlier_detection=False,
            trading_day=False
        )
        
        assert x13.freq == 'Q'
        assert x13.transform == 'log'
        assert x13.outlier_detection == False
        assert x13.trading_day == False
    
    def test_invalid_parameters(self):
        """Geçersiz parametreler testi."""
        with pytest.raises(ValueError):
            x13 = X13SeasonalAdjustment(freq='INVALID')
            x13._validate_parameters()
    
    def test_fit_transform_monthly(self, sample_monthly_data):
        """Aylık veri için fit_transform testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        # Result tipini kontrol et
        assert isinstance(result, SeasonalAdjustmentResult)
        
        # Temel özellikleri kontrol et
        assert len(result.original) == len(sample_monthly_data)
        assert len(result.seasonally_adjusted) == len(sample_monthly_data)
        assert len(result.seasonal_factors) == len(sample_monthly_data)
        assert len(result.trend) == len(sample_monthly_data)
        assert len(result.irregular) == len(sample_monthly_data)
        
        # Index uyumluluğu
        assert result.original.index.equals(sample_monthly_data.index)
        assert result.seasonally_adjusted.index.equals(sample_monthly_data.index)
        
        # Mevsimsellik gücü makul aralıkta olmalı
        assert 0 <= result.seasonality_strength <= 1
        assert 0 <= result.trend_strength <= 1
    
    def test_fit_transform_quarterly(self, sample_quarterly_data):
        """Çeyreklik veri için fit_transform testi."""
        x13 = X13SeasonalAdjustment(freq='Q')
        result = x13.fit_transform(sample_quarterly_data)
        
        assert isinstance(result, SeasonalAdjustmentResult)
        assert len(result.original) == len(sample_quarterly_data)
    
    def test_separate_fit_and_transform(self, sample_monthly_data):
        """Ayrı fit ve transform testleri."""
        x13 = X13SeasonalAdjustment(freq='M')
        
        # Önce fit
        x13.fit(sample_monthly_data)
        assert x13._is_fitted == True
        
        # Sonra transform
        result = x13.transform(sample_monthly_data)
        assert isinstance(result, SeasonalAdjustmentResult)
    
    def test_transform_without_fit(self, sample_monthly_data):
        """Fit edilmemiş modelde transform hatası."""
        x13 = X13SeasonalAdjustment(freq='M')
        
        with pytest.raises(ValueError, match="Model henüz eğitilmemiş"):
            x13.transform(sample_monthly_data)
    
    def test_insufficient_data(self):
        """Yetersiz veri testi."""
        short_data = pd.Series([1, 2, 3, 4, 5], 
                              index=pd.date_range('2020-01-01', periods=5, freq='M'))
        
        x13 = X13SeasonalAdjustment(freq='M')
        
        with pytest.raises(ValueError):
            x13.fit_transform(short_data)
    
    def test_forecast(self, sample_monthly_data):
        """Forecast testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        x13.fit(sample_monthly_data)
        
        forecast = x13.forecast(steps=12)
        
        assert isinstance(forecast, pd.Series)
        assert len(forecast) == 12
    
    def test_model_summary(self, sample_monthly_data):
        """Model özeti testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        x13.fit(sample_monthly_data)
        
        summary = x13.get_model_summary()
        
        assert isinstance(summary, dict)
        assert 'parameters' in summary
        assert 'arima_model' in summary
        assert 'preprocessing' in summary


class TestSeasonalAdjustmentResult:
    """SeasonalAdjustmentResult sınıfı için testler."""
    
    def test_result_creation(self, sample_monthly_data):
        """Result nesnesinin oluşturulması."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        # Temel özellikler
        assert hasattr(result, 'original')
        assert hasattr(result, 'seasonally_adjusted')
        assert hasattr(result, 'seasonal_factors')
        assert hasattr(result, 'trend')
        assert hasattr(result, 'irregular')
        assert hasattr(result, 'seasonality_strength')
        assert hasattr(result, 'trend_strength')
    
    def test_result_summary(self, sample_monthly_data):
        """Result özeti testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        summary = result.summary()
        
        assert isinstance(summary, pd.DataFrame)
        assert 'Metric' in summary.columns
        assert 'Value' in summary.columns
        assert len(summary) > 0
    
    def test_result_properties(self, sample_monthly_data):
        """Result özellikleri testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        # Seasonal variation ratio
        assert hasattr(result, 'seasonal_variation_ratio')
        assert 0 <= result.seasonal_variation_ratio <= 1
        
        # Decomposition quality
        assert hasattr(result, 'decomposition_quality')
        assert isinstance(result.decomposition_quality, str)
    
    def test_result_to_dict(self, sample_monthly_data):
        """Result to_dict testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'original' in result_dict
        assert 'seasonally_adjusted' in result_dict
        assert 'seasonality_strength' in result_dict


class TestSeasonalityTests:
    """SeasonalityTests sınıfı için testler."""
    
    def test_seasonality_detection(self, sample_monthly_data):
        """Mevsimsellik tespiti testi."""
        tester = SeasonalityTests(seasonal_period=12)
        result = tester.run_all_tests(sample_monthly_data)
        
        assert hasattr(result, 'has_seasonality')
        assert hasattr(result, 'confidence_level')
        assert hasattr(result, 'test_results')
        assert hasattr(result, 'recommendations')
        
        assert isinstance(result.has_seasonality, bool)
        assert 0 <= result.confidence_level <= 1
        assert isinstance(result.test_results, dict)
        assert isinstance(result.recommendations, list)
    
    def test_individual_tests(self, sample_monthly_data):
        """Individual testlerin çalışması."""
        tester = SeasonalityTests(seasonal_period=12)
        
        # X11 test
        x11_result = tester.x11_seasonality_test(sample_monthly_data)
        assert isinstance(x11_result, dict)
        
        # QS test
        qs_result = tester.qs_test(sample_monthly_data)
        assert isinstance(qs_result, dict)
        
        # Kruskal-Wallis test
        kw_result = tester.kruskal_wallis_test(sample_monthly_data)
        assert isinstance(kw_result, dict)


class TestAutoARIMA:
    """AutoARIMA sınıfı için testler."""
    
    def test_auto_arima_fit(self, sample_monthly_data):
        """AutoARIMA fit testi."""
        arima = AutoARIMA(seasonal_period=12, stepwise=True)
        arima.fit(sample_monthly_data)
        
        assert arima.is_fitted_ == True
        assert arima.order_ is not None
        assert arima.seasonal_order_ is not None
        assert arima.aic_ is not None
        assert arima.bic_ is not None
    
    def test_arima_forecast(self, sample_monthly_data):
        """ARIMA forecast testi."""
        arima = AutoARIMA(seasonal_period=12, stepwise=True)
        arima.fit(sample_monthly_data)
        
        forecast = arima.forecast(steps=6)
        
        assert isinstance(forecast, pd.Series)
        assert len(forecast) == 6
    
    def test_arima_diagnostic_tests(self, sample_monthly_data):
        """ARIMA diagnostic testleri."""
        arima = AutoARIMA(seasonal_period=12, stepwise=True)
        arima.fit(sample_monthly_data)
        
        diagnostics = arima.diagnostic_tests()
        
        assert isinstance(diagnostics, dict)
        assert 'ljung_box_stat' in diagnostics
        assert 'ljung_box_pvalue' in diagnostics


class TestQualityDiagnostics:
    """QualityDiagnostics sınıfı için testler."""
    
    def test_quality_evaluation(self, sample_monthly_data):
        """Kalite değerlendirmesi testi."""
        x13 = X13SeasonalAdjustment(freq='M')
        result = x13.fit_transform(sample_monthly_data)
        
        quality_diagnostics = QualityDiagnostics()
        quality_report = quality_diagnostics.evaluate(result)
        
        assert hasattr(quality_report, 'overall_quality')
        assert hasattr(quality_report, 'm_statistics')
        assert hasattr(quality_report, 'q_statistics')
        assert hasattr(quality_report, 'recommendations')
        assert hasattr(quality_report, 'warnings')
        assert hasattr(quality_report, 'summary_scores')
        
        assert isinstance(quality_report.overall_quality, str)
        assert isinstance(quality_report.m_statistics, dict)
        assert isinstance(quality_report.q_statistics, dict)
        assert isinstance(quality_report.recommendations, list)
        assert isinstance(quality_report.warnings, list)
        assert isinstance(quality_report.summary_scores, dict)


class TestDataValidation:
    """Veri doğrulama testleri."""
    
    def test_valid_series_input(self, sample_monthly_data):
        """Geçerli series input testi."""
        from x13_seasonal_adjustment.utils.validation import validate_time_series
        
        validated = validate_time_series(sample_monthly_data, freq='M')
        assert isinstance(validated, pd.Series)
        assert len(validated) == len(sample_monthly_data)
    
    def test_invalid_series_input(self):
        """Geçersiz series input testi."""
        from x13_seasonal_adjustment.utils.validation import validate_time_series
        
        # Çok kısa seri
        short_series = pd.Series([1, 2, 3])
        
        with pytest.raises(ValueError):
            validate_time_series(short_series, freq='M', min_length=10)
    
    def test_dataframe_input(self):
        """DataFrame input testi."""
        from x13_seasonal_adjustment.utils.validation import validate_time_series
        
        # Single column DataFrame
        dates = pd.date_range('2020-01-01', periods=30, freq='M')
        df = pd.DataFrame({'value': range(30)}, index=dates)
        
        validated = validate_time_series(df, freq='M')
        assert isinstance(validated, pd.Series)
        assert len(validated) == 30
    
    def test_numpy_array_input(self):
        """NumPy array input testi."""
        from x13_seasonal_adjustment.utils.validation import validate_time_series
        
        arr = np.random.randn(50)
        
        validated = validate_time_series(arr, freq='M')
        assert isinstance(validated, pd.Series)
        assert len(validated) == 50


# Integration testleri
class TestIntegration:
    """Entegrasyon testleri."""
    
    def test_full_workflow(self, sample_monthly_data):
        """Tam iş akışı testi."""
        # 1. Mevsimsellik testi
        seasonality_tester = SeasonalityTests(seasonal_period=12)
        seasonality_result = seasonality_tester.run_all_tests(sample_monthly_data)
        
        # 2. X13 seasonal adjustment
        x13 = X13SeasonalAdjustment(freq='M')
        adjustment_result = x13.fit_transform(sample_monthly_data)
        
        # 3. Kalite değerlendirmesi
        quality_diagnostics = QualityDiagnostics()
        quality_report = quality_diagnostics.evaluate(adjustment_result)
        
        # Tüm adımların başarılı olduğunu kontrol et
        assert seasonality_result is not None
        assert adjustment_result is not None
        assert quality_report is not None
        
        # Sonuçların makul olduğunu kontrol et
        assert isinstance(seasonality_result.has_seasonality, bool)
        assert 0 <= adjustment_result.seasonality_strength <= 1
        assert quality_report.overall_quality in ["Mükemmel", "İyi", "Orta", "Zayıf", "Çok Zayıf", "Belirlenemedi"]


if __name__ == "__main__":
    # Testleri çalıştır
    pytest.main([__file__, "-v"])
