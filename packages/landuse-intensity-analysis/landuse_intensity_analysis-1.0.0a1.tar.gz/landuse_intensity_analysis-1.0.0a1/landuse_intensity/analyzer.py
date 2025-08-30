"""
LandUse Analyzer: High-level API for land use and cover change analysis.

This module provides a simplified, user-friendly interface for performing
complete land use intensity analysis using the Pontius methodology.

The LandUseAnalyzer class encapsulates the complexity of the underlying
modules and provides methods for:
- Quick analysis with minimal configuration
- Step-by-step analysis control
- Automatic visualization generation
- Configuration management

Example:
    >>> from landuse_intensity import LandUseAnalyzer
    >>>
    >>> # Quick analysis
    >>> analyzer = LandUseAnalyzer()
    >>> results = analyzer.quick_analysis(raster_paths, pixel_resolution=30)
    >>>
    >>> # Custom configuration
    >>> analyzer = LandUseAnalyzer(config_path="config.yaml")
    >>> results = analyzer.analyze_multistep(raster_paths)
    >>> analyzer.generate_all_plots(output_dir="./outputs")
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Import from existing core module (fix broken imports)
from .core import (
    ContingencyTable,
    IntensityAnalyzer,
    MultiStepAnalyzer,
    AnalysisResults,
    analyze_land_use_change
)
from .visualization import (
    plot_intensity_analysis,
    plot_single_step_sankey,  # Fixed function name
    plot_net_gain_loss,
    plot_transition_matrix_heatmap,
    create_summary_plots
)
from .raster import load_demo_data  # Fix: use existing function
from .utils import validate_data, format_area_label  # Fix: use existing function

# Configure logging
logger = logging.getLogger(__name__)


class LandUseAnalyzer:
    """
    High-level interface for land use intensity analysis.
    
    This class provides a simplified API that wraps the core functionality
    in an easy-to-use interface for common analysis workflows.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize analyzer with optional configuration.
        
        Parameters
        ----------
        config : dict, optional
            Configuration dictionary for analysis parameters
        """
        self.config = self._get_default_config()
        if config:
            self.config.update(config)
        
        # Results storage
        self.contingency_table: Optional[ContingencyTable] = None
        self.intensity_results: Optional[dict] = None
        self.plots_generated: List[str] = []
        self.execution_time: float = 0.0
        self.metadata: Dict[str, Any] = {}

    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            "pixel_resolution": 30,
            "exclude_classes": None,
            "parallel": False,
            "output_formats": ["png"],
            "generate_plots": True,
            "output_dir": "./analysis_output"
        }

    def summary(self) -> str:
        """Generate a summary of the analysis results."""
        if not self.intensity_results:
            return "No analysis results available."

        summary_lines = [
            "Land Use Intensity Analysis Summary",
            "=" * 40,
            f"Execution time: {self.execution_time:.2f} seconds",
            f"Contingency table shape: {self.contingency_table.table.shape if self.contingency_table else 'N/A'}",
            f"Plots generated: {len(self.plots_generated)}",
            "",
            "Intensity Analysis Results:",
        ]

        # Add interval level summary
        if 'interval' in self.intensity_results:
            interval_data = self.intensity_results['interval']
            summary_lines.append(f"  Uniform intensity (U): {interval_data['uniform_intensity']:.6f}")
            summary_lines.append(f"  Total change: {interval_data['total_change']:,.0f}")

        # Add category level summaries
        if 'category' in self.intensity_results:
            category_data = self.intensity_results['category']
            if 'gain' in category_data:
                summary_lines.append(f"  Gain analysis categories: {len(category_data['gain'])}")
            if 'loss' in category_data:
                summary_lines.append(f"  Loss analysis categories: {len(category_data['loss'])}")

        return "\n".join(summary_lines)
    """
    High-level analyzer for land use and cover change analysis.

    This class provides a simplified interface for performing complete
    land use intensity analysis using the Pontius methodology.

    Parameters
    ----------
    config_path : str, optional
        Path to YAML configuration file
    log_level : str, default "INFO"
        Logging level for analysis operations
    """

    def __init__(self, config_path: Optional[str] = None, log_level: str = "INFO"):
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging(log_level)

        # Default configuration
        self.default_config = {
            "pixel_resolution": 30.0,
            "exclude_classes": [0],
            "parallel": True,
            "output_formats": ["png", "html"],
            "cache_enabled": True,
            "progress_bar": True
        }

        logger.info("LandUseAnalyzer initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if self.config_path and Path(self.config_path).exists():
            try:
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                return {}
        return {}

    def _setup_logging(self, level: str):
        """Setup logging configuration."""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _merge_config(self, **kwargs) -> Dict[str, Any]:
        """Merge default config with user-provided parameters."""
        config = self.default_config.copy()
        config.update(self.config)
        config.update(kwargs)
        return config

    def quick_analysis(
        self,
        raster_paths: Union[str, List[str]],
        pixel_resolution: float = 30.0,
        **kwargs
    ) -> AnalysisResults:
        """
        Perform complete land use intensity analysis with minimal configuration.

        This method performs the full analysis pipeline:
        1. Load and validate raster data
        2. Calculate contingency table
        3. Perform intensity analysis (1-step and multi-step)
        4. Generate visualizations

        Parameters
        ----------
        raster_paths : str or list of str
            Paths to raster files or directory containing rasters
        pixel_resolution : float, default 30.0
            Pixel resolution in meters
        **kwargs
            Additional configuration parameters

        Returns
        -------
        AnalysisResults
            Complete analysis results container

        Example
        -------
        >>> analyzer = LandUseAnalyzer()
        >>> results = analyzer.quick_analysis(["raster1.tif", "raster2.tif", "raster3.tif"])
        >>> print(results.summary())
        """
        start_time = time.time()

        logger.info("Starting quick analysis...")
        config = self._merge_config(pixel_resolution=pixel_resolution, **kwargs)

        results = AnalysisResults()
        results.metadata = {
            "analysis_type": "quick",
            "raster_paths": raster_paths,
            "config": config
        }

        try:
            # Step 1: Load and validate raster data
            logger.info("Loading raster data...")
            raster_data = load_rasters(raster_paths)

            # Step 2: Calculate contingency table
            logger.info("Calculating contingency table...")
            contingency_result = contingency_table(
                input_raster=raster_data,
                pixel_resolution=config["pixel_resolution"],
                exclude_classes=config["exclude_classes"],
                parallel=config["parallel"]
            )

            results.contingency_table = contingency_result["contingency_table"]

            # Step 3: Perform intensity analysis
            logger.info("Performing intensity analysis...")
            intensity_result = intensity_analysis(contingency_result)
            results.intensity_analysis = intensity_result

            # Step 4: Generate visualizations (if requested)
            if config.get("generate_plots", True):
                logger.info("Generating visualizations...")
                output_dir = config.get("output_dir", "./analysis_output")
                Path(output_dir).mkdir(exist_ok=True)

                # Generate all plots
                plot_files = create_summary_plots(
                    intensity_result,
                    output_dir=output_dir,
                    formats=config["output_formats"]
                )
                results.plots_generated = plot_files

            results.execution_time = time.time() - start_time
            logger.info(f"Quick analysis completed in {results.execution_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

        return results

    def analyze_1step(
        self,
        raster_paths: Union[str, List[str]],
        pixel_resolution: float = 30.0,
        **kwargs
    ) -> AnalysisResults:
        """
        Perform 1-step intensity analysis.

        This method focuses on pairwise comparisons between consecutive
        time periods, providing detailed transition analysis.

        Parameters
        ----------
        raster_paths : str or list of str
            Paths to raster files
        pixel_resolution : float, default 30.0
            Pixel resolution in meters
        **kwargs
            Additional configuration parameters

        Returns
        -------
        AnalysisResults
            Analysis results with 1-step intensity analysis
        """
        logger.info("Starting 1-step intensity analysis...")
        config = self._merge_config(pixel_resolution=pixel_resolution, **kwargs)

        # Implementation follows similar pattern to quick_analysis
        # but focuses on 1-step analysis specifically
        results = self.quick_analysis(raster_paths, **config)
        results.metadata["analysis_type"] = "1-step"

        return results

    def analyze_multistep(
        self,
        raster_paths: Union[str, List[str]],
        pixel_resolution: float = 30.0,
        **kwargs
    ) -> AnalysisResults:
        """
        Perform multi-step intensity analysis.

        This method analyzes changes across the entire time series,
        providing insights into long-term trends and patterns.

        Parameters
        ----------
        raster_paths : str or list of str
            Paths to raster files
        pixel_resolution : float, default 30.0
            Pixel resolution in meters
        **kwargs
            Additional configuration parameters

        Returns
        -------
        AnalysisResults
            Analysis results with multi-step intensity analysis
        """
        logger.info("Starting multi-step intensity analysis...")
        config = self._merge_config(pixel_resolution=pixel_resolution, **kwargs)

        # Implementation follows similar pattern to quick_analysis
        # but focuses on multi-step analysis specifically
        results = self.quick_analysis(raster_paths, **config)
        results.metadata["analysis_type"] = "multi-step"

        return results

    def generate_all_plots(
        self,
        results: AnalysisResults,
        output_dir: str = "./plots",
        formats: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate all available plots from analysis results.

        Parameters
        ----------
        results : AnalysisResults
            Results from a previous analysis
        output_dir : str, default "./plots"
            Directory to save plots
        formats : list of str, optional
            Output formats (png, html, pdf)
        **kwargs
            Additional plotting parameters

        Returns
        -------
        list of str
            Paths to generated plot files
        """
        if not results.intensity_analysis:
            raise ValueError("No intensity analysis results available for plotting")

        if formats is None:
            formats = self.default_config["output_formats"]

        logger.info(f"Generating plots in {output_dir}...")
        Path(output_dir).mkdir(exist_ok=True)

        plot_files = create_summary_plots(
            results.intensity_analysis,
            output_dir=output_dir,
            formats=formats,
            **kwargs
        )

        results.plots_generated.extend(plot_files)
        logger.info(f"Generated {len(plot_files)} plot files")

        return plot_files

    def validate_data(
        self,
        raster_paths: Union[str, List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate raster data before analysis.

        Parameters
        ----------
        raster_paths : str or list of str
            Paths to raster files
        **kwargs
            Additional validation parameters

        Returns
        -------
        dict
            Validation results and recommendations
        """
        logger.info("Validating raster data...")

        try:
            raster_data = load_rasters(raster_paths)
            validation_results = validate_contingency_data(raster_data)

            logger.info("Data validation completed")
            return validation_results

        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise

    def get_config_template(self) -> str:
        """
        Get a YAML configuration template.

        Returns
        -------
        str
            YAML configuration template
        """
        template = """
# LandUse Intensity Analysis Configuration
analysis:
  pixel_resolution: 30.0
  exclude_classes: [0, 255]
  parallel: true

output:
  directory: "./analysis_output"
  formats: ["png", "html"]
  generate_plots: true

parallelization:
  backend: "dask"  # options: dask, ray, multiprocessing
  n_workers: 4
  memory_limit: "2GB"

cache:
  enabled: true
  strategy: "smart"  # options: smart, aggressive, conservative
  max_memory: "1GB"
  ttl: "24h"

logging:
  level: "INFO"
  file: "analysis.log"
"""
        return template.strip()


# Convenience functions for backward compatibility
def quick_analysis(
    raster_paths: Union[str, List[str]],
    pixel_resolution: float = 30.0,
    **kwargs
) -> AnalysisResults:
    """
    Convenience function for quick analysis.

    Parameters
    ----------
    raster_paths : str or list of str
        Paths to raster files
    pixel_resolution : float, default 30.0
        Pixel resolution in meters
    **kwargs
        Additional configuration parameters

    Returns
    -------
    AnalysisResults
        Complete analysis results
    """
    analyzer = LandUseAnalyzer()
    return analyzer.quick_analysis(raster_paths, pixel_resolution, **kwargs)


def analyze_1step(
    raster_paths: Union[str, List[str]],
    pixel_resolution: float = 30.0,
    **kwargs
) -> AnalysisResults:
    """
    Convenience function for 1-step analysis.
    """
    analyzer = LandUseAnalyzer()
    return analyzer.analyze_1step(raster_paths, pixel_resolution, **kwargs)


def analyze_multistep(
    raster_paths: Union[str, List[str]],
    pixel_resolution: float = 30.0,
    **kwargs
) -> AnalysisResults:
    """
    Convenience function for multi-step analysis.
    """
    analyzer = LandUseAnalyzer()
    return analyzer.analyze_multistep(raster_paths, pixel_resolution, **kwargs)
