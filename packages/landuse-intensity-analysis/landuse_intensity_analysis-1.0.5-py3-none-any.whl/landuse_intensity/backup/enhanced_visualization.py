"""
Enhanced visualization functions with automatic PNG and HTML generation.

This module provides improved visualization functions that:
1. Generate high-quality PNG files using matplotlib
2. Generate interactive HTML files using plotly
3. Have better documentation and error handling
4. Support multiple output formats automatically
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not available. Only matplotlib plots will be generated.")


def enhanced_sankey_diagram(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    title: str = "Land Use Change Flows",
    output_dir: Union[str, Path] = "outputs",
    filename: str = "sankey_diagram",
    area_km2: bool = True,
    min_flow: float = 0.01,
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create both static (PNG) and interactive (HTML) Sankey diagrams.
    
    Parameters
    ----------
    dataset : pd.DataFrame
        DataFrame with 'From', 'To', 'km2' or 'QtPixel' columns
    legend_table : pd.DataFrame, optional
        Legend mapping category values to names
    title : str
        Title for the diagram
    output_dir : str or Path
        Directory to save outputs
    filename : str
        Base filename (without extension)
    area_km2 : bool
        Use km2 (True) or pixel count (False)
    min_flow : float
        Minimum flow as fraction of total change
    save_png : bool
        Save static PNG version
    save_html : bool
        Save interactive HTML version
    figsize : tuple
        Figure size for PNG version
    dpi : int
        Resolution for PNG version
        
    Returns
    -------
    dict
        Dictionary with paths to saved files
    """
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"
    area_unit = "km²" if area_km2 else "pixels"
    
    # Filter out persistence and small flows
    flows = dataset[dataset["From"] != dataset["To"]].copy()
    
    if len(flows) == 0:
        warnings.warn("No transitions found (all From == To)")
        return {}
    
    # Apply minimum flow threshold
    total_change = flows[area_col].sum()
    min_threshold = total_change * min_flow
    flows = flows[flows[area_col] >= min_threshold]
    
    # Create category labels
    if legend_table is not None:
        label_map = dict(zip(legend_table['CategoryValue'], legend_table['CategoryName']))
    else:
        label_map = {cat: f"Class_{cat}" for cat in sorted(set(flows["From"].unique()) | set(flows["To"].unique()))}
    
    saved_files = {}
    
    # 1. Create matplotlib version (PNG)
    if save_png:
        png_path = _create_matplotlib_sankey(
            flows, label_map, title, area_col, area_unit, 
            output_dir / f"{filename}.png", figsize, dpi
        )
        saved_files['png'] = str(png_path)
    
    # 2. Create plotly version (HTML)
    if save_html and HAS_PLOTLY:
        html_path = _create_plotly_sankey(
            flows, label_map, title, area_col, area_unit,
            output_dir / f"{filename}.html"
        )
        saved_files['html'] = str(html_path)
    
    return saved_files


def _create_matplotlib_sankey(
    flows: pd.DataFrame,
    label_map: Dict,
    title: str,
    area_col: str,
    area_unit: str,
    output_path: Path,
    figsize: Tuple[int, int],
    dpi: int
) -> Path:
    """Create static Sankey diagram using matplotlib."""
    
    # For matplotlib, we'll create a flow matrix visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, facecolor='white')
    
    # Left plot: From categories (losses)
    from_data = flows.groupby('From')[area_col].sum().sort_values(ascending=False)
    from_labels = [label_map.get(cat, f"Class_{cat}") for cat in from_data.index]
    
    colors = sns.color_palette("Reds_r", len(from_data))
    bars1 = ax1.barh(range(len(from_data)), from_data.values, color=colors)
    ax1.set_yticks(range(len(from_data)))
    ax1.set_yticklabels(from_labels)
    ax1.set_xlabel(f'Lost Area ({area_unit})')
    ax1.set_title('Land Cover Losses', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars1, from_data.values)):
        ax1.text(value + max(from_data) * 0.01, i, f'{value:.1f}', 
                va='center', fontweight='bold')
    
    # Right plot: To categories (gains)
    to_data = flows.groupby('To')[area_col].sum().sort_values(ascending=False)
    to_labels = [label_map.get(cat, f"Class_{cat}") for cat in to_data.index]
    
    colors = sns.color_palette("Greens", len(to_data))
    bars2 = ax2.barh(range(len(to_data)), to_data.values, color=colors)
    ax2.set_yticks(range(len(to_data)))
    ax2.set_yticklabels(to_labels)
    ax2.set_xlabel(f'Gained Area ({area_unit})')
    ax2.set_title('Land Cover Gains', fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars2, to_data.values)):
        ax2.text(value + max(to_data) * 0.01, i, f'{value:.1f}', 
                va='center', fontweight='bold')
    
    plt.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout()
    
    # Save with high quality
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    return output_path


