"""
Unified Visualization Module for Land Use Intensity Analysis

This module consolidates all visualization functionality from:
- plots.py (original plotting functions)
- enhanced_visualization.py (improved versions)
- modern_viz.py (modern interactive visualizations)

Provides comprehensive visualization capabilities with:
- Static PNG generation using matplotlib
- Interactive HTML generation using plotly
- Modern styling and themes
- Multiple output formats
- Enhanced error handling and documentation
- Backward compatibility with existing APIs

Main Functions:
- plot_intensity_analysis(): Intensity analysis bar charts
- plot_sankey_diagram(): Sankey flow diagrams
- plot_chord_diagram(): Chord/transition matrix diagrams
- create_summary_plots(): Complete visualization suite
- generate_all_visualizations(): Modern visualization pipeline

Dependencies:
- matplotlib (PNG static charts)
- plotly (HTML interactive charts)
- seaborn (enhanced styling)
- pandas (data handling)
- numpy (numerical operations)
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set matplotlib style for publication-quality plots
plt.style.use('default')
sns.set_palette("husl")

# Optional dependencies
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not available. Only matplotlib plots will be generated.")

# Default color schemes
CATEGORY_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
]

TRANSITION_COLORS = {
    'gain': '#2ECC71',    # Green for gains
    'loss': '#E74C3C',    # Red for losses
    'persistent': '#95A5A6',  # Gray for persistence
    'change': '#F39C12'   # Orange for changes
}


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _get_category_colors(n_categories: int) -> List[str]:
    """Get color palette for categories."""
    if n_categories <= len(CATEGORY_COLORS):
        return CATEGORY_COLORS[:n_categories]
    else:
        # Generate additional colors using seaborn
        return sns.color_palette("husl", n_categories).as_hex()


def _format_title(title: str) -> str:
    """Format title for plots."""
    return title.replace('_', ' ').title()


def plot_intensity_analysis(
    intensity_results: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "intensity_analysis",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 300,
    show_uniform_line: bool = True,
) -> Dict[str, str]:
    """
    Create comprehensive intensity analysis visualization.

    Generates both PNG (matplotlib) and HTML (plotly) versions of intensity
    analysis charts showing gain area and intensity percentages by time interval.

    Parameters
    ----------
    intensity_results : dict
        Results from intensity_analysis() function containing interval data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "intensity_analysis"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version using matplotlib
    save_html : bool, default True
        Whether to save HTML version using plotly
    figsize : tuple, default (14, 10)
        Figure size for PNG version (width, height) in inches
    dpi : int, default 300
        DPI for PNG output
    show_uniform_line : bool, default True
        Whether to show uniform intensity reference line

    Returns
    -------
    dict
        Dictionary with paths to generated files

    Examples
    --------
    >>> import landuse_intensity as lui
    >>> ct = lui.contingency_table('path/to/rasters/', pixel_resolution=30)
    >>> ia = lui.intensity_analysis(ct, category_n=1, category_m=0)
    >>> files = lui.plot_intensity_analysis(ia)
    >>> print(f"PNG saved: {files['png']}")
    >>> print(f"HTML saved: {files['html']}")
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    # Extract data for plotting
    if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'St'):
        # IntensityAnalysis object
        data = intensity_results.interval_level.St.copy()
    elif isinstance(intensity_results, dict) and 'interval_results' in intensity_results:
        # Dictionary format
        data = intensity_results['interval_results'].copy()
    else:
        raise ValueError("No interval data found in intensity_results. Expected IntensityAnalysis object with interval_level.St or dict with 'interval_results'")

    # Ensure required columns exist
    required_cols = ['Period', 'TotalChange', 'St']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}. Available: {list(data.columns)}")

    # Generate PNG version with matplotlib
    if save_png:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Left plot: Total Change
        bars1 = ax1.bar(data['Period'], data['TotalChange'],
                        color=TRANSITION_COLORS['change'], alpha=0.7,
                        edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Total Change (km²)', fontsize=12, fontweight='bold')
        ax1.set_title('Total Change by Time Period', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        # Right plot: Interval Intensity (St)
        bars2 = ax2.bar(data['Period'], data['St'],
                       color=TRANSITION_COLORS['loss'], alpha=0.7,
                       edgecolor='black', linewidth=0.5)
        ax2.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Interval Intensity (St) (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Interval Intensity by Time Period', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Add uniform intensity line (U)
        if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'U'):
            uniform_val = intensity_results.interval_level.U
            ax2.axhline(y=uniform_val, color='red', linestyle='--', linewidth=2,
                       label=f'Uniform Intensity (U): {uniform_val:.3f}%')
            ax2.legend()

        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")

    # Generate HTML version with plotly
    if save_html and HAS_PLOTLY:
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Total Change by Time Period', 'Interval Intensity by Time Period'),
            specs=[[{"secondary_y": False}, {"secondary_y": True}]]
        )

        # Left plot: Total Change
        fig.add_trace(
            go.Bar(
                x=data['Period'],
                y=data['TotalChange'],
                name='Total Change (km²)',
                marker_color=TRANSITION_COLORS['change'],
                text=[f'{val:.1f}' for val in data['TotalChange']],
                textposition='outside'
            ),
            row=1, col=1
        )

        # Right plot: Interval Intensity
        fig.add_trace(
            go.Bar(
                x=data['Period'],
                y=data['St'],
                name='Interval Intensity (St) (%)',
                marker_color=TRANSITION_COLORS['loss'],
                text=[f'{val:.3f}%' for val in data['St']],
                textposition='outside'
            ),
            row=1, col=2
        )

        # Add uniform intensity line
        if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'U'):
            uniform_val = intensity_results.interval_level.U
            fig.add_hline(
                y=uniform_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Uniform Intensity (U): {uniform_val:.3f}%",
                col=2
            )

        fig.update_layout(
            title_text="Land Use Change Intensity Analysis",
            title_x=0.5,
            showlegend=False,
            height=600,
            font=dict(size=12)
        )

        fig.update_xaxes(title_text="Time Period", row=1, col=1)
        fig.update_xaxes(title_text="Time Period", row=1, col=2)
        fig.update_yaxes(title_text="Gain Area (km²)", row=1, col=1)
        fig.update_yaxes(title_text="Intensity Gain (%)", row=1, col=2)

        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")

    return generated_files


