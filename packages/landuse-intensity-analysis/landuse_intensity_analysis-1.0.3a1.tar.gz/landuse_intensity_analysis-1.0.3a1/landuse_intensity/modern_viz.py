"""
Modern visualization utilities for landuse-intensity-analysis.

This module provides enhanced visualization capabilities with:
- Interactive plots using Plotly
- Modern styling and themes
- Responsive design
- Export capabilities (PNG, SVG, HTML)
- Statistical annotations
- Comparative visualizations
- Time series analysis plots

The module integrates with the existing visualization system
while providing more advanced and interactive features.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.warning("Plotly not available. Install with: pip install plotly")

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib/Seaborn not available. Install with: pip install matplotlib seaborn")

try:
    from .visualization import create_intensity_matrix_plot, create_transition_matrix_plot
    HAS_LEGACY_VIZ = True
except ImportError:
    HAS_LEGACY_VIZ = False
    logger.warning("Legacy visualization module not available")


class ModernVisualizer:
    """
    Modern visualization engine for landuse intensity analysis.

    This class provides enhanced visualization capabilities with
    interactive plots, modern styling, and multiple output formats.
    """

    def __init__(self,
                 theme: str = "modern",
                 color_palette: str = "viridis",
                 figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize modern visualizer.

        Parameters
        ----------
        theme : str, default "modern"
            Visual theme: 'modern', 'classic', 'dark', 'light'
        color_palette : str, default "viridis"
            Color palette for plots
        figsize : tuple, default (12, 8)
            Default figure size
        """
        self.theme = theme
        self.color_palette = color_palette
        self.figsize = figsize

        # Theme configurations
        self.themes = {
            'modern': {
                'background': 'white',
                'text_color': '#2c3e50',
                'grid_color': '#ecf0f1',
                'accent_color': '#3498db'
            },
            'dark': {
                'background': '#2c3e50',
                'text_color': '#ecf0f1',
                'grid_color': '#34495e',
                'accent_color': '#3498db'
            },
            'classic': {
                'background': 'white',
                'text_color': 'black',
                'grid_color': '#cccccc',
                'accent_color': '#007acc'
            }
        }

        self.current_theme = self.themes.get(theme, self.themes['modern'])

        # Initialize plotting libraries
        self._setup_plotting()

    def _setup_plotting(self):
        """Setup plotting libraries and themes."""
        if HAS_MATPLOTLIB:
            # Set matplotlib style
            plt.style.use('default')

            # Custom style parameters
            plt.rcParams.update({
                'figure.figsize': self.figsize,
                'font.size': 10,
                'axes.labelsize': 12,
                'axes.titlesize': 14,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 10,
                'figure.titlesize': 16
            })

        if HAS_PLOTLY:
            # Set plotly theme
            if self.theme == 'dark':
                import plotly.io as pio
                pio.templates.default = "plotly_dark"

    def create_intensity_heatmap(self,
                                intensity_matrix: np.ndarray,
                                class_names: List[str] = None,
                                title: str = "Land Use Intensity Matrix",
                                interactive: bool = True) -> Union[Any, None]:
        """
        Create an interactive heatmap for intensity matrix.

        Parameters
        ----------
        intensity_matrix : np.ndarray
            Intensity matrix data
        class_names : list of str, optional
            Names of land use classes
        title : str, default "Land Use Intensity Matrix"
            Plot title
        interactive : bool, default True
            Whether to create interactive plot

        Returns
        -------
        plotly figure or matplotlib figure
            The created visualization
        """
        if class_names is None:
            class_names = [f"Class {i+1}" for i in range(len(intensity_matrix))]

        if interactive and HAS_PLOTLY:
            return self._create_plotly_heatmap(intensity_matrix, class_names, title)
        elif HAS_MATPLOTLIB:
            return self._create_matplotlib_heatmap(intensity_matrix, class_names, title)
        else:
            logger.error("No plotting library available")
            return None

    def _create_plotly_heatmap(self,
                              intensity_matrix: np.ndarray,
                              class_names: List[str],
                              title: str) -> Any:
        """Create Plotly heatmap."""
        # Create hover text
        hover_text = []
        for i in range(len(intensity_matrix)):
            row = []
            for j in range(len(intensity_matrix[i])):
                row.append('.3f')
            hover_text.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=intensity_matrix,
            x=class_names,
            y=class_names,
            hoverongaps=False,
            hovertext=hover_text,
            colorscale=self.color_palette,
            showscale=True,
            colorbar=dict(title="Intensity")
        ))

        fig.update_layout(
            title=title,
            xaxis_title="To Class",
            yaxis_title="From Class",
            font=dict(size=12),
            margin=dict(l=100, r=100, t=100, b=100)
        )

        # Add theme styling
        if self.theme == 'dark':
            fig.update_layout(
                paper_bgcolor=self.current_theme['background'],
                plot_bgcolor=self.current_theme['background'],
                font_color=self.current_theme['text_color']
            )

        return fig

    def _create_matplotlib_heatmap(self,
                                  intensity_matrix: np.ndarray,
                                  class_names: List[str],
                                  title: str) -> Any:
        """Create Matplotlib heatmap."""
        fig, ax = plt.subplots(figsize=self.figsize)

        # Create heatmap
        im = ax.imshow(intensity_matrix, cmap=self.color_palette, aspect='equal')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Intensity', fontsize=12)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(class_names)))
        ax.set_yticks(np.arange(len(class_names)))
        ax.set_xticklabels(class_names, rotation=45, ha='right')
        ax.set_yticklabels(class_names)

        # Add text annotations
        for i in range(len(intensity_matrix)):
            for j in range(len(intensity_matrix[i])):
                text = ax.text(j, i, '.2f',
                             ha="center", va="center", color="w",
                             fontweight='bold' if intensity_matrix[i, j] > np.max(intensity_matrix) * 0.7 else 'normal')

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('To Class', fontsize=12)
        ax.set_ylabel('From Class', fontsize=12)

        plt.tight_layout()
        return fig

    def create_transition_sankey(self,
                                transition_matrix: np.ndarray,
                                class_names: List[str] = None,
                                title: str = "Land Use Transitions",
                                interactive: bool = True) -> Union[Any, None]:
        """
        Create a Sankey diagram for land use transitions.

        Parameters
        ----------
        transition_matrix : np.ndarray
            Transition matrix data
        class_names : list of str, optional
            Names of land use classes
        title : str, default "Land Use Transitions"
            Plot title
        interactive : bool, default True
            Whether to create interactive plot

        Returns
        -------
        plotly figure or matplotlib figure
            The created visualization
        """
        if class_names is None:
            class_names = [f"Class {i+1}" for i in range(len(transition_matrix))]

        if interactive and HAS_PLOTLY:
            return self._create_plotly_sankey(transition_matrix, class_names, title)
        elif HAS_MATPLOTLIB:
            return self._create_matplotlib_sankey(transition_matrix, class_names, title)
        else:
            logger.error("No plotting library available")
            return None

    def _create_plotly_sankey(self,
                             transition_matrix: np.ndarray,
                             class_names: List[str],
                             title: str) -> Any:
        """Create Plotly Sankey diagram."""
        # Prepare Sankey data
        sources = []
        targets = []
        values = []
        labels = class_names * 2  # From and To labels

        for i in range(len(transition_matrix)):
            for j in range(len(transition_matrix[i])):
                if transition_matrix[i, j] > 0:
                    sources.append(i)
                    targets.append(len(class_names) + j)
                    values.append(transition_matrix[i, j])

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=self._get_node_colors(len(labels))
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=self._get_link_colors(len(values))
            )
        )])

        fig.update_layout(
            title=title,
            font_size=12,
            margin=dict(l=50, r=50, t=100, b=50)
        )

        return fig

    def _create_matplotlib_sankey(self,
                                 transition_matrix: np.ndarray,
                                 class_names: List[str],
                                 title: str) -> Any:
        """Create Matplotlib Sankey diagram (simplified version)."""
        fig, ax = plt.subplots(figsize=self.figsize)

        # Create a simplified bar chart representation
        n_classes = len(class_names)
        x = np.arange(n_classes)
        width = 0.35

        # Plot from and to distributions
        from_totals = np.sum(transition_matrix, axis=1)
        to_totals = np.sum(transition_matrix, axis=0)

        ax.bar(x - width/2, from_totals, width, label='From', alpha=0.7)
        ax.bar(x + width/2, to_totals, width, label='To', alpha=0.7)

        ax.set_xlabel('Land Use Class')
        ax.set_ylabel('Total Transitions')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(class_names, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()
        return fig

    def _get_node_colors(self, n_nodes: int) -> List[str]:
        """Get colors for Sankey nodes."""
        if HAS_MATPLOTLIB:
            cmap = plt.get_cmap(self.color_palette)
            return [mcolors.to_hex(cmap(i / n_nodes)) for i in range(n_nodes)]
        else:
            # Fallback colors
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            return colors * (n_nodes // len(colors) + 1)[:n_nodes]

    def _get_link_colors(self, n_links: int) -> List[str]:
        """Get colors for Sankey links."""
        if HAS_MATPLOTLIB:
            cmap = plt.get_cmap(self.color_palette)
            return [mcolors.to_hex(cmap(i / n_links)) for i in range(n_links)]
        else:
            # Fallback colors
            colors = ['rgba(31, 119, 180, 0.4)', 'rgba(255, 127, 14, 0.4)',
                     'rgba(44, 160, 44, 0.4)', 'rgba(214, 39, 40, 0.4)']
            return colors * (n_links // len(colors) + 1)[:n_links]

    def create_change_map(self,
                         change_data: np.ndarray,
                         title: str = "Land Use Change Map",
                         interactive: bool = True) -> Union[Any, None]:
        """
        Create a change map visualization.

        Parameters
        ----------
        change_data : np.ndarray
            Change data (2D array)
        title : str, default "Land Use Change Map"
            Plot title
        interactive : bool, default True
            Whether to create interactive plot

        Returns
        -------
        plotly figure or matplotlib figure
            The created visualization
        """
        if interactive and HAS_PLOTLY:
            return self._create_plotly_change_map(change_data, title)
        elif HAS_MATPLOTLIB:
            return self._create_matplotlib_change_map(change_data, title)
        else:
            logger.error("No plotting library available")
            return None

    def _create_plotly_change_map(self, change_data: np.ndarray, title: str) -> Any:
        """Create Plotly change map."""
        fig = go.Figure(data=go.Heatmap(
            z=change_data,
            colorscale='RdYlBu_r',  # Red for loss, Blue for gain
            showscale=True,
            colorbar=dict(title="Change")
        ))

        fig.update_layout(
            title=title,
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            font=dict(size=12)
        )

        return fig

    def _create_matplotlib_change_map(self, change_data: np.ndarray, title: str) -> Any:
        """Create Matplotlib change map."""
        fig, ax = plt.subplots(figsize=self.figsize)

        im = ax.imshow(change_data, cmap='RdYlBu_r')
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Change', fontsize=12)

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('X Coordinate', fontsize=12)
        ax.set_ylabel('Y Coordinate', fontsize=12)

        plt.tight_layout()
        return fig

    def create_time_series_plot(self,
                               time_data: Dict[str, Any],
                               title: str = "Land Use Time Series",
                               interactive: bool = True) -> Union[Any, None]:
        """
        Create a time series plot for land use changes.

        Parameters
        ----------
        time_data : dict
            Time series data with keys as time periods
        title : str, default "Land Use Time Series"
            Plot title
        interactive : bool, default True
            Whether to create interactive plot

        Returns
        -------
        plotly figure or matplotlib figure
            The created visualization
        """
        if interactive and HAS_PLOTLY:
            return self._create_plotly_time_series(time_data, title)
        elif HAS_MATPLOTLIB:
            return self._create_matplotlib_time_series(time_data, title)
        else:
            logger.error("No plotting library available")
            return None

    def _create_plotly_time_series(self, time_data: Dict[str, Any], title: str) -> Any:
        """Create Plotly time series plot."""
        fig = go.Figure()

        for class_name, values in time_data.items():
            fig.add_trace(go.Scatter(
                x=list(values.keys()),
                y=list(values.values()),
                mode='lines+markers',
                name=class_name
            ))

        fig.update_layout(
            title=title,
            xaxis_title="Time Period",
            yaxis_title="Area/Area Proportion",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=100, b=50)
        )

        return fig

    def _create_matplotlib_time_series(self, time_data: Dict[str, Any], title: str) -> Any:
        """Create Matplotlib time series plot."""
        fig, ax = plt.subplots(figsize=self.figsize)

        for class_name, values in time_data.items():
            ax.plot(list(values.keys()), list(values.values()),
                   marker='o', linewidth=2, label=class_name)

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Time Period', fontsize=12)
        ax.set_ylabel('Area/Area Proportion', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def save_plot(self,
                  plot_obj: Any,
                  filename: Union[str, Path],
                  format: str = "png",
                  **kwargs):
        """
        Save plot to file.

        Parameters
        ----------
        plot_obj : plotly figure or matplotlib figure
            The plot object to save
        filename : str or Path
            Output filename
        format : str, default "png"
            Output format: 'png', 'svg', 'html', 'pdf'
        **kwargs
            Additional arguments for save function
        """
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if HAS_PLOTLY and hasattr(plot_obj, 'write_image'):
            # Plotly figure
            if format == 'html':
                plot_obj.write_html(str(filepath.with_suffix('.html')))
            else:
                plot_obj.write_image(str(filepath.with_suffix(f'.{format}')), **kwargs)
        elif HAS_MATPLOTLIB and hasattr(plot_obj, 'savefig'):
            # Matplotlib figure
            plot_obj.savefig(str(filepath.with_suffix(f'.{format}')),
                           dpi=300, bbox_inches='tight', **kwargs)
        else:
            logger.error(f"Cannot save plot in format {format}")

    def create_dashboard(self,
                        intensity_data: Dict[str, Any],
                        transition_data: Dict[str, Any],
                        title: str = "Land Use Intensity Analysis Dashboard") -> Any:
        """
        Create a comprehensive dashboard with multiple visualizations.

        Parameters
        ----------
        intensity_data : dict
            Intensity analysis results
        transition_data : dict
            Transition analysis results
        title : str, default "Land Use Intensity Analysis Dashboard"
            Dashboard title

        Returns
        -------
        plotly figure
            Dashboard figure
        """
        if not HAS_PLOTLY:
            logger.error("Plotly required for dashboard creation")
            return None

        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Intensity Matrix", "Transition Sankey",
                          "Change Map", "Time Series"),
            specs=[[{"type": "heatmap"}, {"type": "sankey"}],
                   [{"type": "heatmap"}, {"type": "scatter"}]]
        )

        # Add intensity heatmap
        if 'intensity_matrix' in intensity_data:
            intensity_matrix = intensity_data['intensity_matrix']
            fig.add_trace(
                go.Heatmap(z=intensity_matrix, colorscale=self.color_palette),
                row=1, col=1
            )

        # Add transition sankey (placeholder)
        if 'transition_matrix' in transition_data:
            fig.add_trace(
                go.Sankey(
                    node=dict(label=["A", "B", "C"]),
                    link=dict(source=[0, 1], target=[1, 2], value=[1, 1])
                ),
                row=1, col=2
            )

        # Add change map (placeholder)
        fig.add_trace(
            go.Heatmap(z=np.random.rand(10, 10), colorscale='RdYlBu_r'),
            row=2, col=1
        )

        # Add time series (placeholder)
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[1, 2, 1], mode='lines+markers'),
            row=2, col=2
        )

        fig.update_layout(
            title=title,
            height=800,
            showlegend=False
        )

        return fig


