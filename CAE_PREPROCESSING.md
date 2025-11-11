# CAE Format Preprocessing for Point-E

This module provides preprocessing tools for converting CAE (Computer-Aided Engineering) format files to Point-E compatible point clouds with color information.

## Overview

CAE format files typically contain structural analysis mesh data with the following components:

- **GRID**: Point coordinates in 3D space
- **CTRIA3/CQUAD4**: Triangular or quadrilateral elements connecting points
- **PSHELL**: Property definitions with unique PIDs (Property IDs)

This preprocessor reads CAE files, assigns unique colors to each PID, and converts the data to PointCloud format suitable for upsampling with Point-E models.

## CAE Format Specification

### GRID Format
```
GRID,<ID>,,<X>,<Y>,<Z>
```
Example:
```
GRID,4649,,2661.937,-433.604,113.7815
```

### Element Formats
```
CTRIA3,<element_id>,<pid>,<grid1>,<grid2>,<grid3>
CQUAD4,<element_id>,<pid>,<grid1>,<grid2>,<grid3>,<grid4>
```
Examples:
```
CTRIA3,1111015,885657,4653,4650,4652
CQUAD4,1111017,885657,4651,4650,4653,4649
```

### PSHELL Format
```
PSHELL,<pid>,<material_id>,<thickness>,...
```
Example:
```
PSHELL,885657,1,2.,1,,1,,0.,,+
```

## Color Assignment

Each point's color is determined by:
1. Finding all elements that contain the point (via GRID ID)
2. Extracting the PID from those elements
3. If a point belongs to multiple elements with different PIDs, colors are averaged
4. Each unique PID is assigned a distinct color using HSV color space

## Usage

### Basic Preprocessing

```python
from point_e.util.cae_preprocessor import CAEPreprocessor

# Load and preprocess CAE file
preprocessor = CAEPreprocessor()
preprocessor.parse_file('path/to/your_cae_file.txt')

# Convert to PointCloud
point_cloud = preprocessor.to_point_cloud()

# Save the point cloud
point_cloud.save('output.npz')
```

### Quick Conversion

```python
from point_e.util.cae_preprocessor import CAEPreprocessor

# One-line conversion
point_cloud = CAEPreprocessor.preprocess_cae_file('path/to/your_cae_file.txt')
```

### Visualization

```python
from point_e.util.cae_visualizer import visualize_point_cloud, print_point_cloud_stats

# Print statistics
print_point_cloud_stats(point_cloud)

# Create multi-view visualization
fig = visualize_point_cloud(
    point_cloud,
    title="My CAE Point Cloud",
    grid_size=2,
    figsize=(12, 12),
    point_size=50,
    output_path='visualization.png'
)
```

### Simple Single-View Visualization

```python
from point_e.util.cae_visualizer import visualize_point_cloud_simple

fig = visualize_point_cloud_simple(
    point_cloud,
    title="CAE Point Cloud",
    elev=20,
    azim=45,
    point_size=50,
    output_path='simple_view.png'
)
```

## Example Workflow

See the complete example in `point_e/examples/cae2pointcloud.ipynb`:

1. Load CAE format file
2. Convert to PointCloud with colors
3. Visualize the point cloud
4. (Optional) Apply Point-E upsampling models
5. Save results

## File Formats

### Input
- **CAE text files** (`.txt`, `.dat`, `.bdf`, etc.) containing GRID, CTRIA3/CQUAD4, and PSHELL entries

### Output
- **NPZ format** (`.npz`): NumPy compressed format with coordinates and color channels
- **PLY format** (`.ply`): Standard 3D point cloud format for use in other tools
- **PNG images** (`.png`): Visualizations of the point cloud

## Integration with Point-E Upsampling

The generated PointCloud objects are compatible with Point-E's upsampling pipeline:

```python
from point_e.diffusion.sampler import PointCloudSampler
from point_e.models.configs import MODEL_CONFIGS, model_from_config
from point_e.diffusion.configs import DIFFUSION_CONFIGS, diffusion_from_config

# Load your CAE data
point_cloud = CAEPreprocessor.preprocess_cae_file('cae_file.txt')

# Setup upsampling (requires trained models)
# Follow the pattern in text2pointcloud.ipynb
```

## Notes

- Points not belonging to any element are assigned a default gray color (0.5, 0.5, 0.5)
- PIDs not defined in PSHELL entries are assigned gray color
- Color averaging is used when points belong to multiple elements with different PIDs
- The coordinate system is preserved from the CAE file

## Requirements

- numpy
- matplotlib (for visualization)
- point_e (this package)

## See Also

- `point_e/examples/cae2pointcloud.ipynb` - Complete example notebook
- `point_e/examples/data/sample_cae.txt` - Sample CAE file
- `point_e/examples/text2pointcloud.ipynb` - Point-E upsampling example
