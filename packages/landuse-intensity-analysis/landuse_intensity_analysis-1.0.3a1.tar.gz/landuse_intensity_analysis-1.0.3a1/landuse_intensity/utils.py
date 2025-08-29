"""
Utility functions for the LandUse-Intensity-Analysis package.

This module provides utility functions based on the Pontius-Aldwaik methodology
for land use change analysis and intensity metrics.

References:
    - Pontius Jr, R. G., & Aldwaik, S. Z. (2012). Errors, plausible range, and
      intensity of land change analysis. Landscape Ecology, 27(5), 633-641.
    - Aldwaik, S. Z., & Pontius Jr, R. G. (2012). Intensity analysis to unify
      measurements of size and stationarity of land changes by interval, category,
      and transition. Landscape and Urban Planning, 106(1), 103-114.
"""

import warnings
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd


def demo_landscape() -> np.ndarray:
    """
    Generate a simple demo landscape for testing purposes.

    Creates a 10x10 grid with 3 land use categories following patterns
    commonly used in Pontius methodology demonstrations.

    Returns:
        np.ndarray: Demo landscape array with values 1, 2, 3 representing
                   different land use categories
    """
    # Create a simple demo landscape
    landscape = np.array(
        [
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 3],
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 3],
            [1, 1, 2, 2, 2, 3, 3, 3, 3, 3],
            [1, 2, 2, 2, 2, 3, 3, 3, 3, 2],
            [2, 2, 2, 2, 3, 3, 3, 3, 2, 2],
            [2, 2, 2, 3, 3, 3, 3, 2, 2, 2],
            [2, 2, 3, 3, 3, 3, 2, 2, 2, 1],
            [2, 3, 3, 3, 3, 2, 2, 2, 1, 1],
            [3, 3, 3, 3, 2, 2, 2, 1, 1, 1],
            [3, 3, 3, 2, 2, 2, 1, 1, 1, 1],
        ]
    )
    return landscape


def validate_contingency_data(
    contingency_table: Union[np.ndarray, pd.DataFrame],
) -> bool:
    """
    Validate contingency table data for Pontius analysis.

    Args:
        contingency_table: Contingency table to validate

    Returns:
        bool: True if validation passes

    Raises:
        ValueError: If validation fails
    """
    if isinstance(contingency_table, pd.DataFrame):
        data = contingency_table.values
    else:
        data = contingency_table

    if not isinstance(data, np.ndarray):
        raise ValueError("Contingency table must be numpy array or pandas DataFrame")

    if data.ndim != 2:
        raise ValueError("Contingency table must be 2D")

    if data.shape[0] != data.shape[1]:
        raise ValueError("Contingency table must be square")

    if np.any(data < 0):
        raise ValueError("Contingency table cannot contain negative values")

    if np.any(np.isnan(data)):
        raise ValueError("Contingency table cannot contain NaN values")

    return True


def format_area_label(area: float, unit: str = "km2") -> str:
    """
    Format area labels for plots and tables.

    Args:
        area: Area value
        unit: Unit string (default: "km2")

    Returns:
        str: Formatted label
    """
    if area >= 1000:
        return f"{area:,.0f} {unit}"
    elif area >= 10:
        return f"{area:.0f} {unit}"
    elif area >= 1:
        return f"{area:.1f} {unit}"
    else:
        return f"{area:.2f} {unit}"


def get_transition_matrix(time1: np.ndarray, time2: np.ndarray) -> pd.DataFrame:
    """
    Create a transition matrix between two time periods.

    Following Pontius methodology for land change analysis, this function
    creates a transition matrix showing changes between categories.

    Args:
        time1: Land use array for first time period
        time2: Land use array for second time period

    Returns:
        pd.DataFrame: Transition matrix with categories as rows and columns

    References:
        Pontius Jr, R. G., & Aldwaik, S. Z. (2012). Errors, plausible range,
        and intensity of land change analysis.
    """
    if time1.shape != time2.shape:
        raise ValueError("Input arrays must have the same shape")

    # Get unique categories
    categories = sorted(np.unique(np.concatenate([time1.flatten(), time2.flatten()])))

    # Create transition matrix
    transition_matrix = pd.DataFrame(0, index=categories, columns=categories)

    # Count transitions
    for i in range(time1.shape[0]):
        for j in range(time1.shape[1]):
            from_cat = time1[i, j]
            to_cat = time2[i, j]
            transition_matrix.loc[from_cat, to_cat] += 1

    return transition_matrix


