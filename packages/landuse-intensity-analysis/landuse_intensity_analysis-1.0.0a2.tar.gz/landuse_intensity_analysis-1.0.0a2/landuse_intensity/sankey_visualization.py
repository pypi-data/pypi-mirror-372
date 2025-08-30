"""
Sankey Diagram Visualization Module

This module provides specialized Sankey diagram visualizations for land use and land cover
change analysis, including single-step and multi-step transition diagrams with automatic
color extraction and modern design.

Key Features:
- Single-step Sankey diagrams with data-driven color extraction
- Multi-step Sankey diagrams for temporal analysis
- Automatic color generation based on transition patterns
- Modern, publication-ready visualizations
- Interactive HTML exports with hover information
- Multiple export formats (HTML, PNG, SVG, PDF)

Based on research from:
- Frontiers in Environmental Science LULC prediction methodologies
- ResearchGate geospatial assessment techniques
- Modern Python visualization libraries (plotly, matplotlib)
- Aldwaik & Pontius intensity analysis methodology

Functions:
- plot_single_step_sankey(): Single-step Sankey diagrams with automatic color extraction
- plot_multi_step_sankey(): Multi-step Sankey diagrams with temporal analysis
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd

# Optional dependencies
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not available. Sankey diagrams will not be available.")


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def plot_single_step_sankey(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "landuse_sankey",
    title: str = "Land Use Transitions",
    width: int = 1200,
    height: int = 800,
    min_flow: float = 0.1,
    node_thickness: int = 30,
    node_padding: int = 25,
    show_persistence: bool = True,
    color_intensity: float = 0.8,
    export_formats: List[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    Create a modern Sankey diagram for land use transitions with automatic color extraction.

    This function automatically extracts colors from the contingency table data and creates
    a modern, publication-ready Sankey diagram with enhanced interactivity.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function containing transition data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "landuse_sankey"
        Base filename for output files
    title : str, default "Land Use Transitions"
        Plot title
    width : int, default 1200
        Plot width in pixels
    height : int, default 800
        Plot height in pixels
    min_flow : float, default 0.1
        Minimum flow size to display (km²)
    node_thickness : int, default 30
        Thickness of nodes in pixels
    node_padding : int, default 25
        Padding between nodes in pixels
    show_persistence : bool, default True
        Whether to show persistence flows (diagonal elements)
    color_intensity : float, default 0.8
        Color intensity for nodes (0.0 to 1.0)
    export_formats : list of str, optional
        Export formats ['html', 'png', 'svg', 'pdf']
    **kwargs
        Additional arguments passed to plotly

    Returns
    -------
    dict
        Dictionary with paths to generated files

    Examples
    --------
    >>> ct = lui.contingency_table('path/to/rasters/')
    >>> files = lui.plot_single_step_sankey(ct)
    >>> print(f"Interactive: {files['html']}")
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for Sankey diagrams. Install with: pip install plotly")

    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Set default export formats
    if export_formats is None:
        export_formats = ['html', 'png']

    # Extract transition matrix and colors from contingency data
    transition_matrix, node_colors, legend_map = _extract_sankey_data(contingency_data, min_flow, show_persistence)

    if transition_matrix.empty:
        warnings.warn("No transitions found above minimum flow threshold")
        return {}

    # Generate modern Sankey diagram
    fig = _create_modern_sankey(
        transition_matrix=transition_matrix,
        node_colors=node_colors,
        legend_map=legend_map,
        title=title,
        width=width,
        height=height,
        node_thickness=node_thickness,
        node_padding=node_padding,
        color_intensity=color_intensity,
        **kwargs
    )

    # Export files
    generated_files = {}
    for fmt in export_formats:
        if fmt.lower() == 'html':
            html_path = output_path / f"{filename}.html"
            fig.write_html(str(html_path))
            generated_files['html'] = str(html_path)
        elif fmt.lower() == 'png':
            png_path = output_path / f"{filename}.png"
            fig.write_image(str(png_path), width=width, height=height, scale=2)
            generated_files['png'] = str(png_path)
        elif fmt.lower() == 'svg':
            svg_path = output_path / f"{filename}.svg"
            fig.write_image(str(svg_path), width=width, height=height)
            generated_files['svg'] = str(svg_path)
        elif fmt.lower() == 'pdf':
            pdf_path = output_path / f"{filename}.pdf"
            fig.write_image(str(pdf_path), width=width, height=height)
            generated_files['pdf'] = str(pdf_path)

    # Export transition data
    _export_transition_data(transition_matrix, output_path, filename)

    return generated_files


def _extract_sankey_data(contingency_data: Dict, min_flow: float, show_persistence: bool):
    """
    Extract transition matrix, colors, and legend from contingency data.

    Parameters
    ----------
    contingency_data : dict
        Contingency table data
    min_flow : float
        Minimum flow threshold
    show_persistence : bool
        Whether to include persistence flows

    Returns
    -------
    tuple
        (transition_matrix, node_colors, legend_map)
    """
    # Extract data based on available keys
    if 'lulc_SingleStep' in contingency_data:
        data = contingency_data['lulc_SingleStep'].copy()
        is_multistep = False
    elif 'lulc_MultiStep' in contingency_data:
        # Use first period for single-step visualization
        multistep = contingency_data['lulc_MultiStep']
        if 'Period' in multistep.columns:
            first_period = multistep['Period'].iloc[0]
            data = multistep[multistep['Period'] == first_period].copy()
        else:
            data = multistep.copy()
        is_multistep = True
    else:
        raise ValueError("No transition data found. Expected 'lulc_SingleStep' or 'lulc_MultiStep'")

    # Extract legend for color mapping
    legend = contingency_data.get('tb_legend', pd.DataFrame())

    # Create transition matrix
    transition_matrix = data.pivot_table(
        index='From',
        columns='To',
        values='km2',
        fill_value=0
    )

    # Filter small flows
    transition_matrix = transition_matrix.where(transition_matrix >= min_flow, 0)

    # Remove persistence if not requested
    if not show_persistence:
        for cat in transition_matrix.index:
            if cat in transition_matrix.columns:
                transition_matrix.loc[cat, cat] = 0

    # Extract unique categories
    all_categories = sorted(set(transition_matrix.index) | set(transition_matrix.columns))

    # Generate colors based on data characteristics
    node_colors = _generate_data_driven_colors(all_categories, legend, transition_matrix)

    # Create legend mapping
    if not legend.empty and 'CategoryValue' in legend.columns:
        legend_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        legend_map = {cat: cat for cat in all_categories}

    return transition_matrix, node_colors, legend_map


def _generate_data_driven_colors(categories: List[str], legend: pd.DataFrame, transition_matrix: pd.DataFrame):
    """
    Generate colors based on data characteristics and legend information.

    Parameters
    ----------
    categories : list
        List of land use categories
    legend : pd.DataFrame
        Legend data with color information
    transition_matrix : pd.DataFrame
        Transition matrix for flow analysis

    Returns
    -------
    list
        List of colors for each category
    """
    colors = []

    # Try to extract colors from legend first
    if not legend.empty and 'Color' in legend.columns:
        for cat in categories:
            if cat in legend.index:
                color = legend.loc[cat, 'Color']
                colors.append(color)
            else:
                # Generate color based on category characteristics
                colors.append(_generate_category_color(cat, transition_matrix))
    else:
        # Generate colors based on transition patterns
        for cat in categories:
            colors.append(_generate_category_color(cat, transition_matrix))

    return colors


def _generate_category_color(category: str, transition_matrix: pd.DataFrame) -> str:
    """
    Generate a color for a category based on its transition characteristics.

    Parameters
    ----------
    category : str
        Land use category
    transition_matrix : pd.DataFrame
        Transition matrix

    Returns
    -------
    str
        Hex color code
    """
    # Calculate transition characteristics
    if category in transition_matrix.index:
        outflows = transition_matrix.loc[category].sum()
        inflows = transition_matrix[category].sum() if category in transition_matrix.columns else 0
        persistence = transition_matrix.loc[category, category] if category in transition_matrix.columns else 0

        # Calculate flow ratio (outflow/inflow)
        total_flow = outflows + inflows
        if total_flow > 0:
            flow_ratio = outflows / total_flow
        else:
            flow_ratio = 0.5

        # Generate color based on characteristics
        if persistence > outflows + inflows:  # Dominant persistence
            # Stable categories - greens and blues
            hue = 120 + (flow_ratio * 60)  # Green to cyan
        elif outflows > inflows:  # Net loss
            # Loss categories - reds and oranges
            hue = 0 + (flow_ratio * 60)  # Red to orange
        elif inflows > outflows:  # Net gain
            # Gain categories - yellows and greens
            hue = 60 + (flow_ratio * 60)  # Yellow to green
        else:
            # Balanced - neutral colors
            hue = 180 + (flow_ratio * 60)  # Cyan to blue

        # Convert HSL to RGB and then to hex
        return _hsl_to_hex(hue, 70, 50)
    else:
        # Default color for categories with no outflow data
        return "#95A5A6"  # Gray


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL to hex color."""
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0

    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p

        if l < 0.5:
            q = l * (1 + s)
        else:
            q = l + s - l * s
        p = 2 * l - q

        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _create_modern_sankey(
    transition_matrix: pd.DataFrame,
    node_colors: List[str],
    legend_map: Dict[str, str],
    title: str,
    width: int,
    height: int,
    node_thickness: int,
    node_padding: int,
    color_intensity: float,
    **kwargs
) -> go.Figure:
    """
    Create the modern Sankey diagram figure.

    Parameters
    ----------
    transition_matrix : pd.DataFrame
        Filtered transition matrix
    node_colors : list
        Colors for each category
    legend_map : dict
        Mapping from category codes to names
    title : str
        Plot title
    width, height : int
        Figure dimensions
    node_thickness, node_padding : int
        Node styling parameters
    color_intensity : float
        Color intensity multiplier
    **kwargs
        Additional plotly arguments

    Returns
    -------
    plotly.graph_objects.Figure
        The Sankey diagram figure
    """
    # Prepare data for Sankey
    all_categories = list(transition_matrix.index)
    source_labels = [f"{legend_map.get(cat, cat)}<br><sub>Source</sub>" for cat in all_categories]
    target_labels = [f"{legend_map.get(cat, cat)}<br><sub>Target</sub>" for cat in all_categories]
    all_labels = source_labels + target_labels

    # Adjust colors based on intensity
    adjusted_colors = []
    for color in node_colors:
        if color.startswith('#'):
            # Convert hex to rgba with intensity
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            adjusted_colors.append(f'rgba({r}, {g}, {b}, {color_intensity})')
        else:
            adjusted_colors.append(color)

    # Duplicate colors for source and target
    all_node_colors = adjusted_colors + adjusted_colors

    # Prepare links
    sources = []
    targets = []
    values = []
    link_colors = []
    hover_texts = []

    for i, from_cat in enumerate(transition_matrix.index):
        for j, to_cat in enumerate(transition_matrix.columns):
            value = transition_matrix.loc[from_cat, to_cat]
            if value > 0:
                source_idx = all_categories.index(from_cat)
                target_idx = len(all_categories) + all_categories.index(to_cat)

                sources.append(source_idx)
                targets.append(target_idx)
                values.append(value)

                # Create link color based on source node
                source_color = adjusted_colors[all_categories.index(from_cat)]
                if 'rgba' in source_color:
                    link_color = source_color.replace(f', {color_intensity})', ', 0.3)')
                else:
                    link_color = source_color
                link_colors.append(link_color)

                # Enhanced hover text
                transition_type = "Persistence" if from_cat == to_cat else "Change"
                hover_texts.append(
                    f"<b>{transition_type}</b><br>"
                    f"<b>From:</b> {legend_map.get(from_cat, from_cat)}<br>"
                    f"<b>To:</b> {legend_map.get(to_cat, to_cat)}<br>"
                    f"<b>Area:</b> {value:.2f} km²<br>"
                    f"<extra></extra>"
                )

    # Create figure
    fig = go.Figure(data=[go.Sankey(
        valueformat=".2f",
        valuesuffix=" km²",
        node=dict(
            pad=node_padding,
            thickness=node_thickness,
            line=dict(color="white", width=2),
            label=all_labels,
            color=all_node_colors,
            hovertemplate="<b>%{label}</b><br><extra></extra>"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{customdata}",
            customdata=hover_texts
        )
    )])

    # Modern layout
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#2C3E50', family='Arial, sans-serif')
        ),
        width=width,
        height=height,
        font=dict(size=14, color='#34495E', family='Arial, sans-serif'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=120, l=50, r=50, b=80),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#34495E",
            font=dict(color="#34495E", family='Arial, sans-serif')
        )
    )

    # Add summary annotation
    total_flow = sum(values)
    persistence_flow = sum([v for i, v in enumerate(values)
                           if all_categories[sources[i]] == all_categories[targets[i] - len(all_categories)]])

    fig.add_annotation(
        text=f"Total Flow: {total_flow:.2f} km² | Persistence: {persistence_flow:.2f} km²",
        xref="paper", yref="paper",
        x=0.02, y=0.02,
        showarrow=False,
        font=dict(size=12, color='#7F8C8D'),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#BDC3C7",
        borderwidth=1,
        borderpad=8
    )

    return fig