def plot_sankey_diagram(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "sankey_diagram",
    save_png: bool = True,
    save_html: bool = True,
    min_flow: float = 0.1,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create Sankey diagram showing land use transitions.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "sankey_diagram"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    min_flow : float, default 0.1
        Minimum flow size to show (km²)
    figsize : tuple, default (12, 8)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output

    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    # Extract data
    if 'lulc_Multistep' not in contingency_data:
        raise ValueError("No lulc_Multistep data found in contingency_data")

    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())

    # Filter flows
    multistep = multistep[multistep['km2'] >= min_flow].copy()

    if len(multistep) == 0:
        warnings.warn(f"No flows found with minimum size {min_flow} km²")
        return {}

    # Create category labels
    if not legend.empty and 'CategoryValue' in legend.columns:
        label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        all_cats = set(multistep['From'].unique()) | set(multistep['To'].unique())
        label_map = {cat: f"Class_{cat}" for cat in sorted(all_cats)}

    # Generate PNG version
    if save_png:
        png_path = _create_matplotlib_sankey(
            multistep, label_map, filename, output_path, figsize, dpi
        )
        generated_files['png'] = str(png_path)

    # Generate HTML version
    if save_html and HAS_PLOTLY:
        html_path = _create_plotly_sankey(
            multistep, label_map, filename, output_path
        )
        generated_files['html'] = str(html_path)

    return generated_files


