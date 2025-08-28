"""Utility functions for regimesplit."""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional, Tuple
from pathlib import Path


def load_time_series(file_path: Union[str, Path], 
                    time_column: Optional[str] = None,
                    value_column: Optional[str] = None) -> pd.Series:
    """Load time series data from CSV file.
    
    Args:
        file_path: Path to CSV file
        time_column: Name of time column (optional)
        value_column: Name of value column (optional)
        
    Returns:
        pandas Series with time series data
    """
    # Placeholder implementation
    df = pd.read_csv(file_path)
    
    if value_column and value_column in df.columns:
        series = df[value_column]
    else:
        # Use first numeric column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            series = df[numeric_cols[0]]
        else:
            raise ValueError("No numeric columns found in data")
    
    if time_column and time_column in df.columns:
        series.index = pd.to_datetime(df[time_column])
    
    return series


def validate_time_series(data: pd.Series) -> bool:
    """Validate time series data format.
    
    Args:
        data: Time series data
        
    Returns:
        True if valid, raises ValueError if not
    """
    if not isinstance(data, pd.Series):
        raise ValueError("Data must be a pandas Series")
    
    if data.empty:
        raise ValueError("Data cannot be empty")
    
    if data.isna().all():
        raise ValueError("Data cannot be all NaN values")
    
    return True


def prepare_features(data: pd.Series, 
                    window_sizes: List[int] = [5, 10, 20]) -> pd.DataFrame:
    """Prepare features for regime detection.
    
    Args:
        data: Time series data
        window_sizes: List of window sizes for rolling features
        
    Returns:
        DataFrame with engineered features
    """
    # Placeholder implementation
    features = pd.DataFrame(index=data.index)
    
    # Add original values
    features['value'] = data.values
    
    # Add rolling statistics
    for window in window_sizes:
        features[f'mean_{window}'] = data.rolling(window).mean()
        features[f'std_{window}'] = data.rolling(window).std()
        features[f'min_{window}'] = data.rolling(window).min()
        features[f'max_{window}'] = data.rolling(window).max()
    
    # Add differences
    features['diff_1'] = data.diff()
    features['diff_2'] = data.diff(2)
    
    return features.dropna()


def export_results(regimes: np.ndarray, 
                  change_points: List[int],
                  data: pd.Series,
                  output_path: Union[str, Path]) -> None:
    """Export regime detection results to CSV.
    
    Args:
        regimes: Array of regime labels
        change_points: List of change point indices
        data: Original time series data
        output_path: Path for output file
    """
    # Placeholder implementation
    results_df = pd.DataFrame({
        'timestamp': data.index,
        'value': data.values,
        'regime': regimes
    })
    
    # Add change point indicators
    results_df['is_change_point'] = False
    results_df.loc[change_points, 'is_change_point'] = True
    
    results_df.to_csv(output_path, index=False)
    print(f"Results exported to {output_path}")


def get_regime_statistics(data: pd.Series, regimes: np.ndarray) -> Dict[int, Dict[str, Any]]:
    """Calculate statistics for each regime.
    
    Args:
        data: Time series data
        regimes: Array of regime labels
        
    Returns:
        Dictionary with statistics for each regime
    """
    stats = {}
    
    for regime in np.unique(regimes):
        regime_data = data[regimes == regime]
        stats[regime] = {
            'count': len(regime_data),
            'mean': regime_data.mean(),
            'std': regime_data.std(),
            'min': regime_data.min(),
            'max': regime_data.max(),
            'duration_pct': len(regime_data) / len(data) * 100
        }
    
    return stats


