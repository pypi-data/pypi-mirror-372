"""
Essential utility functions for land use intensity analysis.

Simplified and modernized utility functions focusing on core functionality.
"""

import numpy as np
import pandas as pd
import re
import os
from typing import Union, Dict, List, Tuple


def demo_landscape(size: int = 100, 
                   classes: List[int] = None, 
                   fractions: List[float] = None) -> np.ndarray:
    """
    Generate demo landscape data for testing and examples.
    
    Parameters
    ----------
    size : int, default 100
        Size of the square landscape (size x size)
    classes : list of int, optional
        Land use classes to use (default: [1, 2, 3, 4])
    fractions : list of float, optional
        Fractions for each class (default: [0.4, 0.3, 0.2, 0.1])
    
    Returns
    -------
    np.ndarray
        Generated landscape array
    """
    if classes is None:
        classes = [1, 2, 3, 4]
    if fractions is None:
        fractions = [0.4, 0.3, 0.2, 0.1]
    
    # Ensure fractions sum to 1
    fractions = np.array(fractions)
    fractions = fractions / fractions.sum()
    
    # Generate landscape
    landscape = np.random.choice(classes, size=(size, size), p=fractions)
    
    return landscape


def demo_landscape_pair() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate pair of demo landscapes for testing transitions.
    
    Returns
    -------
    tuple
        (landscape_t1, landscape_t2) - Two time periods of synthetic land use data
    """
    np.random.seed(42)
    
    # Time 1: Simple pattern
    landscape_t1 = demo_landscape(100, [1, 2, 3, 4], [0.4, 0.3, 0.2, 0.1])
    
    # Time 2: Some changes from t1
    landscape_t2 = landscape_t1.copy()
    
    # Simulate some transitions
    change_mask = np.random.random((100, 100)) < 0.1  # 10% change
    landscape_t2[change_mask] = np.random.choice([1, 2, 3, 4], size=change_mask.sum())
    
    return landscape_t1, landscape_t2


def validate_data(data: Union[np.ndarray, pd.DataFrame]) -> bool:
    """
    Validate contingency table or raster data.
    
    Parameters
    ----------
    data : array-like
        Data to validate
        
    Returns
    -------
    bool
        True if data is valid, False otherwise
    """
    if data is None:
        return False
    
    if isinstance(data, pd.DataFrame):
        data_array = data.values
    else:
        data_array = np.asarray(data)
    
    # Check for negative values
    if (data_array < 0).any():
        return False
    
    # Check for NaN or infinite values
    if not np.isfinite(data_array).all():
        return False
    
    return True


def calculate_area_matrix(contingency_table: pd.DataFrame, 
                         pixel_area: float = 1.0) -> pd.DataFrame:
    """
    Convert contingency table from pixel counts to area units.
    
    Parameters
    ----------
    contingency_table : pd.DataFrame
        Contingency table in pixel counts
    pixel_area : float
        Area of each pixel in desired units (e.g., hectares, km²)
        
    Returns
    -------
    pd.DataFrame
        Contingency table in area units
    """
    return contingency_table * pixel_area


def get_change_summary(contingency_table: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics from contingency table.
    
    Parameters
    ----------
    contingency_table : pd.DataFrame
        Transition matrix
        
    Returns
    -------
    dict
        Summary statistics including persistence, change, gains, losses
    """
    data = contingency_table.values
    
    # Total area
    total_area = data.sum()
    
    # Persistence (diagonal)
    persistence = np.diag(data).sum()
    
    # Total change
    total_change = total_area - persistence
    
    # Per-class statistics
    gains = data.sum(axis=0) - np.diag(data)  # Column sums minus diagonal
    losses = data.sum(axis=1) - np.diag(data)  # Row sums minus diagonal
    net_change = gains - losses
    
    return {
        'total_area': total_area,
        'persistence': persistence,
        'total_change': total_change,
        'change_percent': (total_change / total_area) * 100,
        'gains': gains.tolist(),
        'losses': losses.tolist(),
        'net_change': net_change.tolist(),
        'classes': list(contingency_table.columns)
    }


def format_area_label(area: float, units: str = "pixels") -> str:
    """
    Format area value for display.
    
    Parameters
    ----------
    area : float
        Area value
    units : str
        Units (pixels, hectares, km², etc.)
        
    Returns
    -------
    str
        Formatted area string
    """
    if area >= 1e6:
        return f"{area/1e6:.2f}M {units}"
    elif area >= 1e3:
        return f"{area/1e3:.2f}K {units}"
    else:
        return f"{area:.1f} {units}"