def _create_plotly_sankey(
    flows: pd.DataFrame,
    label_map: Dict,
    title: str,
    area_col: str,
    area_unit: str,
    output_path: Path
) -> Path:
    """Create interactive Sankey diagram using plotly."""
    
    # Get all unique categories
    all_categories = sorted(set(flows["From"].unique()) | set(flows["To"].unique()))
    
    # Create node labels
    node_labels = [label_map.get(cat, f"Class_{cat}") for cat in all_categories]
    
    # Create source and target indices
    source_list = []
    target_list = []
    value_list = []
    
    for _, row in flows.iterrows():
        source_idx = all_categories.index(row["From"])
        target_idx = all_categories.index(row["To"])
        source_list.append(source_idx)
        target_list.append(target_idx)
        value_list.append(row[area_col])
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="lightblue"
        ),
        link=dict(
            source=source_list,
            target=target_list,
            value=value_list,
            color="rgba(255, 0, 255, 0.4)"
        )
    )])
    
    fig.update_layout(
        title_text=title,
        font_size=12,
        width=1000,
        height=600
    )
    
    # Save as HTML
    fig.write_html(output_path)
    
    return output_path


def enhanced_chord_diagram(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    title: str = "Land Use Change Matrix",
    output_dir: Union[str, Path] = "outputs",
    filename: str = "chord_diagram",
    area_km2: bool = True,
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (10, 10),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create chord diagram showing land use transitions.
    
    Parameters
    ----------
    dataset : pd.DataFrame
        DataFrame with transition data
    legend_table : pd.DataFrame, optional
        Legend mapping category values to names
    title : str
        Title for the diagram
    output_dir : str or Path
        Directory to save outputs
    filename : str
        Base filename (without extension)
    area_km2 : bool
        Use km2 (True) or pixel count (False)
    save_png : bool
        Save static PNG version
    save_html : bool
        Save interactive HTML version
    figsize : tuple
        Figure size for PNG version
    dpi : int
        Resolution for PNG version
        
    Returns
    -------
    dict
        Dictionary with paths to saved files
    """
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"
    area_unit = "km²" if area_km2 else "pixels"
    
    # Create transition matrix
    transition_matrix = dataset.pivot_table(
        index='From', columns='To', values=area_col, fill_value=0
    )
    
    # Create category labels
    if legend_table is not None:
        label_map = dict(zip(legend_table['CategoryValue'], legend_table['CategoryName']))
    else:
        categories = sorted(set(dataset["From"].unique()) | set(dataset["To"].unique()))
        label_map = {cat: f"Class_{cat}" for cat in categories}
    
    saved_files = {}
    
    # 1. Create matplotlib version (PNG) - transition matrix heatmap
    if save_png:
        png_path = _create_matplotlib_chord(
            transition_matrix, label_map, title, area_unit,
            output_dir / f"{filename}.png", figsize, dpi
        )
        saved_files['png'] = str(png_path)
    
    # 2. Create plotly version (HTML) - interactive heatmap
    if save_html and HAS_PLOTLY:
        html_path = _create_plotly_chord(
            transition_matrix, label_map, title, area_unit,
            output_dir / f"{filename}.html"
        )
        saved_files['html'] = str(html_path)
    
    return saved_files


def _create_matplotlib_chord(
    matrix: pd.DataFrame,
    label_map: Dict,
    title: str,
    area_unit: str,
    output_path: Path,
    figsize: Tuple[int, int],
    dpi: int
) -> Path:
    """Create transition matrix heatmap using matplotlib."""
    
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]
    
    # Create heatmap
    im = ax.imshow(matrix.values, cmap='YlOrRd', aspect='auto')
    
    # Set ticks and labels
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_yticks(range(len(matrix.index)))
    ax.set_xticklabels(column_labels, rotation=45, ha='right')
    ax.set_yticklabels(index_labels)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(f'Area ({area_unit})', rotation=270, labelpad=20)
    
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
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    return output_path


def _create_plotly_chord(
    matrix: pd.DataFrame,
    label_map: Dict,
    title: str,
    area_unit: str,
    output_path: Path
) -> Path:
    """Create interactive transition matrix using plotly."""
    
    # Create labels
    index_labels = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
    column_labels = [label_map.get(col, f"Class_{col}") for col in matrix.columns]
    
    # Create interactive heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=column_labels,
        y=index_labels,
        colorscale='YlOrRd',
        colorbar=dict(title=f'Area ({area_unit})')
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='To (Land Cover Class)',
        yaxis_title='From (Land Cover Class)',
        width=800,
        height=600
    )
    
    # Save as HTML
    fig.write_html(output_path)
    
    return output_path


def create_summary_plots(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    output_dir: Union[str, Path] = "outputs",
    title_prefix: str = "Land Use Change Analysis",
    **kwargs
) -> Dict[str, Dict[str, str]]:
    """
    Create a complete set of visualization plots.
    
    Parameters
    ----------
    dataset : pd.DataFrame
        DataFrame with transition data
    legend_table : pd.DataFrame, optional
        Legend mapping category values to names
    output_dir : str or Path
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
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # 1. Sankey diagram
    print("📊 Criando diagrama de Sankey...")
    results['sankey'] = enhanced_sankey_diagram(
        dataset, legend_table, 
        title=f"{title_prefix} - Flow Diagram",
        output_dir=output_dir,
        filename="sankey_flows",
        **kwargs
    )
    
    # 2. Chord diagram / transition matrix
    print("📊 Criando matriz de transição...")
    results['chord'] = enhanced_chord_diagram(
        dataset, legend_table,
        title=f"{title_prefix} - Transition Matrix", 
        output_dir=output_dir,
        filename="transition_matrix",
        **kwargs
    )
    
    return results
