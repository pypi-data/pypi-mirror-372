"""
Veri doğrulama fonksiyonları.
"""

from typing import Union, Optional
import pandas as pd
import numpy as np


def validate_time_series(
    data: Union[pd.Series, pd.DataFrame, np.ndarray], 
    freq: Optional[str] = None,
    min_length: int = 24
) -> pd.Series:
    """
    Zaman serisi verisini doğrular ve standart formata çevirir.
    
    Args:
        data: Zaman serisi verisi
        freq: Beklenen frekans
        min_length: Minimum seri uzunluğu
        
    Returns:
        pd.Series: Doğrulanmış zaman serisi
        
    Raises:
        ValueError: Veri geçersizse
    """
    
    # Veri tipini kontrol et ve Series'e çevir
    if isinstance(data, pd.DataFrame):
        if data.shape[1] == 1:
            series = data.iloc[:, 0]
        else:
            raise ValueError("DataFrame tek sütunlu olmalıdır")
    elif isinstance(data, np.ndarray):
        if data.ndim > 1:
            raise ValueError("NumPy array tek boyutlu olmalıdır")
        series = pd.Series(data)
    elif isinstance(data, pd.Series):
        series = data.copy()
    else:
        try:
            series = pd.Series(data)
        except:
            raise ValueError("Veri pandas.Series, DataFrame veya array-like olmalıdır")
    
    # Uzunluk kontrolü
    if len(series) < min_length:
        raise ValueError(f"Zaman serisi en az {min_length} gözlem içermelidir. Mevcut: {len(series)}")
    
    # Index kontrolü
    if not isinstance(series.index, pd.DatetimeIndex):
        # Eğer numeric index varsa, otomatik datetime index oluştur
        if freq:
            series.index = pd.date_range(start='2000-01-01', periods=len(series), freq=freq)
        else:
            raise ValueError("Veri DatetimeIndex'e sahip olmalıdır veya freq parametresi belirtilmelidir")
    
    # Frekans kontrolü
    if freq:
        if series.index.freq is None:
            try:
                series.index.freq = pd.tseries.frequencies.to_offset(freq)
            except:
                raise ValueError(f"Geçersiz frekans: {freq}")
        elif str(series.index.freq) != freq:
            raise ValueError(f"Index frekansı ({series.index.freq}) beklenen frekansla ({freq}) uyuşmuyor")
    
    # Eksik değer kontrolü
    if series.isnull().any():
        null_count = series.isnull().sum()
        null_pct = (null_count / len(series)) * 100
        if null_pct > 10:  # %10'dan fazla eksik değer
            raise ValueError(f"Çok fazla eksik değer: {null_count} ({null_pct:.1f}%)")
    
    # Sabit değer kontrolü
    if series.nunique() <= 1:
        raise ValueError("Zaman serisi sabit değerlerden oluşuyor")
    
    # Aşırı aykırı değer kontrolü
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr > 0:
        lower_bound = q1 - 3 * iqr
        upper_bound = q3 + 3 * iqr
        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        outlier_pct = (outliers / len(series)) * 100
        
        if outlier_pct > 5:  # %5'ten fazla aşırı aykırı değer
            raise ValueError(f"Çok fazla aşırı aykırı değer: {outliers} ({outlier_pct:.1f}%)")
    
    # Negatif değer uyarısı (log transform için)
    if (series <= 0).any():
        negative_count = (series <= 0).sum()
        import warnings
        warnings.warn(f"Seride {negative_count} adet sıfır veya negatif değer var. "
                     "Logaritmik dönüşüm sorunlu olabilir.")
    
    return series


