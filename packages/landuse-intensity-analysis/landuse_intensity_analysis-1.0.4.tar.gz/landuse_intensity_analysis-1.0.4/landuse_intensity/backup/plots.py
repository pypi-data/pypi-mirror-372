"""
Unified plotting module for land use and land cover change analysis.

This module consolidates all visualization functions into a single, comprehensive
module that generates both high-quality PNG files (for publications) and 
interactive HTML files (for web viewing).

Supported chart types:
- Intensity analysis bar charts (gain/loss over time)
- Sankey diagrams (flows between categories)
- Chord diagrams (category transitions)
- Net gain/loss bar charts
- Summary visualization panels

Dependencies:
- matplotlib (PNG static charts)
- plotly (HTML interactive charts)
- seaborn (enhanced styling)
- pandas (data handling)

References:
- Pontius Jr, R. G., & Aldwaik, S. Z. (2012). Intensity analysis to unify 
  measurements of size and stationarity of land changes. Landscape and Urban 
  Planning, 106(1), 103-114.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle

# Set matplotlib style for publication-quality plots
plt.style.use('default')
sns.set_palette("husl")

# Optional dependencies
HAS_PLOTLY = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.figure_factory as ff
    HAS_PLOTLY = True
except ImportError:
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


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _get_category_colors(n_categories: int) -> List[str]:
    """Get color palette for categories."""
    if n_categories <= len(CATEGORY_COLORS):
        return CATEGORY_COLORS[:n_categories]
    else:
        # Generate additional colors using seaborn
        return sns.color_palette("husl", n_categories).as_hex()


def _format_title(title: str) -> str:
    """Format title for plots."""
    return title.replace('_', ' ').title()


def plot_intensity_analysis(
    intensity_results: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "intensity_analysis",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 300,
    show_uniform_line: bool = True,
) -> Dict[str, str]:
    """
    Create comprehensive intensity analysis visualization.
    
    Generates both PNG (matplotlib) and HTML (plotly) versions of intensity
    analysis charts showing gain area and intensity percentages by time interval.
    
    Parameters
    ----------
    intensity_results : dict
        Results from intensity_analysis() function containing interval data
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "intensity_analysis"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version using matplotlib
    save_html : bool, default True
        Whether to save HTML version using plotly
    figsize : tuple, default (14, 10)
        Figure size for PNG version (width, height) in inches
    dpi : int, default 300
        DPI for PNG output
    show_uniform_line : bool, default True
        Whether to show uniform intensity reference line
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
        
    Examples
    --------
    >>> import landuse_intensity as lui
    >>> ct = lui.contingency_table('path/to/rasters/', pixel_resolution=30)
    >>> ia = lui.intensity_analysis(ct, category_n=1, category_m=0)
    >>> files = lui.plot_intensity_analysis(ia)
    >>> print(f"PNG saved: {files['png']}")
    >>> print(f"HTML saved: {files['html']}")
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Extract data for plotting
    if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'St'):
        # IntensityAnalysis object
        data = intensity_results.interval_level.St.copy()
    elif isinstance(intensity_results, dict) and 'interval_results' in intensity_results:
        # Dictionary format
        data = intensity_results['interval_results'].copy()
    else:
        raise ValueError("No interval data found in intensity_results. Expected IntensityAnalysis object with interval_level.St or dict with 'interval_results'")
    
    # Ensure required columns exist
    required_cols = ['Period', 'TotalChange', 'St']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}. Available: {list(data.columns)}")
    
    # Generate PNG version with matplotlib
    if save_png:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Left plot: Total Change
        bars1 = ax1.bar(data['Period'], data['TotalChange'], 
                        color=TRANSITION_COLORS['change'], alpha=0.7,
                        edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Total Change (km²)', fontsize=12, fontweight='bold')
        ax1.set_title('Total Change by Time Period', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Right plot: Interval Intensity (St)
        bars2 = ax2.bar(data['Period'], data['St'],
                       color=TRANSITION_COLORS['loss'], alpha=0.7,
                       edgecolor='black', linewidth=0.5)
        ax2.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Interval Intensity (St) (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Interval Intensity by Time Period', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add uniform intensity line (U)
        if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'U'):
            uniform_val = intensity_results.interval_level.U
            ax2.axhline(y=uniform_val, color='red', linestyle='--', linewidth=2,
                       label=f'Uniform Intensity (U): {uniform_val:.3f}%')
            ax2.legend()
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    # Generate HTML version with plotly
    if save_html and HAS_PLOTLY:
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Total Change by Time Period', 'Interval Intensity by Time Period'),
            specs=[[{"secondary_y": False}, {"secondary_y": True}]]
        )
        
        # Left plot: Total Change
        fig.add_trace(
            go.Bar(
                x=data['Period'],
                y=data['TotalChange'],
                name='Total Change (km²)',
                marker_color=TRANSITION_COLORS['change'],
                text=[f'{val:.1f}' for val in data['TotalChange']],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Right plot: Interval Intensity
        fig.add_trace(
            go.Bar(
                x=data['Period'],
                y=data['St'],
                name='Interval Intensity (St) (%)',
                marker_color=TRANSITION_COLORS['loss'],
                text=[f'{val:.3f}%' for val in data['St']],
                textposition='outside'
            ),
            row=1, col=2
        )
        
        # Add uniform intensity line
        if hasattr(intensity_results, 'interval_level') and hasattr(intensity_results.interval_level, 'U'):
            uniform_val = intensity_results.interval_level.U
            fig.add_hline(
                y=uniform_val, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Uniform Intensity (U): {uniform_val:.3f}%",
                col=2
            )
        
        fig.update_layout(
            title_text="Land Use Change Intensity Analysis",
            title_x=0.5,
            showlegend=False,
            height=600,
            font=dict(size=12)
        )
        
        fig.update_xaxes(title_text="Time Period", row=1, col=1)
        fig.update_xaxes(title_text="Time Period", row=1, col=2)
        fig.update_yaxes(title_text="Gain Area (km²)", row=1, col=1)
        fig.update_yaxes(title_text="Intensity Gain (%)", row=1, col=2)
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")
    
    return generated_files


def plot_sankey_diagram(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "sankey_diagram", 
    save_png: bool = True,
    save_html: bool = True,
    min_flow: float = 0.1,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create Sankey diagram showing land use transitions.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "sankey_diagram"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True  
        Whether to save HTML version
    min_flow : float, default 0.1
        Minimum flow size to show (km²)
    figsize : tuple, default (12, 8)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Extract data
    if 'lulc_Multistep' not in contingency_data:
        raise ValueError("No lulc_Multistep data found in contingency_data")
    
    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Filter flows
    multistep = multistep[multistep['km2'] >= min_flow].copy()
    
    if len(multistep) == 0:
        warnings.warn(f"No flows >= {min_flow} km². Adjust min_flow parameter.")
        return generated_files
    
    # Create category mapping
    if not legend.empty and 'CategoryValue' in legend.columns:
        category_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        unique_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        category_map = {cat: f"Class_{cat}" for cat in unique_cats}
    
    # Generate HTML version with plotly (better for Sankey)
    if save_html and HAS_PLOTLY:
        # Prepare data for plotly sankey
        unique_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        
        # Create source and target indices
        cat_to_idx = {cat: i for i, cat in enumerate(unique_cats)}
        
        source = [cat_to_idx[row['From']] for _, row in multistep.iterrows()]
        target = [cat_to_idx[row['To']] for _, row in multistep.iterrows()]
        values = multistep['km2'].tolist()
        
        # Create labels
        labels = [category_map.get(cat, f"Class_{cat}") for cat in unique_cats]
        colors = _get_category_colors(len(unique_cats))
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=colors
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                color=[f'rgba({int(colors[s][1:3], 16)}, {int(colors[s][3:5], 16)}, {int(colors[s][5:7], 16)}, 0.4)' for s in source]
            )
        )])
        
        fig.update_layout(
            title_text="Land Use Change Flows (Sankey Diagram)",
            title_x=0.5,
            font_size=12,
            height=600
        )
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")
    
    # Generate PNG version with matplotlib (simplified representation)
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create a simplified flow diagram using rectangles and arrows
        unique_from = sorted(multistep['From'].unique())
        unique_to = sorted(multistep['To'].unique())
        
        # Position categories
        y_from = np.linspace(0.8, 0.2, len(unique_from))
        y_to = np.linspace(0.8, 0.2, len(unique_to))
        
        from_pos = dict(zip(unique_from, y_from))
        to_pos = dict(zip(unique_to, y_to))
        
        # Draw rectangles for categories
        for cat, y in from_pos.items():
            rect = Rectangle((0.1, y-0.03), 0.2, 0.06, 
                           facecolor=_get_category_colors(len(unique_from))[list(unique_from).index(cat)],
                           alpha=0.7, edgecolor='black')
            ax.add_patch(rect)
            ax.text(0.2, y, category_map.get(cat, f"Class_{cat}"), 
                   ha='center', va='center', fontweight='bold')
        
        for cat, y in to_pos.items():
            rect = Rectangle((0.7, y-0.03), 0.2, 0.06,
                           facecolor=_get_category_colors(len(unique_to))[list(unique_to).index(cat)],
                           alpha=0.7, edgecolor='black')
            ax.add_patch(rect)
            ax.text(0.8, y, category_map.get(cat, f"Class_{cat}"),
                   ha='center', va='center', fontweight='bold')
        
        # Draw flows
        max_flow = multistep['km2'].max()
        for _, row in multistep.iterrows():
            y1 = from_pos[row['From']]
            y2 = to_pos[row['To']]
            width = (row['km2'] / max_flow) * 0.01  # Scale line width
            
            ax.arrow(0.3, y1, 0.35, y2-y1, head_width=0.02, head_length=0.03,
                    fc='gray', ec='gray', alpha=0.6, linewidth=width*100)
            
            # Add flow label
            mid_x, mid_y = 0.5, (y1 + y2) / 2
            ax.text(mid_x, mid_y, f'{row["km2"]:.1f}', ha='center', va='center',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('Land Use Change Flows (km²)', fontsize=14, fontweight='bold')
        ax.text(0.2, 0.95, 'From', ha='center', fontsize=12, fontweight='bold')
        ax.text(0.8, 0.95, 'To', ha='center', fontsize=12, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def plot_net_gain_loss(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs", 
    filename: str = "net_gain_loss",
    save_png: bool = True,
    save_html: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create net gain/loss bar chart by category.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "net_gain_loss"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    figsize : tuple, default (12, 8)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Extract and process data
    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Calculate gains and losses by category
    gains = multistep.groupby('To')['km2'].sum().rename('Gain')
    losses = multistep.groupby('From')['km2'].sum().rename('Loss')
    
    # Combine and calculate net change
    net_data = pd.DataFrame({'Gain': gains, 'Loss': losses}).fillna(0)
    net_data['Net_Change'] = net_data['Gain'] - net_data['Loss']
    net_data['Gross_Change'] = net_data['Gain'] + net_data['Loss']
    
    # Add category names
    if not legend.empty and 'CategoryValue' in legend.columns:
        category_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
        net_data['Category_Name'] = [category_map.get(idx, f"Class_{idx}") for idx in net_data.index]
    else:
        net_data['Category_Name'] = [f"Class_{idx}" for idx in net_data.index]
    
    # Sort by net change
    net_data = net_data.sort_values('Net_Change')
    
    # Generate PNG version with matplotlib
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create stacked bars
        categories = net_data['Category_Name']
        x_pos = np.arange(len(categories))
        
        # Plot gross changes (background)
        bars_gross = ax.bar(x_pos, net_data['Gross_Change'], 
                          color='lightgray', alpha=0.7, label='Gross Change')
        
        # Plot net gains (positive)
        gains_mask = net_data['Net_Change'] > 0
        if gains_mask.any():
            bars_gain = ax.bar(x_pos[gains_mask], net_data.loc[gains_mask, 'Net_Change'],
                             color=TRANSITION_COLORS['gain'], alpha=0.8, label='Net Gain')
        
        # Plot net losses (negative)
        losses_mask = net_data['Net_Change'] < 0
        if losses_mask.any():
            bars_loss = ax.bar(x_pos[losses_mask], net_data.loc[losses_mask, 'Net_Change'],
                             color=TRANSITION_COLORS['loss'], alpha=0.8, label='Net Loss')
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Land Use Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Area (km²)', fontsize=12, fontweight='bold')
        ax.set_title('Net Gain/Loss by Land Use Category', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    # Generate HTML version with plotly
    if save_html and HAS_PLOTLY:
        fig = go.Figure()
        
        # Add gross change bars
        fig.add_trace(go.Bar(
            x=net_data['Category_Name'],
            y=net_data['Gross_Change'],
            name='Gross Change',
            marker_color='lightgray',
            opacity=0.7
        ))
        
        # Add net change bars
        colors = [TRANSITION_COLORS['gain'] if val > 0 else TRANSITION_COLORS['loss'] 
                 for val in net_data['Net_Change']]
        
        fig.add_trace(go.Bar(
            x=net_data['Category_Name'],
            y=net_data['Net_Change'],
            name='Net Change',
            marker_color=colors,
            text=[f'{val:.1f}' for val in net_data['Net_Change']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Net Gain/Loss by Land Use Category',
            title_x=0.5,
            xaxis_title='Land Use Category',
            yaxis_title='Area (km²)',
            barmode='overlay',
            height=600,
            font=dict(size=12)
        )
        
        fig.add_hline(y=0, line_color="black", line_width=1)
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")
    
    return generated_files


def plot_chord_diagram(
    contingency_data: Dict,
    output_dir: Union[str, Path] = "outputs",
    filename: str = "chord_diagram",
    save_png: bool = True,
    save_html: bool = True,
    min_flow: float = 1.0,
    figsize: Tuple[int, int] = (10, 10),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create chord diagram showing land use transitions.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "chord_diagram"
        Base filename for output files  
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    min_flow : float, default 1.0
        Minimum flow size to show (km²)
    figsize : tuple, default (10, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    # Extract data
    multistep = contingency_data['lulc_Multistep'].copy()
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Filter flows
    multistep = multistep[multistep['km2'] >= min_flow].copy()
    
    if len(multistep) == 0:
        warnings.warn(f"No flows >= {min_flow} km². Adjust min_flow parameter.")
        return generated_files
    
    # Create category mapping
    if not legend.empty and 'CategoryValue' in legend.columns:
        category_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
    else:
        unique_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        category_map = {cat: f"Class_{cat}" for cat in unique_cats}
    
    # Generate HTML version with plotly (simplified chord)
    if save_html and HAS_PLOTLY:
        # Create transition matrix
        unique_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        matrix = np.zeros((len(unique_cats), len(unique_cats)))
        
        cat_to_idx = {cat: i for i, cat in enumerate(unique_cats)}
        
        for _, row in multistep.iterrows():
            i = cat_to_idx[row['From']]
            j = cat_to_idx[row['To']]
            matrix[i, j] = row['km2']
        
        # Create labels
        labels = [category_map.get(cat, f"Class_{cat}") for cat in unique_cats]
        
        # Create heatmap as chord alternative
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale='Viridis',
            text=matrix.round(1),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Land Use Transition Matrix (km²)',
            title_x=0.5,
            xaxis_title='To Category',
            yaxis_title='From Category',
            height=600,
            font=dict(size=12)
        )
        
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        generated_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")
    
    # Generate PNG version with matplotlib (circular layout)
    if save_png:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
        
        unique_cats = sorted(set(multistep['From'].unique()) | set(multistep['To'].unique()))
        n_cats = len(unique_cats)
        
        # Create circular positions
        angles = np.linspace(0, 2*np.pi, n_cats, endpoint=False)
        cat_angles = dict(zip(unique_cats, angles))
        
        # Plot categories as circles
        colors = _get_category_colors(n_cats)
        for i, (cat, angle) in enumerate(cat_angles.items()):
            ax.scatter(angle, 1, s=1000, c=colors[i], alpha=0.7, edgecolors='black')
            ax.text(angle, 1.1, category_map.get(cat, f"Class_{cat}"), 
                   ha='center', va='center', fontweight='bold')
        
        # Draw connections
        max_flow = multistep['km2'].max()
        for _, row in multistep.iterrows():
            if row['From'] != row['To']:  # Skip self-transitions
                angle1 = cat_angles[row['From']]
                angle2 = cat_angles[row['To']]
                
                # Draw curved line
                angles_line = np.linspace(angle1, angle2, 50)
                radii = np.ones_like(angles_line) * 0.8
                
                width = (row['km2'] / max_flow) * 5
                ax.plot(angles_line, radii, linewidth=width, alpha=0.6, color='gray')
        
        ax.set_ylim(0, 1.3)
        ax.set_rticks([])  # Remove radial ticks
        ax.set_title('Land Use Transitions (Chord Diagram)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(False)
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def create_summary_plots(
    contingency_data: Dict,
    intensity_results: Optional[Dict] = None,
    output_dir: Union[str, Path] = "outputs",
    save_png: bool = True,
    save_html: bool = True,
    dpi: int = 300,
) -> Dict[str, List[str]]:
    """
    Create all visualization plots in one function call.
    
    Parameters
    ----------
    contingency_data : dict
        Results from contingency_table() function
    intensity_results : dict, optional
        Results from intensity_analysis() function
    output_dir : str or Path, default "outputs"
        Directory to save output files
    save_png : bool, default True
        Whether to save PNG versions
    save_html : bool, default True
        Whether to save HTML versions
    dpi : int, default 300
        DPI for PNG outputs
        
    Returns
    -------
    dict
        Dictionary with lists of generated file paths by plot type
    """
    all_files = {
        'sankey': [],
        'chord': [],
        'net_gain_loss': [],
        'intensity': []
    }
    
    print("🎨 Generating comprehensive visualization suite...")
    
    # Generate Sankey diagram
    try:
        files = plot_sankey_diagram(
            contingency_data, output_dir=output_dir,
            save_png=save_png, save_html=save_html, dpi=dpi
        )
        all_files['sankey'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Sankey diagram failed: {e}")
    
    # Generate chord diagram
    try:
        files = plot_chord_diagram(
            contingency_data, output_dir=output_dir,
            save_png=save_png, save_html=save_html, dpi=dpi
        )
        all_files['chord'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Chord diagram failed: {e}")
    
    # Generate net gain/loss chart
    try:
        files = plot_net_gain_loss(
            contingency_data, output_dir=output_dir,
            save_png=save_png, save_html=save_html, dpi=dpi
        )
        all_files['net_gain_loss'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Net gain/loss chart failed: {e}")
    
    # Generate intensity analysis if data available
    if intensity_results:
        try:
            files = plot_intensity_analysis(
                intensity_results, output_dir=output_dir,
                save_png=save_png, save_html=save_html, dpi=dpi
            )
            all_files['intensity'].extend(files.values())
        except Exception as e:
            print(f"⚠️ Intensity analysis chart failed: {e}")
    
    total_files = sum(len(files) for files in all_files.values())
    print(f"🎉 Generated {total_files} visualization files in {output_dir}")
    
    return all_files
