"""
Graph Visualization Module for Land Use and Land Cover (LULC) Change Analysis

This module provides statistical and analytical graph visualizations for LULC change analysis,
including transition matrices, Sankey diagrams, bar plots, and scientific analysis graphs.

Key Features:
- Sankey diagrams for land use transitions using Plotly
- Transition matrix heatmaps using matplotlib and plotly
- Bar plots for LULC area analysis
- Statistical validation plots (accuracy, kappa statistics)
- Gain/loss analysis charts
- Time series analysis plots
- Multi-layer perceptron neural network visualization
- Scientific publication-quality plots

Based on research from:
- Frontiers in Environmental Science LULC prediction methodologies
- ResearchGate geospatial assessment techniques
- Based on land use analysis methodologies
- Modern Python visualization libraries (plotly, matplotlib)
- Aldwaik & Pontius intensity analysis methodology

Functions:
- plot_single_step_sankey(): Single-step Sankey diagrams with customization
- plot_multi_step_sankey(): Multi-step Sankey diagrams with customization
- plot_barplot_lulc(): Bar plots for LULC data with styling options
- plot_transition_matrix_heatmap(): Heatmap visualization of transition matrices
- plot_gain_loss_analysis(): Gain/loss analysis charts from scientific literature
- plot_accuracy_assessment(): Statistical validation plots
- plot_time_series_analysis(): Temporal analysis visualizations
- plot_neural_network_performance(): Neural network model visualization
- plot_markov_transition_probabilities(): Markov chain analysis plots
- plot_confusion_matrix(): Enhanced confusion matrix visualization
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

# Scientific visualization color schemes
SCIENTIFIC_COLORS = {
    'temporal_analysis': ['#440154', '#31688E', '#35B779', '#FDE725'],  # Viridis
    'accuracy_metrics': ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728'],  # Tab10
    'validation': ['#E74C3C', '#2ECC71', '#F39C12', '#9B59B6'],  # Scientific validation
    'neural_network': ['#3498DB', '#E67E22', '#27AE60', '#8E44AD'],  # Network layers
}


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _get_category_colors(n_categories: int) -> List[str]:
    """Get appropriate colors for categories."""
    if n_categories <= len(CATEGORY_COLORS):
        return CATEGORY_COLORS[:n_categories]
    else:
        # Generate additional colors if needed
        import matplotlib.cm as cm
        cmap = cm.get_cmap('tab20')
        return [cmap(i / n_categories) for i in range(n_categories)]


def plot_single_step_sankey(
    tabulation_matrix: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use Transitions",
    width: int = 800,
    height: int = 600,
    font_size: int = 12,
    color_scheme: str = "default",
    show_labels: bool = True,
    save_data: bool = True,
    **kwargs
) -> go.Figure:
    """
    Create a single-step Sankey diagram for land use transitions.
    
    Parameters:
    -----------
    tabulation_matrix : pd.DataFrame
        Cross-tabulation matrix where rows are 'from' categories and columns are 'to' categories
    filename : str, optional
        Output filename (without extension). If None, will not save
    output_dir : str
        Output directory path
    title : str
        Plot title
    width : int
        Plot width in pixels
    height : int
        Plot height in pixels
    font_size : int
        Font size for labels
    color_scheme : str
        Color scheme to use ('default', 'viridis', 'scientific')
    show_labels : bool
        Whether to show node labels
    save_data : bool
        Whether to save transition data as CSV
    **kwargs
        Additional arguments passed to plotly
    
    Returns:
    --------
    plotly.graph_objects.Figure
        The Sankey diagram figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for Sankey diagrams. Install with: pip install plotly")
    
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    # Extract categories
    from_categories = list(tabulation_matrix.index)
    to_categories = list(tabulation_matrix.columns)
    all_categories = list(set(from_categories + to_categories))
    
    # Create node labels
    node_labels = []
    for cat in all_categories:
        node_labels.append(f"{cat} (T1)")
        node_labels.append(f"{cat} (T2)")
    
    # Create unique node labels to avoid duplication
    unique_labels = []
    for cat in all_categories:
        unique_labels.append(f"{cat}_from")
        unique_labels.append(f"{cat}_to")
    
    # Simplify: use category names with source/target distinction
    source_labels = [f"{cat}" for cat in all_categories]
    target_labels = [f"{cat}" for cat in all_categories]
    all_labels = source_labels + target_labels
    
    # Get colors
    if color_scheme == "scientific":
        node_colors = SCIENTIFIC_COLORS['temporal_analysis']
    elif color_scheme == "viridis":
        node_colors = plt.cm.viridis(np.linspace(0, 1, len(all_categories)))
        node_colors = [f"rgba({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)}, 0.8)" for c in node_colors]
    else:
        node_colors = _get_category_colors(len(all_categories))
    
    # Prepare data for Sankey
    source_indices = []
    target_indices = []
    values = []
    link_colors = []
    
    for i, from_cat in enumerate(from_categories):
        for j, to_cat in enumerate(to_categories):
            value = tabulation_matrix.loc[from_cat, to_cat]
            if value > 0:  # Only show non-zero transitions
                source_idx = all_categories.index(from_cat)
                target_idx = len(all_categories) + all_categories.index(to_cat)
                
                source_indices.append(source_idx)
                target_indices.append(target_idx)
                values.append(value)
                
                # Color links based on transition type
                if from_cat == to_cat:
                    link_colors.append("rgba(149, 165, 166, 0.4)")  # Gray for persistence
                else:
                    link_colors.append("rgba(52, 152, 219, 0.4)")  # Blue for change
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=node_colors * 2,  # Duplicate colors for source and target
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors,
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=font_size + 4)
        ),
        width=width,
        height=height,
        font=dict(size=font_size),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Save files
    if filename:
        # Save figure
        fig.write_html(output_path / f"{filename}.html")
        fig.write_image(output_path / f"{filename}.png", width=width, height=height)
        
        # Save data
        if save_data:
            transition_data = pd.DataFrame({
                'From': [all_categories[i] for i in source_indices],
                'To': [all_categories[i - len(all_categories)] for i in target_indices],
                'Value': values
            })
            transition_data.to_csv(output_path / f"{filename}_data.csv", index=False)
    
    return fig


