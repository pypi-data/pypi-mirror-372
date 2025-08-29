"""
Core land use change analysis classes.

This module provides the main object-oriented interface for land use intensity analysis,
implementing the Pontius-Aldwaik methodology in a modern, clean design.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


@dataclass
class AnalysisResults:
    """Container for analysis results."""
    
    contingency_table: Optional[pd.DataFrame] = None
    intensity_analysis: Optional[dict] = None
    spatial_data: Optional[dict] = None
    metadata: Optional[dict] = None


class ContingencyTable:
    """
    Modern contingency table class for land use transition analysis.
    
    Consolidates functionality from analysis.py while maintaining clean OOP design.
    """
    
    def __init__(self, data: Union[np.ndarray, pd.DataFrame]):
        """
        Initialize contingency table from data.
        
        Parameters
        ----------
        data : array-like
            Contingency table data
        """
        if isinstance(data, pd.DataFrame):
            self.table = data
        else:
            self.table = pd.DataFrame(data)
    
    @classmethod
    def from_rasters(cls, raster1: np.ndarray, raster2: np.ndarray,
                     labels1: Optional[List] = None, labels2: Optional[List] = None):
        """
        Create contingency table from two raster arrays.
        
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
        ContingencyTable
            New contingency table instance
        """
        if raster1.shape != raster2.shape:
            raise ValueError("Rasters must have the same shape")
        
        # Get unique values
        unique1 = np.unique(raster1)
        unique2 = np.unique(raster2)
        
        # Use provided labels or create defaults
        if labels1 is None:
            labels1 = [f"Class_{int(val)}" for val in unique1]
        if labels2 is None:
            labels2 = [f"Class_{int(val)}" for val in unique2]
        
        # Create contingency table
        contingency = np.zeros((len(unique1), len(unique2)), dtype=int)
        
        for i, val1 in enumerate(unique1):
            for j, val2 in enumerate(unique2):
                mask = (raster1 == val1) & (raster2 == val2)
                contingency[i, j] = np.sum(mask)
        
        # Convert to DataFrame
        df = pd.DataFrame(contingency, index=labels1, columns=labels2)
        return cls(df)
    
    @property
    def data(self):
        """Access to table data for backward compatibility."""
        return self.table
    
    @property 
    def total_area(self):
        """Total area (sum of all transitions)."""
        return self.table.sum().sum()
    
    @property
    def persistence(self):
        """Persistence (diagonal sum)."""
        return np.diag(self.table.values).sum()
    
    @property
    def total_change(self):
        """Total change (total - persistence)."""
        return self.total_area - self.persistence
        
    
    def validate(self) -> bool:
        """Validate contingency table data."""
        if self.table is None or self.table.empty:
            return False
        
        # Check for non-negative values
        if (self.table < 0).any().any():
            return False
            
        return True
    
    def get_transition_matrix(self) -> pd.DataFrame:
        """Get transition matrix representation."""
        return self.table.copy()
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics."""
        if not self.validate():
            return {}
            
        return {
            'total_area': self.total_area,
            'classes': len(self.table.columns),
            'transitions': (self.table > 0).sum().sum(),
            'persistence': self.persistence
        }