def calculate_change_metrics(transition_matrix: pd.DataFrame) -> Dict:
    """
    Calculate change metrics from transition matrix.

    Args:
        transition_matrix: Transition matrix between time periods

    Returns:
        Dict: Dictionary with change metrics including total change,
              gains, losses, and net change by category
    """
    total_area = transition_matrix.values.sum()
    diagonal = np.diag(transition_matrix.values)
    row_sums = transition_matrix.sum(axis=1).values
    col_sums = transition_matrix.sum(axis=0).values

    # Calculate metrics
    persistence = diagonal.sum()
    total_change = total_area - persistence
    change_ratio = total_change / total_area if total_area > 0 else 0

    # Per category metrics
    gains = col_sums - diagonal
    losses = row_sums - diagonal
    net_change = gains - losses

    return {
        "total_area": total_area,
        "total_change": total_change,
        "persistence": persistence,
        "change_ratio": change_ratio,
        "gains": pd.Series(gains, index=transition_matrix.columns, name="gains"),
        "losses": pd.Series(losses, index=transition_matrix.index, name="losses"),
        "net_change": pd.Series(
            net_change, index=transition_matrix.index, name="net_change"
        ),
    }


def check_data_consistency(time1: np.ndarray, time2: np.ndarray) -> bool:
    """
    Check data consistency between time periods.

    Args:
        time1: Land use array for first time period
        time2: Land use array for second time period

    Returns:
        bool: True if data is consistent

    Raises:
        ValueError: If data is inconsistent
    """
    if time1.shape != time2.shape:
        raise ValueError("Time periods must have the same shape")

    if time1.dtype != time2.dtype:
        warnings.warn("Time periods have different data types")

    if np.any(np.isnan(time1)) or np.any(np.isnan(time2)):
        raise ValueError("Data cannot contain NaN values")

    if np.any(time1 < 0) or np.any(time2 < 0):
        raise ValueError("Data cannot contain negative values")

    return True


def print_summary_stats(
    transition_matrix: pd.DataFrame, category_names: Optional[Dict] = None
) -> None:
    """
    Print summary statistics from transition matrix.

    Args:
        transition_matrix: Transition matrix
        category_names: Optional mapping of category numbers to names
    """
    metrics = calculate_change_metrics(transition_matrix)

    print("=== LAND USE CHANGE SUMMARY (Pontius Methodology) ===")
    print(f"Total Area: {metrics['total_area']:,.0f} pixels")
    print(
        f"Total Change: {metrics['total_change']:,.0f} pixels ({metrics['change_ratio']:.1%})"
    )
    print(
        f"Persistence: {metrics['persistence']:,.0f} pixels ({(1-metrics['change_ratio']):.1%})"
    )
    print()

    print("=== CATEGORY CHANGES ===")
    for idx in transition_matrix.index:
        name = (
            category_names.get(idx, f"Category {idx}")
            if category_names
            else f"Category {idx}"
        )
        gain = metrics["gains"].loc[idx]
        loss = metrics["losses"].loc[idx]
        net = metrics["net_change"].loc[idx]
        print(f"{name:12s}: Gain={gain:6.0f}, Loss={loss:6.0f}, Net={net:+7.0f}")


def get_transition_label(
    from_cat: int, to_cat: int, category_names: Optional[Dict] = None
) -> str:
    """
    Get transition label for visualization.

    Args:
        from_cat: Source category
        to_cat: Target category
        category_names: Optional mapping of category numbers to names

    Returns:
        str: Transition label
    """
    if category_names:
        from_name = category_names.get(from_cat, str(from_cat))
        to_name = category_names.get(to_cat, str(to_cat))
    else:
        from_name = str(from_cat)
        to_name = str(to_cat)

    if from_cat == to_cat:
        return f"{from_name} (persistent)"
    else:
        return f"{from_name} → {to_name}"


