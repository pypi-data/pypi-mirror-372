"""
LandUse-Intensity-Analysis: Scientific Land Use Change# Consolidated visualization functions (replaces plots.py, enhanced_visualization.py)
from .visualization import (
    plot_intensity_analysis,
    plot_transition_flow_diagram,  # Corrected from plot_sankey_diagram
    plot_net_gain_loss,
    plot_transition_matrix_heatmap,  # Corrected from plot_chord_diagram
    plot_spatial_change_map,  # New function for geographic maps
    create_summary_plots,
    create_intensity_matrix_plot,
    create_transition_matrix_plot,
    generate_all_visualizations,
    # Legacy compatibility functions
    enhanced_sankey_diagram,
    enhanced_chord_diagram,
)d on Pontius Methodology

A modern Python package for quantitative analysis of land use and cover change (LUCC)
implementing the Pontius-Aldwaik intensity analysis methodology.

Scientific Foundation:
- Pontius Jr, R. G., & Aldwaik, S. Z. (2012). Intensity analysis to unify measurements
  of size and stationarity of land changes. Landscape and Urban Planning, 106(1), 103-114.
- Aldwaik, S. Z., & Pontius Jr, R. G. (2012). Intensity analysis to unify measurements
  of size and stationarity of land changes by interval, category, and transition.

Key Features:
🔬 Pontius Methodology:
  - Complete intensity analysis (interval, category, transition levels)
  - Quantity and allocation disagreement analysis
  - Systematic and random change detection

📊 Consolidated Visualizations:
  - High-quality PNG and interactive HTML outputs
  - Modern Sankey diagrams with matplotlib and plotly
  - Transition matrices and chord diagrams
  - Publication-ready charts with automatic saving

🗺️ Spatial Analysis:
  - Persistence and transition mapping
  - Change hotspot detection
  - Spatial transition matrix analysis
  - GeoTIFF output support

Core Modules:
  raster: Spatial data loading and processing
  analysis: Statistical analysis and contingency tables
  intensity: Pontius intensity analysis implementation
  plots: Unified visualization module (replaces old fragmented modules)
  spatial_maps: Spatial persistence and transition mapping
  utils: Utility functions and data validation
"""

__version__ = "1.0.3a1"
__author__ = "LandUse-Intensity-Analysis Contributors"
__email__ = "landuse.analysis@github.com"

# Core functionality imports
from .analysis import contingency_table, performance_status
from .intensity import IntensityAnalysis, intensity_analysis
from .raster import load_rasters, summary_dir, summary_map

# Import utility functions
from .utils import (
    calculate_change_metrics,
    check_data_consistency,
    demo_landscape,
    format_area_label,
    get_transition_matrix,
    print_summary_stats,
    validate_contingency_data,
)

# Consolidated visualization functions (replaces plots.py, enhanced_visualization.py)
from .visualization import (
    plot_intensity_analysis,
    plot_transition_flow_diagram,  # Corrected from plot_sankey_diagram
    plot_net_gain_loss,
    plot_transition_matrix_heatmap,  # Corrected from plot_chord_diagram
    create_summary_plots,
    create_intensity_matrix_plot,
    create_transition_matrix_plot,
    generate_all_visualizations,
    # Legacy compatibility functions (deprecated)
    # enhanced_sankey_diagram,  # Removed - function no longer exists
    # enhanced_chord_diagram,   # Removed - function no longer exists
)

# Spatial mapping functions
from .spatial_maps import (
    create_persistence_map,
    create_transition_map,
    create_change_hotspots,
    create_spatial_transition_matrix,
    create_all_spatial_maps
)

# Modern API and pipeline system (optional imports with fallbacks)
try:
    from .analyzer import LandUseAnalyzer, AnalysisResults
    _HAS_MODERN_API = True
except ImportError:
    _HAS_MODERN_API = False
    LandUseAnalyzer = None
    AnalysisResults = None

try:
    from .config import AnalysisConfig, load_config, save_config
    _HAS_CONFIG = True
except ImportError:
    _HAS_CONFIG = False
    AnalysisConfig = None
    load_config = None
    save_config = None

try:
    from .cache import CacheManager, MemoryCache, DiskCache
    _HAS_CACHE = True
except ImportError:
    _HAS_CACHE = False
    CacheManager = None
    MemoryCache = None
    DiskCache = None

try:
    from .parallel import ParallelProcessor, create_processor, parallel_map
    _HAS_PARALLEL = True
except ImportError:
    _HAS_PARALLEL = False
    ParallelProcessor = None
    create_processor = None
    parallel_map = None

try:
    from .pipeline import AnalysisPipeline, create_intensity_analysis_pipeline, run_intensity_analysis
    _HAS_PIPELINE = True
except ImportError:
    _HAS_PIPELINE = False
    AnalysisPipeline = None
    create_intensity_analysis_pipeline = None
    run_intensity_analysis = None

# Public API
__all__ = [
    # Core functionality
    "load_rasters",
    "summary_map",
    "summary_dir",
    "contingency_table",
    "intensity_analysis",
    "IntensityAnalysis",
    "performance_status",

    # Consolidated plotting functions
    "plot_intensity_analysis",
    "plot_transition_flow_diagram",  # Corrected from plot_sankey_diagram
    "plot_net_gain_loss",
    "plot_transition_matrix_heatmap",  # Corrected from plot_chord_diagram
    "plot_spatial_change_map",  # New function for geographic maps
    "create_summary_plots",
    "create_intensity_matrix_plot",
    "create_transition_matrix_plot",
    "generate_all_visualizations",
    # Legacy compatibility
    "enhanced_sankey_diagram",
    "enhanced_chord_diagram",

    # Spatial mapping
    "create_persistence_map",
    "create_transition_map",
    "create_change_hotspots",
    "create_spatial_transition_matrix",
    "create_all_spatial_maps",

    # Utility functions
    "demo_landscape",
    "validate_contingency_data",
    "format_area_label",
    "get_transition_matrix",
    "calculate_change_metrics",
    "check_data_consistency",
    "print_summary_stats",
]

# Add modern API components if available
if _HAS_MODERN_API:
    __all__.extend([
        "LandUseAnalyzer",
        "AnalysisResults"
    ])

if _HAS_CONFIG:
    __all__.extend([
        "AnalysisConfig",
        "load_config",
        "save_config"
    ])

if _HAS_CACHE:
    __all__.extend([
        "CacheManager",
        "MemoryCache",
        "DiskCache"
    ])

if _HAS_PARALLEL:
    __all__.extend([
        "ParallelProcessor",
        "create_processor",
        "parallel_map"
    ])

if _HAS_PIPELINE:
    __all__.extend([
        "AnalysisPipeline",
        "create_intensity_analysis_pipeline",
        "run_intensity_analysis"
    ])