def validate_frequency(series: pd.Series) -> str:
    """
    Zaman serisinin frekansını otomatik tespit eder.
    
    Args:
        series: Zaman serisi
        
    Returns:
        str: Tespit edilen frekans
    """
    
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series DatetimeIndex'e sahip olmalıdır")
    
    # Mevcut frekansı kontrol et
    if series.index.freq is not None:
        return str(series.index.freq)
    
    # Frekansı otomatik tespit et
    try:
        inferred_freq = pd.infer_freq(series.index)
        if inferred_freq:
            return inferred_freq
    except:
        pass
    
    # Manuel frekans tespiti
    if len(series) < 2:
        raise ValueError("Frekans tespiti için en az 2 gözlem gerekli")
    
    # İlk birkaç gözlem arasındaki farkları hesapla
    time_diffs = series.index[1:6] - series.index[0:5]
    median_diff = time_diffs.median()
    
    # Yaygın frekansları kontrol et
    if median_diff <= pd.Timedelta(days=1):
        return 'D'  # Günlük
    elif median_diff <= pd.Timedelta(days=7):
        return 'W'  # Haftalık
    elif median_diff <= pd.Timedelta(days=32):
        return 'M'  # Aylık
    elif median_diff <= pd.Timedelta(days=100):
        return 'Q'  # Çeyreklik
    else:
        return 'A'  # Yıllık


def check_seasonality_requirements(series: pd.Series, seasonal_period: int) -> bool:
    """
    Mevsimsellik analizi için yeterli veri olup olmadığını kontrol eder.
    
    Args:
        series: Zaman serisi
        seasonal_period: Mevsimsel dönem uzunluğu
        
    Returns:
        bool: Yeterli veri varsa True
    """
    
    # En az 2 tam dönem gerekli
    min_length = 2 * seasonal_period
    
    if len(series) < min_length:
        return False
    
    # Optimal olarak 3+ tam dönem olmalı
    optimal_length = 3 * seasonal_period
    
    return len(series) >= optimal_length


def detect_data_issues(series: pd.Series) -> dict:
    """
    Veri kalitesi sorunlarını tespit eder.
    
    Args:
        series: Zaman serisi
        
    Returns:
        dict: Tespit edilen sorunların listesi
    """
    
    issues = {
        'missing_values': [],
        'outliers': [],
        'level_shifts': [],
        'volatility_changes': [],
        'warnings': []
    }
    
    # Eksik değerler
    if series.isnull().any():
        missing_indices = series[series.isnull()].index.tolist()
        issues['missing_values'] = missing_indices
        issues['warnings'].append(f"{len(missing_indices)} eksik değer tespit edildi")
    
    # Aykırı değerler (IQR yöntemi)
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    
    if iqr > 0:
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_mask = (series < lower_bound) | (series > upper_bound)
        
        if outlier_mask.any():
            outlier_indices = series[outlier_mask].index.tolist()
            issues['outliers'] = outlier_indices
            issues['warnings'].append(f"{len(outlier_indices)} aykırı değer tespit edildi")
    
    # Seviye değişimleri (basit tespit)
    if len(series) > 12:
        # Moving average ile trend hesapla
        ma = series.rolling(window=min(12, len(series)//4), center=True).mean()
        ma_diff = ma.diff().abs()
        
        # Büyük değişimleri tespit et
        threshold = ma_diff.quantile(0.95)
        large_changes = ma_diff > threshold
        
        if large_changes.any():
            shift_indices = series[large_changes].index.tolist()
            issues['level_shifts'] = shift_indices
            issues['warnings'].append(f"{len(shift_indices)} olası seviye değişimi tespit edildi")
    
    # Volatilite değişimleri
    if len(series) > 24:
        # Rolling standard deviation
        rolling_std = series.rolling(window=min(12, len(series)//6)).std()
        std_changes = rolling_std.diff().abs()
        
        threshold = std_changes.quantile(0.9)
        vol_changes = std_changes > threshold
        
        if vol_changes.any():
            vol_indices = series[vol_changes].index.tolist()
            issues['volatility_changes'] = vol_indices
            issues['warnings'].append(f"{len(vol_indices)} volatilite değişimi tespit edildi")
    
    return issues
