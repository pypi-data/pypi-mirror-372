"""
Block-based processing for large rasters to avoid memory errors.

This module provides memory-efficient alternatives for processing large rasters
by splitting them into blocks and processing incrementally.
"""

import gc
import os
import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
import psutil


@dataclass
class ProcessingConfig:
    """Configuration for block processing."""
    
    block_size: int = 1000  # Block size in pixels
    max_memory_gb: float = 4.0  # Maximum memory usage in GB
    use_multiprocessing: bool = False  # Enable multiprocessing
    n_workers: int = 4  # Number of worker processes
    progress_callback: Optional[callable] = None  # Progress callback function
    temp_dir: Optional[str] = None  # Temporary directory for intermediate files


class MemoryMonitor:
    """Monitor memory usage during processing."""
    
    def __init__(self, max_memory_gb: float = 4.0):
        self.max_memory_gb = max_memory_gb
        self.process = psutil.Process()
    
    def get_memory_usage_gb(self) -> float:
        """Get current memory usage in GB."""
        return self.process.memory_info().rss / (1024**3)
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage exceeds limit."""
        return self.get_memory_usage_gb() > self.max_memory_gb
    
    def warn_if_high_memory(self):
        """Warn if memory usage is high."""
        usage = self.get_memory_usage_gb()
        if usage > self.max_memory_gb * 0.8:
            warnings.warn(f"High memory usage: {usage:.2f} GB (limit: {self.max_memory_gb} GB)")


def calculate_optimal_block_size(raster_shape: Tuple[int, int], 
                                max_memory_gb: float = 4.0,
                                dtype: np.dtype = np.int32,
                                safety_factor: float = 0.5) -> int:
    """
    Calculate optimal block size based on available memory.
    
    Parameters
    ----------
    raster_shape : Tuple[int, int]
        Shape of the raster (height, width)
    max_memory_gb : float
        Maximum memory to use in GB
    dtype : np.dtype
        Data type of the raster
    safety_factor : float
        Safety factor to apply (0.5 = use 50% of available memory)
    
    Returns
    -------
    int
        Optimal block size in pixels
    """
    height, width = raster_shape
    bytes_per_pixel = np.dtype(dtype).itemsize
    
    # Calculate memory per pixel for processing (multiple arrays)
    # We need memory for: original raster, blocks, contingency table, etc.
    memory_multiplier = 8  # Conservative estimate for processing overhead
    
    available_memory_bytes = max_memory_gb * (1024**3) * safety_factor
    max_pixels = available_memory_bytes / (bytes_per_pixel * memory_multiplier)
    
    # Calculate block size (square blocks)
    max_block_size = int(np.sqrt(max_pixels))
    
    # Ensure block size doesn't exceed raster dimensions
    max_block_size = min(max_block_size, height, width)
    
    # Ensure minimum block size
    max_block_size = max(max_block_size, 100)
    
    return max_block_size


def create_block_indices(raster_shape: Tuple[int, int], 
                        block_size: int) -> List[Tuple[slice, slice]]:
    """
    Create list of slice indices for block processing.
    
    Parameters
    ----------
    raster_shape : Tuple[int, int]
        Shape of the raster (height, width)
    block_size : int
        Size of each block in pixels
    
    Returns
    -------
    List[Tuple[slice, slice]]
        List of (row_slice, col_slice) tuples for each block
    """
    height, width = raster_shape
    blocks = []
    
    for row_start in range(0, height, block_size):
        for col_start in range(0, width, block_size):
            row_end = min(row_start + block_size, height)
            col_end = min(col_start + block_size, width)
            
            row_slice = slice(row_start, row_end)
            col_slice = slice(col_start, col_end)
            
            blocks.append((row_slice, col_slice))
    
    return blocks


def process_block_pair(block_from: np.ndarray, 
                      block_to: np.ndarray) -> pd.DataFrame:
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
    # Flatten arrays
    flat_from = block_from.flatten()
    flat_to = block_to.flatten()
    
    # Get unique classes
    classes_from = set(np.unique(flat_from))
    classes_to = set(np.unique(flat_to))
    all_classes = sorted(classes_from | classes_to)
    
    # Create contingency table for this block
    contingency = pd.DataFrame(0, index=all_classes, columns=all_classes)
    
    # Count transitions
    for from_val in classes_from:
        mask_from = flat_from == from_val
        to_vals, counts = np.unique(flat_to[mask_from], return_counts=True)
        
        for to_val, count in zip(to_vals, counts):
            contingency.loc[from_val, to_val] = count
    
    return contingency


def merge_contingency_tables(tables: List[pd.DataFrame]) -> pd.DataFrame:
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
    if not tables:
        return pd.DataFrame()
    
    # Get all unique classes across all tables
    all_classes = set()
    for table in tables:
        all_classes.update(table.index)
        all_classes.update(table.columns)
    
    all_classes = sorted(list(all_classes))
    
    # Create combined table
    combined = pd.DataFrame(0, index=all_classes, columns=all_classes)
    
    # Sum all tables
    for table in tables:
        for idx in table.index:
            for col in table.columns:
                if idx in combined.index and col in combined.columns:
                    combined.loc[idx, col] += table.loc[idx, col]
    
    return combined


def create_contingency_table_blocked(raster_from: np.ndarray,
                                   raster_to: np.ndarray,
                                   config: ProcessingConfig = None) -> pd.DataFrame:
    """
    Create contingency table using block processing for large rasters.
    
    Parameters
    ----------
    raster_from : np.ndarray
        Source raster
    raster_to : np.ndarray
        Target raster
    config : ProcessingConfig, optional
        Processing configuration
    
    Returns
    -------
    pd.DataFrame
        Contingency table
    """
    if config is None:
        config = ProcessingConfig()
    
    # Setup memory monitoring
    monitor = MemoryMonitor(config.max_memory_gb)
    
    # Calculate optimal block size if not specified
    if config.block_size == "auto":
        config.block_size = calculate_optimal_block_size(
            raster_from.shape, config.max_memory_gb
        )
    
    print(f"Processing {raster_from.shape} raster with block size: {config.block_size}")
    
    # Create block indices
    blocks = create_block_indices(raster_from.shape, config.block_size)
    total_blocks = len(blocks)
    
    print(f"Total blocks to process: {total_blocks}")
    
    # Process blocks
    contingency_tables = []
    
    if config.use_multiprocessing and total_blocks > 4:
        # Use multiprocessing for large number of blocks
        contingency_tables = _process_blocks_parallel(
            raster_from, raster_to, blocks, config, monitor
        )
    else:
        # Use sequential processing
        contingency_tables = _process_blocks_sequential(
            raster_from, raster_to, blocks, config, monitor
        )
    
    # Merge all contingency tables
    print("Merging contingency tables...")
    final_contingency = merge_contingency_tables(contingency_tables)
    
    # Clean up memory
    gc.collect()
    
    print(f"Processing complete. Final memory usage: {monitor.get_memory_usage_gb():.2f} GB")
    
    return final_contingency


def _process_blocks_sequential(raster_from: np.ndarray,
                             raster_to: np.ndarray,
                             blocks: List[Tuple[slice, slice]],
                             config: ProcessingConfig,
                             monitor: MemoryMonitor) -> List[pd.DataFrame]:
    """Process blocks sequentially."""
    contingency_tables = []
    
    for i, (row_slice, col_slice) in enumerate(blocks):
        # Extract blocks
        block_from = raster_from[row_slice, col_slice]
        block_to = raster_to[row_slice, col_slice]
        
        # Process block
        contingency = process_block_pair(block_from, block_to)
        contingency_tables.append(contingency)
        
        # Progress reporting
        if config.progress_callback:
            config.progress_callback(i + 1, len(blocks))
        elif (i + 1) % max(1, len(blocks) // 10) == 0:
            progress = (i + 1) / len(blocks) * 100
            print(f"Progress: {progress:.1f}% ({i + 1}/{len(blocks)} blocks)")
        
        # Memory check
        monitor.warn_if_high_memory()
        
        # Force garbage collection periodically
        if (i + 1) % 50 == 0:
            gc.collect()
    
    return contingency_tables


def _process_blocks_parallel(raster_from: np.ndarray,
                           raster_to: np.ndarray,
                           blocks: List[Tuple[slice, slice]],
                           config: ProcessingConfig,
                           monitor: MemoryMonitor) -> List[pd.DataFrame]:
    """Process blocks in parallel."""
    print(f"Using parallel processing with {config.n_workers} workers")
    
    def process_block_wrapper(args):
        row_slice, col_slice = args
        block_from = raster_from[row_slice, col_slice]
        block_to = raster_to[row_slice, col_slice]
        return process_block_pair(block_from, block_to)
    
    contingency_tables = []
    
    # Process in batches to avoid memory issues
    batch_size = config.n_workers * 2
    
    for i in range(0, len(blocks), batch_size):
        batch_blocks = blocks[i:i + batch_size]
        
        with ProcessPoolExecutor(max_workers=config.n_workers) as executor:
            batch_results = list(executor.map(process_block_wrapper, batch_blocks))
        
        contingency_tables.extend(batch_results)
        
        # Progress reporting
        processed = min(i + batch_size, len(blocks))
        progress = processed / len(blocks) * 100
        print(f"Progress: {progress:.1f}% ({processed}/{len(blocks)} blocks)")
        
        # Memory check
        monitor.warn_if_high_memory()
        gc.collect()
    
    return contingency_tables


def estimate_processing_time(raster_shape: Tuple[int, int],
                           block_size: int,
                           pixels_per_second: float = 1e6) -> float:
    """
    Estimate processing time for block processing.
    
    Parameters
    ----------
    raster_shape : Tuple[int, int]
        Shape of the raster
    block_size : int
        Block size in pixels
    pixels_per_second : float
        Estimated processing speed in pixels per second
    
    Returns
    -------
    float
        Estimated processing time in seconds
    """
    total_pixels = raster_shape[0] * raster_shape[1]
    return total_pixels / pixels_per_second


def get_memory_requirements(raster_shape: Tuple[int, int],
                          dtype: np.dtype = np.int32) -> Dict[str, float]:
    """
    Get memory requirements for different processing approaches.
    
    Parameters
    ----------
    raster_shape : Tuple[int, int]
        Shape of the raster
    dtype : np.dtype
        Data type of the raster
    
    Returns
    -------
    Dict[str, float]
        Memory requirements in GB for different approaches
    """
    height, width = raster_shape
    total_pixels = height * width
    bytes_per_pixel = np.dtype(dtype).itemsize
    
    # Memory for single raster
    single_raster_gb = (total_pixels * bytes_per_pixel) / (1024**3)
    
    # Memory for full processing (multiple arrays, contingency table, etc.)
    full_processing_gb = single_raster_gb * 10  # Conservative estimate
    
    return {
        'single_raster_gb': single_raster_gb,
        'two_rasters_gb': single_raster_gb * 2,
        'full_processing_gb': full_processing_gb,
        'recommended_ram_gb': full_processing_gb * 1.5
    }
