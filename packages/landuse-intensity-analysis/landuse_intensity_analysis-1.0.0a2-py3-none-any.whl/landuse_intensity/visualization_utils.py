"""
Visualization Utilities Module

This module provides utility functions and helper classes for land use and land cover
visualization, including color management, data preprocessing, export utilities,
and common visualization patterns.

Key Features:
- Color palette management and generation
- Data preprocessing for visualization
- Export utilities for multiple formats
- Common visualization patterns and templates
- Theme and styling utilities
- Data validation and cleaning

Based on research from:
- Scientific visualization best practices
- Color theory and accessibility guidelines
- Modern Python visualization libraries
- Data visualization design principles

Functions:
- Color management: generate_color_palettes, create_color_map
- Data utilities: preprocess_visualization_data, validate_visualization_data
- Export utilities: export_multiple_formats, create_export_bundle
- Theme utilities: apply_publication_theme, create_custom_theme
- Layout utilities: create_subplot_grid, optimize_layout
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

# Set matplotlib style for publication-quality plots
plt.style.use('default')
sns.set_palette("husl")


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def generate_color_palettes(
    n_colors: int,
    palette_type: str = "categorical",
    colorblind_friendly: bool = True
) -> List[str]:
    """
    Generate color palettes for visualization.

    Parameters:
    -----------
    n_colors : int
        Number of colors to generate
    palette_type : str
        Type of palette ('categorical', 'sequential', 'diverging')
    colorblind_friendly : bool
        Whether to use colorblind-friendly colors

    Returns:
    --------
    list
        List of hex color codes
    """
    if palette_type == "categorical":
        if colorblind_friendly:
            # Colorblind-friendly categorical palette
            base_colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
            ]
        else:
            # Standard categorical palette
            base_colors = plt.cm.tab10.colors

        # Extend palette if needed
        if n_colors <= len(base_colors):
            colors = base_colors[:n_colors]
        else:
            colors = base_colors * (n_colors // len(base_colors) + 1)
            colors = colors[:n_colors]

    elif palette_type == "sequential":
        if colorblind_friendly:
            # Viridis-like colorblind-friendly sequential
            cmap = plt.cm.viridis
        else:
            # Standard sequential
            cmap = plt.cm.Blues

        colors = [mcolors.to_hex(cmap(i / (n_colors - 1))) for i in range(n_colors)]

    elif palette_type == "diverging":
        if colorblind_friendly:
            # RdYlBu-like colorblind-friendly diverging
            cmap = plt.cm.RdYlBu_r
        else:
            # Standard diverging
            cmap = plt.cm.RdBu

        colors = [mcolors.to_hex(cmap(i / (n_colors - 1))) for i in range(n_colors)]

    else:
        raise ValueError("palette_type must be 'categorical', 'sequential', or 'diverging'")

    return colors


def create_color_map(
    categories: List[str],
    palette_type: str = "categorical",
    colorblind_friendly: bool = True
) -> Dict[str, str]:
    """
    Create a color mapping for categories.

    Parameters:
    -----------
    categories : list
        List of category names
    palette_type : str
        Type of palette to use
    colorblind_friendly : bool
        Whether to use colorblind-friendly colors

    Returns:
    --------
    dict
        Dictionary mapping category names to hex colors
    """
    colors = generate_color_palettes(
        len(categories),
        palette_type=palette_type,
        colorblind_friendly=colorblind_friendly
    )

    return dict(zip(categories, colors))


def preprocess_visualization_data(
    data: Union[pd.DataFrame, pd.Series, Dict],
    data_type: str = "general",
    **kwargs
) -> pd.DataFrame:
    """
    Preprocess data for visualization.

    Parameters:
    -----------
    data : pd.DataFrame, pd.Series, or dict
        Input data to preprocess
    data_type : str
        Type of data ('general', 'lulc', 'time_series', 'spatial')
    **kwargs
        Additional preprocessing parameters

    Returns:
    --------
    pd.DataFrame
        Preprocessed data
    """
    # Convert to DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.Series):
        df = data.to_frame()
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Data must be DataFrame, Series, or dict")

    # Data type specific preprocessing
    if data_type == "lulc":
        # Ensure area column exists
        if 'Area' not in df.columns and 'area' not in df.columns:
            # Try to infer area from other columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df['Area'] = df[numeric_cols[0]]
            else:
                raise ValueError("No numeric columns found for area calculation")

        # Standardize column names
        df.columns = [col.title() if col.lower() in ['area', 'km2', 'hectares']
                     else col for col in df.columns]

    elif data_type == "time_series":
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                df.index = pd.to_datetime(df[date_cols[0]])
                df = df.drop(date_cols[0], axis=1)
            else:
                # Assume first column is date if it looks like dates
                first_col = df.columns[0]
                try:
                    df.index = pd.to_datetime(df[first_col])
                    df = df.drop(first_col, axis=1)
                except:
                    pass  # Keep as is

    elif data_type == "spatial":
        # Ensure coordinate columns exist
        coord_cols = ['x', 'y', 'lon', 'lat', 'longitude', 'latitude']
        found_coords = [col for col in df.columns if col.lower() in coord_cols]

        if len(found_coords) < 2:
            warnings.warn("Spatial data should have at least 2 coordinate columns")

    # General preprocessing
    # Remove completely empty rows/columns
    df = df.dropna(how='all').dropna(axis=1, how='all')

    # Handle missing values based on kwargs
    if 'fillna_method' in kwargs:
        method = kwargs['fillna_method']
        if method == 'mean':
            df = df.fillna(df.mean())
        elif method == 'median':
            df = df.fillna(df.median())
        elif method == 'forward':
            df = df.fillna(method='ffill')
        elif method == 'backward':
            df = df.fillna(method='bfill')
        elif isinstance(method, (int, float)):
            df = df.fillna(method)

    return df


def validate_visualization_data(
    data: Union[pd.DataFrame, pd.Series, Dict],
    required_columns: Optional[List[str]] = None,
    data_types: Optional[Dict[str, type]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate data for visualization.

    Parameters:
    -----------
    data : pd.DataFrame, pd.Series, or dict
        Data to validate
    required_columns : list, optional
        List of required column names
    data_types : dict, optional
        Expected data types for columns

    Returns:
    --------
    tuple
        (is_valid, list_of_issues)
    """
    issues = []

    # Convert to DataFrame for validation
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.Series):
        df = data.to_frame()
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        issues.append("Data must be DataFrame, Series, or dict")
        return False, issues

    # Check required columns
    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")

    # Check data types
    if data_types:
        for col, expected_type in data_types.items():
            if col in df.columns:
                if not df[col].dtype == expected_type:
                    issues.append(f"Column '{col}' has wrong type. Expected {expected_type}, got {df[col].dtype}")

    # Check for empty data
    if df.empty:
        issues.append("Data is empty")

    # Check for all-NaN columns
    nan_cols = df.columns[df.isna().all()].tolist()
    if nan_cols:
        issues.append(f"Columns with all NaN values: {nan_cols}")

    return len(issues) == 0, issues


