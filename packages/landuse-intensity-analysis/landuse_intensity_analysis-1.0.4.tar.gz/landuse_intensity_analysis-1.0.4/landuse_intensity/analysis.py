"""
Analysis functions for land use and cover change contingency tables.

This module provides functions for creating contingency tables from raster
time series and performing various land use change analyses.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

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
    analysis_type: str = "auto",
) -> Dict[str, Any]:
    """
    Extract Land Use and Cover (LUC) transitions for all input grids of the time series.

    This function performs cross-tabulation analysis between time pairs in the
    input raster series. It can perform one-step analysis (first vs last period)
    or multi-step analysis (all consecutive pairs).

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
    analysis_type : str, default "auto"
        Type of analysis to perform:
        - "auto": Automatically choose based on number of rasters
        - "onestep": First vs last period only
        - "multistep": All consecutive pairs

    Returns
    -------
    dict
        Dictionary containing:
        - 'lulc_Multistep': Multi-period contingency table DataFrame (if applicable)
        - 'lulc_Onestep': Full period contingency table DataFrame (if applicable)
        - 'tb_legend': Category legend DataFrame
        - 'totalArea': Total landscape area in km²
        - 'totalInterval': Total time interval in years
        - 'analysis_type': Type of analysis performed
        - 'time_periods': List of time periods analyzed

    Examples
    --------
    >>> # Auto analysis (chooses based on raster count)
    >>> ct = contingency_table('/path/to/rasters/')

    >>> # Force one-step analysis (first vs last)
    >>> ct = contingency_table('/path/to/rasters/', analysis_type='onestep')

    >>> # Force multi-step analysis (all consecutive pairs)
    >>> ct = contingency_table('/path/to/rasters/', analysis_type='multistep')
    """

    # Load raster data if needed
    if isinstance(input_raster, str) or isinstance(input_raster, list):
        raster_data = load_rasters(input_raster, lazy=not parallel)
    elif isinstance(input_raster, xr.Dataset):
        raster_data = input_raster
    else:
        raise TypeError("input_raster must be a path, list of paths, or xarray Dataset")

    # Extract years from time coordinates
    time_values = raster_data.time.values
    
    # Check if time values are already numeric (years)
    if np.issubdtype(time_values.dtype, np.number):
        years = time_values.astype(int).tolist()
        # Use the numeric years as names for indexing
        names = years
    else:
        # Extract years from string names
        years = _extract_years_from_names(
            list(time_values), name_separator, year_position, name_pattern
        )
        names = list(time_values)

    # Validate and sort by year
    year_df = pd.DataFrame({"name": names, "year": years})
    year_df = year_df.sort_values("year").reset_index(drop=True)

    # Reorder dataset by years
    raster_data = raster_data.sel(time=year_df["name"].values)

    # Apply class exclusions if specified
    if exclude_classes is not None:
        raster_data = _apply_class_exclusions(raster_data, exclude_classes)

    # Calculate area information
    pixel_area_km2 = (pixel_resolution**2) / 1_000_000  # Convert m² to km²

    time_values = year_df["year"].values
    n_periods = len(time_values)

    # Determine analysis type automatically if set to "auto"
    if analysis_type == "auto":
        if n_periods == 2:
            analysis_type = "onestep"  # Only two periods available
        else:
            analysis_type = "multistep"  # More than two periods, do multi-step

    print(f"📊 Analysis type: {analysis_type}")
    print(f"📅 Time periods: {list(time_values)}")

    # Initialize results
    results = {
        'analysis_type': analysis_type,
        'time_periods': list(time_values),
        'totalArea': None,
        'totalInterval': time_values[-1] - time_values[0] if n_periods > 1 else 0
    }

    # Generate contingency tables based on analysis type
    if analysis_type == "multistep":
        # Multi-step analysis: all consecutive pairs
        multistep_tables = []

        for i in range(n_periods - 1):
            year_from = time_values[i]
            year_to = time_values[i + 1]
            period = f"{year_from}-{year_to}"
            interval = year_to - year_from

            print(f"🔄 Processing {period}...")

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

        # Combine all multi-step tables
        if multistep_tables:
            results['lulc_Multistep'] = pd.concat(multistep_tables, ignore_index=True)

    elif analysis_type == "onestep":
        # One-step analysis: first to last time period
        year_from = time_values[0]
        year_to = time_values[-1]
        period = f"{year_from}-{year_to}"
        interval = year_to - year_from

        print(f"🔄 Processing one-step {period}...")

        raster_from = raster_data.isel(time=0)["land_use"].values
        raster_to = raster_data.isel(time=-1)["land_use"].values

        # Generate cross-tabulation
        ct_result = _compute_crosstab(
            raster_from, raster_to, pixel_area_km2, chunk_size=chunk_size
        )

        # Add metadata
        ct_result["Period"] = period
        ct_result["Year_from"] = year_from
        ct_result["Year_to"] = year_to
        ct_result["Interval"] = interval

        results['lulc_Onestep'] = ct_result

    # Calculate total area
    if n_periods > 0:
        first_raster = raster_data.isel(time=0)["land_use"].values
        total_pixels = (~np.isnan(first_raster)).sum()
        results['totalArea'] = total_pixels * pixel_area_km2

    # Generate category legend
    results['tb_legend'] = _generate_category_legend(raster_data)

    return results


def _generate_category_legend(raster_data: xr.Dataset) -> pd.DataFrame:
    """
    Generate category legend from raster data.

    Args:
        raster_data: xarray Dataset containing land use data

    Returns:
        DataFrame with category values and names
    """
    all_classes = set()

    # Collect all unique classes from all time periods
    for i in range(len(raster_data.time)):
        land_use_data = raster_data.isel(time=i)["land_use"].values
        unique_classes = np.unique(land_use_data[~np.isnan(land_use_data)])
        all_classes.update(unique_classes)

    # Create legend DataFrame
    tb_legend = pd.DataFrame(
        {
            "CategoryValue": sorted(all_classes),
            "CategoryName": [f"Class_{int(c)}" for c in sorted(all_classes)],
        }
    )

    return tb_legend


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


def contingency_table_multistep(
    input_raster: Union[str, List[str], xr.Dataset],
    steps: Optional[List[Tuple[int, int]]] = None,
    pixel_resolution: float = 30.0,
    name_separator: str = "_",
    year_position: str = "last",
    name_pattern: Optional[str] = None,
    exclude_classes: Optional[List[int]] = None,
    parallel: bool = True,
    chunk_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Extract Land Use and Cover (LUC) transitions for specific time step combinations.

    This function allows for both single-step (consecutive periods) and multi-step
    (non-consecutive periods) analysis by specifying which time pairs to compare.

    Parameters
    ----------
    input_raster : str, list of str, or xr.Dataset
        Path to raster directory, list of raster files, or xarray Dataset.
    steps : list of tuples, optional
        List of (start_year, end_year) tuples to analyze. If None, analyzes all consecutive pairs.
    pixel_resolution : float, default 30.0
        The pixel spatial resolution in meters.
    name_separator : str, default "_"
        The separator used to split the raster names.
    year_position : str, default "last"
        Position of the year in the split name. Options: "last", "first", or numeric.
    name_pattern : str, optional
        Regular expression pattern to extract year from names.
    exclude_classes : list of int, optional
        Class values to exclude from the analysis.
    parallel : bool, default True
        Enable parallel processing.
    chunk_size : int, optional
        Size of chunks for parallel processing.

    Returns
    -------
    dict
        Dictionary containing contingency tables for each step combination.

    Examples
    --------
    >>> # Single-step analysis (consecutive periods)
    >>> result = contingency_table_multistep("data/", steps=[(1990, 2000), (2000, 2010)])
    >>>
    >>> # Multi-step analysis (non-consecutive periods)
    >>> result = contingency_table_multistep("data/", steps=[(1990, 2010), (2000, 2020)])
    >>>
    >>> # All consecutive pairs (default)
    >>> result = contingency_table_multistep("data/")
    """
    # Load raster data
    if isinstance(input_raster, str):
        rasters = load_rasters(
            input_raster,
            name_separator=name_separator,
            year_position=year_position,
            name_pattern=name_pattern
        )
    elif isinstance(input_raster, list):
        rasters = load_rasters(
            input_raster,
            name_separator=name_separator,
            year_position=year_position,
            name_pattern=name_pattern
        )
    else:
        rasters = input_raster

    if not rasters:
        raise ValueError("No raster data found")

    # Get available years
    available_years = sorted(rasters.time.values.astype(int))

    # If no steps specified, use all consecutive pairs
    if steps is None:
        steps = [(available_years[i], available_years[i+1])
                for i in range(len(available_years)-1)]

    results = {}

    for start_year, end_year in steps:
        if start_year not in available_years or end_year not in available_years:
            print(f"Warning: Years {start_year} or {end_year} not found in data. Skipping.")
            continue

        print(f"Analyzing transition: {start_year} → {end_year}")

        # Filter rasters for the specific years
        start_raster = rasters.sel(time=start_year)
        end_raster = rasters.sel(time=end_year)

        # Create contingency table for this specific transition
        ct_key = f"{start_year}_{end_year}"

        # Calculate contingency table
        start_data = start_raster.values.flatten()
        end_data = end_raster.values.flatten()

        # Remove NaN values
        valid_mask = ~(np.isnan(start_data) | np.isnan(end_data))
        start_data = start_data[valid_mask]
        end_data = end_data[valid_mask]

        # Exclude specified classes
        if exclude_classes:
            exclude_mask = ~np.isin(start_data, exclude_classes) & ~np.isin(end_data, exclude_classes)
            start_data = start_data[exclude_mask]
            end_data = end_data[exclude_mask]

        # Create contingency table
        ct = pd.crosstab(start_data, end_data, dropna=False)

        # Calculate areas
        pixel_area = pixel_resolution ** 2
        ct_area = ct * pixel_area

        results[ct_key] = {
            'contingency_table': ct,
            'contingency_table_area': ct_area,
            'start_year': start_year,
            'end_year': end_year,
            'pixel_resolution': pixel_resolution,
            'pixel_area': pixel_area,
            'total_pixels': len(start_data),
            'total_area': len(start_data) * pixel_area
        }

    return results


