"""
CAE format preprocessing module for converting CAE mesh data to PointCloud format.

This module parses CAE format files (typically used in structural analysis) and converts
them to the PointCloud format used by the point-e upsampling models.

CAE Format:
- GRID: Point coordinates (GRID,ID,,X,Y,Z)
- CTRIA3/CQUAD4: Elements/units that reference GRIDs (element_type,element_id,pid,grid1,grid2,...)
- PSHELL: Properties with unique PIDs that determine colors

Each point's color is determined by:
1. Finding which elements contain the point (via GRID ID)
2. Getting the PID from those elements
3. Assigning a unique color per PID
"""

from typing import Dict, List, Set, Tuple
import numpy as np
from .point_cloud import PointCloud


class CAEPreprocessor:
    """Preprocessor for CAE format files."""
    
    def __init__(self):
        self.grids: Dict[int, np.ndarray] = {}  # grid_id -> [x, y, z]
        self.elements: Dict[int, Tuple[int, List[int]]] = {}  # element_id -> (pid, [grid_ids])
        self.pshells: Set[int] = set()  # Set of PIDs
        self.grid_to_pids: Dict[int, Set[int]] = {}  # grid_id -> set of PIDs
        
    def parse_line(self, line: str) -> None:
        """Parse a single line from CAE format file."""
        line = line.strip()
        if not line:
            return
            
        parts = [p.strip() for p in line.split(',')]
        
        if parts[0] == 'GRID':
            # Format: GRID,ID,,X,Y,Z
            if len(parts) >= 6:
                grid_id = int(parts[1])
                x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
                self.grids[grid_id] = np.array([x, y, z])
                
        elif parts[0] == 'CTRIA3':
            # Format: CTRIA3,element_id,pid,grid1,grid2,grid3
            if len(parts) >= 6:
                element_id = int(parts[1])
                pid = int(parts[2])
                grid_ids = [int(parts[3]), int(parts[4]), int(parts[5])]
                self.elements[element_id] = (pid, grid_ids)
                
        elif parts[0] == 'CQUAD4':
            # Format: CQUAD4,element_id,pid,grid1,grid2,grid3,grid4
            if len(parts) >= 7:
                element_id = int(parts[1])
                pid = int(parts[2])
                grid_ids = [int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6])]
                self.elements[element_id] = (pid, grid_ids)
                
        elif parts[0] == 'PSHELL':
            # Format: PSHELL,pid,...
            if len(parts) >= 2:
                pid = int(parts[1])
                self.pshells.add(pid)
                
    def parse_file(self, filepath: str) -> None:
        """Parse a CAE format file."""
        with open(filepath, 'r') as f:
            for line in f:
                self.parse_line(line)
                
    def _build_grid_to_pid_mapping(self) -> None:
        """Build mapping from grid IDs to PIDs via elements."""
        self.grid_to_pids.clear()
        
        for element_id, (pid, grid_ids) in self.elements.items():
            for grid_id in grid_ids:
                if grid_id not in self.grid_to_pids:
                    self.grid_to_pids[grid_id] = set()
                self.grid_to_pids[grid_id].add(pid)
                
    def _assign_colors_to_pids(self) -> Dict[int, np.ndarray]:
        """Assign unique colors to each PID using a color palette."""
        pid_list = sorted(list(self.pshells))
        n_pids = len(pid_list)
        
        # Generate distinct colors using HSV color space
        colors = {}
        for i, pid in enumerate(pid_list):
            # Distribute hues evenly across the color spectrum
            hue = i / max(n_pids, 1)
            # Convert HSV to RGB (simplified)
            # Using full saturation and value for vivid colors
            rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
            colors[pid] = rgb
            
        return colors
        
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> np.ndarray:
        """Convert HSV color to RGB. Values are in [0, 1] range."""
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return np.array([r + m, g + m, b + m])
        
    def to_point_cloud(self) -> PointCloud:
        """
        Convert parsed CAE data to PointCloud format.
        
        Returns:
            PointCloud with coordinates and RGB color channels.
        """
        # Build the grid-to-PID mapping
        self._build_grid_to_pid_mapping()
        
        # Assign colors to PIDs
        pid_colors = self._assign_colors_to_pids()
        
        # Build arrays for PointCloud
        grid_ids = sorted(self.grids.keys())
        n_points = len(grid_ids)
        
        coords = np.zeros((n_points, 3))
        colors_r = np.zeros(n_points)
        colors_g = np.zeros(n_points)
        colors_b = np.zeros(n_points)
        
        for i, grid_id in enumerate(grid_ids):
            coords[i] = self.grids[grid_id]
            
            # Get the PID(s) for this grid
            # If a grid belongs to multiple elements with different PIDs,
            # we'll average their colors
            if grid_id in self.grid_to_pids and self.grid_to_pids[grid_id]:
                pids = sorted(list(self.grid_to_pids[grid_id]))  # Sort for consistency
                valid_colors = [pid_colors[pid] for pid in pids if pid in pid_colors]
                
                if valid_colors:
                    # Average colors if multiple PIDs
                    avg_color = np.mean(valid_colors, axis=0)
                    colors_r[i] = avg_color[0]
                    colors_g[i] = avg_color[1]
                    colors_b[i] = avg_color[2]
                else:
                    # Default color if PID not found in PSHELL
                    colors_r[i] = 0.5
                    colors_g[i] = 0.5
                    colors_b[i] = 0.5
            else:
                # Default gray color for points not in any element
                colors_r[i] = 0.5
                colors_g[i] = 0.5
                colors_b[i] = 0.5
                
        # Create PointCloud with RGB channels in [0, 1] range
        return PointCloud(
            coords=coords,
            channels={
                'R': colors_r,
                'G': colors_g,
                'B': colors_b,
            }
        )
        
    @staticmethod
    def preprocess_cae_file(filepath: str) -> PointCloud:
        """
        Convenience method to parse a CAE file and convert to PointCloud.
        
        Args:
            filepath: Path to the CAE format file.
            
        Returns:
            PointCloud with coordinates and RGB color channels.
        """
        preprocessor = CAEPreprocessor()
        preprocessor.parse_file(filepath)
        return preprocessor.to_point_cloud()
