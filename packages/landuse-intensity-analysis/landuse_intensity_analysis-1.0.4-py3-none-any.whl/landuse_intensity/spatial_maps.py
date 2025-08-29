"""
Spatial mapping module for land use and land cover change analysis.

This module provides functions to generate persistence and transition maps
from raster data, including spatial analysis and visualization capabilities
using geopandas and matplotlib/plotly.

Supported map types:
- Persistence maps (areas that remained the same)
- Transition maps (areas that changed between categories)  
- Spatial transition matrices with geographic context
- Change hotspot analysis
- Spatial statistics and metrics

Dependencies:
- geopandas (spatial operations)
- rasterio (raster I/O)
- matplotlib (static maps)
- plotly (interactive maps) 
- numpy (numerical operations)
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
import rasterio
from rasterio.plot import show
from rasterio.features import shapes
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

# Optional dependencies
HAS_GEOPANDAS = False
HAS_PLOTLY = False
HAS_CONTEXTILY = False

try:
    import geopandas as gpd
    from shapely.geometry import shape
    HAS_GEOPANDAS = True
except ImportError:
    warnings.warn("GeoPandas not available. Spatial analysis features will be limited.")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    warnings.warn("Plotly not available. Interactive maps will not be generated.")

try:
    import contextily as ctx
    HAS_CONTEXTILY = True
except ImportError:
    warnings.warn("Contextily not available. Basemaps will not be added to static maps.")

# Default color schemes for spatial maps
PERSISTENCE_COLORS = {
    0: '#E8E8E8',  # No data / Background
    1: '#2E8B57',  # Forest - Dark green
    2: '#90EE90',  # Grassland - Light green  
    3: '#F4A460',  # Agriculture - Sandy brown
    4: '#DC143C',  # Urban - Crimson
    5: '#4169E1',  # Water - Royal blue
    6: '#D2B48C',  # Barren - Tan
}

CHANGE_COLORS = {
    'no_change': '#CCCCCC',      # Gray for persistence
    'forest_loss': '#FF4500',    # Orange-red for deforestation
    'forest_gain': '#228B22',    # Forest green for reforestation
    'urban_expansion': '#8B0000', # Dark red for urbanization
    'agriculture_expansion': '#DAA520', # Goldenrod for ag expansion
    'water_change': '#4682B4',   # Steel blue for water changes
    'other_change': '#9370DB'    # Medium purple for other changes
}


def _ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _get_raster_bounds(raster_path: Union[str, Path]) -> Tuple[float, float, float, float]:
    """Get bounding box of raster file."""
    with rasterio.open(raster_path) as src:
        return src.bounds


def _create_change_matrix(raster_t1: np.ndarray, raster_t2: np.ndarray) -> np.ndarray:
    """Create change matrix from two raster arrays."""
    # Combine categories to create unique change codes
    # Format: from_class * 100 + to_class (e.g., 1 -> 2 becomes 102)
    change_matrix = raster_t1.astype(np.int32) * 100 + raster_t2.astype(np.int32)
    return change_matrix


def _classify_changes(change_matrix: np.ndarray, class_names: Dict[int, str] = None) -> np.ndarray:
    """Classify changes into meaningful categories."""
    if class_names is None:
        class_names = {1: 'Forest', 2: 'Grassland', 3: 'Agriculture', 4: 'Urban', 5: 'Water', 6: 'Barren'}
    
    # Create classified change map
    classified = np.zeros_like(change_matrix, dtype=np.int32)
    
    # No change (persistence) - same class in both periods
    for class_id in class_names.keys():
        no_change_code = class_id * 100 + class_id
        classified[change_matrix == no_change_code] = 0  # No change
    
    # Forest loss (any forest to non-forest)
    for to_class in class_names.keys():
        if to_class != 1:  # Not forest
            loss_code = 1 * 100 + to_class
            classified[change_matrix == loss_code] = 1  # Forest loss
    
    # Forest gain (any non-forest to forest)
    for from_class in class_names.keys():
        if from_class != 1:  # Not forest
            gain_code = from_class * 100 + 1
            classified[change_matrix == gain_code] = 2  # Forest gain
    
    # Urban expansion (any non-urban to urban)
    for from_class in class_names.keys():
        if from_class != 4:  # Not urban
            urban_code = from_class * 100 + 4
            classified[change_matrix == urban_code] = 3  # Urban expansion
    
    # Agriculture expansion (any non-agriculture to agriculture)
    for from_class in class_names.keys():
        if from_class != 3:  # Not agriculture
            ag_code = from_class * 100 + 3
            classified[change_matrix == ag_code] = 4  # Agriculture expansion
    
    # Water changes
    for from_class in class_names.keys():
        for to_class in class_names.keys():
            if from_class != to_class and (from_class == 5 or to_class == 5):
                water_code = from_class * 100 + to_class
                if classified[change_matrix == water_code].sum() == 0:  # Not already classified
                    classified[change_matrix == water_code] = 5  # Water change
    
    # Other changes
    classified[np.logical_and(change_matrix > 0, classified == 0)] = 6  # Other changes
    
    return classified


def create_persistence_map(
    raster_t1_path: Union[str, Path],
    raster_t2_path: Union[str, Path],
    output_dir: Union[str, Path] = "outputs",
    filename: str = "persistence_map",
    save_png: bool = True,
    save_geotiff: bool = True,
    figsize: Tuple[int, int] = (12, 10),
    dpi: int = 300,
    class_names: Optional[Dict[int, str]] = None,
) -> Dict[str, str]:
    """
    Create persistence map showing areas that remained the same between two time periods.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "persistence_map"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG visualization
    save_geotiff : bool, default True
        Whether to save GeoTIFF of persistence map
    figsize : tuple, default (12, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    class_names : dict, optional
        Mapping of class values to names
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    if class_names is None:
        class_names = {1: 'Forest', 2: 'Grassland', 3: 'Agriculture', 4: 'Urban', 5: 'Water', 6: 'Barren'}
    
    # Read raster data
    with rasterio.open(raster_t1_path) as src1:
        raster_t1 = src1.read(1)
        profile = src1.profile.copy()
        transform = src1.transform
        crs = src1.crs
    
    with rasterio.open(raster_t2_path) as src2:
        raster_t2 = src2.read(1)
    
    # Create persistence map (1 where same, 0 where different)
    persistence = (raster_t1 == raster_t2).astype(np.uint8)
    
    # Create detailed persistence map by class
    persistence_by_class = np.zeros_like(raster_t1, dtype=np.uint8)
    for class_id in class_names.keys():
        mask = (raster_t1 == class_id) & (raster_t2 == class_id)
        persistence_by_class[mask] = class_id
    
    # Save GeoTIFF
    if save_geotiff:
        profile.update(dtype='uint8', count=1, nodata=0)
        
        geotiff_path = output_path / f"{filename}.tif"
        with rasterio.open(geotiff_path, 'w', **profile) as dst:
            dst.write(persistence_by_class, 1)
        
        generated_files['geotiff'] = str(geotiff_path)
        print(f"✅ GeoTIFF saved: {geotiff_path}")
    
    # Create visualization
    if save_png:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Left plot: Binary persistence
        im1 = ax1.imshow(persistence, cmap='RdYlGn', vmin=0, vmax=1)
        ax1.set_title('Areas of Persistence\n(Green = No Change, Red = Change)', 
                     fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        # Add colorbar
        cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.6)
        cbar1.set_ticks([0, 1])
        cbar1.set_ticklabels(['Change', 'Persistence'])
        
        # Right plot: Persistence by class
        colors = [PERSISTENCE_COLORS.get(i, '#CCCCCC') for i in range(max(class_names.keys())+1)]
        cmap = mcolors.ListedColormap(colors)
        
        im2 = ax2.imshow(persistence_by_class, cmap=cmap, vmin=0, vmax=max(class_names.keys()))
        ax2.set_title('Persistent Areas by Land Use Class', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        # Create legend
        patches = [mpatches.Patch(color=PERSISTENCE_COLORS.get(k, '#CCCCCC'), 
                                label=v) for k, v in class_names.items()]
        ax2.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Add overall statistics
        total_pixels = persistence.size
        persistent_pixels = np.sum(persistence)
        persistence_rate = (persistent_pixels / total_pixels) * 100
        
        fig.suptitle(f'Land Use Persistence Analysis\nOverall Persistence Rate: {persistence_rate:.1f}%',
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def create_transition_map(
    raster_t1_path: Union[str, Path],
    raster_t2_path: Union[str, Path], 
    output_dir: Union[str, Path] = "outputs",
    filename: str = "transition_map",
    save_png: bool = True,
    save_geotiff: bool = True,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 300,
    class_names: Optional[Dict[int, str]] = None,
) -> Dict[str, str]:
    """
    Create transition map showing types of land use changes.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "transition_map"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG visualization
    save_geotiff : bool, default True
        Whether to save GeoTIFF of transition map
    figsize : tuple, default (14, 10)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    class_names : dict, optional
        Mapping of class values to names
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    if class_names is None:
        class_names = {1: 'Forest', 2: 'Grassland', 3: 'Agriculture', 4: 'Urban', 5: 'Water', 6: 'Barren'}
    
    # Read raster data
    with rasterio.open(raster_t1_path) as src1:
        raster_t1 = src1.read(1)
        profile = src1.profile.copy()
        transform = src1.transform
        crs = src1.crs
    
    with rasterio.open(raster_t2_path) as src2:
        raster_t2 = src2.read(1)
    
    # Create change matrix
    change_matrix = _create_change_matrix(raster_t1, raster_t2)
    
    # Classify changes
    transition_map = _classify_changes(change_matrix, class_names)
    
    # Save GeoTIFF
    if save_geotiff:
        profile.update(dtype='uint8', count=1, nodata=255)
        
        geotiff_path = output_path / f"{filename}.tif"
        with rasterio.open(geotiff_path, 'w', **profile) as dst:
            dst.write(transition_map, 1)
        
        generated_files['geotiff'] = str(geotiff_path)
        print(f"✅ GeoTIFF saved: {geotiff_path}")
    
    # Create visualization
    if save_png:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Define change categories and colors
        change_categories = {
            0: 'No Change',
            1: 'Forest Loss', 
            2: 'Forest Gain',
            3: 'Urban Expansion',
            4: 'Agriculture Expansion',
            5: 'Water Change',
            6: 'Other Change'
        }
        
        change_color_list = [
            CHANGE_COLORS['no_change'],
            CHANGE_COLORS['forest_loss'],
            CHANGE_COLORS['forest_gain'],
            CHANGE_COLORS['urban_expansion'],
            CHANGE_COLORS['agriculture_expansion'],
            CHANGE_COLORS['water_change'],
            CHANGE_COLORS['other_change']
        ]
        
        cmap = mcolors.ListedColormap(change_color_list)
        
        im = ax.imshow(transition_map, cmap=cmap, vmin=0, vmax=6)
        ax.set_title('Land Use Transition Map', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Create legend
        patches = [mpatches.Patch(color=change_color_list[k], label=v) 
                  for k, v in change_categories.items()]
        ax.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Calculate and display statistics
        total_pixels = transition_map.size
        stats_text = []
        for code, category in change_categories.items():
            count = np.sum(transition_map == code)
            percentage = (count / total_pixels) * 100
            stats_text.append(f"{category}: {percentage:.1f}%")
        
        # Add statistics as text box
        stats_str = '\n'.join(stats_text)
        ax.text(0.02, 0.98, stats_str, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def create_change_hotspots(
    raster_t1_path: Union[str, Path],
    raster_t2_path: Union[str, Path],
    output_dir: Union[str, Path] = "outputs",
    filename: str = "change_hotspots",
    save_png: bool = True,
    window_size: int = 5,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 300,
) -> Dict[str, str]:
    """
    Create change hotspot map using moving window analysis.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "change_hotspots"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG visualization
    window_size : int, default 5
        Size of moving window for hotspot analysis
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
    
    # Read raster data
    with rasterio.open(raster_t1_path) as src1:
        raster_t1 = src1.read(1).astype(np.float32)
        
    with rasterio.open(raster_t2_path) as src2:
        raster_t2 = src2.read(1).astype(np.float32)
    
    # Calculate change (binary: 1 = change, 0 = no change)
    change_binary = (raster_t1 != raster_t2).astype(np.float32)
    
    # Apply moving window to calculate change density
    from scipy import ndimage
    
    kernel = np.ones((window_size, window_size)) / (window_size ** 2)
    change_density = ndimage.convolve(change_binary, kernel, mode='reflect')
    
    # Classify hotspots
    hotspots = np.zeros_like(change_density, dtype=np.uint8)
    hotspots[change_density > 0.7] = 3  # High change
    hotspots[(change_density > 0.3) & (change_density <= 0.7)] = 2  # Medium change
    hotspots[(change_density > 0.1) & (change_density <= 0.3)] = 1  # Low change
    # 0 = No/minimal change
    
    if save_png:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Left plot: Change density
        im1 = ax1.imshow(change_density, cmap='Reds', vmin=0, vmax=1)
        ax1.set_title('Change Density\n(Moving Window Analysis)', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.6)
        cbar1.set_label('Change Density')
        
        # Right plot: Hotspot classification
        hotspot_colors = ['#FFFFFF', '#FFEDA0', '#FEB24C', '#F03B20']  # White to red
        cmap = mcolors.ListedColormap(hotspot_colors)
        
        im2 = ax2.imshow(hotspots, cmap=cmap, vmin=0, vmax=3)
        ax2.set_title('Change Hotspots\n(Classified)', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        # Create legend
        hotspot_labels = ['No Change', 'Low Change', 'Medium Change', 'High Change']
        patches = [mpatches.Patch(color=hotspot_colors[i], label=hotspot_labels[i]) 
                  for i in range(4)]
        ax2.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Calculate statistics
        total_pixels = hotspots.size
        high_change = np.sum(hotspots == 3)
        medium_change = np.sum(hotspots == 2)
        low_change = np.sum(hotspots == 1)
        
        stats = f"Window Size: {window_size}x{window_size}\n"
        stats += f"High Change: {(high_change/total_pixels)*100:.1f}%\n"
        stats += f"Medium Change: {(medium_change/total_pixels)*100:.1f}%\n"
        stats += f"Low Change: {(low_change/total_pixels)*100:.1f}%"
        
        fig.suptitle(f'Land Use Change Hotspot Analysis\n{stats}', 
                    fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def create_spatial_transition_matrix(
    raster_t1_path: Union[str, Path],
    raster_t2_path: Union[str, Path],
    output_dir: Union[str, Path] = "outputs",
    filename: str = "spatial_transition_matrix",
    save_png: bool = True,
    grid_size: Tuple[int, int] = (5, 5),
    figsize: Tuple[int, int] = (15, 12),
    dpi: int = 300,
    class_names: Optional[Dict[int, str]] = None,
) -> Dict[str, str]:
    """
    Create spatial transition matrix showing transitions in different regions.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path, default "outputs"
        Directory to save output files
    filename : str, default "spatial_transition_matrix"
        Base filename for output files
    save_png : bool, default True
        Whether to save PNG visualization
    grid_size : tuple, default (5, 5)
        Number of spatial grid cells (rows, cols) for analysis
    figsize : tuple, default (15, 12)
        Figure size for PNG version
    dpi : int, default 300
        DPI for PNG output
    class_names : dict, optional
        Mapping of class values to names
        
    Returns
    -------
    dict
        Dictionary with paths to generated files
    """
    output_path = _ensure_output_dir(output_dir)
    generated_files = {}
    
    if class_names is None:
        class_names = {1: 'Forest', 2: 'Grassland', 3: 'Agriculture', 4: 'Urban', 5: 'Water', 6: 'Barren'}
    
    # Read raster data
    with rasterio.open(raster_t1_path) as src1:
        raster_t1 = src1.read(1)
        height, width = raster_t1.shape
        
    with rasterio.open(raster_t2_path) as src2:
        raster_t2 = src2.read(1)
    
    # Divide raster into grid cells
    grid_rows, grid_cols = grid_size
    cell_height = height // grid_rows
    cell_width = width // grid_cols
    
    # Calculate transitions for each grid cell
    grid_data = []
    
    for i in range(grid_rows):
        for j in range(grid_cols):
            # Extract cell data
            row_start = i * cell_height
            row_end = min((i + 1) * cell_height, height)
            col_start = j * cell_width
            col_end = min((j + 1) * cell_width, width)
            
            cell_t1 = raster_t1[row_start:row_end, col_start:col_end]
            cell_t2 = raster_t2[row_start:row_end, col_start:col_end]
            
            # Calculate change statistics for this cell
            total_pixels = cell_t1.size
            changed_pixels = np.sum(cell_t1 != cell_t2)
            change_rate = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            
            # Count specific transitions
            forest_loss = np.sum((cell_t1 == 1) & (cell_t2 != 1))
            forest_gain = np.sum((cell_t1 != 1) & (cell_t2 == 1))
            urban_expansion = np.sum((cell_t1 != 4) & (cell_t2 == 4))
            
            grid_data.append({
                'row': i,
                'col': j,
                'change_rate': change_rate,
                'forest_loss': forest_loss,
                'forest_gain': forest_gain,
                'urban_expansion': urban_expansion,
                'total_pixels': total_pixels
            })
    
    grid_df = pd.DataFrame(grid_data)
    
    if save_png:
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        metrics = ['change_rate', 'forest_loss', 'forest_gain', 'urban_expansion']
        titles = ['Overall Change Rate (%)', 'Forest Loss (pixels)', 
                 'Forest Gain (pixels)', 'Urban Expansion (pixels)']
        cmaps = ['Reds', 'Oranges', 'Greens', 'Purples']
        
        for idx, (metric, title, cmap) in enumerate(zip(metrics, titles, cmaps)):
            ax = axes[idx]
            
            # Create grid matrix for visualization
            grid_matrix = np.zeros((grid_rows, grid_cols))
            for _, row in grid_df.iterrows():
                grid_matrix[int(row['row']), int(row['col'])] = row[metric]
            
            im = ax.imshow(grid_matrix, cmap=cmap, aspect='equal')
            ax.set_title(title, fontsize=12, fontweight='bold')
            
            # Add value annotations
            for i in range(grid_rows):
                for j in range(grid_cols):
                    value = grid_matrix[i, j]
                    if metric == 'change_rate':
                        text = f'{value:.1f}%'
                    else:
                        text = f'{int(value)}'
                    ax.text(j, i, text, ha='center', va='center', 
                           fontsize=10, fontweight='bold')
            
            # Remove ticks
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add colorbar
            plt.colorbar(im, ax=ax, shrink=0.6)
        
        plt.suptitle(f'Spatial Transition Matrix Analysis\nGrid Size: {grid_rows}x{grid_cols}',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
    
    return generated_files


def create_all_spatial_maps(
    raster_t1_path: Union[str, Path],
    raster_t2_path: Union[str, Path],
    output_dir: Union[str, Path] = "outputs",
    class_names: Optional[Dict[int, str]] = None,
    save_png: bool = True,
    save_geotiff: bool = True,
    dpi: int = 300,
) -> Dict[str, List[str]]:
    """
    Create all spatial maps in one function call.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path, default "outputs"
        Directory to save output files
    class_names : dict, optional
        Mapping of class values to names
    save_png : bool, default True
        Whether to save PNG versions
    save_geotiff : bool, default True
        Whether to save GeoTIFF versions
    dpi : int, default 300
        DPI for PNG outputs
        
    Returns
    -------
    dict
        Dictionary with lists of generated file paths by map type
    """
    all_files = {
        'persistence': [],
        'transition': [],
        'hotspots': [],
        'spatial_matrix': []
    }
    
    print("🗺️ Generating comprehensive spatial mapping suite...")
    
    # Generate persistence map
    try:
        files = create_persistence_map(
            raster_t1_path, raster_t2_path, output_dir=output_dir,
            save_png=save_png, save_geotiff=save_geotiff, 
            dpi=dpi, class_names=class_names
        )
        all_files['persistence'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Persistence map failed: {e}")
    
    # Generate transition map
    try:
        files = create_transition_map(
            raster_t1_path, raster_t2_path, output_dir=output_dir,
            save_png=save_png, save_geotiff=save_geotiff,
            dpi=dpi, class_names=class_names
        )
        all_files['transition'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Transition map failed: {e}")
    
    # Generate change hotspots
    try:
        files = create_change_hotspots(
            raster_t1_path, raster_t2_path, output_dir=output_dir,
            save_png=save_png, dpi=dpi
        )
        all_files['hotspots'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Change hotspots failed: {e}")
    
    # Generate spatial transition matrix
    try:
        files = create_spatial_transition_matrix(
            raster_t1_path, raster_t2_path, output_dir=output_dir,
            save_png=save_png, dpi=dpi, class_names=class_names
        )
        all_files['spatial_matrix'].extend(files.values())
    except Exception as e:
        print(f"⚠️ Spatial transition matrix failed: {e}")
    
    total_files = sum(len(files) for files in all_files.values())
    print(f"🎉 Generated {total_files} spatial map files in {output_dir}")
    
    return all_files
