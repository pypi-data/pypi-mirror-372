"""
Bar Chart and Gain/Loss Analysis Visualization Module

This module provides specialized bar chart visualizations for land use and land cover
change analysis, including gain/loss analysis, area comparisons, and statistical plots
with modern design and comprehensive annotations.

Key Features:
- Bar plots for LULC area analysis with customizable styling
- Gain/loss analysis charts from scientific literature
- Statistical validation plots (accuracy, kappa statistics)
- Modern, publication-ready visualizations
- Multiple export formats (PNG, SVG, PDF)

Based on research from:
- Frontiers in Environmental Science LULC prediction methodologies
- ResearchGate geospatial assessment techniques
- Modern Python visualization libraries (matplotlib, seaborn)
- Aldwaik & Pontius intensity analysis methodology

Functions:
- plot_barplot_lulc(): Bar plots for LULC data with styling options
- plot_gain_loss_analysis(): Gain/loss analysis charts from scientific literature
- plot_accuracy_assessment(): Statistical validation plots
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec

# Set matplotlib style for publication-quality plots
plt.style.use('default')
sns.set_palette("husl")


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def plot_barplot_lulc(
    data: Union[pd.DataFrame, pd.Series, Dict],
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use and Land Cover Areas",
    figsize: Tuple[int, int] = (12, 8),
    color_palette: str = "Set2",
    orientation: str = "vertical",
    show_values: bool = True,
    show_percentages: bool = False,
    sort_by: Optional[str] = "area",
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create a bar plot visualization for LULC data.

    Parameters:
    -----------
    data : pd.DataFrame, pd.Series, or dict
        LULC data to visualize
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    color_palette : str
        Color palette name for bars
    orientation : str
        'vertical' or 'horizontal' bars
    show_values : bool
        Whether to show values on bars
    show_percentages : bool
        Whether to show percentages
    sort_by : str, optional
        Sort bars by 'area', 'name', or None
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The bar plot figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Prepare data
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Area'])
    elif isinstance(data, pd.Series):
        df = data.reset_index()
        df.columns = ['Category', 'Area']
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
        if len(df.columns) == 2:
            df.columns = ['Category', 'Area']
    else:
        raise ValueError("Data must be DataFrame, Series, or dict")

    # Sort data if requested
    if sort_by == "area":
        df = df.sort_values('Area', ascending=False)
    elif sort_by == "name":
        df = df.sort_values('Category')

    # Calculate percentages
    total_area = df['Area'].sum()
    df['Percentage'] = (df['Area'] / total_area * 100).round(2)

    # Create figure
    if scientific_style:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")

        # Modern color palette
        colors = sns.color_palette(color_palette, len(df))
    else:
        fig, ax = plt.subplots(figsize=figsize)
        colors = plt.cm.get_cmap(color_palette)(np.linspace(0, 1, len(df)))

    # Create bar plot
    if orientation == "vertical":
        bars = ax.bar(df['Category'], df['Area'], color=colors, **kwargs)
        ax.set_xlabel('Land Use Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Area (km²)', fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=10)
    else:
        bars = ax.barh(df['Category'], df['Area'], color=colors, **kwargs)
        ax.set_xlabel('Area (km²)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Land Use Category', fontsize=12, fontweight='bold')
        ax.tick_params(axis='y', labelsize=10)

    # Modern styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y' if orientation == 'vertical' else 'x')

    # Add values on bars
    if show_values:
        for bar, area, pct in zip(bars, df['Area'], df['Percentage']):
            if orientation == "vertical":
                height = bar.get_height()
                if show_percentages:
                    label = '.1f'
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(df['Area'])*0.01,
                           label, ha='center', va='bottom', fontsize=9, fontweight='bold')
                else:
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(df['Area'])*0.01,
                           '.1f', ha='center', va='bottom', fontsize=9, fontweight='bold')
            else:
                width = bar.get_width()
                if show_percentages:
                    label = '.1f'
                    ax.text(width + max(df['Area'])*0.01, bar.get_y() + bar.get_height()/2.,
                           label, ha='left', va='center', fontsize=9, fontweight='bold')
                else:
                    ax.text(width + max(df['Area'])*0.01, bar.get_y() + bar.get_height()/2.,
                           '.1f', ha='left', va='center', fontsize=9, fontweight='bold')

    # Add statistical annotations
    stats_text = ".1f"".1f"".1f"f"""
