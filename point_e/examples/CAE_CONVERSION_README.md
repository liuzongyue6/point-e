# CAE File to Point-E Converter

This module provides tools to convert CAE (Nastran format) files into Point-E compatible point cloud format.

## Overview

CAE files commonly used in finite element analysis (FEA) contain:
- **GRID entries**: Define point coordinates (ID, X, Y, Z)
- **CQUAD4/CTRIA3 entries**: Define quadrilateral/triangular elements that connect points
- **PSHELL entries**: Define shell properties that can be used for color assignment

This converter parses these entries, assigns colors based on element properties, and produces point clouds that Point-E can use for 3D generation tasks.

## Features

- ✅ Parse Nastran format CAE files with GRID, CQUAD4, CTRIA3, and PSHELL entries
- ✅ Handle concatenated coordinate values (e.g., `2661.937-433.604113.7815`)
- ✅ Automatic color assignment based on property IDs
- ✅ Custom color mapping support
- ✅ Coordinate normalization to Point-E's expected range
- ✅ Intelligent downsampling using farthest point sampling
- ✅ Export to NPZ (Point-E native) or PLY format

## Installation

The CAE parser is included with point-e. Simply install:

```bash
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Convert CAE to NPZ format (Point-E native format)
python -m point_e.util.convert_cae input.cae output.npz --max-points 4096

# Convert CAE to PLY format (for visualization)
python -m point_e.util.convert_cae input.cae output.ply --max-points 4096

# Without coordinate normalization
python -m point_e.util.convert_cae input.cae output.npz --no-normalize
```

### Python API Usage

```python
from point_e.util.cae_parser import load_cae_file

# Simple conversion
point_cloud = load_cae_file(
    'input.cae',
    max_points=4096,      # Downsample to 4096 points
    normalize=True        # Normalize coordinates to [-1, 1]
)

# Save in Point-E format
point_cloud.save('output.npz')

# Or save as PLY for visualization
with open('output.ply', 'wb') as f:
    point_cloud.write_ply(f)
```

### Advanced Usage with Custom Colors

```python
from point_e.util.cae_parser import CAEParser

# Parse CAE file
parser = CAEParser()
parser.parse_file('input.cae')

# Define custom color mapping (property_id -> RGB tuple)
custom_colors = {
    885657: (1.0, 0.0, 0.0),  # Red
    885658: (0.0, 1.0, 0.0),  # Green
    885659: (0.0, 0.0, 1.0),  # Blue
}

# Convert with custom colors
point_cloud = parser.to_point_cloud(
    max_points=4096,
    normalize=True,
    color_map=custom_colors
)
```

## Input Format

The parser expects Nastran format CAE files with the following entries:

### GRID Format
```
GRID        4649        2661.937-433.604113.7815
```
- Fixed width fields (8 characters each)
- Field 1: "GRID"
- Field 2: Point ID
- Fields 3-5: X, Y, Z coordinates (may be concatenated)

### CQUAD4 Format (Quadrilateral Elements)
```
CQUAD4   1111017  885657    4651    4650    4653    4649
```
- Field 1: "CQUAD4"
- Field 2: Element ID
- Field 3: Property ID
- Fields 4-7: Four point IDs defining the quad

### CTRIA3 Format (Triangular Elements)
```
CTRIA3   1111015  885657    4653    4650    4652
```
- Field 1: "CTRIA3"
- Field 2: Element ID
- Field 3: Property ID
- Fields 4-6: Three point IDs defining the triangle

### PSHELL Format (Shell Properties)
```
PSHELL    885657       1      2.       1               1              0.
```
- Field 1: "PSHELL"
- Field 2: Property ID
- Fields 3+: Material and thickness data

## Output Format

The converter produces Point-E compatible point clouds:

### NPZ Format (Point-E Native)
```python
{
    'coords': np.ndarray(shape=(N, 3), dtype=float32),  # XYZ coordinates
    'R': np.ndarray(shape=(N,), dtype=float32),         # Red channel [0, 1]
    'G': np.ndarray(shape=(N,), dtype=float32),         # Green channel [0, 1]
    'B': np.ndarray(shape=(N,), dtype=float32),         # Blue channel [0, 1]
}
```

### PLY Format
Binary PLY format with vertices and RGB colors, compatible with MeshLab, CloudCompare, and other 3D visualization tools.

## Downsampling

When the input has more points than `max_points`, the converter uses **farthest point sampling** by default, which provides better spatial distribution than random sampling. This ensures the downsampled point cloud still represents the overall geometry well.

## Examples

See [cae_conversion_example.py](cae_conversion_example.py) for comprehensive examples including:
1. Basic conversion
2. Custom color mapping
3. Detailed data inspection
4. Different downsampling strategies

## Coordinate Normalization

By default, coordinates are normalized to roughly fit in the [-1, 1] range:
1. Points are centered (subtract mean)
2. Scaled by the maximum absolute extent

This normalization helps Point-E process the geometry consistently. Disable with `--no-normalize` or `normalize=False` if needed.

## Color Assignment

Colors are assigned based on the property ID of the element(s) containing each point:
1. Each point is mapped to its containing elements (CQUAD4/CTRIA3)
2. The property ID (PSHELL) of the first containing element is used
3. Each unique property ID gets a distinct color
4. Colors are generated using HSV space for maximum distinction

You can override this with a custom `color_map` dictionary.

## Troubleshooting

### "Cannot parse coordinates from..."
Your CAE file may have concatenated coordinates. The parser tries to handle formats like `2661.937-433.604113.7815`, but if parsing fails, verify the coordinate format matches Nastran specifications.

### "No GRID data found"
Ensure your CAE file contains GRID entries. Lines must start with "GRID" (case-sensitive).

### Points have no color / all same color
Verify that:
1. CQUAD4/CTRIA3 entries reference your GRID point IDs
2. PSHELL entries exist with the property IDs used in elements
3. The property ID mapping is correct

## License

This code is part of the Point-E project and follows the same license.