def _create_matplotlib_sankey(
    multistep: pd.DataFrame,
    label_map: Dict,
    filename: str,
    output_path: Path,
    figsize: Tuple[int, int],
    dpi: int
) -> Path:
    """Create matplotlib Sankey diagram."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Left plot: Losses
    losses = multistep.groupby('From')['km2'].sum().sort_values(ascending=False)
    loss_labels = [label_map.get(cat, f"Class_{cat}") for cat in losses.index]

    colors = sns.color_palette("Reds_r", len(losses))
    bars1 = ax1.barh(range(len(losses)), losses.values, color=colors)
    ax1.set_yticks(range(len(losses)))
    ax1.set_yticklabels(loss_labels)
    ax1.set_xlabel('Lost Area (km²)')
    ax1.set_title('Land Cover Losses', fontweight='bold')

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars1, losses.values)):
        ax1.text(value + max(losses) * 0.01, i, f'{value:.1f}', va='center', fontweight='bold')

    # Right plot: Gains
    gains = multistep.groupby('To')['km2'].sum().sort_values(ascending=False)
    gain_labels = [label_map.get(cat, f"Class_{cat}") for cat in gains.index]

    colors = sns.color_palette("Greens", len(gains))
    bars2 = ax2.barh(range(len(gains)), gains.values, color=colors)
    ax2.set_yticks(range(len(gains)))
    ax2.set_yticklabels(gain_labels)
    ax2.set_xlabel('Gained Area (km²)')
    ax2.set_title('Land Cover Gains', fontweight='bold')

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars2, gains.values)):
        ax2.text(value + max(gains) * 0.01, i, f'{value:.1f}', va='center', fontweight='bold')

    plt.suptitle('Land Use Change Flows', fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout()

    png_path = output_path / f"{filename}.png"
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()

    return png_path


def _create_plotly_sankey(
    multistep: pd.DataFrame,
    label_map: Dict,
    filename: str,
    output_path: Path
) -> Path:
    """Create plotly Sankey diagram."""
    # Prepare data
    all_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
    node_labels = [label_map.get(cat, f"Class_{cat}") for cat in all_cats]

    sources = []
    targets = []
    values = []

    for _, row in multistep.iterrows():
        sources.append(all_cats.index(row['From']))
        targets.append(all_cats.index(row['To']))
        values.append(row['km2'])

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="lightblue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(255, 0, 255, 0.4)"
        )
    )])

    fig.update_layout(
        title_text="Land Use Change Flows",
        font_size=12,
        width=1000,
        height=600
    )

    html_path = output_path / f"{filename}.html"
    fig.write_html(html_path)

    return html_path


def plot_chord_diagram(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "chord_diagram",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (10, 10),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create chord diagram showing transition matrix.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "chord_diagram"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    figsize : tuple, default (10, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output

    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    # Extract data
    if 'lulc_Multistep' not in contingency_data:
        raise ValueError("No lulc_Multistep data found in contingency_data")

    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())

    # Create transition matrix
    transition_matrix = multistep.pivot_table(
        index='From', columns='To', values='km2', fill_value=0
    )

    # Create category labels
    if not legend.empty and 'CategoryValue' in legend.columns:
        label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        categories = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        label_map = {cat: f"Class_{cat}" for cat in categories}

    # Generate PNG version
    if save_png:
        png_path = _create_matplotlib_chord(
            transition_matrix, label_map, filename, output_path, figsize, dpi
        )
        generated_files['png'] = str(png_path)

    # Generate HTML version
    if save_html and HAS_PLOTLY:
        html_path = _create_plotly_chord(
            transition_matrix, label_map, filename, output_path
        )
        generated_files['html'] = str(html_path)

    return generated_files


def _create_matplotlib_chord(
    matrix: pd.DataFrame,
    label_map: Dict,
    filename: str,
    output_path: Path,
    figsize: Tuple[int, int],
    dpi: int
) -> Path:
    """Create matplotlib chord diagram (heatmap)."""
    fig, ax = plt.subplots(figsize=figsize)

    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]

    # Create heatmap
    im = ax.imshow(matrix.values, cmap='YlOrRd', aspect='auto')

    # Set ticks and labels
    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_yticks(np.arange(len(matrix.index)))
    ax.set_xticklabels(column_labels, rotation=45, ha='right')
    ax.set_yticklabels(index_labels)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Area (km²)', rotation=270, labelpad=20)

    # Add text annotations
    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            value = matrix.iloc[i, j]
            if value > 0:
                text = ax.text(j, i, f'{value:.1f}',
                             ha="center", va="center",
                             color="white" if value > matrix.values.max()*0.5 else "black",
                             fontweight='bold')

    ax.set_xlabel('To (Land Cover Class)', fontweight='bold')
    ax.set_ylabel('From (Land Cover Class)', fontweight='bold')
    ax.set_title('Land Use Transition Matrix', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    png_path = output_path / f"{filename}.png"
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()

    return png_path


def _create_plotly_chord(
    matrix: pd.DataFrame,
    label_map: Dict,
    filename: str,
    output_path: Path
) -> Path:
    """Create plotly chord diagram (heatmap)."""
    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]

    # Create interactive heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=column_labels,
        y=index_labels,
        colorscale='YlOrRd',
        colorbar=dict(title='Area (km²)')
    ))

    fig.update_layout(
        title='Land Use Transition Matrix',
        xaxis_title='To (Land Cover Class)',
        yaxis_title='From (Land Cover Class)',
        width=800,
        height=600
    )

    html_path = output_path / f"{filename}.html"
    fig.write_html(html_path)

    return html_path


def plot_net_gain_loss(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "net_gain_loss",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create net gain/loss bar chart.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "net_gain_loss"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    figsize : tuple, default (12, 8)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output

    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    # Extract data
    if 'lulc_Multistep' not in contingency_data:
        raise ValueError("No lulc_Multistep data found in contingency_data")

    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())

    # Calculate net changes
    gains = multistep.groupby('To')['km2'].sum()
    losses = multistep.groupby('From')['km2'].sum()

    # Combine all categories
    all_cats = sorted(set(gains.index) | set(losses.index))
    net_changes = pd.Series(index=all_cats, dtype=float)

    for cat in all_cats:
        gain = gains.get(cat, 0)
        loss = losses.get(cat, 0)
        net_changes[cat] = gain - loss

    # Create category labels
    if not legend.empty and 'CategoryValue' in legend.columns:
        label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        label_map = {cat: f"Class_{cat}" for cat in all_cats}

    category_labels = [label_map.get(cat, f"Class_{cat}") for cat in net_changes.index]

    # Generate PNG version
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)

        colors = ['green' if x > 0 else 'red' for x in net_changes.values]
        bars = ax.bar(range(len(net_changes)), net_changes.values, color=colors, alpha=0.7)

        ax.set_xlabel('Land Cover Class', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net Change (km²)', fontsize=12, fontweight='bold')
        ax.set_title('Net Gain/Loss by Land Cover Class', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(net_changes)))
        ax.set_xticklabels(category_labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, net_changes.values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (0.01 * abs(height)),
                   f'{value:.1f}', ha='center', va='bottom' if height >= 0 else 'top',
                   fontweight='bold')

        plt.tight_layout()

        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)

    # Generate HTML version
    if save_html and HAS_PLOTLY:
        colors = ['#2ECC71' if x > 0 else '#E74C3C' for x in net_changes.values]

        fig = go.Figure(data=[go.Bar(
            x=category_labels,
            y=net_changes.values,
            marker_color=colors,
            text=[f'{val:.1f}' for val in net_changes.values],
            textposition='outside'
        )])

        fig.update_layout(
            title='Net Gain/Loss by Land Cover Class',
            xaxis_title='Land Cover Class',
            yaxis_title='Net Change (km²)',
            width=1000,
            height=600
        )

        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)

    return generated_files


def create_summary_plots(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    title_prefix: str = "Land Use Change Analysis",
    **kwargs
) -> Dict[str, Dict[str, str]]:
    """
    Create a complete set of visualization plots.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save outputs
    title_prefix : str
        Prefix for plot titles
    **kwargs
        Additional arguments passed to individual plot functions

    Returns
    -------
    dict
        Dictionary mapping plot types to file paths
    """
    output_path = _ensure_output_dir(output_dir)
    results = {}

    # 1. Sankey diagram
    print("📊 Creating Sankey diagram...")
    results['sankey'] = plot_sankey_diagram(
        contingency_data,
        output_dir=output_path,
        filename="sankey_flows",
        **kwargs
    )

    # 2. Chord diagram / transition matrix
    print("📊 Creating transition matrix...")
    results['chord'] = plot_chord_diagram(
        contingency_data,
        output_dir=output_path,
        filename="transition_matrix",
        **kwargs
    )

    # 3. Net gain/loss
    print("📊 Creating net gain/loss chart...")
    results['net_gain_loss'] = plot_net_gain_loss(
        contingency_data,
        output_dir=output_path,
        filename="net_gain_loss",
        **kwargs
    )

    return results


# Modern visualization functions (from modern_viz.py)
def create_intensity_matrix_plot(
    intensity_matrix: np.ndarray,
    class_names: List[str] = None,
    title: str = "Land Use Intensity Matrix",
    output_dir: Union[str, Path] = "outputs",
    filename: str = "intensity_matrix",
    save_png: bool = True,
    save_html: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Create intensity matrix plot using modern visualizer.

    Parameters
    ----------
    intensity_matrix : np.ndarray
        Intensity matrix data
    class_names : list of str, optional
        Names of land use classes
    title : str
        Plot title
    output_dir : str or Path
        Directory to save outputs
    filename : str
        Base filename
    save_png : bool
        Save PNG version
    save_html : bool
        Save HTML version
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    dict
        Dictionary with paths to saved files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    if class_names is None:
        class_names = [f"Class_{i}" for i in range(len(intensity_matrix))]

    # Generate PNG version
    if save_png:
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 8)))

        im = ax.imshow(intensity_matrix, cmap='viridis', aspect='equal')
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Intensity', fontsize=12)

        ax.set_xticks(np.arange(len(class_names)))
        ax.set_yticks(np.arange(len(class_names)))
        ax.set_xticklabels(class_names, rotation=45, ha='right')
        ax.set_yticklabels(class_names)

        # Add text annotations
        for i in range(len(intensity_matrix)):
            for j in range(len(intensity_matrix[i])):
                value = intensity_matrix[i, j]
                color = "white" if value > intensity_matrix.max() * 0.5 else "black"
                ax.text(j, i, f'{value:.3f}', ha="center", va="center",
                       color=color, fontweight='bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('To Class', fontsize=12)
        ax.set_ylabel('From Class', fontsize=12)

        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=kwargs.get('dpi', 300), bbox_inches='tight')
        plt.close()
        generated_files['png'] = str(png_path)

    # Generate HTML version
    if save_html and HAS_PLOTLY:
        fig = go.Figure(data=go.Heatmap(
            z=intensity_matrix,
            x=class_names,
            y=class_names,
            colorscale='viridis',
            colorbar=dict(title="Intensity")
        ))

        fig.update_layout(
            title=title,
            xaxis_title="To Class",
            yaxis_title="From Class",
            width=800,
            height=600
        )

        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)

    return generated_files


def create_transition_matrix_plot(
    transition_matrix: np.ndarray,
    class_names: List[str] = None,
    title: str = "Land Use Transition Matrix",
    output_dir: Union[str, Path] = "outputs",
    filename: str = "transition_matrix",
    save_png: bool = True,
    save_html: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Create transition matrix plot using modern visualizer.

    Parameters
    ----------
    transition_matrix : np.ndarray
        Transition matrix data
    class_names : list of str, optional
        Names of land use classes
    title : str
        Plot title
    output_dir : str or Path
        Directory to save outputs
    filename : str
        Base filename
    save_png : bool
        Save PNG version
    save_html : bool
        Save HTML version
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    dict
        Dictionary with paths to saved files
    """
    return create_intensity_matrix_plot(
        transition_matrix, class_names, title,
        output_dir, filename, save_png, save_html, **kwargs
    )