def _export_transition_data(transition_matrix: pd.DataFrame, output_path: Path, filename: str):
    """Export transition data to CSV with metadata."""
    # Prepare data for export
    export_data = []

    for from_cat in transition_matrix.index:
        for to_cat in transition_matrix.columns:
            value = transition_matrix.loc[from_cat, to_cat]
            if value > 0:
                export_data.append({
                    'From': from_cat,
                    'To': to_cat,
                    'Area_km2': value,
                    'Transition_Type': 'Persistence' if from_cat == to_cat else 'Change'
                })

    if export_data:
        export_df = pd.DataFrame(export_data)
        csv_path = output_path / f"{filename}_transitions.csv"
        export_df.to_csv(csv_path, index=False)

        # Also export summary statistics
        summary = {
            'Total_Flow': export_df['Area_km2'].sum(),
            'Persistence_Flow': export_df[export_df['Transition_Type'] == 'Persistence']['Area_km2'].sum(),
            'Change_Flow': export_df[export_df['Transition_Type'] == 'Change']['Area_km2'].sum(),
            'Unique_Categories': len(set(export_df['From'].unique()) | set(export_df['To'].unique())),
            'Transitions_Count': len(export_df)
        }

        summary_df = pd.DataFrame([summary])
        summary_path = output_path / f"{filename}_summary.csv"
        summary_df.to_csv(summary_path, index=False)