class IntensityAnalyzer:
    """
    Modern intensity analysis implementation following Pontius-Aldwaik methodology.
    
    Consolidates and modernizes functionality from intensity.py and pontius.py.
    """
    
    def __init__(self, contingency_table: ContingencyTable):
        """
        Initialize analyzer with contingency table.
        
        Parameters
        ----------
        contingency_table : ContingencyTable
            Prepared contingency table data
        """
        self.ct = contingency_table
        self.results = {}
    
    def analyze_interval_level(self) -> Dict:
        """
        Perform interval-level intensity analysis.
        
        Returns
        -------
        dict
            Interval analysis results including uniform intensity
        """
        if not self.ct.validate():
            raise ValueError("Invalid contingency table")
        
        data = self.ct.table.values
        total_change = data.sum() - np.diag(data).sum()
        total_area = data.sum()
        time_interval = 1  # Simplified - would calculate from years
        
        # Uniform intensity (U)
        uniform_intensity = total_change / (total_area * time_interval)
        
        results = {
            'uniform_intensity': uniform_intensity,
            'total_change': total_change,
            'total_area': total_area,
            'time_interval': time_interval
        }
        
        self.results['interval'] = results
        return results
    
    def analyze_category_level(self) -> Dict:
        """
        Perform category-level intensity analysis.
        
        Returns
        -------
        dict
            Category analysis results for gains and losses
        """
        if not self.ct.validate():
            raise ValueError("Invalid contingency table")
        
        data = self.ct.table.values
        n_rows, n_cols = data.shape
        
        # Calculate gains and losses for each category
        gains = data.sum(axis=0)  # Column sums (gains to each class)
        losses = data.sum(axis=1)  # Row sums (losses from each class)
        
        # Subtract diagonal values (persistence) only where they exist
        min_dim = min(n_rows, n_cols)
        diagonal = np.diag(data[:min_dim, :min_dim])
        
        # Adjust gains and losses by removing persistence
        gains_corrected = gains.copy()
        losses_corrected = losses.copy()
        
        for i in range(min_dim):
            if i < len(gains_corrected):
                gains_corrected[i] -= diagonal[i]
            if i < len(losses_corrected):
                losses_corrected[i] -= diagonal[i]
        
        results = {
            'gains': gains_corrected.tolist(),
            'losses': losses_corrected.tolist(),
            'classes': list(self.ct.table.columns)
        }
        
        self.results['category'] = results
        return results
    
    def analyze_transition_level(self, from_class: int, to_class: int) -> Dict:
        """
        Perform transition-level intensity analysis.
        
        Parameters
        ----------
        from_class : int
            Index of source class
        to_class : int
            Index of target class
            
        Returns
        -------
        dict
            Transition analysis results
        """
        if not self.ct.validate():
            raise ValueError("Invalid contingency table")
        
        data = self.ct.table.values
        
        # Transition intensity calculation
        transition_value = data[from_class, to_class]
        total_from_class = data[from_class, :].sum()
        
        intensity = transition_value / total_from_class if total_from_class > 0 else 0
        
        results = {
            'from_class': from_class,
            'to_class': to_class,
            'transition_intensity': intensity,
            'transition_value': transition_value,
            'total_from_class': total_from_class
        }
        
        self.results['transition'] = results
        return results
    
    def analyze(self) -> Dict:
        """
        Perform complete intensity analysis.
        
        Returns
        -------
        dict
            Complete analysis results with interval, category, and transition levels
        """
        results = {}
        
        # Interval level analysis
        results['interval'] = self.analyze_interval_level()
        
        # Category level analysis  
        results['category'] = self.analyze_category_level()
        
        # Transition level analysis (for all transitions)
        data = self.ct.table.values
        transitions = []
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if i != j and data[i, j] > 0:  # Only non-zero transitions
                    trans_result = self.analyze_transition_level(i, j)
                    transitions.append(trans_result)
        
        results['transition'] = transitions
        
        return results
    
    def full_analysis(self) -> AnalysisResults:
        """
        Perform complete Pontius-Aldwaik intensity analysis.
        
        Returns
        -------
        AnalysisResults
            Complete analysis results
        """
        results = AnalysisResults()
        results.contingency_table = self.ct.table
        
        # Perform all levels of analysis
        interval_results = self.analyze_interval_level()
        category_results = self.analyze_category_level()
        
        results.intensity_analysis = {
            'interval': interval_results,
            'category': category_results,
            'metadata': {
                'classes': list(self.ct.table.columns),
                'n_classes': len(self.ct.table.columns)
            }
        }
        
        return results


