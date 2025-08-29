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

try:
    import rioxarray
    HAS_RIOXARRAY = True
except ImportError:
    HAS_RIOXARRAY = False
    warnings.warn(
        "rioxarray not available. Install with: pip install rioxarray",
        UserWarning
    )


def _open_raster_file(file_path: Union[str, Path], chunks: Dict = None) -> xr.DataArray:
    """
    Open a raster file using the best available method.
    
    This function handles compatibility between different xarray versions,
    automatically choosing between rioxarray.open_rasterio() and legacy
    xr.open_rasterio().
    
    Parameters
    ----------
    file_path : str or Path
        Path to the raster file.
    chunks : dict, optional
        Dictionary mapping dimension names to chunk sizes for dask arrays.
        
    Returns
    -------
    xr.DataArray
        Loaded raster data.
    """
    file_path = str(file_path)
    
    if HAS_RIOXARRAY:
        # Use rioxarray (recommended for xarray >= 0.20.0)
        try:
            if chunks:
                arr = rioxarray.open_rasterio(file_path, chunks=chunks)
            else:
                arr = rioxarray.open_rasterio(file_path)
            return arr
        except Exception as e:
            warnings.warn(f"rioxarray failed for {file_path}: {e}. Trying fallback.")
    
    # Fallback methods
    try:
        # Try xarray with rasterio engine (newer approach)
        if chunks:
            arr = xr.open_dataset(file_path, engine='rasterio', chunks=chunks)
            # Convert to DataArray if it's a Dataset
            if isinstance(arr, xr.Dataset):
                arr = arr.to_array().squeeze()
        else:
            arr = xr.open_dataset(file_path, engine='rasterio')
            if isinstance(arr, xr.Dataset):
                arr = arr.to_array().squeeze()
        return arr
    except Exception:
        pass
    
    try:
        # Legacy xr.open_rasterio (for older xarray versions)
        if chunks:
            arr = xr.open_rasterio(file_path, chunks=chunks)
        else:
            arr = xr.open_rasterio(file_path)
        return arr
    except AttributeError:
        # xr.open_rasterio doesn't exist in this version
        pass
    except Exception as e:
        warnings.warn(f"Legacy xr.open_rasterio failed: {e}")
    
    # Final fallback: use rasterio directly and create xarray manually
    try:
        with rasterio.open(file_path) as src:
            data = src.read()
            if data.shape[0] == 1:
                data = data[0]  # Remove band dimension for single band
            
            # Create coordinate arrays
            height, width = data.shape
            x_coords = np.linspace(src.bounds.left, src.bounds.right, width)
            y_coords = np.linspace(src.bounds.top, src.bounds.bottom, height)
            
            # Create DataArray
            arr = xr.DataArray(
                data,
                coords={'y': y_coords, 'x': x_coords},
                dims=['y', 'x'],
                attrs={'crs': str(src.crs) if src.crs else None}
            )
            
            if chunks:
                import dask.array as da
                arr = arr.chunk(chunks)
                
            return arr
            
    except Exception as e:
        raise RuntimeError(f"Failed to load raster {file_path} with all methods: {e}")


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
                arr = _open_raster_file(file_path, chunks={"x": 1024, "y": 1024})
                # Remove band dimension if it exists and has only one band
                if "band" in arr.dims and arr.sizes.get("band", 1) == 1:
                    arr = arr.squeeze("band", drop=True)
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
            arr = _open_raster_file(file_path)
            # Remove band dimension if it exists and has only one band
            if "band" in arr.dims and arr.sizes.get("band", 1) == 1:
                arr = arr.squeeze("band", drop=True)
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
