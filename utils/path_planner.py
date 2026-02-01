"""
Path planning using NetworkX
"""
import networkx as nx
import numpy as np
from typing import List, Tuple


class PathPlanner:
    """A* path planning for 3D drone navigation"""
    
    def __init__(self, grid_size=200, resolution=5):
        """
        Initialize path planner
        grid_size: size of the 3D grid in meters
        resolution: grid resolution in meters (smaller = more precise but slower)
        """
        self.grid_size = grid_size
        self.resolution = resolution
        self.obstacles = set()  # Set of obstacle positions (x, y, z)
        self.no_fly_zones = []  # List of (min_x, max_x, min_y, max_y, min_z, max_z)
    
    def add_obstacle(self, x: float, y: float, z: float, radius: float = 5):
        """Add a spherical obstacle"""
        # Discretize obstacle into grid cells
        x_grid = int(x / self.resolution)
        y_grid = int(y / self.resolution)
        z_grid = int(z / self.resolution)
        radius_grid = int(radius / self.resolution)
        
        for dx in range(-radius_grid, radius_grid + 1):
            for dy in range(-radius_grid, radius_grid + 1):
                for dz in range(-radius_grid, radius_grid + 1):
                    if dx*dx + dy*dy + dz*dz <= radius_grid*radius_grid:
                        self.obstacles.add((x_grid + dx, y_grid + dy, z_grid + dz))
    
    def add_no_fly_zone(self, min_x, max_x, min_y, max_y, min_z, max_z):
        """Add a rectangular no-fly zone"""
        self.no_fly_zones.append((min_x, max_x, min_y, max_y, min_z, max_z))
    
    def is_obstacle(self, x: float, y: float, z: float) -> bool:
        """Check if position is an obstacle"""
        x_grid = int(x / self.resolution)
        y_grid = int(y / self.resolution)
        z_grid = int(z / self.resolution)
        
        # Check grid obstacles
        if (x_grid, y_grid, z_grid) in self.obstacles:
            return True
        
        # Check no-fly zones
        for min_x, max_x, min_y, max_y, min_z, max_z in self.no_fly_zones:
            if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
                return True
        
        return False
    
    def plan_path(self, start: Tuple[float, float, float], 
                  goal: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """
        Plan optimal path from start to goal using A*
        Returns list of waypoints
        """
        # Create graph
        G = nx.Graph()
        
        # Discretize start and goal
        start_grid = tuple(int(x / self.resolution) for x in start)
        goal_grid = tuple(int(x / self.resolution) for x in goal)
        
        # Add nodes and edges (26-connected grid)
        visited = set()
        queue = [start_grid]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Add node
            if current not in self.obstacles:
                G.add_node(current)
            else:
                continue
            
            # Stop if we reached goal
            if current == goal_grid:
                break
            
            # Check neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == 0 and dy == 0 and dz == 0:
                            continue
                        
                        neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
                        
                        # Skip if out of bounds
                        if any(abs(n * self.resolution) > self.grid_size for n in neighbor):
                            continue
                        
                        # Skip if obstacle
                        if neighbor in self.obstacles:
                            continue
                        
                        if neighbor not in visited:
                            queue.append(neighbor)
                            
                            # Add edge with Euclidean distance as weight
                            dist = np.sqrt(dx*dx + dy*dy + dz*dz) * self.resolution
                            G.add_edge(current, neighbor, weight=dist)
        
        # Find path using A*
        try:
            path_grid = nx.astar_path(
                G, start_grid, goal_grid,
                heuristic=lambda a, b: np.sqrt(sum((x-y)**2 for x, y in zip(a, b))) * self.resolution
            )
            
            # Convert back to real coordinates
            path = [(x * self.resolution, y * self.resolution, z * self.resolution) 
                   for x, y, z in path_grid]
            
            # Simplify path (remove intermediate points on straight lines)
            simplified_path = self._simplify_path(path)
            
            return simplified_path
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # No path found, return direct path
            return [start, goal]
    
    def _simplify_path(self, path: List[Tuple[float, float, float]], 
                       tolerance: float = 0.1) -> List[Tuple[float, float, float]]:
        """Simplify path by removing collinear points"""
        if len(path) <= 2:
            return path
        
        simplified = [path[0]]
        
        for i in range(1, len(path) - 1):
            # Check if point is collinear with previous and next
            prev = np.array(simplified[-1])
            curr = np.array(path[i])
            next_pt = np.array(path[i + 1])
            
            # Calculate cross product
            v1 = curr - prev
            v2 = next_pt - curr
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cross = np.cross(v1, v2)
                if np.linalg.norm(cross) > tolerance:
                    simplified.append(path[i])
        
        simplified.append(path[-1])
        return simplified


# Global path planner instance
_path_planner = None

def get_path_planner():
    """Get or create the global path planner instance"""
    global _path_planner
    if _path_planner is None:
        _path_planner = PathPlanner()
    return _path_planner
