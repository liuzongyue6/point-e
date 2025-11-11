#!/usr/bin/env python3
"""
Example script demonstrating how to convert CAE files to Point-E compatible format.

This example shows:
1. Loading a CAE file with GRID, CQUAD4/CTRIA3, and PSHELL entries
2. Converting to Point-E point cloud format
3. Saving to NPZ or PLY format
4. Using custom color maps for different properties
"""

from pathlib import Path
from point_e.util.cae_parser import CAEParser, load_cae_file


def example_basic_conversion():
    """Basic example: load CAE file and convert to point cloud."""
    print("=" * 60)
    print("Example 1: Basic CAE to Point Cloud Conversion")
    print("=" * 60)
    
    # Load CAE file (adjust path to your file)
    cae_file = "/tmp/test_cae_file.cae"
    
    if not Path(cae_file).exists():
        print(f"Warning: Example file {cae_file} not found. Skipping example 1.")
        return
    
    # Convert to point cloud with default settings
    point_cloud = load_cae_file(
        cae_file,
        max_points=4096,  # Point-E typically uses 4096 points
        normalize=True     # Normalize coordinates to [-1, 1] range
    )
    
    print(f"Loaded point cloud with {len(point_cloud.coords)} points")
    print(f"Coordinate range: [{point_cloud.coords.min():.3f}, {point_cloud.coords.max():.3f}]")
    print(f"Channels: {list(point_cloud.channels.keys())}")
    
    # Save to NPZ format (compatible with Point-E)
    output_npz = "/tmp/converted_pointcloud.npz"
    point_cloud.save(output_npz)
    print(f"Saved to: {output_npz}")
    
    # Save to PLY format (for visualization in tools like MeshLab)
    output_ply = "/tmp/converted_pointcloud.ply"
    with open(output_ply, 'wb') as f:
        point_cloud.write_ply(f)
    print(f"Saved to: {output_ply}")
    print()


def example_with_custom_colors():
    """Example with custom color mapping based on property IDs."""
    print("=" * 60)
    print("Example 2: Custom Color Mapping")
    print("=" * 60)
    
    cae_file = "/tmp/test_cae_file.cae"
    
    if not Path(cae_file).exists():
        print(f"Warning: Example file {cae_file} not found. Skipping example 2.")
        return
    
    # Define custom colors for specific property IDs
    # Each color is (R, G, B) in range [0, 1]
    custom_color_map = {
        885657: (1.0, 0.0, 0.0),  # Red for property 885657
        # Add more property_id: (R, G, B) mappings as needed
    }
    
    # Parse and convert
    parser = CAEParser()
    parser.parse_file(cae_file)
    
    point_cloud = parser.to_point_cloud(
        max_points=4096,
        normalize=True,
        color_map=custom_color_map
    )
    
    print(f"Loaded point cloud with {len(point_cloud.coords)} points")
    print(f"Applied custom colors for {len(custom_color_map)} properties")
    print()


def example_detailed_inspection():
    """Example showing detailed inspection of parsed CAE data."""
    print("=" * 60)
    print("Example 3: Detailed CAE Data Inspection")
    print("=" * 60)
    
    cae_file = "/tmp/test_cae_file.cae"
    
    if not Path(cae_file).exists():
        print(f"Warning: Example file {cae_file} not found. Skipping example 3.")
        return
    
    # Parse CAE file
    parser = CAEParser()
    parser.parse_file(cae_file)
    
    # Inspect parsed data
    print(f"Number of GRID points: {len(parser.grids)}")
    print(f"Number of elements (CQUAD4/CTRIA3): {len(parser.elements)}")
    print(f"Number of properties (PSHELL): {len(parser.properties)}")
    
    # Show sample points
    print("\nSample GRID points:")
    for point_id in list(parser.grids.keys())[:3]:
        coords = parser.grids[point_id]
        prop_id = parser.get_point_color_from_property(point_id)
        print(f"  Point {point_id}: coords={coords}, property={prop_id}")
    
    # Show sample elements
    print("\nSample elements:")
    for elem_id in list(parser.elements.keys())[:3]:
        prop_id, point_ids = parser.elements[elem_id]
        print(f"  Element {elem_id}: property={prop_id}, points={point_ids}")
    
    # Show properties
    print("\nProperties:")
    for prop_id, prop_data in parser.properties.items():
        print(f"  Property {prop_id}: {prop_data}")
    
    print()


def example_downsampling_strategies():
    """Example showing different downsampling strategies."""
    print("=" * 60)
    print("Example 4: Downsampling Strategies")
    print("=" * 60)
    
    cae_file = "/tmp/test_cae_file.cae"
    
    if not Path(cae_file).exists():
        print(f"Warning: Example file {cae_file} not found. Skipping example 4.")
        return
    
    # Load without downsampling first
    point_cloud_full = load_cae_file(cae_file, max_points=100000, normalize=True)
    print(f"Original point cloud: {len(point_cloud_full.coords)} points")
    
    # Downsample using farthest point sampling (default, better distribution)
    point_cloud_fps = point_cloud_full.farthest_point_sample(100)
    print(f"After farthest point sampling: {len(point_cloud_fps.coords)} points")
    
    # Downsample using random sampling (faster, less uniform)
    point_cloud_random = point_cloud_full.random_sample(100)
    print(f"After random sampling: {len(point_cloud_random.coords)} points")
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CAE to Point-E Conversion Examples")
    print("=" * 60 + "\n")
    
    example_basic_conversion()
    example_with_custom_colors()
    example_detailed_inspection()
    example_downsampling_strategies()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
