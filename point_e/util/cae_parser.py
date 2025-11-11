"""
CAE file parser for converting Nastran format files to Point-E compatible point clouds.

This module parses CAE files in Nastran format containing:
- GRID entries: point coordinates (id, x, y, z)
- CQUAD4/CTRIA3 entries: element definitions mapping points to elements
- PSHELL entries: property definitions for color assignment
"""

import re
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from .point_cloud import PointCloud


def parse_fixed_width_line(line: str, field_width: int = 8) -> List[str]:
    """
    Parse a fixed-width format line into fields.
    
    :param line: The line to parse
    :param field_width: Width of each field (default 8 for Nastran format)
    :return: List of field strings
    """
    # Split line into fields of field_width characters
    fields = []
    for i in range(0, len(line), field_width):
        field = line[i:i + field_width].strip()
        if field:
            fields.append(field)
    return fields


def parse_scientific_notation(value: str) -> float:
    """
    Parse scientific notation that may be missing 'E' (e.g., 2661.937-433.604 or 1.23+45)
    
    :param value: String value to parse
    :return: Float value
    """
    # Handle cases like "2661.937-433.604" where the minus is actually a separator
    # or "1.23+45" where + indicates exponent
    value = value.strip()
    
    # Check if this looks like scientific notation without 'E'
    # Pattern: digits, optional decimal, then +/- followed by more digits
    match = re.match(r'^([-+]?\d+\.?\d*)([+-]\d+\.?\d*)$', value)
    if match:
        # This could be "mantissa+exponent" format
        mantissa = match.group(1)
        rest = match.group(2)
        
        # Check if the rest part looks like an exponent (typically shorter)
        if len(rest) <= 4:  # Exponents are usually small
            try:
                # Try to parse as scientific notation
                return float(mantissa + 'E' + rest)
            except ValueError:
                pass
    
    # Try standard float parsing
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Cannot parse value: {value}")


def parse_coordinate(coord_str: str) -> Tuple[float, float, float]:
    """
    Parse coordinate string that may have concatenated values without spaces.
    For example: "2661.937-433.604113.7815" should become (2661.937, -433.604, 113.7815)
    
    :param coord_str: Coordinate string
    :return: Tuple of (x, y, z) coordinates
    """
    # Try to split by looking for patterns like number+/-number
    # This handles the case where coordinates are concatenated
    
    # Remove extra spaces
    coord_str = coord_str.strip()
    
    # Try splitting by spaces first (normal case)
    parts = coord_str.split()
    if len(parts) == 3:
        return tuple(float(p) for p in parts)
    
    # If we have a single string, try to parse it as concatenated values
    # Look for patterns like: digits.digits+/-digits.digits+/-digits.digits
    # We'll use a regex to find all float-like patterns
    pattern = r'[-+]?\d+\.?\d*'
    matches = re.findall(pattern, coord_str)
    
    if len(matches) >= 3:
        # Take the first three matches as x, y, z
        return (float(matches[0]), float(matches[1]), float(matches[2]))
    
    raise ValueError(f"Cannot parse coordinates from: {coord_str}")


