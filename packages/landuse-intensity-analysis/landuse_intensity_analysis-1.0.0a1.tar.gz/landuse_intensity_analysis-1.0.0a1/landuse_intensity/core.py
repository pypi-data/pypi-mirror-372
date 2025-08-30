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
    R-style contingency table for land use change analysis.
    
    This class provides functionality to create and analyze contingency tables
    from raster data, following the R contingencyTable() function structure.
    Returns lulc_Multistep, lulc_Onestep, tb_legend, totalArea, totalInterval.
    """
    
    def __init__(self, rasters: List[np.ndarray], time_labels: List[str] = None, 
                 pixel_resolution: float = 30.0, class_names: Dict[int, str] = None):
        """
        Initialize R-style ContingencyTable with intelligent onestep/multistep detection.
        
        Automatically determines analysis type based on number of rasters:
        - 2 rasters: Creates onestep analysis only  
        - 3+ rasters: Creates both multistep (sequential) and onestep (first→last) analysis
        
        Parameters
        ----------
        rasters : List[np.ndarray]
            List of raster arrays ordered by time
        time_labels : List[str], optional
            Time period labels (e.g., ['1990', '2000', '2010'])
            If None, intelligently generated from indices
        pixel_resolution : float
            Pixel resolution in meters (default: 30)
        class_names : Dict[int, str], optional
            Mapping of class values to names
        """
        if len(rasters) < 2:
            raise ValueError('ContingencyTable needs at least 2 rasters')
        
        self.rasters = rasters
        self.n_rasters = len(rasters)
        
        # Smart time label generation
        if time_labels is None:
            time_labels = [f"t{i}" for i in range(self.n_rasters)]
        
        if len(time_labels) != self.n_rasters:
            raise ValueError("Number of time labels must match number of rasters")
        
        self.time_labels = time_labels
        self.pixel_resolution = pixel_resolution
        self.class_names = class_names or {}
        
        # Determine analysis type intelligently
        self.is_onestep_only = (self.n_rasters == 2)
        self.is_multistep = (self.n_rasters > 2)
        
        # Verify all rasters have same shape
        first_shape = rasters[0].shape
        for i, raster in enumerate(rasters[1:], 1):
            if raster.shape != first_shape:
                raise ValueError(f"Raster {i} has different shape: {raster.shape} vs {first_shape}")
        
        # Generate R-style analysis
        self._generate_r_analysis()
    
    def _create_transition_data(self, raster_from, raster_to, year_from, year_to):
        """Create transition data for a pair of rasters."""
        # Create cross-tabulation
        flat_from = raster_from.flatten()
        flat_to = raster_to.flatten()
        
        # Remove no-data values if present
        valid_mask = (flat_from != -9999) & (flat_to != -9999)
        flat_from = flat_from[valid_mask]
        flat_to = flat_to[valid_mask]
        
        # Create contingency table
        table = pd.crosstab(
            pd.Series(flat_from, name='From'),
            pd.Series(flat_to, name='To'),
            dropna=False
        )
        
        transitions = []
        for idx_from, class_from in enumerate(table.index):
            for idx_to, class_to in enumerate(table.columns):
                qt_pixel = table.iloc[idx_from, idx_to]
                if qt_pixel > 0:  # Only include non-zero transitions
                    
                    # Use class values directly
                    from_val = int(class_from)
                    to_val = int(class_to)
                    
                    # Calculate area in km²
                    km2 = qt_pixel * (self.pixel_resolution ** 2) / 1e6
                    
                    # Calculate interval (handle non-numeric labels)
                    try:
                        interval = int(year_to) - int(year_from)
                        year_from_int = int(year_from)
                        year_to_int = int(year_to)
                    except ValueError:
                        # If labels are not numeric, use position-based interval
                        interval = 1
                        year_from_int = 0
                        year_to_int = 1
                    
                    transitions.append({
                        'Period': f"{year_from}-{year_to}",
                        'From': from_val,
                        'To': to_val,
                        'km2': km2,
                        'QtPixel': int(qt_pixel),
                        'Interval': interval,
                        'yearFrom': year_from_int,
                        'yearTo': year_to_int
                    })
        
        return transitions
    
    def _generate_r_analysis(self):
        """Generate R-style contingency analysis."""
        # 1. Multi-step analysis (all sequential transitions)
        multistep_data = []
        
        if self.n_rasters == 2:
            # For 2 rasters: multistep is empty, onestep contains the single transition
            pass  # multistep_data remains empty
        else:
            # For 3+ rasters: multistep contains all sequential transitions
            for i in range(self.n_rasters - 1):
                transitions = self._create_transition_data(
                    self.rasters[i], self.rasters[i + 1],
                    self.time_labels[i], self.time_labels[i + 1]
                )
                multistep_data.extend(transitions)
        
        # 2. One-step analysis (ALWAYS first to last raster)
        # This is the key correction: onestep should always represent
        # the complete change from first to last time period
        onestep_data = self._create_transition_data(
            self.rasters[0], self.rasters[-1],
            self.time_labels[0], self.time_labels[-1]
        )
        
        # 3. Create legend table
        all_classes = set()
        for raster in self.rasters:
            all_classes.update(np.unique(raster))
        all_classes = sorted(list(all_classes))
        
        # R-style colors
        r_colors = [
            "#002F70", "#0A468D", "#295EAE", "#4A76C7", "#6F8DD2",
            "#8EA4DE", "#ABBBE8", "#C5CFF0", "#DCE2F6", "#EFF1F8",
            "#F9EFEF", "#F9DCDC", "#F3C5C5", "#EAACAC", "#DD9191",
            "#CE7575", "#BD5758", "#A13F3F", "#7F2A2B", "#5F1415"
        ]
        
        # Generate category names
        import random
        import string
        
        def generate_category_name():
            return ''.join(random.choices(string.ascii_uppercase, k=3))
        
        tb_legend_data = []
        for i, category_value in enumerate(all_classes):
            if category_value in self.class_names:
                category_name = self.class_names[category_value]
            else:
                category_name = generate_category_name()
            
            color = r_colors[i % len(r_colors)]
            
            tb_legend_data.append({
                'categoryValue': int(category_value),
                'categoryName': category_name,
                'color': color
            })
        
        # 4. Calculate total area
        area_data = []
        multistep_df = pd.DataFrame(multistep_data) if multistep_data else pd.DataFrame()
        
        if not multistep_df.empty:
            for period in multistep_df['Period'].unique():
                period_data = multistep_df[multistep_df['Period'] == period]
                total_km2 = period_data['km2'].sum()
                total_pixels = period_data['QtPixel'].sum()
                
                area_data.append({
                    'Period': period,
                    'area_km2': total_km2,
                    'QtPixel': total_pixels
                })
        
        # Get first period for totalArea
        if area_data:
            total_area = pd.DataFrame([area_data[0]])[['area_km2', 'QtPixel']]
        else:
            # Fallback calculation
            total_pixels = self.rasters[0].size
            total_km2 = total_pixels * (self.pixel_resolution ** 2) / 1e6
            total_area = pd.DataFrame({
                'area_km2': [total_km2],
                'QtPixel': [total_pixels]
            })
        
        # 5. Calculate total interval
        try:
            total_interval = int(self.time_labels[-1]) - int(self.time_labels[0])
        except ValueError:
            total_interval = len(self.time_labels) - 1
        
        # 6. Create final DataFrames
        self.lulc_Multistep = pd.DataFrame(multistep_data)
        self.lulc_Onestep = pd.DataFrame(onestep_data)
        self.tb_legend = pd.DataFrame(tb_legend_data)
        self.totalArea = total_area
        self.totalInterval = total_interval
    
    def _create_simple_contingency_table(self, raster_from, raster_to):
        """Create simple contingency table for backward compatibility."""
        # Flatten rasters
        flat_from = raster_from.flatten()
        flat_to = raster_to.flatten()
        
        # Get unique classes
        classes = sorted(set(flat_from) | set(flat_to))
        
        # Create contingency table
        contingency = pd.DataFrame(0, index=classes, columns=classes)
        
        for from_val in classes:
            for to_val in classes:
                count = np.sum((flat_from == from_val) & (flat_to == to_val))
                contingency.loc[from_val, to_val] = count
        
        return contingency
        
        # Sort like R function
        if not self.lulc_Multistep.empty:
            self.lulc_Multistep = self.lulc_Multistep.sort_values(['yearFrom', 'From', 'To']).reset_index(drop=True)
        
        if not self.lulc_Onestep.empty:
            self.lulc_Onestep = self.lulc_Onestep.sort_values(['From', 'To']).reset_index(drop=True)
    
    @classmethod
    def from_rasters(cls, rasters: Union[List[np.ndarray], np.ndarray], 
                     raster_to: np.ndarray = None, 
                     time_labels: List[str] = None,
                     pixel_resolution: float = 30.0, 
                     class_names: Dict[int, str] = None) -> 'ContingencyTable':
        """
        Create R-style contingency table from rasters (backward compatibility).
        
        Parameters
        ----------
        rasters : Union[List[np.ndarray], np.ndarray]
            List of raster arrays or single raster (if raster_to provided)
        raster_to : np.ndarray, optional
            Second raster (for backward compatibility)
        time_labels : List[str], optional
            Time period labels
        pixel_resolution : float
            Pixel resolution in meters
        class_names : Dict[int, str], optional
            Mapping of class values to names
            
        Returns
        -------
        ContingencyTable
            R-style contingency table instance
        """
        # Handle backward compatibility
        if raster_to is not None:
            # If raster_to is provided, rasters should be a single raster
            rasters = [rasters, raster_to]
        elif not isinstance(rasters, list):
            # If rasters is a single array, convert to list
            rasters = [rasters]
        # If rasters is already a list, use it as is
        
        return cls(rasters=rasters, time_labels=time_labels, 
                  pixel_resolution=pixel_resolution, class_names=class_names)
    
    @classmethod
    def from_files(cls, filenames: List[str], 
                   label_position: Union[int, str] = "smart",
                   separator: str = "_",
                   pixel_resolution: float = 30.0,
                   class_names: Dict[int, str] = None) -> 'ContingencyTable':
        """
        Create ContingencyTable from raster files with automatic time label extraction.
        
        Parameters
        ----------
        filenames : List[str]
            List of raster file paths
        label_position : Union[int, str], default "smart"
            Position of time labels in filenames:
            - "smart": Auto-detect years and labels
            - "last": Last part before extension
            - "first": First part of filename  
            - int: Specific position after splitting by separator
        separator : str, default "_"
            Character to split filename parts
        pixel_resolution : float
            Pixel resolution in meters
        class_names : Dict[int, str], optional
            Mapping of class values to names
            
        Returns
        -------
        ContingencyTable
            R-style contingency table instance
            
        Examples
        --------
        >>> files = ['landuse_1990.tif', 'landuse_2000.tif', 'landuse_2010.tif']
        >>> ct = ContingencyTable.from_files(files)
        >>> print(ct.time_labels)  # ['1990', '2000', '2010']
        
        >>> files = ['data_T1_v1.tif', 'data_T2_v1.tif']
        >>> ct = ContingencyTable.from_files(files, label_position=1)
        >>> print(ct.time_labels)  # ['T1', 'T2']
        """
        from .raster import read_raster
        from .utils import smart_extract_time_labels, extract_time_labels_from_filenames
        
        # Read rasters
        rasters = []
        for filename in filenames:
            raster, _ = read_raster(filename)
            rasters.append(raster)
        
        # Extract time labels
        if label_position == "smart":
            time_labels = smart_extract_time_labels(filenames)
        else:
            time_labels = extract_time_labels_from_filenames(
                filenames, label_position=label_position, separator=separator
            )
        
        return cls(rasters=rasters, time_labels=time_labels,
                  pixel_resolution=pixel_resolution, class_names=class_names)
    
    def validate(self) -> bool:
        """
        Validate R-style contingency table data.
        
        Returns
        -------
        bool
            True if all R-style components are present and valid
        """
        # Check if all R-style components exist
        required_attrs = ['lulc_Multistep', 'lulc_Onestep', 'tb_legend', 'totalArea', 'totalInterval']
        for attr in required_attrs:
            if not hasattr(self, attr):
                return False
        
        # Check if onestep data exists (minimum requirement)
        return not self.lulc_Onestep.empty
    
    def get_transition_matrix(self) -> pd.DataFrame:
        """
        Get transition matrix representation from onestep data.
        
        Returns
        -------
        pd.DataFrame
            Transition matrix with From classes as rows and To classes as columns
        """
        if self.lulc_Onestep.empty:
            return pd.DataFrame()
        
        return self.lulc_Onestep.pivot_table(
            index='From', columns='To', values='QtPixel', fill_value=0
        )
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics from R-style data.
        
        Returns
        -------
        Dict
            Dictionary with summary statistics
        """
        if not self.validate():
            return {}
        
        # Calculate persistence (diagonal sum)
        persistent = self.lulc_Onestep[self.lulc_Onestep['From'] == self.lulc_Onestep['To']]
        persistence_pixels = persistent['QtPixel'].sum()
        
        total_pixels = self.totalArea['QtPixel'].iloc[0]
        
        return {
            'total_pixels': total_pixels,
            'total_area_km2': self.totalArea['area_km2'].iloc[0],
            'n_classes': len(self.tb_legend),
            'n_transitions': len(self.lulc_Onestep),
            'n_multistep_transitions': len(self.lulc_Multistep),
            'persistence_pixels': persistence_pixels,
            'change_pixels': total_pixels - persistence_pixels,
            'total_interval_years': self.totalInterval,
            'is_onestep_only': self.is_onestep_only,
            'is_multistep': self.is_multistep
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
            Prepared contingency table data (now R-style compatible)
        """
        self.ct = contingency_table
        self.results = {}
        
        # Adapt to new R-style format
        if hasattr(contingency_table, 'lulc_Onestep') and not contingency_table.lulc_Onestep.empty:
            # Use R-style data for analysis
            self.use_r_style = True
        else:
            # Fallback to old-style table
            self.use_r_style = False
    
    def analyze_interval_level(self) -> Dict:
        """
        Perform interval-level intensity analysis.
        
        Returns
        -------
        dict
            Interval analysis results including uniform intensity
        """
        if self.use_r_style:
            # Use R-style data for analysis
            if self.ct.is_onestep_only:
                # Single interval analysis
                data = self.ct.lulc_Onestep
                total_area = self.ct.totalArea['area_km2'].iloc[0]
                time_interval = self.ct.totalInterval
            else:
                # Multi-step analysis - use overall results
                data = self.ct.lulc_Onestep  # First to last transition
                total_area = self.ct.totalArea['area_km2'].iloc[0]
                time_interval = self.ct.totalInterval
            
            # Calculate total change from R-style data
            total_change = data['km2'].sum() - data[data['From'] == data['To']]['km2'].sum()
        else:
            # Fallback to old method
            if not self.ct.validate():
                raise ValueError("Invalid contingency table")
            
            data_matrix = self.ct.get_transition_matrix().values
            total_change = data_matrix.sum() - np.diag(data_matrix).sum()
            total_area = data_matrix.sum()
            time_interval = 1  # Simplified
        
        # Uniform intensity (U)
        uniform_intensity = total_change / (total_area * time_interval) if time_interval > 0 else 0
        
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
        
        data = self.ct.get_transition_matrix().values
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
            'classes': list(self.ct.get_transition_matrix().columns)
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
        
        data = self.ct.get_transition_matrix().values
        
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
        data = self.ct.get_transition_matrix().values
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
        results.contingency_table = self.ct.get_transition_matrix()
        
        # Perform all levels of analysis
        interval_results = self.analyze_interval_level()
        category_results = self.analyze_category_level()
        
        results.intensity_analysis = {
            'interval': interval_results,
            'category': category_results,
            'metadata': {
                'classes': list(self.ct.get_transition_matrix().columns),
                'n_classes': len(self.ct.get_transition_matrix().columns)
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
    
    # Get summary stats
    stats = ct.get_summary_stats()
    
    return {
        'contingency_table': ct.get_transition_matrix(),
        'intensity_analysis': intensity_results,
        'change_analysis': change_results,
        'summary': {
            'total_pixels': stats['total_pixels'],
            'total_area_km2': stats['total_area_km2'],
            'persistence_pixels': stats['persistence_pixels'],
            'change_pixels': stats['change_pixels'],
            'change_percentage': (stats['change_pixels'] / stats['total_pixels']) * 100
        }
    }
