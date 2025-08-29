# X13 Seasonal Adjustment

[![PyPI version](https://badge.fury.io/py/x13-seasonal-adjustment.svg)](https://badge.fury.io/py/x13-seasonal-adjustment)
[![Python Version](https://img.shields.io/pypi/pyversions/x13-seasonal-adjustment.svg)](https://pypi.org/project/x13-seasonal-adjustment/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/x13-seasonal-adjustment/badge/?version=latest)](https://x13-seasonal-adjustment.readthedocs.io/en/latest/?badge=latest)

A comprehensive Python implementation of the X13-ARIMA-SEATS seasonal adjustment algorithm. This library provides robust tools for detecting and removing seasonal effects from time series data.

## Features

- **Automatic Seasonality Detection**: Advanced statistical tests for seasonality identification
- **X13-ARIMA-SEATS Algorithm**: International standard seasonal adjustment methodology
- **High Performance**: Optimized computations using NumPy and SciPy
- **Visualization**: Comprehensive plotting capabilities with matplotlib
- **Flexible API**: Suitable for both simple and advanced use cases
- **Comprehensive Documentation**: Detailed documentation and examples
- **Full Test Coverage**: Reliable code with 95%+ test coverage

## Kurulum

```bash
pip install x13-seasonal-adjustment
```

Geliştirme versiyonu için:

```bash
pip install x13-seasonal-adjustment[dev]
```

## Hızlı Başlangıç

```python
import pandas as pd
from x13_seasonal_adjustment import X13SeasonalAdjustment

# Veri yükle
data = pd.read_csv('your_time_series.csv', index_col=0, parse_dates=True)

# X13 modeli oluştur
x13 = X13SeasonalAdjustment()

# Mevsimsellikten arındırma
result = x13.fit_transform(data['value'])

# Sonuçları görüntüle
print("Orijinal Seri:", result.original)
print("Mevsimsellikten Arındırılmış Seri:", result.seasonally_adjusted)
print("Mevsimsel Faktörler:", result.seasonal_factors)
print("Trend:", result.trend)

# Grafik çizimi
result.plot()
```

## Ana Bileşenler

### 1. X13SeasonalAdjustment (Ana Sınıf)
```python
from x13_seasonal_adjustment import X13SeasonalAdjustment

x13 = X13SeasonalAdjustment(
    freq='M',           # Veri frekansı (M=Aylık, Q=Çeyreklik)
    transform='auto',   # Logaritmik dönüşüm ('auto', 'log', 'none')
    outlier_detection=True,  # Aykırı değer tespiti
    trading_day=True,   # İş günü etkisi
    easter=True,        # Paskalya etkisi
    arima_order='auto'  # ARIMA model sırası
)
```

### 2. Mevsimsellik Testleri
```python
from x13_seasonal_adjustment.tests import SeasonalityTests

tests = SeasonalityTests()
result = tests.run_all_tests(data)
print(f"Mevsimsellik var mı? {result.has_seasonality}")
```

### 3. ARIMA Modelleme
```python
from x13_seasonal_adjustment.arima import AutoARIMA

arima = AutoARIMA()
model = arima.fit(data)
forecast = model.forecast(steps=12)
```

## Metodoloji

Bu kütüphane, ABD Sayım Bürosu'nun X13-ARIMA-SEATS programının metodolojisini takip eder:

1. **Ön İşleme**: Eksik değer doldurma, aykırı değer tespiti
2. **Model Seçimi**: Otomatik ARIMA model seçimi
3. **Mevsimsel Dekompozisyon**: X11 algoritması ile dekompozisyon
4. **Kalite Kontrolü**: M ve Q istatistikleri ile kalite değerlendirmesi

## Örnekler

### Temel Kullanım
```python
import numpy as np
import pandas as pd
from x13_seasonal_adjustment import X13SeasonalAdjustment

# Örnek veri oluştur
dates = pd.date_range('2020-01-01', periods=60, freq='M')
trend = np.linspace(100, 200, 60)
seasonal = 10 * np.sin(2 * np.pi * np.arange(60) / 12)
noise = np.random.normal(0, 5, 60)
data = pd.Series(trend + seasonal + noise, index=dates)

# Mevsimsellikten arındır
x13 = X13SeasonalAdjustment()
result = x13.fit_transform(data)

# Sonuçları analiz et
print(f"Mevsimsellik derecesi: {result.seasonality_strength:.3f}")
print(f"Trend gücü: {result.trend_strength:.3f}")
```

### İleri Seviye Kullanım
```python
from x13_seasonal_adjustment import X13SeasonalAdjustment
from x13_seasonal_adjustment.diagnostics import QualityDiagnostics

# Özelleştirilmiş model
x13 = X13SeasonalAdjustment(
    transform='log',
    outlier_detection=True,
    outlier_types=['AO', 'LS', 'TC'],  # Aykırı değer tipleri
    arima_order=(0, 1, 1),             # Manuel ARIMA sırası
    seasonal_arima_order=(0, 1, 1),    # Mevsimsel ARIMA sırası
)

result = x13.fit_transform(data)

# Kalite diagnostikleri
diagnostics = QualityDiagnostics()
quality_report = diagnostics.evaluate(result)
print(quality_report)
```

## API Referansı

### X13SeasonalAdjustment

**Parametreler:**
- `freq` (str): Veri frekansı ('M', 'Q', 'A')
- `transform` (str): Dönüşüm tipi ('auto', 'log', 'none')
- `outlier_detection` (bool): Aykırı değer tespiti aktif mi?
- `trading_day` (bool): İş günü etkisi modellenir mi?
- `easter` (bool): Paskalya etkisi modellenir mi?
- `arima_order` (tuple veya 'auto'): ARIMA model sırası

**Metodlar:**
- `fit(X)`: Modeli eğit
- `transform(X)`: Mevsimsellikten arındır
- `fit_transform(X)`: Eğit ve dönüştür
- `plot_decomposition()`: Dekompozisyon grafiğini çiz

### SeasonalAdjustmentResult

**Özellikler:**
- `original`: Orijinal seri
- `seasonally_adjusted`: Mevsimsellikten arındırılmış seri
- `seasonal_factors`: Mevsimsel faktörler
- `trend`: Trend bileşeni
- `irregular`: Düzensiz bileşen
- `seasonality_strength`: Mevsimsellik gücü (0-1)
- `trend_strength`: Trend gücü (0-1)

## Katkıda Bulunma

Bu projeye katkıda bulunmak istiyorsanız:

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Geliştirme Ortamı

```bash
# Repository'yi klonlayın
git clone https://github.com/gardashabbasov/x13-seasonal-adjustment.git
cd x13-seasonal-adjustment

# Geliştirme bağımlılıklarını yükleyin
pip install -e .[dev]

# Testleri çalıştırın
pytest

# Code style kontrolü
black src/ tests/
flake8 src/ tests/

# Type checking
mypy src/
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Contact

- **Developer**: Gardash Abbasov
- **Email**: gardash.abbasov@gmail.com
- **GitHub**: [@Gardash023](https://github.com/Gardash023)

## Teşekkürler

- ABD Sayım Bürosu'nun X13-ARIMA-SEATS programına
- Statsmodels, NumPy, SciPy, Pandas topluluklarına
- Türk ekonometri ve istatistik topluluğuna

## Changelog

### v0.1.0 (2024-01-XX)
- İlk release
- Temel X13-ARIMA-SEATS implementasyonu
- Otomatik mevsimsellik tespiti
- Kapsamlı test suite'i
- Türkçe dokümantasyon
