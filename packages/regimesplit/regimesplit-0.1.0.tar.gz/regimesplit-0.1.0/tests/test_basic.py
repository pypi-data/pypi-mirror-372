"""Basic tests for regimesplit package."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from regimesplit import RegimeSplit
from regimesplit.splitter import RegimeSplit as SplitterClass
from regimesplit.detection import detect_change_points_basic, cluster_regimes, detect_regime_changes
from regimesplit.utils import validate_time_series, prepare_features, get_regime_statistics
from regimesplit.plotting import plot_regimes, plot_regime_summary


class TestRegimeSplit:
    """Test cases for the main RegimeSplit class."""
    
    def test_regimesplit_import(self):
        """Test that RegimeSplit can be imported from main package."""
        assert RegimeSplit is not None
        assert RegimeSplit == SplitterClass
    
    def test_regimesplit_init(self):
        """Test RegimeSplit initialization."""
        model = RegimeSplit()
        assert model.regimes_ is None
        assert model.change_points_ is None
    
    def test_regimesplit_fit(self):
        """Test RegimeSplit fit method with dummy data."""
        data = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1])
        model = RegimeSplit()
        
        result = model.fit(data)
        
        # Should return self for method chaining
        assert result is model
        
        # Should set attributes (placeholder implementation)
        assert model.regimes_ is not None
        assert model.change_points_ is not None
        assert len(model.regimes_) == len(data)
    
    def test_regimesplit_predict(self):
        """Test RegimeSplit predict method."""
        train_data = pd.Series([1, 2, 3, 4, 5])
        test_data = pd.Series([6, 7, 8])
        
        model = RegimeSplit()
        model.fit(train_data)
        
        predictions = model.predict(test_data)
        
        assert len(predictions) == len(test_data)
        assert isinstance(predictions, np.ndarray)


class TestDetection:
    """Test cases for detection algorithms."""
    
    def test_detect_change_points_basic(self):
        """Test basic change point detection."""
        # Create simple time series with obvious change
        data = pd.Series([1] * 50 + [10] * 50)
        
        change_points = detect_change_points_basic(data, window_size=10, threshold=2.0)
        
        assert isinstance(change_points, list)
        # Should detect some change points (implementation dependent)
    
    def test_cluster_regimes(self):
        """Test regime clustering."""
        # Create data with two clear clusters
        data = pd.Series([1] * 25 + [10] * 25)
        
        regimes = cluster_regimes(data, n_clusters=2)
        
        assert len(regimes) == len(data)
        assert len(np.unique(regimes)) <= 2  # Should have at most 2 regimes
    
    def test_detect_regime_changes(self):
        """Test regime change detection."""
        data = pd.Series([1, 1, 1, 5, 5, 5, 1, 1, 1])
        
        regimes, change_points = detect_regime_changes(data, method="clustering", n_clusters=2)
        
        assert len(regimes) == len(data)
        assert isinstance(change_points, list)
    
    def test_detect_regime_changes_invalid_method(self):
        """Test detection with invalid method."""
        data = pd.Series([1, 2, 3])
        
        with pytest.raises(ValueError):
            detect_regime_changes(data, method="invalid_method")


class TestUtils:
    """Test cases for utility functions."""
    
    def test_validate_time_series_valid(self):
        """Test validation with valid time series."""
        data = pd.Series([1, 2, 3, 4, 5])
        assert validate_time_series(data) is True
    
    def test_validate_time_series_not_series(self):
        """Test validation with non-Series input."""
        data = [1, 2, 3, 4, 5]
        
        with pytest.raises(ValueError, match="Data must be a pandas Series"):
            validate_time_series(data)
    
    def test_validate_time_series_empty(self):
        """Test validation with empty Series."""
        data = pd.Series([])
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            validate_time_series(data)
    
    def test_validate_time_series_all_nan(self):
        """Test validation with all NaN Series."""
        data = pd.Series([np.nan, np.nan, np.nan])
        
        with pytest.raises(ValueError, match="Data cannot be all NaN values"):
            validate_time_series(data)
    
    def test_prepare_features(self):
        """Test feature preparation."""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 5)
        
        features = prepare_features(data, window_sizes=[5, 10])
        
        assert isinstance(features, pd.DataFrame)
        assert 'value' in features.columns
        assert 'mean_5' in features.columns
        assert 'mean_10' in features.columns
        assert 'diff_1' in features.columns
        
        # Should have fewer rows due to rolling windows and dropna
        assert len(features) < len(data)
    
    def test_get_regime_statistics(self):
        """Test regime statistics calculation."""
        data = pd.Series([1, 1, 1, 5, 5, 5])
        regimes = np.array([0, 0, 0, 1, 1, 1])
        
        stats = get_regime_statistics(data, regimes)
        
        assert isinstance(stats, dict)
        assert 0 in stats
        assert 1 in stats
        
        # Check regime 0 stats
        assert stats[0]['count'] == 3
        assert stats[0]['mean'] == 1.0
        
        # Check regime 1 stats
        assert stats[1]['count'] == 3
        assert stats[1]['mean'] == 5.0


class TestPlotting:
    """Test cases for plotting functions."""
    
    def test_plot_regimes(self):
        """Test regime plotting function."""
        data = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1])
        regimes = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        change_points = [3, 6]
        
        fig = plot_regimes(data, regimes, change_points)
        
        assert fig is not None
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_plot_regime_summary(self):
        """Test regime summary plotting."""
        regimes = np.array([0, 0, 0, 1, 1, 2])
        
        fig = plot_regime_summary(regimes)
        
        assert fig is not None
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)


class TestRegimeSplitIntegration:
    """Integration tests for RegimeSplit class."""
    
    def test_regimesplit_properties(self):
        """Test RegimeSplit cross-validation properties."""
        # Import the synthetic data generator
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
        from synth_make import make_series
        
        # Generate synthetic data with known regimes
        df = make_series(n=1000, seed=42)  # Small dataset for testing
        
        # Initialize RegimeSplit
        splitter = RegimeSplit(
            n_splits=3,
            embargo=5,
            purge=10,
            vol_window=30,
            k_regimes=3,
            method="quantiles",
            min_regime_len=20
        )
        
        # Generate splits
        splits = list(splitter.split(df))
        
        # Property 1: Number of splits should match n_splits (or less if insufficient data)
        assert len(splits) <= splitter.n_splits
        assert len(splits) > 0, "Should generate at least one split"
        
        # Property 2: Train/test indices should be non-overlapping integers
        for i, (train_idx, test_idx) in enumerate(splits):
            # Should be numpy arrays of integers
            assert isinstance(train_idx, np.ndarray)
            assert isinstance(test_idx, np.ndarray)
            assert train_idx.dtype in [np.int32, np.int64]
            assert test_idx.dtype in [np.int32, np.int64]
            
            # Should be sorted
            assert np.array_equal(train_idx, np.sort(train_idx))
            assert np.array_equal(test_idx, np.sort(test_idx))
            
            # Should be non-overlapping
            train_set = set(train_idx)
            test_set = set(test_idx)
            assert len(train_set.intersection(test_set)) == 0, f"Fold {i}: Train and test indices overlap"
        
        # Property 3: Temporal order (train always before test)
        for i, (train_idx, test_idx) in enumerate(splits):
            if len(train_idx) > 0 and len(test_idx) > 0:
                max_train_idx = np.max(train_idx)
                min_test_idx = np.min(test_idx)
                assert max_train_idx < min_test_idx, f"Fold {i}: Train indices should be before test indices"
        
        # Property 4: Embargo and purge should create gaps
        for i, (train_idx, test_idx) in enumerate(splits):
            if len(train_idx) > 0 and len(test_idx) > 0:
                max_train_idx = np.max(train_idx)
                min_test_idx = np.min(test_idx)
                gap = min_test_idx - max_train_idx - 1
                
                # Gap should be at least purge size (purge removes from end of train)
                expected_min_gap = splitter.purge
                assert gap >= expected_min_gap, f"Fold {i}: Gap {gap} should be >= purge {expected_min_gap}"
        
        print(f"✓ Generated {len(splits)} valid splits with proper temporal ordering")
    
    def test_min_regime_length_enforcement(self):
        """Test that min_regime_len parameter forces segment merging."""
        # Import the synthetic data generator
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
        from synth_make import make_series
        
        # Generate synthetic data
        df = make_series(n=500, seed=123)
        
        # Test with small min_regime_len (should have more segments)
        splitter_small = RegimeSplit(
            n_splits=3,
            vol_window=20,
            k_regimes=3,
            method="quantiles", 
            min_regime_len=5  # Small minimum length
        )
        
        # Test with large min_regime_len (should have fewer segments)
        splitter_large = RegimeSplit(
            n_splits=3,
            vol_window=20,
            k_regimes=3,
            method="quantiles",
            min_regime_len=50  # Large minimum length
        )
        
        # Generate splits for both
        splits_small = list(splitter_small.split(df))
        splits_large = list(splitter_large.split(df))
        
        # Both should work
        assert len(splits_small) > 0
        assert len(splits_large) > 0
        
        # Check that segments were detected
        segments_small = splitter_small.segments_
        segments_large = splitter_large.segments_
        
        assert segments_small is not None
        assert segments_large is not None
        
        # Large min_regime_len should result in fewer or equal segments
        # (due to merging of short segments)
        assert len(segments_large) <= len(segments_small), \
            f"Large min_regime_len ({len(segments_large)} segments) should have <= small min_regime_len ({len(segments_small)} segments)"
        
        print(f"✓ min_regime_len enforcement: {len(segments_small)} -> {len(segments_large)} segments")
    
    def test_regimesplit_with_different_methods(self):
        """Test RegimeSplit with different regime detection methods."""
        # Import the synthetic data generator
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
        from synth_make import make_series
        
        # Generate synthetic data
        df = make_series(n=300, seed=456)
        
        # Test both methods
        for method in ["quantiles", "kmeans"]:
            splitter = RegimeSplit(
                n_splits=2,
                vol_window=25,
                k_regimes=3,
                method=method,
                min_regime_len=15
            )
            
            splits = list(splitter.split(df))
            
            # Should generate valid splits
            assert len(splits) > 0, f"Method {method} should generate splits"
            
            # Should detect regimes
            assert splitter.regimes_ is not None, f"Method {method} should detect regimes"
            
            # Regimes should have valid labels
            unique_regimes = splitter.regimes_.dropna().unique()
            assert len(unique_regimes) > 0, f"Method {method} should have detected regimes"
            assert all(r >= 0 for r in unique_regimes), f"Method {method} should have non-negative regime labels"
            
            print(f"✓ Method {method}: {len(splits)} splits, {len(unique_regimes)} unique regimes")


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test a complete regime detection workflow."""
        # Generate simple test data
        np.random.seed(42)
        data = pd.Series(np.concatenate([
            np.random.normal(0, 0.1, 50),    # Low volatility regime
            np.random.normal(5, 1.0, 50)     # High volatility regime
        ]))
        
        # Validate data
        assert validate_time_series(data) is True
        
        # Detect regimes
        regimes, change_points = detect_regime_changes(data, method="clustering", n_clusters=2)
        
        # Get statistics
        stats = get_regime_statistics(data, regimes)
        
        # Create plots
        regime_fig = plot_regimes(data, regimes, change_points)
        summary_fig = plot_regime_summary(regimes)
        
        # Verify results
        assert len(regimes) == len(data)
        assert isinstance(stats, dict)
        assert len(np.unique(regimes)) <= 2
        
        # Clean up plots
        import matplotlib.pyplot as plt
        plt.close(regime_fig)
        plt.close(summary_fig)


if __name__ == "__main__":
    # Run tests with pytest if called directly
    pytest.main([__file__])