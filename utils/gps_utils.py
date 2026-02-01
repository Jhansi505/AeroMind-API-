"""
GPS and Geospatial utilities using geopy
"""
from geopy.distance import geodesic
from geopy.point import Point
import math

# Base coordinates (you can change this to your actual base location)
BASE_GPS = (37.7749, -122.4194)  # San Francisco (example)
METERS_PER_DEGREE_LAT = 111320  # Approximate


class GPSConverter:
    """Convert between GPS coordinates and XYZ meters"""
    
    def __init__(self, base_lat=37.7749, base_lon=-122.4194):
        self.base_lat = base_lat
        self.base_lon = base_lon
        self.base_point = Point(base_lat, base_lon)
    
    def gps_to_xyz(self, lat: float, lon: float, altitude: float = 0) -> tuple:
        """Convert GPS coordinates to XYZ meters from base"""
        target_point = Point(lat, lon)
        
        # Calculate X (North-South distance in meters)
        x = (lat - self.base_lat) * METERS_PER_DEGREE_LAT
        
        # Calculate Y (East-West distance in meters)
        # Longitude degrees vary with latitude
        meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(lat))
        y = (lon - self.base_lon) * meters_per_degree_lon
        
        z = altitude
        
        return (x, y, z)
    
    def xyz_to_gps(self, x: float, y: float, z: float) -> tuple:
        """Convert XYZ meters to GPS coordinates"""
        # Convert X to latitude
        lat = self.base_lat + (x / METERS_PER_DEGREE_LAT)
        
        # Convert Y to longitude
        meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(lat))
        lon = self.base_lon + (y / meters_per_degree_lon)
        
        altitude = z
        
        return (lat, lon, altitude)
    
    def distance_between_points(self, point1: tuple, point2: tuple) -> float:
        """Calculate distance in meters between two GPS points"""
        return geodesic(point1[:2], point2[:2]).meters
    
    def get_waypoint(self, start_lat: float, start_lon: float, 
                     bearing: float, distance_m: float) -> tuple:
        """
        Calculate waypoint given start point, bearing (degrees), and distance (meters)
        """
        start = Point(start_lat, start_lon)
        destination = geodesic(meters=distance_m).destination(start, bearing)
        return (destination.latitude, destination.longitude)


# Global GPS converter instance
_gps_converter = None

def get_gps_converter():
    """Get or create the global GPS converter instance"""
    global _gps_converter
    if _gps_converter is None:
        _gps_converter = GPSConverter()
    return _gps_converter


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two GPS coordinates"""
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def format_gps_coordinates(lat: float, lon: float, alt: float = 0) -> str:
    """Format GPS coordinates for display"""
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return f"{abs(lat):.6f}°{lat_dir}, {abs(lon):.6f}°{lon_dir}, {alt:.1f}m"
