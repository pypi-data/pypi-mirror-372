"""
Simple Land Use Analyzer: High-level API for land use and cover change analysis.

This module provides a simplified, user-friendly interface that uses only
the working core functionality.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Import from existing core module (working imports only)
from .core import (
    ContingencyTable,
    IntensityAnalyzer,
    MultiStepAnalyzer,
    AnalysisResults,
    analyze_land_use_change
)
from .utils import demo_landscape, demo_landscape_pair, validate_data

# Configure logging
logger = logging.getLogger(__name__)


class SimpleLandUseAnalyzer:
    """
    Simplified interface for land use intensity analysis.
    
    This class provides easy-to-use methods that work with the current
    core functionality without broken dependencies.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize analyzer.
        
        Parameters
        ----------
        config : dict, optional
            Configuration dictionary for analysis parameters
        """
        self.config = config or {}
        
        # Results storage
        self.contingency_table: Optional[ContingencyTable] = None
        self.intensity_results: Optional[dict] = None
        self.multistep_results: Optional[dict] = None
        self.execution_time: float = 0.0

    def analyze_two_step(
        self,
        raster1: np.ndarray,
        raster2: np.ndarray,
        labels1: Optional[List] = None,
        labels2: Optional[List] = None
    ) -> AnalysisResults:
        """
        Perform two-step (single transition) analysis.
        
        Parameters
        ----------
        raster1 : np.ndarray
            First time period raster
        raster2 : np.ndarray
            Second time period raster
        labels1 : list, optional
            Labels for raster1 classes
        labels2 : list, optional
            Labels for raster2 classes
            
        Returns
        -------
        AnalysisResults
            Complete analysis results
        """
        start_time = time.time()
        logger.info("Starting two-step analysis...")
        
        try:
            # Create contingency table with new R-style format
            self.contingency_table = ContingencyTable.from_rasters(
                raster1, raster2, time_labels=[labels1, labels2] if labels1 and labels2 else None
            )
            
            # Run intensity analysis
            analyzer = IntensityAnalyzer(self.contingency_table)
            self.intensity_results = analyzer.analyze_interval_level()
            
            self.execution_time = time.time() - start_time
            logger.info(f"Two-step analysis completed in {self.execution_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

        # Create results container
        results = AnalysisResults()
        results.contingency_table = self.contingency_table.table
        results.intensity_analysis = self.intensity_results
        results.metadata = {
            "analysis_type": "two_step",
            "execution_time": self.execution_time,
            "raster_shapes": [raster1.shape, raster2.shape]
        }
        
        return results

    def analyze_multistep(
        self,
        rasters: List[np.ndarray],
        time_labels: Optional[List[str]] = None
    ) -> AnalysisResults:
        """
        Perform multi-step analysis.
        
        Parameters
        ----------
        rasters : list of np.ndarray
            List of raster arrays (minimum 3)
        time_labels : list of str, optional
            Labels for each time period
            
        Returns
        -------
        AnalysisResults
            Complete multi-step analysis results
        """
        start_time = time.time()
        logger.info("Starting multi-step analysis...")
        
        if len(rasters) < 3:
            raise ValueError("Multi-step analysis requires at least 3 time periods")
        
        try:
            # Create multi-step analyzer
            analyzer = MultiStepAnalyzer(rasters, time_labels)
            
            # Run all analyses
            self.multistep_results = analyzer.analyze_all_steps()
            overall_results = analyzer.analyze_overall_change()
            comparison = analyzer.compare_step_vs_overall()
            persistence = analyzer.get_persistence_through_time()
            
            self.execution_time = time.time() - start_time
            logger.info(f"Multi-step analysis completed in {self.execution_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Multi-step analysis failed: {e}")
            raise

        # Create results container
        results = AnalysisResults()
        results.intensity_analysis = {
            'step_by_step': self.multistep_results,
            'overall': overall_results,
            'comparison': comparison,
            'persistence': persistence
        }
        results.metadata = {
            "analysis_type": "multi_step",
            "execution_time": self.execution_time,
            "n_periods": len(rasters),
            "time_labels": time_labels or [f"t{i}" for i in range(len(rasters))]
        }
        
        return results

    def quick_demo_analysis(self) -> AnalysisResults:
        """
        Perform quick demo analysis using generated demo data.
        
        Returns
        -------
        AnalysisResults
            Demo analysis results
        """
        logger.info("Generating demo data for quick analysis...")
        
        # Generate demo landscapes using corrected function
        raster1, raster2 = demo_landscape_pair()
        
        labels = ["Forest", "Agriculture", "Urban", "Water"]
        
        return self.analyze_two_step(raster1, raster2, labels, labels)

    def summary(self) -> str:
        """Generate a summary of the analysis results."""
        if not (self.intensity_results or self.multistep_results):
            return "No analysis results available."

        summary_lines = [
            "Land Use Intensity Analysis Summary",
            "=" * 40,
            f"Execution time: {self.execution_time:.2f} seconds"
        ]

        if self.contingency_table:
            summary_lines.extend([
                f"Contingency table shape: {self.contingency_table.table.shape}",
                f"Total area: {self.contingency_table.total_area:,.0f}",
                f"Total change: {self.contingency_table.total_change:,.0f}",
                f"Persistence: {self.contingency_table.persistence:,.0f}"
            ])

        if self.intensity_results:
            if 'interval' in self.intensity_results:
                interval_data = self.intensity_results['interval']
                summary_lines.append(f"Uniform intensity: {interval_data['uniform_intensity']:.6f}")

        if self.multistep_results:
            summary_lines.extend([
                f"Multi-step analysis: {self.multistep_results['n_steps']} steps",
                f"Time span: {self.multistep_results['total_time_span']}"
            ])

        return "\n".join(summary_lines)


# Convenience functions
def quick_analysis(raster1: np.ndarray, raster2: np.ndarray) -> AnalysisResults:
    """
    Quick two-step analysis convenience function.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period raster
    raster2 : np.ndarray
        Second time period raster
        
    Returns
    -------
    AnalysisResults
        Analysis results
    """
    analyzer = SimpleLandUseAnalyzer()
    return analyzer.analyze_two_step(raster1, raster2)


def multistep_analysis(rasters: List[np.ndarray], 
                      time_labels: Optional[List[str]] = None) -> AnalysisResults:
    """
    Multi-step analysis convenience function.
    
    Parameters
    ----------
    rasters : list of np.ndarray
        List of raster arrays
    time_labels : list of str, optional
        Labels for each time period
        
    Returns
    -------
    AnalysisResults
        Analysis results
    """
    analyzer = SimpleLandUseAnalyzer()
    return analyzer.analyze_multistep(rasters, time_labels)


def demo_analysis() -> AnalysisResults:
    """
    Quick demo analysis convenience function.
    
    Returns
    -------
    AnalysisResults
        Demo analysis results
    """
    analyzer = SimpleLandUseAnalyzer()
    return analyzer.quick_demo_analysis()
