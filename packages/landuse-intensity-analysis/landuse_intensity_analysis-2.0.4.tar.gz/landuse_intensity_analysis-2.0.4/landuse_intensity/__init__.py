"""
Modern Land Use Intensity Analysis Package

A clean, object-oriented package for land use change analysis using
the Pontius methodology with modern Python practices.

Key Features:
- Object-oriented design with clear separation of concerns
- ContingencyTable class for transition matrix operations
- IntensityAnalyzer for Pontius intensity analysis
- ChangeAnalyzer for spatial change detection
- Modern Visualizer with matplotlib and plotly support
- Simplified utility functions
- Essential image processing tools
- Streamlined raster data handling

Classes:
- ContingencyTable: Handle transition matrices and basic statistics
- IntensityAnalyzer: Implement Pontius methodology for intensity analysis
- ChangeAnalyzer: Analyze spatial patterns of land use change
- Visualizer: Create modern, publication-ready visualizations

Example:
    >>> from landuse_intensity import ContingencyTable, IntensityAnalyzer, Visualizer
    >>> 
    >>> # Create contingency table
    >>> ct = ContingencyTable.from_rasters(raster_t1, raster_t2)
    >>> 
    >>> # Run intensity analysis
    >>> analyzer = IntensityAnalyzer(ct)
    >>> results = analyzer.analyze()
    >>> 
    >>> # Create visualizations
    >>> viz = Visualizer()
    >>> viz.plot_contingency_matrix(ct.table)
    >>> viz.plot_intensity_analysis(results)
"""

# Core classes
from .core import (
    ContingencyTable,
    IntensityAnalyzer, 
    ChangeAnalyzer,
    MultiStepAnalyzer,
    analyze_land_use_change
)

# Visualization
# from .visualizer import Visualizer  # Commented out - no visualizer.py file

# New modular visualization
from . import graph_visualization
from . import map_visualization

# Utility functions
from .utils import (
    demo_landscape,
    validate_data,
    calculate_area_matrix,
    get_change_summary,
    format_area_label,
    create_transition_names
)

# Image processing
from .image_processing import (
    create_contingency_table,
    calculate_change_map,
    apply_majority_filter,
    calculate_patch_metrics,
    resample_raster,
    align_rasters,
    validate_raster,
    mask_raster
)

# Raster handling
from .raster import (
    read_raster,
    write_raster,
    raster_to_contingency_table,
    load_demo_data,
    raster_summary,
    align_rasters as align_raster_files,
    reclassify_raster
)

# Package metadata
__version__ = "2.0.4"
__author__ = "Land Use Intensity Analysis Development Team"
__email__ = "dev@landuse-intensity.org"
__license__ = "MIT"

# Public API
__all__ = [
    # Core classes
    'ContingencyTable',
    'IntensityAnalyzer',
    'ChangeAnalyzer',
    'MultiStepAnalyzer',
    # 'Visualizer',  # Commented out - no visualizer.py file
    
    # Visualization modules
    'graph_visualization',
    'map_visualization',
    
    # Main analysis function
    'analyze_land_use_change',
    
    # Utility functions
    'demo_landscape',
    'validate_data',
    'calculate_area_matrix',
    'get_change_summary',
    'format_area_label',
    'create_transition_names',
    
    # Image processing
    'create_contingency_table',
    'calculate_change_map',
    'apply_majority_filter',
    'calculate_patch_metrics',
    'resample_raster',
    'align_rasters',
    'validate_raster',
    'mask_raster',
    
    # Raster handling
    'read_raster',
    'write_raster',
    'raster_to_contingency_table',
    'load_demo_data',
    'raster_summary',
    'align_raster_files',
    'reclassify_raster',
]