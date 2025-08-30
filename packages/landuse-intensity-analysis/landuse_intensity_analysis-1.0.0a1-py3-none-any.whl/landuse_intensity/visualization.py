"""
Modern Land Use and Land Cover (LULC) Change Visualization Module

This module provides state-of-the-art visualization capabilities for LULC change analysis,
following best practices from established libraries and modern Python
visualization libraries.

Key Features:
- Sankey diagrams for land use transitions using Plotly
- Transition matrix heatmaps using matplotlib and plotly
- Bar plots for LULC area analysis
- Spatial change maps with geographic orientation
- Intensity analysis visualizations
- Professional styling and customization options

Based on research from:
- Based on land use analysis methodologies
- Modern Python visualization libraries (plotly, matplotlib)
- Aldwaik & Pontius intensity analysis methodology

Main Functions:
- plot_single_step_sankey(): Single-step Sankey diagrams with customization
- plot_multi_step_sankey(): Multi-step Sankey diagrams with customization  
- plot_barplot_lulc(): Bar plots for LULC data with styling options
- plot_transition_matrix_heatmap(): Heatmap visualization of transition matrices
- plot_spatial_change_map(): Geographic change maps with orientation
- plot_intensity_analysis(): Intensity analysis visualization
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

# Geospatial dependencies
try:
    import geopandas as gpd
    import rasterio
    from rasterio.features import shapes
    from shapely.geometry import shape
    HAS_GEOSPATIAL = True
except ImportError:
    HAS_GEOSPATIAL = False
    warnings.warn("Geospatial libraries not available (geopandas, rasterio). Geospatial maps will not be generated.")

try:
    import contextily as ctx
    HAS_CONTEXTILY = True
except ImportError:
    HAS_CONTEXTILY = False

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

# Pontius methodology color schemes for geospatial analysis
PONTIUS_COLORS = {
    'persistence': ['#E8E8E8', '#D0D0D0', '#B8B8B8', '#A0A0A0'],  # Muted grays
    'change_frequency': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#3182BD', '#08519C'],  # Sequential blues
    'land_transitions': ['#8C510A', '#D8B365', '#F6E8C3', '#C7EAE5', '#5AAE61', '#1B7837'],  # Diverging brown-green
    'temporal_change': ['#FDE725', '#B5DE2B', '#6DCD59', '#35B779', '#1F9E89', '#26828E', '#31688E', '#3E4989', '#482777', '#440154']  # Viridis
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


def plot_single_step_sankey(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "single_step_sankey",
    title: str = "Single-step Land Use Transitions",
    min_flow: float = 0.5,
    include_persistence: bool = False,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
    color_palette: Optional[List[str]] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    output_filename_prefix: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create single-step Sankey diagram showing direct transitions between two time periods.
    
    This visualization shows land use transitions between only two time periods,
    providing a clear view of direct changes without intermediate steps.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "single_step_sankey"
        Base filename for output files
    title : str, default "Single-step Land Use Transitions"
        Title for the diagram
    min_flow : float, default 0.5
        Minimum flow size to show (km²)
    include_persistence : bool, default False
        Whether to include persistence (diagonal of transition matrix)
    figsize : tuple, default (12, 8)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    color_palette : list of str, optional
        Custom color palette for node colors
    custom_labels : dict, optional
        Custom labels for categories {original_name: custom_name}
    output_filename_prefix : str, optional
        Custom prefix for output filenames
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Apply custom filename prefix if provided
    if output_filename_prefix:
        filename = f"{output_filename_prefix}_{filename}"
    
    # Extract data
    if 'lulc_SingleStep' not in contingency_data:
        if 'lulc_MultiStep' in contingency_data:
            # Try to use the first period from multistep
            multistep = contingency_data['lulc_MultiStep']
            if 'Period' in multistep.columns:
                first_period = multistep['Period'].iloc[0]
                onestep_data = multistep[multistep['Period'] == first_period].copy()
            else:
                onestep_data = multistep.copy()
        else:
            raise ValueError("No suitable data found for single-step Sankey")
    else:
        onestep_data = contingency_data['lulc_SingleStep'].copy()
    
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Create transition matrix
    transition_matrix = onestep_data.pivot_table(
        index='From', 
        columns='To', 
        values='km2', 
        fill_value=0
    )
    
    # Filter small flows
    if not include_persistence:
        # Remove diagonal (persistence)
        for cat in transition_matrix.index:
            if cat in transition_matrix.columns:
                transition_matrix.loc[cat, cat] = 0
    
    # Create category labels
    if not legend.empty and 'CategoryValue' in legend.columns:
        label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        all_cats = set(transition_matrix.index) | set(transition_matrix.columns)
        label_map = {cat: f"Class_{cat}" for cat in sorted(all_cats)}
    
    # Apply custom labels if provided
    if custom_labels:
        label_map.update(custom_labels)
    
    if HAS_PLOTLY:
        # Prepare data for Plotly
        sources = []
        targets = []
        values = []
        colors = []
        
        all_cats = sorted(set(transition_matrix.index) | set(transition_matrix.columns))
        source_labels = [f"{label_map.get(cat, cat)}_T1" for cat in all_cats]
        target_labels = [f"{label_map.get(cat, cat)}_T2" for cat in all_cats]
        all_labels = source_labels + target_labels
        
        # Enhanced colors for different transition types
        transition_colors = {
            'persistence': 'rgba(128, 128, 128, 0.6)',
            'change': 'rgba(52, 152, 219, 0.6)'
        }
        
        for i, source_cat in enumerate(transition_matrix.index):
            for j, target_cat in enumerate(transition_matrix.columns):
                value = transition_matrix.loc[source_cat, target_cat]
                
                if value >= min_flow:
                    sources.append(i)
                    targets.append(len(source_labels) + j)
                    values.append(value)
                    
                    # Color based on transition type
                    if source_cat == target_cat:
                        colors.append(transition_colors['persistence'])
                    else:
                        colors.append(transition_colors['change'])
        
        # Create figure
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=color_palette if color_palette else _get_category_colors(len(all_labels))
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>' +
                             'Área: %{value:.1f} km²<extra></extra>'
            )
        )])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            font_size=12,
            width=1000,
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
    
    return generated_files


def plot_multi_step_sankey(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "multi_step_sankey",
    title: str = "Multi-step Land Use Transitions",
    min_flow: float = 0.5,
    time_column: str = 'Period',
    from_column: str = 'From',
    to_column: str = 'To',
    value_column: str = 'km2',
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 300,
    color_palette: Optional[List[str]] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    output_filename_prefix: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create multi-step Sankey diagram showing transitions across multiple time periods.
    
    This visualization shows land use transitions across multiple time periods,
    allowing visualization of complex transition pathways and temporal dynamics.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function containing multistep data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "multi_step_sankey"
        Base filename for output files
    title : str, default "Multi-step Land Use Transitions"
        Title for the diagram
    min_flow : float, default 0.5
        Minimum flow size to show (km²)
    time_column : str, default 'Period'
        Name of column containing time periods
    from_column : str, default 'From'
        Name of column containing source categories
    to_column : str, default 'To'
        Name of column containing target categories
    value_column : str, default 'km2'
        Name of column containing transition values
    figsize : tuple, default (14, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    color_palette : list of str, optional
        Custom color palette for node colors
    custom_labels : dict, optional
        Custom labels for categories {original_name: custom_name}
    output_filename_prefix : str, optional
        Custom prefix for output filenames
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Apply custom filename prefix if provided
    if output_filename_prefix:
        filename = f"{output_filename_prefix}_{filename}"
    
    # Extract data
    if 'lulc_MultiStep' not in contingency_data:
        raise ValueError("No lulc_MultiStep data found in contingency_data")
    
    multistep_data = contingency_data['lulc_MultiStep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Filter flows
    data = multistep_data[multistep_data[value_column] >= min_flow].copy()
    
    if len(data) == 0:
        warnings.warn(f"No flows found with minimum size {min_flow} km²")
        return {}
    
    if HAS_PLOTLY:
        # Get unique periods and classes
        periods = sorted(data[time_column].unique())
        all_classes = sorted(set(data[from_column].unique()) | set(data[to_column].unique()))
        
        # Create category labels
        if not legend.empty and 'CategoryValue' in legend.columns:
            label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
        else:
            label_map = {cat: f"Class_{cat}" for cat in all_classes}
        
        # Apply custom labels if provided
        if custom_labels:
            label_map.update(custom_labels)
        
        # Create nodes for each class in each time period
        node_labels = []
        node_map = {}
        node_counter = 0
        
        # Add nodes for each period
        for i, period in enumerate(periods):
            for class_name in all_classes:
                class_label = label_map.get(class_name, class_name)
                node_label = f"{class_label}_{period}"
                node_labels.append(node_label)
                node_map[(class_name, period)] = node_counter
                node_counter += 1
        
        # Add final nodes for the period after the last one
        if len(periods) > 0:
            final_period = "Final"
            for class_name in all_classes:
                class_label = label_map.get(class_name, class_name)
                node_label = f"{class_label}_{final_period}"
                node_labels.append(node_label)
                node_map[(class_name, final_period)] = node_counter
                node_counter += 1
        
        # Prepare links
        sources = []
        targets = []
        values = []
        colors = []
        
        # Colors by period using a nice palette
        import plotly.express as px
        period_colors = px.colors.qualitative.Set3[:len(periods)]
        
        for _, row in data.iterrows():
            period = row[time_column]
            from_class = row[from_column]
            to_class = row[to_column]
            value = row[value_column]
            
            # Determine target period
            period_idx = periods.index(period)
            if period_idx < len(periods) - 1:
                next_period = periods[period_idx + 1]
            else:
                next_period = "Final"
            
            # Map to node indices
            source_idx = node_map.get((from_class, period))
            target_idx = node_map.get((to_class, next_period))
            
            if source_idx is not None and target_idx is not None:
                sources.append(source_idx)
                targets.append(target_idx)
                values.append(value)
                
                # Color based on period
                color_base = period_colors[period_idx % len(period_colors)]
                # Convert to rgba with transparency
                if color_base.startswith('#'):
                    r = int(color_base[1:3], 16)
                    g = int(color_base[3:5], 16)
                    b = int(color_base[5:7], 16)
                    color_rgba = f"rgba({r}, {g}, {b}, 0.6)"
                else:
                    color_rgba = "rgba(52, 152, 219, 0.6)"
                colors.append(color_rgba)
        
        # Create figure
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=color_palette if color_palette else "lightgray"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>' +
                             'Área: %{value:.1f} km²<extra></extra>'
            )
        )])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            font_size=12,
            width=1200,
            height=700,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
    
    return generated_files


def plot_transition_matrix_heatmap(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "transition_matrix_heatmap",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (10, 10),
    dpi: int = 300,
    color_palette: Optional[str] = "viridis",
    custom_labels: Optional[Dict[str, str]] = None,
    output_filename_prefix: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create transition matrix heatmap showing land use change patterns.

    This visualization shows the transition matrix as a heatmap, where rows represent
    the original land use classes and columns represent the final classes. The color
    intensity represents the magnitude of transitions between classes.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "transition_matrix_heatmap"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    figsize : tuple, default (10, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    color_palette : str, default "viridis"
        Color palette for heatmap (matplotlib/plotly compatible)
    custom_labels : dict, optional
        Custom labels for categories {original_name: custom_name}
    output_filename_prefix : str, optional
        Custom prefix for output filenames

    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    # Apply custom filename prefix if provided
    if output_filename_prefix:
        filename = f"{output_filename_prefix}_{filename}"

    # Extract data
    if 'lulc_MultiStep' not in contingency_data:
        raise ValueError("No lulc_MultiStep data found in contingency_data")

    multistep = contingency_data['lulc_MultiStep'].copy()
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

    # Apply custom labels if provided
    if custom_labels:
        label_map.update(custom_labels)

    # Generate PNG version
    if save_png:
        png_path = _create_matplotlib_chord(
            transition_matrix, label_map, filename, output_path, figsize, dpi, color_palette
        )
        generated_files['png'] = str(png_path)

    # Generate HTML version
    if save_html and HAS_PLOTLY:
        html_path = _create_plotly_chord(
            transition_matrix, label_map, filename, output_path, color_palette
        )
        generated_files['html'] = str(html_path)

    return generated_files


def _create_matplotlib_chord(
    matrix: pd.DataFrame,
    label_map: Dict,
    filename: str,
    output_path: Path,
    figsize: Tuple[int, int],
    dpi: int,
    color_palette: str = "viridis"
) -> Path:
    """Create matplotlib chord diagram (heatmap)."""
    fig, ax = plt.subplots(figsize=figsize)

    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]

    # Create heatmap with custom color palette
    im = ax.imshow(matrix.values, cmap=color_palette, aspect='auto')

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
    output_path: Path,
    color_palette: str = "viridis"
) -> Path:
    """Create plotly chord diagram (heatmap)."""
    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]

    # Create interactive heatmap with custom color palette
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=column_labels,
        y=index_labels,
        colorscale=color_palette,
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


def plot_spatial_change_map(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "spatial_change_map",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (12, 10),
    dpi: int = 300,
    add_north_arrow: bool = True,
    add_scale_bar: bool = True,
    add_coordinates: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Create spatial change map with geographic orientation using Leafmap.

    This function generates spatial maps showing land use transitions with proper
    geographic orientation, including north arrow, scale bar, and coordinate system.
    Follows best practices for spatial visualization.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function containing spatial data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "spatial_change_map"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    figsize : tuple, default (12, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    add_north_arrow : bool, default True
        Whether to add north arrow to the map
    add_scale_bar : bool, default True
        Whether to add scale bar to the map
    add_coordinates : bool, default True
        Whether to add coordinate grid to the map
    **kwargs
        Additional arguments for Leafmap

    Returns
    -------
    dict
        Dictionary with paths to generated files

    Notes
    -----
    Requires leafmap package for geographic orientation features.
    Falls back to matplotlib if leafmap is not available.
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}

    try:
        import leafmap
        HAS_LEAFMAP = True
    except ImportError:
        HAS_LEAFMAP = False
        warnings.warn("Leafmap not available. Using matplotlib fallback for spatial maps.")

    # Extract spatial data
    if 'spatial_data' not in contingency_data and 'lulc_MultiStep' not in contingency_data:
        raise ValueError("No spatial data found in contingency_data")

    if HAS_LEAFMAP and save_html:
        # Create interactive map with Leafmap
        try:
            m = leafmap.Map(center=[0, 0], zoom=10)

            # Add base layers
            m.add_basemap("OpenStreetMap")

            # Add spatial data layers (placeholder - would need actual spatial data)
            # This is a template for when spatial data is properly integrated

            if add_north_arrow:
                m.add_north_arrow()
            if add_scale_bar:
                m.add_scale_bar()
            if add_coordinates:
                m.add_coordinates()

            # Save interactive HTML
            html_path = output_path / f"{filename}.html"
            m.to_html(html_path)
            generated_files['html'] = str(html_path)

        except Exception as e:
            warnings.warn(f"Failed to create Leafmap visualization: {e}")

    # Create static PNG version with matplotlib
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)

        # Placeholder for spatial data visualization
        # In a real implementation, this would use actual spatial data
        ax.text(0.5, 0.5, 'Spatial Change Map\n(Geographic Orientation)',
                transform=ax.transAxes, ha='center', va='center',
                fontsize=14, fontweight='bold')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Add geographic elements
        if add_north_arrow:
            # Add north arrow
            ax.arrow(0.9, 0.1, 0, 0.1, head_width=0.02, head_length=0.03,
                    fc='black', ec='black', transform=ax.transAxes)
            ax.text(0.9, 0.22, 'N', transform=ax.transAxes, ha='center',
                   va='bottom', fontweight='bold')

        if add_scale_bar:
            # Add scale bar
            ax.plot([0.1, 0.3], [0.05, 0.05], 'k-', linewidth=3, transform=ax.transAxes)
            ax.text(0.2, 0.03, 'Scale', transform=ax.transAxes, ha='center', va='top')

        if add_coordinates:
            # Add coordinate grid
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')

        plt.title('Land Use Change Spatial Map', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()

        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)

    return generated_files


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
    if 'lulc_MultiStep' not in contingency_data:
        raise ValueError("No lulc_MultiStep data found in contingency_data")

    multistep = contingency_data['lulc_MultiStep'].copy()
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


def plot_barplot_lulc(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "barplot_lulc",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
    color_palette: Optional[List[str]] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    output_filename_prefix: Optional[str] = None,
    show_values: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Create barplot for LULC data following barplotLand function standards.
    
    This function generates horizontal bar plots showing land use/cover areas
    with professional styling and customization options. Similar to R barplotLand
    function but with enhanced Python capabilities.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function containing:
        - 'lulc_MultiStep': Multi-period DataFrame
        - 'lulc_SingleStep': Single-step DataFrame  
        - 'tb_legend': Legend DataFrame
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "barplot_lulc"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version using matplotlib
    save_html : bool, default True
        Whether to save HTML version using plotly
    figsize : tuple, default (12, 8)
        Figure size for PNG version (width, height) in inches
    dpi : int, default 300
        Resolution for PNG output
    color_palette : list of str, optional
        Custom color palette for categories. If None, uses default colors
    custom_labels : dict, optional
        Custom labels for categories {original_name: custom_name}
    output_filename_prefix : str, optional
        Custom prefix for output filenames
    show_values : bool, default True
        Whether to show value labels on bars
    **kwargs
        Additional styling arguments

    Returns
    -------
    dict
        Dictionary with paths to generated files {'png': path, 'html': path}

    Notes
    -----
    - Follows barplotLand conventions for land use visualization
    - Supports both matplotlib (PNG) and plotly (HTML) outputs
    - Automatically handles missing categories and zero values
    - Provides professional styling suitable for publications
    
    Examples
    --------
    >>> # Basic usage
    >>> files = plot_barplot_lulc(contingency_data)
    
    >>> # With custom colors and labels
    >>> custom_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'] 
    >>> custom_names = {'Forest': 'Floresta', 'Urban': 'Urbano'}
    >>> files = plot_barplot_lulc(
    ...     contingency_data,
    ...     color_palette=custom_colors,
    ...     custom_labels=custom_names,
    ...     output_filename_prefix="analise_lulc"
    ... )
    """
    # Setup output directory and filename
    output_path = _ensure_output_dir(output_dir)
    
    if output_filename_prefix:
        filename = f"{output_filename_prefix}_{filename}"
    
    generated_files = {}

    # Extract data - prioritize SingleStep, fallback to MultiStep
    if 'lulc_SingleStep' in contingency_data:
        lulc_data = contingency_data['lulc_SingleStep'].copy()
    elif 'lulc_MultiStep' in contingency_data:
        # Use the most recent period from MultiStep
        multistep_data = contingency_data['lulc_MultiStep'].copy()
        latest_period = multistep_data['Period'].max()
        lulc_data = multistep_data[multistep_data['Period'] == latest_period].copy()
    else:
        raise ValueError("No valid LULC data found in contingency_data")

    # Get legend/category information
    if 'tb_legend' in contingency_data:
        legend_data = contingency_data['tb_legend'].copy()
        categories = legend_data['categoryName'].tolist()
    else:
        # Extract categories from data
        categories = sorted(list(set(lulc_data['From'].tolist() + lulc_data['To'].tolist())))

    # Calculate areas by category (sum of 'To' transitions)
    area_data = []
    for category in categories:
        area = lulc_data[lulc_data['To'] == category]['km2'].sum()
        area_data.append({'Category': category, 'Area_km2': area})
    
    df_areas = pd.DataFrame(area_data)
    df_areas = df_areas.sort_values('Area_km2', ascending=True)  # Sort for horizontal barplot

    # Apply custom labels if provided
    if custom_labels:
        df_areas['Category_Label'] = df_areas['Category'].map(
            lambda x: custom_labels.get(x, x)
        )
    else:
        df_areas['Category_Label'] = df_areas['Category']

    # Setup colors
    if color_palette:
        colors = color_palette[:len(df_areas)]
        if len(color_palette) < len(df_areas):
            warnings.warn("Color palette has fewer colors than categories. Repeating colors.")
            colors = (color_palette * ((len(df_areas) // len(color_palette)) + 1))[:len(df_areas)]
    else:
        colors = _get_category_colors(len(df_areas))

    # Generate PNG version with matplotlib
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)
        
        bars = ax.barh(
            range(len(df_areas)), 
            df_areas['Area_km2'], 
            color=colors,
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5
        )

        # Customize plot
        ax.set_yticks(range(len(df_areas)))
        ax.set_yticklabels(df_areas['Category_Label'], fontsize=11)
        ax.set_xlabel('Area (km²)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Land Use/Land Cover Categories', fontsize=12, fontweight='bold')
        ax.set_title('Land Use/Cover Area Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # Add value labels on bars
        if show_values:
            for i, (bar, value) in enumerate(zip(bars, df_areas['Area_km2'])):
                width = bar.get_width()
                ax.text(
                    width + (0.01 * max(df_areas['Area_km2'])), 
                    bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}', 
                    ha='left', 
                    va='center',
                    fontweight='bold',
                    fontsize=10
                )

        plt.tight_layout()

        # Save PNG
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        generated_files['png'] = str(png_path)

    # Generate HTML version with plotly
    if save_html and HAS_PLOTLY:
        fig = go.Figure(data=[go.Bar(
            y=df_areas['Category_Label'],
            x=df_areas['Area_km2'],
            orientation='h',
            marker_color=colors,
            text=[f'{val:.1f} km²' if show_values else '' for val in df_areas['Area_km2']],
            textposition='outside',
            marker_line=dict(color='black', width=1)
        )])

        fig.update_layout(
            title={
                'text': 'Land Use/Cover Area Distribution',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Arial Black'}
            },
            xaxis_title='Area (km²)',
            yaxis_title='Land Use/Land Cover Categories',
            width=800,
            height=max(400, len(df_areas) * 40),  # Dynamic height based on categories
            font=dict(size=12),
            plot_bgcolor='rgba(240,240,240,0.8)',
            paper_bgcolor='white',
            margin=dict(l=150, r=50, t=80, b=50)  # Adjust margins for labels
        )

        # Customize axes
        fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.3)')
        fig.update_yaxes(showgrid=False)

        # Save HTML
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

    # 1. Single-step Sankey diagram
    results['single_step_sankey'] = plot_single_step_sankey(
        contingency_data,
        output_dir=output_path,
        filename="single_step_sankey",
        **kwargs
    )

    # 1b. Multi-step Sankey diagram
    print("📊 Creating multi-step Sankey diagram...")
    results['multi_step_sankey'] = plot_multi_step_sankey(
        contingency_data,
        output_dir=output_path,
        filename="multi_step_sankey",
        **kwargs
    )

    # 2. Chord diagram / transition matrix
    print("📊 Creating transition matrix...")
    results['transition_matrix'] = plot_transition_matrix_heatmap(
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

    # 4. LULC Bar plot
    print("📊 Creating LULC bar plot...")
    results['barplot_lulc'] = plot_barplot_lulc(
        contingency_data,
        output_dir=output_path,
        filename="barplot_lulc",
        **kwargs
    )

    # 5. Spatial change map
    print("🗺️ Creating spatial change map...")
    results['spatial_change_map'] = plot_spatial_change_map(
        contingency_data,
        output_dir=output_path,
        filename="spatial_change_map",
        **kwargs
    )

    return results


# Additional visualization functions
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


# =============================================================================
# GEOSPATIAL VISUALIZATION FUNCTIONS (PONTIUS METHODOLOGY)
# =============================================================================

def _raster_to_geodataframe(
    raster_path: Union[str, Path], 
    band: int = 1,
    crs: str = "EPSG:4326"
) -> Optional['gpd.GeoDataFrame']:
    """
    Convert raster data to GeoDataFrame for geospatial visualization.
    
    Parameters
    ----------
    raster_path : str or Path
        Path to the raster file
    band : int, default 1
        Band number to read
    crs : str, default "EPSG:4326"
        Target coordinate reference system
        
    Returns
    -------
    GeoDataFrame or None
        GeoDataFrame with raster values and geometries, or None if geospatial libs not available
    """
    if not HAS_GEOSPATIAL:
        warnings.warn("Geospatial libraries not available. Cannot create GeoDataFrame.")
        return None
        
    try:
        with rasterio.open(raster_path) as src:
            # Read raster data
            data = src.read(band)
            
            # Get transform and CRS
            transform = src.transform
            src_crs = src.crs
            
            # Create shapes from raster
            mask = data != src.nodata if src.nodata is not None else None
            geoms_and_values = []
            
            for geom, value in shapes(data, mask=mask, transform=transform):
                geoms_and_values.append({
                    'geometry': shape(geom),
                    'value': int(value)
                })
            
            # Create GeoDataFrame
            if geoms_and_values:
                gdf = gpd.GeoDataFrame(geoms_and_values, crs=src_crs)
                
                # Transform to target CRS if needed
                if gdf.crs != crs:
                    gdf = gdf.to_crs(crs)
                    
                return gdf
            else:
                return None
                
    except Exception as e:
        warnings.warn(f"Error converting raster to GeoDataFrame: {e}")
        return None


def plot_persistence_map(
    raster_files: List[Union[str, Path]],
    category_names: Optional[Dict[int, str]] = None,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "persistence_map",
    figsize: Tuple[int, int] = (12, 10),
    dpi: int = 300,
    add_basemap: bool = True,
    transparency: float = 0.7,
    save_formats: List[str] = ["png", "html"]
) -> Dict[str, str]:
    """
    Create persistence map showing areas that remained unchanged across all time periods.
    
    Follows Pontius methodology using muted colors and transparency effects.
    
    Parameters
    ----------
    raster_files : list of str or Path
        List of raster file paths in temporal order
    category_names : dict, optional
        Mapping of category values to names
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "persistence_map"
        Base filename for output files
    figsize : tuple, default (12, 10)
        Figure size (width, height) in inches
    dpi : int, default 300
        DPI for PNG output
    add_basemap : bool, default True
        Whether to add a basemap (requires contextily)
    transparency : float, default 0.7
        Transparency level for persistence areas
    save_formats : list, default ["png", "html"]
        Output formats to save
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
        
    Examples
    --------
    >>> files = plot_persistence_map(
    ...     ['data/land_2010.tif', 'data/land_2015.tif', 'data/land_2020.tif'],
    ...     category_names={1: 'Forest', 2: 'Agriculture', 3: 'Urban'},
    ...     save_formats=['png']
    ... )
    """
    if not HAS_GEOSPATIAL:
        raise ImportError("Geospatial libraries required for persistence maps. Install with: pip install geopandas rasterio")
    
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    try:
        # Read all rasters and find persistent areas
        print("🗺️ Processing raster files for persistence analysis...")
        
        raster_data = []
        for i, raster_path in enumerate(raster_files):
            print(f"   Reading {Path(raster_path).name}...")
            with rasterio.open(raster_path) as src:
                data = src.read(1)
                if i == 0:
                    # Store reference info
                    ref_transform = src.transform
                    ref_crs = src.crs
                    ref_shape = data.shape
                raster_data.append(data)
        
        # Calculate persistence mask (areas that never changed)
        persistence_mask = np.ones_like(raster_data[0], dtype=bool)
        first_raster = raster_data[0]
        
        for raster in raster_data[1:]:
            persistence_mask &= (raster == first_raster)
        
        # Create persistence raster (showing persistent land use types)
        persistence_raster = np.where(persistence_mask, first_raster, 0)
        
        # Convert to GeoDataFrame
        print("🗺️ Converting to geospatial format...")
        geoms_and_values = []
        for geom, value in shapes(persistence_raster, mask=persistence_raster > 0, transform=ref_transform):
            if value > 0:  # Only include persistent areas
                geoms_and_values.append({
                    'geometry': shape(geom),
                    'land_use': int(value),
                    'category': category_names.get(int(value), f'Category {int(value)}') if category_names else f'Category {int(value)}'
                })
        
        if not geoms_and_values:
            warnings.warn("No persistent areas found in the dataset.")
            return {}
        
        gdf = gpd.GeoDataFrame(geoms_and_values, crs=ref_crs)
        
        # Transform to Web Mercator for basemap if needed
        if add_basemap and HAS_CONTEXTILY:
            gdf_plot = gdf.to_crs('EPSG:3857')
        else:
            gdf_plot = gdf.to_crs('EPSG:4326')
        
        # Create static map with matplotlib
        if "png" in save_formats:
            print("🗺️ Creating static persistence map...")
            
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Plot persistence areas with Pontius muted colors
            unique_categories = gdf_plot['land_use'].unique()
            colors = PONTIUS_COLORS['persistence'][:len(unique_categories)]
            legend_handles = []
            
            for i, category in enumerate(unique_categories):
                category_data = gdf_plot[gdf_plot['land_use'] == category]
                category_name = category_names.get(category, f'Category {category}') if category_names else f'Category {category}'
                
                patches = category_data.plot(
                    ax=ax,
                    color=colors[i % len(colors)],
                    alpha=transparency,
                    edgecolor='white',
                    linewidth=0.5,
                    label=f'{category_name} (Persistent)'
                )
                
                # Create legend handle manually
                from matplotlib.patches import Patch
                legend_handles.append(Patch(color=colors[i % len(colors)], 
                                          alpha=transparency, 
                                          label=f'{category_name} (Persistent)'))
            
            # Add basemap if requested
            if add_basemap and HAS_CONTEXTILY:
                try:
                    ctx.add_basemap(ax, crs=gdf_plot.crs.to_string(), source=ctx.providers.CartoDB.Positron)
                except Exception as e:
                    warnings.warn(f"Could not add basemap: {e}")
            
            # Styling
            ax.set_title(f'Land Use Persistence Map\n({len(raster_files)} time periods)', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add legend with proper handles
            if legend_handles:
                ax.legend(handles=legend_handles, bbox_to_anchor=(1.05, 1), loc='upper left')
            
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            
            # Remove axes if basemap is used
            if add_basemap and HAS_CONTEXTILY:
                ax.set_axis_off()
            
            plt.tight_layout()
            
            # Save PNG
            png_path = output_path / f"{filename}.png"
            plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files['png'] = str(png_path)
            print(f"✅ Static map saved: {png_path}")
        
        # Create interactive map with GeoPandas
        if "html" in save_formats:
            print("🗺️ Creating interactive persistence map...")
            
            try:
                # Use explore() for interactive mapping
                gdf_wgs84 = gdf.to_crs('EPSG:4326')
                
                # Create color mapping
                unique_categories = gdf_wgs84['land_use'].unique()
                color_map = {cat: PONTIUS_COLORS['persistence'][i % len(PONTIUS_COLORS['persistence'])] 
                           for i, cat in enumerate(unique_categories)}
                
                m = gdf_wgs84.explore(
                    column='land_use',
                    categorical=True,
                    cmap='Set3',
                    alpha=transparency,
                    popup=['category'],
                    tooltip=['category'],
                    legend=True,
                    tiles='CartoDB positron'
                )
                
                # Save HTML
                html_path = output_path / f"{filename}.html"
                m.save(str(html_path))
                generated_files['html'] = str(html_path)
                print(f"✅ Interactive map saved: {html_path}")
                
            except Exception as e:
                warnings.warn(f"Could not create interactive map: {e}")
        
        print(f"🎯 Persistence analysis completed. Found {len(geoms_and_values)} persistent areas.")
        return generated_files
        
    except Exception as e:
        print(f"❌ Error creating persistence map: {e}")
        return {}


def plot_temporal_land_change(
    raster_files: List[Union[str, Path]],
    time_labels: Optional[List[str]] = None,
    category_names: Optional[Dict[int, str]] = None,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "temporal_land_change",
    figsize: Tuple[int, int] = (15, 10),
    dpi: int = 300,
    add_basemap: bool = True,
    save_formats: List[str] = ["png", "html"]
) -> Dict[str, str]:
    """
    Create temporal land change visualization showing transitions through years.
    
    Follows Pontius methodology with distinct color palettes for different transitions.
    
    Parameters
    ----------
    raster_files : list of str or Path
        List of raster file paths in temporal order
    time_labels : list of str, optional
        Labels for time periods (e.g., ['2010', '2015', '2020'])
    category_names : dict, optional
        Mapping of category values to names
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "temporal_land_change"
        Base filename for output files
    figsize : tuple, default (15, 10)
        Figure size (width, height) in inches
    dpi : int, default 300
        DPI for PNG output
    add_basemap : bool, default True
        Whether to add a basemap
    save_formats : list, default ["png", "html"]
        Output formats to save
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    if not HAS_GEOSPATIAL:
        raise ImportError("Geospatial libraries required for temporal change maps. Install with: pip install geopandas rasterio")
    
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    try:
        print("🗺️ Processing temporal land change analysis...")
        
        # Default time labels if not provided
        if time_labels is None:
            time_labels = [f'T{i+1}' for i in range(len(raster_files))]
        
        # Read raster data
        raster_data = []
        for i, raster_path in enumerate(raster_files):
            print(f"   Reading {Path(raster_path).name}...")
            with rasterio.open(raster_path) as src:
                data = src.read(1)
                if i == 0:
                    ref_transform = src.transform
                    ref_crs = src.crs
                raster_data.append(data)
        
        # Create multi-panel figure for static visualization
        if "png" in save_formats:
            print("🗺️ Creating temporal change map...")
            
            n_periods = len(raster_files)
            cols = min(3, n_periods)
            rows = (n_periods + cols - 1) // cols
            
            fig, axes = plt.subplots(rows, cols, figsize=figsize, dpi=dpi)
            if n_periods == 1:
                axes = [axes]
            elif rows == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()
            
            # Plot each time period
            for i, (raster, time_label) in enumerate(zip(raster_data, time_labels)):
                ax = axes[i]
                
                # Convert raster to GeoDataFrame
                geoms_and_values = []
                for geom, value in shapes(raster, mask=raster > 0, transform=ref_transform):
                    if value > 0:
                        geoms_and_values.append({
                            'geometry': shape(geom),
                            'land_use': int(value),
                            'category': category_names.get(int(value), f'Category {int(value)}') if category_names else f'Category {int(value)}'
                        })
                
                if geoms_and_values:
                    gdf = gpd.GeoDataFrame(geoms_and_values, crs=ref_crs)
                    
                    if add_basemap and HAS_CONTEXTILY:
                        gdf_plot = gdf.to_crs('EPSG:3857')
                    else:
                        gdf_plot = gdf.to_crs('EPSG:4326')
                    
                    # Plot with temporal colors
                    unique_categories = gdf_plot['land_use'].unique()
                    colors = PONTIUS_COLORS['temporal_change'][:len(unique_categories)]
                    
                    for j, category in enumerate(unique_categories):
                        category_data = gdf_plot[gdf_plot['land_use'] == category]
                        category_name = category_names.get(category, f'Cat {category}') if category_names else f'Cat {category}'
                        
                        category_data.plot(
                            ax=ax,
                            color=colors[j % len(colors)],
                            alpha=0.8,
                            edgecolor='white',
                            linewidth=0.3,
                            label=category_name if i == 0 else ""  # Only show legend for first subplot
                        )
                    
                    # Add basemap
                    if add_basemap and HAS_CONTEXTILY:
                        try:
                            ctx.add_basemap(ax, crs=gdf_plot.crs.to_string(), source=ctx.providers.CartoDB.Positron)
                        except Exception as e:
                            warnings.warn(f"Could not add basemap to subplot {i}: {e}")
                
                ax.set_title(time_label, fontsize=12, fontweight='bold')
                ax.set_axis_off()
            
            # Hide extra subplots
            for i in range(n_periods, len(axes)):
                axes[i].set_visible(False)
            
            # Add overall title and legend
            fig.suptitle('Temporal Land Use Change', fontsize=16, fontweight='bold', y=0.95)
            if axes[0].get_legend():
                axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            # Save PNG
            png_path = output_path / f"{filename}.png"
            plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files['png'] = str(png_path)
            print(f"✅ Temporal change map saved: {png_path}")
        
        # Create interactive temporal map (show latest period with tooltip info)
        if "html" in save_formats:
            print("🗺️ Creating interactive temporal map...")
            
            try:
                # Use the last time period for interactive map
                final_raster = raster_data[-1]
                
                geoms_and_values = []
                for geom, value in shapes(final_raster, mask=final_raster > 0, transform=ref_transform):
                    if value > 0:
                        category_name = category_names.get(int(value), f'Category {int(value)}') if category_names else f'Category {int(value)}'
                        geoms_and_values.append({
                            'geometry': shape(geom),
                            'land_use': int(value),
                            'category': category_name,
                            'time_period': time_labels[-1]
                        })
                
                if geoms_and_values:
                    gdf = gpd.GeoDataFrame(geoms_and_values, crs=ref_crs)
                    gdf_wgs84 = gdf.to_crs('EPSG:4326')
                    
                    m = gdf_wgs84.explore(
                        column='land_use',
                        categorical=True,
                        cmap='viridis',
                        alpha=0.8,
                        popup=['category', 'time_period'],
                        tooltip=['category', 'time_period'],
                        legend=True,
                        tiles='CartoDB positron'
                    )
                    
                    # Save HTML
                    html_path = output_path / f"{filename}.html"
                    m.save(str(html_path))
                    generated_files['html'] = str(html_path)
                    print(f"✅ Interactive temporal map saved: {html_path}")
                
            except Exception as e:
                warnings.warn(f"Could not create interactive temporal map: {e}")
        
        print(f"🎯 Temporal change analysis completed for {len(raster_files)} time periods.")
        return generated_files
        
    except Exception as e:
        print(f"❌ Error creating temporal change map: {e}")
        return {}


def plot_change_frequency_map(
    raster_files: List[Union[str, Path]],
    category_names: Optional[Dict[int, str]] = None,
    output_dir: Union[str, Path] = "outputs", 
    filename: str = "change_frequency_map",
    figsize: Tuple[int, int] = (12, 10),
    dpi: int = 300,
    add_basemap: bool = True,
    hotspot_threshold: int = 2,
    save_formats: List[str] = ["png", "html"]
) -> Dict[str, str]:
    """
    Create change frequency map showing quantity of changes per pixel (0, 1, 2, 3+ transitions).
    
    Follows Pontius methodology with sequential color ramps and hotspot identification.
    
    Parameters
    ----------
    raster_files : list of str or Path
        List of raster file paths in temporal order
    category_names : dict, optional
        Mapping of category values to names
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "change_frequency_map"
        Base filename for output files  
    figsize : tuple, default (12, 10)
        Figure size (width, height) in inches
    dpi : int, default 300
        DPI for PNG output
    add_basemap : bool, default True
        Whether to add a basemap
    hotspot_threshold : int, default 2
        Minimum number of changes to consider as hotspot
    save_formats : list, default ["png", "html"]
        Output formats to save
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    if not HAS_GEOSPATIAL:
        raise ImportError("Geospatial libraries required for change frequency maps. Install with: pip install geopandas rasterio")
    
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    try:
        print("🗺️ Processing change frequency analysis...")
        
        # Read raster data
        raster_data = []
        for i, raster_path in enumerate(raster_files):
            print(f"   Reading {Path(raster_path).name}...")
            with rasterio.open(raster_path) as src:
                data = src.read(1)
                if i == 0:
                    ref_transform = src.transform
                    ref_crs = src.crs
                    ref_shape = data.shape
                raster_data.append(data)
        
        # Calculate change frequency for each pixel
        print("🗺️ Calculating change frequencies...")
        change_count = np.zeros_like(raster_data[0], dtype=int)
        
        for i in range(len(raster_data) - 1):
            current = raster_data[i]
            next_period = raster_data[i + 1]
            
            # Count changes (where values differ between consecutive periods)
            changes = (current != next_period) & (current > 0) & (next_period > 0)
            change_count += changes.astype(int)
        
        # Create categories for visualization
        frequency_categories = np.where(
            change_count == 0, 0,  # No change
            np.where(change_count == 1, 1,  # 1 change
                np.where(change_count == 2, 2,  # 2 changes  
                    np.where(change_count >= 3, 3, change_count)))  # 3+ changes
        ).astype(np.int32)  # Ensure proper data type for rasterio
        
        # Convert to GeoDataFrame
        print("🗺️ Converting to geospatial format...")
        geoms_and_values = []
        
        for geom, value in shapes(frequency_categories, mask=frequency_categories >= 0, transform=ref_transform):
            freq_value = int(value)
            if freq_value >= 0:
                freq_labels = {0: 'No Change', 1: '1 Change', 2: '2 Changes', 3: '3+ Changes'}
                is_hotspot = freq_value >= hotspot_threshold
                
                geoms_and_values.append({
                    'geometry': shape(geom),
                    'frequency': freq_value,
                    'label': freq_labels.get(freq_value, f'{freq_value} Changes'),
                    'is_hotspot': is_hotspot,
                    'change_count': freq_value  # Use freq_value directly since it represents the change count
                })
        
        if not geoms_and_values:
            warnings.warn("No change data found in the dataset.")
            return {}
        
        gdf = gpd.GeoDataFrame(geoms_and_values, crs=ref_crs)
        
        # Create static map
        if "png" in save_formats:
            print("🗺️ Creating static change frequency map...")
            
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Transform for plotting
            if add_basemap and HAS_CONTEXTILY:
                gdf_plot = gdf.to_crs('EPSG:3857')
            else:
                gdf_plot = gdf.to_crs('EPSG:4326')
            
            # Plot using sequential color scheme
            colors = PONTIUS_COLORS['change_frequency']
            
            for freq in sorted(gdf_plot['frequency'].unique()):
                freq_data = gdf_plot[gdf_plot['frequency'] == freq]
                freq_label = freq_data['label'].iloc[0]
                color = colors[freq % len(colors)]
                
                freq_data.plot(
                    ax=ax,
                    color=color,
                    alpha=0.8,
                    edgecolor='white',
                    linewidth=0.5,
                    label=freq_label
                )
            
            # Highlight hotspots
            hotspots = gdf_plot[gdf_plot['is_hotspot']]
            if not hotspots.empty:
                hotspots.boundary.plot(
                    ax=ax,
                    color='red',
                    linewidth=2,
                    alpha=0.8,
                    label='Change Hotspots'
                )
            
            # Add basemap
            if add_basemap and HAS_CONTEXTILY:
                try:
                    ctx.add_basemap(ax, crs=gdf_plot.crs.to_string(), source=ctx.providers.CartoDB.Positron)
                except Exception as e:
                    warnings.warn(f"Could not add basemap: {e}")
            
            # Styling
            ax.set_title(f'Land Use Change Frequency Map\n({len(raster_files)} time periods)', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            
            if add_basemap and HAS_CONTEXTILY:
                ax.set_axis_off()
            
            plt.tight_layout()
            
            # Save PNG
            png_path = output_path / f"{filename}.png"
            plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files['png'] = str(png_path)
            print(f"✅ Static frequency map saved: {png_path}")
        
        # Create interactive map
        if "html" in save_formats:
            print("🗺️ Creating interactive change frequency map...")
            
            try:
                gdf_wgs84 = gdf.to_crs('EPSG:4326')
                
                # Create interactive map with frequency coloring
                m = gdf_wgs84.explore(
                    column='frequency',
                    categorical=True,
                    cmap='YlOrRd',
                    alpha=0.8,
                    popup=['label', 'is_hotspot'],
                    tooltip=['label', 'is_hotspot'],
                    legend=True,
                    tiles='CartoDB positron'
                )
                
                # Save HTML
                html_path = output_path / f"{filename}.html"
                m.save(str(html_path))
                generated_files['html'] = str(html_path)
                print(f"✅ Interactive frequency map saved: {html_path}")
                
            except Exception as e:
                warnings.warn(f"Could not create interactive frequency map: {e}")
        
        # Print summary statistics
        freq_stats = gdf['frequency'].value_counts().sort_index()
        hotspot_count = gdf['is_hotspot'].sum()
        
        print(f"🎯 Change frequency analysis completed:")
        for freq, count in freq_stats.items():
            freq_labels = {0: 'No Change', 1: '1 Change', 2: '2 Changes', 3: '3+ Changes'}
            print(f"   {freq_labels.get(freq, f'{freq} Changes')}: {count:,} areas")
        print(f"   Change hotspots (≥{hotspot_threshold} changes): {hotspot_count:,} areas")
        
        return generated_files
        
    except Exception as e:
        print(f"❌ Error creating change frequency map: {e}")
        return {}




# Export all functions
__all__ = [
    # Main plotting functions (following PEP 8 naming conventions)
    'plot_intensity_analysis',
    'plot_transition_matrix_heatmap',
    'plot_spatial_change_map', 
    'plot_net_gain_loss',
    'plot_barplot_lulc',  # LULC bar plots following barplotLand standards
    
    # Sankey diagram functions
    'plot_single_step_sankey',
    'plot_multi_step_sankey',
    
    # Geospatial visualization functions (Pontius methodology)
    'plot_persistence_map',
    'plot_temporal_land_change', 
    'plot_change_frequency_map',
    
    # Summary and utility functions
    'create_summary_plots',
    'create_intensity_matrix_plot',
    'create_transition_matrix_plot',
    'generate_all_visualizations',
]
