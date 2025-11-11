#!/usr/bin/env python3
"""
Integration example: Convert CAE file to Point-E format and use it with Point-E models.

This example demonstrates the complete workflow:
1. Load and convert a CAE file
2. Prepare it for Point-E input
3. Show how it integrates with Point-E's existing tools
"""

from pathlib import Path
import numpy as np
from point_e.util.cae_parser import load_cae_file
from point_e.util.plotting import plot_point_cloud


def create_sample_cae_file(output_path: str):
    """Create a sample CAE file for demonstration."""
    content = """$2345678$2345678$2345678$2345678$2345678$2345678
GRID        4649        2661.937-433.604113.7815
GRID        4650        2662.825-436.489116.7319
GRID        4651        2662.018-433.853116.4177
GRID        4652        2663.893-440.114114.9757
GRID        4653        2662.735-436.186114.3488
GRID       84005        2660.5  -430.5   112.0
GRID       84006        2665.0  -432.0   115.5
GRID       84007        2658.0  -435.0   110.0
GRID       84008        2656.5  -438.5   111.2
GRID       84009        2667.0  -442.0   117.8
GRID       10507        2660.0  -433.0   109.5
GRID        5038        2669.5  -441.5   118.5
CQUAD4   1111014  885657   84005    4649    4653   84006
CTRIA3   1111015  885657    4653    4650    4652
CQUAD4   1111016  885657   84008   84007    4649   84005
CQUAD4   1111017  885657    4651    4650    4653    4649
CQUAD4   1111018  885657    4652    4650   84009    5038
CQUAD4   1111019  885657    4651    4649   84007   10507
PSHELL    885657       1      2.       1               1              0.
"""
    
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created sample CAE file: {output_path}")


def main():
    print("=" * 70)
    print("CAE to Point-E Integration Example")
    print("=" * 70)
    print()
    
    # Create a sample CAE file
    cae_file = "/tmp/sample_integration.cae"
    create_sample_cae_file(cae_file)
    print()
    
    # Convert CAE to Point-E format
    print("Converting CAE to Point-E format...")
    point_cloud = load_cae_file(
        cae_file,
        max_points=4096,  # Point-E typically uses 4096 points
        normalize=True     # Normalize to [-1, 1] range
    )
    print(f"✓ Loaded point cloud with {len(point_cloud.coords)} points")
    print(f"  Coordinate range: [{point_cloud.coords.min():.3f}, {point_cloud.coords.max():.3f}]")
    print(f"  Channels: {list(point_cloud.channels.keys())}")
    print()
    
    # Save to Point-E's native format
    npz_output = "/tmp/cae_pointcloud.npz"
    point_cloud.save(npz_output)
    print(f"✓ Saved to Point-E format: {npz_output}")
    print()
    
    # Verify the format matches Point-E expectations
    print("Verifying Point-E compatibility...")
    data = np.load(npz_output)
    print(f"  ✓ Contains 'coords': shape {data['coords'].shape}")
    print(f"  ✓ Contains 'R': shape {data['R'].shape}, range [{data['R'].min():.2f}, {data['R'].max():.2f}]")
    print(f"  ✓ Contains 'G': shape {data['G'].shape}, range [{data['G'].min():.2f}, {data['G'].max():.2f}]")
    print(f"  ✓ Contains 'B': shape {data['B'].shape}, range [{data['B'].min():.2f}, {data['B'].max():.2f}]")
    print()
    
    # Demonstrate visualization
    print("Visualizing point cloud...")
    try:
        # Generate a matplotlib figure
        fig = plot_point_cloud(
            point_cloud,
            grid_size=2,
            fixed_bounds=((-1, -1, -1), (1, 1, 1))
        )
        
        # Save the visualization
        viz_output = "/tmp/cae_pointcloud_viz.png"
        fig.savefig(viz_output, dpi=100, bbox_inches='tight')
        print(f"✓ Saved visualization: {viz_output}")
        print()
    except Exception as e:
        print(f"Note: Visualization not saved (requires matplotlib): {e}")
        print()
    
    # Show how this can be used with Point-E models
    print("Integration with Point-E models:")
    print("-" * 70)
    print("This point cloud can now be used with Point-E models:")
    print()
    print("1. As conditioning input for image-to-3D models:")
    print("   from point_e.diffusion.sampler import PointCloudSampler")
    print("   # Use the point cloud as conditioning...")
    print()
    print("2. For mesh generation:")
    print("   from point_e.util.pc_to_mesh import marching_cubes_mesh")
    print("   # Convert point cloud to mesh...")
    print()
    print("3. For evaluation and comparison:")
    print("   # Compare generated point clouds with your CAE-derived reference")
    print()
    
    print("=" * 70)
    print("Integration example complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Input CAE file: {cae_file}")
    print(f"  - Output NPZ file: {npz_output}")
    print(f"  - Point cloud: {len(point_cloud.coords)} points with RGB colors")
    print(f"  - Ready for use with Point-E models!")


if __name__ == '__main__':
    main()