Total Area: {total_area:.1f} km²
Categories: {len(df)}
Largest: {df.loc[df['Area'].idxmax(), 'Category']} ({df['Area'].max():.1f} km²)
Smallest: {df.loc[df['Area'].idxmin(), 'Category']} ({df['Area'].min():.1f} km²)
"""

    # Position annotation
    if orientation == "vertical":
        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5',
                         facecolor='white',
                         alpha=0.9,
                         edgecolor='gray'))
    else:
        ax.text(0.98, 0.02, stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='bottom',
                horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5',
                         facecolor='white',
                         alpha=0.9,
                         edgecolor='gray'))

    plt.tight_layout()

    # Save files
    if filename:
        # Save PNG
        fig.savefig(output_path / f"{filename}.png",
                   dpi=300, bbox_inches='tight', facecolor='white')
        # Save SVG
        fig.savefig(output_path / f"{filename}.svg",
                   bbox_inches='tight', facecolor='white')
        # Save PDF
        fig.savefig(output_path / f"{filename}.pdf",
                   bbox_inches='tight', facecolor='white')

        # Export data
        df.to_csv(output_path / f"{filename}_data.csv", index=False)

        # Export statistics
        stats = {
            'Total_Area_km2': total_area,
            'Number_of_Categories': len(df),
            'Largest_Category': df.loc[df['Area'].idxmax(), 'Category'],
            'Largest_Area_km2': df['Area'].max(),
            'Smallest_Category': df.loc[df['Area'].idxmin(), 'Category'],
            'Smallest_Area_km2': df['Area'].min(),
            'Mean_Area_km2': df['Area'].mean(),
            'Median_Area_km2': df['Area'].median(),
            'Std_Area_km2': df['Area'].std()
        }

        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(output_path / f"{filename}_statistics.csv", index=False)

    return fig


def plot_gain_loss_analysis(
    contingency_data: Dict,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use Gain/Loss Analysis",
    figsize: Tuple[int, int] = (14, 10),
    color_scheme: str = "RdYlGn",
    show_net_change: bool = True,
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create a comprehensive gain/loss analysis chart from scientific literature.

    Parameters:
    -----------
    contingency_data : dict
        Results from contingency_table() function
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    color_scheme : str
        Color scheme for the analysis
    show_net_change : bool
        Whether to show net change calculations
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The gain/loss analysis figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Extract data
    if 'lulc_SingleStep' in contingency_data:
        data = contingency_data['lulc_SingleStep'].copy()
    else:
        raise ValueError("No transition data found")

    # Create transition matrix
    transition_matrix = data.pivot_table(
        index='From',
        columns='To',
        values='km2',
        fill_value=0
    )

    # Calculate gains and losses
    categories = list(transition_matrix.index)
    gains = []
    losses = []
    net_changes = []

    for cat in categories:
        # Gain: inflows from other categories
        gain = transition_matrix.loc[transition_matrix.index != cat, cat].sum()
        gains.append(gain)

        # Loss: outflows to other categories
        loss = transition_matrix.loc[cat, transition_matrix.columns != cat].sum()
        losses.append(loss)

        # Net change
        net_change = gain - loss
        net_changes.append(net_change)

    # Create analysis DataFrame
    analysis_df = pd.DataFrame({
        'Category': categories,
        'Gains_km2': gains,
        'Losses_km2': losses,
        'Net_Change_km2': net_changes,
        'Net_Change_Percent': [(nc / (gains[i] + losses[i]) * 100) if (gains[i] + losses[i]) > 0 else 0
                              for i, nc in enumerate(net_changes)]
    })

    # Sort by absolute net change
    analysis_df['Abs_Net_Change'] = analysis_df['Net_Change_km2'].abs()
    analysis_df = analysis_df.sort_values('Abs_Net_Change', ascending=False)
    analysis_df = analysis_df.drop('Abs_Net_Change', axis=1)

    # Create figure with subplots
    if scientific_style:
        fig = plt.figure(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig = plt.figure(figsize=figsize)

    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Gains vs Losses bar chart
    ax1 = fig.add_subplot(gs[0, :])
    x = np.arange(len(analysis_df))
    width = 0.35

    bars1 = ax1.bar(x - width/2, analysis_df['Gains_km2'], width,
                   label='Gains', color='#2E8B57', alpha=0.8)
    bars2 = ax1.bar(x + width/2, analysis_df['Losses_km2'], width,
                   label='Losses', color='#DC143C', alpha=0.8)

    ax1.set_xlabel('Land Use Category', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Area (km²)', fontsize=12, fontweight='bold')
    ax1.set_title('Gains vs Losses by Category', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(analysis_df['Category'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Net change bar chart
    ax2 = fig.add_subplot(gs[1, 0])
    colors = ['#2E8B57' if x > 0 else '#DC143C' for x in analysis_df['Net_Change_km2']]
    bars3 = ax2.bar(analysis_df['Category'], analysis_df['Net_Change_km2'],
                   color=colors, alpha=0.8)

    ax2.set_xlabel('Land Use Category', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Net Change (km²)', fontsize=10, fontweight='bold')
    ax2.set_title('Net Change by Category', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    ax2.grid(True, alpha=0.3)

    # 3. Summary statistics
    ax3 = fig.add_subplot(gs[1, 1])

    # Calculate summary stats
    total_gains = analysis_df['Gains_km2'].sum()
    total_losses = analysis_df['Losses_km2'].sum()
    total_net = analysis_df['Net_Change_km2'].sum()

    categories_gaining = (analysis_df['Net_Change_km2'] > 0).sum()
    categories_losing = (analysis_df['Net_Change_km2'] < 0).sum()
    categories_stable = (analysis_df['Net_Change_km2'] == 0).sum()

    # Create summary text
    summary_text = ".1f"".1f"".1f"".1f"".1f"".1f"f"""
