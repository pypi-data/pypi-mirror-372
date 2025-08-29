"""
X13 Seasonal Adjustment - Temel Kullanım Örneği

Bu dosya, X13 seasonal adjustment kütüphanesinin temel kullanımını gösterir.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# X13 kütüphanesini import et
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from x13_seasonal_adjustment import X13SeasonalAdjustment, SeasonalityTests


def create_sample_data(n_years: int = 5) -> pd.Series:
    """
    Örnek mevsimsel zaman serisi oluşturur.
    
    Args:
        n_years: Yıl sayısı
        
    Returns:
        pd.Series: Sentetik zaman serisi
    """
    # Tarih aralığı oluştur
    dates = pd.date_range(start='2020-01-01', periods=n_years*12, freq='M')
    
    # Trend bileşeni (yavaş artış)
    trend = 100 + np.linspace(0, 50, len(dates))
    
    # Mevsimsel bileşen (12 aylık dönem)
    seasonal_pattern = [10, 8, 5, -2, -8, -12, -15, -12, -5, 0, 5, 8]
    seasonal = np.tile(seasonal_pattern, n_years)
    
    # Düzensiz bileşen (rastgele gürültü)
    np.random.seed(42)
    irregular = np.random.normal(0, 3, len(dates))
    
    # Bazı aykırı değerler ekle
    irregular[15] += 25  # Büyük pozitif şok
    irregular[30] -= 20  # Büyük negatif şok
    irregular[45] += 15  # Orta büyüklükte şok
    
    # Toplam seri (additive model)
    total = trend + seasonal + irregular
    
    return pd.Series(total, index=dates, name='sample_data')


def basic_seasonal_adjustment_example():
    """Temel mevsimsellikten arındırma örneği."""
    
    print("=== Temel X13 Seasonal Adjustment Örneği ===\n")
    
    # 1. Örnek veri oluştur
    print("1. Örnek veri oluşturuluyor...")
    data = create_sample_data(n_years=5)
    print(f"   Veri uzunluğu: {len(data)} gözlem")
    print(f"   Tarih aralığı: {data.index[0].strftime('%Y-%m')} - {data.index[-1].strftime('%Y-%m')}")
    print(f"   Ortalama: {data.mean():.2f}")
    print(f"   Standart sapma: {data.std():.2f}\n")
    
    # 2. Mevsimsellik testleri
    print("2. Mevsimsellik testleri yapılıyor...")
    seasonality_tester = SeasonalityTests(seasonal_period=12)
    seasonality_result = seasonality_tester.run_all_tests(data)
    
    print(f"   Mevsimsellik var mı? {seasonality_result.has_seasonality}")
    print(f"   Güven düzeyi: {seasonality_result.confidence_level:.3f}")
    print(f"   Öneriler: {len(seasonality_result.recommendations)} adet\n")
    
    # 3. X13 seasonal adjustment
    print("3. X13 seasonal adjustment yapılıyor...")
    
    # X13 modeli oluştur
    x13 = X13SeasonalAdjustment(
        freq='M',                    # Aylık veri
        transform='auto',            # Otomatik dönüşüm
        outlier_detection=True,      # Aykırı değer tespiti
        trading_day=False,           # İş günü etkisi (basit örnek için kapalı)
        easter=False,                # Paskalya etkisi (basit örnek için kapalı)
        arima_order='auto'           # Otomatik ARIMA seçimi
    )
    
    # Model fit et ve seasonal adjustment yap
    result = x13.fit_transform(data)
    
    print("   ✓ Seasonal adjustment tamamlandı")
    print(f"   Mevsimsellik gücü: {result.seasonality_strength:.3f}")
    print(f"   Trend gücü: {result.trend_strength:.3f}")
    print(f"   Dekompozisyon kalitesi: {result.decomposition_quality}\n")
    
    # 4. Sonuçları analiz et
    print("4. Sonuç analizi:")
    
    # Temel istatistikler
    original_std = result.original.std()
    sa_std = result.seasonally_adjusted.std()
    volatility_reduction = (original_std - sa_std) / original_std * 100
    
    print(f"   Orijinal seri std sapma: {original_std:.3f}")
    print(f"   SA seri std sapma: {sa_std:.3f}")
    print(f"   Volatilite azalması: {volatility_reduction:.1f}%")
    
    # Mevsimsel faktörlerin stabilitesi
    seasonal_std = result.seasonal_factors.std()
    print(f"   Mevsimsel faktör std sapma: {seasonal_std:.3f}")
    
    # 5. Sonuçları görselleştir
    print("\n5. Sonuçlar görselleştiriliyor...")
    
    # Ana grafik
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Orijinal vs SA
    axes[0].plot(result.original.index, result.original, 
                label='Orijinal', alpha=0.7, linewidth=1)
    axes[0].plot(result.seasonally_adjusted.index, result.seasonally_adjusted,
                label='Mevsimsellikten Arındırılmış', linewidth=1.5)
    axes[0].plot(result.trend.index, result.trend,
                label='Trend', linestyle='--', alpha=0.8)
    axes[0].set_title('X13 Seasonal Adjustment Sonuçları')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Mevsimsel faktörler
    axes[1].plot(result.seasonal_factors.index, result.seasonal_factors,
                color='orange', linewidth=1)
    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1].set_title('Mevsimsel Faktörler')
    axes[1].grid(True, alpha=0.3)
    
    # Düzensiz bileşen
    axes[2].plot(result.irregular.index, result.irregular,
                color='red', alpha=0.6, linewidth=1)
    axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[2].set_title('Düzensiz Bileşen')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Mevsimsel pattern grafiği
    result.plot_seasonal_pattern()
    
    # 6. Özet rapor
    print("\n6. Özet Rapor:")
    summary_df = result.summary()
    print(summary_df.to_string(index=False))
    
    return result


def advanced_seasonal_adjustment_example():
    """Gelişmiş mevsimsellikten arındırma örneği."""
    
    print("\n\n=== Gelişmiş X13 Seasonal Adjustment Örneği ===\n")
    
    # Daha karmaşık veri oluştur
    dates = pd.date_range(start='2015-01-01', periods=8*12, freq='M')
    
    # Nonlinear trend
    t = np.arange(len(dates))
    trend = 100 + 0.5 * t + 0.001 * t**2
    
    # Variable seasonal pattern
    seasonal_base = [15, 12, 8, 2, -5, -10, -15, -12, -8, -2, 5, 10]
    seasonal = []
    for year in range(8):
        # Seasonal pattern gradually changes
        factor = 1 + 0.1 * year
        year_seasonal = [x * factor for x in seasonal_base]
        seasonal.extend(year_seasonal)
    
    # Level shift (structural break)
    level_shift = np.zeros(len(dates))
    level_shift[48:] = 20  # Level shift after 4 years
    
    # Irregular with outliers
    np.random.seed(123)
    irregular = np.random.normal(0, 4, len(dates))
    
    # Add specific outliers
    irregular[20] += 30   # Additive outlier
    irregular[55] -= 25   # Another outlier
    
    # Total series
    total = trend + np.array(seasonal) + level_shift + irregular
    complex_data = pd.Series(total, index=dates, name='complex_data')
    
    print(f"Karmaşık veri oluşturuldu: {len(complex_data)} gözlem")
    
    # Advanced X13 configuration
    x13_advanced = X13SeasonalAdjustment(
        freq='M',
        transform='auto',
        outlier_detection=True,
        outlier_types=['AO', 'LS', 'TC'],  # All outlier types
        trading_day=False,
        easter=False,
        arima_order='auto',
        x11_mode='auto',
        forecast_maxlead=24,      # 2 year forecast extension
        backcast_maxlead=12       # 1 year backcast extension
    )
    
    # Fit and transform
    advanced_result = x13_advanced.fit_transform(complex_data)
    
    print(f"Gelişmiş seasonal adjustment tamamlandı")
    print(f"Tespit edilen aykırı değer sayısı: {len(advanced_result.outliers) if advanced_result.outliers is not None else 0}")
    
    # Model bilgileri
    model_summary = x13_advanced.get_model_summary()
    print(f"ARIMA modeli: {model_summary['arima_model']['order']} x {model_summary['arima_model']['seasonal_order']}")
    print(f"AIC: {model_summary['arima_model']['aic']:.3f}")
    
    # Advanced visualization
    advanced_result.plot(figsize=(14, 12))
    
    return advanced_result


def quality_diagnostics_example(result):
    """Kalite diagnostik örneği."""
    
    print("\n\n=== Kalite Diagnostikleri ===\n")
    
    from x13_seasonal_adjustment import QualityDiagnostics
    
    # Quality diagnostics çalıştır
    quality_diagnostics = QualityDiagnostics()
    quality_report = quality_diagnostics.evaluate(result)
    
    print(f"Genel kalite: {quality_report.overall_quality}")
    print(f"Kalite skoru: {quality_report.summary_scores['quality_score']:.1f}/100")
    print(f"Stabilite skoru: {quality_report.summary_scores['stability_score']:.1f}/100")
    
    # M statistics
    print("\nM İstatistikleri:")
    for stat_name, value in quality_report.m_statistics.items():
        if not np.isinf(value):
            print(f"  {stat_name}: {value:.3f}")
    
    # Q statistics  
    print("\nQ İstatistikleri:")
    for stat_name, value in quality_report.q_statistics.items():
        if not np.isinf(value):
            print(f"  {stat_name}: {value:.3f}")
    
    # Öneriler
    print("\nÖneriler:")
    for rec in quality_report.recommendations:
        print(f"  • {rec}")
    
    # Uyarılar
    if quality_report.warnings:
        print("\nUyarılar:")
        for warning in quality_report.warnings:
            print(f"  ⚠ {warning}")
    
    return quality_report


def main():
    """Ana fonksiyon - tüm örnekleri çalıştırır."""
    
    try:
        # Temel örnek
        result1 = basic_seasonal_adjustment_example()
        
        # Gelişmiş örnek
        result2 = advanced_seasonal_adjustment_example()
        
        # Kalite diagnostikleri
        quality_report = quality_diagnostics_example(result1)
        
        print("\n=== TÜM ÖRNEKLER BAŞARIYLA TAMAMLANDI ===")
        
        return {
            'basic_result': result1,
            'advanced_result': result2,
            'quality_report': quality_report
        }
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
