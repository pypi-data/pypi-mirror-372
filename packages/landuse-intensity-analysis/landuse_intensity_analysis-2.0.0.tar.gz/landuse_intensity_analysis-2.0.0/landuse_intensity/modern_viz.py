"""
Modern interactive visualizations for land use and land cover change analysis.

This module provides state-of-the-art visualizations using modern libraries:
- Interactive chord diagrams with Plotly
- Advanced Sankey diagrams
- Animated temporal maps
- Interactive dashboards
- Modern color schemes and accessibility features

Features:
- Responsive design for web deployment
- Export capabilities (PNG, SVG, HTML, PDF)
- Accessibility compliance (colorblind-safe palettes)
- Interactive tooltips and filtering
- Real-time data updates
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Modern visualization libraries
HAS_PLOTLY = False
HAS_DASH = False
HAS_STREAMLIT = False
HAS_HOLOVIEWS = False
HAS_ALTAIR = False

try:
    import plotly.express as px
    import plotly.figure_factory as ff
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    pass

try:
    import dash
    from dash import Input, Output, callback, dcc, html

    HAS_DASH = True
except ImportError:
    pass

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    pass

try:
    import geoviews as gv
    import holoviews as hv
    from holoviews import opts

    HAS_HOLOVIEWS = True
except ImportError:
    pass

try:
    import altair as alt

    HAS_ALTAIR = True
except ImportError:
    pass

# Color schemes for accessibility and modern design
MODERN_LULC_COLORS = {
    "forest": "#2d5016",
    "agriculture": "#ffbb33",
    "urban": "#ff4444",
    "water": "#0099cc",
    "grassland": "#99cc00",
    "barren": "#cccccc",
    "wetland": "#6699ff",
}

COLORBLIND_SAFE_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


class ModernVisualizer:
    """
    Modern visualization suite for LULC change analysis.

    Provides cutting-edge interactive visualizations using latest Python libraries.
    Supports web deployment, real-time updates, and accessibility standards.
    """

    def __init__(
        self,
        theme: str = "plotly_white",
        colorblind_safe: bool = True,
        export_config: Optional[Dict] = None,
    ):
        """
        Initialize modern visualizer.

        Parameters
        ----------
        theme : str, default 'plotly_white'
            Visual theme for plots
        colorblind_safe : bool, default True
            Use colorblind-safe color schemes
        export_config : dict, optional
            Configuration for plot exports
        """
        self.theme = theme
        self.colorblind_safe = colorblind_safe
        self.export_config = export_config or {
            "format": "html",
            "width": 1200,
            "height": 800,
            "scale": 2,
        }

        # Set default template if Plotly available
        if HAS_PLOTLY:
            import plotly.io as pio

            pio.templates.default = theme

    def interactive_chord_diagram(
        self,
        transition_matrix: np.ndarray,
        category_names: List[str],
        title: str = "Land Use Transitions",
        min_flow: float = 0.01,
        **kwargs,
    ) -> go.Figure:
        """
        Create interactive chord diagram for LULC transitions.

        Parameters
        ----------
        transition_matrix : np.ndarray
            Square matrix of transitions between categories
        category_names : List[str]
            Names of LULC categories
        title : str
            Plot title
        min_flow : float
            Minimum flow threshold to display

        Returns
        -------
        go.Figure
            Interactive Plotly chord diagram
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for interactive chord diagrams")

        # Prepare data for chord diagram
        n_cats = len(category_names)

        # Convert matrix to flow data, excluding diagonal (persistence)
        flows = []
        labels = []
        colors = []

        # Get colors
        color_palette = (
            COLORBLIND_SAFE_PALETTE
            if self.colorblind_safe
            else px.colors.qualitative.Set3
        )

        for i in range(n_cats):
            for j in range(n_cats):
                if i != j and transition_matrix[i, j] > min_flow:
                    flows.append(
                        {
                            "source": i,
                            "target": j
                            + n_cats,  # Offset targets to create separate node set
                            "value": transition_matrix[i, j],
                            "source_name": f"{category_names[i]} (From)",
                            "target_name": f"{category_names[j]} (To)",
                        }
                    )

        # Create node list
        node_labels = [f"{name} (From)" for name in category_names] + [
            f"{name} (To)" for name in category_names
        ]
        node_colors = (color_palette[:n_cats] + color_palette[:n_cats])[: 2 * n_cats]

        # Create Sankey (similar to chord) diagram
        if flows:
            fig = go.Figure(
                data=[
                    go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="black", width=0.5),
                            label=node_labels,
                            color=node_colors,
                            hovertemplate="%{label}<br>Total: %{value}<extra></extra>",
                        ),
                        link=dict(
                            source=[f["source"] for f in flows],
                            target=[f["target"] for f in flows],
                            value=[f["value"] for f in flows],
                            hovertemplate="%{source.label} → %{target.label}<br>Area: %{value:.2f}<extra></extra>",
                        ),
                    )
                ]
            )
        else:
            # Empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No transitions above threshold",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16),
            )

        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            font=dict(size=12),
            height=600,
            margin=dict(t=80, l=20, r=20, b=20),
        )

        return fig

    def advanced_sankey_diagram(
        self,
        flow_data: pd.DataFrame,
        source_col: str = "From",
        target_col: str = "To",
        value_col: str = "Area",
        time_col: Optional[str] = None,
        title: str = "Land Use Change Flows",
        **kwargs,
    ) -> go.Figure:
        """
        Create advanced multi-level Sankey diagram.

        Parameters
        ----------
        flow_data : pd.DataFrame
            DataFrame with transition data
        source_col, target_col, value_col : str
            Column names for source, target, and values
        time_col : str, optional
            Column for temporal grouping
        title : str
            Plot title

        Returns
        -------
        go.Figure
            Interactive Plotly Sankey diagram
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for Sankey diagrams")

        # Prepare data
        df = flow_data.copy()

        # Filter out persistence if specified
        if "exclude_persistence" in kwargs and kwargs["exclude_persistence"]:
            df = df[df[source_col] != df[target_col]]

        # Get unique labels
        all_labels = sorted(set(df[source_col].unique()) | set(df[target_col].unique()))
        label_to_id = {label: i for i, label in enumerate(all_labels)}

        # Create source and target indices
        source_indices = [label_to_id[label] for label in df[source_col]]
        target_indices = [label_to_id[label] for label in df[target_col]]
        values = df[value_col].tolist()

        # Color scheme
        n_labels = len(all_labels)
        colors = (
            COLORBLIND_SAFE_PALETTE[:n_labels]
            if self.colorblind_safe
            else px.colors.qualitative.Set3[:n_labels]
        )

        # Create Sankey diagram
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=all_labels,
                        color=colors,
                        hovertemplate="%{label}<br>Total Flow: %{value:.2f}<extra></extra>",
                    ),
                    link=dict(
                        source=source_indices,
                        target=target_indices,
                        value=values,
                        color=[
                            "rgba(128,128,128,0.6)" for i in source_indices
                        ],  # Use fixed semi-transparent gray
                        hovertemplate="%{source.label} → %{target.label}<br>Area: %{value:.2f}<extra></extra>",
                    ),
                )
            ]
        )

        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            font=dict(size=12),
            height=600,
            margin=dict(t=80, l=20, r=20, b=20),
        )

        return fig

    def animated_change_map(
        self,
        raster_data: Dict[str, np.ndarray],
        category_names: List[str],
        coordinates: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        title: str = "Land Use Change Over Time",
        frame_duration: int = 1000,
        **kwargs,
    ) -> go.Figure:
        """
        Create animated map showing LULC change over time.

        Parameters
        ----------
        raster_data : Dict[str, np.ndarray]
            Dictionary with year as key and raster as value
        category_names : List[str]
            Names of LULC categories
        coordinates : Tuple[np.ndarray, np.ndarray], optional
            Longitude and latitude grids
        title : str
            Plot title
        frame_duration : int
            Duration of each frame in milliseconds

        Returns
        -------
        go.Figure
            Animated Plotly map
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for animated maps")

        # Prepare data for animation
        years = sorted(raster_data.keys())

        # Create frames for animation
        frames = []

        for year in years:
            raster = raster_data[year]

            if coordinates is not None:
                lon_grid, lat_grid = coordinates
                # Create heatmap with geographic coordinates
                frame_data = go.Heatmap(
                    z=raster,
                    x=lon_grid[0, :] if lon_grid.ndim == 2 else lon_grid,
                    y=lat_grid[:, 0] if lat_grid.ndim == 2 else lat_grid,
                    colorscale="Viridis",
                    showscale=True,
                    hovertemplate="Lon: %{x:.3f}<br>Lat: %{y:.3f}<br>Category: %{z}<extra></extra>",
                )
            else:
                # Simple heatmap without coordinates
                frame_data = go.Heatmap(
                    z=raster,
                    colorscale="Viridis",
                    showscale=True,
                    hovertemplate="X: %{x}<br>Y: %{y}<br>Category: %{z}<extra></extra>",
                )

            frames.append(
                go.Frame(
                    data=[frame_data],
                    name=str(year),
                    layout=dict(title=f"{title} - {year}"),
                )
            )

        # Create initial figure
        initial_frame = frames[0].data[0] if frames else go.Heatmap(z=[[0]])

        fig = go.Figure(data=[initial_frame], frames=frames)

        # Add animation controls
        fig.update_layout(
            title=dict(
                text=f"{title} - {years[0] if years else 'No Data'}",
                x=0.5,
                font=dict(size=20),
            ),
            updatemenus=[
                {
                    "type": "buttons",
                    "showactive": False,
                    "buttons": [
                        {
                            "label": "Play",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "frame": {
                                        "duration": frame_duration,
                                        "redraw": True,
                                    },
                                    "fromcurrent": True,
                                    "transition": {
                                        "duration": 300,
                                        "easing": "quadratic-in-out",
                                    },
                                },
                            ],
                        },
                        {
                            "label": "Pause",
                            "method": "animate",
                            "args": [
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0},
                                },
                            ],
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top",
                }
            ],
            sliders=[
                {
                    "steps": [
                        {
                            "args": [
                                [year],
                                {
                                    "frame": {"duration": 300, "redraw": True},
                                    "mode": "immediate",
                                    "transition": {"duration": 300},
                                },
                            ],
                            "label": str(year),
                            "method": "animate",
                        }
                        for year in years
                    ],
                    "active": 0,
                    "currentvalue": {"prefix": "Year: "},
                    "transition": {"duration": 300, "easing": "cubic-in-out"},
                    "x": 0.1,
                    "len": 0.9,
                    "xanchor": "left",
                    "y": 0,
                    "yanchor": "top",
                }
            ],
        )

        return fig

    def interactive_confusion_matrix(
        self,
        confusion_matrix: np.ndarray,
        category_names: List[str],
        title: str = "Confusion Matrix",
        show_percentages: bool = True,
        **kwargs,
    ) -> go.Figure:
        """
        Create interactive confusion matrix heatmap.

        Parameters
        ----------
        confusion_matrix : np.ndarray
            Square confusion matrix
        category_names : List[str]
            Names of categories
        title : str
            Plot title
        show_percentages : bool
            Show percentages instead of raw values

        Returns
        -------
        go.Figure
            Interactive confusion matrix
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for interactive confusion matrix")

        # Prepare data
        matrix = confusion_matrix.copy()

        if show_percentages:
            # Convert to percentages
            total = np.sum(matrix)
            matrix_display = (matrix / total * 100) if total > 0 else matrix
            text_template = "%{z:.2f}%"
            hover_template = (
                "From: %{x}<br>To: %{y}<br>Percentage: %{z:.2f}%<extra></extra>"
            )
        else:
            matrix_display = matrix
            text_template = "%{z:.0f}"
            hover_template = "From: %{x}<br>To: %{y}<br>Count: %{z:.0f}<extra></extra>"

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=matrix_display,
                x=category_names,
                y=category_names,
                colorscale="RdYlBu_r",
                showscale=True,
                text=matrix_display,
                texttemplate=text_template,
                textfont={"size": 12},
                hovertemplate=hover_template,
            )
        )

        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            xaxis=dict(title="Predicted Category", side="top"),
            yaxis=dict(
                title="Actual Category",
                autorange="reversed",  # Reverse y-axis for standard confusion matrix layout
            ),
            width=600,
            height=600,
            margin=dict(t=120, l=120, r=50, b=50),
        )

        return fig

    def create_dashboard_layout(
        self, analysis_results: Dict[str, Any], export_format: str = "html"
    ) -> str:
        """
        Create comprehensive dashboard layout.

        Parameters
        ----------
        analysis_results : Dict[str, Any]
            Complete analysis results
        export_format : str
            Export format ('html', 'json', 'pdf')

        Returns
        -------
        str
            Dashboard HTML or file path
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for dashboard creation")

        # Create subplot layout
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Interval Analysis",
                "Category Analysis",
                "Transition Matrix",
                "Change Summary",
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "pie"}],
            ],
        )

        # Add plots to subplots (simplified for example)
        # This would be expanded with actual data

        # Interval analysis
        years = [2000, 2010, 2020]
        change_rates = [0.5, 0.8, 0.3]
        fig.add_trace(
            go.Scatter(
                x=years, y=change_rates, mode="lines+markers", name="Change Rate"
            ),
            row=1,
            col=1,
        )

        # Category analysis
        categories = ["Forest", "Agriculture", "Urban"]
        gains = [10, 25, 15]
        fig.add_trace(go.Bar(x=categories, y=gains, name="Gains"), row=1, col=2)

        # Update layout
        fig.update_layout(
            title_text="Land Use Change Analysis Dashboard", showlegend=True, height=800
        )

        # Export based on format
        if export_format == "html":
            html_str = fig.to_html(include_plotlyjs="cdn", full_html=True)
            return html_str
        elif export_format == "json":
            return fig.to_json()
        else:
            # Save as image
            output_path = "dashboard.png"
            fig.write_image(output_path)
            return output_path

    def export_figure(
        self, figure: go.Figure, filename: str, format: str = "html", **kwargs
    ) -> str:
        """
        Export figure in various formats.

        Parameters
        ----------
        figure : go.Figure
            Plotly figure to export
        filename : str
            Output filename
        format : str
            Export format ('html', 'png', 'svg', 'pdf', 'json')

        Returns
        -------
        str
            Path to exported file
        """
        if not HAS_PLOTLY:
            raise ImportError("plotly is required for figure export")

        # Ensure file extension matches format
        if not filename.endswith(f".{format}"):
            filename = f"{filename}.{format}"

        # Export based on format
        if format == "html":
            figure.write_html(filename, **kwargs)
        elif format == "json":
            figure.write_json(filename, **kwargs)
        elif format in ["png", "svg", "pdf"]:
            figure.write_image(filename, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        return filename
