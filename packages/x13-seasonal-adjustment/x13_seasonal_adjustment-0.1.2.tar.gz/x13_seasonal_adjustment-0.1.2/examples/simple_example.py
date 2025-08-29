"""
X13 Seasonal Adjustment - Simple Usage Example

A straightforward example showing basic usage of the x13-seasonal-adjustment library.
Author: Gardash Abbasov
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import the X13 library
from x13_seasonal_adjustment import X13SeasonalAdjustment, SeasonalityTests


def simple_usage_example():
    """
    Simple example: Monthly sales data analysis
    """
    print("X13 Seasonal Adjustment - Simple Example")
    print("=" * 50)
    
    # Step 1: Create sample monthly data
    print("Step 1: Creating sample monthly sales data...")
    
    # Generate 5 years of monthly data
    dates = pd.date_range('2019-01-01', '2023-12-01', freq='ME')
    
    # Create realistic sales data with trend and seasonality
    np.random.seed(42)
    trend = 1000 + 20 * np.arange(len(dates))  # Growing trend
    seasonal = 100 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)  # Annual cycle
    noise = np.random.normal(0, 50, len(dates))  # Random variation
    
    sales_data = trend + seasonal + noise
    sales = pd.Series(sales_data, index=dates, name='Monthly_Sales')
    
    print(f"Created {len(sales)} months of data")
    print(f"Average monthly sales: ${sales.mean():,.0f}")
    print(f"Data range: {sales.index[0].strftime('%Y-%m')} to {sales.index[-1].strftime('%Y-%m')}")
    
    # Step 2: Test for seasonality
    print("\nStep 2: Testing for seasonality...")
    
    seasonality_tests = SeasonalityTests(seasonal_period=12)
    seasonality_result = seasonality_tests.run_all_tests(sales)
    
    print(f"Seasonality detected: {seasonality_result.has_seasonality}")
    print(f"Confidence level: {seasonality_result.confidence_level:.1%}")
    
    # Step 3: Apply X13 seasonal adjustment
    print("\nStep 3: Applying X13 seasonal adjustment...")
    
    # Create X13 model with default settings
    x13 = X13SeasonalAdjustment(freq='M')
    
    # Fit and transform the data
    result = x13.fit_transform(sales)
    
    print("Seasonal adjustment completed!")
    print(f"Seasonality strength: {result.seasonality_strength:.1%}")
    print(f"Trend strength: {result.trend_strength:.1%}")
    
    # Step 4: Analyze results
    print("\nStep 4: Analyzing results...")
    
    # Calculate some basic statistics
    original_volatility = sales.std()
    adjusted_volatility = result.seasonally_adjusted.std()
    volatility_reduction = (original_volatility - adjusted_volatility) / original_volatility * 100
    
    print(f"Original data volatility: ${original_volatility:,.0f}")
    print(f"Seasonally adjusted volatility: ${adjusted_volatility:,.0f}")
    print(f"Volatility reduction: {volatility_reduction:.1f}%")
    
    # Monthly seasonal factors
    print(f"\nMonthly seasonal patterns:")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month_num in range(1, 13):
        month_mask = result.seasonal_factors.index.month == month_num
        if month_mask.any():
            avg_factor = result.seasonal_factors[month_mask].mean()
            month_name = months[month_num - 1]
            direction = "above" if avg_factor > 0 else "below"
            print(f"{month_name}: ${avg_factor:+,.0f} ({direction} trend)")
    
    # Step 5: Create visualization
    print("\nStep 5: Creating visualization...")
    
    # Create a comprehensive plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Original vs Seasonally Adjusted
    axes[0, 0].plot(sales.index, sales, label='Original Sales', alpha=0.7, linewidth=1)
    axes[0, 0].plot(result.seasonally_adjusted.index, result.seasonally_adjusted, 
                   label='Seasonally Adjusted', linewidth=2, color='red')
    axes[0, 0].set_title('Original vs Seasonally Adjusted Sales')
    axes[0, 0].set_ylabel('Sales ($)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Trend Component
    axes[0, 1].plot(result.trend.index, result.trend, color='green', linewidth=2)
    axes[0, 1].set_title('Underlying Trend')
    axes[0, 1].set_ylabel('Sales ($)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Seasonal Factors
    axes[1, 0].plot(result.seasonal_factors.index, result.seasonal_factors, 
                   color='orange', linewidth=1)
    axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 0].set_title('Seasonal Factors')
    axes[1, 0].set_ylabel('Seasonal Effect ($)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Monthly Seasonal Pattern
    monthly_factors = []
    for month_num in range(1, 13):
        month_mask = result.seasonal_factors.index.month == month_num
        if month_mask.any():
            monthly_factors.append(result.seasonal_factors[month_mask].mean())
        else:
            monthly_factors.append(0)
    
    bars = axes[1, 1].bar(months, monthly_factors, 
                         color=['red' if x < 0 else 'green' for x in monthly_factors])
    axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    axes[1, 1].set_title('Average Monthly Seasonal Factors')
    axes[1, 1].set_ylabel('Seasonal Effect ($)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_factors):
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., 
                       height + (10 if height >= 0 else -20),
                       f'${value:,.0f}', ha='center', 
                       va='bottom' if height >= 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/simple_example_output.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # Step 6: Summary and recommendations
    print("\nStep 6: Summary and Recommendations")
    print("=" * 50)
    
    if result.seasonality_strength > 0.3:
        print("✓ Strong seasonal pattern detected - seasonal adjustment recommended")
    elif result.seasonality_strength > 0.1:
        print("○ Moderate seasonal pattern - seasonal adjustment may be beneficial")
    else:
        print("✗ Weak seasonal pattern - seasonal adjustment may not be necessary")
    
    print(f"\nKey insights:")
    print(f"- The data shows {result.seasonality_strength:.1%} seasonality strength")
    print(f"- Seasonal adjustment reduced volatility by {volatility_reduction:.1f}%")
    
    # Find peak and trough months
    peak_month_idx = np.argmax(monthly_factors)
    trough_month_idx = np.argmin(monthly_factors)
    peak_month = months[peak_month_idx]
    trough_month = months[trough_month_idx]
    
    print(f"- Peak sales month: {peak_month} (${monthly_factors[peak_month_idx]:+,.0f})")
    print(f"- Lowest sales month: {trough_month} (${monthly_factors[trough_month_idx]:+,.0f})")
    
    # Business recommendations
    print(f"\nBusiness recommendations:")
    if monthly_factors[peak_month_idx] > 50:
        print(f"- Prepare extra inventory for {peak_month}")
    if monthly_factors[trough_month_idx] < -50:
        print(f"- Plan promotions or cost reduction for {trough_month}")
    print(f"- Use seasonally adjusted data for trend analysis and forecasting")
    print(f"- Monitor month-to-month changes using seasonally adjusted figures")
    
    return result


def quick_start_example():
    """
    Quick start example with minimal code
    """
    print("\n" + "=" * 50)
    print("QUICK START EXAMPLE")
    print("=" * 50)
    
    # Just 5 lines of code for basic seasonal adjustment!
    dates = pd.date_range('2020-01-01', periods=48, freq='ME')
    data = pd.Series(1000 + 50*np.sin(2*np.pi*np.arange(48)/12) + np.random.randn(48)*20, 
                     index=dates, name='data')
    
    x13 = X13SeasonalAdjustment()
    result = x13.fit_transform(data)
    
    print(f"Original data mean: {data.mean():.1f}")
    print(f"Seasonally adjusted mean: {result.seasonally_adjusted.mean():.1f}")
    print(f"Seasonality strength: {result.seasonality_strength:.1%}")
    
    # Simple plot
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data, label='Original', alpha=0.7)
    plt.plot(result.seasonally_adjusted.index, result.seasonally_adjusted, 
             label='Seasonally Adjusted', linewidth=2)
    plt.title('Quick Start Example')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/gardashabbasov/Desktop/x13/examples/quick_start_output.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    return result


if __name__ == "__main__":
    print("Running X13 Seasonal Adjustment Examples")
    print("Package: x13-seasonal-adjustment")
    print("Author: Gardash Abbasov\n")
    
    # Run simple example
    simple_result = simple_usage_example()
    
    # Run quick start
    quick_result = quick_start_example()
    
    print("\n" + "=" * 50)
    print("EXAMPLES COMPLETED!")
    print("=" * 50)
    print("Output files saved:")
    print("- simple_example_output.png")
    print("- quick_start_output.png")
    print("\nFor more advanced examples, see comprehensive_example.py")