def generate_all_visualizations(
    intensity_data: Dict[str, Any],
    output_dir: Union[str, Path] = "outputs",
    **kwargs
) -> Dict[str, Any]:
    """
    Generate all visualizations for intensity analysis results.

    Parameters
    ----------
    intensity_data : dict
        Intensity analysis results
    output_dir : str or Path
        Directory to save visualizations
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    dict
        Dictionary of created visualizations
    """
    output_path = _ensure_output_dir(output_dir)
    results = {}

    # Create intensity matrix heatmap
    if 'intensity_matrix' in intensity_data:
        print("📊 Creating intensity matrix...")
        results['intensity_matrix'] = create_intensity_matrix_plot(
            intensity_data['intensity_matrix'],
            intensity_data.get('class_names'),
            output_dir=output_path,
            filename="intensity_matrix",
            **kwargs
        )

    # Create transition matrix
    if 'transition_matrix' in intensity_data:
        print("📊 Creating transition matrix...")
        results['transition_matrix'] = create_transition_matrix_plot(
            intensity_data['transition_matrix'],
            intensity_data.get('class_names'),
            output_dir=output_path,
            filename="transition_matrix_modern",
            **kwargs
        )

    # Create change map if available
    if 'change_map' in intensity_data:
        print("📊 Creating change map...")
        # This would require additional implementation for spatial maps
        pass

    # Create time series if available
    if 'time_series' in intensity_data:
        print("📊 Creating time series...")
        # This would require additional implementation
        pass

    return results


# Legacy compatibility functions
def enhanced_sankey_diagram(*args, **kwargs):
    """Legacy compatibility function. Use plot_sankey_diagram instead."""
    warnings.warn("enhanced_sankey_diagram is deprecated. Use plot_sankey_diagram instead.",
                  DeprecationWarning, stacklevel=2)
    return plot_sankey_diagram(*args, **kwargs)


def enhanced_chord_diagram(*args, **kwargs):
    """Legacy compatibility function. Use plot_chord_diagram instead."""
    warnings.warn("enhanced_chord_diagram is deprecated. Use plot_chord_diagram instead.",
                  DeprecationWarning, stacklevel=2)
    return plot_chord_diagram(*args, **kwargs)


# Export all functions
__all__ = [
    'plot_intensity_analysis',
    'plot_sankey_diagram',
    'plot_chord_diagram',
    'plot_net_gain_loss',
    'create_summary_plots',
    'create_intensity_matrix_plot',
    'create_transition_matrix_plot',
    'generate_all_visualizations',
    # Legacy functions
    'enhanced_sankey_diagram',
    'enhanced_chord_diagram',
]