class CAEParser:
    """
    Parser for CAE (Nastran format) files to extract point clouds with colors.
    """
    
    def __init__(self):
        self.grids: Dict[int, np.ndarray] = {}  # point_id -> [x, y, z]
        self.elements: Dict[int, Tuple[int, List[int]]] = {}  # element_id -> (property_id, [point_ids])
        self.properties: Dict[int, Dict] = {}  # property_id -> property_data
        self.point_to_elements: Dict[int, List[int]] = {}  # point_id -> [element_ids]
    
    def parse_file(self, filepath: str):
        """
        Parse a CAE file and extract all relevant data.
        
        :param filepath: Path to the CAE file
        """
        with open(filepath, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line.strip():
                    continue
                
                # Parse based on the keyword
                if line.startswith('GRID'):
                    self._parse_grid(line)
                elif line.startswith('CQUAD4'):
                    self._parse_cquad4(line)
                elif line.startswith('CTRIA3'):
                    self._parse_ctria3(line)
                elif line.startswith('PSHELL'):
                    self._parse_pshell(line)
    
    def _parse_grid(self, line: str):
        """Parse a GRID line to extract point ID and coordinates."""
        # GRID format: GRID, ID, CP, X1, X2, X3, CD, PS, SEID
        # Example: GRID        4649        2661.937-433.604113.7815
        # Can also be space-separated: GRID    4649    0    1.0 2.0 3.0
        
        # Try simple whitespace split first (handles most cases)
        parts = line.split()
        if len(parts) >= 5:
            try:
                point_id = int(parts[1])
                # Skip coordinate system field (parts[2] if present)
                # Try to find 3 consecutive float values
                coords = []
                for i in range(2, len(parts)):
                    try:
                        val = float(parts[i])
                        coords.append(val)
                        if len(coords) == 3:
                            break
                    except ValueError:
                        continue
                
                if len(coords) == 3:
                    self.grids[point_id] = np.array(coords, dtype=np.float32)
                    return
            except (ValueError, IndexError):
                pass
        
        # Fallback to fixed-width parsing for concatenated coordinates
        fields = parse_fixed_width_line(line)
        
        if len(fields) < 2:
            return
        
        try:
            point_id = int(fields[1])
            
            # Coordinates can be in fields[2], [3], [4] or concatenated in one field
            if len(fields) >= 5:
                # Normal case: separate fields
                x, y, z = float(fields[2]), float(fields[3]), float(fields[4])
            elif len(fields) >= 3:
                # Concatenated case: parse the coordinate string
                coord_str = ''.join(fields[2:])
                x, y, z = parse_coordinate(coord_str)
            else:
                return
            
            self.grids[point_id] = np.array([x, y, z], dtype=np.float32)
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse GRID line: {line[:50]}... Error: {e}")
    
    def _parse_cquad4(self, line: str):
        """Parse a CQUAD4 (quadrilateral element) line."""
        # CQUAD4 format: CQUAD4, EID, PID, G1, G2, G3, G4
        # Example: CQUAD4   1111017  885657    4651    4650    4653    4649
        fields = parse_fixed_width_line(line)
        
        if len(fields) < 7:
            return
        
        try:
            element_id = int(fields[1])
            property_id = int(fields[2])
            point_ids = [int(fields[i]) for i in range(3, 7)]
            
            self.elements[element_id] = (property_id, point_ids)
            
            # Build reverse mapping: point_id -> element_ids
            for pid in point_ids:
                if pid not in self.point_to_elements:
                    self.point_to_elements[pid] = []
                self.point_to_elements[pid].append(element_id)
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse CQUAD4 line: {line[:50]}... Error: {e}")
    
    def _parse_ctria3(self, line: str):
        """Parse a CTRIA3 (triangular element) line."""
        # CTRIA3 format: CTRIA3, EID, PID, G1, G2, G3
        # Example: CTRIA3   1111015  885657    4653    4650    4652
        fields = parse_fixed_width_line(line)
        
        if len(fields) < 6:
            return
        
        try:
            element_id = int(fields[1])
            property_id = int(fields[2])
            point_ids = [int(fields[i]) for i in range(3, 6)]
            
            self.elements[element_id] = (property_id, point_ids)
            
            # Build reverse mapping: point_id -> element_ids
            for pid in point_ids:
                if pid not in self.point_to_elements:
                    self.point_to_elements[pid] = []
                self.point_to_elements[pid].append(element_id)
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse CTRIA3 line: {line[:50]}... Error: {e}")
    
    def _parse_pshell(self, line: str):
        """Parse a PSHELL (shell property) line."""
        # PSHELL format: PSHELL, PID, MID1, T, MID2, 12I/T^3, MID3, TS/T, NSM, Z1, Z2
        # Example: PSHELL    885657       1      2.       1               1              0.
        fields = parse_fixed_width_line(line)
        
        if len(fields) < 2:
            return
        
        try:
            property_id = int(fields[1])
            # Store basic property data (can be extended as needed)
            self.properties[property_id] = {
                'id': property_id,
                'material_id': int(fields[2]) if len(fields) > 2 and fields[2] else None,
                'thickness': float(fields[3]) if len(fields) > 3 and fields[3] else None,
            }
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse PSHELL line: {line[:50]}... Error: {e}")
    
    def get_point_color_from_property(self, point_id: int) -> Optional[int]:
        """
        Get the property ID associated with a point (via its elements).
        
        :param point_id: The point ID
        :return: Property ID or None if not found
        """
        if point_id not in self.point_to_elements:
            return None
        
        # Get the first element containing this point
        element_ids = self.point_to_elements[point_id]
        if not element_ids:
            return None
        
        element_id = element_ids[0]
        if element_id not in self.elements:
            return None
        
        property_id, _ = self.elements[element_id]
        return property_id
    
    def to_point_cloud(
        self,
        max_points: int = 4096,
        normalize: bool = True,
        color_map: Optional[Dict[int, Tuple[float, float, float]]] = None,
        default_color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    ) -> PointCloud:
        """
        Convert parsed CAE data to a Point-E compatible point cloud.
        
        :param max_points: Maximum number of points (will downsample if needed)
        :param normalize: Whether to normalize coordinates to roughly [-1, 1] range
        :param color_map: Optional mapping from property_id to RGB color (each in [0, 1])
        :param default_color: Default RGB color for points without property mapping
        :return: PointCloud object ready for Point-E
        """
        if not self.grids:
            raise ValueError("No GRID data found in CAE file")
        
        # Convert grids to numpy arrays
        point_ids = list(self.grids.keys())
        coords = np.array([self.grids[pid] for pid in point_ids], dtype=np.float32)
        
        # Normalize coordinates if requested
        if normalize:
            # Center the point cloud
            center = np.mean(coords, axis=0)
            coords = coords - center
            
            # Scale to fit roughly in [-1, 1] range
            max_extent = np.max(np.abs(coords))
            if max_extent > 0:
                coords = coords / max_extent
        
        # Assign colors based on property IDs
        colors = np.zeros((len(point_ids), 3), dtype=np.float32)
        
        # Generate a color map if not provided
        if color_map is None:
            # Get unique property IDs
            unique_props = set()
            for pid in point_ids:
                prop_id = self.get_point_color_from_property(pid)
                if prop_id is not None:
                    unique_props.add(prop_id)
            
            # Generate distinct colors for each property
            color_map = self._generate_color_map(list(unique_props))
        
        # Assign colors to points
        for i, pid in enumerate(point_ids):
            prop_id = self.get_point_color_from_property(pid)
            if prop_id is not None and prop_id in color_map:
                colors[i] = color_map[prop_id]
            else:
                colors[i] = default_color
        
        # Create initial point cloud
        pc = PointCloud(
            coords=coords,
            channels={
                'R': colors[:, 0],
                'G': colors[:, 1],
                'B': colors[:, 2],
            }
        )
        
        # Downsample if needed
        if len(coords) > max_points:
            print(f"Downsampling from {len(coords)} to {max_points} points using farthest point sampling...")
            pc = pc.farthest_point_sample(max_points)
        
        return pc
    
    def _generate_color_map(self, property_ids: List[int]) -> Dict[int, Tuple[float, float, float]]:
        """
        Generate a color map for property IDs using distinct colors.
        
        :param property_ids: List of property IDs
        :return: Dictionary mapping property_id to RGB tuple
        """
        color_map = {}
        
        # Use HSV color space to generate distinct colors
        import colorsys
        
        n = len(property_ids)
        for i, prop_id in enumerate(sorted(property_ids)):
            # Vary hue to get distinct colors
            hue = i / max(n, 1)
            saturation = 0.7
            value = 0.9
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            color_map[prop_id] = (r, g, b)
        
        return color_map


def load_cae_file(
    filepath: str,
    max_points: int = 4096,
    normalize: bool = True,
    color_map: Optional[Dict[int, Tuple[float, float, float]]] = None
) -> PointCloud:
    """
    Convenience function to load a CAE file and convert it to a point cloud.
    
    :param filepath: Path to the CAE file
    :param max_points: Maximum number of points (will downsample if needed)
    :param normalize: Whether to normalize coordinates
    :param color_map: Optional mapping from property_id to RGB color
    :return: PointCloud object ready for Point-E
    """
    parser = CAEParser()
    parser.parse_file(filepath)
    return parser.to_point_cloud(max_points=max_points, normalize=normalize, color_map=color_map)
