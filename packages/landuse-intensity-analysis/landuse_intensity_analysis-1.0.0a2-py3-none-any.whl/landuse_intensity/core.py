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
    Contingency table for land use change analysis.
    
    This class provides functionality to create and analyze contingency tables
    from raster data, implementing land use change analysis methodology.
    Returns lulc_Multistep, lulc_Onestep, tb_legend, totalArea, totalInterval.
    """
    
    def __init__(self, rasters: List[np.ndarray], time_labels: List[str] = None, 
                 pixel_resolution: float = 30.0, class_names: Dict[int, str] = None,
                 use_block_processing: bool = None, block_size: int = 1000,
                 max_memory_gb: float = 4.0, use_multiprocessing: bool = False,
                 exclude_classes: List[int] = None):
        """
        Initialize ContingencyTable with intelligent onestep/multistep detection.
        
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
        pixel_resolution : float, default 30.0
            Pixel resolution in meters for area calculations
        class_names : Dict[int, str], optional
            Mapping of class values to descriptive names
        use_block_processing : bool, optional
            Force block processing for large rasters
            If None, automatically determined based on raster size
        block_size : int, default 1000
            Size of processing blocks in pixels (for large rasters)
        max_memory_gb : float, default 4.0
            Maximum memory usage in GB for processing
        use_multiprocessing : bool, default False
            Enable multiprocessing for block processing
        exclude_classes : List[int], optional
            List of class values to exclude from analysis
            (e.g., [0, 255] to exclude no-data and mask values)
        pixel_resolution : float
            Pixel resolution in meters (default: 30)
        class_names : Dict[int, str], optional
            Mapping of class values to names
        """
        # Validation
        if len(rasters) < 2:
            raise ValueError('ContingencyTable needs at least 2 rasters')
        
        # Store configuration
        self.rasters = rasters
        self.n_rasters = len(rasters)
        self.time_labels = time_labels
        self.pixel_resolution = pixel_resolution  
        self.class_names = class_names or {}
        self.exclude_classes = set(exclude_classes or [])
        
        # Remove excluded classes from class_names if they exist
        if self.exclude_classes and self.class_names:
            self.class_names = {k: v for k, v in self.class_names.items() 
                              if k not in self.exclude_classes}
        
        # Memory and processing configuration
        self.use_block_processing = use_block_processing
        self.block_size = block_size
        self.max_memory_gb = max_memory_gb
        self.use_multiprocessing = use_multiprocessing
        
        # Auto-detect if block processing is needed
        if self.use_block_processing is None:
            self.use_block_processing = self._should_use_block_processing()
        
        # Generate time labels if not provided
        if self.time_labels is None:
            self.time_labels = [str(i) for i in range(self.n_rasters)]
        
        # Validate inputs
        if len(self.time_labels) != self.n_rasters:
            raise ValueError(f"Number of time labels ({len(self.time_labels)}) must match number of rasters ({self.n_rasters})")
        
        # Check raster shapes
        reference_shape = self.rasters[0].shape
        for i, raster in enumerate(self.rasters[1:], 1):
            if raster.shape != reference_shape:
                raise ValueError(f"All rasters must have the same shape. Raster {i} has shape {raster.shape}, expected {reference_shape}")
        
        # Display processing information
        if self.use_block_processing:
            total_pixels = self.rasters[0].size
            print(f"🔄 Large raster detected ({total_pixels:,} pixels)")
            print(f"📦 Using block processing (block size: {self.block_size})")
            if self.use_multiprocessing:
                print("⚡ Multiprocessing enabled")
            if self.exclude_classes:
                print(f"🚫 Excluding classes: {sorted(list(self.exclude_classes))}")
            estimated_memory = self._estimate_memory_usage()
            print(f"💾 Estimated memory usage: {estimated_memory:.2f} GB")
        elif self.exclude_classes:
            print(f"🚫 Excluding classes: {sorted(list(self.exclude_classes))}")
        
        # Initialize analysis results  
        self.lulc_Multistep = None
        self.lulc_Onestep = None 
        self.tb_legend = None
        self.totalArea = None
        self.totalInterval = None
        
        # Generate analysis
        self._generate_analysis()
    
    def _should_use_block_processing(self) -> bool:
        """
        Determine if block processing should be used based on raster size.
        
        Returns
        -------
        bool
            True if block processing is recommended
        """
        # Get raster size in pixels
        total_pixels = self.rasters[0].size
        
        # Estimate memory requirements (conservative estimate)
        bytes_per_pixel = 4  # int32
        estimated_memory_gb = (total_pixels * bytes_per_pixel * 8) / (1024**3)  # 8x multiplier for processing overhead
        
        # Use block processing if estimated memory > 70% of limit
        return estimated_memory_gb > (self.max_memory_gb * 0.7)
    
    def _estimate_memory_usage(self) -> float:
        """
        Estimate memory usage for processing.
        
        Returns
        -------
        float
            Estimated memory usage in GB
        """
        total_pixels = self.rasters[0].size
        bytes_per_pixel = 4  # Assuming int32
        # Conservative estimate: original rasters + working memory + contingency tables
        return (total_pixels * bytes_per_pixel * 10) / (1024**3)
    
    def _create_contingency_table_memory_efficient(self, raster_from: np.ndarray, 
                                                  raster_to: np.ndarray) -> pd.DataFrame:
        """
        Create contingency table with memory-efficient approach.
        
        Parameters
        ----------
        raster_from : np.ndarray
            Source raster
        raster_to : np.ndarray
            Target raster
        
        Returns
        -------
        pd.DataFrame
            Contingency table
        """
        if self.use_block_processing:
            return self._create_contingency_table_blocked(raster_from, raster_to)
        else:
            return self._create_simple_contingency_table(raster_from, raster_to)
    
    def _create_contingency_table_blocked(self, raster_from: np.ndarray, 
                                        raster_to: np.ndarray) -> pd.DataFrame:
        """
        Create contingency table using block processing for large rasters.
        
        Parameters
        ----------
        raster_from : np.ndarray
            Source raster
        raster_to : np.ndarray
            Target raster
        
        Returns
        -------
        pd.DataFrame
            Contingency table
        """
        import gc
        from concurrent.futures import ThreadPoolExecutor
        
        print(f"📦 Processing {raster_from.shape} raster in blocks...")
        
        # Calculate optimal block size if needed
        if self.block_size == "auto":
            total_pixels = raster_from.size
            estimated_memory_gb = (total_pixels * 4 * 8) / (1024**3)
            optimal_pixels = int((self.max_memory_gb * 0.5 * 1024**3) / (4 * 8))
            self.block_size = int(np.sqrt(optimal_pixels))
            self.block_size = max(self.block_size, 100)  # Minimum block size
            print(f"🎯 Auto-calculated block size: {self.block_size}")
        
        height, width = raster_from.shape
        blocks = []
        
        # Create block indices
        for row_start in range(0, height, self.block_size):
            for col_start in range(0, width, self.block_size):
                row_end = min(row_start + self.block_size, height)
                col_end = min(col_start + self.block_size, width)
                blocks.append((slice(row_start, row_end), slice(col_start, col_end)))
        
        print(f"📊 Processing {len(blocks)} blocks...")
        
        # Process blocks
        contingency_tables = []
        
        def process_single_block(block_idx):
            row_slice, col_slice = blocks[block_idx]
            block_from = raster_from[row_slice, col_slice]
            block_to = raster_to[row_slice, col_slice]
            return self._process_block_pair(block_from, block_to)
        
        if self.use_multiprocessing and len(blocks) > 4:
            # Use threading for I/O bound operations
            print(f"⚡ Using parallel processing...")
            with ThreadPoolExecutor(max_workers=4) as executor:
                contingency_tables = list(executor.map(process_single_block, range(len(blocks))))
        else:
            # Sequential processing
            for i in range(len(blocks)):
                contingency_tables.append(process_single_block(i))
                
                # Progress reporting
                if (i + 1) % max(1, len(blocks) // 10) == 0:
                    progress = (i + 1) / len(blocks) * 100
                    print(f"⏳ Progress: {progress:.1f}% ({i + 1}/{len(blocks)} blocks)")
                
                # Periodic garbage collection
                if (i + 1) % 50 == 0:
                    gc.collect()
        
        # Merge all contingency tables
        print("🔄 Merging contingency tables...")
        final_contingency = self._merge_contingency_tables(contingency_tables)
        
        # Clean up
        gc.collect()
        print("✅ Block processing complete!")
        
        return final_contingency
    
    def _process_block_pair(self, block_from: np.ndarray, block_to: np.ndarray) -> pd.DataFrame:
        """
        Process a single block pair to create contingency table.
        
        Parameters
        ----------
        block_from : np.ndarray
            Source block
        block_to : np.ndarray
            Target block
        
        Returns
        -------
        pd.DataFrame
            Contingency table for this block
        """
        # Flatten arrays and remove invalid values
        flat_from = block_from.flatten()
        flat_to = block_to.flatten()
        
        # Remove no-data values and excluded classes
        valid_mask = (flat_from != -9999) & (flat_to != -9999) & (flat_from >= 0) & (flat_to >= 0)
        
        # Apply class exclusion
        if self.exclude_classes:
            for exclude_class in self.exclude_classes:
                valid_mask = valid_mask & (flat_from != exclude_class) & (flat_to != exclude_class)
        
        flat_from = flat_from[valid_mask]
        flat_to = flat_to[valid_mask]
        
        if len(flat_from) == 0:
            return pd.DataFrame()  # Empty block
        
        # Get unique classes efficiently
        classes_from = np.unique(flat_from)
        classes_to = np.unique(flat_to)
        all_classes = np.unique(np.concatenate([classes_from, classes_to]))
        
        # Create contingency table
        contingency = pd.DataFrame(0, index=all_classes, columns=all_classes, dtype=np.int64)
        
        # Optimized counting using np.unique
        for from_val in classes_from:
            mask = flat_from == from_val
            to_vals, counts = np.unique(flat_to[mask], return_counts=True)
            for to_val, count in zip(to_vals, counts):
                if to_val in contingency.columns:
                    contingency.loc[from_val, to_val] = count
        
        return contingency
    
    def _merge_contingency_tables(self, tables: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge multiple contingency tables into one.
        
        Parameters
        ----------
        tables : List[pd.DataFrame]
            List of contingency tables to merge
        
        Returns
        -------
        pd.DataFrame
            Combined contingency table
        """
        # Remove empty tables
        tables = [t for t in tables if not t.empty]
        
        if not tables:
            return pd.DataFrame()
        
        # Get all unique classes
        all_classes = set()
        for table in tables:
            all_classes.update(table.index)
            all_classes.update(table.columns)
        
        all_classes = sorted(list(all_classes))
        
        # Create combined table
        combined = pd.DataFrame(0, index=all_classes, columns=all_classes, dtype=np.int64)
        
        # Sum all tables efficiently
        for table in tables:
            # Use pandas addition with fill_value=0 for missing indices
            for idx in table.index:
                for col in table.columns:
                    if idx in combined.index and col in combined.columns:
                        combined.loc[idx, col] += table.loc[idx, col]
        
        return combined
    
    def _create_transition_data(self, raster_from, raster_to, year_from, year_to):
        """Create transition data for a pair of rasters following contingencyTable format."""
        
        # Use memory-efficient contingency table creation
        contingency_table = self._create_contingency_table_memory_efficient(raster_from, raster_to)
        
        if contingency_table.empty:
            return []
        
        transitions = []
        
        # Calculate interval (handle non-numeric labels)
        try:
            interval = int(year_to) - int(year_from)
            year_from_int = int(year_from)
            year_to_int = int(year_to)
        except ValueError:
            # If labels are not numeric, use position-based interval
            interval = 1
            year_from_int = int(year_from) if year_from.isdigit() else 0
            year_to_int = int(year_to) if year_to.isdigit() else 1
        
        # Convert contingency table to transition data format
        for idx_from, class_from in enumerate(contingency_table.index):
            for idx_to, class_to in enumerate(contingency_table.columns):
                qt_pixel = contingency_table.loc[class_from, class_to]
                
                if qt_pixel > 0:  # Only include non-zero transitions
                    # Calculate area in km²
                    km2 = qt_pixel * (self.pixel_resolution ** 2) / 1e6
                    
                    transition = {
                        'Period': f"{year_from}-{year_to}",
                        'From': int(class_from),
                        'To': int(class_to),
                        'km2': km2,
                        'QtPixel': int(qt_pixel),
                        'Interval': interval,
                        'yearFrom': year_from_int,
                        'yearTo': year_to_int
                    }
                    transitions.append(transition)
        
        return transitions
        return transitions
    
    def _generate_analysis(self):
        """Generate contingency table analysis."""
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
        # This represents the complete change from first to last time period
        onestep_data = self._create_transition_data(
            self.rasters[0], self.rasters[-1],
            self.time_labels[0], self.time_labels[-1]
        )
        
        # 3. Create legend table - usando apenas classes válidas
        all_classes = set()
        for raster in self.rasters:
            classes_in_raster = set(np.unique(raster))
            # Aplicar exclusão
            if self.exclude_classes:
                classes_in_raster = classes_in_raster - self.exclude_classes
            all_classes.update(classes_in_raster)
        all_classes = sorted(list(all_classes))
        
        # Atualizar class_names com as classes válidas
        for class_val in all_classes:
            if class_val not in self.class_names:
                self.class_names[class_val] = f"Class_{class_val}"
        
        # Generate colors (predefined color palette)
        colors = [
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
            
            color = colors[i % len(colors)]
            
            tb_legend_data.append({
                'categoryValue': int(category_value),
                'categoryName': category_name,
                'color': color
            })
        
        # 4. Calculate total area (based on standard methodology)
        area_data = []
        multistep_df = pd.DataFrame(multistep_data) if multistep_data else pd.DataFrame()
        
        if not multistep_df.empty and 'Period' in multistep_df.columns:
            # Group by Period and calculate totals
            area_summary = multistep_df.groupby('Period').agg({
                'km2': 'sum',
                'QtPixel': 'sum'
            }).reset_index()
            
            area_data = area_summary.to_dict('records')
        
        # Get first period for totalArea (standard methodology)
        if area_data:
            total_area = pd.DataFrame([{
                'area_km2': area_data[0]['km2'],
                'QtPixel': area_data[0]['QtPixel']
            }])
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
        """Create simple contingency table for small/medium rasters."""
        # Flatten rasters
        flat_from = raster_from.flatten()
        flat_to = raster_to.flatten()
        
        # Remove invalid values and excluded classes
        valid_mask = (flat_from != -9999) & (flat_to != -9999) & (flat_from >= 0) & (flat_to >= 0)
        
        # Apply class exclusion
        if self.exclude_classes:
            for exclude_class in self.exclude_classes:
                valid_mask = valid_mask & (flat_from != exclude_class) & (flat_to != exclude_class)
        
        flat_from = flat_from[valid_mask]
        flat_to = flat_to[valid_mask]
        
        if len(flat_from) == 0:
            return pd.DataFrame()
        
        # Get unique classes
        classes = sorted(set(flat_from) | set(flat_to))
        
        # Create contingency table
        contingency = pd.DataFrame(0, index=classes, columns=classes, dtype=np.int64)
        
        # Optimized counting
        for from_val in np.unique(flat_from):
            mask = flat_from == from_val
            to_vals, counts = np.unique(flat_to[mask], return_counts=True)
            for to_val, count in zip(to_vals, counts):
                contingency.loc[from_val, to_val] = count
        
        return contingency
        
        # Sort using standard ordering
        if not self.lulc_Multistep.empty:
            self.lulc_Multistep = self.lulc_Multistep.sort_values(['yearFrom', 'From', 'To']).reset_index(drop=True)
        
        if not self.lulc_Onestep.empty:
            self.lulc_Onestep = self.lulc_Onestep.sort_values(['From', 'To']).reset_index(drop=True)
    
    @classmethod
    def from_rasters(cls, rasters: Union[List[np.ndarray], np.ndarray], 
                     raster_to: np.ndarray = None, 
                     time_labels: List[str] = None,
                     pixel_resolution: float = 30.0, 
                     class_names: Dict[int, str] = None,
                     use_block_processing: bool = None,
                     block_size: int = 1000,
                     max_memory_gb: float = 4.0,
                     use_multiprocessing: bool = False,
                     exclude_classes: List[int] = None) -> 'ContingencyTable':
        """
        Create contingency table from rasters with memory optimization and class exclusion.
        
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
        use_block_processing : bool, optional
            Force block processing for large rasters
        block_size : int, default 1000
            Size of processing blocks in pixels
        max_memory_gb : float, default 4.0
            Maximum memory usage in GB
        use_multiprocessing : bool, default False
            Enable multiprocessing for block processing
        exclude_classes : List[int], optional
            List of class values to exclude from analysis
            
        Returns
        -------
        ContingencyTable
            Contingency table instance
            
        Examples
        --------
        # Basic usage
        >>> ct = ContingencyTable.from_rasters([raster1, raster2])
        
        # Large rasters with block processing
        >>> ct = ContingencyTable.from_rasters(rasters, use_block_processing=True,
        ...                                   max_memory_gb=8.0)
        
        # Exclude no-data and mask classes
        >>> ct = ContingencyTable.from_rasters(rasters, exclude_classes=[0, 255])
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
                  pixel_resolution=pixel_resolution, class_names=class_names,
                  use_block_processing=use_block_processing, block_size=block_size,
                  max_memory_gb=max_memory_gb, use_multiprocessing=use_multiprocessing,
                  exclude_classes=exclude_classes)
    
    @classmethod
    def from_files(cls, filenames: List[str], 
                   label_position: Union[int, str] = "smart",
                   separator: str = "_",
                   pixel_resolution: float = 30.0,
                   class_names: Dict[int, str] = None,
                   use_block_processing: bool = None,
                   block_size: int = 1000,
                   max_memory_gb: float = 4.0,
                   use_multiprocessing: bool = False,
                   exclude_classes: List[int] = None) -> 'ContingencyTable':
        """
        Create ContingencyTable from raster files with automatic time label extraction and memory optimization.
        
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
        use_block_processing : bool, optional
            Force block processing for large rasters
        block_size : int, default 1000
            Size of processing blocks in pixels
        max_memory_gb : float, default 4.0
            Maximum memory usage in GB
        use_multiprocessing : bool, default False
            Enable multiprocessing for block processing
            
        Returns
        -------
        ContingencyTable
            Contingency table instance
            
        Examples
        --------
        # Small rasters (automatic processing)
        >>> files = ['landuse_1990.tif', 'landuse_2000.tif', 'landuse_2010.tif']
        >>> ct = ContingencyTable.from_files(files)
        >>> print(ct.time_labels)  # ['1990', '2000', '2010']
        
        # Large rasters (force block processing)
        >>> ct = ContingencyTable.from_files(files, use_block_processing=True, 
        ...                                 block_size=500, max_memory_gb=8.0)
        
        # Very large rasters (with multiprocessing)
        >>> ct = ContingencyTable.from_files(files, use_block_processing=True,
        ...                                 use_multiprocessing=True, max_memory_gb=16.0)
        
        # Exclude no-data and mask classes
        >>> ct = ContingencyTable.from_files(files, exclude_classes=[0, 255])
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
                  pixel_resolution=pixel_resolution, class_names=class_names,
                  use_block_processing=use_block_processing, block_size=block_size,
                  max_memory_gb=max_memory_gb, use_multiprocessing=use_multiprocessing,
                  exclude_classes=exclude_classes)
    
    def validate(self) -> bool:
        """
        Validate contingency table data.
        
        Returns
        -------
        bool
            True if all components are present and valid
        """
        # Check if all components exist
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
        Get summary statistics from contingency table data.
        
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
            'is_onestep_only': self.n_rasters == 2,
            'is_multistep': self.n_rasters > 2
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
        
        # Check for available data format
        if hasattr(contingency_table, 'lulc_Onestep') and not contingency_table.lulc_Onestep.empty:
            # Use available data for analysis
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
            # Use available data for analysis
            if self.ct.get_summary_stats()['is_onestep_only']:
                # Single interval analysis
                data = self.ct.lulc_Onestep
                total_area = self.ct.totalArea['area_km2'].iloc[0]
                time_interval = self.ct.totalInterval
            else:
                # Multi-step analysis - use overall results
                data = self.ct.lulc_Onestep  # First to last transition
                total_area = self.ct.totalArea['area_km2'].iloc[0]
                time_interval = self.ct.totalInterval
            
            # Calculate total change from contingency table data
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
