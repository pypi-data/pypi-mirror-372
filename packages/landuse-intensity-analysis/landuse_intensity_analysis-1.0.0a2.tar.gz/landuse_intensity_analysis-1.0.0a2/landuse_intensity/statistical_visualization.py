"""
Statistical Visualization and Validation Module

This module provides specialized statistical visualizations for land use and land cover
analysis, including validation plots, accuracy assessment, and statistical analysis
with modern design and comprehensive annotations.

Key Features:
- Statistical validation plots (ROC curves, precision-recall)
- Accuracy assessment visualizations
- Statistical distribution plots
- Model performance metrics visualization
- Modern, publication-ready statistical plots
- Multiple export formats (PNG, SVG, PDF)

Based on research from:
- Frontiers in Environmental Science statistical validation methods
- ResearchGate geospatial accuracy assessment techniques
- Modern Python statistical visualization libraries
- Scientific publication standards for statistical plots

Functions:
- plot_roc_curve(): ROC curve for binary classification
- plot_precision_recall(): Precision-recall curve
- plot_confusion_matrix_stats(): Enhanced confusion matrix with statistics
- plot_accuracy_trends(): Accuracy trends over time/iterations
- plot_statistical_distribution(): Distribution plots for LULC data
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

# Try to import sklearn metrics, but handle gracefully if not available
try:
    from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. Some statistical functions will be limited.")

# Set matplotlib style for publication-quality plots
plt.style.use('default')
sns.set_palette("husl")


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def plot_roc_curve(
    y_true: Union[List, np.ndarray],
    y_scores: Union[List, np.ndarray],
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "ROC Curve",
    figsize: Tuple[int, int] = (10, 8),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create a ROC curve for binary classification evaluation.

    Parameters:
    -----------
    y_true : array-like
        True binary labels
    y_scores : array-like
        Target scores (probabilities or confidence values)
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The ROC curve figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    # Calculate ROC curve
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    # Create figure
    if scientific_style:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig, ax = plt.subplots(figsize=figsize)

    # Plot ROC curve
    ax.plot(fpr, tpr, color='#2E8B57', linewidth=2, label=f'AUC = {roc_auc:.3f}')
    # Plot diagonal line (random classifier)
    ax.plot([0, 1], [0, 1], color='red', linestyle='--', linewidth=1,
            label='Random Classifier (AUC = 0.500)')

    # Styling
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add statistical annotations
    stats_text = ".3f"".3f"".3f"f"""
ROC Statistics:

AUC: {roc_auc:.3f}
Optimal Threshold: {thresholds[np.argmax(tpr - fpr)]:.3f}

At Optimal Threshold:
TPR: {tpr[np.argmax(tpr - fpr)]:.3f}
FPR: {fpr[np.argmax(tpr - fpr)]:.3f}

Total Samples: {len(y_true)}
Positive Class: {np.sum(y_true)}
Negative Class: {len(y_true) - np.sum(y_true)}
"""

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
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

        # Export ROC data
        roc_data = pd.DataFrame({
            'False_Positive_Rate': fpr,
            'True_Positive_Rate': tpr,
            'Thresholds': thresholds
        })
        roc_data.to_csv(output_path / f"{filename}_data.csv", index=False)

        # Export statistics
        stats = {
            'AUC': roc_auc,
            'Optimal_Threshold': thresholds[np.argmax(tpr - fpr)],
            'Optimal_TPR': tpr[np.argmax(tpr - fpr)],
            'Optimal_FPR': fpr[np.argmax(tpr - fpr)],
            'Total_Samples': len(y_true),
            'Positive_Class_Count': int(np.sum(y_true)),
            'Negative_Class_Count': len(y_true) - int(np.sum(y_true))
        }

        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(output_path / f"{filename}_statistics.csv", index=False)

    return fig


def plot_precision_recall(
    y_true: Union[List, np.ndarray],
    y_scores: Union[List, np.ndarray],
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Precision-Recall Curve",
    figsize: Tuple[int, int] = (10, 8),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create a precision-recall curve for binary classification evaluation.

    Parameters:
    -----------
    y_true : array-like
        True binary labels
    y_scores : array-like
        Target scores (probabilities or confidence values)
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The precision-recall curve figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    # Calculate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
    pr_auc = auc(recall, precision)

    # Calculate baseline (random classifier)
    baseline = np.sum(y_true) / len(y_true)

    # Create figure
    if scientific_style:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig, ax = plt.subplots(figsize=figsize)

    # Plot precision-recall curve
    ax.plot(recall, precision, color='#4169E1', linewidth=2, label=f'PR AUC = {pr_auc:.3f}')
    # Plot baseline
    ax.axhline(y=baseline, color='red', linestyle='--', linewidth=1,
               label=f'Baseline = {baseline:.3f}')
    # Styling
    ax.set_xlabel('Recall (Sensitivity)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision (Positive Predictive Value)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower left", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add statistical annotations
    stats_text = ".3f"".3f"".3f"f"""
