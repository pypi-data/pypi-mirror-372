"""
Raster data loading and processing functionality for OpenLand.

This module provides functions for loading, summarizing, and processing
spatiotemporal raster data for land use and cover change analysis.
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
import rasterio
import rasterio.features
import xarray as xr


def summary_dir(path: Union[str, List[str], List[xr.DataArray]]) -> pd.DataFrame:
    """
    Summary of multiple parameters in a raster directory.

    Lists major characteristics of raster inputs including dimensions,
    resolution, extent, values (min, max), and coordinate reference system.

    Parameters
    ----------
    path : str, list of str, or list of xarray.DataArray
        The path to the raster directory, list of file paths, or list of
        raster objects to be analyzed.

    Returns
    -------
    pd.DataFrame
        Table with raster parameters in columns including file_name,
        xmin, xmax, ymin, ymax, res_x, res_y, nrow, ncol, min_val,
        max_val, and crs.

    Examples
    --------
    >>> import openland as ol
    >>> summary = ol.summary_dir('/path/to/raster/directory')
    >>> print(summary)
    """

    # Handle different input types
    if isinstance(path, str):
        # Directory path - load .tif files
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory does not exist: {path}")

        if path_obj.is_dir():
            # Get all .tif files in directory
            raster_files = list(path_obj.glob("*.tif")) + list(path_obj.glob("*.tiff"))
            if not raster_files:
                raise ValueError(f"No .tif files found in directory: {path}")
            file_list = [str(f) for f in raster_files]
        else:
            # Single file
            file_list = [path]

    elif isinstance(path, list):
        if isinstance(path[0], str):
            # List of file paths
            file_list = path
        elif isinstance(path[0], xr.DataArray):
            # List of xarray DataArrays
            return _summary_from_arrays(path)
        else:
            raise TypeError("List elements must be file paths or xarray DataArrays")
    else:
        raise TypeError("Input must be a string path or list of paths/arrays")

    # Process each raster file
    summary_list = []
    for file_path in file_list:
        try:
            with rasterio.open(file_path) as src:
                # Get basic metadata
                bounds = src.bounds
                transform = src.transform

                # Calculate min/max values efficiently
                try:
                    # Read a sample to get min/max (memory efficient)
                    data = src.read(1, masked=True)
                    min_val = float(np.nanmin(data))
                    max_val = float(np.nanmax(data))
                except Exception:
                    min_val = np.nan
                    max_val = np.nan

                summary_dict = {
                    "file_name": Path(file_path).name,
                    "xmin": bounds.left,
                    "xmax": bounds.right,
                    "ymin": bounds.bottom,
                    "ymax": bounds.top,
                    "res_x": abs(transform.a),
                    "res_y": abs(transform.e),
                    "nrow": src.height,
                    "ncol": src.width,
                    "min_val": min_val,
                    "max_val": max_val,
                    "crs": str(src.crs) if src.crs else "Unknown",
                }
                summary_list.append(summary_dict)

        except Exception as e:
            warnings.warn(f"Could not process file {file_path}: {e}")
            continue

    if not summary_list:
        raise ValueError("No valid raster files could be processed")

    return pd.DataFrame(summary_list)


def _summary_from_arrays(arrays: List[xr.DataArray]) -> pd.DataFrame:
    """Helper function to create summary from xarray DataArrays."""
    summary_list = []

    for i, arr in enumerate(arrays):
        # Get spatial coordinates
        if "x" in arr.dims and "y" in arr.dims:
            x_coords = arr.coords["x"].values
            y_coords = arr.coords["y"].values

            summary_dict = {
                "file_name": arr.name or f"array_{i}",
                "xmin": float(x_coords.min()),
                "xmax": float(x_coords.max()),
                "ymin": float(y_coords.min()),
                "ymax": float(y_coords.max()),
                "res_x": (
                    float(abs(x_coords[1] - x_coords[0])) if len(x_coords) > 1 else 1.0
                ),
                "res_y": (
                    float(abs(y_coords[1] - y_coords[0])) if len(y_coords) > 1 else 1.0
                ),
                "nrow": len(y_coords),
                "ncol": len(x_coords),
                "min_val": float(np.nanmin(arr.values)),
                "max_val": float(np.nanmax(arr.values)),
                "crs": str(arr.attrs.get("crs", "Unknown")),
            }
            summary_list.append(summary_dict)
        else:
            warnings.warn(f"Array {i} does not have standard x/y coordinates")

    return pd.DataFrame(summary_list)


def summary_map(path: Union[str, xr.DataArray]) -> pd.DataFrame:
    """
    Quantitative summary of a unique categorical raster.

    Presents a summary with the pixel quantity of each category present
    in a categorical raster.

    Parameters
    ----------
    path : str or xarray.DataArray
        The path to the raster file or raster object to be analyzed.
        If multilayer, only the first layer will be analyzed.

    Returns
    -------
    pd.DataFrame
        Table containing pixel counts for each pixel value with columns
        'pixvalue' and 'Qt' (quantity).

    Examples
    --------
    >>> import openland as ol
    >>> summary = ol.summary_map('/path/to/raster.tif')
    >>> print(summary)
    """

    # Load raster data
    if isinstance(path, str):
        try:
            with rasterio.open(path) as src:
                # Read first band only
                data = src.read(1, masked=True)
        except Exception as e:
            raise ValueError(f"Could not read raster file {path}: {e}")

    elif isinstance(path, xr.DataArray):
        data = path.values
        # Handle masked arrays
        if hasattr(data, "mask"):
            data = np.ma.masked_array(data, mask=data.mask)
    else:
        raise TypeError("Input must be a file path or xarray DataArray")

    # Remove NaN/masked values
    if isinstance(data, np.ma.MaskedArray):
        valid_data = data.compressed()
    else:
        valid_data = data[~np.isnan(data)]

    if len(valid_data) == 0:
        return pd.DataFrame({"pixvalue": [], "Qt": []})

    # Count unique values efficiently
    unique_vals, counts = np.unique(valid_data, return_counts=True)

    # Create result DataFrame
    result = pd.DataFrame({"pixvalue": unique_vals.astype(int), "Qt": counts})

    return result.sort_values("pixvalue").reset_index(drop=True)


def load_rasters(
    path: Union[str, List[str]], time_dim: str = "time", lazy: bool = True
) -> xr.Dataset:
    """
    Load multiple raster files into an xarray Dataset for time series analysis.

    Parameters
    ----------
    path : str or list of str
        Directory path containing raster files or list of file paths.
    time_dim : str, default 'time'
        Name for the time dimension.
    lazy : bool, default True
        Whether to use lazy loading with dask for large datasets.

    Returns
    -------
    xr.Dataset
        Dataset with raster data organized by time.

    Examples
    --------
    >>> import openland as ol
    >>> rasters = ol.load_rasters('/path/to/raster/directory')
    >>> print(rasters)
    """

    # Get file list
    if isinstance(path, str):
        path_obj = Path(path)
        if path_obj.is_dir():
            file_list = sorted(
                list(path_obj.glob("*.tif")) + list(path_obj.glob("*.tiff"))
            )
        else:
            file_list = [path_obj]
    else:
        file_list = [Path(p) for p in path]

    if not file_list:
        raise ValueError("No raster files found")

    # Load rasters using xarray
    if lazy:
        # Use dask for lazy loading
        try:
            import dask.array as da

            arrays = []
            for file_path in file_list:
                arr = xr.open_rasterio(str(file_path), chunks={"x": 1024, "y": 1024})
                arr = arr.squeeze(
                    "band", drop=True
                )  # Remove band dimension if single band
                arrays.append(arr)

            # Concatenate along time dimension
            dataset = xr.concat(arrays, dim=time_dim)
            dataset[time_dim] = [
                f.stem for f in file_list
            ]  # Use filenames as time labels

        except ImportError:
            warnings.warn("Dask not available, falling back to non-lazy loading")
            lazy = False

    if not lazy:
        # Load all data into memory
        arrays = []
        for file_path in file_list:
            arr = xr.open_rasterio(str(file_path))
            arr = arr.squeeze("band", drop=True)  # Remove band dimension if single band
            arrays.append(arr)

        # Concatenate along time dimension
        dataset = xr.concat(arrays, dim=time_dim)
        dataset[time_dim] = [f.stem for f in file_list]  # Use filenames as time labels

    return dataset.to_dataset(name="land_use")


def performance_status() -> Dict[str, Any]:
    """
    Check performance optimization status and available libraries.

    Returns
    -------
    dict
        Dictionary containing information about available optimization libraries
        and performance settings.

    Examples
    --------
    >>> import openland as ol
    >>> status = ol.performance_status()
    >>> print(status)
    """

    status = {
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "rasterio_version": rasterio.__version__,
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

    # Check rasterio GDAL version
    try:
        import rasterio.env

        with rasterio.env.Env() as env:
            status["gdal_version"] = env.gdal_version
    except:
        status["gdal_version"] = "Unknown"

    return status
