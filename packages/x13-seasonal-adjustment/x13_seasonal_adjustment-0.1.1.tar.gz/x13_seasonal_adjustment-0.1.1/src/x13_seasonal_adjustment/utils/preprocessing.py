"""
Veri ön işleme fonksiyonları.
"""

from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler


def preprocess_series(
    series: pd.Series,
    handle_missing: bool = True,
    detect_outliers: bool = True,
    outlier_info: Optional[Dict] = None
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Zaman serisini X13 analizi için ön işleme tabi tutar.
    
    Args:
        series: İşlenecek zaman serisi
        handle_missing: Eksik değerler doldurulsun mu?
        detect_outliers: Aykırı değer tespiti yapılsın mı?
        outlier_info: Önceden tespit edilmiş aykırı değer bilgisi
        
    Returns:
        Tuple[pd.Series, Dict]: İşlenmiş seri ve işlem bilgileri
    """
    
    preprocessed = series.copy()
    info = {
        'missing_handled': False,
        'outliers_detected': False,
        'outliers': None,
        'transformations': []
    }
    
    # 1. Eksik değer işleme
    if handle_missing and preprocessed.isnull().any():
        missing_count = preprocessed.isnull().sum()
        missing_indices = preprocessed[preprocessed.isnull()].index.tolist()
        
        # Eksik değer doldurma stratejisi
        preprocessed = fill_missing_values(preprocessed)
        
        info['missing_handled'] = True
        info['missing_count'] = missing_count
        info['missing_indices'] = missing_indices
        info['transformations'].append('missing_value_imputation')
    
    # 2. Aykırı değer tespiti ve işleme
    if detect_outliers:
        if outlier_info is None:
            outliers = detect_outliers_comprehensive(preprocessed)
        else:
            outliers = outlier_info
        
        if outliers and len(outliers.get('indices', [])) > 0:
            preprocessed = handle_outliers(preprocessed, outliers)
            info['outliers_detected'] = True
            info['outliers'] = outliers
            info['transformations'].append('outlier_treatment')
    
    return preprocessed, info


def fill_missing_values(series: pd.Series) -> pd.Series:
    """
    Eksik değerleri akıllı yöntemlerle doldurur.
    
    Args:
        series: Eksik değerleri olan zaman serisi
        
    Returns:
        pd.Series: Eksik değerleri doldurulmuş seri
    """
    
    filled = series.copy()
    
    # Eksik değer oranını kontrol et
    missing_pct = filled.isnull().sum() / len(filled)
    
    if missing_pct == 0:
        return filled
    
    if missing_pct > 0.1:  # %10'dan fazla eksik değer
        # Karmaşık interpolasyon
        # Önce linear interpolation
        filled = filled.interpolate(method='linear')
        
        # Hala eksik değer varsa (başta veya sonda)
        if filled.isnull().any():
            # Forward fill ve backward fill kombinasyonu
            filled = filled.fillna(method='ffill').fillna(method='bfill')
    else:
        # Az eksik değer için gelişmiş yöntemler
        
        # 1. Mevsimsel interpolasyon (eğer yeterli veri varsa)
        if len(filled) >= 24:  # En az 2 yıl veri
            try:
                # Seasonal decomposition ile pattern'ı kullan
                seasonal_filled = seasonal_interpolation(filled)
                if not seasonal_filled.isnull().any():
                    filled = seasonal_filled
                else:
                    raise ValueError("Seasonal interpolation başarısız")
            except:
                # Seasonal interpolation başarısızsa spline kullan
                filled = filled.interpolate(method='spline', order=2)
        else:
            # Az veri için spline interpolation
            filled = filled.interpolate(method='spline', order=min(2, len(filled)-1))
        
        # Hala eksik değer varsa basit forward/backward fill
        if filled.isnull().any():
            filled = filled.fillna(method='ffill').fillna(method='bfill')
    
    return filled


def seasonal_interpolation(series: pd.Series, seasonal_period: int = 12) -> pd.Series:
    """
    Mevsimsel pattern kullanarak eksik değer doldurma.
    
    Args:
        series: Zaman serisi
        seasonal_period: Mevsimsel dönem
        
    Returns:
        pd.Series: Doldurulmuş seri
    """
    
    filled = series.copy()
    
    # Her mevsimsel dönem için ortalama pattern hesapla
    seasonal_means = {}
    for i in range(seasonal_period):
        season_mask = filled.index % seasonal_period == i
        season_values = filled[season_mask]
        if not season_values.empty:
            seasonal_means[i] = season_values.mean()
    
    # Eksik değerleri mevsimsel ortalama ile doldur
    for idx in filled[filled.isnull()].index:
        season = idx % seasonal_period
        if season in seasonal_means:
            filled.loc[idx] = seasonal_means[season]
    
    return filled


def detect_outliers_comprehensive(series: pd.Series) -> Dict[str, Any]:
    """
    Kapsamlı aykırı değer tespiti yapar.
    
    Args:
        series: Zaman serisi
        
    Returns:
        Dict: Aykırı değer bilgileri
    """
    
    outlier_info = {
        'indices': [],
        'types': [],
        'values': [],
        'methods': []
    }
    
    # 1. IQR yöntemi
    iqr_outliers = detect_outliers_iqr(series)
    
    # 2. Z-score yöntemi  
    zscore_outliers = detect_outliers_zscore(series)
    
    # 3. Modified Z-score (robust)
    modified_zscore_outliers = detect_outliers_modified_zscore(series)
    
    # 4. X13-specific outlier detection (Additive/Level Shift/Temporary Change)
    x13_outliers = detect_x13_outliers(series)
    
    # Sonuçları birleştir
    all_outliers = set()
    all_outliers.update(iqr_outliers)
    all_outliers.update(zscore_outliers) 
    all_outliers.update(modified_zscore_outliers)
    all_outliers.update(x13_outliers['indices'])
    
    for idx in all_outliers:
        outlier_info['indices'].append(idx)
        outlier_info['values'].append(series.loc[idx])
        
        # Aykırı değer tipini belirle
        methods = []
        if idx in iqr_outliers:
            methods.append('IQR')
        if idx in zscore_outliers:
            methods.append('Z-score')
        if idx in modified_zscore_outliers:
            methods.append('Modified Z-score')
        if idx in x13_outliers['indices']:
            methods.append('X13')
            
        outlier_info['methods'].append(methods)
        
        # X13 tipi varsa onu kullan, yoksa genel 'outlier'
        if idx in x13_outliers['indices']:
            idx_pos = x13_outliers['indices'].index(idx)
            outlier_info['types'].append(x13_outliers['types'][idx_pos])
        else:
            outlier_info['types'].append('AO')  # Additive Outlier default
    
    return outlier_info


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> list:
    """IQR yöntemi ile aykırı değer tespiti."""
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    
    outliers = series[(series < lower_bound) | (series > upper_bound)].index.tolist()
    return outliers


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> list:
    """Z-score yöntemi ile aykırı değer tespiti."""
    z_scores = np.abs(stats.zscore(series))
    outliers = series[z_scores > threshold].index.tolist()
    return outliers


def detect_outliers_modified_zscore(series: pd.Series, threshold: float = 3.5) -> list:
    """Modified Z-score (robust) ile aykırı değer tespiti."""
    median = np.median(series)
    mad = np.median(np.abs(series - median))
    
    if mad == 0:
        return []
    
    modified_z_scores = 0.6745 * (series - median) / mad
    outliers = series[np.abs(modified_z_scores) > threshold].index.tolist()
    return outliers


def detect_x13_outliers(series: pd.Series) -> Dict[str, list]:
    """
    X13-ARIMA-SEATS tipinde aykırı değer tespiti.
    
    Types:
    - AO: Additive Outlier (tek nokta aykırı değeri)
    - LS: Level Shift (seviye değişimi)
    - TC: Temporary Change (geçici değişim)
    """
    
    outliers = {
        'indices': [],
        'types': [],
        'values': []
    }
    
    # 1. Additive Outliers (AO) - tek nokta aykırı değerleri
    ao_indices = detect_additive_outliers(series)
    outliers['indices'].extend(ao_indices)
    outliers['types'].extend(['AO'] * len(ao_indices))
    outliers['values'].extend(series.loc[ao_indices].tolist())
    
    # 2. Level Shifts (LS) - seviye değişimleri
    ls_indices = detect_level_shifts(series)
    outliers['indices'].extend(ls_indices)
    outliers['types'].extend(['LS'] * len(ls_indices))
    outliers['values'].extend(series.loc[ls_indices].tolist())
    
    # 3. Temporary Changes (TC) - geçici değişimler
    tc_indices = detect_temporary_changes(series)
    outliers['indices'].extend(tc_indices)
    outliers['types'].extend(['TC'] * len(tc_indices))
    outliers['values'].extend(series.loc[tc_indices].tolist())
    
    return outliers


def detect_additive_outliers(series: pd.Series, threshold: float = 3.0) -> list:
    """Additive Outlier (AO) tespiti."""
    # Basit Z-score yöntemi (geliştirilmesi gerekebilir)
    residuals = series - series.rolling(window=5, center=True).median()
    z_scores = np.abs(stats.zscore(residuals.dropna()))
    
    outlier_mask = z_scores > threshold
    outliers = residuals.dropna()[outlier_mask].index.tolist()
    
    return outliers


def detect_level_shifts(series: pd.Series, min_shift_size: float = None) -> list:
    """Level Shift (LS) tespiti."""
    if min_shift_size is None:
        min_shift_size = 2 * series.std()
    
    # Moving average ile trend hesapla
    trend = series.rolling(window=min(12, len(series)//4), center=True).mean()
    trend_diff = trend.diff().abs()
    
    # Büyük değişimleri tespit et
    threshold = min_shift_size
    large_changes = trend_diff > threshold
    
    outliers = series[large_changes].index.tolist()
    return outliers


def detect_temporary_changes(series: pd.Series, window: int = 3) -> list:
    """Temporary Change (TC) tespiti."""
    outliers = []
    
    # Kısa süreli değişimleri tespit et
    for i in range(window, len(series) - window):
        # Önceki ve sonraki pencere ortalamaları
        before = series.iloc[i-window:i].mean()
        after = series.iloc[i+1:i+window+1].mean()
        current = series.iloc[i]
        
        # Current değer, önceki ve sonraki ortalamalardan çok farklıysa
        if abs(current - before) > 2 * series.std() and abs(current - after) > 2 * series.std():
            # Ve önceki-sonraki ortalamalar birbirine yakınsa
            if abs(before - after) < series.std():
                outliers.append(series.index[i])
    
    return outliers


def handle_outliers(series: pd.Series, outlier_info: Dict[str, Any]) -> pd.Series:
    """
    Tespit edilen aykırı değerleri işler.
    
    Args:
        series: Zaman serisi
        outlier_info: Aykırı değer bilgileri
        
    Returns:
        pd.Series: İşlenmiş seri
    """
    
    treated = series.copy()
    
    for i, idx in enumerate(outlier_info['indices']):
        outlier_type = outlier_info['types'][i]
        
        if outlier_type == 'AO':
            # Additive Outlier: interpolation ile değiştir
            treated.loc[idx] = np.nan
            treated = treated.interpolate(method='linear')
            
        elif outlier_type == 'LS':
            # Level Shift: değeri olduğu gibi bırak (structural change olabilir)
            pass
            
        elif outlier_type == 'TC':
            # Temporary Change: interpolation ile düzelt
            treated.loc[idx] = np.nan
            treated = treated.interpolate(method='linear')
    
    # Final interpolation (eğer hala NaN varsa)
    if treated.isnull().any():
        treated = treated.fillna(method='ffill').fillna(method='bfill')
    
    return treated