# Convenience functions
def create_intensity_matrix_plot(intensity_matrix: np.ndarray,
                                class_names: List[str] = None,
                                **kwargs) -> Any:
    """
    Create intensity matrix plot using modern visualizer.

    Parameters
    ----------
    intensity_matrix : np.ndarray
        Intensity matrix data
    class_names : list of str, optional
        Names of land use classes
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    plotly figure or matplotlib figure
        The created visualization
    """
    visualizer = ModernVisualizer(**kwargs)
    return visualizer.create_intensity_heatmap(intensity_matrix, class_names)

def create_transition_matrix_plot(transition_matrix: np.ndarray,
                                 class_names: List[str] = None,
                                 **kwargs) -> Any:
    """
    Create transition matrix plot using modern visualizer.

    Parameters
    ----------
    transition_matrix : np.ndarray
        Transition matrix data
    class_names : list of str, optional
        Names of land use classes
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    plotly figure or matplotlib figure
        The created visualization
    """
    visualizer = ModernVisualizer(**kwargs)
    return visualizer.create_transition_sankey(transition_matrix, class_names)

def generate_all_visualizations(intensity_data: Dict[str, Any],
                               output_dir: Union[str, Path] = None,
                               **kwargs) -> Dict[str, Any]:
    """
    Generate all visualizations for intensity analysis results.

    Parameters
    ----------
    intensity_data : dict
        Intensity analysis results
    output_dir : str or Path, optional
        Directory to save visualizations
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    dict
        Dictionary of created visualizations
    """
    visualizer = ModernVisualizer(**kwargs)
    results = {}

    # Create intensity matrix heatmap
    if 'intensity_matrix' in intensity_data:
        intensity_plot = visualizer.create_intensity_heatmap(
            intensity_data['intensity_matrix'],
            intensity_data.get('class_names'),
            "Land Use Intensity Matrix"
        )
        results['intensity_heatmap'] = intensity_plot

        if output_dir:
            visualizer.save_plot(intensity_plot, Path(output_dir) / "intensity_matrix")

    # Create transition matrix sankey
    if 'transition_matrix' in intensity_data:
        transition_plot = visualizer.create_transition_sankey(
            intensity_data['transition_matrix'],
            intensity_data.get('class_names'),
            "Land Use Transitions"
        )
        results['transition_sankey'] = transition_plot

        if output_dir:
            visualizer.save_plot(transition_plot, Path(output_dir) / "transition_sankey")

    # Create change map if available
    if 'change_map' in intensity_data:
        change_plot = visualizer.create_change_map(
            intensity_data['change_map'],
            "Land Use Change Map"
        )
        results['change_map'] = change_plot

        if output_dir:
            visualizer.save_plot(change_plot, Path(output_dir) / "change_map")

    # Create time series if available
    if 'time_series' in intensity_data:
        time_plot = visualizer.create_time_series_plot(
            intensity_data['time_series'],
            "Land Use Time Series"
        )
        results['time_series'] = time_plot

        if output_dir:
            visualizer.save_plot(time_plot, Path(output_dir) / "time_series")

    # Create dashboard
    if len(results) > 1:
        dashboard = visualizer.create_dashboard(intensity_data, intensity_data)
        results['dashboard'] = dashboard

        if output_dir:
            visualizer.save_plot(dashboard, Path(output_dir) / "dashboard", format="html")

    return results