PR Statistics:

AUC: {pr_auc:.3f}
Baseline: {baseline:.3f}

Optimal Threshold: {thresholds[np.argmax(precision * recall)]:.3f}

At Optimal Threshold:
Precision: {precision[np.argmax(precision * recall)]:.3f}
Recall: {recall[np.argmax(precision * recall)]:.3f}
F1-Score: {2 * precision[np.argmax(precision * recall)] * recall[np.argmax(precision * recall)] / (precision[np.argmax(precision * recall)] + recall[np.argmax(precision * recall)]):.3f}

Total Samples: {len(y_true)}
Positive Class: {np.sum(y_true)}
Negative Class: {len(y_true) - np.sum(y_true)}
"""

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
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

        # Export PR data
        pr_data = pd.DataFrame({
            'Recall': recall,
            'Precision': precision,
            'Thresholds': np.concatenate([thresholds, [1.0]])
        })
        pr_data.to_csv(output_path / f"{filename}_data.csv", index=False)

        # Export statistics
        stats = {
            'PR_AUC': pr_auc,
            'Baseline': baseline,
            'Optimal_Threshold': thresholds[np.argmax(precision * recall)],
            'Optimal_Precision': precision[np.argmax(precision * recall)],
            'Optimal_Recall': recall[np.argmax(precision * recall)],
            'Optimal_F1': 2 * precision[np.argmax(precision * recall)] * recall[np.argmax(precision * recall)] / (precision[np.argmax(precision * recall)] + recall[np.argmax(precision * recall)]),
            'Total_Samples': len(y_true),
            'Positive_Class_Count': int(np.sum(y_true)),
            'Negative_Class_Count': len(y_true) - int(np.sum(y_true))
        }

        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(output_path / f"{filename}_statistics.csv", index=False)

    return fig


def plot_confusion_matrix_stats(
    y_true: Union[List, np.ndarray],
    y_pred: Union[List, np.ndarray],
    class_names: Optional[List[str]] = None,
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Confusion Matrix with Statistics",
    figsize: Tuple[int, int] = (12, 10),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create an enhanced confusion matrix with statistical annotations.

    Parameters:
    -----------
    y_true : array-like
        True labels
    y_pred : array-like
        Predicted labels
    class_names : list, optional
        Names of the classes
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The confusion matrix figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Generate class names if not provided
    if class_names is None:
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        class_names = [f'Class {i}' for i in unique_classes]

    # Calculate statistics
    n_classes = len(class_names)
    stats = {}

    # Per-class metrics
    for i in range(n_classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - (tp + fp + fn)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        stats[class_names[i]] = {
            'Precision': precision,
            'Recall': recall,
            'F1_Score': f1,
            'Support': cm[i, :].sum()
        }

    # Overall metrics
    overall_accuracy = np.trace(cm) / cm.sum()
    macro_precision = np.mean([stats[cls]['Precision'] for cls in class_names])
    macro_recall = np.mean([stats[cls]['Recall'] for cls in class_names])
    macro_f1 = np.mean([stats[cls]['F1_Score'] for cls in class_names])

    # Create figure with subplots
    if scientific_style:
        fig = plt.figure(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig = plt.figure(figsize=figsize)

    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Confusion Matrix Heatmap
    ax1 = fig.add_subplot(gs[0, 0])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                ax=ax1, cbar=True)
    ax1.set_xlabel('Predicted Label', fontsize=10, fontweight='bold')
    ax1.set_ylabel('True Label', fontsize=10, fontweight='bold')
    ax1.set_title('Confusion Matrix', fontsize=12, fontweight='bold')

    # 2. Normalized Confusion Matrix
    ax2 = fig.add_subplot(gs[0, 1])
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Oranges',
                xticklabels=class_names, yticklabels=class_names,
                ax=ax2, cbar=True)
    ax2.set_xlabel('Predicted Label', fontsize=10, fontweight='bold')
    ax2.set_ylabel('True Label', fontsize=10, fontweight='bold')
    ax2.set_title('Normalized Confusion Matrix', fontsize=12, fontweight='bold')

    # 3. Per-class metrics
    ax3 = fig.add_subplot(gs[1, :])

    metrics_df = pd.DataFrame(stats).T
    x = np.arange(len(class_names))
    width = 0.25

    bars1 = ax3.bar(x - width, metrics_df['Precision'], width,
                   label='Precision', color='#2E8B57', alpha=0.8)
    bars2 = ax3.bar(x, metrics_df['Recall'], width,
                   label='Recall', color='#4169E1', alpha=0.8)
    bars3 = ax3.bar(x + width, metrics_df['F1_Score'], width,
                   label='F1-Score', color='#DC143C', alpha=0.8)

    ax3.set_xlabel('Class', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Score', fontsize=10, fontweight='bold')
    ax3.set_title('Per-Class Performance Metrics', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(class_names, rotation=45, ha='right')
    ax3.legend()
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)

    # Main title and overall statistics
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Add overall statistics as text
    overall_text = ".3f"".3f"".3f"".3f"f"""