def contiguous_segments(regime_id: pd.Series) -> List[Tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Extract contiguous segments from regime ID series.
    
    Args:
        regime_id: Series with regime labels, indexed by datetime
        
    Returns:
        List of tuples (start_timestamp, end_timestamp, regime_label) for each contiguous segment
        
    Raises:
        ValueError: If regime_id is empty or has no valid values
    """
    if regime_id.empty:
        raise ValueError("regime_id cannot be empty")
    
    # Remove NaN values and sort by index
    clean_regime = regime_id.dropna().sort_index()
    if clean_regime.empty:
        raise ValueError("regime_id has no valid (non-NaN) values")
    
    segments = []
    current_regime = clean_regime.iloc[0]
    segment_start = clean_regime.index[0]
    
    for i in range(1, len(clean_regime)):
        if clean_regime.iloc[i] != current_regime:
            # End current segment
            segment_end = clean_regime.index[i-1]
            segments.append((segment_start, segment_end, int(current_regime)))
            
            # Start new segment
            current_regime = clean_regime.iloc[i]
            segment_start = clean_regime.index[i]
    
    # Add final segment
    segment_end = clean_regime.index[-1]
    segments.append((segment_start, segment_end, int(current_regime)))
    
    return segments


def enforce_min_len(segments: List[Tuple[pd.Timestamp, pd.Timestamp, int]], 
                   min_len: int, 
                   freq: Optional[str], 
                   index: pd.DatetimeIndex) -> List[Tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Merge segments that are too short with neighboring segments.
    
    Args:
        segments: List of (start_ts, end_ts, regime_label) tuples
        min_len: Minimum number of points required for a segment
        freq: Frequency string for the time series (used to calculate segment lengths)
        index: Complete DatetimeIndex to calculate actual segment lengths
        
    Returns:
        List of segments with minimum length enforced
    """
    if not segments:
        return segments
    
    # Calculate segment lengths in number of points
    def get_segment_length(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> int:
        # Find actual positions in the index
        start_idx = index.get_indexer([start_ts], method='nearest')[0]
        end_idx = index.get_indexer([end_ts], method='nearest')[0]
        return end_idx - start_idx + 1
    
    result_segments = []
    i = 0
    
    while i < len(segments):
        start_ts, end_ts, regime_label = segments[i]
        segment_len = get_segment_length(start_ts, end_ts)
        
        if segment_len >= min_len:
            # Segment is long enough, keep it
            result_segments.append((start_ts, end_ts, regime_label))
            i += 1
        else:
            # Segment is too short, merge with neighbor
            if i > 0:
                # Merge with left neighbor (previous segment)
                prev_start, _, prev_label = result_segments.pop()
                merged_segment = (prev_start, end_ts, prev_label)
                result_segments.append(merged_segment)
            elif i + 1 < len(segments):
                # Merge with right neighbor (next segment)
                next_start, next_end, next_label = segments[i + 1]
                merged_segment = (start_ts, next_end, next_label)
                result_segments.append(merged_segment)
                i += 1  # Skip the next segment since we merged it
            else:
                # Only segment, keep it even if short
                result_segments.append((start_ts, end_ts, regime_label))
            i += 1
    
    return result_segments


def segment_bins_for_splits(segments: List[Tuple[pd.Timestamp, pd.Timestamp, int]], 
                           n_splits: int) -> List[List[int]]:
    """Assign segments to bins for balanced splits.
    
    Args:
        segments: List of (start_ts, end_ts, regime_label) tuples
        n_splits: Number of bins to create
        
    Returns:
        List of bins, each containing segment indices
        
    Raises:
        ValueError: If n_splits <= 0 or greater than number of segments
    """
    if n_splits <= 0:
        raise ValueError("n_splits must be positive")
    
    if n_splits > len(segments):
        raise ValueError(f"n_splits ({n_splits}) cannot be greater than number of segments ({len(segments)})")
    
    # Calculate segment lengths (in time units, approximation)
    segment_lengths = []
    for start_ts, end_ts, _ in segments:
        # Use seconds as common unit
        length = (end_ts - start_ts).total_seconds()
        segment_lengths.append(max(1, length))  # Ensure at least 1
    
    # Greedy bin packing: assign each segment to the bin with smallest current total
    bins: List[List[int]] = [[] for _ in range(n_splits)]
    bin_totals = [0.0] * n_splits
    
    # Sort segments by length (descending) for better balance
    sorted_indices = sorted(range(len(segments)), key=lambda i: segment_lengths[i], reverse=True)
    
    for seg_idx in sorted_indices:
        # Find bin with minimum total
        min_bin_idx = min(range(n_splits), key=lambda i: bin_totals[i])
        
        # Assign segment to this bin
        bins[min_bin_idx].append(seg_idx)
        bin_totals[min_bin_idx] += segment_lengths[seg_idx]
    
    # Sort segment indices within each bin to maintain chronological order
    for bin_segments in bins:
        bin_segments.sort()
    
    return bins


def bin_index_ranges(segments: List[Tuple[pd.Timestamp, pd.Timestamp, int]], 
                    bin_indices: List[List[int]], 
                    index: pd.DatetimeIndex) -> List[Tuple[int, int]]:
    """Convert segment bins to global index ranges.
    
    Args:
        segments: List of (start_ts, end_ts, regime_label) tuples
        bin_indices: List of bins, each containing segment indices
        index: Complete DatetimeIndex for the time series
        
    Returns:
        List of (start_index, end_index) tuples for each bin (end_index is exclusive)
        
    Raises:
        ValueError: If bin is empty or segments not found in index
    """
    ranges = []
    
    for bin_segments in bin_indices:
        if not bin_segments:
            raise ValueError("Empty bin found")
        
        # Find global start and end indices for this bin
        bin_start_ts = segments[bin_segments[0]][0]  # Start of first segment
        bin_end_ts = segments[bin_segments[-1]][1]   # End of last segment
        
        # Convert to global indices
        try:
            start_idx = index.get_indexer([bin_start_ts], method='nearest')[0]
            end_idx = index.get_indexer([bin_end_ts], method='nearest')[0]
            
            # Make end_idx exclusive
            ranges.append((start_idx, end_idx + 1))
            
        except (KeyError, IndexError) as e:
            raise ValueError(f"Could not find segment timestamps in index: {e}")
    
    return ranges


# Simple unit tests
def _test_contiguous_segments():
    """Test contiguous_segments function."""
    # Create test data
    dates = pd.date_range('2023-01-01', periods=10, freq='H')
    regime_data = [0, 0, 1, 1, 1, 2, 2, 0, 0, 0]
    regime_series = pd.Series(regime_data, index=dates)
    
    segments = contiguous_segments(regime_series)
    
    # Should have 4 segments: [0,0], [1,1,1], [2,2], [0,0,0]
    assert len(segments) == 4
    assert segments[0][2] == 0  # First segment is regime 0
    assert segments[1][2] == 1  # Second segment is regime 1
    assert segments[2][2] == 2  # Third segment is regime 2
    assert segments[3][2] == 0  # Fourth segment is regime 0
    
    print("✓ contiguous_segments test passed")


def _test_segment_bins_for_splits():
    """Test segment_bins_for_splits function."""
    # Create test segments with different lengths
    start_time = pd.Timestamp('2023-01-01')
    segments = [
        (start_time, start_time + pd.Timedelta(hours=1), 0),  # 1 hour
        (start_time + pd.Timedelta(hours=1), start_time + pd.Timedelta(hours=5), 1),  # 4 hours  
        (start_time + pd.Timedelta(hours=5), start_time + pd.Timedelta(hours=7), 0),  # 2 hours
        (start_time + pd.Timedelta(hours=7), start_time + pd.Timedelta(hours=10), 2), # 3 hours
    ]
    
    bins = segment_bins_for_splits(segments, n_splits=2)
    
    assert len(bins) == 2
    # Each bin should contain some segments
    assert all(len(bin_segs) > 0 for bin_segs in bins)
    # Total segments should be preserved
    total_segments = sum(len(bin_segs) for bin_segs in bins)
    assert total_segments == len(segments)
    
    print("✓ segment_bins_for_splits test passed")


def apply_embargo(test_start_idx: int, embargo: int) -> int:
    """Apply embargo by shifting test start index forward.
    
    Args:
        test_start_idx: Original test start index
        embargo: Number of observations to embargo (skip)
        
    Returns:
        New test start index after applying embargo
    """
    return test_start_idx + embargo


def apply_purge(train_idx: np.ndarray, test_idx: np.ndarray, purge: int) -> Tuple[np.ndarray, np.ndarray]:
    """Apply purge by removing observations from train/test boundaries.
    
    Args:
        train_idx: Training set indices
        test_idx: Test set indices  
        purge: Number of observations to purge from boundaries
        
    Returns:
        Tuple of (purged_train_idx, purged_test_idx) as sorted unique arrays
    """
    if purge <= 0:
        # No purging needed, just ensure sorted and unique
        return np.unique(train_idx), np.unique(test_idx)
    
    # Remove last `purge` indices from train
    if len(train_idx) > purge:
        train_purged = train_idx[:-purge]
    else:
        train_purged = np.array([], dtype=train_idx.dtype)
    
    # Remove first `purge` indices from test
    if len(test_idx) > purge:
        test_purged = test_idx[purge:]
    else:
        test_purged = np.array([], dtype=test_idx.dtype)
    
    # Return sorted unique arrays
    return np.unique(train_purged), np.unique(test_purged)


# Simple unit tests
def _test_apply_embargo():
    """Test apply_embargo function."""
    assert apply_embargo(100, 10) == 110
    assert apply_embargo(50, 0) == 50
    assert apply_embargo(0, 5) == 5
    print("✓ apply_embargo test passed")


def _test_apply_purge():
    """Test apply_purge function."""
    train_idx = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    test_idx = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    
    # Test with purge=3
    train_purged, test_purged = apply_purge(train_idx, test_idx, purge=3)
    
    expected_train = np.array([0, 1, 2, 3, 4, 5, 6])  # Remove last 3
    expected_test = np.array([13, 14, 15, 16, 17, 18, 19])  # Remove first 3
    
    assert np.array_equal(train_purged, expected_train)
    assert np.array_equal(test_purged, expected_test)
    
    # Test with no purge
    train_no_purge, test_no_purge = apply_purge(train_idx, test_idx, purge=0)
    assert np.array_equal(train_no_purge, train_idx)
    assert np.array_equal(test_no_purge, test_idx)
    
    # Test with excessive purge
    train_excess, test_excess = apply_purge(train_idx[:2], test_idx[:2], purge=5)
    assert len(train_excess) == 0
    assert len(test_excess) == 0
    
    print("✓ apply_purge test passed")


if __name__ == "__main__":
    # Run simple tests
    _test_contiguous_segments()
    _test_segment_bins_for_splits()
    _test_apply_embargo()
    _test_apply_purge()
    print("✓ All utility function tests passed!")