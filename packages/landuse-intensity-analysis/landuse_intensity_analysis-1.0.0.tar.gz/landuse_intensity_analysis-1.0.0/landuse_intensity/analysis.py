"""
Analysis functions for land use and cover change contingency tables.

This module provides functions for creating contingency tables from raster
time series and performing various land use change analyses.
"""

import re
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import xarray as xr

from .raster import load_rasters


def contingency_table(
    input_raster: Union[str, List[str], xr.Dataset],
    pixel_resolution: float = 30.0,
    name_separator: str = "_",
    year_position: str = "last",
    name_pattern: Optional[str] = None,
    exclude_classes: Optional[List[int]] = None,
    parallel: bool = True,
    chunk_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Extract Land Use and Cover (LUC) transitions for all input grids of the time series.

    This function performs cross-tabulation analysis between all time pairs in the
    input raster series, generating pairwise comparisons and full period analysis.

    Parameters
    ----------
    input_raster : str, list of str, or xr.Dataset
        Path to raster directory, list of raster files, or xarray Dataset.
    pixel_resolution : float, default 30.0
        The pixel spatial resolution in meters.
    name_separator : str, default "_"
        The separator used to split the raster names.
    year_position : str, default "last"
        Position of the year in the split name. Options: "last", "first", or numeric.
    name_pattern : str, optional
        Regular expression pattern to extract year from names. If provided,
        overrides name_separator and year_position.
    exclude_classes : list of int, optional
        Class values to exclude from the analysis (e.g., [0] for background).
    parallel : bool, default True
        Enable parallel processing (when available).
    chunk_size : int, optional
        Number of cells to process per chunk for large rasters.

    Returns
    -------
    dict
        Dictionary containing:
        - 'lulc_Multistep': Multi-period contingency table DataFrame
        - 'lulc_Onestep': Full period contingency table DataFrame
        - 'tb_legend': Category legend DataFrame
        - 'totalArea': Total landscape area in km²
        - 'totalInterval': Total time interval in years

    Examples
    --------
    >>> import openland as ol
    >>> ct = ol.contingency_table('/path/to/rasters/', pixel_resolution=30)
    >>> print(ct['lulc_Multistep'])
    """

    # Load raster data if needed
    if isinstance(input_raster, str) or isinstance(input_raster, list):
        raster_data = load_rasters(input_raster, lazy=not parallel)
    elif isinstance(input_raster, xr.Dataset):
        raster_data = input_raster
    else:
        raise TypeError("input_raster must be a path, list of paths, or xarray Dataset")

    # Extract years from time coordinates
    years = _extract_years_from_names(
        list(raster_data.time.values), name_separator, year_position, name_pattern
    )

    # Validate and sort by year
    year_df = pd.DataFrame({"name": raster_data.time.values, "year": years})
    year_df = year_df.sort_values("year").reset_index(drop=True)

    # Reorder dataset by years
    raster_data = raster_data.sel(time=year_df["name"].values)

    # Apply class exclusions if specified
    if exclude_classes is not None:
        raster_data = _apply_class_exclusions(raster_data, exclude_classes)

    # Calculate area information
    pixel_area_km2 = (pixel_resolution**2) / 1_000_000  # Convert m² to km²

    # Generate contingency tables
    multistep_tables = []
    onestep_table = None

    time_values = year_df["year"].values

    # Multi-step analysis (consecutive time pairs)
    for i in range(len(time_values) - 1):
        year_from = time_values[i]
        year_to = time_values[i + 1]
        period = f"{year_from}-{year_to}"
        interval = year_to - year_from

        # Get raster data for the two time points
        raster_from = raster_data.isel(time=i)["land_use"].values
        raster_to = raster_data.isel(time=i + 1)["land_use"].values

        # Generate cross-tabulation
        ct_result = _compute_crosstab(
            raster_from, raster_to, pixel_area_km2, chunk_size=chunk_size
        )

        # Add metadata
        ct_result["Period"] = period
        ct_result["Year_from"] = year_from
        ct_result["Year_to"] = year_to
        ct_result["Interval"] = interval

        multistep_tables.append(ct_result)

    # One-step analysis (first to last time period)
    if len(time_values) > 2:
        year_from = time_values[0]
        year_to = time_values[-1]
        period = f"{year_from}-{year_to}"
        interval = year_to - year_from

        raster_from = raster_data.isel(time=0)["land_use"].values
        raster_to = raster_data.isel(time=-1)["land_use"].values

        onestep_table = _compute_crosstab(
            raster_from, raster_to, pixel_area_km2, chunk_size=chunk_size
        )

        onestep_table["Period"] = period
        onestep_table["Year_from"] = year_from
        onestep_table["Year_to"] = year_to
        onestep_table["Interval"] = interval

    # Combine multistep results
    lulc_multistep = pd.concat(multistep_tables, ignore_index=True)

    # Create legend from unique classes
    all_classes = set()
    for table in multistep_tables:
        all_classes.update(table["From"].unique())
        all_classes.update(table["To"].unique())

    if onestep_table is not None:
        all_classes.update(onestep_table["From"].unique())
        all_classes.update(onestep_table["To"].unique())

    tb_legend = pd.DataFrame(
        {
            "CategoryValue": sorted(all_classes),
            "CategoryName": [f"Class_{int(c)}" for c in sorted(all_classes)],
        }
    )

    # Calculate total area and interval
    total_area = lulc_multistep["km2"].sum() / len(
        multistep_tables
    )  # Average area per period
    total_interval = time_values[-1] - time_values[0]

    result = {
        "lulc_Multistep": lulc_multistep,
        "lulc_Onestep": onestep_table if onestep_table is not None else pd.DataFrame(),
        "tb_legend": tb_legend,
        "totalArea": total_area,
        "totalInterval": total_interval,
    }

    return result


def _extract_years_from_names(
    names: List[str], separator: str, year_position: str, pattern: Optional[str]
) -> List[int]:
    """Extract years from raster names using different strategies."""

    years = []

    for name in names:
        try:
            if pattern is not None:
                # Use regex pattern
                match = re.search(pattern, name)
                if match:
                    year = int(match.group(1) if match.groups() else match.group(0))
                else:
                    raise ValueError(f"Pattern '{pattern}' not found in '{name}'")
            else:
                # Use separator and position
                parts = name.split(separator)

                if year_position == "last":
                    year_str = parts[-1]
                elif year_position == "first":
                    year_str = parts[0]
                elif isinstance(year_position, int):
                    year_str = parts[year_position]
                else:
                    raise ValueError(f"Invalid year_position: {year_position}")

                # Extract numeric year from string
                year_match = re.search(r"\d{4}", year_str)
                if year_match:
                    year = int(year_match.group())
                else:
                    raise ValueError(f"No 4-digit year found in '{year_str}'")

            years.append(year)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Could not extract year from '{name}': {e}")

    return years


def _apply_class_exclusions(
    raster_data: xr.Dataset, exclude_classes: List[int]
) -> xr.Dataset:
    """Apply class exclusions by setting excluded values to NaN."""

    data = raster_data.copy()
    land_use = data["land_use"]

    # Create mask for excluded classes
    exclude_mask = np.isin(land_use.values, exclude_classes)

    # Set excluded values to NaN
    land_use_filtered = land_use.where(~exclude_mask)
    data["land_use"] = land_use_filtered

    return data


def _compute_crosstab(
    raster_from: np.ndarray,
    raster_to: np.ndarray,
    pixel_area_km2: float,
    chunk_size: Optional[int] = None,
) -> pd.DataFrame:
    """Compute cross-tabulation between two raster arrays."""

    # Flatten arrays and remove NaN values
    from_flat = raster_from.flatten()
    to_flat = raster_to.flatten()

    # Create mask for valid pixels (non-NaN in both arrays)
    valid_mask = ~(np.isnan(from_flat) | np.isnan(to_flat))
    from_valid = from_flat[valid_mask].astype(int)
    to_valid = to_flat[valid_mask].astype(int)

    if len(from_valid) == 0:
        return pd.DataFrame(columns=["From", "To", "km2", "QtPixel"])

    # Process in chunks if specified
    if chunk_size is not None and len(from_valid) > chunk_size:
        return _compute_crosstab_chunked(
            from_valid, to_valid, pixel_area_km2, chunk_size
        )

    # Use numpy unique for efficient counting
    # Combine from and to values into single array for joint counting
    combined = from_valid * 10000 + to_valid  # Assume class values < 10000
    unique_combined, counts = np.unique(combined, return_counts=True)

    # Separate back into from/to values
    from_vals = unique_combined // 10000
    to_vals = unique_combined % 10000

    # Create result DataFrame
    result = pd.DataFrame(
        {
            "From": from_vals,
            "To": to_vals,
            "QtPixel": counts,
            "km2": counts * pixel_area_km2,
        }
    )

    return result


def _compute_crosstab_chunked(
    from_array: np.ndarray, to_array: np.ndarray, pixel_area_km2: float, chunk_size: int
) -> pd.DataFrame:
    """Compute cross-tabulation in chunks for memory efficiency."""

    n_chunks = (len(from_array) + chunk_size - 1) // chunk_size
    chunk_results = []

    for i in range(n_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(from_array))

        from_chunk = from_array[start_idx:end_idx]
        to_chunk = to_array[start_idx:end_idx]

        # Process chunk
        combined = from_chunk * 10000 + to_chunk
        unique_combined, counts = np.unique(combined, return_counts=True)

        from_vals = unique_combined // 10000
        to_vals = unique_combined % 10000

        chunk_df = pd.DataFrame({"From": from_vals, "To": to_vals, "QtPixel": counts})

        chunk_results.append(chunk_df)

    # Combine chunks and aggregate
    combined_df = pd.concat(chunk_results, ignore_index=True)

    # Aggregate counts for duplicate From-To combinations
    aggregated = combined_df.groupby(["From", "To"])["QtPixel"].sum().reset_index()
    aggregated["km2"] = aggregated["QtPixel"] * pixel_area_km2

    return aggregated


def performance_status() -> Dict[str, Any]:
    """
    Check performance optimization status and available libraries.

    Returns
    -------
    dict
        Dictionary containing information about available optimization libraries.
    """
    import sys

    status = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "xarray_version": xr.__version__,
    }

    # Check for optional performance libraries
    try:
        import dask

        status["dask_available"] = True
        status["dask_version"] = dask.__version__
    except ImportError:
        status["dask_available"] = False

    try:
        import numba

        status["numba_available"] = True
        status["numba_version"] = numba.__version__
    except ImportError:
        status["numba_available"] = False

    return status