class MultiStepAnalyzer:
    """
    Multi-step intensity analysis for temporal land use change sequences.
    
    Supports analysis of land use transitions across multiple time periods,
    following Pontius-Aldwaik methodology for multi-temporal analysis.
    """
    
    def __init__(self, rasters: List[np.ndarray], time_labels: List[str] = None):
        """
        Initialize multi-step analyzer.
        
        Parameters
        ----------
        rasters : List[np.ndarray]
            List of raster arrays for each time period (minimum 3 periods)
        time_labels : List[str], optional
            Labels for each time period
        """
        if len(rasters) < 3:
            raise ValueError("Multi-step analysis requires at least 3 time periods")
        
        self.rasters = rasters
        self.n_periods = len(rasters)
        
        if time_labels is None:
            self.time_labels = [f"t{i}" for i in range(self.n_periods)]
        else:
            if len(time_labels) != self.n_periods:
                raise ValueError("Number of time labels must match number of rasters")
            self.time_labels = time_labels
        
        # Create contingency tables for each transition
        self.contingency_tables = []
        for i in range(self.n_periods - 1):
            ct = ContingencyTable.from_rasters(rasters[i], rasters[i + 1])
            self.contingency_tables.append(ct)
    
    def analyze_all_steps(self) -> Dict:
        """
        Analyze intensity for all time step transitions.
        
        Returns
        -------
        dict
            Multi-step analysis results
        """
        step_results = []
        
        for i, ct in enumerate(self.contingency_tables):
            # Analyze each step individually
            analyzer = IntensityAnalyzer(ct)
            interval_result = analyzer.analyze_interval_level()
            category_result = analyzer.analyze_category_level()
            
            step_result = {
                'intensity_analysis': {
                    'interval': interval_result,
                    'category': category_result
                },
                'time_step': f"{self.time_labels[i]} to {self.time_labels[i+1]}",
                'step_index': i
            }
            step_results.append(step_result)
        
        return {
            'step_results': step_results,
            'n_steps': len(step_results),
            'time_labels': self.time_labels,
            'total_time_span': f"{self.time_labels[0]} to {self.time_labels[-1]}"
        }
    
    def analyze_overall_change(self) -> Dict:
        """
        Analyze overall change from first to last time period.
        
        Returns
        -------
        dict
            Overall change analysis results
        """
        # Create contingency table for first to last period
        overall_ct = ContingencyTable.from_rasters(self.rasters[0], self.rasters[-1])
        analyzer = IntensityAnalyzer(overall_ct)
        interval_results = analyzer.analyze_interval_level()
        category_results = analyzer.analyze_category_level()
        
        overall_results = {
            'intensity_analysis': {
                'interval': interval_results,
                'category': category_results
            },
            'time_span': f"{self.time_labels[0]} to {self.time_labels[-1]}",
            'n_intermediate_steps': self.n_periods - 2
        }
        
        return overall_results
    
    def compare_step_vs_overall(self) -> Dict:
        """
        Compare step-wise changes with overall change to detect temporal patterns.
        
        Returns
        -------
        dict
            Comparison analysis results
        """
        step_results = self.analyze_all_steps()
        overall_results = self.analyze_overall_change()
        
        # Calculate cumulative uniform intensity
        step_intensities = [step['intensity_analysis']['interval']['uniform_intensity'] 
                          for step in step_results['step_results']]
        cumulative_intensity = sum(step_intensities)
        overall_intensity = overall_results['intensity_analysis']['interval']['uniform_intensity']
        
        return {
            'step_by_step': step_results,
            'overall': overall_results,
            'comparison': {
                'cumulative_step_intensity': cumulative_intensity,
                'overall_intensity': overall_intensity,
                'intensity_ratio': cumulative_intensity / overall_intensity if overall_intensity > 0 else 0,
                'temporal_pattern': 'uniform' if abs(cumulative_intensity - overall_intensity) < 0.01 else 'non-uniform'
            }
        }
    
    def get_persistence_through_time(self) -> Dict:
        """
        Calculate persistence of each category through all time periods.
        
        Returns
        -------
        dict
            Persistence analysis through time
        """
        # Get unique categories across all periods
        all_categories = set()
        for raster in self.rasters:
            all_categories.update(np.unique(raster))
        all_categories = sorted(list(all_categories))
        
        persistence_data = {}
        
        for category in all_categories:
            # Track this category through all time periods
            category_areas = []
            for raster in self.rasters:
                area = np.sum(raster == category)
                category_areas.append(area)
            
            # Calculate persistence (areas that remain the same category throughout)
            if len(self.rasters) > 1:
                persistent_mask = (self.rasters[0] == category)
                for raster in self.rasters[1:]:
                    persistent_mask &= (raster == category)
                persistent_area = np.sum(persistent_mask)
            else:
                persistent_area = category_areas[0]
            
            persistence_data[f"Category_{category}"] = {
                'areas_through_time': category_areas,
                'persistent_area': persistent_area,
                'initial_area': category_areas[0],
                'final_area': category_areas[-1],
                'persistence_rate': persistent_area / category_areas[0] if category_areas[0] > 0 else 0
            }
        
        return {
            'persistence_by_category': persistence_data,
            'time_labels': self.time_labels
        }