def create_change_matrix(time1: np.ndarray, time2: np.ndarray) -> pd.DataFrame:
    """
    Create a change matrix between two time periods.

    Alias for get_transition_matrix for backward compatibility.
    """
    return get_transition_matrix(time1, time2)


def calculate_area_stats(landscape: np.ndarray, pixel_area: float = 1.0) -> Dict:
    """
    Calculate area statistics for a landscape.

    Computes total area, category areas, and proportions following
    the Pontius methodology for land use analysis.

    Args:
        landscape: Land use array
        pixel_area: Area of each pixel in km2 (default: 1.0)

    Returns:
        Dict: Dictionary with area statistics including total area,
              category areas, and proportions
    """
    total_pixels = landscape.size
    total_area = total_pixels * pixel_area

    categories = np.unique(landscape)
    category_areas = {}
    category_proportions = {}

    for cat in categories:
        pixels = np.sum(landscape == cat)
        area = pixels * pixel_area
        proportion = pixels / total_pixels

        category_areas[cat] = area
        category_proportions[cat] = proportion

    return {
        "total_area": total_area,
        "total_pixels": total_pixels,
        "pixel_area": pixel_area,
        "category_areas": category_areas,
        "category_proportions": category_proportions,
    }


def validate_landscape_data(landscape: np.ndarray, name: str = "landscape") -> bool:
    """
    Validate landscape data for analysis.

    Performs basic validation checks on landscape data to ensure
    it meets requirements for Pontius methodology analysis.

    Args:
        landscape: Land use array to validate
        name: Name of the landscape for error messages

    Returns:
        bool: True if validation passes

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(landscape, np.ndarray):
        raise ValueError(f"{name} must be a numpy array")

    if landscape.ndim != 2:
        raise ValueError(f"{name} must be a 2D array")

    if landscape.size == 0:
        raise ValueError(f"{name} cannot be empty")

    if np.any(np.isnan(landscape)):
        raise ValueError(f"{name} contains NaN values")

    if np.any(landscape < 0):
        raise ValueError(f"{name} contains negative values")

    return True


def get_pontius_categories() -> Dict[int, str]:
    """
    Get standard category labels used in Pontius methodology examples.

    Returns:
        Dict[int, str]: Mapping of category numbers to descriptive names
    """
    return {1: "Forest", 2: "Agriculture", 3: "Urban", 4: "Water", 5: "Other"}


def format_area_for_display(area: float, unit: str = "km2") -> str:
    """
    Format area values for display.

    Args:
        area: Area value to format
        unit: Unit for display (default: "km2")

    Returns:
        str: Formatted area string
    """
    if area >= 1000:
        return f"{area:,.1f} {unit}"
    elif area >= 1:
        return f"{area:.1f} {unit}"
    else:
        return f"{area:.3f} {unit}"


def calculate_persistence_ratio(change_matrix: pd.DataFrame) -> pd.Series:
    """
    Calculate persistence ratio for each category.

    Following Pontius methodology, persistence ratio is the proportion
    of a category that remains unchanged.

    Args:
        change_matrix: Transition matrix between time periods

    Returns:
        pd.Series: Persistence ratio for each category
    """
    diagonal = np.diag(change_matrix.values)
    row_sums = change_matrix.sum(axis=1).values

    # Avoid division by zero
    persistence_ratio = np.where(row_sums > 0, diagonal / row_sums, 0)

    return pd.Series(
        persistence_ratio, index=change_matrix.index, name="persistence_ratio"
    )


def create_demo_time_series() -> Tuple[np.ndarray, np.ndarray]:
    """
    Create demo time series data for testing.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Two landscapes representing
                                      different time periods
    """
    time1 = demo_landscape()

    # Create time2 with some changes
    time2 = time1.copy()
    # Simulate some urban expansion (category 3)
    time2[7:9, 7:9] = 3
    # Simulate some forest loss (category 1 to 2)
    time2[0:2, 0:2] = 2

    return time1, time2