def create_comparison_visualization(data_list: List[Dict[str, Any]],
                                   labels: List[str],
                                   **kwargs) -> Any:
    """
    Create comparison visualization for multiple datasets.

    Parameters
    ----------
    data_list : list of dict
        List of intensity analysis results
    labels : list of str
        Labels for each dataset
    **kwargs
        Additional arguments for visualizer

    Returns
    -------
    plotly figure
        Comparison visualization
    """
    if not HAS_PLOTLY:
        logger.error("Plotly required for comparison visualization")
        return None

    visualizer = ModernVisualizer(**kwargs)

    # Create subplot for comparison
    n_datasets = len(data_list)
    fig = make_subplots(
        rows=1, cols=n_datasets,
        subplot_titles=labels,
        shared_yaxes=True
    )

    for i, (data, label) in enumerate(zip(data_list, labels)):
        if 'intensity_matrix' in data:
            fig.add_trace(
                go.Heatmap(
                    z=data['intensity_matrix'],
                    colorscale=visualizer.color_palette,
                    showscale=i == 0  # Only show scale for first plot
                ),
                row=1, col=i+1
            )

    fig.update_layout(
        title="Intensity Matrix Comparison",
        height=400,
        margin=dict(l=50, r=50, t=100, b=50)
    )

    return fig
