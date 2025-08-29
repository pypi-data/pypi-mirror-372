"""
Mevsimsellik tespiti için istatistiksel testler.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.diagnostic import acorr_ljungbox


@dataclass
class SeasonalityTestResult:
    """
    Mevsimsellik testi sonuçları.
    
    Attributes:
        has_seasonality (bool): Mevsimsellik var mı?
        confidence_level (float): Güven düzeyi (0-1)
        test_results (Dict): Individual test sonuçları
        recommendations (List[str]): Öneriler
    """
    has_seasonality: bool
    confidence_level: float
    test_results: Dict[str, Dict]
    recommendations: List[str]


class SeasonalityTests:
    """
    Zaman serilerinde mevsimsellik tespiti için kapsamlı test sınıfı.
    
    Bu sınıf, X13-ARIMA-SEATS'de kullanılan mevsimsellik tespit yöntemlerini
    ve ek robust testleri implementasyonunu sağlar.
    """
    
    def __init__(self, seasonal_period: int = 12, alpha: float = 0.05):
        self.seasonal_period = seasonal_period
        self.alpha = alpha
    
    def run_all_tests(self, series: pd.Series) -> SeasonalityTestResult:
        """
        Tüm mevsimsellik testlerini çalıştırır ve birleşik sonuç verir.
        
        Args:
            series (pd.Series): Test edilecek zaman serisi
            
        Returns:
            SeasonalityTestResult: Birleşik test sonuçları
        """
        
        test_results = {}
        seasonal_evidence = []
        
        # 1. X11 Seasonality Test (F-test based)
        try:
            x11_result = self.x11_seasonality_test(series)
            test_results['x11_test'] = x11_result
            seasonal_evidence.append(x11_result['is_seasonal'])
        except Exception as e:
            test_results['x11_test'] = {'error': str(e)}
        
        # 2. QS (QS Test for Seasonality)
        try:
            qs_result = self.qs_test(series)
            test_results['qs_test'] = qs_result
            seasonal_evidence.append(qs_result['is_seasonal'])
        except Exception as e:
            test_results['qs_test'] = {'error': str(e)}
        
        # 3. Kruskal-Wallis Test
        try:
            kw_result = self.kruskal_wallis_test(series)
            test_results['kruskal_wallis'] = kw_result
            seasonal_evidence.append(kw_result['is_seasonal'])
        except Exception as e:
            test_results['kruskal_wallis'] = {'error': str(e)}
        
        # 4. Friedman Test
        try:
            friedman_result = self.friedman_test(series)
            test_results['friedman'] = friedman_result
            seasonal_evidence.append(friedman_result['is_seasonal'])
        except Exception as e:
            test_results['friedman'] = {'error': str(e)}
        
        # 5. Autocorrelation Test
        try:
            autocorr_result = self.autocorrelation_test(series)
            test_results['autocorrelation'] = autocorr_result
            seasonal_evidence.append(autocorr_result['is_seasonal'])
        except Exception as e:
            test_results['autocorrelation'] = {'error': str(e)}
        
        # 6. Combined Seasonality Test (X13 style)
        try:
            combined_result = self.combined_seasonality_test(series)
            test_results['combined'] = combined_result
            seasonal_evidence.append(combined_result['is_seasonal'])
        except Exception as e:
            test_results['combined'] = {'error': str(e)}
        
        # Birleşik karar ver
        valid_tests = [evidence for evidence in seasonal_evidence if evidence is not None]
        
        if len(valid_tests) == 0:
            has_seasonality = False
            confidence = 0.0
        else:
            seasonal_count = sum(valid_tests)
            has_seasonality = seasonal_count > len(valid_tests) / 2
            confidence = seasonal_count / len(valid_tests)
        
        # Öneriler oluştur
        recommendations = self._generate_recommendations(test_results, has_seasonality, confidence)
        
        return SeasonalityTestResult(
            has_seasonality=has_seasonality,
            confidence_level=confidence,
            test_results=test_results,
            recommendations=recommendations
        )
    
    def x11_seasonality_test(self, series: pd.Series) -> Dict:
        """
        X11 F-test based seasonality test.
        
        X13-ARIMA-SEATS'de kullanılan temel mevsimsellik testidir.
        """
        
        # Minimum veri kontrolü
        if len(series) < 2 * self.seasonal_period:
            return {
                'is_seasonal': None,
                'f_statistic': None,
                'p_value': None,
                'error': 'Insufficient data for X11 test'
            }
        
        try:
            # Seasonal decomposition
            decomposition = seasonal_decompose(
                series, 
                model='additive', 
                period=self.seasonal_period,
                extrapolate_trend='freq'
            )
            
            seasonal_component = decomposition.seasonal
            residual_component = decomposition.resid.dropna()
            
            # F-test for seasonality
            # H0: No seasonality (seasonal component variance = 0)
            # H1: Seasonality exists
            
            seasonal_var = np.var(seasonal_component.dropna())
            residual_var = np.var(residual_component)
            
            if residual_var == 0:
                f_stat = float('inf')
                p_value = 0.0
            else:
                f_stat = seasonal_var / residual_var
                
                # Degrees of freedom
                df1 = self.seasonal_period - 1
                df2 = len(residual_component) - self.seasonal_period
                
                if df2 > 0:
                    p_value = 1 - stats.f.cdf(f_stat, df1, df2)
                else:
                    p_value = None
            
            is_seasonal = p_value is not None and p_value < self.alpha
            
            return {
                'is_seasonal': is_seasonal,
                'f_statistic': f_stat,
                'p_value': p_value,
                'seasonal_variance': seasonal_var,
                'residual_variance': residual_var,
                'test_type': 'X11 F-test'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'X11 test failed: {str(e)}'
            }
    
    def qs_test(self, series: pd.Series) -> Dict:
        """
        QS (Quality Seasonality) Test.
        
        Ljung-Box testi tabanlı mevsimsellik testi.
        """
        
        try:
            # Seasonal differencing
            seasonal_diff = series.diff(self.seasonal_period).dropna()
            
            if len(seasonal_diff) < self.seasonal_period:
                return {
                    'is_seasonal': None,
                    'error': 'Insufficient data for QS test'
                }
            
            # Ljung-Box test on seasonal differences
            lags = min(self.seasonal_period, len(seasonal_diff) // 4)
            
            if lags < 1:
                return {
                    'is_seasonal': None,
                    'error': 'Not enough lags for QS test'
                }
            
            lb_result = acorr_ljungbox(seasonal_diff, lags=lags, return_df=True)
            
            # Test istatistiği ve p-value
            qs_stat = lb_result['lb_stat'].iloc[-1]
            p_value = lb_result['lb_pvalue'].iloc[-1]
            
            # Seasonality varsa autocorrelation olmamalı (H0: no autocorr)
            # p < alpha ise autocorrelation var, seasonality zayıf
            is_seasonal = p_value >= self.alpha
            
            return {
                'is_seasonal': is_seasonal,
                'qs_statistic': qs_stat,
                'p_value': p_value,
                'test_type': 'QS Test (Ljung-Box based)'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'QS test failed: {str(e)}'
            }
    
    def kruskal_wallis_test(self, series: pd.Series) -> Dict:
        """
        Kruskal-Wallis test for seasonal differences.
        
        Non-parametric test for checking if different seasons
        have the same distribution.
        """
        
        try:
            # Group data by season
            seasonal_groups = []
            
            for season in range(self.seasonal_period):
                season_data = []
                for i in range(season, len(series), self.seasonal_period):
                    season_data.append(series.iloc[i])
                
                if len(season_data) >= 2:  # En az 2 gözlem gerekli
                    seasonal_groups.append(season_data)
            
            if len(seasonal_groups) < 2:
                return {
                    'is_seasonal': None,
                    'error': 'Not enough seasonal groups for Kruskal-Wallis test'
                }
            
            # Kruskal-Wallis test
            h_stat, p_value = stats.kruskal(*seasonal_groups)
            
            # H0: All seasons have same distribution
            # H1: At least one season differs (seasonality exists)
            is_seasonal = p_value < self.alpha
            
            return {
                'is_seasonal': is_seasonal,
                'h_statistic': h_stat,
                'p_value': p_value,
                'num_groups': len(seasonal_groups),
                'test_type': 'Kruskal-Wallis'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'Kruskal-Wallis test failed: {str(e)}'
            }
    
    def friedman_test(self, series: pd.Series) -> Dict:
        """
        Friedman test for seasonality.
        
        Non-parametric alternative to repeated measures ANOVA.
        """
        
        try:
            # Reshape data into matrix (years x seasons)
            n_complete_cycles = len(series) // self.seasonal_period
            
            if n_complete_cycles < 2:
                return {
                    'is_seasonal': None,
                    'error': 'Need at least 2 complete cycles for Friedman test'
                }
            
            # Create matrix
            data_matrix = []
            for year in range(n_complete_cycles):
                year_data = []
                for season in range(self.seasonal_period):
                    idx = year * self.seasonal_period + season
                    if idx < len(series):
                        year_data.append(series.iloc[idx])
                
                if len(year_data) == self.seasonal_period:
                    data_matrix.append(year_data)
            
            if len(data_matrix) < 2:
                return {
                    'is_seasonal': None,
                    'error': 'Not enough complete years for Friedman test'
                }
            
            # Friedman test
            data_array = np.array(data_matrix)
            stat, p_value = stats.friedmanchisquare(*data_array.T)
            
            # H0: No seasonal effect
            # H1: Seasonal effect exists
            is_seasonal = p_value < self.alpha
            
            return {
                'is_seasonal': is_seasonal,
                'friedman_statistic': stat,
                'p_value': p_value,
                'num_years': len(data_matrix),
                'test_type': 'Friedman Test'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'Friedman test failed: {str(e)}'
            }
    
    def autocorrelation_test(self, series: pd.Series) -> Dict:
        """
        Autocorrelation-based seasonality test.
        
        Tests for significant autocorrelation at seasonal lags.
        """
        
        try:
            from statsmodels.tsa.stattools import acf
            
            max_lags = min(len(series) // 2, 3 * self.seasonal_period)
            
            if max_lags < self.seasonal_period:
                return {
                    'is_seasonal': None,
                    'error': 'Not enough data for autocorrelation test'
                }
            
            # Calculate autocorrelation function
            autocorr, confint = acf(
                series, 
                nlags=max_lags, 
                alpha=self.alpha,
                fft=True
            )
            
            # Check for significant autocorrelation at seasonal lags
            seasonal_lags = [self.seasonal_period, 2 * self.seasonal_period]
            if max_lags >= 3 * self.seasonal_period:
                seasonal_lags.append(3 * self.seasonal_period)
            
            significant_seasonal_lags = []
            seasonal_autocorrs = []
            
            for lag in seasonal_lags:
                if lag < len(autocorr):
                    acf_value = autocorr[lag]
                    # Confidence interval check
                    lower_ci = confint[lag, 0] - autocorr[0]
                    upper_ci = confint[lag, 1] - autocorr[0]
                    
                    # Check if autocorrelation is significantly different from 0
                    if acf_value < lower_ci or acf_value > upper_ci:
                        significant_seasonal_lags.append(lag)
                    
                    seasonal_autocorrs.append(acf_value)
            
            # Test istatistiği: seasonal lag'lerdeki autocorrelation'ların karesi toplamı
            seasonal_acf_sum = sum([abs(autocorr[lag]) for lag in seasonal_lags 
                                  if lag < len(autocorr)])
            
            is_seasonal = len(significant_seasonal_lags) > 0
            
            return {
                'is_seasonal': is_seasonal,
                'seasonal_autocorrelations': seasonal_autocorrs,
                'significant_lags': significant_seasonal_lags,
                'seasonal_acf_sum': seasonal_acf_sum,
                'test_type': 'Autocorrelation Test'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'Autocorrelation test failed: {str(e)}'
            }
    
    def combined_seasonality_test(self, series: pd.Series) -> Dict:
        """
        Combined seasonality test (X13-ARIMA-SEATS style).
        
        Birleşik mevsimsellik testi, çoklu kriterleri değerlendirir.
        """
        
        try:
            # 1. Seasonal strength (STL decomposition based)
            seasonal_strength = self._calculate_seasonal_strength(series)
            
            # 2. Seasonal variance ratio
            seasonal_var_ratio = self._calculate_seasonal_variance_ratio(series)
            
            # 3. Peak detection in periodogram
            periodogram_peak = self._detect_periodogram_peak(series)
            
            # Combined decision logic
            criteria_met = 0
            total_criteria = 3
            
            # Criterion 1: Seasonal strength > threshold
            if seasonal_strength > 0.3:
                criteria_met += 1
            
            # Criterion 2: Seasonal variance ratio > threshold  
            if seasonal_var_ratio > 0.1:
                criteria_met += 1
            
            # Criterion 3: Significant peak at seasonal frequency
            if periodogram_peak['has_seasonal_peak']:
                criteria_met += 1
            
            # Decision: majority of criteria must be met
            is_seasonal = criteria_met >= (total_criteria / 2)
            confidence = criteria_met / total_criteria
            
            return {
                'is_seasonal': is_seasonal,
                'confidence': confidence,
                'seasonal_strength': seasonal_strength,
                'seasonal_variance_ratio': seasonal_var_ratio,
                'periodogram_peak': periodogram_peak,
                'criteria_met': criteria_met,
                'total_criteria': total_criteria,
                'test_type': 'Combined Seasonality Test'
            }
            
        except Exception as e:
            return {
                'is_seasonal': None,
                'error': f'Combined test failed: {str(e)}'
            }
    
    def _calculate_seasonal_strength(self, series: pd.Series) -> float:
        """STL decomposition ile seasonal strength hesaplar."""
        try:
            decomposition = seasonal_decompose(
                series,
                model='additive',
                period=self.seasonal_period,
                extrapolate_trend='freq'
            )
            
            seasonal_var = np.var(decomposition.seasonal.dropna())
            remainder_var = np.var(decomposition.resid.dropna())
            
            if seasonal_var + remainder_var == 0:
                return 0.0
            
            strength = seasonal_var / (seasonal_var + remainder_var)
            return min(1.0, max(0.0, strength))
            
        except:
            return 0.0
    
    def _calculate_seasonal_variance_ratio(self, series: pd.Series) -> float:
        """Seasonal variance ratio hesaplar."""
        try:
            # Her mevsim için varyans hesapla
            seasonal_vars = []
            
            for season in range(self.seasonal_period):
                season_data = [series.iloc[i] for i in range(season, len(series), self.seasonal_period)]
                if len(season_data) > 1:
                    seasonal_vars.append(np.var(season_data))
            
            if not seasonal_vars:
                return 0.0
            
            # Seasonal variance'ların varyansı / total variance
            seasonal_var_variation = np.var(seasonal_vars)
            total_variance = np.var(series)
            
            if total_variance == 0:
                return 0.0
            
            return seasonal_var_variation / total_variance
            
        except:
            return 0.0
    
    def _detect_periodogram_peak(self, series: pd.Series) -> Dict:
        """Periodogram'da seasonal frequency'de peak tespit eder."""
        try:
            from scipy.signal import periodogram
            
            # Periodogram hesapla
            frequencies, psd = periodogram(series.values)
            
            # Seasonal frequency
            seasonal_freq = 1.0 / self.seasonal_period
            
            # En yakın frequency index'ini bul
            freq_idx = np.argmin(np.abs(frequencies - seasonal_freq))
            
            # Peak detection: seasonal frequency'deki power
            seasonal_power = psd[freq_idx]
            
            # Threshold: ortalama power'ın 2 katı
            mean_power = np.mean(psd[1:])  # DC component'i hariç tut
            threshold = 2 * mean_power
            
            has_peak = seasonal_power > threshold
            
            return {
                'has_seasonal_peak': has_peak,
                'seasonal_power': seasonal_power,
                'mean_power': mean_power,
                'power_ratio': seasonal_power / mean_power if mean_power > 0 else 0
            }
            
        except:
            return {
                'has_seasonal_peak': False,
                'error': 'Periodogram analysis failed'
            }
    
    def _generate_recommendations(
        self, 
        test_results: Dict, 
        has_seasonality: bool, 
        confidence: float
    ) -> List[str]:
        """Test sonuçlarına göre öneriler oluşturur."""
        
        recommendations = []
        
        if has_seasonality:
            if confidence > 0.8:
                recommendations.append("Güçlü mevsimsellik tespit edildi. X13 seasonal adjustment önerilir.")
            elif confidence > 0.6:
                recommendations.append("Orta düzeyde mevsimsellik var. Seasonal adjustment yapılabilir.")
            else:
                recommendations.append("Zayıf mevsimsellik tespit edildi. Dikkatli seasonal adjustment gerekli.")
            
            # Specific test recommendations
            if 'x11_test' in test_results and test_results['x11_test'].get('is_seasonal'):
                recommendations.append("X11 F-test pozitif: Additive seasonal decomposition uygun.")
            
            if 'autocorrelation' in test_results:
                autocorr_result = test_results['autocorrelation']
                if autocorr_result.get('is_seasonal') and autocorr_result.get('seasonal_acf_sum', 0) > 0.5:
                    recommendations.append("Güçlü seasonal autocorrelation: SARIMA modeli önerilir.")
        
        else:
            recommendations.append("Belirgin mevsimsellik tespit edilmedi.")
            
            if confidence < 0.2:
                recommendations.append("Seasonal adjustment gerekli değil. Trend-cycle analysis yeterli olabilir.")
            else:
                recommendations.append("Borderline durum: Ek testler veya uzman değerlendirmesi önerilir.")
        
        # Data quality recommendations
        if len([r for r in test_results.values() if 'error' in r]) > 0:
            recommendations.append("Bazı testler başarısız oldu. Veri kalitesini kontrol edin.")
        
        return recommendations
