"""
Essential utility functions for land use intensity analysis.

Simplified and modernized utility functions focusing on core functionality.
"""

import numpy as np
import pandas as pd
from typing import Union, Dict, List, Tuple


def demo_landscape() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate demo landscape data for testing and examples.
    
    Returns
    -------
    tuple
        (landscape_t1, landscape_t2) - Two time periods of synthetic land use data
    """
    np.random.seed(42)
    
    # Create simple 100x100 landscape
    size = 100
    
    # Time 1: Simple pattern
    landscape_t1 = np.random.choice([1, 2, 3, 4], size=(size, size), p=[0.4, 0.3, 0.2, 0.1])
    
    # Time 2: Some changes from t1
    landscape_t2 = landscape_t1.copy()
    
    # Simulate some transitions
    change_mask = np.random.random((size, size)) < 0.1  # 10% change
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
