"""
Otomatik ARIMA model seçimi ve tahmin.
"""

from typing import Tuple, Optional, Union, List, Dict, Any
import pandas as pd
import numpy as np
import warnings
from itertools import product
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox


class AutoARIMA:
    """
    Otomatik ARIMA model seçimi ve tahmin sınıfı.
    
    Bu sınıf, X13-ARIMA-SEATS'de kullanılan otomatik ARIMA model seçim
    prosedürünü implementasyonunu sağlar.
    """
    
    def __init__(
        self,
        max_p: int = 3,
        max_d: int = 2, 
        max_q: int = 3,
        max_P: int = 2,
        max_D: int = 1,
        max_Q: int = 2,
        seasonal: bool = True,
        seasonal_period: int = 12,
        information_criterion: str = 'aicc',
        max_order: int = 5,
        stepwise: bool = True,
        suppress_warnings: bool = True
    ):
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.max_P = max_P
        self.max_D = max_D
        self.max_Q = max_Q
        self.seasonal = seasonal
        self.seasonal_period = seasonal_period
        self.information_criterion = information_criterion.lower()
        self.max_order = max_order
        self.stepwise = stepwise
        self.suppress_warnings = suppress_warnings
        
        # Fitted model attributes
        self.model_ = None
        self.order_ = None
        self.seasonal_order_ = None
        self.aic_ = None
        self.bic_ = None
        self.aicc_ = None
        self.hqic_ = None
        self.is_fitted_ = False
        
        # Validation
        valid_ic = ['aic', 'bic', 'aicc', 'hqic']
        if self.information_criterion not in valid_ic:
            raise ValueError(f"information_criterion must be one of {valid_ic}")
    
    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> 'AutoARIMA':
        """
        Otomatik ARIMA model seçimi ve tahmin.
        
        Args:
            y (pd.Series): Bağımlı değişken (zaman serisi)
            X (Optional[pd.DataFrame]): Dışsal değişkenler
            
        Returns:
            AutoARIMA: Fitted model
        """
        if self.suppress_warnings:
            warnings.filterwarnings('ignore')
        
        # Veri doğrulama
        y = self._validate_input(y)
        
        # Differencing order'ları belirle
        d = self._determine_d(y)
        D = self._determine_D(y) if self.seasonal else 0
        
        # Model arama
        if self.stepwise:
            best_model = self._stepwise_search(y, d, D, X)
        else:
            best_model = self._grid_search(y, d, D, X)
        
        # En iyi modeli sakla
        self.model_ = best_model['model']
        self.order_ = best_model['order']
        self.seasonal_order_ = best_model['seasonal_order']
        self.aic_ = best_model['aic']
        self.bic_ = best_model['bic']
        self.aicc_ = best_model['aicc']
        self.hqic_ = best_model['hqic']
        self.is_fitted_ = True
        
        return self
    
    def _validate_input(self, y: pd.Series) -> pd.Series:
        """Giriş verisini doğrular."""
        if not isinstance(y, pd.Series):
            y = pd.Series(y)
        
        if y.isnull().any():
            raise ValueError("Zaman serisinde eksik değer bulunamaz")
        
        if len(y) < 2 * self.seasonal_period:
            raise ValueError(f"En az {2 * self.seasonal_period} gözlem gerekli")
        
        return y
    
    def _determine_d(self, y: pd.Series) -> int:
        """Differencing order (d) belirler."""
        max_d = min(self.max_d, 2)  # Genellikle 2'den fazla fark almaya gerek yok
        
        current_series = y.copy()
        
        for d in range(max_d + 1):
            # ADF testi
            try:
                adf_stat, adf_p = adfuller(current_series.dropna(), autolag='AIC')[:2]
                adf_stationary = adf_p < 0.05
            except:
                adf_stationary = False
            
            # KPSS testi
            try:
                kpss_stat, kpss_p = kpss(current_series.dropna(), regression='c')[:2]
                kpss_stationary = kpss_p > 0.05
            except:
                kpss_stationary = False
            
            # Her iki test de durağanlık gösteriyorsa
            if adf_stationary and kpss_stationary:
                return d
            
            # Bir sonraki differencing için hazırla
            if d < max_d:
                current_series = current_series.diff().dropna()
        
        return max_d
    
    def _determine_D(self, y: pd.Series) -> int:
        """Seasonal differencing order (D) belirler."""
        if not self.seasonal or self.seasonal_period <= 1:
            return 0
        
        max_D = min(self.max_D, 1)  # Genellikle 1'den fazla mevsimsel fark gerekmez
        
        # Mevsimsel durağanlık testi
        try:
            # Mevsimsel lag ile birim kök testi
            seasonal_diff = y.diff(self.seasonal_period).dropna()
            
            if len(seasonal_diff) > self.seasonal_period:
                adf_stat, adf_p = adfuller(seasonal_diff, autolag='AIC')[:2]
                if adf_p < 0.05:
                    return 1
            
            return 0
        except:
            return 0
    
    def _stepwise_search(
        self, 
        y: pd.Series, 
        d: int, 
        D: int, 
        X: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """Stepwise model arama algoritması."""
        
        # Başlangıç modelleri
        start_models = [
            (0, d, 0, 0, D, 0),  # (0,d,0)(0,D,0)
            (1, d, 0, 0, D, 0),  # (1,d,0)(0,D,0)
            (0, d, 1, 0, D, 0),  # (0,d,1)(0,D,0)
        ]
        
        if self.seasonal:
            start_models.extend([
                (0, d, 0, 1, D, 0),  # (0,d,0)(1,D,0)
                (0, d, 0, 0, D, 1),  # (0,d,0)(0,D,1)
                (1, d, 1, 0, D, 0),  # (1,d,1)(0,D,0)
                (0, d, 0, 1, D, 1),  # (0,d,0)(1,D,1)
            ])
        
        # En iyi modeli bul
        best_model = None
        best_ic = float('inf')
        
        for p, d, q, P, D, Q in start_models:
            if p + d + q + P + D + Q <= self.max_order:
                model_result = self._fit_arima(y, (p, d, q), (P, D, Q), X)
                if model_result and model_result[self.information_criterion] < best_ic:
                    best_ic = model_result[self.information_criterion]
                    best_model = model_result
        
        if best_model is None:
            raise ValueError("Hiçbir model tahmin edilemedi")
        
        # Stepwise improvement
        current_order = best_model['order']
        current_seasonal_order = best_model['seasonal_order']
        improved = True
        
        while improved:
            improved = False
            candidates = self._get_neighbor_models(current_order, current_seasonal_order)
            
            for order, seasonal_order in candidates:
                if sum(order) + sum(seasonal_order) <= self.max_order:
                    model_result = self._fit_arima(y, order, seasonal_order, X)
                    if model_result and model_result[self.information_criterion] < best_ic:
                        best_ic = model_result[self.information_criterion]
                        best_model = model_result
                        current_order = order
                        current_seasonal_order = seasonal_order
                        improved = True
                        break
        
        return best_model
    
    def _grid_search(
        self, 
        y: pd.Series, 
        d: int, 
        D: int, 
        X: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """Grid search ile model arama."""
        
        p_range = range(0, self.max_p + 1)
        q_range = range(0, self.max_q + 1)
        P_range = range(0, self.max_P + 1) if self.seasonal else [0]
        Q_range = range(0, self.max_Q + 1) if self.seasonal else [0]
        
        best_model = None
        best_ic = float('inf')
        
        for p, q, P, Q in product(p_range, q_range, P_range, Q_range):
            if p + d + q + P + D + Q <= self.max_order:
                order = (p, d, q)
                seasonal_order = (P, D, Q) if self.seasonal else (0, 0, 0)
                
                model_result = self._fit_arima(y, order, seasonal_order, X)
                if model_result and model_result[self.information_criterion] < best_ic:
                    best_ic = model_result[self.information_criterion]
                    best_model = model_result
        
        if best_model is None:
            raise ValueError("Hiçbir model tahmin edilemedi")
        
        return best_model
    
    def _fit_arima(
        self, 
        y: pd.Series, 
        order: Tuple[int, int, int],
        seasonal_order: Tuple[int, int, int],
        X: Optional[pd.DataFrame]
    ) -> Optional[Dict[str, Any]]:
        """Tek bir ARIMA modeli tahmin eder."""
        
        try:
            # Seasonal order'ı period ile genişlet
            if self.seasonal and len(seasonal_order) == 3:
                seasonal_order = seasonal_order + (self.seasonal_period,)
            
            # Model tahmin et
            model = ARIMA(y, order=order, seasonal_order=seasonal_order, exog=X)
            fitted_model = model.fit(method_kwargs={'warn_convergence': False})
            
            # Information criteria hesapla
            aic = fitted_model.aic
            bic = fitted_model.bic
            hqic = fitted_model.hqic
            
            # AICC hesapla (küçük örnekler için düzeltilmiş AIC)
            n = len(y)
            k = len(fitted_model.params)
            if n - k - 1 > 0:
                aicc = aic + (2 * k * (k + 1)) / (n - k - 1)
            else:
                aicc = float('inf')
            
            return {
                'model': fitted_model,
                'order': order,
                'seasonal_order': seasonal_order,
                'aic': aic,
                'bic': bic,
                'aicc': aicc,
                'hqic': hqic
            }
            
        except Exception as e:
            if not self.suppress_warnings:
                warnings.warn(f"Model {order}{seasonal_order} tahmin edilemedi: {e}")
            return None
    
    def _get_neighbor_models(
        self, 
        order: Tuple[int, int, int],
        seasonal_order: Tuple[int, int, int]
    ) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
        """Stepwise search için komşu modelleri döndürür."""
        
        p, d, q = order
        P, D, Q = seasonal_order[:3]  # Period'u ignore et
        
        candidates = []
        
        # p, q için ±1 varyasyonları
        for dp in [-1, 1]:
            if 0 <= p + dp <= self.max_p:
                candidates.append(((p + dp, d, q), seasonal_order))
        
        for dq in [-1, 1]:
            if 0 <= q + dq <= self.max_q:
                candidates.append(((p, d, q + dq), seasonal_order))
        
        # Seasonal P, Q için ±1 varyasyonları (eğer seasonal aktifse)
        if self.seasonal:
            for dP in [-1, 1]:
                if 0 <= P + dP <= self.max_P:
                    new_seasonal = (P + dP, D, Q)
                    if self.seasonal_period > 1:
                        new_seasonal += (self.seasonal_period,)
                    candidates.append((order, new_seasonal))
            
            for dQ in [-1, 1]:
                if 0 <= Q + dQ <= self.max_Q:
                    new_seasonal = (P, D, Q + dQ)
                    if self.seasonal_period > 1:
                        new_seasonal += (self.seasonal_period,)
                    candidates.append((order, new_seasonal))
        
        return candidates
    
    def predict(
        self, 
        start: Optional[int] = None, 
        end: Optional[int] = None,
        X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """In-sample tahmin yapar."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        return self.model_.predict(start=start, end=end, exog=X)
    
    def forecast(
        self, 
        steps: int = 1, 
        X: Optional[pd.DataFrame] = None,
        alpha: float = 0.05
    ) -> Union[pd.Series, Tuple[pd.Series, pd.DataFrame]]:
        """Out-of-sample öngörü yapar."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        forecast_result = self.model_.get_forecast(steps=steps, exog=X)
        forecast_values = forecast_result.predicted_mean
        
        if alpha > 0:
            conf_int = forecast_result.conf_int(alpha=alpha)
            return forecast_values, conf_int
        else:
            return forecast_values
    
    def predict_in_sample(self, start: int = 0, end: Optional[int] = None) -> pd.Series:
        """In-sample öngörü (backcast için kullanılır)."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        return self.model_.predict(start=start, end=end)
    
    def residuals(self) -> pd.Series:
        """Model residuals'larını döndürür."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        return self.model_.resid
    
    def diagnostic_tests(self) -> Dict[str, Any]:
        """Model tanı testlerini yapar."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        resid = self.residuals()
        
        # Ljung-Box testi (autocorrelation)
        try:
            ljung_box = acorr_ljungbox(resid, lags=min(10, len(resid)//4), return_df=True)
            lb_stat = ljung_box['lb_stat'].iloc[-1]
            lb_pvalue = ljung_box['lb_pvalue'].iloc[-1]
        except:
            lb_stat, lb_pvalue = np.nan, np.nan
        
        # Jarque-Bera normallik testi
        try:
            from scipy.stats import jarque_bera
            jb_stat, jb_pvalue = jarque_bera(resid.dropna())
        except:
            jb_stat, jb_pvalue = np.nan, np.nan
        
        return {
            'ljung_box_stat': lb_stat,
            'ljung_box_pvalue': lb_pvalue,
            'jarque_bera_stat': jb_stat,
            'jarque_bera_pvalue': jb_pvalue,
            'aic': self.aic_,
            'bic': self.bic_,
            'aicc': self.aicc_,
            'hqic': self.hqic_
        }
    
    def summary(self) -> str:
        """Model özetini döndürür."""
        if not self.is_fitted_:
            raise ValueError("Model henüz eğitilmemiş")
        
        return self.model_.summary().as_text()
