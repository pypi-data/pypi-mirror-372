"""
Seasonal adjustment result data structures.
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class SeasonalAdjustmentResult:
    """
    X13 mevsimsellikten arındırma sonuçlarını içeren veri yapısı.
    
    Bu sınıf, X13-ARIMA-SEATS algoritmasının çıktılarını organize bir şekilde tutar
    ve sonuçların analizi için yardımcı metodlar sağlar.
    
    Attributes:
        original (pd.Series): Orijinal zaman serisi
        seasonally_adjusted (pd.Series): Mevsimsellikten arındırılmış seri
        seasonal_factors (pd.Series): Mevsimsel faktörler
        trend (pd.Series): Trend bileşeni
        irregular (pd.Series): Düzensiz bileşen
        seasonality_strength (float): Mevsimsellik gücü (0-1 arası)
        trend_strength (float): Trend gücü (0-1 arası)
        trading_day_factors (Optional[pd.Series]): İş günü faktörleri
        easter_factors (Optional[pd.Series]): Paskalya faktörleri
        outliers (Optional[pd.DataFrame]): Tespit edilen aykırı değerler
        arima_model_info (Optional[Dict]): ARIMA model bilgileri
        quality_measures (Optional[Dict]): Kalite ölçütleri (M ve Q istatistikleri)
    """
    
    original: pd.Series
    seasonally_adjusted: pd.Series
    seasonal_factors: pd.Series
    trend: pd.Series
    irregular: pd.Series
    seasonality_strength: float
    trend_strength: float
    trading_day_factors: Optional[pd.Series] = None
    easter_factors: Optional[pd.Series] = None
    outliers: Optional[pd.DataFrame] = None
    arima_model_info: Optional[Dict[str, Any]] = None
    quality_measures: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Sonuç nesnesinin başlatılması sonrası doğrulama ve hesaplamalar."""
        self._validate_data()
        self._calculate_additional_measures()
    
    def _validate_data(self) -> None:
        """Veri tutarlılığını kontrol eder."""
        series_list = [self.original, self.seasonally_adjusted, 
                      self.seasonal_factors, self.trend, self.irregular]
        
        # Tüm serilerin aynı uzunlukta olduğunu kontrol et
        lengths = [len(series) for series in series_list]
        if not all(length == lengths[0] for length in lengths):
            raise ValueError("Tüm zaman serileri aynı uzunlukta olmalıdır")
        
        # Index uyumluluğunu kontrol et
        for series in series_list[1:]:
            if not self.original.index.equals(series.index):
                raise ValueError("Tüm zaman serilerinin index'i aynı olmalıdır")
    
    def _calculate_additional_measures(self) -> None:
        """Ek ölçütleri hesaplar."""
        # Mevsimsellik variasyonu
        seasonal_var = np.var(self.seasonal_factors)
        total_var = np.var(self.original)
        
        if total_var > 0:
            self._seasonal_variation_ratio = seasonal_var / total_var
        else:
            self._seasonal_variation_ratio = 0.0
    
    @property
    def seasonal_variation_ratio(self) -> float:
        """Mevsimsel varyasyon oranı."""
        return self._seasonal_variation_ratio
    
    @property
    def decomposition_quality(self) -> str:
        """Dekompozisyon kalitesini kategorik olarak döndürür."""
        if self.quality_measures is None:
            return "Belirsiz"
        
        # M7 istatistiği (mevsimsel stabilite)
        m7 = self.quality_measures.get('M7', float('inf'))
        
        if m7 < 1.0:
            return "Mükemmel"
        elif m7 < 2.0:
            return "İyi"
        elif m7 < 3.0:
            return "Orta"
        else:
            return "Zayıf"
    
    def summary(self) -> pd.DataFrame:
        """
        Sonuçların özetini DataFrame formatında döndürür.
        
        Returns:
            pd.DataFrame: Özet istatistikler
        """
        summary_data = {
            'Metric': [
                'Orijinal Seri Ortalaması',
                'SA Seri Ortalaması', 
                'Mevsimsellik Gücü',
                'Trend Gücü',
                'Mevsimsel Varyasyon Oranı',
                'Dekompozisyon Kalitesi'
            ],
            'Value': [
                f"{self.original.mean():.2f}",
                f"{self.seasonally_adjusted.mean():.2f}",
                f"{self.seasonality_strength:.3f}",
                f"{self.trend_strength:.3f}",
                f"{self.seasonal_variation_ratio:.3f}",
                self.decomposition_quality
            ]
        }
        
        if self.quality_measures:
            for key, value in self.quality_measures.items():
                summary_data['Metric'].append(f'Kalite Ölçütü {key}')
                summary_data['Value'].append(f"{value:.3f}")
        
        return pd.DataFrame(summary_data)
    
    def plot(self, figsize: tuple = (12, 10), save_path: Optional[str] = None) -> None:
        """
        Sonuçları görselleştirir.
        
        Args:
            figsize (tuple): Grafik boyutu
            save_path (Optional[str]): Grafiği kaydetmek için dosya yolu
        """
        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        
        # Orijinal ve SA seriler
        axes[0].plot(self.original.index, self.original, 
                    label='Orijinal', color='blue', alpha=0.7)
        axes[0].plot(self.seasonally_adjusted.index, self.seasonally_adjusted,
                    label='Mevsimsellikten Arındırılmış', color='red', alpha=0.7)
        axes[0].set_title('Orijinal ve Mevsimsellikten Arındırılmış Seriler')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Trend
        axes[1].plot(self.trend.index, self.trend, 
                    label='Trend', color='green', linewidth=2)
        axes[1].set_title('Trend Bileşeni')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Mevsimsel faktörler
        axes[2].plot(self.seasonal_factors.index, self.seasonal_factors,
                    label='Mevsimsel Faktörler', color='orange')
        axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[2].set_title('Mevsimsel Faktörler')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Düzensiz bileşen
        axes[3].plot(self.irregular.index, self.irregular,
                    label='Düzensiz Bileşen', color='purple', alpha=0.6)
        axes[3].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[3].set_title('Düzensiz Bileşen')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_seasonal_pattern(self, figsize: tuple = (10, 6)) -> None:
        """
        Mevsimsel pattern'i döngüsel olarak görselleştirir.
        
        Args:
            figsize (tuple): Grafik boyutu
        """
        # Frekansa göre dönem uzunluğunu belirle
        if hasattr(self.original.index, 'freq'):
            if self.original.index.freq == 'M':
                period = 12
                labels = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
                         'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
            elif self.original.index.freq == 'Q':
                period = 4
                labels = ['Q1', 'Q2', 'Q3', 'Q4']
            else:
                period = 12  # Default
                labels = [f'P{i+1}' for i in range(period)]
        else:
            period = 12  # Default
            labels = [f'P{i+1}' for i in range(period)]
        
        # Mevsimsel faktörleri period'a göre grupla
        seasonal_by_period = []
        for i in range(period):
            mask = np.arange(len(self.seasonal_factors)) % period == i
            seasonal_by_period.append(self.seasonal_factors.iloc[mask].mean())
        
        plt.figure(figsize=figsize)
        plt.plot(range(period), seasonal_by_period, 'o-', linewidth=2, markersize=8)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.xlabel('Dönem')
        plt.ylabel('Ortalama Mevsimsel Faktör')
        plt.title('Mevsimsel Pattern')
        plt.xticks(range(period), labels)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Sonuçları dictionary formatında döndürür.
        
        Returns:
            Dict[str, Any]: Tüm sonuçları içeren dictionary
        """
        result_dict = {
            'original': self.original.to_dict(),
            'seasonally_adjusted': self.seasonally_adjusted.to_dict(),
            'seasonal_factors': self.seasonal_factors.to_dict(),
            'trend': self.trend.to_dict(),
            'irregular': self.irregular.to_dict(),
            'seasonality_strength': self.seasonality_strength,
            'trend_strength': self.trend_strength,
            'seasonal_variation_ratio': self.seasonal_variation_ratio,
            'decomposition_quality': self.decomposition_quality,
        }
        
        if self.trading_day_factors is not None:
            result_dict['trading_day_factors'] = self.trading_day_factors.to_dict()
        
        if self.easter_factors is not None:
            result_dict['easter_factors'] = self.easter_factors.to_dict()
        
        if self.outliers is not None:
            result_dict['outliers'] = self.outliers.to_dict()
        
        if self.arima_model_info is not None:
            result_dict['arima_model_info'] = self.arima_model_info
        
        if self.quality_measures is not None:
            result_dict['quality_measures'] = self.quality_measures
        
        return result_dict
    
    def save(self, filepath: str) -> None:
        """
        Sonuçları pickle formatında kaydeder.
        
        Args:
            filepath (str): Kayıt dosyası yolu
        """
        import pickle
        
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'SeasonalAdjustmentResult':
        """
        Pickle dosyasından sonuçları yükler.
        
        Args:
            filepath (str): Dosya yolu
            
        Returns:
            SeasonalAdjustmentResult: Yüklenmiş sonuç nesnesi
        """
        import pickle
        
        with open(filepath, 'rb') as f:
            return pickle.load(f)
