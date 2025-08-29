import hashlib
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any
from geopy.distance import geodesic

@dataclass(frozen=True)
class LatLon:
    """A data class to represent a point with latitude and longitude."""
    lat: float
    lon: float

@dataclass(frozen=True)
class Surface:
    """A data class to represent a rectangular area."""
    bottom_left: LatLon
    top_right: LatLon

@dataclass
class GridCell:
    """A data class to represent a single grid cell with its hash ID."""
    surface: Surface
    hash_id: str

class GridSystem:
    """
    A class to calculate grid properties on demand without pre-computing all grids.
    """
    def __init__(self, surface: Surface, lat_step: float, lon_step: float):
        """
        Initializes the GridSystem with the surface and grid dimensions.
        :param surface: The Surface object that defines the area.
        :param lat_step: The fixed height of each grid cell in degrees.
        :param lon_step: The fixed width of each grid cell in degrees.
        """
        self.surface = surface
        self.lat_step = lat_step
        self.lon_step = lon_step
        self._round_precision = 6  # Precision for hashing

    def get_grid_cell_by_latlon(self, lat: float, lon: float) -> GridCell | None:
        """
        Calculates and returns the GridCell that contains a given lat/lon point.
        Returns None if the point is outside the defined surface.
        """
        # Check if the point is within the surface boundaries
        if not (self.surface.bottom_left.lat <= lat < self.surface.top_right.lat and
                self.surface.bottom_left.lon <= lon < self.surface.top_right.lon):
            return None

        # Calculate the bottom-left corner of the grid cell
        bottom_left_lat = self.surface.bottom_left.lat + \
            int((lat - self.surface.bottom_left.lat) / self.lat_step) * self.lat_step
        bottom_left_lon = self.surface.bottom_left.lon + \
            int((lon - self.surface.bottom_left.lon) / self.lon_step) * self.lon_step

        # Define the top-right corner of the grid cell
        top_right_lat = min(bottom_left_lat + self.lat_step, self.surface.top_right.lat)
        top_right_lon = min(bottom_left_lon + self.lon_step, self.surface.top_right.lon)

        # Create the GridCell's Surface
        cell_surface = Surface(
            bottom_left=LatLon(bottom_left_lat, bottom_left_lon),
            top_right=LatLon(top_right_lat, top_right_lon)
        )
        
        # Calculate the hash ID for the grid cell
        hash_id = self.get_hash_from_latlon(bottom_left_lat, bottom_left_lon)
        
        return GridCell(surface=cell_surface, hash_id=hash_id)

    def get_hash_from_latlon(self, lat: float, lon: float) -> str:
        """
        Generates a unique MD5 hash for a grid cell based on its bottom-left corner coordinates.
        """
        hash_input = f"{lat:.{self._round_precision}f},{lon:.{self._round_precision}f}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    def get_all_grid_cells(self) -> List[GridCell]:
        """
        A generator-like method to produce all grid cells. 
        This is provided for cases where you still need to iterate over all cells,
        but it doesn't store the results in memory.
        """
        bottom_left = self.surface.bottom_left
        top_right = self.surface.top_right

        current_lat = bottom_left.lat
        while current_lat < top_right.lat:
            current_lon = bottom_left.lon
            while current_lon < top_right.lon:
                cell_surface = Surface(
                    bottom_left=LatLon(current_lat, current_lon),
                    top_right=LatLon(min(current_lat + self.lat_step, top_right.lat),
                                    min(current_lon + self.lon_step, top_right.lon))
                )
                hash_id = self.get_hash_from_latlon(current_lat, current_lon)
                yield GridCell(cell_surface, hash_id)
                current_lon += self.lon_step
            current_lat += self.lat_step

    def get_grid_cells_for_surface(self, input_surface: Surface) -> List[List[GridCell]]:
        """
        Returns a 2D array of GridCell objects that are required to cover the input surface.
        """
        if not (self.surface.bottom_left.lat <= input_surface.bottom_left.lat and
                self.surface.bottom_left.lon <= input_surface.bottom_left.lon and
                self.surface.top_right.lat >= input_surface.top_right.lat and
                self.surface.top_right.lon >= input_surface.top_right.lon):
            print("Warning: Input surface is not fully contained within the GridSystem's surface.")
        
        covered_grids = []
        
        # Calculate the starting lat/lon based on the input surface
        start_lat = self.surface.bottom_left.lat + \
            int((input_surface.bottom_left.lat - self.surface.bottom_left.lat) / self.lat_step) * self.lat_step
        start_lon = self.surface.bottom_left.lon + \
            int((input_surface.bottom_left.lon - self.surface.bottom_left.lon) / self.lon_step) * self.lon_step
            
        current_lat = start_lat
        while current_lat < input_surface.top_right.lat:
            row = []
            current_lon = start_lon
            while current_lon < input_surface.top_right.lon:
                # Calculate the bounds of the current grid cell
                cell_bottom_left = LatLon(current_lat, current_lon)
                cell_top_right = LatLon(min(current_lat + self.lat_step, input_surface.top_right.lat),
                                        min(current_lon + self.lon_step, input_surface.top_right.lon))
                
                # Create the GridCell and add to the row
                cell_surface = Surface(cell_bottom_left, cell_top_right)
                hash_id = self.get_hash_from_latlon(current_lat, current_lon)
                row.append(GridCell(cell_surface, hash_id))

                current_lon += self.lon_step
            covered_grids.append(row)
            current_lat += self.lon_step
            
        return covered_grids

    def __repr__(self) -> str:
        """Provides a string representation of the GridSystem."""
        return f"GridSystem(surface={self.surface})"