def plot_multi_step_sankey(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "multi_step_sankey",
    title: str = "Multi-Step Land Use Transitions",
    width: int = 1400,
    height: int = 900,
    min_flow: float = 0.1,
    node_thickness: int = 25,
    node_padding: int = 20,
    show_persistence: bool = True,
    color_intensity: float = 0.8,
    export_formats: List[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    Create a multi-step Sankey diagram for temporal land use transitions.

    This function creates a comprehensive Sankey diagram showing transitions across
    multiple time periods with automatic color extraction and modern design.

    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function with multi-step data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "multi_step_sankey"
        Base filename for output files
    title : str, default "Multi-Step Land Use Transitions"
        Plot title
    width : int, default 1400
        Plot width in pixels
    height : int, default 900
        Plot height in pixels
    min_flow : float, default 0.1
        Minimum flow size to display (km²)
    node_thickness : int, default 25
        Thickness of nodes in pixels
    node_padding : int, default 20
        Padding between nodes in pixels
    show_persistence : bool, default True
        Whether to show persistence flows
    color_intensity : float, default 0.8
        Color intensity for nodes (0.0 to 1.0)
    export_formats : list of str, optional
        Export formats ['html', 'png', 'svg', 'pdf']
    **kwargs
        Additional arguments passed to plotly

    Returns
    -------
    dict
        Dictionary with paths to generated files

    Examples
    --------
    >>> ct = lui.contingency_table('path/to/rasters/')
    >>> files = lui.plot_multi_step_sankey(ct)
    >>> print(f"Interactive: {files['html']}")
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for Sankey diagrams. Install with: pip install plotly")

    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Set default export formats
    if export_formats is None:
        export_formats = ['html', 'png']

    # Extract multi-step data
    multistep_data = contingency_data.get('lulc_MultiStep')
    if multistep_data is None:
        raise ValueError("Multi-step data not found. Expected 'lulc_MultiStep' in contingency_data")

    # Get unique periods
    periods = sorted(multistep_data['Period'].unique())
    if len(periods) < 2:
        raise ValueError("Multi-step data must contain at least 2 periods")

    # Create comprehensive Sankey diagram
    fig = _create_multi_step_sankey(
        multistep_data=multistep_data,
        periods=periods,
        legend=contingency_data.get('tb_legend', pd.DataFrame()),
        title=title,
        width=width,
        height=height,
        min_flow=min_flow,
        node_thickness=node_thickness,
        node_padding=node_padding,
        show_persistence=show_persistence,
        color_intensity=color_intensity,
        **kwargs
    )

    # Export files
    generated_files = {}
    for fmt in export_formats:
        if fmt.lower() == 'html':
            html_path = output_path / f"{filename}.html"
            fig.write_html(str(html_path))
            generated_files['html'] = str(html_path)
        elif fmt.lower() == 'png':
            png_path = output_path / f"{filename}.png"
            fig.write_image(str(png_path), width=width, height=height, scale=2)
            generated_files['png'] = str(png_path)
        elif fmt.lower() == 'svg':
            svg_path = output_path / f"{filename}.svg"
            fig.write_image(str(svg_path), width=width, height=height)
            generated_files['svg'] = str(svg_path)
        elif fmt.lower() == 'pdf':
            pdf_path = output_path / f"{filename}.pdf"
            fig.write_image(str(pdf_path), width=width, height=height)
            generated_files['pdf'] = str(pdf_path)

    # Export multi-step data
    _export_multi_step_data(multistep_data, output_path, filename)

    return generated_files


def _create_multi_step_sankey(
    multistep_data: pd.DataFrame,
    periods: List[str],
    legend: pd.DataFrame,
    title: str,
    width: int,
    height: int,
    min_flow: float,
    node_thickness: int,
    node_padding: int,
    show_persistence: bool,
    color_intensity: float,
    **kwargs
) -> go.Figure:
    """
    Create multi-step Sankey diagram figure.

    Parameters
    ----------
    multistep_data : pd.DataFrame
        Multi-step transition data
    periods : list
        List of time periods
    legend : pd.DataFrame
        Legend data with colors
    title : str
        Plot title
    width, height : int
        Figure dimensions
    min_flow : float
        Minimum flow threshold
    node_thickness, node_padding : int
        Node styling parameters
    show_persistence : bool
        Whether to show persistence flows
    color_intensity : float
        Color intensity multiplier
    **kwargs
        Additional plotly arguments

    Returns
    -------
    plotly.graph_objects.Figure
        Multi-step Sankey diagram figure
    """
    # Get all unique categories
    all_categories = sorted(multistep_data['From'].unique() | multistep_data['To'].unique())

    # Create legend mapping
    if not legend.empty and 'CategoryValue' in legend.columns:
        legend_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        legend_map = {cat: cat for cat in all_categories}

    # Generate colors for all categories
    node_colors = _generate_data_driven_colors(all_categories, legend, pd.DataFrame())

    # Create node labels for all periods
    node_labels = []
    node_colors_all = []

    for period in periods:
        for cat in all_categories:
            node_labels.append(f"{legend_map.get(cat, cat)}<br><sub>{period}</sub>")
            node_colors_all.append(node_colors[all_categories.index(cat)])

    # Prepare links data
    sources = []
    targets = []
    values = []
    link_colors = []
    hover_texts = []

    # Create links between consecutive periods
    for i in range(len(periods) - 1):
        current_period = periods[i]
        next_period = periods[i + 1]

        # Get transitions for current period
        period_data = multistep_data[multistep_data['Period'] == current_period]

        for _, row in period_data.iterrows():
            from_cat = row['From']
            to_cat = row['To']
            value = row['km2']

            if value >= min_flow:
                # Skip persistence if not requested
                if not show_persistence and from_cat == to_cat:
                    continue

                # Source node index (current period)
                source_idx = i * len(all_categories) + all_categories.index(from_cat)

                # Target node index (next period)
                target_idx = (i + 1) * len(all_categories) + all_categories.index(to_cat)

                sources.append(source_idx)
                targets.append(target_idx)
                values.append(value)

                # Link color based on source node
                source_color = node_colors[all_categories.index(from_cat)]
                if source_color.startswith('#'):
                    r = int(source_color[1:3], 16)
                    g = int(source_color[3:5], 16)
                    b = int(source_color[5:7], 16)
                    link_color = f'rgba({r}, {g}, {b}, 0.3)'
                else:
                    link_color = source_color
                link_colors.append(link_color)

                # Enhanced hover text
                transition_type = "Persistence" if from_cat == to_cat else "Change"
                hover_texts.append(
                    f"<b>{transition_type}</b><br>"
                    f"<b>Period:</b> {current_period} → {next_period}<br>"
                    f"<b>From:</b> {legend_map.get(from_cat, from_cat)}<br>"
                    f"<b>To:</b> {legend_map.get(to_cat, to_cat)}<br>"
                    f"<b>Area:</b> {value:.2f} km²<br>"
                    f"<extra></extra>"
                )

    # Create figure
    fig = go.Figure(data=[go.Sankey(
        valueformat=".2f",
        valuesuffix=" km²",
        node=dict(
            pad=node_padding,
            thickness=node_thickness,
            line=dict(color="white", width=2),
            label=node_labels,
            color=node_colors_all,
            hovertemplate="<b>%{label}</b><br><extra></extra>"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{customdata}",
            customdata=hover_texts
        )
    )])

    # Modern layout for multi-step
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#2C3E50', family='Arial, sans-serif')
        ),
        width=width,
        height=height,
        font=dict(size=14, color='#34495E', family='Arial, sans-serif'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=120, l=50, r=50, b=80),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#34495E",
            font=dict(color="#34495E", family='Arial, sans-serif')
        )
    )

    # Add period information annotation
    period_info = f"Periods: {' → '.join(periods)}"
    fig.add_annotation(
        text=period_info,
        xref="paper", yref="paper",
        x=0.02, y=0.05,
        showarrow=False,
        font=dict(size=12, color='#7F8C8D'),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#BDC3C7",
        borderwidth=1,
        borderpad=8
    )

    return fig


def _export_multi_step_data(multistep_data: pd.DataFrame, output_path: Path, filename: str):
    """Export multi-step transition data to CSV."""
    csv_path = output_path / f"{filename}_multistep.csv"
    multistep_data.to_csv(csv_path, index=False)

    # Create summary by period
    summary_by_period = multistep_data.groupby('Period').agg({
        'km2': ['sum', 'count'],
        'From': 'nunique',
        'To': 'nunique'
    }).round(2)

    summary_path = output_path / f"{filename}_multistep_summary.csv"
    summary_by_period.to_csv(summary_path)


# Export public functions
__all__ = [
    'plot_single_step_sankey',
    'plot_multi_step_sankey',
]