Summary Statistics:

Total Gains: {total_gains:.1f} km²
Total Losses: {total_losses:.1f} km²
Net Change: {total_net:.1f} km²

Categories:
• Gaining: {categories_gaining}
• Losing: {categories_losing}
• Stable: {categories_stable}

Top Gainer:
{analysis_df.loc[analysis_df['Net_Change_km2'].idxmax(), 'Category']}
({analysis_df['Net_Change_km2'].max():.1f} km²)

Top Loser:
{analysis_df.loc[analysis_df['Net_Change_km2'].idxmin(), 'Category']}
({analysis_df['Net_Change_km2'].min():.1f} km²)
"""

    ax3.text(0.05, 0.95, summary_text,
             transform=ax3.transAxes,
             fontsize=10,
             verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='white',
                      alpha=0.9,
                      edgecolor='gray'))

    ax3.set_title('Analysis Summary', fontsize=12, fontweight='bold')
    ax3.axis('off')

    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout()

    # Save files
    if filename:
        # Save PNG
        fig.savefig(output_path / f"{filename}.png",
                   dpi=300, bbox_inches='tight', facecolor='white')
        # Save SVG
        fig.savefig(output_path / f"{filename}.svg",
                   bbox_inches='tight', facecolor='white')
        # Save PDF
        fig.savefig(output_path / f"{filename}.pdf",
                   bbox_inches='tight', facecolor='white')

        # Export analysis data
        analysis_df.to_csv(output_path / f"{filename}_analysis.csv", index=False)

        # Export summary statistics
        summary_stats = {
            'Total_Gains_km2': total_gains,
            'Total_Losses_km2': total_losses,
            'Total_Net_Change_km2': total_net,
            'Categories_Gaining': categories_gaining,
            'Categories_Losing': categories_losing,
            'Categories_Stable': categories_stable,
            'Top_Gainer_Category': analysis_df.loc[analysis_df['Net_Change_km2'].idxmax(), 'Category'],
            'Top_Gainer_Amount_km2': analysis_df['Net_Change_km2'].max(),
            'Top_Loser_Category': analysis_df.loc[analysis_df['Net_Change_km2'].idxmin(), 'Category'],
            'Top_Loser_Amount_km2': analysis_df['Net_Change_km2'].min()
        }

        summary_df = pd.DataFrame([summary_stats])
        summary_df.to_csv(output_path / f"{filename}_summary.csv", index=False)

    return fig


def plot_accuracy_assessment(
    accuracy_data: Dict,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Accuracy Assessment",
    figsize: Tuple[int, int] = (12, 8),
    show_kappa: bool = True,
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create statistical validation plots for accuracy assessment.

    Parameters:
    -----------
    accuracy_data : dict
        Dictionary containing accuracy metrics
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    show_kappa : bool
        Whether to show kappa statistics
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The accuracy assessment figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Create figure
    if scientific_style:
        fig, axes = plt.subplots(2, 2, figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig, axes = plt.subplots(2, 2, figsize=figsize)

    axes = axes.ravel()

    # 1. Overall Accuracy
    if 'overall_accuracy' in accuracy_data:
        overall_acc = accuracy_data['overall_accuracy']
        axes[0].bar(['Overall Accuracy'], [overall_acc], color='#2E8B57', alpha=0.8)
        axes[0].set_ylim(0, 1)
        axes[0].set_ylabel('Accuracy')
        axes[0].set_title('Overall Accuracy', fontweight='bold')
        axes[0].text(0, overall_acc + 0.02, '.3f',
                    ha='center', va='bottom', fontweight='bold')

    # 2. Producer's vs User's Accuracy
    if 'producers_accuracy' in accuracy_data and 'users_accuracy' in accuracy_data:
        categories = list(accuracy_data['producers_accuracy'].keys())
        producers = list(accuracy_data['producers_accuracy'].values())
        users = list(accuracy_data['users_accuracy'].values())

        x = np.arange(len(categories))
        width = 0.35

        axes[1].bar(x - width/2, producers, width, label="Producer's", color='#4169E1', alpha=0.8)
        axes[1].bar(x + width/2, users, width, label="User's", color='#DC143C', alpha=0.8)

        axes[1].set_xlabel('Categories')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title("Producer's vs User's Accuracy", fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(categories, rotation=45, ha='right')
        axes[1].legend()
        axes[1].set_ylim(0, 1)

    # 3. Kappa Statistics
    if show_kappa and 'kappa' in accuracy_data:
        kappa = accuracy_data['kappa']
        axes[2].bar(['Kappa'], [kappa], color='#FFD700', alpha=0.8)
        axes[2].set_ylim(-1, 1)
        axes[2].set_ylabel('Kappa Value')
        axes[2].set_title('Kappa Statistics', fontweight='bold')
        axes[2].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[2].text(0, kappa + 0.02, '.3f',
                    ha='center', va='bottom', fontweight='bold')

        # Add interpretation
        if kappa > 0.8:
            interpretation = "Very Good"
        elif kappa > 0.6:
            interpretation = "Good"
        elif kappa > 0.4:
            interpretation = "Moderate"
        elif kappa > 0.2:
            interpretation = "Fair"
        else:
            interpretation = "Poor"

        axes[2].text(0, kappa - 0.1, interpretation, ha='center', va='top',
                    fontsize=10, style='italic')

    # 4. F1-Score
    if 'f1_scores' in accuracy_data:
        categories = list(accuracy_data['f1_scores'].keys())
        f1_scores = list(accuracy_data['f1_scores'].values())

        axes[3].bar(categories, f1_scores, color='#8A2BE2', alpha=0.8)
        axes[3].set_xlabel('Categories')
        axes[3].set_ylabel('F1-Score')
        axes[3].set_title('F1-Score by Category', fontweight='bold')
        axes[3].set_ylim(0, 1)
        axes[3].tick_params(axis='x', rotation=45, labelsize=8)

        # Add values on bars
        for i, v in enumerate(f1_scores):
            axes[3].text(i, v + 0.02, '.2f', ha='center', va='bottom', fontweight='bold')

    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout()

    # Save files
    if filename:
        # Save PNG
        fig.savefig(output_path / f"{filename}.png",
                   dpi=300, bbox_inches='tight', facecolor='white')
        # Save SVG
        fig.savefig(output_path / f"{filename}.svg",
                   bbox_inches='tight', facecolor='white')
        # Save PDF
        fig.savefig(output_path / f"{filename}.pdf",
                   bbox_inches='tight', facecolor='white')

        # Export accuracy data
        accuracy_df = pd.DataFrame([accuracy_data])
        accuracy_df.to_csv(output_path / f"{filename}_data.csv", index=False)

    return fig


# Export public functions
__all__ = [
    'plot_barplot_lulc',
    'plot_gain_loss_analysis',
    'plot_accuracy_assessment',
]