def intensity_analysis_multistep(
    multistep_results: Dict[str, Any],
    analysis_type: str = "both"
) -> Dict[str, Any]:
    """
    Perform intensity analysis for multiple time step combinations.

    Parameters
    ----------
    multistep_results : dict
        Results from contingency_table_multistep function.
    analysis_type : str, default "both"
        Type of analysis: "interval", "category", or "both".

    Returns
    -------
    dict
        Intensity analysis results for each time step combination.

    Examples
    --------
    >>> ct_results = contingency_table_multistep("data/", steps=[(1990, 2000), (1990, 2010)])
    >>> intensity_results = intensity_analysis_multistep(ct_results)
    """
    from .intensity import intensity_analysis

    intensity_results = {}

    for step_key, step_data in multistep_results.items():
        print(f"Performing intensity analysis for {step_key}")

        ct = step_data['contingency_table']

        # Perform intensity analysis
        intensity_result = intensity_analysis(ct, analysis_type=analysis_type)

        intensity_results[step_key] = {
            'intensity_analysis': intensity_result,
            'start_year': step_data['start_year'],
            'end_year': step_data['end_year'],
            'contingency_table': ct
        }

    return intensity_results


def create_change_maps_multistep(
    multistep_results: Dict[str, Any],
    output_dir: str = "change_maps",
    colormap: str = "RdYlGn",
    figsize: tuple = (12, 8)
) -> Dict[str, str]:
    """
    Create change maps for multiple time step combinations.

    Parameters
    ----------
    multistep_results : dict
        Results from contingency_table_multistep function.
    output_dir : str, default "change_maps"
        Directory to save the change maps.
    colormap : str, default "RdYlGn"
        Colormap for the change maps.
    figsize : tuple, default (12, 8)
        Figure size for the maps.

    Returns
    -------
    dict
        Dictionary mapping step keys to saved file paths.

    Examples
    --------
    >>> ct_results = contingency_table_multistep("data/", steps=[(1990, 2000), (1990, 2010)])
    >>> maps = create_change_maps_multistep(ct_results)
    """
    import os
    import matplotlib.pyplot as plt
    from pathlib import Path

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    saved_files = {}

    for step_key, step_data in multistep_results.items():
        print(f"Creating change map for {step_key}")

        start_year = step_data['start_year']
        end_year = step_data['end_year']
        ct = step_data['contingency_table']

        # Create change map visualization
        fig, ax = plt.subplots(figsize=figsize)

        # Create a change matrix visualization
        change_matrix = ct.div(ct.sum(axis=1), axis=0)  # Normalize by row sums

        im = ax.imshow(change_matrix.values, cmap=colormap, aspect='auto')

        # Set labels
        ax.set_xticks(range(len(ct.columns)))
        ax.set_yticks(range(len(ct.index)))
        ax.set_xticklabels([f"Class {int(x)}" for x in ct.columns])
        ax.set_yticklabels([f"Class {int(x)}" for x in ct.index])

        ax.set_xlabel(f"Land Use Class {end_year}")
        ax.set_ylabel(f"Land Use Class {start_year}")
        ax.set_title(f"Land Use Change: {start_year} → {end_year}")

        # Add colorbar
        plt.colorbar(im, ax=ax, label="Proportion of Change")

        # Save the figure
        filename = f"change_map_{step_key}.png"
        filepath = output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        saved_files[step_key] = str(filepath)
        print(f"Saved: {filepath}")

    return saved_files


