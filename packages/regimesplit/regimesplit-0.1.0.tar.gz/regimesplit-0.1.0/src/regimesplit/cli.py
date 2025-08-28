"""Command-line interface for regimesplit."""

import tyro
from pathlib import Path
import pandas as pd
import json
import numpy as np
import shutil
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from .splitter import RegimeSplit
from .report import render_report, build_report_context
from .plotting import plot_timeline


@dataclass
class FoldsConfig:
    """Configuration for folds command.
    
    Attributes:
        csv_path: Path to CSV file containing time series data
        ret_col: Column name for returns (if None, computed from price_col)
        price_col: Column name for price data (used if ret_col is None)
        n_splits: Number of cross-validation folds to generate
        embargo: Number of observations to embargo after each test period
        purge: Number of observations to purge before each test period
        vol_window: Rolling window size for volatility calculation
        k_regimes: Number of volatility regimes to detect
        method: Regime detection method ("quantiles" or "kmeans")
        min_regime_len: Minimum length for regime segments (shorter ones merged)
        output_dir: Directory to save output files
    """
    csv_path: Path
    ret_col: Optional[str] = None
    price_col: Optional[str] = "price"
    n_splits: int = 5
    embargo: int = 0
    purge: int = 0
    vol_window: int = 60
    k_regimes: int = 3
    method: str = "quantiles"
    min_regime_len: int = 30
    output_dir: Path = Path("./output")


@dataclass
class ReportConfig:
    """Configuration for report command."""
    folds_json: Path
    regimes_csv: Path
    output_dir: Path = Path("./output")


