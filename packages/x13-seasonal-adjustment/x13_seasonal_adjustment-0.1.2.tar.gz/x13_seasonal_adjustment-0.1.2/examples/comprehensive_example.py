"""
X13 Seasonal Adjustment - Comprehensive Usage Examples

This file demonstrates various usage scenarios for the x13-seasonal-adjustment library.
Author: Gardash Abbasov
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the X13 library
from x13_seasonal_adjustment import (
    X13SeasonalAdjustment, 
    SeasonalityTests, 
    QualityDiagnostics,
    AutoARIMA
)


def scenario_1_economic_data():
    """
    Scenario 1: Economic Time Series Analysis
    
    Analyzing monthly GDP or industrial production data
    """
    print("=" * 60)
    print("SCENARIO 1: Economic Time Series Analysis")
    print("=" * 60)
    
    # Create synthetic economic data (GDP-like)
    np.random.seed(42)
    dates = pd.date_range('2010-01-01', '2023-12-01', freq='ME')
    
    # Economic growth trend
    trend = 100 * (1.025 ** (np.arange(len(dates)) / 12))  # 2.5% annual growth
    
    # Strong seasonal pattern (typical for economic data)
    seasonal_pattern = [5, 3, 7, 8, 6, 4, -2, -4, 2, 8, 10, 12]
    seasonal = np.tile(seasonal_pattern, len(dates) // 12 + 1)[:len(dates)]
    
    # Economic shocks and cycles
    noise = np.random.normal(0, 3, len(dates))
    # COVID-19 shock in 2020
    covid_shock = np.where((dates.year == 2020) & (dates.month.isin([3, 4, 5])), -15, 0)
    
    gdp_data = trend + seasonal + noise + covid_shock
    gdp_series = pd.Series(gdp_data, index=dates, name='GDP')
    
    print(f"Data period: {dates[0].strftime('%Y-%m')} to {dates[-1].strftime('%Y-%m')}")
    print(f"Number of observations: {len(gdp_series)}")
    print(f"Mean GDP: {gdp_series.mean():.2f}")
    
    # Step 1: Test for seasonality
    print("\nStep 1: Testing for seasonality...")
    seasonality_tests = SeasonalityTests(seasonal_period=12)
    seasonality_result = seasonality_tests.run_all_tests(gdp_series)
    
    print(f"Seasonality detected: {seasonality_result.has_seasonality}")
    print(f"Confidence level: {seasonality_result.confidence_level:.3f}")
    
    # Step 2: Apply X13 seasonal adjustment
    print("\nStep 2: Applying X13 seasonal adjustment...")
    x13 = X13SeasonalAdjustment(
        freq='M',
        transform='auto',
        outlier_detection=True,
        trading_day=False,  # Not relevant for monthly GDP
        easter=False,
        arima_order='auto'
    )
    
    result = x13.fit_transform(gdp_series)
    
    print(f"Seasonality strength: {result.seasonality_strength:.3f}")
    print(f"Trend strength: {result.trend_strength:.3f}")
    print(f"Quality assessment: {result.decomposition_quality}")
    
    # Step 3: Quality diagnostics
    print("\nStep 3: Quality diagnostics...")
    quality_diag = QualityDiagnostics()
    quality_report = quality_diag.evaluate(result)
    
    print(f"Overall quality: {quality_report.overall_quality}")
    print(f"Quality score: {quality_report.summary_scores.get('quality_score', 0):.1f}/100")
    
    # Step 4: Analysis results
    print("\nStep 4: Economic analysis...")
    
    # Calculate annual growth rates
    sa_annual_growth = result.seasonally_adjusted.resample('A').last().pct_change() * 100
    original_annual_growth = result.original.resample('A').last().pct_change() * 100
    
    print("\nAnnual Growth Rates (%):")
    for year in sa_annual_growth.index[1:]:
        sa_growth = sa_annual_growth.loc[year]
        orig_growth = original_annual_growth.loc[year]
        print(f"{year.year}: SA = {sa_growth:.1f}%, Original = {orig_growth:.1f}%")
    
    # Step 5: Visualization
    print("\nStep 5: Creating visualizations...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Original vs Seasonally Adjusted
    axes[0, 0].plot(result.original.index, result.original, label='Original', alpha=0.7)
    axes[0, 0].plot(result.seasonally_adjusted.index, result.seasonally_adjusted, 
                   label='Seasonally Adjusted', linewidth=2)
    axes[0, 0].set_title('GDP: Original vs Seasonally Adjusted')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Trend component
    axes[0, 1].plot(result.trend.index, result.trend, color='green', linewidth=2)
    axes[0, 1].set_title('Trend Component')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Seasonal factors
    axes[1, 0].plot(result.seasonal_factors.index, result.seasonal_factors, color='orange')
    axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 0].set_title('Seasonal Factors')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Annual growth comparison
    years = sa_annual_growth.index[1:]
    sa_values = sa_annual_growth.values[1:]
    orig_values = original_annual_growth.values[1:]
    
    x_pos = np.arange(len(years))
    width = 0.35
    
    axes[1, 1].bar(x_pos - width/2, sa_values, width, label='Seasonally Adjusted', alpha=0.8)
    axes[1, 1].bar(x_pos + width/2, orig_values, width, label='Original', alpha=0.8)
    axes[1, 1].set_title('Annual Growth Rates Comparison')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Growth Rate (%)')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels([str(y.year) for y in years], rotation=45)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/economic_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return result


def scenario_2_retail_sales():
    """
    Scenario 2: Retail Sales Data Analysis
    
    Analyzing monthly retail sales with strong seasonal patterns
    """
    print("\n" + "=" * 60)
    print("SCENARIO 2: Retail Sales Analysis")
    print("=" * 60)
    
    # Create synthetic retail sales data
    np.random.seed(123)
    dates = pd.date_range('2015-01-01', '2024-12-01', freq='ME')
    
    # Base trend with seasonal adjustments
    base_trend = 1000 * (1.03 ** (np.arange(len(dates)) / 12))  # 3% annual growth
    
    # Strong seasonal pattern (retail calendar)
    seasonal_multipliers = [0.85, 0.80, 0.95, 1.00, 1.05, 1.10, 
                           0.90, 0.95, 1.00, 1.05, 1.15, 1.35]  # December peak
    seasonal = []
    for i in range(len(dates)):
        month = dates[i].month
        seasonal.append(base_trend[i] * (seasonal_multipliers[month-1] - 1))
    
    # Random variations and special events
    noise = np.random.normal(0, 20, len(dates))
    
    # Black Friday effects (November boost)
    black_friday_effect = np.where(dates.month == 11, 50, 0)
    
    # Pandemic effect on retail
    pandemic_effect = np.where((dates.year == 2020) & (dates.month.isin([4, 5, 6])), -200, 0)
    
    sales_data = base_trend + seasonal + noise + black_friday_effect + pandemic_effect
    sales_series = pd.Series(sales_data, index=dates, name='Retail_Sales')
    
    print(f"Retail sales data: {len(sales_series)} observations")
    print(f"Average monthly sales: ${sales_series.mean():,.0f}")
    
    # Advanced X13 configuration for retail data
    x13_retail = X13SeasonalAdjustment(
        freq='M',
        transform='auto',
        outlier_detection=True,
        outlier_types=['AO', 'LS', 'TC'],  # All outlier types
        trading_day=True,   # Important for retail
        easter=True,        # Easter effects on retail
        arima_order='auto'
    )
    
    print("\nApplying X13 with trading day and Easter adjustments...")
    retail_result = x13_retail.fit_transform(sales_series)
    
    # Analyze seasonal patterns
    print(f"\nSeasonal Analysis:")
    print(f"Seasonality strength: {retail_result.seasonality_strength:.3f}")
    
    # Monthly seasonal factors
    monthly_factors = {}
    for month in range(1, 13):
        month_mask = retail_result.seasonal_factors.index.month == month
        if month_mask.any():
            monthly_factors[month] = retail_result.seasonal_factors[month_mask].mean()
    
    print("\nAverage Seasonal Factors by Month:")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month, name in enumerate(month_names, 1):
        factor = monthly_factors.get(month, 0)
        print(f"{name}: {factor:+6.1f} ({'boost' if factor > 0 else 'decline'})")
    
    # Year-over-year growth analysis
    print("\nYear-over-Year Growth Analysis:")
    
    # Calculate YoY growth for both original and SA series
    original_yoy = retail_result.original.pct_change(12) * 100
    sa_yoy = retail_result.seasonally_adjusted.pct_change(12) * 100
    
    # Recent years comparison
    recent_data = pd.DataFrame({
        'Original_YoY': original_yoy,
        'SA_YoY': sa_yoy
    }).dropna()
    
    print(f"\nRecent YoY Growth (last 12 months):")
    for date, row in recent_data.tail(12).iterrows():
        print(f"{date.strftime('%Y-%m')}: Original={row['Original_YoY']:+5.1f}%, SA={row['SA_YoY']:+5.1f}%")
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Time series plot
    axes[0, 0].plot(retail_result.original.index, retail_result.original/1000, 
                   label='Original', alpha=0.7)
    axes[0, 0].plot(retail_result.seasonally_adjusted.index, 
                   retail_result.seasonally_adjusted/1000, 
                   label='Seasonally Adjusted', linewidth=2)
    axes[0, 0].set_title('Retail Sales (Thousands $)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Seasonal pattern
    monthly_factors_list = [monthly_factors.get(i, 0) for i in range(1, 13)]
    axes[0, 1].bar(month_names, monthly_factors_list, 
                  color=['red' if x < 0 else 'green' for x in monthly_factors_list])
    axes[0, 1].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    axes[0, 1].set_title('Average Seasonal Factors by Month')
    axes[0, 1].set_ylabel('Seasonal Factor')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].grid(True, alpha=0.3)
    
    # YoY Growth comparison
    recent_months = recent_data.tail(24)
    axes[1, 0].plot(recent_months.index, recent_months['Original_YoY'], 
                   label='Original YoY%', alpha=0.7)
    axes[1, 0].plot(recent_months.index, recent_months['SA_YoY'], 
                   label='SA YoY%', linewidth=2)
    axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 0].set_title('Year-over-Year Growth (Last 24 Months)')
    axes[1, 0].set_ylabel('Growth Rate (%)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Trend analysis
    axes[1, 1].plot(retail_result.trend.index, retail_result.trend/1000, 
                   color='blue', linewidth=2)
    axes[1, 1].set_title('Underlying Trend (Thousands $)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/retail_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return retail_result


def scenario_3_financial_data():
    """
    Scenario 3: Financial Market Data
    
    Analyzing quarterly earnings or financial indicators
    """
    print("\n" + "=" * 60)
    print("SCENARIO 3: Financial Market Analysis")
    print("=" * 60)
    
    # Create synthetic quarterly earnings data
    np.random.seed(456)
    dates = pd.date_range('2010-Q1', '2024-Q4', freq='Q')
    
    # Corporate earnings trend
    base_earnings = 50 * (1.06 ** (np.arange(len(dates)) / 4))  # 6% annual growth
    
    # Quarterly seasonal pattern (typical for many industries)
    quarterly_seasonal = [5, -2, 8, -3]  # Q4 strong, Q2 weak
    seasonal = np.tile(quarterly_seasonal, len(dates) // 4 + 1)[:len(dates)]
    
    # Market volatility and cycles
    noise = np.random.normal(0, 8, len(dates))
    
    # Financial crisis effects
    crisis_2008 = np.where((dates.year == 2008) | (dates.year == 2009), -20, 0)
    covid_2020 = np.where((dates.year == 2020) & (dates.quarter == 2), -25, 0)
    
    earnings_data = base_earnings + seasonal + noise + crisis_2008 + covid_2020
    earnings_series = pd.Series(earnings_data, index=dates, name='Quarterly_Earnings')
    
    print(f"Quarterly earnings data: {len(earnings_series)} observations")
    print(f"Average quarterly earnings: ${earnings_series.mean():.2f}M")
    
    # X13 for quarterly data
    x13_financial = X13SeasonalAdjustment(
        freq='Q',
        transform='log',  # Log transform for financial data
        outlier_detection=True,
        trading_day=False,  # Not relevant for quarterly
        easter=False,
        arima_order='auto'
    )
    
    print("\nApplying X13 to quarterly financial data...")
    financial_result = x13_financial.fit_transform(earnings_series)
    
    # Financial analysis
    print(f"\nFinancial Analysis Results:")
    print(f"Seasonality strength: {financial_result.seasonality_strength:.3f}")
    print(f"Trend strength: {financial_result.trend_strength:.3f}")
    
    # Quarterly seasonal factors
    quarterly_factors = {}
    for quarter in range(1, 5):
        quarter_mask = financial_result.seasonal_factors.index.quarter == quarter
        if quarter_mask.any():
            quarterly_factors[quarter] = financial_result.seasonal_factors[quarter_mask].mean()
    
    print("\nQuarterly Seasonal Factors:")
    for q in range(1, 5):
        factor = quarterly_factors.get(q, 0)
        print(f"Q{q}: {factor:+6.2f}")
    
    # Calculate quarterly growth rates
    quarterly_growth_sa = financial_result.seasonally_adjusted.pct_change() * 100
    quarterly_growth_orig = financial_result.original.pct_change() * 100
    
    print(f"\nRecent Quarterly Growth Rates:")
    for date, sa_growth, orig_growth in zip(
        quarterly_growth_sa.tail(8).index,
        quarterly_growth_sa.tail(8).values,
        quarterly_growth_orig.tail(8).values
    ):
        print(f"{date.strftime('%Y-Q%q')}: SA={sa_growth:+5.1f}%, Original={orig_growth:+5.1f}%")
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Earnings time series
    axes[0, 0].plot(financial_result.original.index, financial_result.original, 
                   label='Original', alpha=0.7, marker='o', markersize=3)
    axes[0, 0].plot(financial_result.seasonally_adjusted.index, 
                   financial_result.seasonally_adjusted, 
                   label='Seasonally Adjusted', linewidth=2, marker='s', markersize=3)
    axes[0, 0].set_title('Quarterly Earnings ($M)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Quarterly seasonal pattern
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    quarterly_factors_list = [quarterly_factors.get(i, 0) for i in range(1, 5)]
    bars = axes[0, 1].bar(quarters, quarterly_factors_list, 
                         color=['red' if x < 0 else 'green' for x in quarterly_factors_list])
    axes[0, 1].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    axes[0, 1].set_title('Quarterly Seasonal Factors')
    axes[0, 1].set_ylabel('Seasonal Factor')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, quarterly_factors_list):
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + (0.1 if height >= 0 else -0.3),
                       f'{value:.2f}', ha='center', va='bottom' if height >= 0 else 'top')
    
    # Growth rates comparison
    recent_growth = pd.DataFrame({
        'SA_Growth': quarterly_growth_sa.tail(16),
        'Original_Growth': quarterly_growth_orig.tail(16)
    }).dropna()
    
    axes[1, 0].plot(recent_growth.index, recent_growth['Original_Growth'], 
                   label='Original QoQ%', alpha=0.7, marker='o')
    axes[1, 0].plot(recent_growth.index, recent_growth['SA_Growth'], 
                   label='SA QoQ%', linewidth=2, marker='s')
    axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 0].set_title('Quarter-over-Quarter Growth (Last 4 Years)')
    axes[1, 0].set_ylabel('Growth Rate (%)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Trend analysis with confidence bands
    trend_line = financial_result.trend
    axes[1, 1].plot(trend_line.index, trend_line, color='blue', linewidth=3, label='Trend')
    
    # Add confidence bands (using irregular component as proxy for uncertainty)
    std_irregular = financial_result.irregular.std()
    upper_band = trend_line + 1.96 * std_irregular
    lower_band = trend_line - 1.96 * std_irregular
    
    axes[1, 1].fill_between(trend_line.index, lower_band, upper_band, 
                           alpha=0.2, color='blue', label='95% Confidence Band')
    axes[1, 1].set_title('Earnings Trend with Confidence Bands')
    axes[1, 1].set_ylabel('Earnings ($M)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/financial_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return financial_result


def scenario_4_model_comparison():
    """
    Scenario 4: Model Comparison and Sensitivity Analysis
    
    Comparing different X13 configurations and ARIMA models
    """
    print("\n" + "=" * 60)
    print("SCENARIO 4: Model Comparison & Sensitivity Analysis")
    print("=" * 60)
    
    # Use retail sales data from scenario 2
    np.random.seed(789)
    dates = pd.date_range('2018-01-01', '2024-12-01', freq='ME')
    
    # Create test data with known properties
    trend = 1000 + 5 * np.arange(len(dates))
    seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
    noise = np.random.normal(0, 10, len(dates))
    
    test_data = trend + seasonal + noise
    test_series = pd.Series(test_data, index=dates, name='Test_Data')
    
    print(f"Test data: {len(test_series)} observations")
    
    # Define different X13 configurations
    configs = {
        'Basic': X13SeasonalAdjustment(freq='M'),
        
        'Advanced': X13SeasonalAdjustment(
            freq='M',
            transform='auto',
            outlier_detection=True,
            trading_day=True,
            easter=True
        ),
        
        'Log Transform': X13SeasonalAdjustment(
            freq='M',
            transform='log',
            outlier_detection=True
        ),
        
        'Conservative': X13SeasonalAdjustment(
            freq='M',
            transform='none',
            outlier_detection=False,
            trading_day=False,
            easter=False
        )
    }
    
    results = {}
    quality_scores = {}
    
    print("\nComparing different X13 configurations...")
    
    for name, x13_config in configs.items():
        print(f"\nTesting configuration: {name}")
        
        try:
            # Fit the model
            result = x13_config.fit_transform(test_series)
            results[name] = result
            
            # Quality assessment
            quality_diag = QualityDiagnostics()
            quality_report = quality_diag.evaluate(result)
            quality_scores[name] = quality_report.summary_scores
            
            print(f"  Seasonality strength: {result.seasonality_strength:.3f}")
            print(f"  Quality score: {quality_report.summary_scores.get('quality_score', 0):.1f}/100")
            print(f"  Overall quality: {quality_report.overall_quality}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            continue
    
    # Compare ARIMA models directly
    print(f"\n{'='*40}")
    print("ARIMA Model Comparison")
    print(f"{'='*40}")
    
    arima_configs = {
        'Auto ARIMA': AutoARIMA(seasonal_period=12, stepwise=True),
        'Conservative ARIMA': AutoARIMA(seasonal_period=12, max_p=2, max_q=2, max_P=1, max_Q=1),
        'Comprehensive ARIMA': AutoARIMA(seasonal_period=12, max_p=5, max_q=5, max_P=2, max_Q=2)
    }
    
    arima_results = {}
    
    for name, arima_config in arima_configs.items():
        print(f"\nTesting ARIMA: {name}")
        
        try:
            arima_config.fit(test_series)
            
            arima_results[name] = {
                'order': arima_config.order_,
                'seasonal_order': arima_config.seasonal_order_,
                'aic': arima_config.aic_,
                'bic': arima_config.bic_
            }
            
            print(f"  Order: {arima_config.order_}")
            print(f"  Seasonal Order: {arima_config.seasonal_order_}")
            print(f"  AIC: {arima_config.aic_:.2f}")
            print(f"  BIC: {arima_config.bic_:.2f}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Forecast comparison
    print(f"\n{'='*40}")
    print("Forecast Comparison")
    print(f"{'='*40}")
    
    forecast_horizon = 12
    forecasts = {}
    
    for name, result in results.items():
        if hasattr(result, 'original'):
            try:
                # Get the fitted X13 model
                x13_model = configs[name]
                if hasattr(x13_model, '_arima_model') and x13_model._arima_model:
                    forecast = x13_model.forecast(steps=forecast_horizon)
                    forecasts[name] = forecast
                    print(f"{name}: {forecast_horizon}-step forecast generated")
                    
            except Exception as e:
                print(f"{name}: Forecast error - {str(e)}")
    
    # Visualization of comparisons
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Seasonally adjusted series comparison
    for name, result in results.items():
        if hasattr(result, 'seasonally_adjusted'):
            axes[0, 0].plot(result.seasonally_adjusted.index, result.seasonally_adjusted, 
                           label=f'{name} SA', alpha=0.8, linewidth=1.5)
    
    axes[0, 0].plot(test_series.index, test_series, 
                   label='Original', color='black', alpha=0.5, linewidth=1)
    axes[0, 0].set_title('Seasonally Adjusted Series Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Quality scores comparison
    config_names = list(quality_scores.keys())
    quality_values = [quality_scores[name].get('quality_score', 0) for name in config_names]
    stability_values = [quality_scores[name].get('stability_score', 0) for name in config_names]
    
    x_pos = np.arange(len(config_names))
    width = 0.35
    
    bars1 = axes[0, 1].bar(x_pos - width/2, quality_values, width, 
                          label='Quality Score', alpha=0.8, color='skyblue')
    bars2 = axes[0, 1].bar(x_pos + width/2, stability_values, width, 
                          label='Stability Score', alpha=0.8, color='lightcoral')
    
    axes[0, 1].set_title('Quality Metrics Comparison')
    axes[0, 1].set_ylabel('Score (0-100)')
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(config_names, rotation=45)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{height:.0f}', ha='center', va='bottom', fontsize=8)
    
    # 3. ARIMA model comparison
    if arima_results:
        arima_names = list(arima_results.keys())
        aic_values = [arima_results[name]['aic'] for name in arima_names]
        bic_values = [arima_results[name]['bic'] for name in arima_names]
        
        x_pos = np.arange(len(arima_names))
        
        axes[1, 0].bar(x_pos - width/2, aic_values, width, label='AIC', alpha=0.8)
        axes[1, 0].bar(x_pos + width/2, bic_values, width, label='BIC', alpha=0.8)
        
        axes[1, 0].set_title('ARIMA Information Criteria Comparison')
        axes[1, 0].set_ylabel('Information Criterion Value')
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(arima_names, rotation=45)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Forecast comparison
    if forecasts:
        # Create future dates for forecasts
        last_date = test_series.index[-1]
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                   periods=forecast_horizon, freq='ME')
        
        # Plot historical data
        axes[1, 1].plot(test_series.tail(24).index, test_series.tail(24), 
                       label='Historical', color='black', linewidth=2)
        
        # Plot forecasts
        colors = ['red', 'blue', 'green', 'orange']
        for i, (name, forecast) in enumerate(forecasts.items()):
            color = colors[i % len(colors)]
            axes[1, 1].plot(future_dates, forecast, 
                           label=f'{name} Forecast', color=color, 
                           linestyle='--', marker='o', markersize=4)
        
        axes[1, 1].axvline(x=last_date, color='gray', linestyle=':', alpha=0.7)
        axes[1, 1].set_title(f'{forecast_horizon}-Month Forecast Comparison')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/model_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Summary recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if quality_scores:
        best_config = max(quality_scores.keys(), 
                         key=lambda x: quality_scores[x].get('quality_score', 0))
        best_score = quality_scores[best_config].get('quality_score', 0)
        
        print(f"Best performing configuration: {best_config}")
        print(f"Quality score: {best_score:.1f}/100")
        
        print(f"\nConfiguration recommendations:")
        print(f"- For high accuracy: Use '{best_config}' configuration")
        print(f"- For robustness: Use 'Conservative' configuration") 
        print(f"- For financial data: Consider 'Log Transform' configuration")
        print(f"- For economic data: Use 'Advanced' configuration with calendar adjustments")
    
    if arima_results:
        best_arima = min(arima_results.keys(), 
                        key=lambda x: arima_results[x]['aic'])
        
        print(f"\nBest ARIMA model: {best_arima}")
        print(f"Model order: {arima_results[best_arima]['order']}")
        print(f"Seasonal order: {arima_results[best_arima]['seasonal_order']}")
    
    return results, quality_scores, arima_results


def main():
    """
    Run all usage scenarios
    """
    print("X13 Seasonal Adjustment - Comprehensive Usage Examples")
    print("Author: Gardash Abbasov")
    print("Package: x13-seasonal-adjustment")
    print("=" * 80)
    
    try:
        # Run all scenarios
        economic_result = scenario_1_economic_data()
        retail_result = scenario_2_retail_sales()
        financial_result = scenario_3_financial_data()
        comparison_results = scenario_4_model_comparison()
        
        print(f"\n{'='*80}")
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")
        
        print(f"\nExample outputs saved to:")
        print(f"- /Users/gardashabbasov/Desktop/x13/examples/economic_analysis.png")
        print(f"- /Users/gardashabbasov/Desktop/x13/examples/retail_analysis.png")
        print(f"- /Users/gardashabbasov/Desktop/x13/examples/financial_analysis.png")
        print(f"- /Users/gardashabbasov/Desktop/x13/examples/model_comparison.png")
        
        print(f"\nPackage performance summary:")
        print(f"- Economic data: Quality = {economic_result.decomposition_quality}")
        print(f"- Retail data: Seasonality strength = {retail_result.seasonality_strength:.3f}")
        print(f"- Financial data: Trend strength = {financial_result.trend_strength:.3f}")
        
        return {
            'economic': economic_result,
            'retail': retail_result,
            'financial': financial_result,
            'comparison': comparison_results
        }
        
    except Exception as e:
        print(f"Error in example execution: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