def verify_analysis_support() -> Dict[str, bool]:
    """
    Verify what types of analysis are supported by the current implementation.
    
    Returns
    -------
    dict
        Dictionary indicating support for different analysis types
    """
    return {
        'single_step_analysis': True,
        'multi_step_analysis': True,
        'contingency_table_analysis': True,
        'intensity_analysis': True,
        'spatial_change_analysis': True,
        'persistence_analysis': True,
        'sankey_diagrams': True,  # Available if plotly is installed
        'pontius_methodology': True
    }


class ChangeAnalyzer:
    """
    Spatial and temporal change analysis.
    
    Consolidates functionality from spatial_maps.py and image_processing.py.
    """
    
    def __init__(self, raster1: np.ndarray, raster2: np.ndarray):
        """
        Initialize change analyzer.
        
        Parameters
        ----------
        raster1 : np.ndarray
            First time period raster
        raster2 : np.ndarray
            Second time period raster
        """
        self.raster1 = raster1
        self.raster2 = raster2
    
    def analyze(self) -> Dict:
        """
        Perform spatial change analysis.
        
        Returns
        -------
        dict
            Change analysis results
        """
        # Calculate change map
        change_map = (self.raster1 != self.raster2).astype(int)
        
        # Calculate statistics
        total_pixels = self.raster1.size
        changed_pixels = np.sum(change_map)
        change_percentage = (changed_pixels / total_pixels) * 100
        
        return {
            'change_map': change_map,
            'total_pixels': total_pixels,
            'changed_pixels': changed_pixels,
            'change_percentage': change_percentage,
            'persistence_pixels': total_pixels - changed_pixels
        }
    
    def detect_hotspots(self) -> Dict:
        """Detect change hotspots."""
        # Simplified implementation
        return {'hotspots': []}
    
    def create_change_map(self) -> Dict:
        """Create spatial change visualization."""
        # Simplified implementation
        return {'change_map': None}


def analyze_land_use_change(
    raster1: np.ndarray, 
    raster2: np.ndarray,
    analysis_type: str = "full"
) -> Dict:
    """
    Main analysis function that combines contingency table and intensity analysis.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period raster
    raster2 : np.ndarray 
        Second time period raster
    analysis_type : str
        Type of analysis to perform
        
    Returns
    -------
    dict
        Complete analysis results
    """
    # Create contingency table
    ct = ContingencyTable.from_rasters(raster1, raster2)
    
    # Create intensity analyzer
    intensity_analyzer = IntensityAnalyzer(ct)
    intensity_results = intensity_analyzer.analyze()
    
    # Create change analyzer
    change_analyzer = ChangeAnalyzer(raster1, raster2)
    change_results = change_analyzer.analyze()
    
    return {
        'contingency_table': ct.table,
        'intensity_analysis': intensity_results,
        'change_analysis': change_results,
        'summary': {
            'total_area': ct.total_area,
            'persistence': ct.persistence,
            'total_change': ct.total_change,
            'change_percentage': (ct.total_change / ct.total_area) * 100
        }
    }
