"""
Visualization post-processing tool for point clouds with colors.

This module provides utilities for visualizing point clouds,
particularly those generated from CAE format files.
"""

from typing import Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from .point_cloud import PointCloud


def visualize_point_cloud(
    pc: PointCloud,
    output_path: Optional[str] = None,
    title: str = "Point Cloud Visualization",
    grid_size: int = 2,
    figsize: Tuple[int, int] = (12, 12),
    fixed_bounds: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None,
    show_axes: bool = True,
    point_size: int = 1,
) -> plt.Figure:
    """
    Visualize a point cloud with colors from multiple angles.
    
    Args:
        pc: PointCloud to visualize
        output_path: If provided, save the figure to this path
        title: Title for the figure
        grid_size: Number of views in each dimension (grid_size x grid_size views)
        figsize: Size of the figure
        fixed_bounds: If provided, use fixed bounds for all views: ((x_min, y_min, z_min), (x_max, y_max, z_max))
        show_axes: Whether to show axes labels
        point_size: Size of points in the plot
        
    Returns:
        matplotlib Figure object
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Get coordinates and colors
    coords = pc.coords
    
    # Check if RGB channels exist
    has_color = all(c in pc.channels for c in ['R', 'G', 'B'])
    if has_color:
        colors = np.stack([pc.channels['R'], pc.channels['G'], pc.channels['B']], axis=1)
        # Ensure colors are in [0, 1] range
        colors = np.clip(colors, 0, 1)
    else:
        # Use a default color if no RGB channels
        colors = np.ones((len(coords), 3)) * 0.5
    
    # Determine bounds
    if fixed_bounds is None:
        # Auto-compute bounds with some padding
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        center = (mins + maxs) / 2
        span = (maxs - mins).max() * 0.6  # Add 20% padding
        fixed_bounds = (
            tuple(center - span),
            tuple(center + span)
        )
    
    # Create multiple views with different rotations
    for i in range(grid_size):
        for j in range(grid_size):
            ax = fig.add_subplot(grid_size, grid_size, 1 + j + i * grid_size, projection='3d')
            
            # Rotate the view
            angle = (i * grid_size + j) * (360.0 / (grid_size * grid_size))
            ax.view_init(elev=20, azim=angle)
            
            # Plot points
            ax.scatter(
                coords[:, 0],
                coords[:, 1], 
                coords[:, 2],
                c=colors,
                s=point_size,
                alpha=0.8
            )
            
            # Set bounds
            ax.set_xlim(fixed_bounds[0][0], fixed_bounds[1][0])
            ax.set_ylim(fixed_bounds[0][1], fixed_bounds[1][1])
            ax.set_zlim(fixed_bounds[0][2], fixed_bounds[1][2])
            
            if show_axes:
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
            else:
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_zticks([])
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to {output_path}")
    
    return fig


def visualize_point_cloud_simple(
    pc: PointCloud,
    output_path: Optional[str] = None,
    title: str = "Point Cloud",
    figsize: Tuple[int, int] = (10, 10),
    elev: float = 20,
    azim: float = 45,
    point_size: int = 1,
) -> plt.Figure:
    """
    Simple single-view visualization of a point cloud.
    
    Args:
        pc: PointCloud to visualize
        output_path: If provided, save the figure to this path
        title: Title for the figure
        figsize: Size of the figure
        elev: Elevation angle for viewing
        azim: Azimuth angle for viewing
        point_size: Size of points in the plot
        
    Returns:
        matplotlib Figure object
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Get coordinates and colors
    coords = pc.coords
    
    # Check if RGB channels exist
    has_color = all(c in pc.channels for c in ['R', 'G', 'B'])
    if has_color:
        colors = np.stack([pc.channels['R'], pc.channels['G'], pc.channels['B']], axis=1)
        colors = np.clip(colors, 0, 1)
    else:
        colors = np.ones((len(coords), 3)) * 0.5
    
    # Plot points
    ax.scatter(
        coords[:, 0],
        coords[:, 1],
        coords[:, 2],
        c=colors,
        s=point_size,
        alpha=0.8
    )
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    ax.view_init(elev=elev, azim=azim)
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to {output_path}")
    
    return fig


def print_point_cloud_stats(pc: PointCloud) -> None:
    """
    Print statistics about a point cloud.
    
    Args:
        pc: PointCloud to analyze
    """
    print(f"Point Cloud Statistics:")
    print(f"  Number of points: {len(pc.coords)}")
    print(f"  Channels: {list(pc.channels.keys())}")
    print(f"  Coordinate bounds:")
    print(f"    X: [{pc.coords[:, 0].min():.3f}, {pc.coords[:, 0].max():.3f}]")
    print(f"    Y: [{pc.coords[:, 1].min():.3f}, {pc.coords[:, 1].max():.3f}]")
    print(f"    Z: [{pc.coords[:, 2].min():.3f}, {pc.coords[:, 2].max():.3f}]")
    
    if all(c in pc.channels for c in ['R', 'G', 'B']):
        print(f"  Color ranges:")
        print(f"    R: [{pc.channels['R'].min():.3f}, {pc.channels['R'].max():.3f}]")
        print(f"    G: [{pc.channels['G'].min():.3f}, {pc.channels['G'].max():.3f}]")
        print(f"    B: [{pc.channels['B'].min():.3f}, {pc.channels['B'].max():.3f}]")
