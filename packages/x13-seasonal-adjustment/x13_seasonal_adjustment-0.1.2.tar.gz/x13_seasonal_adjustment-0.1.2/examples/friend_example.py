"""
X13 Seasonal Adjustment - Arkadaş için Basit Örnek

Bu dosyayı arkadaşına gönderebilirsin. Kendi bilgisayarında çalıştırabilir.
Yazar: Gardash Abbasov
Paket: x13-seasonal-adjustment
"""

# ============================================================================
# KURULUM TALİMATLARI
# ============================================================================
"""
ADIM 1: Terminal/Command Prompt'u açın
ADIM 2: Şu komutu çalıştırın:

pip install x13-seasonal-adjustment

ADIM 3: Bu dosyayı çalıştırın:

python friend_example.py

İşte bu kadar! 😊
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("X13 Seasonal Adjustment Paketi Test Ediliyor...")
print("Paket: x13-seasonal-adjustment")
print("Geliştirici: Gardash Abbasov")
print("=" * 50)

try:
    # X13 paketini import et
    from x13_seasonal_adjustment import X13SeasonalAdjustment, SeasonalityTests
    print("✅ Paket başarıyla yüklendi!")
    
except ImportError:
    print("❌ Hata: Paket yüklü değil!")
    print("Lütfen şu komutu çalıştırın: pip install x13-seasonal-adjustment")
    exit()

# ============================================================================
# ÖRNEKLİ KULLANIM
# ============================================================================

def ornek_veri_olustur():
    """Örnek zaman serisi verisi oluştur"""
    print("\n📊 Örnek veri oluşturuluyor...")
    
    # 4 yıl aylık veri
    tarihler = pd.date_range('2020-01-01', '2023-12-01', freq='M')
    
    # Gerçekçi satış verisi simülasyonu
    np.random.seed(42)
    
    # Yavaş yavaş artan trend
    trend = 1000 + 30 * np.arange(len(tarihler))
    
    # Güçlü mevsimsel pattern (yaz yüksek, kış düşük)
    mevsimsel = 200 * np.sin(2 * np.pi * np.arange(len(tarihler)) / 12)
    
    # Rastgele gürültü
    gurultu = np.random.normal(0, 50, len(tarihler))
    
    # Toplam satış verisi
    satis_verisi = trend + mevsimsel + gurultu
    
    # Pandas Series oluştur
    satis = pd.Series(satis_verisi, index=tarihler, name='Aylık_Satışlar')
    
    print(f"✅ {len(satis)} aylık veri oluşturuldu")
    print(f"📅 Dönem: {satis.index[0].strftime('%Y-%m')} - {satis.index[-1].strftime('%Y-%m')}")
    print(f"💰 Ortalama satış: {satis.mean():,.0f} TL")
    
    return satis


def mevsimsellik_testi(veri):
    """Mevsimsellik testi yap"""
    print("\n🔍 Mevsimsellik testi yapılıyor...")
    
    test = SeasonalityTests(seasonal_period=12)
    sonuc = test.run_all_tests(veri)
    
    print(f"📈 Mevsimsellik var mı? {sonuc.has_seasonality}")
    print(f"📊 Güven seviyesi: {sonuc.confidence_level:.1%}")
    
    if sonuc.has_seasonality:
        print("✅ Veri mevsimsel! X13 uygulanabilir.")
    else:
        print("⚠️ Zayıf mevsimsellik. X13 yine de denenebilir.")
    
    return sonuc


def x13_uygula(veri):
    """X13 seasonal adjustment uygula"""
    print("\n🔧 X13 Seasonal Adjustment uygulanıyor...")
    
    # X13 modeli oluştur
    x13 = X13SeasonalAdjustment()  # Frekansı otomatik tespit et
    
    # Modeli fit et ve dönüştür
    sonuc = x13.fit_transform(veri)
    
    print("✅ X13 tamamlandı!")
    print(f"📊 Mevsimsellik gücü: {sonuc.seasonality_strength:.1%}")
    print(f"📈 Trend gücü: {sonuc.trend_strength:.1%}")
    print(f"⭐ Kalite: {sonuc.decomposition_quality}")
    
    return sonuc


def sonuclari_analiz_et(sonuc):
    """Sonuçları analiz et ve yazdır"""
    print("\n📋 SONUÇ ANALİZİ:")
    print("=" * 30)
    
    # Temel istatistikler
    orijinal = sonuc.original
    mevsimsel_arindirilmis = sonuc.seasonally_adjusted
    
    orijinal_std = orijinal.std()
    sa_std = mevsimsel_arindirilmis.std()
    volatilite_azalma = (orijinal_std - sa_std) / orijinal_std * 100
    
    print(f"📊 Orijinal veri volatilitesi: {orijinal_std:,.0f}")
    print(f"📊 Seasonal adjusted volatilite: {sa_std:,.0f}")
    print(f"📉 Volatilite azalması: {volatilite_azalma:.1f}%")
    
    # Aylık mevsimsel faktörler
    print(f"\n📅 AYLIK MEVSİMSEL FAKTÖRLER:")
    aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
             'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    
    for ay_no in range(1, 13):
        ay_mask = sonuc.seasonal_factors.index.month == ay_no
        if ay_mask.any():
            ortalama_faktor = sonuc.seasonal_factors[ay_mask].mean()
            ay_adi = aylar[ay_no - 1]
            yon = "📈 yüksek" if ortalama_faktor > 0 else "📉 düşük"
            print(f"{ay_adi:8}: {ortalama_faktor:+7.0f} TL ({yon})")


def grafik_ciz(sonuc):
    """Sonuçların grafiğini çiz"""
    print("\n🎨 Grafik oluşturuluyor...")
    
    fig, eksenler = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('X13 Seasonal Adjustment Sonuçları', fontsize=16, fontweight='bold')
    
    # 1. Orijinal vs Mevsimsel Arındırılmış
    eksenler[0, 0].plot(sonuc.original.index, sonuc.original, 
                       label='Orijinal Veri', alpha=0.7, linewidth=1)
    eksenler[0, 0].plot(sonuc.seasonally_adjusted.index, sonuc.seasonally_adjusted, 
                       label='Mevsimsel Arındırılmış', linewidth=2, color='red')
    eksenler[0, 0].set_title('Orijinal vs Mevsimsel Arındırılmış')
    eksenler[0, 0].set_ylabel('Satış (TL)')
    eksenler[0, 0].legend()
    eksenler[0, 0].grid(True, alpha=0.3)
    
    # 2. Trend Bileşeni
    eksenler[0, 1].plot(sonuc.trend.index, sonuc.trend, color='green', linewidth=2)
    eksenler[0, 1].set_title('Trend Bileşeni')
    eksenler[0, 1].set_ylabel('Satış (TL)')
    eksenler[0, 1].grid(True, alpha=0.3)
    
    # 3. Mevsimsel Faktörler
    eksenler[1, 0].plot(sonuc.seasonal_factors.index, sonuc.seasonal_factors, 
                       color='orange', linewidth=1)
    eksenler[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    eksenler[1, 0].set_title('Mevsimsel Faktörler')
    eksenler[1, 0].set_ylabel('Mevsimsel Etki (TL)')
    eksenler[1, 0].grid(True, alpha=0.3)
    
    # 4. Aylık Ortalama Mevsimsel Pattern
    aylar = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
             'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
    
    aylik_faktorler = []
    for ay_no in range(1, 13):
        ay_mask = sonuc.seasonal_factors.index.month == ay_no
        if ay_mask.any():
            aylik_faktorler.append(sonuc.seasonal_factors[ay_mask].mean())
        else:
            aylik_faktorler.append(0)
    
    renkler = ['red' if x < 0 else 'green' for x in aylik_faktorler]
    bars = eksenler[1, 1].bar(aylar, aylik_faktorler, color=renkler, alpha=0.7)
    eksenler[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    eksenler[1, 1].set_title('Aylık Ortalama Mevsimsel Faktörler')
    eksenler[1, 1].set_ylabel('Mevsimsel Etki (TL)')
    eksenler[1, 1].tick_params(axis='x', rotation=45)
    eksenler[1, 1].grid(True, alpha=0.3)
    
    # Bar'lara değer etiketleri ekle
    for bar, deger in zip(bars, aylik_faktorler):
        yukseklik = bar.get_height()
        eksenler[1, 1].text(bar.get_x() + bar.get_width()/2., 
                           yukseklik + (10 if yukseklik >= 0 else -20),
                           f'{deger:,.0f}', ha='center', 
                           va='bottom' if yukseklik >= 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    
    # Grafiği kaydet
    try:
        grafik_dosyasi = 'x13_sonuclari.png'
        plt.savefig(grafik_dosyasi, dpi=80)
        print(f"✅ Grafik kaydedildi: {grafik_dosyasi}")
    except Exception as e:
        print(f"⚠️ Grafik kaydetme hatası: {e}")
        print("📊 Grafik verileri hesaplandı ama dosyaya kaydedilemedi.")
    
    # Terminal'de çalıştığımız için show() kapatıldı
    # plt.show()
    plt.close()  # Bellek temizliği


def pratik_tavsiyeler():
    """Pratik kullanım tavsiyeleri"""
    print(f"\n💡 PRATİK TAVSİYELER:")
    print("=" * 30)
    print("📈 İş Analitiği:")
    print("  - Seasonal adjusted veriyi trend analizi için kullanın")
    print("  - Aylık performans karşılaştırmalarında SA veri daha doğru")
    print("  - Bütçe planlaması için mevsimsel faktörleri dikkate alın")
    
    print(f"\n📊 Veri Kalitesi:")
    print("  - En az 2-3 yıl veri kullanın")
    print("  - Eksik değerleri kontrol edin")
    print("  - Aykırı değerleri (outlier) paket otomatik tespit eder")
    
    print(f"\n🔧 Model Ayarları:")
    print("  - Perakende veriler için: trading_day=True")
    print("  - Finansal veriler için: transform='log'")
    print("  - Çeyreklik veriler için: freq='Q'")


def hizli_test():
    """5 satırda hızlı test"""
    print(f"\n⚡ HIZLI TEST (5 satır kod):")
    print("=" * 30)
    
    # Basit veri oluştur
    dates = pd.date_range('2022-01-01', periods=24, freq='M')
    data = pd.Series(1000 + 100*np.sin(2*np.pi*np.arange(24)/12) + np.random.randn(24)*20, 
                     index=dates)
    
    # X13 uygula (sadece 3 satır!)
    x13 = X13SeasonalAdjustment()
    result = x13.fit_transform(data)
    print(f"✅ Mevsimsellik gücü: {result.seasonality_strength:.1%}")


def ana_program():
    """Ana program - tüm adımları çalıştır"""
    
    # 1. Örnek veri oluştur
    veri = ornek_veri_olustur()
    
    # 2. Mevsimsellik testi
    mevsimsellik_sonucu = mevsimsellik_testi(veri)
    
    # 3. X13 uygula
    x13_sonucu = x13_uygula(veri)
    
    # 4. Sonuçları analiz et
    sonuclari_analiz_et(x13_sonucu)
    
    # 5. Grafik çiz
    grafik_ciz(x13_sonucu)
    
    # 6. Pratik tavsiyeler
    pratik_tavsiyeler()
    
    # 7. Hızlı test
    hizli_test()
    
    print(f"\n🎉 TÜM TESTLER TAMAMLANDI!")
    print("=" * 50)
    print("📦 Paket başarıyla çalışıyor!")
    print("📧 Sorular için: gardash.abbasov@gmail.com")
    print("🐙 GitHub: @Gardash023")
    
    return x13_sonucu


# ============================================================================
# ARKADAŞINA GÖNDERECEĞİN BİLGİLER
# ============================================================================

def arkadas_icin_bilgiler():
    """Arkadaşın için yararlı bilgiler"""
    print(f"\n📋 ARKADAŞIN İÇİN BİLGİLER:")
    print("=" * 40)
    
    print(f"🔗 Paket Linki:")
    print(f"   https://pypi.org/project/x13-seasonal-adjustment/")
    
    print(f"\n💻 Kurulum:")
    print(f"   pip install x13-seasonal-adjustment")
    
    print(f"\n📚 Basit Kullanım:")
    print(f"""
   from x13_seasonal_adjustment import X13SeasonalAdjustment
   import pandas as pd
   
   # Verin var mı? (pandas Series olmalı, DatetimeIndex ile)
   x13 = X13SeasonalAdjustment()
   result = x13.fit_transform(verinin)
   print(result.seasonally_adjusted)
    """)
    
    print(f"\n📈 Ne işe yarar:")
    print(f"   - Satış verilerindeki mevsimsel etkiyi çıkarır")
    print(f"   - Gerçek trend'i gösterir")
    print(f"   - Aylık/çeyreklik karşılaştırma yapar")
    print(f"   - İş planlaması için mevsimsel pattern'ları tespit eder")
    
    print(f"\n🎯 Hangi veriler için kullanılır:")
    print(f"   - Satış verileri")
    print(f"   - Ekonomik göstergeler (GDP, enflasyon)")
    print(f"   - Finansal veriler (kazanç, gelir)")
    print(f"   - Üretim verileri")
    print(f"   - Herhangi bir zaman serisi!")


if __name__ == "__main__":
    print("🚀 X13 Seasonal Adjustment Paketi Test Başlıyor...")
    print("👨‍💻 Geliştirici: Gardash Abbasov")
    print("🔗 GitHub: @Gardash023")
    print()
    
    # Arkadaş bilgileri göster
    arkadas_icin_bilgiler()
    
    # Ana programı çalıştır
    try:
        sonuc = ana_program()
        print(f"\n✅ HER ŞEY MÜKEMMEL! Paket çalışıyor! 🎉")
        
    except Exception as hata:
        import traceback
        print(f"\n❌ Hata oluştu: {hata}")
        print("🔧 Detaylı hata bilgisi:")
        traceback.print_exc()
        print("📧 Hata ile ilgili gardash.abbasov@gmail.com'a yazabilirsin")