def create_spatial_change_maps(
    rasters: Dict[str, np.ndarray],
    contingency_data: Dict,
    output_dir: str = "spatial_maps",
    colormap: str = "RdYlGn",
    figsize: tuple = (12, 8),
    add_north_arrow: bool = True,
    add_scale_bar: bool = True,
    add_coordinates: bool = True
) -> Dict[str, str]:
    """
    Create spatial change maps with geographic orientation.

    Parameters
    ----------
    rasters : dict
        Dictionary of rasters by year
    contingency_data : dict
        Results from contingency_table() function
    output_dir : str, default "spatial_maps"
        Directory to save the spatial maps
    colormap : str, default "RdYlGn"
        Colormap for the change maps
    figsize : tuple, default (12, 8)
        Figure size for the maps
    add_north_arrow : bool, default True
        Add north arrow to maps
    add_scale_bar : bool, default True
        Add scale bar to maps
    add_coordinates : bool, default True
        Add coordinate grid to maps

    Returns
    -------
    dict
        Dictionary mapping period keys to saved file paths
    """
    import os
    import matplotlib.pyplot as plt
    from pathlib import Path
    import numpy as np

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    saved_files = {}

    # Extract time periods from contingency data
    if 'lulc_Multistep' in contingency_data:
        multistep_data = contingency_data['lulc_Multistep']

        # Group by period
        periods = multistep_data['Period'].unique()

        for period in periods:
            period_data = multistep_data[multistep_data['Period'] == period]
            years = period.split('-')
            start_year = int(years[0])
            end_year = int(years[1])

            # Get rasters for this period
            if start_year in rasters and end_year in rasters:
                raster_from = rasters[start_year]
                raster_to = rasters[end_year]

                # Create spatial change map
                fig, ax = plt.subplots(figsize=figsize)

                # Calculate change (simple difference for visualization)
                change_map = raster_to.astype(float) - raster_from.astype(float)

                # Create mask for no-change areas
                no_change_mask = change_map == 0

                # Plot change map
                im = ax.imshow(change_map, cmap=colormap, alpha=0.8)

                # Overlay no-change areas with subtle pattern
                ax.imshow(no_change_mask, cmap='gray', alpha=0.1, interpolation='none')

                # Set title and labels
                ax.set_title(f'Mapa de Mudança no Uso do Solo\n{start_year} → {end_year}',
                           fontsize=14, fontweight='bold', pad=20)
                ax.set_xlabel('Coordenada X (pixels)', fontsize=12)
                ax.set_ylabel('Coordenada Y (pixels)', fontsize=12)

                # Add colorbar
                cbar = plt.colorbar(im, ax=ax, label='Mudança nas Classes', shrink=0.8)
                cbar.set_label('Mudança nas Classes', fontsize=12)

                # Add north arrow
                if add_north_arrow:
                    _add_north_arrow(ax, raster_from.shape)

                # Add scale information
                if add_scale_bar:
                    _add_scale_bar(ax, raster_from.shape)

                # Add coordinate grid
                if add_coordinates:
                    ax.grid(True, alpha=0.3, linestyle='--')

                plt.tight_layout()

                # Save the figure
                filename = f"spatial_change_map_{period}.png"
                filepath = output_path / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()

                saved_files[period] = str(filepath)
                print(f"Saved spatial map: {filepath}")

    return saved_files


