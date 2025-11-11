#!/usr/bin/env python3
"""
Command-line utility to convert CAE (Nastran format) files to Point-E compatible format.

Usage:
    python convert_cae.py input.cae output.npz [--max-points 4096] [--no-normalize]
    python convert_cae.py input.cae output.ply [--max-points 4096] [--no-normalize]
"""

import argparse
import sys
from pathlib import Path

from .cae_parser import load_cae_file


def main():
    parser = argparse.ArgumentParser(
        description='Convert CAE (Nastran format) files to Point-E compatible point clouds'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input CAE file path'
    )
    parser.add_argument(
        'output',
        type=str,
        help='Output file path (.npz or .ply format)'
    )
    parser.add_argument(
        '--max-points',
        type=int,
        default=4096,
        help='Maximum number of points (default: 4096, will downsample if needed)'
    )
    parser.add_argument(
        '--no-normalize',
        action='store_true',
        help='Do not normalize coordinates to [-1, 1] range'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Validate output format
    output_path = Path(args.output)
    output_ext = output_path.suffix.lower()
    if output_ext not in ['.npz', '.ply']:
        print(f"Error: Output format must be .npz or .ply, got {output_ext}", file=sys.stderr)
        sys.exit(1)
    
    # Load and convert CAE file
    print(f"Loading CAE file: {args.input}")
    try:
        point_cloud = load_cae_file(
            args.input,
            max_points=args.max_points,
            normalize=not args.no_normalize
        )
        print(f"Loaded point cloud with {len(point_cloud.coords)} points")
    except Exception as e:
        print(f"Error loading CAE file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save to output format
    print(f"Saving to: {args.output}")
    try:
        if output_ext == '.npz':
            point_cloud.save(args.output)
        elif output_ext == '.ply':
            with open(args.output, 'wb') as f:
                point_cloud.write_ply(f)
        print("Conversion complete!")
    except Exception as e:
        print(f"Error saving output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
