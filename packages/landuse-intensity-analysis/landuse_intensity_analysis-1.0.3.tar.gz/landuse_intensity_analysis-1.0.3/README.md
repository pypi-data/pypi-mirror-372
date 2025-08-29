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

```python
from landuse_intensity import LandUseAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = LandUseAnalyzer()

# Load land use data
data = pd.read_csv('land_use_data.csv')

# Perform intensity analysis
results = analyzer.analyze_intensity(data)

# Generate visualizations
analyzer.create_visualizations(results, output_dir='output/')
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

## Examples

See the `examples/` directory for complete usage examples:

- `dashboard.py`: Interactive web dashboard
- `simple_test.py`: Basic usage example
- `test_modern_openland.py`: Modern visualization examples

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up a development environment
- Code style and standards
- Testing guidelines
- Documentation requirements

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