def create_transition_names(from_classes: List, to_classes: List) -> List[str]:
    """
    Create human-readable transition names.
    
    Parameters
    ----------
    from_classes : list
        Source class names
    to_classes : list
        Target class names
        
    Returns
    -------
    list
        Transition names in format "From → To"
    """
    transitions = []
    for from_class in from_classes:
        for to_class in to_classes:
            if from_class != to_class:  # Skip persistence
                transitions.append(f"{from_class} → {to_class}")
    return transitions


def extract_time_labels_from_filenames(filenames: List[str], 
                                     label_position: Union[int, str] = "last", 
                                     separator: str = "_") -> List[str]:
    """
    Extract time labels from raster filenames based on position.
    
    Useful for automatically extracting years or time periods from filenames
    like 'landuse_1990.tif', 'region_data_2000_v1.tif', etc.
    
    Parameters
    ----------
    filenames : List[str]
        List of filenames or file paths
    label_position : int or str, default "last"
        Position of the time label in the filename:
        - "last": Last part before extension
        - "first": First part of filename
        - int: Specific position (0-based index) after splitting by separator
    separator : str, default "_"
        Character to split filename parts
        
    Returns
    -------
    List[str]
        Extracted time labels
        
    Examples
    --------
    >>> files = ['landuse_1990.tif', 'landuse_2000.tif', 'landuse_2010.tif']
    >>> extract_time_labels_from_filenames(files)
    ['1990', '2000', '2010']
    
    >>> files = ['2000_region_data.tif', '2010_region_data.tif']
    >>> extract_time_labels_from_filenames(files, label_position="first")
    ['2000', '2010']
    
    >>> files = ['data_1990_final.tif', 'data_2000_final.tif']
    >>> extract_time_labels_from_filenames(files, label_position=1)
    ['1990', '2000']
    """
    time_labels = []
    
    for filename in filenames:
        # Get basename without path
        basename = os.path.basename(filename)
        
        # Remove extension
        name_without_ext = os.path.splitext(basename)[0]
        
        # Split by separator
        parts = name_without_ext.split(separator)
        
        if len(parts) == 1:
            # No separator found, use the whole name
            label = name_without_ext
        else:
            # Extract based on position
            if label_position == "last":
                label = parts[-1]
            elif label_position == "first":
                label = parts[0]
            elif isinstance(label_position, int):
                if 0 <= label_position < len(parts):
                    label = parts[label_position]
                else:
                    # Fallback to last if position is out of range
                    label = parts[-1]
            else:
                # Fallback to last
                label = parts[-1]
        
        time_labels.append(label)
    
    return time_labels


def extract_years_from_text(text: str) -> List[str]:
    """
    Extract 4-digit years from text using regex.
    
    Parameters
    ----------
    text : str
        Text containing years
        
    Returns
    -------
    List[str]
        List of found years
        
    Examples
    --------
    >>> extract_years_from_text("landuse_1990_2000_final")
    ['1990', '2000']
    
    >>> extract_years_from_text("data_from_2010_to_2020")
    ['2010', '2020']
    """
    # Find all 4-digit numbers that look like years (1900-2099)
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    return years


def smart_extract_time_labels(filenames: List[str]) -> List[str]:
    """
    Intelligently extract time labels from filenames.
    
    Tries multiple strategies to extract meaningful time labels:
    1. Look for 4-digit years anywhere in filename
    2. Use last part of filename (split by underscore)
    3. Use filename without extension as fallback
    
    Parameters
    ----------
    filenames : List[str]
        List of filenames
        
    Returns
    -------
    List[str]
        Extracted time labels
        
    Examples
    --------
    >>> files = ['region_1990.tif', 'region_2000.tif', 'region_2010.tif']
    >>> smart_extract_time_labels(files)
    ['1990', '2000', '2010']
    
    >>> files = ['data_T1.tif', 'data_T2.tif']
    >>> smart_extract_time_labels(files)
    ['T1', 'T2']
    """
    time_labels = []
    
    for filename in filenames:
        basename = os.path.basename(filename)
        name_without_ext = os.path.splitext(basename)[0]
        
        # Strategy 1: Look for 4-digit years
        years = extract_years_from_text(name_without_ext)
        if years:
            # Use the first found year
            time_labels.append(years[0])
            continue
        
        # Strategy 2: Try last part after underscore
        parts = name_without_ext.split('_')
        if len(parts) > 1:
            last_part = parts[-1]
            # Check if it looks like a time label (contains digits)
            if re.search(r'\d', last_part):
                time_labels.append(last_part)
                continue
        
        # Strategy 3: Fallback to whole filename without extension
        time_labels.append(name_without_ext)
    
    return time_labels
