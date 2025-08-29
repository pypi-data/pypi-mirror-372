# Land Use Intensity Analysis

[![PyPI version](https://badge.fury.io/py/landuse-intensity-analysis.svg)](https://pypi.org/project/landuse-intensity-analysis/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://landuse-intensity-analysis.readthedocs.io/)

A comprehensive Python library for land use intensity analysis based on the Pontius-Aldwaik methodology. This package provides tools for analyzing land use change patterns, intensity analysis, and spatial-temporal dynamics using remote sensing data.

## Features

- **Pontius-Aldwaik Intensity Analysis**: Full implementation of the intensity analysis methodology
- **Multi-temporal Analysis**: Compare land use changes across multiple time periods
- **Spatial Analysis**: Advanced spatial mapping and visualization capabilities
- **Modern Visualizations**: Interactive plots using Plotly and HoloViews
- **Performance Optimized**: Parallel processing and caching for large datasets
- **Extensible Architecture**: Modular design for custom analysis workflows

## Installation

### Basic Installation

```bash
pip install landuse-intensity-analysis
```

### With Optional Dependencies

```bash
# For spatial analysis
pip install landuse-intensity-analysis[spatial]

# For parallel processing
pip install landuse-intensity-analysis[parallel]

# For data compression
pip install landuse-intensity-analysis[compression]

# Development dependencies
pip install landuse-intensity-analysis[dev]

# Documentation dependencies
pip install landuse-intensity-analysis[docs]

# Complete installation
pip install landuse-intensity-analysis[complete]
```

## Quick Start

### Basic Usage

```python
from landuse_intensity import LandUseAnalyzer

# Initialize analyzer
analyzer = LandUseAnalyzer()

# Quick analysis with automatic data loading
results = analyzer.quick_analysis("path/to/raster/directory")

# Access results
print(f"Analysis completed in {results.execution_time:.2f} seconds")
```

### Loading Raster Data Directly

The package supports multiple ways to load raster data:

#### 1. Directory-based Loading (Automatic)

```python
from landuse_intensity import LandUseAnalyzer

# Load all GeoTIFF files from a directory
analyzer = LandUseAnalyzer()
results = analyzer.quick_analysis("data/landuse_maps/")
```

#### 2. Direct Raster Loading

```python
from landuse_intensity.raster import load_rasters
import xarray as xr

# Load specific raster files
rasters = load_rasters([
    "landuse_1990.tif",
    "landuse_2000.tif",
    "landuse_2010.tif"
])

# Or load from directory
rasters = load_rasters("path/to/raster/directory")

# Convert to DataFrame for analysis
from landuse_intensity.raster import summary_dir
df = summary_dir(rasters)
```

#### 3. Individual Raster Processing

```python
from landuse_intensity.raster import summary_map

# Process single raster file
summary = summary_map("landuse_1990.tif")
print(summary)
```

### Complete Analysis Workflow

For a comprehensive step-by-step analysis from data loading to final results:

```python
from landuse_intensity.raster import load_rasters
from landuse_intensity import contingency_table, intensity_analysis
from landuse_intensity.visualization import plot_transition_matrix
from landuse_intensity.modern_viz import create_modern_visualizations

# Step 1: Load raster data
rasters = load_rasters("data/")

# Step 2: Generate contingency table
ct = contingency_table(rasters)

# Step 3: Run intensity analysis
intensity_results = intensity_analysis(ct)

# Step 4: Create visualizations
transition_plot = plot_transition_matrix(ct)
modern_plots = create_modern_visualizations(ct, intensity_results)

# Step 5: Save results
transition_plot.write_html("outputs/transition_matrix.html")
for name, plot in modern_plots.items():
    plot.write_html(f"outputs/{name}.html")
```

### Complete Analysis Workflow

The library provides a streamlined workflow for conducting comprehensive land use intensity analysis.

### Supported Raster Formats

- **GeoTIFF** (.tif, .tiff)
- **Any format supported by rasterio/xarray**
- **Multi-band and single-band rasters**
- **Time series data**

### Data Requirements

- **Coordinate System**: Any projected CRS
- **Data Type**: Integer (categorical land use classes)
- **NoData Values**: Automatically detected and handled
- **File Organization**: Use consistent naming (e.g., landuse_1990.tif, landuse_2000.tif)

### Sankey Diagrams for Land Transitions

Create interactive flow diagrams to visualize land use transitions:

```python
from landuse_intensity.modern_viz import create_sankey_diagram

# Create interactive Sankey diagram
sankey_fig = create_sankey_diagram(
    contingency_table,
    title="Land Use Transitions Flow",
    color_palette=['#2E8B57', '#FFD700', '#8FBC8F', '#DC143C']
)

# Export to interactive HTML
sankey_fig.write_html("land_transitions_sankey.html")
```

**Features:**

- **Interactive Flow Visualization**: Click and hover for detailed transition information
- **Color-Coded Links**: Each land use class has distinct colors with opacity
- **Responsive Design**: Adapts to different screen sizes
- **Export Options**: HTML (interactive), PNG (static), SVG (vector)
- **Advanced Version**: Integrates with intensity analysis results

### Intelligent Contingency Table Analysis

The `contingency_table` function now features intelligent automatic detection of analysis type based on the established methodology:

```python
from landuse_intensity.analysis import contingency_table

# Intelligent auto-detection (recommended)
result = contingency_table(
    input_raster=["landuse_1990.tif", "landuse_2000.tif", "landuse_2010.tif"],
    analysis_type="auto",  # Automatically detects multi-step vs one-step
    pixel_resolution=30.0
)

# The function automatically:
# - Detects 3+ periods → Multi-step analysis (1990→2000, 2000→2010)
# - Detects 2 periods → One-step analysis (1990→2010)
# - Returns appropriate results structure

# Access results
if 'lulc_Multistep' in result:
    multistep_data = result['lulc_Multistep']
    print(f"Multi-step periods: {multistep_data['Period'].unique()}")

if 'lulc_Onestep' in result:
    onestep_data = result['lulc_Onestep']
    print(f"One-step period: {onestep_data['Period'].iloc[0]}")
```

**Analysis Types:**

- **`"auto"`** (Recommended): Automatically detects analysis type
  - 2 periods → One-step analysis
  - 3+ periods → Multi-step analysis

- **`"multistep"`**: Forces multi-step analysis (consecutive pairs)
- **`"onestep"`**: Forces one-step analysis (first to last)

**Benefits:**

- **Smart Detection**: No need to manually specify analysis type
- **Methodology Compatible**: Follows established methodology
- **Flexible**: Override auto-detection when needed
- **Unified Interface**: Single function for all analysis types

### Raster Stacking and Year Detection

#### Raster Stacking Options

**1. Automatic Directory Loading:**

```python
from landuse_intensity.raster import load_rasters

# Load all .tif files from directory
rasters = load_rasters("data/landuse/")
# Automatically finds and stacks: landuse_1990.tif, landuse_2000.tif, landuse_2010.tif
```

**2. Manual File Selection:**

```python
# Load specific files in custom order
files = ["landuse_1990.tif", "landuse_2005.tif", "landuse_2010.tif"]
rasters = load_rasters(files)
```

#### Year Detection Strategies

**Default (year_position='last'):**

```python
from landuse_intensity import contingency_table

# For files: GLAD_LULC_recortado_1990.tif, GLAD_LULC_recortado_2000.tif
ct = contingency_table("data/", year_position="last")  # Extracts: 1990, 2000
```

**Custom Position:**

```python
# For files: GLAD_LULC_1990_recortado.tif (year in position 2)
ct = contingency_table("data/", year_position=2)
```

**Regex Pattern:**

```python
# For complex filenames like: ESACCI-LC-L4-LCCS-Map-300m-P1Y-2000-v2.0.7cds.tif
ct = contingency_table("data/", name_pattern=r"P1Y-(\d{4})")
```

**Custom Separator:**

```python
# For files: landuse-1990-final.tif
ct = contingency_table("data/", name_separator="-", year_position=1)
```

## Scientific Background

This library implements the Pontius-Aldwaik intensity analysis methodology, which provides a comprehensive framework for understanding land use change patterns. The methodology distinguishes between:

- **Quantity of change**: How much land changed category
- **Exchange**: Land that would have changed even if proportions remained constant
- **Shift**: Land that changed due to systematic transitions

## API Reference

### Core Classes

#### `LandUseAnalyzer`

Main class for performing land use intensity analysis.

**Methods:**

- `analyze_intensity(data)`: Perform complete intensity analysis
- `create_visualizations(results, output_dir)`: Generate visualization outputs
- `validate_data(data)`: Validate input data format
- `export_results(results, format='json')`: Export analysis results

### Data Format

The library expects land use data in the following format:

```python
data = {
    'year': [1990, 2000, 2010],
    'land_use_category': ['forest', 'agriculture', 'urban'],
    'area': [1000, 800, 1200],
    'coordinates': [(x1, y1), (x2, y2), (x3, y3)]
}
```

## Visualization Gallery

The library provides several types of visualizations:

- **Intensity Maps**: Spatial distribution of land use intensity
- **Transition Matrices**: Category transition probabilities
- **Time Series Plots**: Temporal evolution of land use patterns
- **Chord Diagrams**: Flow visualization between categories
- **Sankey Diagrams**: Flow-based transition visualization

## Advanced Usage

### Custom Configuration

```python
from landuse_intensity import LandUseConfig

config = LandUseConfig(
    analysis_method='pontius',
    spatial_resolution=30,
    temporal_window=10,
    enable_caching=True,
    parallel_processing=True
)

analyzer = LandUseAnalyzer(config=config)
```

### Parallel Processing

```python
# Enable parallel processing for large datasets
config = LandUseConfig(parallel_processing=True, max_workers=4)
analyzer = LandUseAnalyzer(config=config)

# Process multiple time periods
results = analyzer.batch_analyze(data_list)
```

### Spatial Analysis

```python
# Load geospatial data
import rasterio
import xarray as xr

with rasterio.open('land_use_1990.tif') as src:
    data_1990 = src.read(1)

with rasterio.open('land_use_2000.tif') as src:
    data_2000 = src.read(1)

# Perform spatial intensity analysis
spatial_results = analyzer.spatial_intensity_analysis(
    data_1990, data_2000,
    transform=src.transform
)
```

## 📚 Complete Documentation

## Usage

### 🔧 Key Features

- **Raster Loading**: Multiple methods (automatic, manual, dataset)
- **Year Detection**: Automatic year extraction from filenames
- **Contingency Tables**: Transition matrix generation
- **Intensity Analysis**: Pontius-Aldwaik methodology
- **Visualizations**: Modern interactive plots
- **Change Maps**: Spatial analysis and mapping
- **Export Options**: CSV, JSON, HTML formats

### 📋 Complete Analysis Workflow

```python
# 1. Load raster data
from landuse_intensity.raster import load_rasters
rasters = load_rasters("data/")

# 2. Generate contingency table
from landuse_intensity.analysis import contingency_table
ct = contingency_table(rasters)

# 3. Perform intensity analysis
from landuse_intensity.intensity import intensity_analysis
results = intensity_analysis(ct)

# 4. Create visualizations
from landuse_intensity.modern_viz import create_modern_visualizations
create_modern_visualizations(ct, results)

# 5. Generate change maps
from landuse_intensity.visualization import create_change_maps
create_change_maps(rasters)

# 6. Export results
from landuse_intensity.utils import export_to_csv
export_to_csv(results, "analysis_results.csv")
```

## Examples

The library includes comprehensive examples demonstrating various land use analysis capabilities:

```python
# Basic intensity analysis example
from landuse_intensity.analyzer import LandUseAnalyzer

# Initialize analyzer
analyzer = LandUseAnalyzer()

# Load data and run analysis
results = analyzer.analyze_from_rasters([
    "landuse_1990.tif",
    "landuse_2000.tif",
    "landuse_2010.tif"
])

# Generate visualizations
analyzer.create_all_visualizations(results)
```

## Contributing

We welcome contributions! Please see our GitHub repository for details on contributing to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{landuse_intensity_analysis,
  title = {Land Use Intensity Analysis},
  author = {LandUse Intensity Analysis Contributors},
  url = {https://github.com/your-repo/landuse-intensity-analysis},
  version = {1.0.3a1},
  date = {2024}
}
```

## Support

- **Documentation**: [Read the Docs](https://landuse-intensity-analysis.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/landuse-intensity-analysis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/landuse-intensity-analysis/discussions)

## Related Projects

- [Pontius Research Group](https://www.clarku.edu/departments/geography/pontius/): Original methodology developers
- [GDAL](https://gdal.org/): Geospatial data processing
- [Rasterio](https://rasterio.readthedocs.io/): Python geospatial raster processing
- [Xarray](https://xarray.pydata.org/): N-dimensional arrays for Python
