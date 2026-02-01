from utils.drone_visualizer import get_visualizer
from utils.gps_utils import get_gps_converter, format_gps_coordinates
from utils.path_planner import get_path_planner
from utils.physics import get_physics

def takeoff(height: float) -> str:
    visualizer = get_visualizer()
    physics = get_physics()
    
    # Check battery
    if physics.battery_percentage < 5:
        return "[DRONE] ERROR: Battery too low to takeoff!"
    
    current_pos = visualizer.get_current_position()
    new_pos = [current_pos[0], current_pos[1], height]
    visualizer.add_position(*new_pos)
    
    # Simulate physics
    time_taken, energy = physics.takeoff(height)
    
    return f"[DRONE] Takeoff to {height}m - Time: {time_taken:.1f}s, Energy: {energy:.2f}Wh, Battery: {physics.battery_percentage:.1f}%"

def move_to_location(x: float, y: float, z: float) -> str:
    visualizer = get_visualizer()
    physics = get_physics()
    
    if not physics.is_flying:
        return "[DRONE] ERROR: Drone not in flight! Takeoff first."
    
    if physics.battery_percentage < 5:
        return f"[DRONE] ERROR: Battery critical ({physics.battery_percentage:.1f}%)"
    
    current = visualizer.get_current_position()
    dx = x - current[0]
    dy = y - current[1]
    dz = z - current[2]
    
    visualizer.add_position(x, y, z)
    
    # Simulate physics
    time_taken, energy = physics.move(dx, dy, dz)
    distance = (dx**2 + dy**2 + dz**2)**0.5
    
    return f"[DRONE] Moved to ({x:.1f}, {y:.1f}, {z:.1f}) - Distance: {distance:.1f}m, Time: {time_taken:.1f}s, Energy: {energy:.2f}Wh, Battery: {physics.battery_percentage:.1f}%"