def _add_north_arrow(ax, shape, position='upper right'):
    """Add north arrow to the map."""
    import matplotlib.patches as patches

    height, width = shape

    if position == 'upper right':
        x = width * 0.85
        y = height * 0.85
    elif position == 'upper left':
        x = width * 0.15
        y = height * 0.85
    else:
        x = width * 0.5
        y = height * 0.85

    # Create arrow
    arrow_length = min(width, height) * 0.05

    # Arrow shaft
    ax.arrow(x, y, 0, arrow_length, head_width=arrow_length*0.3,
             head_length=arrow_length*0.3, fc='black', ec='black', alpha=0.8)

    # Arrow head
    ax.arrow(x, y+arrow_length, 0, -arrow_length*0.2, head_width=arrow_length*0.4,
             head_length=arrow_length*0.2, fc='black', ec='black', alpha=0.8)

    # Add "N" label
    ax.text(x, y+arrow_length*1.3, 'N', ha='center', va='bottom',
            fontsize=12, fontweight='bold', alpha=0.8)


def _add_scale_bar(ax, shape, position='lower left'):
    """Add scale bar to the map."""
    height, width = shape

    if position == 'lower left':
        x = width * 0.1
        y = height * 0.1
    elif position == 'lower right':
        x = width * 0.7
        y = height * 0.1
    else:
        x = width * 0.1
        y = height * 0.1

    # Scale bar length (assuming 30m resolution)
    scale_length_pixels = min(width * 0.2, 100)  # Max 100 pixels or 20% of width
    scale_length_km = (scale_length_pixels * 30) / 1000  # Convert to km

    # Draw scale bar
    ax.plot([x, x+scale_length_pixels], [y, y], 'k-', linewidth=3, alpha=0.8)
    ax.plot([x, x], [y-2, y+2], 'k-', linewidth=3, alpha=0.8)
    ax.plot([x+scale_length_pixels, x+scale_length_pixels], [y-2, y+2], 'k-', linewidth=3, alpha=0.8)

    # Add scale text
    ax.text(x + scale_length_pixels/2, y - 10, '.1f',
            ha='center', va='top', fontsize=10, alpha=0.8)


