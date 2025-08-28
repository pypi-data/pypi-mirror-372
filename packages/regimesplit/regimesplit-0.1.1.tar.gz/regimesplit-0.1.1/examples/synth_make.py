"""Script to create synthetic time series data with distinct regimes."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def create_regime_series_1(n_points: int = 1000) -> pd.Series:
    """Create synthetic time series with 3 distinct regimes.
    
    Args:
        n_points: Number of data points to generate
        
    Returns:
        pandas Series with synthetic time series data
    """
    np.random.seed(42)
    
    # Define regime boundaries
    regime1_end = n_points // 3
    regime2_end = 2 * n_points // 3
    
    # Generate time series with different regimes
    data = np.zeros(n_points)
    
    # Regime 1: Low volatility, trending up
    regime1_trend = np.linspace(0, 2, regime1_end)
    regime1_noise = np.random.normal(0, 0.1, regime1_end)
    data[:regime1_end] = regime1_trend + regime1_noise
    
    # Regime 2: High volatility, mean-reverting
    regime2_base = np.ones(regime2_end - regime1_end) * 2
    regime2_noise = np.random.normal(0, 0.8, regime2_end - regime1_end)
    data[regime1_end:regime2_end] = regime2_base + regime2_noise
    
    # Regime 3: Moderate volatility, trending down
    regime3_trend = np.linspace(2, -1, n_points - regime2_end)
    regime3_noise = np.random.normal(0, 0.3, n_points - regime2_end)
    data[regime2_end:] = regime3_trend + regime3_noise
    
    # Create pandas series with date index
    dates = pd.date_range('2020-01-01', periods=n_points, freq='D')
    series = pd.Series(data, index=dates, name='value')
    
    return series


def create_regime_series_2(n_points: int = 1000) -> pd.Series:
    """Create synthetic time series with 2 distinct regimes (volatility change).
    
    Args:
        n_points: Number of data points to generate
        
    Returns:
        pandas Series with synthetic time series data
    """
    np.random.seed(123)
    
    # Define regime boundary
    regime_change = n_points // 2
    
    # Generate time series
    data = np.zeros(n_points)
    
    # Regime 1: Low volatility around mean of 0
    regime1_noise = np.random.normal(0, 0.2, regime_change)
    data[:regime_change] = regime1_noise
    
    # Regime 2: High volatility around mean of 1
    regime2_base = np.ones(n_points - regime_change) * 1
    regime2_noise = np.random.normal(0, 1.0, n_points - regime_change)
    data[regime_change:] = regime2_base + regime2_noise
    
    # Create pandas series with date index
    dates = pd.date_range('2021-01-01', periods=n_points, freq='h')
    series = pd.Series(data, index=dates, name='value')
    
    return series


def plot_synthetic_series(series1: pd.Series, series2: pd.Series, 
                         output_dir: Path = Path("./output")) -> None:
    """Plot both synthetic series and save to files.
    
    Args:
        series1: First synthetic series
        series2: Second synthetic series
        output_dir: Directory to save plots
    """
    output_dir.mkdir(exist_ok=True)
    
    # Plot series 1
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(series1.index, series1.values, 'b-', alpha=0.7)
    ax1.set_title('Synthetic Time Series 1: Multiple Trend Regimes')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Value')
    ax1.grid(True, alpha=0.3)
    
    # Add regime boundaries for visualization
    regime1_end = len(series1) // 3
    regime2_end = 2 * len(series1) // 3
    ax1.axvline(x=series1.index[regime1_end], color='red', linestyle='--', alpha=0.7, label='Regime Change')
    ax1.axvline(x=series1.index[regime2_end], color='red', linestyle='--', alpha=0.7)
    ax1.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'synthetic_series_1.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot series 2
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(series2.index, series2.values, 'g-', alpha=0.7)
    ax2.set_title('Synthetic Time Series 2: Volatility Regime Change')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Value')
    ax2.grid(True, alpha=0.3)
    
    # Add regime boundary for visualization
    regime_change = len(series2) // 2
    ax2.axvline(x=series2.index[regime_change], color='red', linestyle='--', alpha=0.7, label='Regime Change')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'synthetic_series_2.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Plots saved to {output_dir}/")


def make_series(n: int = 5000, seed: int = 123) -> pd.DataFrame:
    """Generate financial time series with 3 distinct regimes.
    
    Args:
        n: Number of data points to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with columns: price, ret, feature1, feature2
    """
    np.random.seed(seed)
    
    # Create minutely datetime index starting from a base date
    start_date = pd.Timestamp('2023-01-01 09:00:00')
    dates = pd.date_range(start_date, periods=n, freq='min')
    
    # Define regime boundaries
    regime1_end = n // 3
    regime2_end = 2 * n // 3
    
    # Generate log returns for each regime
    returns = np.zeros(n)
    
    # Regime 1: Low volatility (σ=0.02), positive drift (μ=0.0003)
    regime1_returns = np.random.normal(0.0003, 0.02, regime1_end)
    returns[:regime1_end] = regime1_returns
    
    # Regime 2: High volatility (σ=0.08), zero drift (μ=0)
    regime2_returns = np.random.normal(0.0, 0.08, regime2_end - regime1_end)
    returns[regime1_end:regime2_end] = regime2_returns
    
    # Regime 3: Medium volatility (σ=0.04), negative drift (μ=-0.0002)
    regime3_returns = np.random.normal(-0.0002, 0.04, n - regime2_end)
    returns[regime2_end:] = regime3_returns
    
    # Generate price series from returns (starting at 100)
    prices = np.zeros(n)
    prices[0] = 100.0
    for i in range(1, n):
        prices[i] = prices[i-1] * np.exp(returns[i])
    
    # Create DataFrame
    df = pd.DataFrame(index=dates)
    df['price'] = prices
    df['ret'] = returns
    
    # Feature 1: Lagged returns
    df['feature1'] = df['ret'].shift(1)
    
    # Feature 2: Rolling mean of returns (30 periods)
    df['feature2'] = df['ret'].rolling(window=30, min_periods=1).mean()
    
    return df


def main():
    """Main function to generate synthetic data and save to files."""
    # Create output directory
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate new financial series
    print("Generating financial time series with regimes...")
    df = make_series(n=5000, seed=123)
    
    # Save to CSV in examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    df.to_csv(examples_dir / 'series.csv')
    print(f"Financial series saved to {examples_dir / 'series.csv'}")
    
    # Also generate original synthetic series
    print("Generating original synthetic time series...")
    
    series1 = create_regime_series_1(1000)
    series2 = create_regime_series_2(1000)
    
    # Save to CSV files
    series1.to_csv(output_dir / 'synthetic_series_1.csv', header=True)
    series2.to_csv(output_dir / 'synthetic_series_2.csv', header=True)
    
    print(f"Series 1 saved to {output_dir / 'synthetic_series_1.csv'}")
    print(f"Series 2 saved to {output_dir / 'synthetic_series_2.csv'}")
    
    # Create plots
    print("Creating visualization plots...")
    plot_synthetic_series(series1, series2, output_dir)
    
    # Print summary statistics for new financial series
    print("\nFinancial Series Summary:")
    print(f"  Length: {len(df)}")
    print(f"  Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
    print(f"  Returns mean: {df['ret'].mean():.6f}")
    print(f"  Returns std: {df['ret'].std():.6f}")
    print(f"  Index: {df.index[0]} to {df.index[-1]}")
    
    # Print summary statistics for original series
    print("\nSeries 1 Summary:")
    print(f"  Length: {len(series1)}")
    print(f"  Mean: {series1.mean():.3f}")
    print(f"  Std: {series1.std():.3f}")
    print(f"  Min: {series1.min():.3f}")
    print(f"  Max: {series1.max():.3f}")
    
    print("\nSeries 2 Summary:")
    print(f"  Length: {len(series2)}")
    print(f"  Mean: {series2.mean():.3f}")
    print(f"  Std: {series2.std():.3f}")
    print(f"  Min: {series2.min():.3f}")
    print(f"  Max: {series2.max():.3f}")
    
    print("\nSynthetic data generation complete!")


if __name__ == "__main__":
    main()