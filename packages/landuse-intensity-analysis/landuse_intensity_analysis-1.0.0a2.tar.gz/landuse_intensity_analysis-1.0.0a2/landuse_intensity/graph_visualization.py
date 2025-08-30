"""
Main Graph Visualization Module for Land Use and Land Cover (LULC) Change Analysis

This module serves as the main entry point for LULC visualization functionality,
importing specialized functions from focused modules for better maintainability.

Key Features:
- Unified interface to all visualization functions
- Import and re-export specialized visualization modules
- Centralized documentation and examples

Specialized Modules:
- sankey_visualization: Sankey diagrams for land use transitions
- matrix_visualization: Matrix heatmaps and confusion matrices
- bar_chart_visualization: Bar plots and gain/loss analysis
- statistical_visualization: Statistical validation and performance plots
- visualization_utils: Utility functions and helpers

Based on research from:
- Frontiers in Environmental Science LULC prediction methodologies
- ResearchGate geospatial assessment techniques
- Modern Python visualization libraries and best practices
- Scientific publication standards

Usage:
    # Import specific functions from specialized modules
    from landuse_intensity.sankey_visualization import plot_single_step_sankey
    from landuse_intensity.matrix_visualization import plot_transition_matrix_heatmap
    from landuse_intensity.bar_chart_visualization import plot_barplot_lulc

    # This module serves as documentation and module loader only
    # No functions are re-exported to maintain clean separation
"""

import warnings

# Import specialized visualization modules using absolute imports
try:
    import landuse_intensity.sankey_visualization
    import landuse_intensity.matrix_visualization
    import landuse_intensity.bar_chart_visualization
    import landuse_intensity.statistical_visualization
    import landuse_intensity.visualization_utils
except ImportError as e:
    warnings.warn(f"Could not import specialized visualization modules: {e}")
    warnings.warn("Some visualization functions may not be available")

# Note: Functions are not re-exported to maintain clean module separation
# Import directly from specialized modules:
# - from landuse_intensity.sankey_visualization import plot_single_step_sankey
# - from landuse_intensity.matrix_visualization import plot_transition_matrix_heatmap
# - etc.
