"""
ARIMA model seçimi ve değerlendirme araçları.
"""

from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np
import warnings
from itertools import product

from .auto_arima import AutoARIMA


class ARIMAModelSelector:
    """
    ARIMA model seçimi için gelişmiş araçlar.
    
    Bu sınıf, AutoARIMA'ya ek olarak, manuel model karşılaştırması
    ve model seçimi için araçlar sağlar.
    """
    
    def __init__(
        self,
        information_criterion: str = 'aicc',
        cross_validation: bool = False,
        cv_folds: int = 3
    ):
        self.information_criterion = information_criterion.lower()
        self.cross_validation = cross_validation
        self.cv_folds = cv_folds
        
        self.candidate_models = []
        self.best_model = None
        self.model_comparisons = None
    
    def add_candidate_model(
        self, 
        order: Tuple[int, int, int],
        seasonal_order: Tuple[int, int, int],
        seasonal_period: int = 12
    ) -> None:
        """Aday model ekler."""
        
        self.candidate_models.append({
            'order': order,
            'seasonal_order': seasonal_order,
            'seasonal_period': seasonal_period
        })
    
    def add_candidate_models_range(
        self,
        p_range: List[int],
        d_range: List[int], 
        q_range: List[int],
        P_range: List[int] = None,
        D_range: List[int] = None,
        Q_range: List[int] = None,
        seasonal_period: int = 12
    ) -> None:
        """Belirtilen aralıklarda tüm model kombinasyonlarını ekler."""
        
        if P_range is None:
            P_range = [0]
        if D_range is None:
            D_range = [0]
        if Q_range is None:
            Q_range = [0]
        
        for p, d, q, P, D, Q in product(p_range, d_range, q_range, P_range, D_range, Q_range):
            self.add_candidate_model((p, d, q), (P, D, Q), seasonal_period)
    
    def fit_and_compare(
        self, 
        series: pd.Series,
        X: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Tüm aday modelleri fit eder ve karşılaştırır.
        
        Args:
            series: Zaman serisi
            X: Dışsal değişkenler
            
        Returns:
            Dict: Model karşılaştırma sonuçları
        """
        
        if not self.candidate_models:
            raise ValueError("Hiçbir aday model eklenmemiş")
        
        results = []
        
        for i, model_config in enumerate(self.candidate_models):
            try:
                # Model oluştur ve fit et
                auto_arima = AutoARIMA(
                    seasonal_period=model_config['seasonal_period'],
                    information_criterion=self.information_criterion,
                    suppress_warnings=True
                )
                
                # Manuel order set et
                auto_arima.order_ = model_config['order']
                auto_arima.seasonal_order_ = model_config['seasonal_order']
                
                # Model fit et
                fitted_model = auto_arima._fit_arima(
                    series, 
                    model_config['order'],
                    model_config['seasonal_order'] + (model_config['seasonal_period'],),
                    X
                )
                
                if fitted_model:
                    model_result = {
                        'model_id': i,
                        'order': model_config['order'],
                        'seasonal_order': model_config['seasonal_order'],
                        'seasonal_period': model_config['seasonal_period'],
                        'aic': fitted_model['aic'],
                        'bic': fitted_model['bic'], 
                        'aicc': fitted_model['aicc'],
                        'hqic': fitted_model['hqic'],
                        'model': fitted_model['model'],
                        'converged': True
                    }
                    
                    # Cross-validation skorları
                    if self.cross_validation:
                        cv_scores = self._cross_validate_model(
                            fitted_model['model'], series, X
                        )
                        model_result['cv_scores'] = cv_scores
                    
                    results.append(model_result)
                
            except Exception as e:
                # Model fit edilemezse
                results.append({
                    'model_id': i,
                    'order': model_config['order'],
                    'seasonal_order': model_config['seasonal_order'],
                    'error': str(e),
                    'converged': False
                })
        
        # Sonuçları sırala
        successful_results = [r for r in results if r.get('converged', False)]
        
        if successful_results:
            # Information criterion'a göre sırala
            ic_key = self.information_criterion
            successful_results.sort(key=lambda x: x.get(ic_key, float('inf')))
            self.best_model = successful_results[0]
        
        self.model_comparisons = {
            'all_results': results,
            'successful_results': successful_results,
            'best_model': self.best_model,
            'comparison_table': self._create_comparison_table(successful_results)
        }
        
        return self.model_comparisons
    
    def _cross_validate_model(
        self, 
        fitted_model, 
        series: pd.Series,
        X: Optional[pd.DataFrame]
    ) -> Dict[str, float]:
        """Model için cross-validation yapar."""
        
        try:
            n = len(series)
            fold_size = n // self.cv_folds
            
            cv_errors = []
            
            for fold in range(self.cv_folds):
                # Train/test split
                test_start = fold * fold_size
                test_end = min((fold + 1) * fold_size, n)
                
                if test_end - test_start < 10:  # En az 10 gözlem gerekli
                    continue
                
                train_series = series.iloc[:test_start + int(0.8 * (test_end - test_start))]
                test_series = series.iloc[test_start + int(0.8 * (test_end - test_start)):test_end]
                
                if len(train_series) < 20 or len(test_series) < 5:
                    continue
                
                # Model yeniden fit et
                try:
                    from statsmodels.tsa.arima.model import ARIMA
                    
                    cv_model = ARIMA(
                        train_series,
                        order=fitted_model.specification['order'],
                        seasonal_order=fitted_model.specification.get('seasonal_order'),
                        exog=X.iloc[:len(train_series)] if X is not None else None
                    )
                    
                    cv_fitted = cv_model.fit(method_kwargs={'warn_convergence': False})
                    
                    # Forecast
                    forecast = cv_fitted.forecast(
                        steps=len(test_series),
                        exog=X.iloc[len(train_series):len(train_series) + len(test_series)] if X is not None else None
                    )
                    
                    # Error hesapla
                    mae = np.mean(np.abs(test_series - forecast))
                    mse = np.mean((test_series - forecast) ** 2)
                    rmse = np.sqrt(mse)
                    
                    cv_errors.append({
                        'mae': mae,
                        'mse': mse, 
                        'rmse': rmse
                    })
                    
                except:
                    continue
            
            if cv_errors:
                return {
                    'cv_mae': np.mean([e['mae'] for e in cv_errors]),
                    'cv_mse': np.mean([e['mse'] for e in cv_errors]),
                    'cv_rmse': np.mean([e['rmse'] for e in cv_errors]),
                    'cv_folds_used': len(cv_errors)
                }
            else:
                return {'error': 'Cross-validation failed'}
                
        except Exception as e:
            return {'error': f'Cross-validation error: {str(e)}'}
    
    def _create_comparison_table(self, results: List[Dict]) -> pd.DataFrame:
        """Model karşılaştırma tablosu oluşturur."""
        
        if not results:
            return pd.DataFrame()
        
        table_data = []
        
        for result in results:
            row = {
                'Model': f"ARIMA{result['order']}x{result['seasonal_order']}",
                'AIC': result.get('aic', np.nan),
                'BIC': result.get('bic', np.nan), 
                'AICC': result.get('aicc', np.nan),
                'HQIC': result.get('hqic', np.nan)
            }
            
            # CV scores varsa ekle
            if 'cv_scores' in result and isinstance(result['cv_scores'], dict):
                row['CV_RMSE'] = result['cv_scores'].get('cv_rmse', np.nan)
                row['CV_MAE'] = result['cv_scores'].get('cv_mae', np.nan)
            
            table_data.append(row)
        
        df = pd.DataFrame(table_data)
        
        # Rank ekle (information criterion'a göre)
        ic_col = self.information_criterion.upper()
        if ic_col in df.columns:
            df['Rank'] = df[ic_col].rank()
        
        return df.sort_values('Rank' if 'Rank' in df.columns else ic_col)
    
    def get_best_model(self) -> Optional[Dict]:
        """En iyi modeli döndürür."""
        return self.best_model
    
    def summary_report(self) -> str:
        """Model karşılaştırma özetini döndürür."""
        
        if self.model_comparisons is None:
            return "Henüz model karşılaştırması yapılmamış."
        
        report = []
        report.append("=== ARIMA MODEL KARŞILAŞTIRMA RAPORU ===\n")
        
        successful_count = len(self.model_comparisons['successful_results'])
        total_count = len(self.model_comparisons['all_results'])
        
        report.append(f"Toplam test edilen model: {total_count}")
        report.append(f"Başarıyla fit edilen model: {successful_count}")
        report.append(f"Başarı oranı: {successful_count/total_count*100:.1f}%\n")
        
        if self.best_model:
            report.append("=== EN İYİ MODEL ===")
            report.append(f"Model: ARIMA{self.best_model['order']}x{self.best_model['seasonal_order']}")
            report.append(f"AIC: {self.best_model['aic']:.3f}")
            report.append(f"BIC: {self.best_model['bic']:.3f}")
            report.append(f"AICC: {self.best_model['aicc']:.3f}")
            
            if 'cv_scores' in self.best_model:
                cv = self.best_model['cv_scores']
                if isinstance(cv, dict) and 'cv_rmse' in cv:
                    report.append(f"CV RMSE: {cv['cv_rmse']:.3f}")
            
            report.append("")
        
        # Top 5 model listesi
        if successful_count > 0:
            report.append("=== EN İYİ 5 MODEL ===")
            comparison_table = self.model_comparisons['comparison_table']
            
            top_models = comparison_table.head(5)
            report.append(top_models.to_string(index=False))
        
        return "\n".join(report)
    
    def plot_model_comparison(self, figsize: tuple = (12, 8)) -> None:
        """Model karşılaştırma grafiği çizer."""
        
        if self.model_comparisons is None:
            print("Henüz model karşılaştırması yapılmamış.")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            comparison_table = self.model_comparisons['comparison_table']
            
            if comparison_table.empty:
                print("Karşılaştırma tablosu boş.")
                return
            
            fig, axes = plt.subplots(2, 2, figsize=figsize)
            
            # AIC comparison
            axes[0, 0].bar(range(len(comparison_table)), comparison_table['AIC'])
            axes[0, 0].set_title('AIC Karşılaştırması')
            axes[0, 0].set_xlabel('Model Index')
            axes[0, 0].set_ylabel('AIC')
            
            # BIC comparison  
            axes[0, 1].bar(range(len(comparison_table)), comparison_table['BIC'])
            axes[0, 1].set_title('BIC Karşılaştırması')
            axes[0, 1].set_xlabel('Model Index')
            axes[0, 1].set_ylabel('BIC')
            
            # AICC comparison
            axes[1, 0].bar(range(len(comparison_table)), comparison_table['AICC'])
            axes[1, 0].set_title('AICC Karşılaştırması')
            axes[1, 0].set_xlabel('Model Index')
            axes[1, 0].set_ylabel('AICC')
            
            # CV RMSE (eğer varsa)
            if 'CV_RMSE' in comparison_table.columns:
                valid_cv = comparison_table['CV_RMSE'].dropna()
                if not valid_cv.empty:
                    axes[1, 1].bar(range(len(valid_cv)), valid_cv)
                    axes[1, 1].set_title('CV RMSE Karşılaştırması')
                    axes[1, 1].set_xlabel('Model Index')
                    axes[1, 1].set_ylabel('CV RMSE')
                else:
                    axes[1, 1].text(0.5, 0.5, 'CV sonucu yok', 
                                   ha='center', va='center', transform=axes[1, 1].transAxes)
            else:
                axes[1, 1].text(0.5, 0.5, 'CV yapılmamış', 
                               ha='center', va='center', transform=axes[1, 1].transAxes)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib kurulu değil. Grafik çizilemedi.")
        except Exception as e:
            print(f"Grafik çiziminde hata: {e}")
