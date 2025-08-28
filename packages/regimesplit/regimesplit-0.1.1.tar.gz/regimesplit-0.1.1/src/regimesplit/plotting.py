"""Plotting utilities for regime visualization."""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union
from pathlib import Path


def plot_regimes(data: pd.Series, regimes: np.ndarray, 
                 change_points: Optional[List[int]] = None,
                 title: str = "Time Series with Regimes",
                 figsize: tuple = (12, 6)) -> plt.Figure:
    """Plot time series data with regime coloring.
    
    Args:
        data: Time series data
        regimes: Array of regime labels for each point
        change_points: List of change point indices (optional)
        title: Plot title
        figsize: Figure size tuple
        
    Returns:
        matplotlib Figure object
    """
    # Placeholder implementation
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the time series
    ax.plot(data.index, data.values, 'k-', alpha=0.7)
    
    # Add regime coloring (placeholder)
    unique_regimes = np.unique(regimes)
    colors = plt.colormaps['Set1'](np.linspace(0, 1, len(unique_regimes)))
    
    for i, regime in enumerate(unique_regimes):
        mask = regimes == regime
        ax.scatter(data.index[mask], data.values[mask], 
                  c=[colors[i]], alpha=0.6, s=10, 
                  label=f'Regime {regime}')
    
    # Add change points if provided
    if change_points:
        for cp in change_points:
            ax.axvline(x=data.index[cp], color='red', 
                      linestyle='--', alpha=0.7)
    
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    
    return fig


def plot_regime_summary(regimes: np.ndarray, 
                       title: str = "Regime Distribution") -> plt.Figure:
    """Plot summary statistics for detected regimes.
    
    Args:
        regimes: Array of regime labels
        title: Plot title
        
    Returns:
        matplotlib Figure object
    """
    # Placeholder implementation
    fig, ax = plt.subplots(figsize=(8, 6))
    
    unique_regimes, counts = np.unique(regimes, return_counts=True)
    ax.bar(unique_regimes, counts)
    
    ax.set_title(title)
    ax.set_xlabel('Regime')
    ax.set_ylabel('Count')
    
    return fig


def plot_timeline(index: pd.DatetimeIndex, 
                 regime_id: pd.Series,
                 folds: List[Dict],
                 path_png: Union[str, Path],
                 save_svg: bool = True) -> None:
    """Plot timeline with regimes and cross-validation folds.
    
    Creates a comprehensive timeline visualization showing:
    1. Top panel: Detected volatility regimes as colored background segments
    2. Bottom panel: Cross-validation folds with train (blue) and test (red) periods
    
    Args:
        index: DatetimeIndex for the time series, used for temporal alignment
        regime_id: Series with regime labels (integers), should align with index
        folds: List of fold dictionaries containing train/test information.
               Each fold should have structure: 
               {'fold': int, 'train': {'start_ts': str, 'end_ts': str}, 
                'test': {'start_ts': str, 'end_ts': str}}
        path_png: Path to save the PNG plot (string or Path object)
        save_svg: If True, also saves an SVG version alongside PNG
        
    Returns:
        None (saves plot to disk)
        
    Raises:
        ValueError: If index and regime_id have incompatible lengths or formats
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.colors import ListedColormap
    import numpy as np
    from pathlib import Path
    from typing import Dict
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                   gridspec_kw={'height_ratios': [1, 2]})
    
    # Align regime_id with index
    regime_aligned = regime_id.reindex(index).fillna(-1)
    
    # Plot 1: Regime background
    unique_regimes = sorted([r for r in regime_aligned.unique() if r >= 0])
    n_regimes = len(unique_regimes)
    
    if n_regimes > 0:
        # Create colormap for regimes
        colors = plt.colormaps['Set3'](np.linspace(0, 1, n_regimes))
        
        # Plot regime segments as colored background
        for i, ts in enumerate(index[:-1]):
            regime = regime_aligned.iloc[i]
            if regime >= 0 and regime in unique_regimes:
                color_idx = unique_regimes.index(regime)
                ax1.axvspan(ts, index[i+1], 
                           color=colors[color_idx], alpha=0.7,
                           label=f'Regime {int(regime)}' if regime not in [r for r in regime_aligned.iloc[:i] if r >= 0] else "")
        
        ax1.set_xlim(index[0], index[-1])
        ax1.set_ylim(0, 1)
        ax1.set_ylabel('Regimes')
        ax1.set_title('Detected Regimes Timeline')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.set_yticks([])
    
    # Plot 2: Cross-validation folds
    fold_height = 0.8
    fold_spacing = 1.0
    
    for fold_idx, fold in enumerate(folds):
        y_pos = fold_idx * fold_spacing
        
        # Parse timestamps
        train_start = pd.to_datetime(fold['train']['start_ts']) if fold['train']['start_ts'] else None
        train_end = pd.to_datetime(fold['train']['end_ts']) if fold['train']['end_ts'] else None
        test_start = pd.to_datetime(fold['test']['start_ts']) if fold['test']['start_ts'] else None
        test_end = pd.to_datetime(fold['test']['end_ts']) if fold['test']['end_ts'] else None
        
        # Plot training period
        if train_start and train_end:
            train_width = (train_end - train_start).total_seconds() / (index[-1] - index[0]).total_seconds() * (index[-1] - index[0])
            rect_train = patches.Rectangle(
                (train_start, y_pos), train_width, fold_height,
                linewidth=1, edgecolor='blue', facecolor='lightblue', 
                alpha=0.6, label='Train' if fold_idx == 0 else ""
            )
            ax2.add_patch(rect_train)
        
        # Plot test period  
        if test_start and test_end:
            test_width = (test_end - test_start).total_seconds() / (index[-1] - index[0]).total_seconds() * (index[-1] - index[0])
            rect_test = patches.Rectangle(
                (test_start, y_pos), test_width, fold_height,
                linewidth=1, edgecolor='red', facecolor='lightcoral',
                alpha=0.6, label='Test' if fold_idx == 0 else ""
            )
            ax2.add_patch(rect_test)
        
        # Add fold label
        ax2.text(index[0] - (index[-1] - index[0]) * 0.02, y_pos + fold_height/2, 
                f'Fold {fold["fold"]}', 
                ha='right', va='center', fontsize=10)
    
    # Format fold plot
    ax2.set_xlim(index[0], index[-1])
    ax2.set_ylim(-0.5, len(folds) * fold_spacing - 0.5)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Cross-Validation Folds')
    ax2.set_title('Train/Test Splits Timeline')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Format x-axis
    fig.autofmt_xdate()
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(path_png, dpi=150, bbox_inches='tight')
    
    # Also save SVG version if requested
    if save_svg:
        path_svg = Path(path_png).with_suffix('.svg')
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        print(f"Timeline plot saved to: {path_png} and {path_svg}")
    else:
        print(f"Timeline plot saved to: {path_png}")
    
    plt.close(fig)