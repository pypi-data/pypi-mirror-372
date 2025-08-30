"""
Matrix Visualization Module

This module provides specialized matrix visualizations for land use and land cover
change analysis, including transition matrix heatmaps and confusion matrices with
modern design and statistical annotations.

Key Features:
- Transition matrix heatmaps with customizable colormaps
- Confusion matrices for accuracy assessment
- Statistical annotations and performance metrics
- Modern, publication-ready visualizations
- Multiple export formats (PNG, SVG, PDF)

Based on research from:
- Frontiers in Environmental Science LULC prediction methodologies
- ResearchGate geospatial assessment techniques
- Modern Python visualization libraries (matplotlib, seaborn)
- Aldwaik & Pontius intensity analysis methodology

Functions:
- plot_transition_matrix_heatmap(): Heatmap visualization of transition matrices
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


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


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
        String format for annotations
    show_percentages : bool
        Whether to show percentages alongside absolute values
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to seaborn.heatmap

    Returns:
    --------
    matplotlib.figure.Figure
        The heatmap figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Create figure with modern styling
    if scientific_style:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")

        # Modern color palette
        colors = ["#f7fbff", "#08306b"] if cmap == "Blues" else ["#fff5f0", "#67000d"]
        cmap_obj = sns.color_palette(colors, as_cmap=True)
    else:
        fig, ax = plt.subplots(figsize=figsize)
        cmap_obj = cmap

    # Prepare data for visualization
    matrix_data = tabulation_matrix.copy()

    # Calculate percentages if requested
    if show_percentages:
        row_sums = matrix_data.sum(axis=1)
        percentages = matrix_data.div(row_sums, axis=0) * 100

    # Create heatmap
    heatmap = sns.heatmap(
        matrix_data,
        annot=annot,
        fmt=fmt,
        cmap=cmap_obj,
        cbar_kws={'label': 'Area (km²)'},
        ax=ax,
        **kwargs
    )

    # Add percentage annotations if requested
    if show_percentages and annot:
        for i in range(len(matrix_data.index)):
            for j in range(len(matrix_data.columns)):
                value = matrix_data.iloc[i, j]
                percentage = percentages.iloc[i, j]
                if value > 0:
                    ax.text(j + 0.5, i + 0.7,
                           f'{percentage:.1f}%',
                           ha='center', va='center',
                           fontsize=8, color='black',
                           bbox=dict(boxstyle='round,pad=0.2',
                                   facecolor='white', alpha=0.8))

    # Modern styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('To Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('From Category', fontsize=12, fontweight='bold')

    # Rotate tick labels for better readability
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)

    # Add grid lines
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Add statistical annotations
    total_area = matrix_data.sum().sum()
    persistence_area = np.diag(matrix_data).sum()
    change_area = total_area - persistence_area

    # Add text annotation
    annotation_text = f'Total: {total_area:.1f} km²\nPersistence: {persistence_area:.1f} km²\nChange: {change_area:.1f} km²'
    ax.text(1.05, 0.5, annotation_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='center',
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
        matrix_data.to_csv(output_path / f"{filename}_data.csv")

        # Export statistics
        stats = {
            'Total_Area_km2': total_area,
            'Persistence_Area_km2': persistence_area,
            'Change_Area_km2': change_area,
            'Persistence_Percentage': (persistence_area / total_area * 100) if total_area > 0 else 0,
            'Change_Percentage': (change_area / total_area * 100) if total_area > 0 else 0,
            'Number_of_Categories': len(matrix_data.index),
            'Number_of_Transitions': (matrix_data > 0).sum().sum()
        }

        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(output_path / f"{filename}_statistics.csv", index=False)

    return fig


def plot_confusion_matrix(
    confusion_matrix: pd.DataFrame,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Confusion Matrix",
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = "Blues",
    annot: bool = True,
    fmt: str = 'd',
    normalize: Optional[str] = None,
    show_accuracy: bool = True,
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create an enhanced confusion matrix visualization.

    Parameters:
    -----------
    confusion_matrix : pd.DataFrame
        Confusion matrix with predicted vs actual values
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
        String format for annotations
    normalize : str, optional
        Normalization method ('true', 'pred', 'all')
    show_accuracy : bool
        Whether to show accuracy metrics
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to seaborn.heatmap

    Returns:
    --------
    matplotlib.figure.Figure
        The confusion matrix figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Prepare data
    cm_data = confusion_matrix.copy()

    # Normalize if requested
    if normalize == 'true':
        cm_data = cm_data.div(cm_data.sum(axis=1), axis=0)
        fmt = '.2f'
    elif normalize == 'pred':
        cm_data = cm_data.div(cm_data.sum(axis=0), axis=1)
        fmt = '.2f'
    elif normalize == 'all':
        cm_data = cm_data / cm_data.sum().sum()
        fmt = '.2f'

    # Create figure
    if scientific_style:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
        sns.set_style("white")

        # Modern color palette
        colors = ["#f7fbff", "#08306b"] if cmap == "Blues" else ["#fff5f0", "#67000d"]
        cmap_obj = sns.color_palette(colors, as_cmap=True)
    else:
        fig, ax = plt.subplots(figsize=figsize)
        cmap_obj = cmap

    # Create heatmap
    heatmap = sns.heatmap(
        cm_data,
        annot=annot,
        fmt=fmt,
        cmap=cmap_obj,
        cbar_kws={'label': 'Count' if not normalize else 'Proportion'},
        ax=ax,
        **kwargs
    )

    # Modern styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')

    # Rotate tick labels
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)

    # Calculate and display accuracy metrics
    if show_accuracy:
        # Calculate metrics
        n_classes = len(cm_data)
        true_positives = np.diag(cm_data)
        false_positives = cm_data.sum(axis=0) - true_positives
        false_negatives = cm_data.sum(axis=1) - true_positives
        true_negatives = cm_data.sum().sum() - (true_positives + false_positives + false_negatives)

        # Overall accuracy
        overall_accuracy = true_positives.sum() / cm_data.sum().sum()

        # Precision, Recall, F1-Score for each class
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1_score = 2 * (precision * recall) / (precision + recall)

        # Handle NaN values
        precision = np.nan_to_num(precision, nan=0.0)
        recall = np.nan_to_num(recall, nan=0.0)
        f1_score = np.nan_to_num(f1_score, nan=0.0)

        # Macro averages
        macro_precision = precision.mean()
        macro_recall = recall.mean()
        macro_f1 = f1_score.mean()

        # Create metrics text
        metrics_text = ".3f"".3f"".3f"".3f"".3f"".3f"f"""