Overall Statistics:

Accuracy: {overall_accuracy:.3f}
Macro Precision: {macro_precision:.3f}
Macro Recall: {macro_recall:.3f}
Macro F1-Score: {macro_f1:.3f}

Total Samples: {cm.sum()}
Classes: {n_classes}

Best Performing Class:
{metrics_df['F1_Score'].idxmax()} (F1: {metrics_df['F1_Score'].max():.3f})

Worst Performing Class:
{metrics_df['F1_Score'].idxmin()} (F1: {metrics_df['F1_Score'].min():.3f})
"""

    # Position text in the center bottom
    fig.text(0.5, 0.02, overall_text,
             ha='center', va='bottom',
             fontsize=10,
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

        # Export confusion matrix
        cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
        cm_df.to_csv(output_path / f"{filename}_confusion_matrix.csv")

        # Export metrics
        metrics_df.to_csv(output_path / f"{filename}_metrics.csv")

        # Export overall statistics
        overall_stats = {
            'Overall_Accuracy': overall_accuracy,
            'Macro_Precision': macro_precision,
            'Macro_Recall': macro_recall,
            'Macro_F1': macro_f1,
            'Total_Samples': int(cm.sum()),
            'Number_of_Classes': n_classes,
            'Best_Class': metrics_df['F1_Score'].idxmax(),
            'Best_F1_Score': metrics_df['F1_Score'].max(),
            'Worst_Class': metrics_df['F1_Score'].idxmin(),
            'Worst_F1_Score': metrics_df['F1_Score'].min()
        }

        overall_df = pd.DataFrame([overall_stats])
        overall_df.to_csv(output_path / f"{filename}_overall_stats.csv", index=False)

    return fig


def plot_accuracy_trends(
    accuracy_history: Dict[str, List[float]],
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Accuracy Trends Over Time",
    figsize: Tuple[int, int] = (12, 8),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create accuracy trends visualization over time or iterations.

    Parameters:
    -----------
    accuracy_history : dict
        Dictionary with metric names as keys and lists of values as values
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The accuracy trends figure
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

    # Colors for different metrics
    colors = ['#2E8B57', '#4169E1', '#DC143C', '#FFD700', '#8A2BE2', '#FF6347']

    # 1. Main accuracy trend
    ax1 = axes[0]
    if 'accuracy' in accuracy_history:
        x = range(1, len(accuracy_history['accuracy']) + 1)
        ax1.plot(x, accuracy_history['accuracy'], color=colors[0],
                linewidth=2, marker='o', markersize=4, label='Accuracy')
        ax1.set_xlabel('Iteration/Epoch', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Accuracy', fontsize=10, fontweight='bold')
        ax1.set_title('Accuracy Trend', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

    # 2. Loss trend
    ax2 = axes[1]
    if 'loss' in accuracy_history:
        x = range(1, len(accuracy_history['loss']) + 1)
        ax2.plot(x, accuracy_history['loss'], color=colors[1],
                linewidth=2, marker='s', markersize=4, label='Loss')
        ax2.set_xlabel('Iteration/Epoch', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Loss', fontsize=10, fontweight='bold')
        ax2.set_title('Loss Trend', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

    # 3. Precision and Recall trends
    ax3 = axes[2]
    x = range(1, len(next(iter(accuracy_history.values()))) + 1)

    plot_count = 0
    for i, (metric, values) in enumerate(accuracy_history.items()):
        if metric in ['precision', 'recall', 'f1_score']:
            ax3.plot(x, values, color=colors[plot_count % len(colors)],
                    linewidth=2, marker='^', markersize=4, label=metric.title())
            plot_count += 1

    if plot_count > 0:
        ax3.set_xlabel('Iteration/Epoch', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Score', fontsize=10, fontweight='bold')
        ax3.set_title('Precision/Recall Trends', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

    # 4. Summary statistics
    ax4 = axes[3]

    # Calculate final values and improvements
    summary_text = "Performance Summary:\n\n"
    for metric, values in accuracy_history.items():
        if values:
            final_value = values[-1]
            initial_value = values[0]
            improvement = final_value - initial_value

            summary_text += ".3f"".3f"".3f"".3f"f"""
{metric.title()}:
  Final: {final_value:.3f}
  Initial: {initial_value:.3f}
  Change: {improvement:+.3f}
  Best: {max(values):.3f}

