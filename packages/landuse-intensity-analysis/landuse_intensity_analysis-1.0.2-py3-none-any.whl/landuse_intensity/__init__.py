"""
LandUse-Intensity-Analysis: Scientific Land Use Change Analysis Based on Pontius Methodology

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

📊 Scientific Visualizations:
  - Publication-ready charts and diagrams
  - Interactive Sankey and chord diagrams
  - Statistical validation plots

�️ Spatial Analysis:
  - Raster data processing and analysis
  - Landscape pattern metrics
  - Change detection algorithms

Core Modules:
  raster: Spatial data loading and processing
  analysis: Statistical analysis and contingency tables
  intensity: Pontius intensity analysis implementation
  visualization: Scientific plotting functions
  utils: Utility functions and data validation
"""

__version__ = "1.0.1"
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
from .visualization import netgross_plot, plot_bar, plot_chord_diagram, plot_sankey

# Advanced features (optional imports)
try:
    from .pontius import (
        AdvancedPontius,
        CategoryLevelResults,
        IntensityLevelResults,
        PontiusMetrics,
        TransitionLevelResults,
    )

    _pontius_available = True
except ImportError:
    _pontius_available = False

try:
    from .modern_viz import ModernVisualizer

    _modern_viz_available = True
except ImportError:
    _modern_viz_available = False

try:
    from .image_processing import (
        AdvancedImageProcessor,
        ChangeDetectionResults,
        ConnectivityMetrics,
        FilterType,
        LandscapeMetrics,
    )

    _image_processing_available = True
except ImportError:
    _image_processing_available = False

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
    "plot_sankey",
    "plot_chord_diagram",
    "plot_bar",
    "netgross_plot",
    # Utility functions
    "demo_landscape",
    "validate_contingency_data",
    "format_area_label",
    "get_transition_matrix",
    "calculate_change_metrics",
    "check_data_consistency",
    "print_summary_stats",
]

# Add optional features to __all__ if available
if _pontius_available:
    __all__.extend(
        [
            "AdvancedPontius",
            "PontiusMetrics",
            "IntensityLevelResults",
            "CategoryLevelResults",
            "TransitionLevelResults",
        ]
    )

if _modern_viz_available:
    __all__.extend(["ModernVisualizer"])

if _image_processing_available:
    __all__.extend(
        [
            "AdvancedImageProcessor",
            "LandscapeMetrics",
            "ConnectivityMetrics",
            "ChangeDetectionResults",
            "FilterType",
        ]
    )
