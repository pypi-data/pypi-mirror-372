"""Regime detection algorithms."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import List, Tuple, Optional


def detect_change_points_basic(data: pd.Series, 
                              window_size: int = 20,
                              threshold: float = 2.0) -> List[int]:
    """Basic change point detection using rolling statistics.
    
    Args:
        data: Time series data
        window_size: Size of rolling window for statistics
        threshold: Threshold for change point detection
        
    Returns:
        List of change point indices
    """
    # Placeholder implementation
    change_points = []
    
    # Calculate rolling mean and std
    rolling_mean = data.rolling(window=window_size).mean()
    rolling_std = data.rolling(window=window_size).std()
    
    # Simple change detection based on standard deviation changes
    for i in range(window_size, len(data) - window_size):
        if rolling_std.iloc[i] > threshold * rolling_std.iloc[i-1]:
            change_points.append(i)
    
    return change_points


def cluster_regimes(data: pd.Series, 
                   n_clusters: int = 2,
                   features: Optional[List[str]] = None) -> np.ndarray:
    """Cluster data points into regimes using K-means.
    
    Args:
        data: Time series data
        n_clusters: Number of regimes to detect
        features: List of features to use for clustering
        
    Returns:
        Array of regime labels
    """
    # Placeholder implementation using simple value-based clustering
    X = data.values.reshape(-1, 1)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    regimes = kmeans.fit_predict(X)
    
    return regimes


def detect_regime_changes(data: pd.Series,
                         method: str = "basic",
                         **kwargs) -> Tuple[np.ndarray, List[int]]:
    """Detect regime changes in time series data.
    
    Args:
        data: Time series data
        method: Detection method ("basic", "clustering", etc.)
        **kwargs: Method-specific parameters
        
    Returns:
        Tuple of (regime_labels, change_points)
    """
    if method == "basic":
        change_points = detect_change_points_basic(data, **kwargs)
        # Simple regime assignment based on change points
        regimes = np.zeros(len(data), dtype=int)
        for i, cp in enumerate(change_points):
            if i + 1 < len(change_points):
                regimes[cp:change_points[i+1]] = i + 1
            else:
                regimes[cp:] = i + 1
                
    elif method == "clustering":
        regimes = cluster_regimes(data, **kwargs)
        # Derive change points from regime changes
        change_points = []
        for i in range(1, len(regimes)):
            if regimes[i] != regimes[i-1]:
                change_points.append(i)
                
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return regimes, change_points


def realized_volatility(ret: pd.Series, window: int = 60) -> pd.Series:
    """Calculate realized volatility using rolling standard deviation.
    
    Computes the rolling standard deviation of returns over a specified window,
    which serves as a proxy for realized volatility. This measure captures
    the time-varying volatility structure that forms the basis for regime detection.
    
    The function uses pandas rolling window with min_periods set to half the window
    size to ensure reasonable volatility estimates even at the beginning of the series.
    
    Args:
        ret: Return series (typically log returns) with datetime index
        window: Rolling window size for volatility calculation. Larger windows
               provide smoother volatility estimates but with more lag.
        
    Returns:
        Series of realized volatility aligned to original index. Values will be
        NaN for the first min_periods observations.
        
    Raises:
        ValueError: If return series has >90% NaN values, making volatility
                   estimation unreliable
                   
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> returns = pd.Series(np.random.normal(0, 0.02, 100))
        >>> vol = realized_volatility(returns, window=20)
        >>> print(f"Average volatility: {vol.mean():.4f}")
    """
    if ret.isna().sum() / len(ret) > 0.9:
        raise ValueError("Return series has too many NaN values (>90%)")
    
    min_periods = max(1, window // 2)
    vol = ret.rolling(window=window, min_periods=min_periods).std()
    
    return vol


def label_regimes_from_vol(vol: pd.Series, k: int = 3, method: str = "quantiles") -> pd.Series:
    """Label regimes based on volatility levels using quantiles or clustering.
    
    This function identifies distinct volatility regimes by partitioning the 
    volatility distribution. Two methods are supported:
    
    1. "quantiles": Uses empirical quantiles to create k equal-sized regimes
       based on volatility ranking. This ensures balanced regime sizes but
       may not capture natural clustering in volatility space.
       
    2. "kmeans": Uses K-means clustering to identify k volatility clusters
       based on actual volatility values. This captures natural groupings
       but regime sizes may be unbalanced.
    
    Args:
        vol: Volatility series (output from realized_volatility function)
             with datetime index
        k: Number of regimes to identify (typically 2-5 for financial data)
        method: Regime detection method:
               - "quantiles": Empirical quantile-based partitioning
               - "kmeans": K-means clustering approach
        
    Returns:
        Series of regime labels (integers 0 to k-1) aligned to original index.
        NaN values in original volatility series remain NaN in output.
        
    Raises:
        ValueError: If method is not "quantiles" or "kmeans", or if insufficient
                   non-NaN values (<10% of series or fewer than k observations)
                   
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> vol = pd.Series(np.random.lognormal(0, 0.5, 1000))
        >>> regimes = label_regimes_from_vol(vol, k=3, method="quantiles")
        >>> print(regimes.value_counts())
    """
    if method not in {"quantiles", "kmeans"}:
        raise ValueError(f"Unknown method: {method}. Must be 'quantiles' or 'kmeans'")
    
    # Check for sufficient non-NaN values
    vol_clean = vol.dropna()
    if len(vol_clean) < k:
        raise ValueError(f"Insufficient non-NaN values ({len(vol_clean)}) for {k} regimes")
    
    if len(vol_clean) / len(vol) < 0.1:
        raise ValueError("Volatility series has too many NaN values (>90%)")
    
    if method == "quantiles":
        # Use quantile-based labeling
        regime_labels = pd.qcut(vol_clean, q=k, labels=range(k), duplicates='drop')
        # Reindex to original series index, filling NaN where original vol was NaN
        regimes = regime_labels.reindex(vol.index)
        
    elif method == "kmeans":
        # Use K-means clustering
        vol_filled = vol.fillna(vol.median())
        X = vol_filled.values.reshape(-1, 1)
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        # Create series aligned to original index
        regimes = pd.Series(cluster_labels, index=vol.index, dtype='Int64')
        
        # Set NaN where original volatility was NaN
        regimes[vol.isna()] = pd.NA
    
    regimes.name = 'regime_id'
    return regimes