"""

    ax4.text(0.05, 0.95, summary_text,
             transform=ax4.transAxes,
             fontsize=10,
             verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='white',
                      alpha=0.9,
                      edgecolor='gray'))

    ax4.set_title('Performance Summary', fontsize=12, fontweight='bold')
    ax4.axis('off')

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

        # Export accuracy history
        max_length = max(len(values) for values in accuracy_history.values())
        history_df = pd.DataFrame({
            metric: values + [None] * (max_length - len(values))
            for metric, values in accuracy_history.items()
        })
        history_df['Iteration'] = range(1, max_length + 1)
        history_df.to_csv(output_path / f"{filename}_history.csv", index=False)

        # Export final statistics
        final_stats = {}
        for metric, values in accuracy_history.items():
            if values:
                final_stats[f'{metric}_final'] = values[-1]
                final_stats[f'{metric}_initial'] = values[0]
                final_stats[f'{metric}_improvement'] = values[-1] - values[0]
                final_stats[f'{metric}_best'] = max(values)
                final_stats[f'{metric}_mean'] = np.mean(values)
                final_stats[f'{metric}_std'] = np.std(values)

        stats_df = pd.DataFrame([final_stats])
        stats_df.to_csv(output_path / f"{filename}_statistics.csv", index=False)

    return fig


def plot_statistical_distribution(
    data: Union[pd.DataFrame, pd.Series, Dict],
    filename: Optional[str] = None,
    output_dir: str = "outputs",
    title: str = "Statistical Distribution Analysis",
    figsize: Tuple[int, int] = (14, 10),
    scientific_style: bool = True,
    **kwargs
) -> plt.Figure:
    """
    Create statistical distribution plots for LULC data analysis.

    Parameters:
    -----------
    data : pd.DataFrame, pd.Series, or dict
        Data to analyze statistically
    filename : str, optional
        Output filename (without extension)
    output_dir : str
        Output directory path
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    scientific_style : bool
        Whether to use scientific publication styling
    **kwargs
        Additional arguments passed to matplotlib

    Returns:
    --------
    matplotlib.figure.Figure
        The statistical distribution figure
    """
    # Ensure output directory exists
    output_path = _ensure_output_dir(output_dir)

    # Prepare data
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.Series):
        df = data.to_frame()
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Data must be DataFrame, Series, or dict")

    # Create figure with subplots
    if scientific_style:
        fig = plt.figure(figsize=figsize, dpi=150)
        sns.set_style("whitegrid")
    else:
        fig = plt.figure(figsize=figsize)

    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3)

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found in data")

    # 1. Histograms for each numeric column
    for i, col in enumerate(numeric_cols[:6]):  # Show up to 6 columns
        row = i // 3
        col_pos = i % 3

        if row < 3 and col_pos < 3:
            ax = fig.add_subplot(gs[row, col_pos])
            sns.histplot(data=df, x=col, ax=ax, kde=True, color='#2E8B57', alpha=0.7)
            ax.set_title(f'{col} Distribution', fontsize=10, fontweight='bold')
            ax.set_xlabel(col, fontsize=8)
            ax.set_ylabel('Frequency', fontsize=8)
            ax.tick_params(axis='both', labelsize=7)

    # 2. Box plots for comparison
    if len(numeric_cols) > 1:
        ax_box = fig.add_subplot(gs[2, :])
        melted_df = df[numeric_cols].melt(var_name='Variable', value_name='Value')
        sns.boxplot(data=melted_df, x='Variable', y='Value', ax=ax_box,
                   palette='Set2', showfliers=True)
        ax_box.set_title('Box Plot Comparison', fontsize=12, fontweight='bold')
        ax_box.set_xlabel('Variables', fontsize=10, fontweight='bold')
        ax_box.set_ylabel('Values', fontsize=10, fontweight='bold')
        ax_box.tick_params(axis='x', rotation=45, labelsize=8)

    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Add statistical summary
    stats_summary = "Statistical Summary:\n\n"
    for col in numeric_cols:
        values = df[col].dropna()
        if len(values) > 0:
            stats_summary += ".3f"".3f"".3f"".3f"".3f"".3f"f"""
{col}:
  Mean: {values.mean():.3f}
  Std: {values.std():.3f}
  Min: {values.min():.3f}
  Max: {values.max():.3f}
  Median: {values.median():.3f}
  Skew: {values.skew():.3f}

"""

    # Position summary text
    fig.text(0.02, 0.02, stats_summary,
             fontsize=8,
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

        # Export statistical summary
        stats_data = {}
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 0:
                stats_data[col] = {
                    'Count': len(values),
                    'Mean': values.mean(),
                    'Std': values.std(),
                    'Min': values.min(),
                    'Max': values.max(),
                    'Median': values.median(),
                    'Skewness': values.skew(),
                    'Kurtosis': values.kurtosis()
                }

        stats_df = pd.DataFrame(stats_data).T
        stats_df.to_csv(output_path / f"{filename}_statistics.csv")

        # Export raw data
        df.to_csv(output_path / f"{filename}_data.csv", index=False)

    return fig


# Export public functions
__all__ = [
    'plot_roc_curve',
    'plot_precision_recall',
    'plot_confusion_matrix_stats',
    'plot_accuracy_trends',
]