def calculate_geodesic_distance(point1: LatLon, point2: LatLon) -> float:
    """
    Calculates the geodesic distance in meters between two LatLon points using the geopy library.
    
    :param point1: The first LatLon point.
    :param point2: The second LatLon point.
    :return: The geodesic distance in meters.
    """
    # Geopy expects coordinates in (lat, lon) tuple format
    return geodesic((point1.lat, point1.lon), (point2.lat, point2.lon)).meters

def main_method():
    print("--- Creating a Grid System for Hong Kong Territory ---")

    # Define the LatLon points for Hong Kong's approximate boundaries
    # Lat/Lon are in decimal degrees (WGS84)
    bottom_left_latlon = LatLon(22.15, 113.80)
    top_right_latlon = LatLon(22.60, 114.45)

    # Create the Surface object for Hong Kong
    hong_kong_surface = Surface(bottom_left_latlon, top_right_latlon)

    print(f"Surface defined from {hong_kong_surface.bottom_left} to {hong_kong_surface.top_right}")
    
    # Create the GridSystem with a 0.001-degree step (~100 meters)
    lat_step = 0.001
    lon_step = 0.001
    hk_grid_system = GridSystem(hong_kong_surface, lat_step, lon_step)

    print(f"Grid system created with a grid size of {lat_step} deg x {lon_step} deg")
    
    print("\n--- Getting a specific grid cell for a point in Central, Hong Kong ---")
    
    # A point near Central, Hong Kong, with 3 decimal places
    test_lat = 22.283
    test_lon = 114.160
    
    central_grid_cell = hk_grid_system.get_grid_cell_by_latlon(test_lat, test_lon)
    
    if central_grid_cell:
        print(f"The point ({test_lat}, {test_lon}) falls within:")
        print(f"  Hash ID: {central_grid_cell.hash_id}")
        print(f"  Coordinates: {central_grid_cell.surface.bottom_left} to {central_grid_cell.surface.top_right}")
    else:
        print(f"The point ({test_lat}, {test_lon}) is outside the defined surface.")
    
    print("\n--- Listing the first 5 grid cells (lazy calculation) ---")
    
    # Use a loop to iterate through the cells without storing them all
    for i, grid_cell in enumerate(hk_grid_system.get_all_grid_cells()):
        if i >= 5:
            break
        print(f"Grid Cell {i+1}:")
        print(f"  Hash ID: {grid_cell.hash_id}")
        print(f"  Coordinates: {grid_cell.surface.bottom_left} to {grid_cell.surface.top_right}")

    print("\n--- Getting a 2D array of grid cells for a specific sub-surface ---")
    
    # Define a smaller sub-surface in Central, Hong Kong
    sub_surface_bottom_left = LatLon(22.280, 114.150)
    sub_surface_top_right = LatLon(22.285, 114.160)
    
    sub_surface = Surface(sub_surface_bottom_left, sub_surface_top_right)
    
    covered_grids_2d = hk_grid_system.get_grid_cells_for_surface(sub_surface)
    
    print(f"Number of rows: {len(covered_grids_2d)}")
    print(f"Number of columns in first row: {len(covered_grids_2d[0]) if covered_grids_2d else 0}")
    
    print("\n--- Displaying the 2D grid cell hashes ---")
    for row in covered_grids_2d:
        row_hashes = [cell.hash_id[:5] + "..." for cell in row]
        print(row_hashes)

    print("\n--- Calculating distance between two points ---")
    
    # Two points in Hong Kong to calculate the distance between
    point_a = LatLon(22.283, 114.160)  # Near Central Pier
    point_b = LatLon(22.281, 114.155)  # Near IFC Mall
    
    distance_meters = calculate_geodesic_distance(point_a, point_b)
    print(f"The geodesic distance between point A ({point_a}) and point B ({point_b}) is approximately {distance_meters:.2f} meters.")
