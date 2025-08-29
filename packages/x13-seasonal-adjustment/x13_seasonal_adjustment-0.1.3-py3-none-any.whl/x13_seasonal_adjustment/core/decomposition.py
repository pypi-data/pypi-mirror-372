"""
X11 mevsimsel dekompozisyon algoritması.
"""

from typing import Dict, Optional, Union
import pandas as pd
import numpy as np
from scipy import signal
from statsmodels.tsa.filters.hp_filter import hpfilter


class SeasonalDecomposition:
    """
    X11 algoritmasına dayalı mevsimsel dekompozisyon sınıfı.
    
    Bu sınıf, X13-ARIMA-SEATS'in kalbi olan X11 dekompozisyon algoritmasını
    implementasyonunu sağlar.
    """
    
    def __init__(
        self,
        mode: str = 'auto',
        seasonal_period: int = 12,
        arima_model = None,
        forecast_maxlead: int = 12,
        backcast_maxlead: int = 12,
        henderson_filter_length: int = 13
    ):
        self.mode = mode
        self.seasonal_period = seasonal_period  
        self.arima_model = arima_model
        self.forecast_maxlead = forecast_maxlead
        self.backcast_maxlead = backcast_maxlead
        self.henderson_filter_length = henderson_filter_length
    
    def decompose(self, series: pd.Series) -> Dict[str, pd.Series]:
        """
        X11 dekompozisyonu gerçekleştirir.
        
        Args:
            series (pd.Series): Dekompozisyon yapılacak zaman serisi
            
        Returns:
            Dict[str, pd.Series]: Dekompozisyon bileşenleri
        """
        # 1. Mod belirleme (toplamsal vs çarpımsal)
        decomposition_mode = self._determine_mode(series)
        
        # 2. Seriyi genişlet (öngörü ve geçmiş öngörü ile)
        extended_series = self._extend_series(series)
        
        # 3. İlk kaba trend tahmini
        preliminary_trend = self._estimate_preliminary_trend(extended_series)
        
        # 4. İlk mevsimsel-düzensiz bileşen
        if decomposition_mode == 'multiplicative':
            seasonal_irregular = extended_series / preliminary_trend
        else:
            seasonal_irregular = extended_series - preliminary_trend
        
        # 5. İlk mevsimsel faktörler
        seasonal_factors = self._estimate_seasonal_factors(
            seasonal_irregular, mode=decomposition_mode
        )
        
        # 6. İlk mevsimsellikten arındırma
        if decomposition_mode == 'multiplicative':
            seasonally_adjusted = extended_series / seasonal_factors
        else:
            seasonally_adjusted = extended_series - seasonal_factors
        
        # 7. İkinci trend tahmini (Henderson filtresi)
        final_trend = self._henderson_filter(seasonally_adjusted)
        
        # 8. İkinci mevsimsel faktörler (trend düzeltmeli)
        if decomposition_mode == 'multiplicative':
            seasonal_irregular_2 = extended_series / final_trend
        else:
            seasonal_irregular_2 = extended_series - final_trend
        
        final_seasonal = self._estimate_seasonal_factors(
            seasonal_irregular_2, mode=decomposition_mode, iteration=2
        )
        
        # 9. Final mevsimsellikten arındırma
        if decomposition_mode == 'multiplicative':
            final_sa = extended_series / final_seasonal
        else:
            final_sa = extended_series - final_seasonal
        
        # 10. Düzensiz bileşen
        if decomposition_mode == 'multiplicative':
            irregular = final_sa / final_trend
        else:
            irregular = final_sa - final_trend
        
        # 11. Orijinal seri uzunluğuna geri dön
        original_length = len(series)
        start_idx = self.backcast_maxlead
        end_idx = start_idx + original_length
        
        result = {
            'trend': final_trend.iloc[start_idx:end_idx],
            'seasonal': final_seasonal.iloc[start_idx:end_idx],
            'seasonally_adjusted': final_sa.iloc[start_idx:end_idx],
            'irregular': irregular.iloc[start_idx:end_idx],
            'mode': decomposition_mode
        }
        
        return result
    
    def _determine_mode(self, series: pd.Series) -> str:
        """Dekompozisyon modunu (toplamsal vs çarpımsal) belirler."""
        if self.mode != 'auto':
            return self.mode
        
        # Otomatik mod belirleme: varyans stabilite testi
        # Seride logaritmik dönüşümün etkisini test et
        log_series = np.log(series[series > 0])
        
        # Her yıl için varyansı hesapla
        if self.seasonal_period == 12:  # Aylık veri
            years = series.index.year.unique()
            variances = []
            log_variances = []
            
            for year in years:
                year_data = series[series.index.year == year]
                log_year_data = log_series[log_series.index.year == year]
                
                if len(year_data) >= 6:  # En az 6 gözlem
                    variances.append(np.var(year_data))
                    if len(log_year_data) >= 6:
                        log_variances.append(np.var(log_year_data))
            
            if len(variances) >= 2 and len(log_variances) >= 2:
                # Varyans kararlılığını karşılaştır
                var_cv = np.std(variances) / np.mean(variances)
                log_var_cv = np.std(log_variances) / np.mean(log_variances)
                
                # Logaritmik dönüşüm varyansı daha kararlı hale getiriyorsa çarpımsal
                return 'multiplicative' if log_var_cv < var_cv else 'additive'
        
        # Default: ortalama ile varyans arasındaki ilişkiye bak
        mean_val = np.mean(series)
        std_val = np.std(series)
        cv = std_val / mean_val
        
        return 'multiplicative' if cv > 0.1 else 'additive'
    
    def _extend_series(self, series: pd.Series) -> pd.Series:
        """Seriyi ARIMA öngörüsü ile genişletir."""
        if self.arima_model is None:
            # ARIMA modeli yoksa basit trend ile genişlet
            return self._simple_extend(series)
        
        # Geçmiş öngörü (backcast)
        backcast = self.arima_model.predict_in_sample(start=-self.backcast_maxlead)
        
        # Gelecek öngörü (forecast) 
        forecast = self.arima_model.forecast(steps=self.forecast_maxlead)
        
        # Forecast tuple ise ilk elementi al (predicted values)
        if isinstance(forecast, tuple):
            forecast = forecast[0]  # İlk element predicted_mean
        
        # Pandas Series'se values'ları al
        if hasattr(forecast, 'values'):
            forecast = forecast.values
        
        # Numpy array'e çevir
        forecast = np.asarray(forecast, dtype=float)
        
        # Backcast sonucunu numpy array'e çevir
        if hasattr(backcast, 'values'):  # pandas Series/DataFrame
            backcast = backcast.values  
        if hasattr(backcast, 'flatten'):  # multi-dimensional array
            backcast = backcast.flatten()
        backcast = np.asarray(backcast)
        
        # Forecast sonucunun uzunluğunu kontrol et ve gerekirse ayarla
        if len(forecast) != self.forecast_maxlead:
            # Eğer daha az değer dönerse, son değeri tekrarla
            if len(forecast) < self.forecast_maxlead:
                last_value = forecast[-1] if len(forecast) > 0 else series.iloc[-1]
                additional_values = np.repeat(last_value, self.forecast_maxlead - len(forecast))
                forecast = np.concatenate([forecast, additional_values])
            # Eğer daha fazla değer dönerse, ilk n tanesini al
            else:
                forecast = forecast[:self.forecast_maxlead]
        
        # Backcast için de aynı kontrolü yap
        if len(backcast) != self.backcast_maxlead:
            if len(backcast) < self.backcast_maxlead:
                first_value = backcast[0] if len(backcast) > 0 else series.iloc[0]
                additional_values = np.repeat(first_value, self.backcast_maxlead - len(backcast))
                backcast = np.concatenate([additional_values, backcast])
            else:
                backcast = backcast[-self.backcast_maxlead:]
        
        # Genişletilmiş seri oluştur
        backcast_index = pd.date_range(
            end=series.index[0] - pd.Timedelta(days=1),
            periods=self.backcast_maxlead,
            freq=series.index.freq
        )
        
        forecast_index = pd.date_range(
            start=series.index[-1] + pd.Timedelta(days=1),
            periods=self.forecast_maxlead,
            freq=series.index.freq
        )
        
        backcast_series = pd.Series(backcast, index=backcast_index)
        forecast_series = pd.Series(forecast, index=forecast_index)
        
        extended = pd.concat([backcast_series, series, forecast_series])
        return extended
    
    def _simple_extend(self, series: pd.Series) -> pd.Series:
        """ARIMA modeli olmadığında basit genişletme."""
        # Basit lineer trend ile genişlet
        n = len(series)
        x = np.arange(n)
        y = series.values
        
        # Lineer regresyon
        coeffs = np.polyfit(x, y, 1)
        trend_func = np.poly1d(coeffs)
        
        # Geçmiş genişletme
        back_x = np.arange(-self.backcast_maxlead, 0)
        back_values = trend_func(back_x)
        
        # Gelecek genişletme  
        fore_x = np.arange(n, n + self.forecast_maxlead)
        fore_values = trend_func(fore_x)
        
        # Index'leri oluştur
        back_index = pd.date_range(
            end=series.index[0] - pd.Timedelta(days=1),
            periods=self.backcast_maxlead,
            freq=series.index.freq
        )
        
        fore_index = pd.date_range(
            start=series.index[-1] + pd.Timedelta(days=1), 
            periods=self.forecast_maxlead,
            freq=series.index.freq
        )
        
        back_series = pd.Series(back_values, index=back_index)
        fore_series = pd.Series(fore_values, index=fore_index)
        
        return pd.concat([back_series, series, fore_series])
    
    def _estimate_preliminary_trend(self, series: pd.Series) -> pd.Series:
        """İlk kaba trend tahmini yapar."""
        # 2x12 hareketli ortalama (aylık veri için)
        if self.seasonal_period == 12:
            # 12-dönem hareketli ortalama
            ma12 = series.rolling(window=12, center=True).mean()
            # 2-dönem hareketli ortalama (merkezleme için)
            trend = ma12.rolling(window=2, center=True).mean()
        elif self.seasonal_period == 4:
            # Çeyreklik veri için 2x4 hareketli ortalama
            ma4 = series.rolling(window=4, center=True).mean()
            trend = ma4.rolling(window=2, center=True).mean()
        else:
            # Genel durum için 2xperiod hareketli ortalama
            ma_period = series.rolling(window=self.seasonal_period, center=True).mean()
            trend = ma_period.rolling(window=2, center=True).mean()
        
        # NaN değerleri lineer interpolasyon ile doldur
        trend = trend.interpolate(method='linear')
        
        return trend
    
    def _estimate_seasonal_factors(
        self, 
        seasonal_irregular: pd.Series, 
        mode: str,
        iteration: int = 1
    ) -> pd.Series:
        """Mevsimsel faktörleri tahmin eder."""
        
        seasonal_factors = pd.Series(index=seasonal_irregular.index, dtype=float)
        
        # Her dönem için ortalama hesapla
        for period in range(self.seasonal_period):
            # Bu döneme ait tüm değerleri bul
            period_positions = np.arange(len(seasonal_irregular)) % self.seasonal_period
            mask = period_positions == period
            period_values = seasonal_irregular.iloc[mask]
            
            if len(period_values) > 0:
                if iteration == 1:
                    # İlk iterasyonda basit ortalama
                    if mode == 'multiplicative':
                        factor = np.median(period_values)  # Median daha robust
                    else:
                        factor = np.mean(period_values)
                else:
                    # İkinci iterasyonda weighted ortalama
                    weights = self._calculate_seasonal_weights(period_values)
                    factor = np.average(period_values, weights=weights)
                
                seasonal_factors.iloc[mask] = factor
        
        # NaN değerleri için interpolation yap
        if seasonal_factors.isna().any():
            # Her period için ortalama faktörü hesapla
            period_groups = np.arange(len(seasonal_factors)) % self.seasonal_period
            period_means = seasonal_factors.groupby(period_groups).mean()
            
            # NaN değerleri ilgili period ortalaması ile doldur
            for i, is_nan in enumerate(seasonal_factors.isna()):
                if is_nan:
                    period = i % self.seasonal_period
                    if not pd.isna(period_means.iloc[period]):
                        seasonal_factors.iloc[i] = period_means.iloc[period]
                    else:
                        # Eğer period ortalaması da NaN ise, genel ortalama kullan
                        overall_mean = seasonal_factors.mean()
                        if not pd.isna(overall_mean):
                            if mode == 'multiplicative':
                                seasonal_factors.iloc[i] = 1.0  # Nötr çarpan
                            else:
                                seasonal_factors.iloc[i] = 0.0  # Nötr toplam
                        else:
                            # Son çare: sabit değer
                            seasonal_factors.iloc[i] = 1.0 if mode == 'multiplicative' else 0.0
        
        # Seasonal faktörleri normalize et
        if mode == 'multiplicative':
            # Çarpımsal modelde ortalama 1 olmalı
            period_groups = np.arange(len(seasonal_factors)) % self.seasonal_period
            mean_factor = seasonal_factors.groupby(period_groups).mean().mean()
            if mean_factor != 0 and not pd.isna(mean_factor):
                seasonal_factors = seasonal_factors / mean_factor
        else:
            # Toplamsal modelde toplam 0 olmalı  
            period_groups = np.arange(len(seasonal_factors)) % self.seasonal_period
            mean_factor = seasonal_factors.groupby(period_groups
            ).mean().sum() / self.seasonal_period
            if not pd.isna(mean_factor):
                seasonal_factors = seasonal_factors - mean_factor
        
        return seasonal_factors
    
    def _calculate_seasonal_weights(self, values: pd.Series) -> np.ndarray:
        """Mevsimsel faktör hesaplamada kullanılacak ağırlıkları hesaplar."""
        # Son yıllara daha fazla ağırlık ver
        n = len(values)
        weights = np.ones(n)
        
        # Son 3 yıla daha fazla ağırlık
        if n > 3:
            weights[-3:] *= 2.0
        
        # Aykırı değerlere düşük ağırlık
        q75, q25 = np.percentile(values, [75, 25])
        iqr = q75 - q25
        outlier_threshold = 1.5 * iqr
        
        for i, val in enumerate(values):
            if abs(val - np.median(values)) > outlier_threshold:
                weights[i] *= 0.5
        
        return weights / np.sum(weights)
    
    def _henderson_filter(self, series: pd.Series) -> pd.Series:
        """Henderson filtresi ile trend hesaplar."""
        # Henderson filtre katsayılarını hesapla
        n = self.henderson_filter_length
        weights = self._henderson_weights(n)
        
        # Filtreyi uygula
        # Pandas rolling ile custom weights kullan
        def apply_henderson(x):
            if len(x) == n:
                return np.sum(x * weights)
            else:
                return np.nan
        
        # Rolling window uygula
        filtered = series.rolling(
            window=n, 
            center=True
        ).apply(apply_henderson, raw=True)
        
        # Uç noktalarda lineer interpolasyon
        filtered = filtered.interpolate(method='linear')
        
        return filtered
    
    def _henderson_weights(self, n: int) -> np.ndarray:
        """Henderson filtre ağırlıklarını hesaplar."""
        if n == 13:
            # 13-dönem Henderson filtresi (en yaygın)
            weights = np.array([
                -0.019, -0.028, 0.0, 0.066, 0.147, 0.214, 
                0.240, 0.214, 0.147, 0.066, 0.0, -0.028, -0.019
            ])
        elif n == 9:
            # 9-dönem Henderson filtresi
            weights = np.array([
                -0.041, -0.010, 0.119, 0.267, 0.330, 
                0.267, 0.119, -0.010, -0.041
            ])
        else:
            # Genel Henderson filtre formülü
            m = (n - 1) // 2
            weights = np.zeros(n)
            
            for i in range(n):
                j = i - m
                if abs(j) <= m:
                    numerator = 315 * (m**2 - j**2) * (m**4 - j**4)
                    denominator = 8 * m * (m**2 - 1) * (4*m**2 - 1) * (4*m**2 - 9)
                    weights[i] = numerator / denominator
        
        # Ağırlıkları normalize et
        return weights / np.sum(weights)
