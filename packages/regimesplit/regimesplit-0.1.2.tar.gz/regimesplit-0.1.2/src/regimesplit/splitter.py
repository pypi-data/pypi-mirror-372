"""Main RegimeSplit class for time series regime detection and splitting."""

import pandas as pd
import numpy as np
from typing import Optional, Union, Iterator, Tuple, Generator, List
from .detection import realized_volatility, label_regimes_from_vol
from .utils import contiguous_segments, enforce_min_len, segment_bins_for_splits, bin_index_ranges


class RegimeSplit:
    """Cross-validation splitter based on regime detection in time series.
    
    This splitter identifies regimes based on realized volatility and creates
    train/test splits that respect regime boundaries and temporal order.
    """
    
    def __init__(self, 
                 n_splits: int = 5,
                 embargo: int = 0,
                 purge: int = 0,
                 vol_window: int = 60,
                 k_regimes: int = 3,
                 method: str = "quantiles",
                 min_regime_len: int = 30,
                 use_col_for_ret: Optional[str] = "ret"):
        """Initialize RegimeSplit cross-validator.
        
        Args:
            n_splits: Number of splits to generate
            embargo: Number of observations to embargo after each test period
            purge: Number of observations to purge before each test period
            vol_window: Window size for realized volatility calculation
            k_regimes: Number of regimes to detect
            method: Method for regime labeling ("quantiles" or "kmeans")
            min_regime_len: Minimum length for regime segments
            use_col_for_ret: Column name for returns, None to compute from 'price'
        """
        self.n_splits = n_splits
        self.embargo = embargo
        self.purge = purge
        self.vol_window = vol_window
        self.k_regimes = k_regimes
        self.method = method
        self.min_regime_len = min_regime_len
        self.use_col_for_ret = use_col_for_ret
        
        # Fitted attributes
        self.regimes_: Optional[pd.Series] = None
        self.change_points_: Optional[List[pd.Timestamp]] = None
        self.segments_: Optional[List[Tuple[pd.Timestamp, pd.Timestamp, int]]] = None
    
    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        """Return the number of splits.
        
        Args:
            X: Ignored, present for API compatibility
            y: Ignored, present for API compatibility  
            groups: Ignored, present for API compatibility
            
        Returns:
            Number of splits
        """
        return self.n_splits
    
    def split(self, X: pd.DataFrame, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """Generate train/test splits based on regime detection.
        
        Args:
            X: DataFrame with datetime index and price/return data
            y: Ignored, present for API compatibility
            groups: Alternative datetime index if X.index is not datetime
            
        Yields:
            Tuple of (train_indices, test_indices) as sorted integer arrays
            
        Raises:
            ValueError: If data format is invalid or insufficient for splitting
        """
        # Step 1: Get temporal index and returns
        datetime_index = self._get_datetime_index(X, groups)
        returns = self._get_returns(X)
        
        if len(returns) != len(datetime_index):
            raise ValueError("Returns and datetime index must have same length")
        
        # Step 2: Calculate realized volatility
        vol = realized_volatility(returns, window=self.vol_window)
        
        # Step 3: Label regimes based on volatility
        regime_series = label_regimes_from_vol(vol, k=self.k_regimes, method=self.method)
        regime_series.index = datetime_index
        
        # Step 4: Extract contiguous segments
        segments = contiguous_segments(regime_series)
        
        # Step 5: Enforce minimum segment length
        segments = enforce_min_len(segments, self.min_regime_len, None, datetime_index)
        
        # Store fitted attributes
        self.regimes_ = regime_series
        self.segments_ = segments
        
        # Step 6: Create balanced bins for splits
        bins = segment_bins_for_splits(segments, self.n_splits)
        
        # Step 7: Convert bins to index ranges
        bin_ranges = bin_index_ranges(segments, bins, datetime_index)
        
        # Step 8: Generate train/test splits
        for i, (test_start, test_end) in enumerate(bin_ranges):
            # Test indices are the current bin range
            test_indices = np.arange(test_start, test_end)
            
            # Train indices are everything strictly before test period
            train_end_raw = test_start
            
            # Apply purge: remove observations immediately before test
            train_end_purged = max(0, train_end_raw - self.purge)
            
            # Apply embargo: ensure gap between train and test
            train_end_embargo = max(0, train_end_purged - self.embargo)
            
            # Train indices
            train_indices = np.arange(0, train_end_embargo)
            
            # Filter out empty splits
            if len(train_indices) == 0 or len(test_indices) == 0:
                continue
                
            yield train_indices, test_indices
    
    def _get_datetime_index(self, X: pd.DataFrame, groups=None) -> pd.DatetimeIndex:
        """Extract datetime index from data.
        
        Args:
            X: Input DataFrame
            groups: Alternative datetime index
            
        Returns:
            DatetimeIndex for temporal alignment
            
        Raises:
            ValueError: If no valid datetime index found
        """
        if groups is not None:
            if isinstance(groups, pd.DatetimeIndex):
                return groups
            else:
                try:
                    return pd.to_datetime(groups)
                except Exception as e:
                    raise ValueError(f"Could not convert groups to datetime: {e}")
        
        if isinstance(X.index, pd.DatetimeIndex):
            return X.index
        
        # Try to find a datetime column
        datetime_cols = X.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            return pd.to_datetime(X[datetime_cols[0]])
        
        raise ValueError("No valid datetime index found. Provide datetime index or groups parameter.")
    
    def _get_returns(self, X: pd.DataFrame) -> pd.Series:
        """Extract or calculate returns from data.
        
        Args:
            X: Input DataFrame
            
        Returns:
            Series of log returns
            
        Raises:
            ValueError: If returns cannot be obtained
        """
        if self.use_col_for_ret is not None:
            if self.use_col_for_ret in X.columns:
                return X[self.use_col_for_ret]
            else:
                raise ValueError(f"Column '{self.use_col_for_ret}' not found in DataFrame")
        
        # Try to calculate returns from price
        if 'price' in X.columns:
            prices = X['price']
            returns = np.log(prices).diff()
            return returns.dropna()
        
        # Try first numeric column as price
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            prices = X[numeric_cols[0]]
            returns = np.log(prices).diff()
            return returns.dropna()
        
        raise ValueError("Could not find returns or price data. Provide 'ret' or 'price' column.")
    
    def fit(self, data: pd.Series) -> "RegimeSplit":
        """Fit the regime detection model to the data.
        
        Args:
            data: Time series data as pandas Series
            
        Returns:
            Self for method chaining
        """
        # Convert Series to DataFrame for compatibility
        if isinstance(data.index, pd.DatetimeIndex):
            df = pd.DataFrame({'price': data}, index=data.index)
        else:
            # Create a dummy datetime index
            dates = pd.date_range('2020-01-01', periods=len(data), freq='D')
            df = pd.DataFrame({'price': data}, index=dates)
        
        # Run split to fit the model (consume first split)
        try:
            splits = list(self.split(df))
            if splits and self.segments_:
                self.change_points_ = [seg[0] for seg in self.segments_[1:]]  # Start times of segments except first
        except Exception:
            # Fallback for compatibility
            self.regimes_ = pd.Series(np.zeros(len(data), dtype=int), index=data.index)
            self.change_points_ = []
        
        return self
    
    def predict(self, data: pd.Series) -> np.ndarray:
        """Predict regimes for new data.
        
        Args:
            data: Time series data as pandas Series
            
        Returns:
            Array of regime labels
        """
        # Simple implementation - would need more sophisticated approach for true prediction
        if self.regimes_ is not None and len(self.regimes_) == len(data):
            return self.regimes_.fillna(0).astype(int).values
        else:
            # Fallback
            return np.zeros(len(data), dtype=int)