Overall Accuracy: {overall_accuracy:.3f}

Macro Average:
Precision: {macro_precision:.3f}
Recall: {macro_recall:.3f}
F1-Score: {macro_f1:.3f}

Per-Class Metrics:
"""

        for i, class_name in enumerate(cm_data.index):
            metrics_text += ".3f"".3f"".3f"".3f"".3f"".3f"f"""
{class_name}:
  Precision: {precision[i]:.3f}
  Recall: {recall[i]:.3f}
  F1-Score: {f1_score[i]:.3f}
"""

        # Add metrics annotation
        ax.text(1.15, 0.5, metrics_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='center',
                fontfamily='monospace',
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
        cm_data.to_csv(output_path / f"{filename}_data.csv")

        # Export detailed metrics if calculated
        if show_accuracy:
            metrics_data = []
            for i, class_name in enumerate(cm_data.index):
                metrics_data.append({
                    'Class': class_name,
                    'Precision': precision[i],
                    'Recall': recall[i],
                    'F1_Score': f1_score[i],
                    'True_Positives': true_positives[i],
                    'False_Positives': false_positives[i],
                    'False_Negatives': false_negatives[i],
                    'True_Negatives': true_negatives[i]
                })

            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_csv(output_path / f"{filename}_metrics.csv", index=False)

    return fig


# Export public functions
__all__ = [
    'plot_transition_matrix_heatmap',
    'plot_confusion_matrix',
]
