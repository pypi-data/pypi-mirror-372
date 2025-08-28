"""HTML report generation using Jinja2 templates."""

from jinja2 import Environment, FileSystemLoader
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import base64
import io
import matplotlib.pyplot as plt
import shutil
import os

from .plotting import plot_regimes, plot_regime_summary
from .utils import get_regime_statistics


def generate_html_report(data: pd.Series,
                        regimes: np.ndarray,
                        change_points: List[int],
                        output_path: str = "regime_report.html") -> None:
    """Generate HTML report for regime detection results.
    
    Args:
        data: Original time series data
        regimes: Array of regime labels
        change_points: List of change point indices
        output_path: Path for output HTML file
    """
    # Generate plots and convert to base64
    regime_plot = plot_regimes(data, regimes, change_points)
    regime_plot_b64 = _fig_to_base64(regime_plot)
    plt.close(regime_plot)
    
    summary_plot = plot_regime_summary(regimes)
    summary_plot_b64 = _fig_to_base64(summary_plot)
    plt.close(summary_plot)
    
    # Get statistics
    stats = get_regime_statistics(data, regimes)
    
    # Prepare template context
    context = {
        'title': 'Regime Detection Report',
        'data_points': len(data),
        'num_regimes': len(np.unique(regimes)),
        'num_change_points': len(change_points),
        'regime_plot': regime_plot_b64,
        'summary_plot': summary_plot_b64,
        'statistics': stats,
        'change_points': change_points
    }
    
    # HTML template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
            .section { margin: 30px 0; }
            .plot { text-align: center; margin: 20px 0; }
            .stats-table { border-collapse: collapse; width: 100%; }
            .stats-table th, .stats-table td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            .stats-table th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ title }}</h1>
            <p><strong>Data Points:</strong> {{ data_points }}</p>
            <p><strong>Detected Regimes:</strong> {{ num_regimes }}</p>
            <p><strong>Change Points:</strong> {{ num_change_points }}</p>
        </div>
        
        <div class="section">
            <h2>Time Series with Regimes</h2>
            <div class="plot">
                <img src="data:image/png;base64,{{ regime_plot }}" alt="Regime Plot">
            </div>
        </div>
        
        <div class="section">
            <h2>Regime Distribution</h2>
            <div class="plot">
                <img src="data:image/png;base64,{{ summary_plot }}" alt="Summary Plot">
            </div>
        </div>
        
        <div class="section">
            <h2>Regime Statistics</h2>
            <table class="stats-table">
                <tr>
                    <th>Regime</th>
                    <th>Count</th>
                    <th>Mean</th>
                    <th>Std Dev</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Duration %</th>
                </tr>
                {% for regime, stats in statistics.items() %}
                <tr>
                    <td>{{ regime }}</td>
                    <td>{{ stats.count }}</td>
                    <td>{{ "%.3f"|format(stats.mean) }}</td>
                    <td>{{ "%.3f"|format(stats.std) }}</td>
                    <td>{{ "%.3f"|format(stats.min) }}</td>
                    <td>{{ "%.3f"|format(stats.max) }}</td>
                    <td>{{ "%.1f"|format(stats.duration_pct) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="section">
            <h2>Change Points</h2>
            <p>Detected {{ num_change_points }} change points at indices: {{ change_points|join(', ') }}</p>
        </div>
    </body>
    </html>
    """
    
    # Generate report (legacy function kept for compatibility)
    # Note: This function is deprecated, use render_report instead
    html_content = f"<html><body><h1>Legacy Report</h1><p>Use render_report function instead</p></body></html>"
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {output_path}")


def render_report(context: Dict[str, Any], out_html: str) -> None:
    """Render HTML report using Jinja2 template.
    
    Args:
        context: Template context dictionary
        out_html: Output HTML file path
    """
    # Get template directory path
    templates_dir = Path(__file__).parent / "templates"
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Add custom filters
    def basename_filter(path):
        """Extract basename from path."""
        return Path(path).name if path else ""
    
    env.filters['basename'] = basename_filter
    
    # Load and render template
    template = env.get_template("report.html.j2")
    html_content = template.render(context)
    
    # Write HTML file
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report rendered: {out_html}")


def build_report_context(folds_data: Dict[str, Any], 
                        regimes_df: pd.DataFrame,
                        timeline_image_path: Optional[str] = None) -> Dict[str, Any]:
    """Build context dictionary for report template.
    
    Args:
        folds_data: Folds configuration and data from JSON
        regimes_df: Regimes DataFrame
        timeline_image_path: Optional path to timeline image
        
    Returns:
        Context dictionary for template rendering
    """
    config = folds_data["config"]
    folds = folds_data["folds"]
    
    # Calculate summary statistics
    total_train_obs = sum(fold['train']['n_obs'] for fold in folds)
    total_test_obs = sum(fold['test']['n_obs'] for fold in folds)
    
    summary = {
        'total_folds': len(folds),
        'total_train_obs': total_train_obs,
        'total_test_obs': total_test_obs,
        'avg_train_size': int(total_train_obs / len(folds)) if folds else 0,
        'avg_test_size': int(total_test_obs / len(folds)) if folds else 0,
        'unique_regimes': len(regimes_df['regime_id'].dropna().unique())
    }
    
    # Calculate regime statistics
    regime_counts = regimes_df['regime_id'].value_counts().sort_index()
    total_obs = len(regimes_df)
    
    regime_stats = []
    for regime_id, count in regime_counts.items():
        if pd.notna(regime_id):
            percentage = (count / total_obs) * 100
            # Estimate duration from data frequency (approximate)
            duration = f"{count} obs"
            
            regime_stats.append({
                'regime_id': int(regime_id),
                'count': count,
                'percentage': percentage,
                'duration': duration
            })
    
    # Build context
    context = {
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'config': config,
        'folds': folds,
        'summary': summary,
        'regime_stats': regime_stats,
        'timeline_image': os.path.basename(timeline_image_path) if timeline_image_path else None,
        'version': '0.1.0'
    }
    
    return context


def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 string.
    
    Args:
        fig: matplotlib Figure object
        
    Returns:
        Base64 encoded string of the plot
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    
    plot_data = buffer.getvalue()
    buffer.close()
    
    encoded = base64.b64encode(plot_data).decode('utf-8')
    return encoded