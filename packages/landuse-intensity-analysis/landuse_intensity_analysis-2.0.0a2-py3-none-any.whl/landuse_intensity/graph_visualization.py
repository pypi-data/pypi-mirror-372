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
# Graph visualization module is available for direct function imports
# Import visualization functions directly from this module or use core ContingencyTable

import warnings

# Basic imports for essential functionality
import matplotlib.pyplot as plt
import numpy as np

# Note: This module provides the structure for graph visualizations
# All functionality is now integrated into the core ContingencyTable class
# - from landuse_intensity.matrix_visualization import plot_transition_matrix_heatmap
# - etc.