def export_multiple_formats(
    fig: plt.Figure,
    filename: str,
    output_dir: str = "outputs",
    formats: Optional[List[str]] = None,
    dpi: int = 300,
    **kwargs
) -> Dict[str, str]:
    """
    Export figure to multiple formats.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to export
    filename : str
        Base filename (without extension)
    output_dir : str
        Output directory
    formats : list, optional
        List of formats to export ('png', 'svg', 'pdf', 'jpg', 'eps')
    dpi : int
        DPI for raster formats
    **kwargs
        Additional arguments for savefig

    Returns:
    --------
    dict
        Dictionary mapping format to file path
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Default formats
    if formats is None:
        formats = ['png', 'svg', 'pdf']

    exported_files = {}

    for fmt in formats:
        filepath = output_path / f"{filename}.{fmt}"

        try:
            if fmt in ['png', 'jpg', 'jpeg']:
                fig.savefig(filepath, dpi=dpi, bbox_inches='tight', **kwargs)
            elif fmt in ['svg', 'pdf', 'eps', 'ps']:
                fig.savefig(filepath, bbox_inches='tight', **kwargs)
            else:
                warnings.warn(f"Unsupported format: {fmt}")
                continue

            exported_files[fmt] = str(filepath)

        except Exception as e:
            warnings.warn(f"Failed to export {fmt}: {e}")

    return exported_files


def create_export_bundle(
    data: Union[pd.DataFrame, Dict],
    filename: str,
    output_dir: str = "outputs",
    include_statistics: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Create a complete export bundle with data and statistics.

    Parameters:
    -----------
    data : pd.DataFrame or dict
        Data to export
    filename : str
        Base filename
    output_dir : str
        Output directory
    include_statistics : bool
        Whether to include statistical summary
    **kwargs
        Additional arguments

    Returns:
    --------
    dict
        Dictionary mapping file type to file path
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    exported_files = {}

    # Convert to DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Data must be DataFrame or dict")

    # Export main data
    data_path = output_path / f"{filename}_data.csv"
    df.to_csv(data_path, index=False)
    exported_files['data'] = str(data_path)

    # Export statistics if requested
    if include_statistics:
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe()

            # Add additional statistics
            additional_stats = pd.DataFrame({
                'skewness': df[numeric_cols].skew(),
                'kurtosis': df[numeric_cols].kurtosis(),
                'missing_values': df[numeric_cols].isna().sum(),
                'missing_percentage': (df[numeric_cols].isna().sum() / len(df)) * 100
            }).T

            combined_stats = pd.concat([stats, additional_stats])

            stats_path = output_path / f"{filename}_statistics.csv"
            combined_stats.to_csv(stats_path)
            exported_files['statistics'] = str(stats_path)

    # Export metadata
    metadata = {
        'filename': filename,
        'export_date': pd.Timestamp.now().isoformat(),
        'rows': len(df),
        'columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }

    metadata_df = pd.DataFrame([metadata])
    metadata_path = output_path / f"{filename}_metadata.csv"
    metadata_df.to_csv(metadata_path, index=False)
    exported_files['metadata'] = str(metadata_path)

    return exported_files


def apply_publication_theme(
    fig: plt.Figure,
    theme: str = "nature",
    **kwargs
) -> plt.Figure:
    """
    Apply publication-ready theme to figure.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to style
    theme : str
        Theme to apply ('nature', 'science', 'minimal', 'colorful')
    **kwargs
        Additional theme parameters

    Returns:
    --------
    matplotlib.figure.Figure
        Styled figure
    """
    if theme == "nature":
        # Nature-style theme
        plt.style.use('default')
        sns.set_style("whitegrid", {'grid.color': '.8', 'grid.linestyle': '-'})

        # Set colors
        colors = ['#2E8B57', '#4169E1', '#DC143C', '#FFD700', '#8A2BE2']

    elif theme == "science":
        # Science journal style
        plt.style.use('default')
        sns.set_style("ticks")

        # Professional colors
        colors = ['#000000', '#2E8B57', '#DC143C', '#4169E1', '#FFD700']

    elif theme == "minimal":
        # Minimalist theme
        plt.style.use('default')
        sns.set_style("white")

        # Simple colors
        colors = ['#2E8B57', '#7F7F7F', '#DC143C', '#4169E1', '#FFD700']

    elif theme == "colorful":
        # Colorful theme
        plt.style.use('default')
        sns.set_style("whitegrid")

        # Vibrant colors
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    else:
        raise ValueError("Theme must be 'nature', 'science', 'minimal', or 'colorful'")

    # Apply theme to all axes
    for ax in fig.get_axes():
        # Set colors
        if hasattr(ax, 'lines'):
            for i, line in enumerate(ax.lines):
                line.set_color(colors[i % len(colors)])

        # Style text
        ax.title.set_fontsize(14)
        ax.title.set_fontweight('bold')

        ax.xaxis.label.set_fontsize(12)
        ax.xaxis.label.set_fontweight('bold')

        ax.yaxis.label.set_fontsize(12)
        ax.yaxis.label.set_fontweight('bold')

        # Style ticks
        ax.tick_params(axis='both', labelsize=10)

        # Add grid
        ax.grid(True, alpha=0.3)

    return fig


def create_subplot_grid(
    n_plots: int,
    max_cols: int = 3,
    figsize: Optional[Tuple[int, int]] = None,
    **kwargs
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create an optimal subplot grid layout.

    Parameters:
    -----------
    n_plots : int
        Number of subplots
    max_cols : int
        Maximum number of columns
    figsize : tuple, optional
        Figure size (auto-calculated if None)
    **kwargs
        Additional arguments for plt.subplots

    Returns:
    --------
    tuple
        (figure, axes_array)
    """
    # Calculate optimal grid layout
    n_cols = min(max_cols, n_plots)
    n_rows = int(np.ceil(n_plots / n_cols))

    # Auto-calculate figsize if not provided
    if figsize is None:
        base_width = 4
        base_height = 3
        figsize = (n_cols * base_width, n_rows * base_height)

    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, **kwargs)

    # Handle single subplot case
    if n_plots == 1:
        axes = np.array([axes])

    # Flatten axes array for easy iteration
    axes = axes.flatten()

    # Hide unused subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)

    return fig, axes[:n_plots]


