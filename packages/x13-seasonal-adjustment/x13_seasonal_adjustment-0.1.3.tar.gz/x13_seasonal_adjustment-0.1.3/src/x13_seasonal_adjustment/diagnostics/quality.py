"""
X13 seasonal adjustment kalite diagnostikleri.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass

from ..core.result import SeasonalAdjustmentResult


@dataclass
class QualityReport:
    """
    Kalite değerlendirme raporu.
    
    Attributes:
        overall_quality (str): Genel kalite değerlendirmesi
        m_statistics (Dict): M istatistikleri
        q_statistics (Dict): Q istatistikleri  
        recommendations (List[str]): Öneriler
        warnings (List[str]): Uyarılar
        summary_scores (Dict): Özet skorlar
    """
    overall_quality: str
    m_statistics: Dict[str, float]
    q_statistics: Dict[str, float]
    recommendations: List[str]
    warnings: List[str]
    summary_scores: Dict[str, float]


class QualityDiagnostics:
    """
    X13-ARIMA-SEATS kalite diagnostik sınıfı.
    
    Bu sınıf, X13 seasonal adjustment sonuçlarının kalitesini değerlendirmek
    için M ve Q istatistiklerini hesaplar ve yorumlar.
    """
    
    def __init__(self):
        # M statistics thresholds (X13 default values)
        self.m_thresholds = {
            'M1': 1.0,    # Relative contribution of irregular
            'M2': 1.0,    # Relative contribution of irregular in changes
            'M3': 1.0,    # Amount of month-to-month change in irregular
            'M4': 1.0,    # Autocorrelation in irregular
            'M5': 1.0,    # Number of runs in irregular
            'M6': 1.0,    # Yearly changes in irregular
            'M7': 1.0,    # Amount of month-to-month change in trend-cycle
            'M8': 1.0,    # Changes in year-to-year trends
            'M9': 1.0,    # Linearity and stability of seasonal factors
            'M10': 1.0,   # Year-to-year changes in seasonal factors
            'M11': 1.0,   # Average linear movement in seasonal factors
        }
        
        # Q statistics thresholds
        self.q_thresholds = {
            'Q': 1.0,     # Overall quality measure
            'Q2': 1.0,    # Quality without M2
        }
    
    def evaluate(self, result: SeasonalAdjustmentResult) -> QualityReport:
        """
        Seasonal adjustment sonuçlarını kapsamlı olarak değerlendirir.
        
        Args:
            result: SeasonalAdjustmentResult nesnesi
            
        Returns:
            QualityReport: Detaylı kalite raporu
        """
        
        # M statistics hesapla
        m_stats = self._calculate_m_statistics(result)
        
        # Q statistics hesapla
        q_stats = self._calculate_q_statistics(m_stats)
        
        # Genel kalite değerlendirmesi
        overall_quality = self._assess_overall_quality(q_stats)
        
        # Öneriler ve uyarılar oluştur
        recommendations = self._generate_recommendations(m_stats, q_stats, overall_quality)
        warnings = self._generate_warnings(m_stats, q_stats)
        
        # Summary scores
        summary_scores = self._calculate_summary_scores(m_stats, q_stats)
        
        return QualityReport(
            overall_quality=overall_quality,
            m_statistics=m_stats,
            q_statistics=q_stats,
            recommendations=recommendations,
            warnings=warnings,
            summary_scores=summary_scores
        )
    
    def _calculate_m_statistics(self, result: SeasonalAdjustmentResult) -> Dict[str, float]:
        """M istatistiklerini hesaplar."""
        
        m_stats = {}
        
        original = result.original
        sa = result.seasonally_adjusted
        seasonal = result.seasonal_factors
        trend = result.trend
        irregular = result.irregular
        
        try:
            # M1: Relative contribution of the irregular component to the variance
            m_stats['M1'] = self._calculate_m1(sa, irregular)
            
            # M2: Relative contribution of the irregular component to the variance of changes
            m_stats['M2'] = self._calculate_m2(sa, irregular)
            
            # M3: Amount of month-to-month change in the irregular component
            m_stats['M3'] = self._calculate_m3(irregular)
            
            # M4: Autocorrelation in the irregular component
            m_stats['M4'] = self._calculate_m4(irregular)
            
            # M5: Number of runs in the irregular component
            m_stats['M5'] = self._calculate_m5(irregular)
            
            # M6: Year-to-year changes in the irregular component
            m_stats['M6'] = self._calculate_m6(irregular)
            
            # M7: Amount of month-to-month change in the trend-cycle
            m_stats['M7'] = self._calculate_m7(trend)
            
            # M8: Changes in year-to-year trends
            m_stats['M8'] = self._calculate_m8(trend)
            
            # M9: Linearity and stability of seasonal factors
            m_stats['M9'] = self._calculate_m9(seasonal)
            
            # M10: Year-to-year changes in seasonal factors
            m_stats['M10'] = self._calculate_m10(seasonal)
            
            # M11: Average linear movement in seasonal factors
            m_stats['M11'] = self._calculate_m11(seasonal)
            
        except Exception as e:
            # Eğer hesaplama başarısız olursa default değerler
            for i in range(1, 12):
                if f'M{i}' not in m_stats:
                    m_stats[f'M{i}'] = float('inf')
        
        return m_stats
    
    def _calculate_m1(self, sa: pd.Series, irregular: pd.Series) -> float:
        """M1: Relative contribution of the irregular component to the variance."""
        try:
            var_irregular = np.var(irregular)
            var_sa = np.var(sa)
            
            if var_sa == 0:
                return float('inf')
            
            return var_irregular / var_sa
        except:
            return float('inf')
    
    def _calculate_m2(self, sa: pd.Series, irregular: pd.Series) -> float:
        """M2: Relative contribution of the irregular component to the variance of changes."""
        try:
            sa_diff = sa.diff().dropna()
            irregular_diff = irregular.diff().dropna()
            
            var_irregular_diff = np.var(irregular_diff)
            var_sa_diff = np.var(sa_diff)
            
            if var_sa_diff == 0:
                return float('inf')
            
            return var_irregular_diff / var_sa_diff
        except:
            return float('inf')
    
    def _calculate_m3(self, irregular: pd.Series) -> float:
        """M3: Amount of month-to-month change in the irregular component."""
        try:
            irregular_diff = irregular.diff().dropna()
            
            if len(irregular_diff) == 0:
                return float('inf')
            
            # Average absolute month-to-month change
            avg_change = np.mean(np.abs(irregular_diff))
            std_irregular = np.std(irregular)
            
            if std_irregular == 0:
                return float('inf')
            
            return avg_change / std_irregular
        except:
            return float('inf')
    
    def _calculate_m4(self, irregular: pd.Series) -> float:
        """M4: Autocorrelation in the irregular component."""
        try:
            # First order autocorrelation
            if len(irregular) < 2:
                return float('inf')
            
            autocorr = irregular.autocorr(lag=1)
            
            if pd.isna(autocorr):
                return float('inf')
            
            # Convert to M4 scale (higher is worse)
            return abs(autocorr) * 10  # Scale factor for interpretation
        except:
            return float('inf')
    
    def _calculate_m5(self, irregular: pd.Series) -> float:
        """M5: Number of runs in the irregular component."""
        try:
            # Runs test - consecutive values above/below median
            median_val = irregular.median()
            signs = (irregular > median_val).astype(int)
            
            # Count runs (changes in sign)
            runs = 1
            for i in range(1, len(signs)):
                if signs.iloc[i] != signs.iloc[i-1]:
                    runs += 1
            
            # Expected number of runs under randomness
            n = len(irregular)
            n1 = np.sum(signs)
            n2 = n - n1
            
            if n1 == 0 or n2 == 0:
                return float('inf')
            
            expected_runs = (2 * n1 * n2) / n + 1
            
            if expected_runs == 0:
                return float('inf')
            
            # M5 statistic (deviation from expected)
            return abs(runs - expected_runs) / expected_runs
        except:
            return float('inf')
    
    def _calculate_m6(self, irregular: pd.Series) -> float:
        """M6: Year-to-year changes in the irregular component."""
        try:
            # 12-month difference (for monthly data)
            if len(irregular) < 13:
                return float('inf')
            
            yearly_diff = irregular.diff(12).dropna()
            
            if len(yearly_diff) == 0:
                return float('inf')
            
            # Average absolute yearly change
            avg_yearly_change = np.mean(np.abs(yearly_diff))
            std_irregular = np.std(irregular)
            
            if std_irregular == 0:
                return float('inf')
            
            return avg_yearly_change / std_irregular
        except:
            return float('inf')
    
    def _calculate_m7(self, trend: pd.Series) -> float:
        """M7: Amount of month-to-month change in the trend-cycle."""
        try:
            trend_diff = trend.diff().dropna()
            
            if len(trend_diff) == 0:
                return float('inf')
            
            # Average absolute change in trend
            avg_trend_change = np.mean(np.abs(trend_diff))
            std_trend = np.std(trend)
            
            if std_trend == 0:
                return float('inf')
            
            return avg_trend_change / std_trend
        except:
            return float('inf')
    
    def _calculate_m8(self, trend: pd.Series) -> float:
        """M8: Changes in year-to-year trends."""
        try:
            if len(trend) < 25:  # Need at least 2 years + 1 month
                return float('inf')
            
            # Year-to-year trend changes
            yearly_trend_diff = trend.diff(12).dropna()
            yearly_change_diff = yearly_trend_diff.diff().dropna()
            
            if len(yearly_change_diff) == 0:
                return float('inf')
            
            # Measure of trend stability
            avg_change_in_changes = np.mean(np.abs(yearly_change_diff))
            std_yearly_trend = np.std(yearly_trend_diff)
            
            if std_yearly_trend == 0:
                return float('inf')
            
            return avg_change_in_changes / std_yearly_trend
        except:
            return float('inf')
    
    def _calculate_m9(self, seasonal: pd.Series) -> float:
        """M9: Linearity and stability of seasonal factors."""
        try:
            if len(seasonal) < 24:  # Need at least 2 years
                return float('inf')
            
            # Group by season (month) and check stability over years
            seasonal_by_month = {}
            for i in range(12):  # Assuming monthly data
                month_data = []
                for j in range(i, len(seasonal), 12):
                    month_data.append(seasonal.iloc[j])
                seasonal_by_month[i] = month_data
            
            # Calculate stability measure
            total_variation = 0
            valid_months = 0
            
            for month, values in seasonal_by_month.items():
                if len(values) > 1:
                    month_std = np.std(values)
                    month_mean = np.mean(np.abs(values))
                    if month_mean > 0:
                        total_variation += month_std / month_mean
                        valid_months += 1
            
            if valid_months == 0:
                return float('inf')
            
            return total_variation / valid_months
        except:
            return float('inf')
    
    def _calculate_m10(self, seasonal: pd.Series) -> float:
        """M10: Year-to-year changes in seasonal factors."""
        try:
            if len(seasonal) < 24:
                return float('inf')
            
            # Year-to-year changes in seasonal factors
            yearly_seasonal_diff = seasonal.diff(12).dropna()
            
            if len(yearly_seasonal_diff) == 0:
                return float('inf')
            
            # Average absolute yearly change
            avg_yearly_change = np.mean(np.abs(yearly_seasonal_diff))
            std_seasonal = np.std(seasonal)
            
            if std_seasonal == 0:
                return float('inf')
            
            return avg_yearly_change / std_seasonal
        except:
            return float('inf')
    
    def _calculate_m11(self, seasonal: pd.Series) -> float:
        """M11: Average linear movement in seasonal factors."""
        try:
            if len(seasonal) < 36:  # Need at least 3 years
                return float('inf')
            
            # Group seasonal factors by month and check for linear trend
            total_linear_movement = 0
            valid_months = 0
            
            for month in range(12):  # Monthly data
                month_indices = range(month, len(seasonal), 12)
                month_values = [seasonal.iloc[i] for i in month_indices if i < len(seasonal)]
                
                if len(month_values) >= 3:
                    # Linear regression to detect trend
                    x = np.arange(len(month_values))
                    coeffs = np.polyfit(x, month_values, 1)
                    slope = abs(coeffs[0])
                    
                    # Normalize by standard deviation
                    month_std = np.std(month_values)
                    if month_std > 0:
                        total_linear_movement += slope / month_std
                        valid_months += 1
            
            if valid_months == 0:
                return float('inf')
            
            return total_linear_movement / valid_months
        except:
            return float('inf')
    
    def _calculate_q_statistics(self, m_stats: Dict[str, float]) -> Dict[str, float]:
        """Q istatistiklerini hesaplar."""
        
        q_stats = {}
        
        try:
            # Q: Overall quality measure (average of M statistics)
            valid_m_stats = [v for v in m_stats.values() if not np.isinf(v)]
            
            if valid_m_stats:
                q_stats['Q'] = np.mean(valid_m_stats)
            else:
                q_stats['Q'] = float('inf')
            
            # Q2: Quality without M2 (sometimes M2 can be problematic)
            m_stats_no_m2 = {k: v for k, v in m_stats.items() if k != 'M2'}
            valid_m_stats_no_m2 = [v for v in m_stats_no_m2.values() if not np.isinf(v)]
            
            if valid_m_stats_no_m2:
                q_stats['Q2'] = np.mean(valid_m_stats_no_m2)
            else:
                q_stats['Q2'] = float('inf')
            
        except:
            q_stats['Q'] = float('inf')
            q_stats['Q2'] = float('inf')
        
        return q_stats
    
    def _assess_overall_quality(self, q_stats: Dict[str, float]) -> str:
        """Genel kalite değerlendirmesi yapar."""
        
        q_value = q_stats.get('Q', float('inf'))
        
        if np.isinf(q_value):
            return "Belirlenemedi"
        elif q_value < 0.5:
            return "Mükemmel"
        elif q_value < 1.0:
            return "İyi"
        elif q_value < 2.0:
            return "Orta"
        elif q_value < 3.0:
            return "Zayıf"
        else:
            return "Çok Zayıf"
    
    def _generate_recommendations(
        self, 
        m_stats: Dict[str, float], 
        q_stats: Dict[str, float],
        overall_quality: str
    ) -> List[str]:
        """Öneriler oluşturur."""
        
        recommendations = []
        
        if overall_quality in ["Mükemmel", "İyi"]:
            recommendations.append("Seasonal adjustment kalitesi yeterli. Sonuçlar kullanılabilir.")
        elif overall_quality == "Orta":
            recommendations.append("Seasonal adjustment kalitesi orta düzeyde. Dikkatli kullanım önerilir.")
        else:
            recommendations.append("Seasonal adjustment kalitesi düşük. Model parametrelerini gözden geçirin.")
        
        # Specific M statistic recommendations
        if m_stats.get('M1', 0) > 1.0:
            recommendations.append("M1 yüksek: Irregular component çok büyük. Outlier tespiti yapın.")
        
        if m_stats.get('M7', 0) > 1.0:
            recommendations.append("M7 yüksek: Trend çok volatile. Henderson filter uzunluğunu artırın.")
        
        if m_stats.get('M9', 0) > 1.0:
            recommendations.append("M9 yüksek: Seasonal factors instabil. Seasonal MA filter'ı ayarlayın.")
        
        if m_stats.get('M4', 0) > 1.0:
            recommendations.append("M4 yüksek: Irregular component'te autocorrelation var. ARIMA modelini kontrol edin.")
        
        return recommendations
    
    def _generate_warnings(
        self, 
        m_stats: Dict[str, float], 
        q_stats: Dict[str, float]
    ) -> List[str]:
        """Uyarılar oluşturur."""
        
        warnings = []
        
        # Check for extreme values
        for stat_name, value in m_stats.items():
            if np.isinf(value):
                warnings.append(f"{stat_name} hesaplanamadı. Veri yetersizliği olabilir.")
            elif value > 5.0:
                warnings.append(f"{stat_name} çok yüksek ({value:.2f}). Kalite sorunu var.")
        
        if q_stats.get('Q', 0) > 3.0:
            warnings.append("Q istatistiği çok yüksek. Seasonal adjustment başarısız olabilir.")
        
        # Check for specific problematic patterns
        if (m_stats.get('M1', 0) > 2.0 and m_stats.get('M3', 0) > 2.0):
            warnings.append("Irregular component hem büyük hem instabil. Model uygun değil.")
        
        return warnings
    
    def _calculate_summary_scores(
        self, 
        m_stats: Dict[str, float], 
        q_stats: Dict[str, float]
    ) -> Dict[str, float]:
        """Özet skorları hesaplar."""
        
        summary = {}
        
        # Overall quality score (0-100 scale)
        q_value = q_stats.get('Q', float('inf'))
        if not np.isinf(q_value):
            # Convert Q statistic to 0-100 score (lower Q is better)
            summary['quality_score'] = max(0, 100 - (q_value * 20))
        else:
            summary['quality_score'] = 0
        
        # Stability score (based on M7, M9, M10)
        stability_stats = [m_stats.get('M7', float('inf')), 
                          m_stats.get('M9', float('inf')), 
                          m_stats.get('M10', float('inf'))]
        valid_stability = [s for s in stability_stats if not np.isinf(s)]
        
        if valid_stability:
            avg_stability = np.mean(valid_stability)
            summary['stability_score'] = max(0, 100 - (avg_stability * 25))
        else:
            summary['stability_score'] = 0
        
        # Irregular component quality (based on M1, M3, M4)
        irregular_stats = [m_stats.get('M1', float('inf')),
                          m_stats.get('M3', float('inf')),
                          m_stats.get('M4', float('inf'))]
        valid_irregular = [s for s in irregular_stats if not np.isinf(s)]
        
        if valid_irregular:
            avg_irregular = np.mean(valid_irregular)
            summary['irregular_quality_score'] = max(0, 100 - (avg_irregular * 30))
        else:
            summary['irregular_quality_score'] = 0
        
        return summary
