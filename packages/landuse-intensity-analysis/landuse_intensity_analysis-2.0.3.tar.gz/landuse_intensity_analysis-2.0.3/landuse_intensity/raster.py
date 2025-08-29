"""
Simple raster data handling for land use change analysis.

Essential functions for reading and processing raster data without
complex dependencies.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, Dict, List
from pathlib import Path

# Optional imports
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


def read_raster(file_path: Union[str, Path]) -> Tuple[np.ndarray, Dict]:
    """
    Read raster file and return data with metadata.
    
    Parameters
    ----------
    file_path : str or Path
        Path to raster file
        
    Returns
    -------
    tuple
        (data_array, metadata_dict) where metadata contains
        transform, crs, and other spatial information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Raster file not found: {file_path}")
    
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for reading raster files. Install with: pip install rasterio")
    
    with rasterio.open(file_path) as src:
        data = src.read(1)  # Read first band
        metadata = {
            'transform': src.transform,
            'crs': src.crs,
            'width': src.width,
            'height': src.height,
            'count': src.count,
            'dtype': src.dtype,
            'nodata': src.nodata
        }
    
    return data, metadata


def write_raster(data: np.ndarray, file_path: Union[str, Path], 
                metadata: Dict, **kwargs) -> None:
    """
    Write raster data to file.
    
    Parameters
    ----------
    data : np.ndarray
        Raster data to write
    file_path : str or Path
        Output file path
    metadata : dict
        Metadata dictionary with spatial information
    **kwargs
        Additional rasterio write parameters
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for writing raster files. Install with: pip install rasterio")
    
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with rasterio.open(
        file_path,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs=metadata.get('crs'),
        transform=metadata.get('transform'),
        nodata=metadata.get('nodata'),
        **kwargs
    ) as dst:
        dst.write(data, 1)


def raster_to_contingency_table(raster1: np.ndarray, raster2: np.ndarray,
                               labels1: Optional[List] = None,
                               labels2: Optional[List] = None) -> pd.DataFrame:
    """
    Create contingency table from two raster arrays.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period raster
    raster2 : np.ndarray
        Second time period raster  
    labels1 : list, optional
        Class labels for raster1
    labels2 : list, optional
        Class labels for raster2
        
    Returns
    -------
    pd.DataFrame
        Contingency table as DataFrame
    """
    if raster1.shape != raster2.shape:
        raise ValueError("Rasters must have the same shape")
    
    # Get unique values
    unique1 = np.unique(raster1[~np.isnan(raster1)])
    unique2 = np.unique(raster2[~np.isnan(raster2)])
    
    # Use provided labels or default to unique values
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
    return df


def load_demo_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate demo raster data for testing.
    
    Returns
    -------
    tuple
        (raster_t1, raster_t2) - Two time periods of demo data
    """
    np.random.seed(42)
    
    # Create 50x50 demo rasters
    size = 50
    
    # Time 1: Random pattern with 4 classes
    raster_t1 = np.random.choice([1, 2, 3, 4], size=(size, size), p=[0.4, 0.3, 0.2, 0.1])
    
    # Time 2: Modified version with some changes
    raster_t2 = raster_t1.copy()
    
    # Apply some random changes (10% of pixels)
    change_mask = np.random.random((size, size)) < 0.1
    raster_t2[change_mask] = np.random.choice([1, 2, 3, 4], size=change_mask.sum())
    
    return raster_t1, raster_t2


def raster_summary(raster: np.ndarray) -> Dict:
    """
    Calculate summary statistics for a raster.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
        
    Returns
    -------
    dict
        Summary statistics
    """
    valid_data = raster[~np.isnan(raster)]
    
    if len(valid_data) == 0:
        return {
            'min': np.nan,
            'max': np.nan,
            'mean': np.nan,
            'std': np.nan,
            'unique_values': [],
            'total_pixels': raster.size,
            'valid_pixels': 0,
            'nodata_pixels': raster.size
        }
    
    unique_vals, counts = np.unique(valid_data, return_counts=True)
    
    return {
        'min': float(np.min(valid_data)),
        'max': float(np.max(valid_data)),
        'mean': float(np.mean(valid_data)),
        'std': float(np.std(valid_data)),
        'unique_values': unique_vals.tolist(),
        'class_counts': dict(zip(unique_vals.tolist(), counts.tolist())),
        'total_pixels': raster.size,
        'valid_pixels': len(valid_data),
        'nodata_pixels': raster.size - len(valid_data)
    }


def align_rasters(raster1: np.ndarray, raster2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align two rasters to have the same dimensions.
    
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


def reclassify_raster(raster: np.ndarray, reclass_dict: Dict) -> np.ndarray:
    """
    Reclassify raster values.
    
    Parameters
    ----------
    raster : np.ndarray
        Input raster
    reclass_dict : dict
        Dictionary mapping old values to new values
        
    Returns
    -------
    np.ndarray
        Reclassified raster
    """
    result = raster.copy()
    
    for old_val, new_val in reclass_dict.items():
        result[raster == old_val] = new_val
    
    return result