def move_forward(distance: float) -> str:
    """Move forward (positive X direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0] + distance, current[1], current[2]]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving forward {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def move_backward(distance: float) -> str:
    """Move backward (negative X direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0] - distance, current[1], current[2]]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving backward {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def move_right(distance: float) -> str:
    """Move right (positive Y direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0], current[1] + distance, current[2]]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving right {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def move_left(distance: float) -> str:
    """Move left (negative Y direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0], current[1] - distance, current[2]]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving left {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def move_up(distance: float) -> str:
    """Move up (positive Z direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0], current[1], current[2] + distance]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving up {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def move_down(distance: float) -> str:
    """Move down (negative Z direction)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    new_pos = [current[0], current[1], max(0, current[2] - distance)]
    visualizer.add_position(*new_pos)
    return f"[DRONE] Moving down {distance} meters to ({new_pos[0]}, {new_pos[1]}, {new_pos[2]})."

def return_to_home() -> str:
    """Return to initial starting point (0, 0, 0)"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    # First move to home position at current height
    visualizer.add_position(0, 0, current[2])
    # Then descend to ground
    visualizer.add_position(0, 0, 0)
    return "[DRONE] Returning to home position (0, 0, 0)."

def get_current_location() -> str:
    """Get current drone position"""
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    return f"[DRONE] Current position: X={current[0]}, Y={current[1]}, Z={current[2]}"

def land() -> str:
    visualizer = get_visualizer()
    physics = get_physics()
    
    current_pos = visualizer.get_current_position()
    visualizer.add_position(current_pos[0], current_pos[1], 0)
    
    # Simulate physics
    time_taken, energy = physics.land()
    
    return f"[DRONE] Landing - Time: {time_taken:.1f}s, Energy: {energy:.2f}Wh, Total flight time: {physics.total_flight_time:.1f}s"


# GPS-based navigation functions
def move_to_gps(lat: float, lon: float, altitude: float) -> str:
    """Move to GPS coordinates"""
    visualizer = get_visualizer()
    gps_converter = get_gps_converter()
    
    # Convert GPS to XYZ
    x, y, z = gps_converter.gps_to_xyz(lat, lon, altitude)
    visualizer.add_position(x, y, z)
    
    gps_str = format_gps_coordinates(lat, lon, altitude)
    return f"[DRONE] Moving to GPS {gps_str} -> XYZ({x:.1f}, {y:.1f}, {z:.1f})"


def get_current_gps() -> str:
    """Get current GPS coordinates"""
    visualizer = get_visualizer()
    gps_converter = get_gps_converter()
    current = visualizer.get_current_position()
    
    lat, lon, alt = gps_converter.xyz_to_gps(current[0], current[1], current[2])
    gps_str = format_gps_coordinates(lat, lon, alt)
    
    return f"[DRONE] Current GPS: {gps_str}"


def plan_path_to(x: float, y: float, z: float) -> str:
    """Plan optimal path to destination avoiding obstacles"""
    visualizer = get_visualizer()
    path_planner = get_path_planner()
    
    current = visualizer.get_current_position()
    start = tuple(current)
    goal = (x, y, z)
    
    # Plan path
    waypoints = path_planner.plan_path(start, goal)
    
    # Add all waypoints to visualization
    for waypoint in waypoints[1:]:  # Skip first waypoint (current position)
        visualizer.add_position(*waypoint)
    
    return f"[DRONE] Planned path with {len(waypoints)} waypoints to ({x}, {y}, {z})"


def add_obstacle(x: float, y: float, z: float, radius: float = 10.0) -> str:
    """Add obstacle for path planning"""
    path_planner = get_path_planner()
    path_planner.add_obstacle(x, y, z, radius)
    
    return f"[DRONE] Obstacle added at ({x}, {y}, {z}) with radius {radius}m"


def add_no_fly_zone(min_x: float, max_x: float, min_y: float, 
                    max_y: float, min_z: float, max_z: float) -> str:
    """Add no-fly zone"""
    path_planner = get_path_planner()
    path_planner.add_no_fly_zone(min_x, max_x, min_y, max_y, min_z, max_z)
    
    return f"[DRONE] No-fly zone added: X[{min_x},{max_x}], Y[{min_y},{max_y}], Z[{min_z},{max_z}]"


# Physics-based telemetry functions
def get_battery_status() -> str:
    """Get battery status"""
    physics = get_physics()
    telemetry = physics.get_telemetry()
    
    return f"""[TELEMETRY] Battery Status:
  - Charge: {telemetry['battery_percentage']:.1f}% ({telemetry['battery_remaining_mah']:.0f} mAh)
  - Flight time remaining: {telemetry['flight_time_remaining']:.1f} minutes
  - Energy consumed: {telemetry['energy_consumed']:.2f} Wh"""


def get_flight_statistics() -> str:
    """Get flight statistics"""
    physics = get_physics()
    telemetry = physics.get_telemetry()
    
    return f"""[TELEMETRY] Flight Statistics:
  - Current altitude: {telemetry['position'][2]:.1f} m
  - Current speed: {telemetry['current_speed']:.2f} m/s
  - Max speed reached: {telemetry['max_speed_reached']:.2f} m/s
  - Max altitude: {telemetry['max_altitude']:.1f} m
  - Total distance: {telemetry['total_distance']:.1f} m
  - Total flight time: {telemetry['total_flight_time']:.1f} s"""


def get_full_telemetry() -> str:
    """Get complete telemetry"""
    physics = get_physics()
    telemetry = physics.get_telemetry()
    
    status = "FLYING" if telemetry['is_flying'] else "LANDED"
    
    return f"""[TELEMETRY] Complete Drone Status:
  - Status: {status}
  - Position: X={telemetry['position'][0]:.1f}m, Y={telemetry['position'][1]:.1f}m, Z={telemetry['position'][2]:.1f}m
  - Velocity: X={telemetry['velocity'][0]:.2f}m/s, Y={telemetry['velocity'][1]:.2f}m/s, Z={telemetry['velocity'][2]:.2f}m/s
  - Current speed: {telemetry['current_speed']:.2f} m/s
  - Battery: {telemetry['battery_percentage']:.1f}% ({telemetry['battery_remaining_mah']:.0f} mAh)
  - Flight time remaining: {telemetry['flight_time_remaining']:.1f} minutes
  - Energy consumed: {telemetry['energy_consumed']:.2f} Wh
  - Total distance: {telemetry['total_distance']:.1f} m
  - Max speed: {telemetry['max_speed_reached']:.2f} m/s
  - Max altitude: {telemetry['max_altitude']:.1f} m"""


def recharge_battery(percentage: float = 100.0) -> str:
    """Recharge battery to specified percentage"""
    physics = get_physics()
    physics.recharge_battery(percentage)
    return f"[DRONE] Battery recharged to {percentage:.1f}%"


def set_wind(speed: float, direction: float = 0.0) -> str:
    """Set wind conditions for realistic flight"""
    physics = get_physics()
    physics.set_wind(speed, direction)
    return f"[DRONE] Wind set to {speed} m/s at {direction}° bearing"