def plot_transition_matrix_heatmap(
    tabulation_matrix: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use Transition Matrix",
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = "YlOrRd",
    annot: bool = True,
    fmt: str = '.1f',
    show_percentages: bool = False,
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create a heatmap visualization of the transition matrix.
    
    Parameters:
    -----------
    tabulation_matrix : pd.DataFrame
        Cross-tabulation matrix
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    cmap : str
        Colormap name
    annot : bool
        Whether to annotate cells with values
    fmt : str
        String formatting for annotations
    show_percentages : bool
        Whether to show percentages instead of absolute values
    scientific_style : bool
        Whether to use scientific publication style
    **kwargs
        Additional arguments passed to seaborn.heatmap
    
    Returns:
    --------
    matplotlib.figure.Figure
        The heatmap figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    # Create figure
    if scientific_style:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 10
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Prepare data
    matrix_data = tabulation_matrix.copy()
    
    if show_percentages:
        # Convert to percentages
        total = matrix_data.sum().sum()
        matrix_data = (matrix_data / total) * 100
        fmt = '.1f'
        cbar_label = "Percentage (%)"
    else:
        cbar_label = "Area (hectares)" if 'hectares' in str(matrix_data.values.dtype) else "Count"
    
    # Create heatmap
    im = sns.heatmap(
        matrix_data,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        ax=ax,
        cbar_kws={'label': cbar_label},
        **kwargs
    )
    
    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Land Use Class (Time 2)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Land Use Class (Time 1)', fontsize=12, fontweight='bold')
    
    # Rotate labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    # Add grid for scientific publications
    if scientific_style:
        ax.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    
    # Save figure
    if filename:
        fig.savefig(output_path / f"{filename}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_path / f"{filename}.pdf", bbox_inches='tight')
    
    return fig


def plot_barplot_lulc(
    data: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use and Land Cover Areas",
    x_col: str = "class",
    y_col: str = "area",
    time_col: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 8),
    color_palette: str = "husl",
    scientific_style: bool = True,
    show_values: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create bar plots for LULC area analysis.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with LULC data
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    x_col : str
        Column name for x-axis (land use classes)
    y_col : str
        Column name for y-axis (areas)
    time_col : str, optional
        Column name for time periods (for grouped plots)
    figsize : tuple
        Figure size (width, height)
    color_palette : str
        Color palette name
    scientific_style : bool
        Whether to use scientific publication style
    show_values : bool
        Whether to show values on bars
    **kwargs
        Additional arguments passed to seaborn.barplot
    
    Returns:
    --------
    matplotlib.figure.Figure
        The bar plot figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    # Create figure
    if scientific_style:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 10
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create bar plot
    if time_col:
        # Grouped bar plot for multiple time periods
        sns.barplot(
            data=data,
            x=x_col,
            y=y_col,
            hue=time_col,
            palette=color_palette,
            ax=ax,
            **kwargs
        )
        ax.legend(title=time_col.title(), bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        # Simple bar plot
        sns.barplot(
            data=data,
            x=x_col,
            y=y_col,
            palette=color_palette,
            ax=ax,
            **kwargs
        )
    
    # Add value labels on bars
    if show_values:
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f', rotation=90, padding=3)
    
    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    
    # Rotate x labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    if scientific_style:
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # Save figure
    if filename:
        fig.savefig(output_path / f"{filename}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_path / f"{filename}.pdf", bbox_inches='tight')
    
    return fig


def plot_gain_loss_analysis(
    gain_loss_data: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Land Use Gain/Loss Analysis",
    figsize: Tuple[int, int] = (12, 8),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create gain/loss analysis charts based on scientific literature.
    
    This function creates visualization for land use gain and loss analysis
    as described in Frontiers in Environmental Science methodologies.
    
    Parameters:
    -----------
    gain_loss_data : pd.DataFrame
        DataFrame with columns: 'class', 'gain', 'loss', 'net_change'
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication style
    **kwargs
        Additional plotting arguments
    
    Returns:
    --------
    matplotlib.figure.Figure
        The gain/loss analysis figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    if scientific_style:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 10
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Subplot 1: Gain vs Loss
    ax1 = fig.add_subplot(gs[0, :])
    x = np.arange(len(gain_loss_data))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, gain_loss_data['gain'], width, 
                    label='Gain', color=TRANSITION_COLORS['gain'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, gain_loss_data['loss'], width,
                    label='Loss', color=TRANSITION_COLORS['loss'], alpha=0.8)
    
    ax1.set_xlabel('Land Use Class', fontweight='bold')
    ax1.set_ylabel('Area (hectares)', fontweight='bold')
    ax1.set_title('Land Use Gain and Loss by Class', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(gain_loss_data['class'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    # Subplot 2: Net Change
    ax2 = fig.add_subplot(gs[1, 0])
    colors = [TRANSITION_COLORS['gain'] if x >= 0 else TRANSITION_COLORS['loss'] 
              for x in gain_loss_data['net_change']]
    
    bars3 = ax2.bar(gain_loss_data['class'], gain_loss_data['net_change'], 
                    color=colors, alpha=0.8)
    ax2.set_xlabel('Land Use Class', fontweight='bold')
    ax2.set_ylabel('Net Change (hectares)', fontweight='bold')
    ax2.set_title('Net Change by Class', fontweight='bold')
    ax2.set_xticklabels(gain_loss_data['class'], rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Subplot 3: Percentage Change
    ax3 = fig.add_subplot(gs[1, 1])
    if 'percentage_change' in gain_loss_data.columns:
        colors = [TRANSITION_COLORS['gain'] if x >= 0 else TRANSITION_COLORS['loss'] 
                  for x in gain_loss_data['percentage_change']]
        
        bars4 = ax3.bar(gain_loss_data['class'], gain_loss_data['percentage_change'], 
                        color=colors, alpha=0.8)
        ax3.set_xlabel('Land Use Class', fontweight='bold')
        ax3.set_ylabel('Change (%)', fontweight='bold')
        ax3.set_title('Percentage Change by Class', fontweight='bold')
        ax3.set_xticklabels(gain_loss_data['class'], rotation=45, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    
    # Save figure
    if filename:
        fig.savefig(output_path / f"{filename}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_path / f"{filename}.pdf", bbox_inches='tight')
    
    return fig


def plot_accuracy_assessment(
    accuracy_data: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Classification Accuracy Assessment",
    figsize: Tuple[int, int] = (12, 6),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create accuracy assessment plots for classification validation.
    
    Based on ResearchGate and Frontiers methodologies for accuracy assessment
    including overall accuracy, kappa statistics, and producer/user accuracy.
    
    Parameters:
    -----------
    accuracy_data : pd.DataFrame
        DataFrame with accuracy metrics by class and time period
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication style
    **kwargs
        Additional plotting arguments
    
    Returns:
    --------
    matplotlib.figure.Figure
        The accuracy assessment figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    if scientific_style:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 10
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot 1: Overall Accuracy and Kappa over time
    if 'year' in accuracy_data.columns:
        years = accuracy_data['year'].unique()
        overall_acc = accuracy_data.groupby('year')['overall_accuracy'].mean()
        kappa = accuracy_data.groupby('year')['kappa'].mean()
        
        ax1.plot(years, overall_acc, marker='o', linewidth=2, 
                label='Overall Accuracy', color=SCIENTIFIC_COLORS['accuracy_metrics'][0])
        ax1.plot(years, kappa, marker='s', linewidth=2,
                label='Kappa Coefficient', color=SCIENTIFIC_COLORS['accuracy_metrics'][1])
        
        ax1.set_xlabel('Year', fontweight='bold')
        ax1.set_ylabel('Accuracy', fontweight='bold')
        ax1.set_title('Classification Accuracy Over Time', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
    
    # Plot 2: Producer and User Accuracy by Class
    if 'class' in accuracy_data.columns:
        classes = accuracy_data['class'].unique()
        x = np.arange(len(classes))
        width = 0.35
        
        if 'producer_accuracy' in accuracy_data.columns:
            producer_acc = accuracy_data.groupby('class')['producer_accuracy'].mean()
            user_acc = accuracy_data.groupby('class')['user_accuracy'].mean()
            
            bars1 = ax2.bar(x - width/2, producer_acc, width, 
                           label='Producer Accuracy', 
                           color=SCIENTIFIC_COLORS['validation'][0], alpha=0.8)
            bars2 = ax2.bar(x + width/2, user_acc, width,
                           label='User Accuracy', 
                           color=SCIENTIFIC_COLORS['validation'][1], alpha=0.8)
            
            ax2.set_xlabel('Land Use Class', fontweight='bold')
            ax2.set_ylabel('Accuracy', fontweight='bold')
            ax2.set_title('Producer vs User Accuracy', fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(classes, rotation=45, ha='right')
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            ax2.set_ylim(0, 1)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save figure
    if filename:
        fig.savefig(output_path / f"{filename}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_path / f"{filename}.pdf", bbox_inches='tight')
    
    return fig


def plot_confusion_matrix(
    confusion_matrix: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Confusion Matrix",
    figsize: Tuple[int, int] = (10, 8),
    normalize: Optional[str] = None,
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create enhanced confusion matrix visualization.
    
    Parameters:
    -----------
    confusion_matrix : pd.DataFrame
        Confusion matrix with actual vs predicted classes
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    normalize : str, optional
        Normalization method ('true', 'pred', 'all', or None)
    scientific_style : bool
        Whether to use scientific publication style
    **kwargs
        Additional plotting arguments
    
    Returns:
    --------
    matplotlib.figure.Figure
        The confusion matrix figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)
    
    if scientific_style:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 10
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalize if requested
    cm_data = confusion_matrix.copy()
    if normalize == 'true':
        cm_data = cm_data.div(cm_data.sum(axis=1), axis=0)
        fmt = '.2f'
        cbar_label = 'Proportion'
    elif normalize == 'pred':
        cm_data = cm_data.div(cm_data.sum(axis=0), axis=1)
        fmt = '.2f'
        cbar_label = 'Proportion'
    elif normalize == 'all':
        cm_data = cm_data / cm_data.sum().sum()
        fmt = '.2f'
        cbar_label = 'Proportion'
    else:
        fmt = 'd'
        cbar_label = 'Count'
    
    # Create heatmap
    im = sns.heatmap(
        cm_data,
        annot=True,
        fmt=fmt,
        cmap='Blues',
        ax=ax,
        cbar_kws={'label': cbar_label},
        **kwargs
    )
    
    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Predicted Class', fontsize=12, fontweight='bold')
    ax.set_ylabel('Actual Class', fontsize=12, fontweight='bold')
    
    # Rotate labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    # Save figure
    if filename:
        fig.savefig(output_path / f"{filename}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_path / f"{filename}.pdf", bbox_inches='tight')
    
    return fig


# Export main functions
__all__ = [
    'plot_single_step_sankey',
    'plot_transition_matrix_heatmap', 
    'plot_barplot_lulc',
    'plot_gain_loss_analysis',
    'plot_accuracy_assessment',
    'plot_confusion_matrix',
]