def analyze_all_combinations(
    input_raster: Union[str, List[str], xr.Dataset],
    include_singlestep: bool = True,
    include_multistep: bool = True,
    pixel_resolution: float = 30.0,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform complete analysis for all possible time combinations.

    This function automatically generates both single-step and multi-step
    analyses for all available time periods.

    Parameters
    ----------
    input_raster : str, list of str, or xr.Dataset
        Input raster data.
    include_singlestep : bool, default True
        Include single-step (consecutive) analyses.
    include_multistep : bool, default True
        Include multi-step (non-consecutive) analyses.
    pixel_resolution : float, default 30.0
        Pixel resolution in meters.
    **kwargs
        Additional arguments for analysis functions.

    Returns
    -------
    dict
        Complete analysis results for all combinations.

    Examples
    --------
    >>> # For years 1990, 2000, 2010
    >>> results = analyze_all_combinations("data/")
    >>> # Results will include:
    >>> # - Single-step: 1990→2000, 2000→2010
    >>> # - Multi-step: 1990→2010
    """
    # Load raster data to get available years
    if isinstance(input_raster, str):
        rasters = load_rasters(input_raster, **kwargs)
    elif isinstance(input_raster, list):
        rasters = load_rasters(input_raster, **kwargs)
    else:
        rasters = input_raster

    if not rasters:
        raise ValueError("No raster data found")

    available_years = sorted(rasters.time.values.astype(int))
    print(f"Available years: {available_years}")

    # Generate all step combinations
    all_steps = []

    if include_singlestep:
        # Single-step: consecutive periods
        singlestep = [(available_years[i], available_years[i+1])
                     for i in range(len(available_years)-1)]
        all_steps.extend(singlestep)
        print(f"Single-step combinations: {singlestep}")

    if include_multistep and len(available_years) > 2:
        # Multi-step: non-consecutive periods
        multistep = []
        for i in range(len(available_years)):
            for j in range(i+2, len(available_years)):  # Skip consecutive
                multistep.append((available_years[i], available_years[j]))
        all_steps.extend(multistep)
        print(f"Multi-step combinations: {multistep}")

    print(f"Total combinations to analyze: {len(all_steps)}")

    # Perform contingency table analysis
    print("\n📊 Generating contingency tables...")
    ct_results = contingency_table_multistep(
        input_raster,
        steps=all_steps,
        pixel_resolution=pixel_resolution,
        **kwargs
    )

    # Perform intensity analysis
    print("\n🔬 Performing intensity analysis...")
    intensity_results = intensity_analysis_multistep(ct_results)

    # Create change maps
    print("\n🗺️ Creating change maps...")
    map_files = create_change_maps_multistep(ct_results)

    # Combine all results
    complete_results = {
        'metadata': {
            'available_years': available_years,
            'total_combinations': len(all_steps),
            'single_step_count': len(singlestep) if include_singlestep else 0,
            'multi_step_count': len(multistep) if include_multistep else 0,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        },
        'contingency_tables': ct_results,
        'intensity_analysis': intensity_results,
        'change_maps': map_files,
        'step_combinations': all_steps
    }

    print("✅ Complete analysis finished!")
    print(f"📊 Contingency tables: {len(ct_results)}")
    print(f"🔬 Intensity analyses: {len(intensity_results)}")
    print(f"🗺️ Change maps: {len(map_files)}")

    return complete_results
