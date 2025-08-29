# Changelog

X13 Seasonal Adjustment kütüphanesinin sürüm geçmişi.

## [0.1.0] - 2024-01-XX

### Added
- İlk sürüm yayını
- X13-ARIMA-SEATS algoritmasının temel implementasyonu
- Otomatik ARIMA model seçimi (AutoARIMA)
- Kapsamlı mevsimsellik tespiti testleri
- X11 seasonal decomposition algoritması
- Henderson trend filtreleri
- Aykırı değer tespiti (AO, LS, TC tipleride)
- M ve Q istatistikleri ile kalite değerlendirmesi
- Türkçe ve İngilizce dokümantasyon
- Comprehensive test suite (%95+ coverage)
- Matplotlib ile görselleştirme araçları
- Örnek kullanım dosyaları

### Features
- **Otomatik Mevsimsellik Tespiti**: 6 farklı istatistiksel test
- **X13-ARIMA-SEATS**: Uluslararası standartlarda implementasyon
- **Esnek API**: Hem basit hem ileri seviye kullanım
- **Yüksek Performans**: NumPy/SciPy tabanlı optimize edilmiş hesaplamalar
- **Kalite Kontrolü**: M1-M11 ve Q istatistikleri
- **Robust Outlier Detection**: AO, LS, TC, SO tiplerine sahip
- **Seasonal Pattern Analysis**: Döngüsel pattern görselleştirmesi
- **Model Diagnostics**: Ljung-Box, Jarque-Bera testleri
- **Cross-validation**: Model seçimi için CV desteği

### Technical Details
- Python 3.8+ desteği
- Pandas 1.3.0+ ile zaman serisi işleme
- Statsmodels entegrasyonu
- Scikit-learn API uyumluluğu
- Type hints desteği
- Comprehensive error handling

### Documentation
- Türkçe README ve dokümantasyon
- API referans dokümantasyonu
- Örnek kullanım senaryoları
- Best practices rehberi
- Installation ve setup kılavuzu

### Testing
- 50+ unit test
- Integration testler
- Performance testler
- Coverage %95+
- Continuous integration hazır

### Known Issues
- Çok kısa zaman serileri (< 24 gözlem) için sınırlı performans
- Extreme outlier'ların tespit edilememesi durumunda uyarı verilmiyor
- Very high frequency data (günlük+) için henüz optimizasyon yapılmamış

### Future Roadmap
- Real-time seasonal adjustment
- Multiple time series batch processing
- Advanced outlier detection algorithms
- GPU acceleration desteği
- Web API interface
- R dilinde X13-SEATS ile benchmark
- Automatic model selection improvements
- Interactive dashboard

### Contributors
- Gardash Abbasov (@Gardash023) - Lead Developer

### Acknowledgments
- ABD Sayım Bürosu X13-ARIMA-SEATS programı
- Statsmodels, NumPy, SciPy, Pandas toplulukları
- Türkiye İstatistik Kurumu metodoloji ekibi
