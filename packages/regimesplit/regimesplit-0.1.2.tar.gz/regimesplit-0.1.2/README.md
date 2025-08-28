# RegimeSplit

A volatility/regime-aware cross-validation splitter for financial time-series ML backtests.  
Prevents leakage by **never splitting across regime boundaries**, with built-in **embargo & purge**.  
Includes CLI tools, HTML reports, and sklearn compatibility.

[![PyPI version](https://img.shields.io/pypi/v/regimesplit.svg)](https://pypi.org/project/regimesplit/)
[![Python versions](https://img.shields.io/pypi/pyversions/regimesplit.svg)](https://pypi.org/project/regimesplit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/regimesplit)](https://pepy.tech/project/regimesplit)

## Install
```bash
pip install -e .
```

## Quick Example

```python
import pandas as pd
from regimesplit import RegimeSplit

df = pd.read_csv("examples/series.csv", parse_dates=[0], index_col=0)
rs = RegimeSplit(n_splits=5, embargo=15, purge=5, vol_window=60, k_regimes=3, method="quantiles")
for i, (tr, te) in enumerate(rs.split(df)):
    print(i, len(tr), len(te), df.index[tr[0]], df.index[te[0]])
```

## CLI Usage
```bash
regimesplit folds --csv examples/series.csv --ret-col ret --n-splits 5 --embargo 15 --purge 5 --vol-window 60 --k 3 --method quantiles --out out/
```

## Features

- ** Regime-Aware Splitting**: Detects volatility regimes and never splits within regime segments
- ** Temporal Constraints**: Built-in embargo and purge to prevent look-ahead bias
- ** Multiple Detection Methods**: Quantile-based and K-means clustering for regime identification
- ** Realized Volatility**: Uses rolling standard deviation for regime detection
- ** Rich Visualization**: Timeline plots showing regimes and train/test splits
- ** HTML Reports**: Professional reports with interactive visualizations
- ** CLI Interface**: Easy-to-use command-line tools for analysis
- ** sklearn Compatible**: Drop-in replacement for standard cross-validation

## For Hiring Managers

Use-case: Validating ML models for financial time series.
- Prevents regime leakage across folds
- Embargo & purge ensure realistic OOS tests
- sklearn-compatible for plug-and-play integration

**CV Snippet:**
> Built RegimeSplit: a volatility/regime-aware CV splitter for financial ML backtesting (sklearn-compatible, embargo/purge, CLI + HTML reports).


## Quick Start

### Cross-Validation for ML Backtesting

```python
import pandas as pd
from regimesplit import RegimeSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Load financial data with datetime index
df = pd.read_csv('financial_data.csv', index_col=0, parse_dates=True)
# Columns: 'price', 'ret', 'feature1', 'feature2', etc.

# Initialize regime-aware splitter
splitter = RegimeSplit(
    n_splits=5,           # Number of CV folds
    embargo=24,           # 24-hour embargo period
    purge=12,            # 12-hour purge period  
    vol_window=60,       # 60-period volatility window
    k_regimes=3,         # Detect 3 volatility regimes
    method="quantiles"   # Use quantile-based regime detection
)

# Prepare features and target
X = df[['feature1', 'feature2', 'feature3']]
y = df['ret'].shift(-1).dropna()  # Next period return
X = X.iloc[:-1]  # Align with y

# Cross-validate with regime-aware splits
model = RandomForestRegressor(n_estimators=100)
scores = cross_val_score(model, X, y, cv=splitter, scoring='neg_mean_squared_error')

print(f"CV Scores: {scores}")
print(f"Mean CV Score: {scores.mean():.4f} ± {scores.std():.4f}")
```

### Command Line Interface

```bash
# Generate cross-validation folds
regimesplit folds data/prices.csv --ret-col returns --n-splits 5 --embargo 24 --purge 12

# Create HTML report with timeline visualization  
regimesplit report output/folds.json output/regimes.csv --output-dir reports/

# Generate synthetic test data
python examples/synth_make.py
```

### Generate Synthetic Data

Create realistic financial time series with regime changes:

```python
from examples.synth_make import make_series

# Generate 5000 observations with 3 volatility regimes
df = make_series(n=5000, seed=123)
# Returns DataFrame with columns: 'price', 'ret', 'feature1', 'feature2'

print(f"Generated {len(df)} observations")
print(f"Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
```

## API Reference

### Main Classes

#### `RegimeSplit(n_splits=5, embargo=0, purge=0, vol_window=60, k_regimes=3, method="quantiles", min_regime_len=30)`
**sklearn-compatible cross-validator** for regime-aware time series splitting.

**Parameters:**
- `n_splits`: Number of cross-validation folds
- `embargo`: Observations to skip after each test period (prevent leakage)
- `purge`: Observations to remove before each test period  
- `vol_window`: Rolling window for realized volatility calculation
- `k_regimes`: Number of volatility regimes to detect
- `method`: Regime detection method ("quantiles" or "kmeans")
- `min_regime_len`: Minimum length for regime segments (shorter ones merged)

**Methods:**
- `split(X, y=None, groups=None)`: Generate (train_idx, test_idx) tuples
- `get_n_splits()`: Return number of splits

### Detection Functions

#### `realized_volatility(ret, window=60)`
Calculate realized volatility using rolling standard deviation.

#### `label_regimes_from_vol(vol, k=3, method="quantiles")`
Label volatility regimes using quantiles or K-means clustering.

#### `contiguous_segments(regime_id)`  
Extract contiguous regime segments with start/end timestamps.

#### `enforce_min_len(segments, min_len, freq, index)`
Merge segments shorter than minimum length with neighbors.

### Visualization

#### `plot_regimes(data, regimes, change_points=None)`
Plot time series with regime coloring and change points.

#### `plot_timeline(index, regime_id, folds, path_png)`
**Timeline visualization** showing regimes and cross-validation splits.

### Utilities

#### `apply_embargo(test_start_idx, embargo)` 
Apply embargo by shifting test start forward.

#### `apply_purge(train_idx, test_idx, purge)`
Remove observations from train/test boundaries.

## Examples

### Example 1: Financial Backtesting Pipeline

```python
import pandas as pd
import numpy as np
from regimesplit import RegimeSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load or generate financial data
from examples.synth_make import make_series
df = make_series(n=2000, seed=42)

# Prepare features and target
features = ['feature1', 'feature2'] 
X = df[features].dropna()
y = df['ret'].shift(-1).dropna()  # Predict next return
X = X.iloc[:-1]  # Align indices

# Initialize regime-aware cross-validator
cv = RegimeSplit(
    n_splits=5,
    embargo=12,      # 12-period embargo
    purge=6,         # 6-period purge
    vol_window=48,   # 48-period volatility window
    k_regimes=3,
    method="quantiles"
)

# Train/test with proper temporal validation
model = RandomForestRegressor(n_estimators=50, random_state=42)
oos_predictions = []
oos_actuals = []

for train_idx, test_idx in cv.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    oos_predictions.extend(y_pred)
    oos_actuals.extend(y_test)

# Evaluate out-of-sample performance
oos_mse = mean_squared_error(oos_actuals, oos_predictions)
print(f"Out-of-sample MSE: {oos_mse:.6f}")
```

### Example 2: CLI Workflow

```bash
# Step 1: Generate synthetic data
python examples/synth_make.py

# Step 2: Create cross-validation folds
regimesplit folds examples/series.csv \
  --ret-col ret \
  --n-splits 5 \
  --embargo 24 \
  --purge 12 \
  --vol-window 60 \
  --k-regimes 3 \
  --method quantiles \
  --output-dir results/

# Step 3: Generate professional HTML report  
regimesplit report \
  results/folds.json \
  results/regimes.csv \
  --output-dir reports/

# Open report in browser
open reports/folds_report.html
```

### Example 3: Custom Regime Analysis

```python
from regimesplit.detection import realized_volatility, label_regimes_from_vol
from regimesplit.utils import contiguous_segments
from regimesplit.plotting import plot_timeline

# Load data
df = pd.read_csv('your_data.csv', index_col=0, parse_dates=True)
returns = df['ret']

# Step-by-step regime detection
vol = realized_volatility(returns, window=60)
regime_labels = label_regimes_from_vol(vol, k=3, method="quantiles")
segments = contiguous_segments(regime_labels)

print(f"Detected {len(segments)} regime segments:")
for start_ts, end_ts, regime_id in segments[:5]:
    duration = end_ts - start_ts
    print(f"  Regime {regime_id}: {start_ts} to {end_ts} ({duration})")
```

## Development

### Setup Development Environment

```bash
make venv          # Create virtual environment
make install       # Install package in development mode  
```

### Run Tests

```bash
make test          # Run test suite
```

### Create Demo

```bash
make demo          # Run synthetic data generation demo
```

## Project Structure

```
regimesplit/
├── src/regimesplit/
│   ├── __init__.py          # Package initialization
│   ├── splitter.py          # Main RegimeSplit class
│   ├── cli.py              # Command-line interface
│   ├── detection.py        # Detection algorithms
│   ├── plotting.py         # Visualization functions
│   ├── utils.py            # Utility functions
│   └── report.py           # HTML report generation
├── examples/
│   └── synth_make.py       # Synthetic data generation
├── tests/
│   └── test_basic.py       # Basic test suite
├── pyproject.toml          # Project configuration
├── README.md              # This file
├── LICENSE                # MIT License
└── Makefile               # Development commands
```

## Requirements

- Python ≥ 3.8
- pandas
- numpy  
- scikit-learn
- matplotlib
- tyro
- jinja2
- pytest

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Why RegimeSplit?

**Traditional time series cross-validation problems:**
- ❌ **KFold**: Ignores temporal order, causes severe data leakage
- ❌ **TimeSeriesSplit**: Creates arbitrary splits that may cut through regime changes
- ❌ **Standard methods**: No consideration of market regime shifts

**RegimeSplit advantages:**
- ✅ **Regime-aware**: Never splits within homogeneous volatility periods
- ✅ **Realistic backtesting**: Mimics real trading constraints with embargo/purge
- ✅ **No look-ahead bias**: Strict temporal ordering with customizable gaps
- ✅ **sklearn compatible**: Drop-in replacement for existing CV workflows

**Perfect for:**
- 🏦 **Financial ML**: Trading strategy backtesting and model validation
- 📈 **Quantitative research**: Regime-aware performance evaluation  
- 🔬 **Academic studies**: Robust cross-validation for financial time series
- ⚡ **Production systems**: Realistic out-of-sample testing

## Roadmap

- [ ] **Advanced detection**: PELT, Binary Segmentation, Hidden Markov Models
- [ ] **Multivariate regimes**: Correlation-based and PCA regime detection  
- [ ] **Online detection**: Streaming regime identification for live trading
- [ ] **Statistical testing**: Regime change significance and stability tests
- [ ] **Enhanced visualization**: Interactive plots and regime diagnostics
- [ ] **Performance optimization**: Cython implementation for large datasets
- [ ] **Integration**: Native support for popular trading frameworks