def folds_command(config: FoldsConfig) -> None:
    """Generate cross-validation folds based on regime detection.
    
    Args:
        config: Configuration for folds generation
    """
    print(f"Processing file: {config.csv_path}")
    print(f"Output directory: {config.output_dir}")
    
    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load CSV data
    try:
        df = pd.read_csv(config.csv_path, index_col=0, parse_dates=True)
        print(f"Loaded data with shape: {df.shape}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Determine return column
    if config.ret_col is not None:
        if config.ret_col not in df.columns:
            print(f"Error: Column '{config.ret_col}' not found in CSV")
            return
        use_col_for_ret = config.ret_col
    elif config.price_col is not None:
        if config.price_col not in df.columns:
            print(f"Error: Column '{config.price_col}' not found in CSV")
            return
        use_col_for_ret = None  # Will compute returns from price
    else:
        print("Error: Must specify either ret_col or price_col")
        return
    
    # Initialize RegimeSplit
    splitter = RegimeSplit(
        n_splits=config.n_splits,
        embargo=config.embargo,
        purge=config.purge,
        vol_window=config.vol_window,
        k_regimes=config.k_regimes,
        method=config.method,
        min_regime_len=config.min_regime_len,
        use_col_for_ret=use_col_for_ret
    )
    
    print(f"Initialized RegimeSplit with {config.n_splits} splits")
    
    # Generate splits
    try:
        splits = list(splitter.split(df))
        print(f"Generated {len(splits)} folds")
    except Exception as e:
        print(f"Error generating splits: {e}")
        return
    
    # Build serializable structure
    folds_list: List[Dict[str, Any]] = []
    folds_data: Dict[str, Any] = {
        "config": {
            "n_splits": config.n_splits,
            "embargo": config.embargo,
            "purge": config.purge,
            "vol_window": config.vol_window,
            "k_regimes": config.k_regimes,
            "method": config.method,
            "min_regime_len": config.min_regime_len,
            "csv_path": str(config.csv_path),
            "use_col_for_ret": use_col_for_ret
        },
        "folds": folds_list
    }
    
    for i, (train_idx, test_idx) in enumerate(splits):
        train_start_ts = df.index[train_idx[0]].isoformat() if len(train_idx) > 0 else None
        train_end_ts = df.index[train_idx[-1]].isoformat() if len(train_idx) > 0 else None
        test_start_ts = df.index[test_idx[0]].isoformat() if len(test_idx) > 0 else None
        test_end_ts = df.index[test_idx[-1]].isoformat() if len(test_idx) > 0 else None
        
        fold_data = {
            "fold": i,
            "train": {
                "start_ts": train_start_ts,
                "end_ts": train_end_ts,
                "n_obs": len(train_idx),
                "indices": train_idx.tolist()
            },
            "test": {
                "start_ts": test_start_ts,
                "end_ts": test_end_ts,
                "n_obs": len(test_idx),
                "indices": test_idx.tolist()
            }
        }
        
        folds_list.append(fold_data)
        print(f"Fold {i}: Train {len(train_idx)} obs ({train_start_ts} to {train_end_ts}), "
              f"Test {len(test_idx)} obs ({test_start_ts} to {test_end_ts})")
    
    # folds_list is already referenced in folds_data
    
    # Save folds.json
    folds_path = config.output_dir / "folds.json"
    with open(folds_path, 'w') as f:
        json.dump(folds_data, f, indent=2)
    print(f"Saved folds data to: {folds_path}")
    
    # Save regimes.csv
    if splitter.regimes_ is not None:
        regimes_df = pd.DataFrame({
            'timestamp': splitter.regimes_.index,
            'regime_id': splitter.regimes_.values
        })
        regimes_path = config.output_dir / "regimes.csv"
        regimes_df.to_csv(regimes_path, index=False)
        print(f"Saved regimes data to: {regimes_path}")
        
        # Generate timeline plot
        try:
            timeline_path = config.output_dir / "timeline.png"
            plot_timeline(
                index=df.index,
                regime_id=splitter.regimes_,
                folds=folds_list,
                path_png=timeline_path
            )
            print(f"Saved timeline plot to: {timeline_path}")
        except Exception as e:
            print(f"Warning: Could not generate timeline plot: {e}")
    
    print("Folds generation completed!")


def report_command(config: ReportConfig) -> None:
    """Generate HTML report from folds and regimes data.
    
    Args:
        config: Configuration for report generation
    """
    print(f"Generating report from: {config.folds_json}, {config.regimes_csv}")
    
    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load folds data
    try:
        with open(config.folds_json, 'r') as f:
            folds_data = json.load(f)
    except Exception as e:
        print(f"Error loading folds JSON: {e}")
        return
    
    # Load regimes data
    try:
        regimes_df = pd.read_csv(config.regimes_csv, parse_dates=['timestamp'])
        regimes_df.set_index('timestamp', inplace=True)
    except Exception as e:
        print(f"Error loading regimes CSV: {e}")
        return
    
    # Look for timeline plot in the same directory as the JSON/CSV files
    timeline_source_path = config.folds_json.parent / "timeline.png"
    timeline_dest_path = config.output_dir / "timeline.png"
    timeline_image_name = None
    
    if timeline_source_path.exists():
        # Copy timeline plot to output directory
        shutil.copy2(timeline_source_path, timeline_dest_path)
        timeline_image_name = timeline_dest_path.name
        print(f"Copied timeline plot to: {timeline_dest_path}")
    else:
        print(f"Timeline plot not found at: {timeline_source_path}")
    
    # Build report context
    context = build_report_context(
        folds_data=folds_data,
        regimes_df=regimes_df,
        timeline_image_path=str(timeline_dest_path) if timeline_image_name else None
    )
    
    # Render HTML report
    report_path = config.output_dir / "folds_report.html"
    render_report(context, str(report_path))
    
    print(f"Generated HTML report: {report_path}")


def generate_simple_html_report(folds_data: Dict[str, Any], regimes_df: pd.DataFrame) -> str:
    """Generate a simple HTML report for folds and regimes.
    
    Args:
        folds_data: Folds configuration and data
        regimes_df: Regimes DataFrame
        
    Returns:
        HTML content as string
    """
    config = folds_data["config"]
    folds = folds_data["folds"]
    
    # Calculate regime statistics
    regime_counts = regimes_df['regime_id'].value_counts().sort_index()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RegimeSplit Folds Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 30px 0; }}
            .config-table, .folds-table {{ border-collapse: collapse; width: 100%; }}
            .config-table th, .config-table td, 
            .folds-table th, .folds-table td {{ border: 1px solid #ddd; padding: 8px; }}
            .config-table th, .folds-table th {{ background-color: #f2f2f2; }}
            .folds-table td {{ text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RegimeSplit Cross-Validation Report</h1>
            <p><strong>Data Source:</strong> {config['csv_path']}</p>
            <p><strong>Generated:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Configuration</h2>
            <table class="config-table">
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Number of Splits</td><td>{config['n_splits']}</td></tr>
                <tr><td>Embargo</td><td>{config['embargo']}</td></tr>
                <tr><td>Purge</td><td>{config['purge']}</td></tr>
                <tr><td>Volatility Window</td><td>{config['vol_window']}</td></tr>
                <tr><td>Number of Regimes</td><td>{config['k_regimes']}</td></tr>
                <tr><td>Method</td><td>{config['method']}</td></tr>
                <tr><td>Min Regime Length</td><td>{config['min_regime_len']}</td></tr>
                <tr><td>Return Column</td><td>{config['use_col_for_ret'] or 'Computed from price'}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Regime Distribution</h2>
            <table class="config-table">
                <tr><th>Regime</th><th>Count</th><th>Percentage</th></tr>
    """
    
    total_obs = len(regimes_df)
    for regime_id, count in regime_counts.items():
        if pd.notna(regime_id):
            pct = (count / total_obs) * 100
            html += f"<tr><td>{int(regime_id)}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>Cross-Validation Folds</h2>
            <table class="folds-table">
                <tr>
                    <th>Fold</th>
                    <th>Train Start</th>
                    <th>Train End</th>
                    <th>Train Obs</th>
                    <th>Test Start</th>
                    <th>Test End</th>
                    <th>Test Obs</th>
                </tr>
    """
    
    for fold in folds:
        html += f"""
                <tr>
                    <td>{fold['fold']}</td>
                    <td>{fold['train']['start_ts'] or 'N/A'}</td>
                    <td>{fold['train']['end_ts'] or 'N/A'}</td>
                    <td>{fold['train']['n_obs']}</td>
                    <td>{fold['test']['start_ts'] or 'N/A'}</td>
                    <td>{fold['test']['end_ts'] or 'N/A'}</td>
                    <td>{fold['test']['n_obs']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>Summary</h2>
            <ul>
    """
    
    total_train_obs = sum(fold['train']['n_obs'] for fold in folds)
    total_test_obs = sum(fold['test']['n_obs'] for fold in folds)
    
    html += f"""
                <li>Total folds generated: {len(folds)}</li>
                <li>Total training observations: {total_train_obs}</li>
                <li>Total test observations: {total_test_obs}</li>
                <li>Average train size per fold: {total_train_obs / len(folds):.0f}</li>
                <li>Average test size per fold: {total_test_obs / len(folds):.0f}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html


def main():
    """Main CLI entry point with subcommands."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: regimesplit [folds|report] ...")
        print("  folds:  Generate cross-validation folds")  
        print("  report: Generate HTML report")
        return
    
    command = sys.argv[1]
    if command == "folds":
        tyro.cli(folds_command, args=sys.argv[2:])
    elif command == "report":
        tyro.cli(report_command, args=sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: folds, report")


if __name__ == "__main__":
    main()