def optimize_layout(
    fig: plt.Figure,
    tight_layout: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Optimize figure layout for better presentation.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to optimize
    tight_layout : bool
        Whether to use tight layout
    **kwargs
        Additional arguments for tight_layout

    Returns:
    --------
    matplotlib.figure.Figure
        Optimized figure
    """
    if tight_layout:
        plt.tight_layout(**kwargs)

    return fig


def create_custom_colormap(
    colors: List[str],
    name: str = "custom_cmap"
) -> LinearSegmentedColormap:
    """
    Create a custom colormap from a list of colors.

    Parameters:
    -----------
    colors : list
        List of color specifications (hex, rgb, etc.)
    name : str
        Name for the colormap

    Returns:
    --------
    matplotlib.colors.LinearSegmentedColormap
        Custom colormap
    """
    # Convert colors to RGB
    rgb_colors = [mcolors.to_rgb(color) for color in colors]

    # Create colormap
    cmap = LinearSegmentedColormap.from_list(name, rgb_colors)

    return cmap


def add_figure_annotations(
    fig: plt.Figure,
    annotations: Dict[str, Any],
    **kwargs
) -> plt.Figure:
    """
    Add annotations to figure.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to annotate
    annotations : dict
        Dictionary of annotations to add
    **kwargs
        Additional arguments

    Returns:
    --------
    matplotlib.figure.Figure
        Annotated figure
    """
    # Add title if provided
    if 'title' in annotations:
        fig.suptitle(annotations['title'],
                    fontsize=annotations.get('title_fontsize', 16),
                    fontweight='bold',
                    y=annotations.get('title_y', 0.98))

    # Add subtitle if provided
    if 'subtitle' in annotations:
        fig.text(0.5, annotations.get('subtitle_y', 0.95),
                annotations['subtitle'],
                ha='center',
                fontsize=annotations.get('subtitle_fontsize', 12))

    # Add footer if provided
    if 'footer' in annotations:
        fig.text(0.5, annotations.get('footer_y', 0.02),
                annotations['footer'],
                ha='center',
                fontsize=annotations.get('footer_fontsize', 10),
                style='italic')

    return fig


class VisualizationTemplate:
    """
    Template class for creating consistent visualizations.
    """

    def __init__(
        self,
        theme: str = "nature",
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = 150,
        **kwargs
    ):
        """
        Initialize visualization template.

        Parameters:
        -----------
        theme : str
            Default theme to apply
        figsize : tuple
            Default figure size
        dpi : int
            Default DPI
        **kwargs
            Additional template parameters
        """
        self.theme = theme
        self.figsize = figsize
        self.dpi = dpi
        self.kwargs = kwargs

    def create_figure(self, **kwargs) -> plt.Figure:
        """Create a new figure with template settings."""
        figsize = kwargs.get('figsize', self.figsize)
        dpi = kwargs.get('dpi', self.dpi)

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Apply theme
        fig = apply_publication_theme(fig, self.theme)

        return fig

    def export_figure(
        self,
        fig: plt.Figure,
        filename: str,
        output_dir: str = "outputs",
        **kwargs
    ) -> Dict[str, str]:
        """Export figure using template settings."""
        return export_multiple_formats(
            fig, filename, output_dir,
            dpi=self.dpi,
            **kwargs
        )


# Export public functions and classes
__all__ = [
    'generate_color_palettes',
    'preprocess_visualization_data',
    'export_multiple_formats',
    'VisualizationTemplate',
]
