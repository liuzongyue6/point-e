#!/usr/bin/env python3
"""
Simple example script demonstrating CAE format preprocessing.

This script shows how to:
1. Load a CAE format file
2. Convert it to PointCloud format
3. Visualize the result
4. Save the point cloud
"""

import argparse
import matplotlib.pyplot as plt

from point_e.util.cae_preprocessor import CAEPreprocessor
from point_e.util.cae_visualizer import (
    visualize_point_cloud,
    visualize_point_cloud_simple,
    print_point_cloud_stats,
)


def main():
    parser = argparse.ArgumentParser(
        description="Convert CAE format file to PointCloud"
    )
    parser.add_argument(
        "input_file",
        help="Input CAE format file (e.g., sample_cae.txt)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output.npz",
        help="Output file for point cloud (default: output.npz)",
    )
    parser.add_argument(
        "--visualize",
        "-v",
        action="store_true",
        help="Display visualization",
    )
    parser.add_argument(
        "--save-viz",
        help="Save visualization to file (e.g., output.png)",
    )
    parser.add_argument(
        "--multi-view",
        action="store_true",
        help="Use multi-view visualization (default: single view)",
    )
    parser.add_argument(
        "--point-size",
        type=int,
        default=50,
        help="Size of points in visualization (default: 50)",
    )
    
    args = parser.parse_args()
    
    print(f"Loading CAE file: {args.input_file}")
    print()
    
    # Load and preprocess CAE file
    preprocessor = CAEPreprocessor()
    preprocessor.parse_file(args.input_file)
    
    print(f"Loaded {len(preprocessor.grids)} points")
    print(f"Loaded {len(preprocessor.elements)} elements")
    print(f"Found {len(preprocessor.pshells)} unique PIDs")
    print()
    
    # Convert to PointCloud
    point_cloud = preprocessor.to_point_cloud()
    
    # Print statistics
    print_point_cloud_stats(point_cloud)
    print()
    
    # Save point cloud
    print(f"Saving point cloud to: {args.output}")
    point_cloud.save(args.output)
    
    # Also save as PLY
    ply_output = args.output.rsplit('.', 1)[0] + '.ply'
    with open(ply_output, 'wb') as f:
        point_cloud.write_ply(f)
    print(f"Saved PLY format to: {ply_output}")
    print()
    
    # Visualization
    if args.visualize or args.save_viz:
        print("Creating visualization...")
        
        if args.multi_view:
            fig = visualize_point_cloud(
                point_cloud,
                output_path=args.save_viz,
                title="CAE Point Cloud - Multiple Views",
                grid_size=2,
                figsize=(12, 12),
                point_size=args.point_size,
            )
        else:
            fig = visualize_point_cloud_simple(
                point_cloud,
                output_path=args.save_viz,
                title="CAE Point Cloud",
                figsize=(10, 10),
                point_size=args.point_size,
            )
        
        if args.visualize:
            plt.show()
        else:
            plt.close(fig)
    
    print("Done!")


if __name__ == "__main__":
    main()
