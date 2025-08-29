"""
Essential image processing for land use change analysis.

Simplified image processing functions focusing on core functionality
needed for contingency table generation and basic spatial analysis.
"""

import numpy as np
from typing import Tuple, Optional, Dict, List
from scipy import ndimage


def create_contingency_table(raster1: np.ndarray, raster2: np.ndarray, 
                            labels1: Optional[List] = None, 
                            labels2: Optional[List] = None) -> np.ndarray:
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
    np.ndarray
        Contingency table showing transitions between time periods
    """
    # Validate inputs
    if raster1.shape != raster2.shape:
        raise ValueError("Rasters must have the same shape")
    
    # Get unique values
    unique1 = np.unique(raster1)
    unique2 = np.unique(raster2)
    
    # Create contingency table
    contingency = np.zeros((len(unique1), len(unique2)), dtype=int)
    
    for i, val1 in enumerate(unique1):
        for j, val2 in enumerate(unique2):
            mask = (raster1 == val1) & (raster2 == val2)
            contingency[i, j] = np.sum(mask)
    
    return contingency


def calculate_change_map(raster1: np.ndarray, raster2: np.ndarray) -> np.ndarray:
    """
    Calculate binary change map.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period
    raster2 : np.ndarray
        Second time period
        
    Returns
    -------
    np.ndarray
        Binary change map (1 = change, 0 = no change)
    """
    return (raster1 != raster2).astype(int)


def apply_majority_filter(raster: np.ndarray, window_size: int = 3) -> np.ndarray:
    """
    Apply majority filter to remove noise.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
    window_size : int
        Size of the filter window
        
    Returns
    -------
    np.ndarray
        Filtered raster
    """
    def majority_func(values):
        unique, counts = np.unique(values, return_counts=True)
        return unique[np.argmax(counts)]
    
    return ndimage.generic_filter(raster, majority_func, size=window_size)


def calculate_patch_metrics(raster: np.ndarray, class_value: int) -> Dict:
    """
    Calculate basic patch metrics for a specific class.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
    class_value : int
        Class value to analyze
        
    Returns
    -------
    dict
        Patch metrics including count, total area, mean size
    """
    # Create binary mask for the class
    mask = (raster == class_value).astype(int)
    
    # Label connected components
    labeled, num_patches = ndimage.label(mask)
    
    if num_patches == 0:
        return {
            'patch_count': 0,
            'total_area': 0,
            'mean_patch_size': 0,
            'largest_patch_size': 0
        }
    
    # Calculate patch sizes
    patch_sizes = ndimage.sum(mask, labeled, range(1, num_patches + 1))
    
    return {
        'patch_count': num_patches,
        'total_area': int(np.sum(mask)),
        'mean_patch_size': float(np.mean(patch_sizes)),
        'largest_patch_size': int(np.max(patch_sizes))
    }


def resample_raster(raster: np.ndarray, target_shape: Tuple[int, int], 
                   method: str = 'nearest') -> np.ndarray:
    """
    Resample raster to target shape.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
    target_shape : tuple
        Target (height, width)
    method : str
        Resampling method ('nearest', 'linear')
        
    Returns
    -------
    np.ndarray
        Resampled raster
    """
    from scipy.ndimage import zoom
    
    zoom_factors = (target_shape[0] / raster.shape[0], 
                   target_shape[1] / raster.shape[1])
    
    order = 0 if method == 'nearest' else 1
    
    return zoom(raster, zoom_factors, order=order)


def align_rasters(raster1: np.ndarray, raster2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align two rasters to the same shape.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First raster
    raster2 : np.ndarray
        Second raster
        
    Returns
    -------
    tuple
        Aligned rasters with same shape
    """
    if raster1.shape == raster2.shape:
        return raster1, raster2
    
    # Find minimum dimensions
    min_height = min(raster1.shape[0], raster2.shape[0])
    min_width = min(raster1.shape[1], raster2.shape[1])
    
    # Crop to common size
    raster1_aligned = raster1[:min_height, :min_width]
    raster2_aligned = raster2[:min_height, :min_width]
    
    return raster1_aligned, raster2_aligned


def validate_raster(raster: np.ndarray) -> bool:
    """
    Validate raster data.
    
    Parameters
    ----------
    raster : np.ndarray
        Raster to validate
        
    Returns
    -------
    bool
        True if valid, False otherwise
    """
    if raster is None or raster.size == 0:
        return False
    
    if not np.isfinite(raster).all():
        return False
    
    if len(raster.shape) != 2:
        return False
    
    return True


def mask_raster(raster: np.ndarray, mask: np.ndarray, 
               fill_value: int = -1) -> np.ndarray:
    """
    Apply mask to raster.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
    mask : np.ndarray
        Boolean mask (True = keep, False = mask)
    fill_value : int
        Value to use for masked areas
        
    Returns
    -------
    np.ndarray
        Masked raster
    """
    result = raster.copy()
    result[~mask] = fill_value
    return result
