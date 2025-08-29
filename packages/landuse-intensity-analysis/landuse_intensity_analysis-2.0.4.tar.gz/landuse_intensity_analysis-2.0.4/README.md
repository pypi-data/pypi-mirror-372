# Land Use Intensity Analysis 🌍

[![PyPI version](https://badge.fury.io/py/landuse-intensity-analysis.svg)](https://pypi.org/project/landuse-intensity-analysis/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A comprehensive Python library for scientifically rigorous land use change analysis using the Pontius-Aldwaik intensity analysis methodology.**

## 🌟 What does it do?

Transform your land cover raster data into meaningful insights about environmental change:

1. **Quantify Changes**: Calculate transition matrices and area statistics from multi-temporal raster data
2. **Intensity Analysis**: Apply the proven Pontius-Aldwaik methodology for interval, category, and transition-level analysis
3. **Rich Visualizations**: Create publication-ready Sankey diagrams, heatmaps, spatial maps, and statistical plots
4. **Spatial Analysis**: Process GeoTIFF files with built-in raster handling and spatial change detection

## ✨ Key Features

- 🔬 **Scientific Rigor**: Implements the established Pontius-Aldwaik intensity analysis methodology
- 📊 **Rich Visualizations**: Sankey diagrams, transition matrices, spatial maps, and statistical plots using matplotlib and plotly
- 🗺️ **Spatial Support**: Direct processing of GeoTIFF files and numpy arrays
- 🎯 **Object-Oriented Design**: Clean API with `ContingencyTable`, `IntensityAnalyzer`, and `MultiStepAnalyzer` classes
- 📈 **Multi-temporal Analysis**: Support for analyzing changes across multiple time periods
- 🔧 **Comprehensive Toolkit**: Complete suite of utility functions for data processing and validation

## 🚀 Installation

```bash
pip install landuse-intensity-analysis
```

## 📖 Quick Start

### Basic Analysis Example

```python
import numpy as np
import landuse_intensity as lui

# Step 1: Create contingency table from rasters
# Example with 2 time periods and 3 land use classes
raster_t1 = np.array([[1, 1, 2], [1, 2, 3], [2, 3, 3]])  # Time 1
raster_t2 = np.array([[1, 2, 2], [2, 2, 3], [3, 3, 3]])  # Time 2

# Create contingency table
ct = lui.ContingencyTable.from_rasters(
    raster_t1, raster_t2, 
    labels1=['Forest', 'Agriculture', 'Urban', 'Water'],
    labels2=['Forest', 'Agriculture', 'Urban', 'Water']
)

# Step 2: Run intensity analysis
analyzer = lui.IntensityAnalyzer(ct)
results = analyzer.full_analysis()

# Step 3: Display results
print("Contingency Table:")
print(ct.table)
print(f"\nTotal Change: {ct.total_change} pixels")
print(f"Persistence: {ct.persistence} pixels")

# Step 4: Create visualizations
from landuse_intensity import visualization as viz

# Sankey diagram
viz.plot_single_step_sankey(
    ct.table, 
    title="Land Use Transitions",
    save_path="sankey_diagram.html"
)

# Transition matrix heatmap
viz.plot_transition_matrix_heatmap(
    ct.table,
    title="Land Use Transition Matrix",
    save_path="transition_matrix.png"
)
```

### Working with Real Raster Files

```python
import landuse_intensity as lui

# Load raster data
raster1, metadata1 = lui.read_raster("land_cover_2000.tif")
raster2, metadata2 = lui.read_raster("land_cover_2020.tif")

# Create contingency table
contingency_df = lui.raster_to_contingency_table(
    raster1, raster2,
    class_names=['Forest', 'Agriculture', 'Urban', 'Water']
)

# Initialize analysis
ct = lui.ContingencyTable(contingency_df)
analyzer = lui.IntensityAnalyzer(ct)

# Perform complete analysis
results = analyzer.analyze()
print("Interval Level Analysis:", results['interval'])
print("Category Level Analysis:", results['category'])
```

### Multi-Temporal Analysis

```python
import landuse_intensity as lui

# Load multiple time periods
rasters = [
    lui.read_raster("land_cover_1990.tif")[0],
    lui.read_raster("land_cover_2000.tif")[0], 
    lui.read_raster("land_cover_2010.tif")[0],
    lui.read_raster("land_cover_2020.tif")[0]
]

time_labels = ['1990', '2000', '2010', '2020']

# Multi-step analysis
multi_analyzer = lui.MultiStepAnalyzer(rasters, time_labels)
multi_results = multi_analyzer.analyze_all_steps()

print("Multi-step Analysis Results:")
for step, result in multi_results.items():
    print(f"{step}: {result['interval']['annual_change_rate']:.2f}% annual change")
```

## � Complete API Reference

### Core Classes

#### ContingencyTable
Main class for handling transition matrices:

```python
# Create from rasters
ct = lui.ContingencyTable.from_rasters(raster1, raster2, labels1, labels2)

# Create from existing data  
ct = lui.ContingencyTable(dataframe_or_array)

# Properties
ct.table              # Access transition matrix
ct.total_area        # Total number of pixels/area
ct.persistence       # Unchanged pixels
ct.total_change      # Changed pixels
ct.validate()        # Validate table structure
```

#### IntensityAnalyzer
Implements Pontius-Aldwaik intensity analysis:

```python
analyzer = lui.IntensityAnalyzer(contingency_table)

# Analysis methods
analyzer.analyze_interval_level()    # Overall change intensity
analyzer.analyze_category_level()    # Class-specific gains/losses  
analyzer.analyze_transition_level(from_class, to_class)  # Transition intensity
analyzer.analyze()                   # Complete analysis
analyzer.full_analysis()            # Returns AnalysisResults object
```

#### MultiStepAnalyzer
For multi-temporal analysis:

```python
analyzer = lui.MultiStepAnalyzer(raster_list, time_labels)

analyzer.analyze_all_steps()         # Step-by-step analysis
analyzer.analyze_overall_change()    # Overall change summary
analyzer.compare_step_vs_overall()   # Compare step vs overall rates
```

#### ChangeAnalyzer
For spatial change detection:

```python
change_analyzer = lui.ChangeAnalyzer(raster1, raster2)

change_analyzer.analyze()            # Basic change detection
change_analyzer.detect_hotspots()    # Change hotspot detection
change_analyzer.create_change_map()  # Spatial change mapping
```

### Visualization Functions

#### Graph Visualizations
From `landuse_intensity.graph_visualization`:

```python
from landuse_intensity import graph_visualization as gv

# Sankey diagrams
gv.plot_single_step_sankey(
    contingency_table, 
    title="Land Use Transitions",
    save_path="sankey.html"
)

# Transition matrix heatmaps
gv.plot_transition_matrix_heatmap(
    contingency_table,
    title="Transition Matrix",
    save_path="heatmap.png"
)

# Bar plots for LULC analysis
gv.plot_barplot_lulc(
    lulc_data,
    title="Land Use Areas",
    save_path="barplot.png"
)

# Gain/Loss analysis
gv.plot_gain_loss_analysis(
    contingency_table,
    title="Gain/Loss Analysis"
)

# Accuracy assessment
gv.plot_accuracy_assessment(
    observed, predicted,
    save_path="accuracy.png"
)

# Confusion matrix
gv.plot_confusion_matrix(
    true_labels, predicted_labels
)
```

#### Spatial Visualizations  
From `landuse_intensity.map_visualization`:

```python
from landuse_intensity import map_visualization as mv

# Spatial change maps
mv.plot_spatial_change_map(
    raster_t1, raster_t2,
    title="Land Use Change Map",
    save_path="change_map.png"
)

# Multi-temporal maps
mv.plot_multi_temporal_maps(
    raster_list, time_labels,
    title="Land Use Over Time"
)

# Change detection
mv.plot_change_detection_map(
    raster_t1, raster_t2,
    title="Change Detection"
)

# Interactive maps
mv.plot_interactive_map(
    raster_data, coordinates,
    save_path="interactive_map.html"
)

# Elevation models
mv.plot_elevation_model(
    elevation_raster,
    title="Digital Elevation Model"
)
```

#### Advanced Visualizations
From `landuse_intensity.visualization`:

```python
from landuse_intensity import visualization as viz

# Intensity analysis plots
viz.plot_intensity_analysis(
    intensity_results,
    title="Pontius Intensity Analysis"
)

# Multi-step Sankey
viz.plot_multi_step_sankey(
    transitions_list,
    time_labels=time_labels
)

# Spatial change with persistence
viz.plot_persistence_map(
    raster_t1, raster_t2,
    title="Persistence Analysis"
)

# Temporal land change
viz.plot_temporal_land_change(
    raster_list, time_labels,
    save_path="temporal_change.png"
)

# Change frequency mapping
viz.plot_change_frequency_map(
    raster_list,
    title="Change Frequency Analysis"
)
```

### Utility Functions

#### Data Processing
```python
import landuse_intensity as lui

# Demo data generation
raster_t1, raster_t2 = lui.demo_landscape()

# Data validation
is_valid = lui.validate_data(raster_data)

# Area calculations
area_matrix = lui.calculate_area_matrix(contingency_table, pixel_area=900)

# Change summary
summary = lui.get_change_summary(contingency_table)

# Area formatting
label = lui.format_area_label(1500.5, units="hectares")

# Transition naming
names = lui.create_transition_names(
    from_classes=['Forest', 'Agriculture'], 
    to_classes=['Urban', 'Water']
)
```

#### Image Processing
```python
import landuse_intensity as lui

# Create contingency table from rasters
ct = lui.create_contingency_table(raster1, raster2, labels=['Forest', 'Urban'])

# Calculate change map
change_map = lui.calculate_change_map(raster_t1, raster_t2)

# Apply majority filter  
filtered = lui.apply_majority_filter(raster, window_size=3)

# Calculate patch metrics
metrics = lui.calculate_patch_metrics(raster, class_value=1)

# Resample raster
resampled = lui.resample_raster(raster, target_shape=(100, 100))

# Align rasters
aligned1, aligned2 = lui.align_rasters(raster1, raster2)

# Validate raster
is_valid = lui.validate_raster(raster)

# Mask raster
masked = lui.mask_raster(raster, mask, nodata_value=-9999)
```

#### Raster Handling
```python
import landuse_intensity as lui

# Read raster file
raster_data, metadata = lui.read_raster("landcover.tif")

# Write raster file
lui.write_raster(
    raster_data, "output.tif", 
    metadata=metadata,
    nodata_value=-9999
)

# Convert rasters to contingency table
contingency_df = lui.raster_to_contingency_table(
    raster1, raster2,
    class_names=['Forest', 'Agriculture', 'Urban']
)

# Load demo data
demo_raster1, demo_raster2 = lui.load_demo_data()

# Raster summary statistics
summary = lui.raster_summary(raster)

# Reclassify raster
reclassified = lui.reclassify_raster(
    raster, 
    reclass_dict={1: 10, 2: 20, 3: 30}
)
```

## 📊 Analysis Functions

### Main Analysis Function
```python
# One-step comprehensive analysis
results = lui.analyze_land_use_change(
    raster1=raster_t1,
    raster2=raster_t2, 
    area_calculation=True,
    intensity_analysis=True,
    save_tables=True,
    output_dir="./results/"
)
```

## 🎯 Complete Example: Real Dataset Analysis

```python
import landuse_intensity as lui
import numpy as np

# 1. Load real raster data
raster_2000, meta_2000 = lui.read_raster("cerrado_2000.tif")
raster_2010, meta_2010 = lui.read_raster("cerrado_2010.tif") 
raster_2020, meta_2020 = lui.read_raster("cerrado_2020.tif")

# 2. Create contingency tables
ct_2000_2010 = lui.ContingencyTable.from_rasters(
    raster_2000, raster_2010,
    labels1=['Forest', 'Savanna', 'Agriculture', 'Pasture', 'Urban'],
    labels2=['Forest', 'Savanna', 'Agriculture', 'Pasture', 'Urban']
)

ct_2010_2020 = lui.ContingencyTable.from_rasters(
    raster_2010, raster_2020,
    labels1=['Forest', 'Savanna', 'Agriculture', 'Pasture', 'Urban'],
    labels2=['Forest', 'Savanna', 'Agriculture', 'Pasture', 'Urban']
)

# 3. Intensity analysis
analyzer_2000_2010 = lui.IntensityAnalyzer(ct_2000_2010)
analyzer_2010_2020 = lui.IntensityAnalyzer(ct_2010_2020)

results_2000_2010 = analyzer_2000_2010.analyze()
results_2010_2020 = analyzer_2010_2020.analyze()

# 4. Multi-temporal analysis
multi_analyzer = lui.MultiStepAnalyzer(
    [raster_2000, raster_2010, raster_2020],
    ['2000', '2010', '2020']
)
multi_results = multi_analyzer.analyze_all_steps()

# 5. Create visualizations
from landuse_intensity import graph_visualization as gv
from landuse_intensity import map_visualization as mv

# Sankey diagrams for each period
gv.plot_single_step_sankey(
    ct_2000_2010.table,
    title="Cerrado Land Use Transitions 2000-2010",
    save_path="sankey_2000_2010.html"
)

gv.plot_single_step_sankey(
    ct_2010_2020.table, 
    title="Cerrado Land Use Transitions 2010-2020",
    save_path="sankey_2010_2020.html"
)

# Spatial change maps
mv.plot_spatial_change_map(
    raster_2000, raster_2020,
    title="Cerrado Land Use Change 2000-2020",
    save_path="cerrado_change_map.png"
)

# Multi-temporal maps
mv.plot_multi_temporal_maps(
    [raster_2000, raster_2010, raster_2020],
    ['2000', '2010', '2020'],
    title="Cerrado Land Use Evolution"
)

# 6. Export results
print("=== ANALYSIS RESULTS ===")
print(f"Period 2000-2010:")
print(f"  Annual change rate: {results_2000_2010['interval']['annual_change_rate']:.2f}%")
print(f"  Total change: {ct_2000_2010.total_change} pixels")

print(f"Period 2010-2020:")  
print(f"  Annual change rate: {results_2010_2020['interval']['annual_change_rate']:.2f}%")
print(f"  Total change: {ct_2010_2020.total_change} pixels")

# Export contingency tables
ct_2000_2010.table.to_csv("contingency_2000_2010.csv")
ct_2010_2020.table.to_csv("contingency_2010_2020.csv")
```

## 📚 References

This library implements the Pontius-Aldwaik intensity analysis methodology:

- Aldwaik, S. Z., & Pontius Jr, R. G. (2012). Intensity analysis to unify measurements of size and stationarity of land changes by interval, category, and transition. *Landscape and Urban Planning*, 106(1), 103-114.

- Pontius Jr, R. G., & Millones, M. (2011). Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing*, 32(15), 4407-4429.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📮 Support

If you encounter any issues or have questions:

1. Check the examples in the `examples/` directory
2. Read the documentation
3. Open an issue on GitHub

## 🎯 Version Information

- **Current Version**: 2.0.3
- **Python Requirements**: Python 3.8+
- **Key Dependencies**: numpy, pandas, matplotlib, plotly, rasterio

---

*Made with ❤️ for the geospatial and environmental science community*

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
