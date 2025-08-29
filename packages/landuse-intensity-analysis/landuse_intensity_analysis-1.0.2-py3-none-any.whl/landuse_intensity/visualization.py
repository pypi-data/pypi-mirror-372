"""
Visualization functions for land use and cover change analysis.

This module provides scientific visualization tools for the Pontius-Aldwaik
intensity analysis methodology, including Sankey diagrams, bar charts,
and net/gross change visualizations.

References
----------
Aldwaik, S., & Pontius Jr, R. G. (2012). Intensity analysis to unify
measurements of land change. Landscape and Urban Planning, 106(1), 33-41.
"""

import warnings
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Optional dependencies
HAS_PLOTLY = False
HAS_HOLOVIEWS = False

try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    pass

try:
    import holoviews as hv

    HAS_HOLOVIEWS = True
except ImportError:
    pass


def plot_bar(
    dataset: pd.DataFrame,
    legend_table: pd.DataFrame,
    title: Optional[str] = None,
    caption: str = "LUC Categories",
    xlab: str = "Year",
    ylab: str = "Area (km2 or pixel)",
    area_km2: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    **kwargs,
) -> plt.Figure:
    """Create a grouped barplot representing areas of LUC categories at each time point."""

    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"

    # Prepare data - aggregate by category and year
    annual_data = dataset.groupby(["Year_from", "From"])[area_col].sum().reset_index()
    annual_data = annual_data.rename(columns={"Year_from": "Year", "From": "Category"})

    # Get unique years and categories
    years = sorted(annual_data["Year"].unique())
    categories = sorted(annual_data["Category"].unique())

    # Create color mapping from legend table
    color_map = {}
    if legend_table is not None:
        for _, row in legend_table.iterrows():
            if "color" in row:
                color_map[row["CategoryValue"]] = row["color"]

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Calculate bar positions
    n_categories = len(categories)
    bar_width = 0.8 / n_categories
    x_pos = np.arange(len(years))

    # Plot bars for each category
    for i, category in enumerate(categories):
        category_data = annual_data[annual_data["Category"] == category]

        # Get values for all years (fill missing with 0)
        values = []
        for year in years:
            year_data = category_data[category_data["Year"] == year]
            values.append(year_data[area_col].sum() if not year_data.empty else 0)

        # Plot bars
        ax.bar(
            x_pos + i * bar_width,
            values,
            bar_width,
            label=f"Category {category}",
            color=color_map.get(category, f"C{i}"),
        )

    # Customize plot
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title or "Land Use Categories by Year")
    ax.set_xticks(x_pos + bar_width * (n_categories - 1) / 2)
    ax.set_xticklabels(years)
    ax.legend(title=caption)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_sankey(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    title: str = "Land Use Change Flows",
    area_km2: bool = True,
    min_flow: float = 0.01,
    **kwargs,
):
    """Create a Sankey diagram showing land use change flows."""
    if not HAS_PLOTLY:
        raise ImportError(
            "plotly is required for plot_sankey. Install with: pip install plotly"
        )

    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"

    # Filter out persistence (From == To) and small flows
    flows = dataset[dataset["From"] != dataset["To"]].copy()

    if len(flows) == 0:
        warnings.warn("No transitions found (all From == To)")
        return go.Figure()

    # Apply minimum flow threshold
    total_change = flows[area_col].sum()
    min_threshold = total_change * min_flow
    flows = flows[flows[area_col] >= min_threshold]

    # Create node labels
    all_categories = sorted(set(flows["From"].unique()) | set(flows["To"].unique()))
    node_labels = [f"Category {cat}" for cat in all_categories]

    # Create links
    source_list = []
    target_list = []
    value_list = []

    for _, row in flows.iterrows():
        source_idx = all_categories.index(row["From"])
        target_idx = all_categories.index(row["To"])
        value = row[area_col]
        source_list.append(source_idx)
        target_list.append(target_idx)
        value_list.append(value)

    # Create Sankey diagram
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=node_labels,
                    color="blue",
                ),
                link=dict(source=source_list, target=target_list, value=value_list),
            )
        ]
    )

    fig.update_layout(title_text=title, font_size=10)
    return fig


def plot_chord_diagram(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    title: str = "Land Use Change Chord Diagram",
    area_km2: bool = True,
    **kwargs,
):
    """Create a chord diagram showing land use change connections."""
    if not HAS_HOLOVIEWS:
        raise ImportError(
            "holoviews is required for plot_chord_diagram. Install with: pip install holoviews"
        )

    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"

    # Prepare data for chord diagram
    flows = dataset[dataset["From"] != dataset["To"]].copy()

    if len(flows) == 0:
        warnings.warn("No transitions found (all From == To)")
        return None

    # Create chord data format: (source, target, value)
    chord_data = []
    for _, row in flows.iterrows():
        chord_data.append((f"Cat_{row['From']}", f"Cat_{row['To']}", row[area_col]))

    chord = hv.Chord(chord_data, vdims="value").select(value=lambda x: x > 0)
    return chord


def netgross_plot(
    dataset: pd.DataFrame,
    legend_table: Optional[pd.DataFrame] = None,
    title: str = "Net vs Gross Changes",
    area_km2: bool = True,
    figsize: Tuple[int, int] = (10, 8),
    **kwargs,
) -> plt.Figure:
    """Create a plot comparing net vs gross changes by category."""
    # Choose area column
    area_col = "km2" if area_km2 else "QtPixel"

    # Calculate gains and losses for each category
    categories = sorted(set(dataset["From"].unique()) | set(dataset["To"].unique()))

    net_changes = []
    gross_changes = []
    category_labels = []

    for cat in categories:
        # Calculate gains (transitions TO this category)
        gains = dataset[dataset["To"] == cat][area_col].sum()

        # Calculate losses (transitions FROM this category)
        losses = dataset[dataset["From"] == cat][area_col].sum()

        # Net change = gains - losses
        net_change = gains - losses

        # Gross change = gains + losses
        gross_change = gains + losses

        net_changes.append(net_change)
        gross_changes.append(gross_change)
        category_labels.append(f"Category {cat}")

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    x_pos = np.arange(len(categories))
    width = 0.35

    ax.bar(x_pos - width / 2, net_changes, width, label="Net Change", alpha=0.8)
    ax.bar(x_pos + width / 2, gross_changes, width, label="Gross Change", alpha=0.8)

    # Customize plot
    ax.set_xlabel("Land Use Categories")
    ax.set_ylabel(f"Area ({area_col})")
    ax.set_title(title)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(category_labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.5)

    plt.tight_layout()
    return fig
