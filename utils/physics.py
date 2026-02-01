"""
Realistic drone physics simulation
"""
import math
import time
from typing import Tuple
from utils.logger import get_logger

logger = get_logger("DronePhysics")

class DronePhysics:
    """Realistic physics simulation for autonomous drone"""
    
    # Physical constants
    GRAVITY = 9.81  # m/s^2
    AIR_DENSITY = 1.225  # kg/m^3 at sea level
    
    # Drone specifications
    MASS = 1.2  # kg (typical for consumer drones like DJI Mini)
    ROTOR_DIAMETER = 0.25  # m (250mm rotors)
    DRAG_COEFFICIENT = 0.5  # unitless
    MAX_SPEED = 20.0  # m/s (72 km/h)
    MAX_ACCELERATION = 5.0  # m/s^2
    MAX_CLIMB_RATE = 3.0  # m/s (vertical)
    
    # Power characteristics
    BATTERY_CAPACITY = 2250.0  # mAh
    VOLTAGE = 11.55  # V (3S LiPo)
    IDLE_POWER = 20.0  # W (hovering)
    MAX_POWER = 100.0  # W
    
    # Environmental
    WIND_SPEED = 0.0  # m/s (configurable)
    WIND_DIRECTION = 0.0  # degrees
    
    def __init__(self):
        self.position = [0.0, 0.0, 0.0]  # meters (x, y, z)
        self.velocity = [0.0, 0.0, 0.0]  # m/s
        self.acceleration = [0.0, 0.0, 0.0]  # m/s^2
        
        # Battery state
        self.battery_capacity = self.BATTERY_CAPACITY  # mAh
        self.battery_current = self.BATTERY_CAPACITY  # mAh remaining
        
        # Flight state
        self.is_flying = False
        self.flight_start_time = None
        self.total_flight_time = 0.0  # seconds
        self.energy_consumed = 0.0  # Wh
        
        # Flight statistics
        self.max_speed_reached = 0.0  # m/s
        self.max_altitude = 0.0  # m
        self.total_distance = 0.0  # m
        self.waypoints_passed = 0
    
    def takeoff(self, target_height: float) -> Tuple[float, float]:
        """
        Simulate takeoff to target height
        Returns: (time_required, energy_consumed)
        """
        if self.is_flying:
            return 0.0, 0.0
        
        self.is_flying = True
        self.flight_start_time = time.time()
        
        # Calculate climb time with acceleration
        climb_time = target_height / self.MAX_CLIMB_RATE
        
        # Energy for climbing (overcome gravity + drag)
        hover_power = self._calculate_hover_power()
        climb_power = self._calculate_climb_power(self.MAX_CLIMB_RATE)
        avg_power = (hover_power + climb_power) / 2
        energy_wh = (avg_power * climb_time) / 3600.0  # Convert to Wh
        
        # Update state
        self.position[2] = target_height
        self.energy_consumed += energy_wh
        self._consume_battery(energy_wh)
        self.max_altitude = max(self.max_altitude, target_height)
        
        logger.info(f"Takeoff: {climb_time:.1f}s, {energy_wh:.2f}Wh, Battery: {self.battery_percentage:.1f}%")
        
        return climb_time, energy_wh
    
    def move(self, dx: float, dy: float, dz: float) -> Tuple[float, float]:
        """
        Simulate movement to new position
        Returns: (time_required, energy_consumed)
        """
        if not self.is_flying:
            return 0.0, 0.0
        
        # Calculate distance
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Determine movement type
        if dz != 0:  # Vertical movement
            time_required = abs(dz) / self.MAX_CLIMB_RATE
            power = self._calculate_climb_power(self.MAX_CLIMB_RATE if dz > 0 else -self.MAX_CLIMB_RATE)
        else:  # Horizontal movement
            horizontal_distance = math.sqrt(dx**2 + dy**2)
            time_required = horizontal_distance / self.MAX_SPEED if self.MAX_SPEED > 0 else 0
            power = self._calculate_cruise_power(self.MAX_SPEED)
        
        # Calculate energy
        energy_wh = (power * time_required) / 3600.0
        
        # Update state
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz
        self.total_distance += distance
        self.energy_consumed += energy_wh
        self.max_altitude = max(self.max_altitude, self.position[2])
        
        # Update velocity for display
        if time_required > 0:
            self.velocity[0] = dx / time_required
            self.velocity[1] = dy / time_required
            self.velocity[2] = dz / time_required
        
        self.max_speed_reached = max(self.max_speed_reached, 
                                    math.sqrt(sum(v**2 for v in self.velocity)))
        
        self._consume_battery(energy_wh)
        
        return time_required, energy_wh
    
    def land(self) -> Tuple[float, float]:
        """
        Simulate landing from current height
        Returns: (time_required, energy_consumed)
        """
        if not self.is_flying:
            return 0.0, 0.0
        
        current_height = self.position[2]
        descent_time = current_height / self.MAX_CLIMB_RATE
        
        # Energy for descent
        hover_power = self._calculate_hover_power()
        energy_wh = (hover_power * descent_time) / 3600.0
        
        # Update state
        self.position[2] = 0.0
        self.velocity = [0.0, 0.0, 0.0]
        self.is_flying = False
        self.energy_consumed += energy_wh
        self.total_flight_time = time.time() - self.flight_start_time if self.flight_start_time else 0
        
        self._consume_battery(energy_wh)
        
        return descent_time, energy_wh
    
    def _calculate_hover_power(self) -> float:
        """Calculate power required to hover"""
        # P = mg / (2 * rho * A)^0.5
        rotor_area = math.pi * (self.ROTOR_DIAMETER / 2) ** 2
        induced_velocity = math.sqrt((self.MASS * self.GRAVITY) / (2 * self.AIR_DENSITY * rotor_area * 2))
        power_hover = self.MASS * self.GRAVITY * induced_velocity
        
        return max(self.IDLE_POWER, power_hover / 1000)  # Convert to W
    
    def _calculate_climb_power(self, climb_rate: float) -> float:
        """Calculate power required for vertical climb"""
        hover_power = self._calculate_hover_power()
        # Add power for climbing: P = m*g*v_climb
        climb_power = (self.MASS * self.GRAVITY * abs(climb_rate)) / 1000
        return min(self.MAX_POWER, hover_power + climb_power)
    
    def _calculate_cruise_power(self, speed: float) -> float:
        """Calculate power required for horizontal cruise"""
        hover_power = self._calculate_hover_power()
        # Add drag force power: P = 0.5 * rho * Cd * A * v^3
        rotor_area = math.pi * (self.ROTOR_DIAMETER / 2) ** 2
        drag_power = 0.5 * self.AIR_DENSITY * self.DRAG_COEFFICIENT * rotor_area * (speed ** 3) / 1000
        return min(self.MAX_POWER, hover_power + drag_power)
    
    def _consume_battery(self, energy_wh: float):
        """Consume battery energy"""
        # Convert Wh to mAh: mAh = Wh * 1000 / V
        mah_consumed = (energy_wh * 1000) / self.VOLTAGE
        self.battery_current = max(0, self.battery_current - mah_consumed)
    
    @property
    def battery_percentage(self) -> float:
        """Get battery percentage"""
        return (self.battery_current / self.battery_capacity) * 100
    
    @property
    def flight_time_remaining(self) -> float:
        """Estimate remaining flight time in minutes"""
        if self.battery_current <= 0:
            return 0.0
        
        remaining_energy = (self.battery_current * self.VOLTAGE) / 1000  # Wh
        hover_power = self._calculate_hover_power()
        
        return (remaining_energy / hover_power) * 60  # minutes
    
    @property
    def current_speed(self) -> float:
        """Get current speed in m/s"""
        return math.sqrt(sum(v**2 for v in self.velocity))
    
    def recharge_battery(self, percentage: float = 100.0):
        """Recharge battery to percentage"""
        self.battery_current = (percentage / 100.0) * self.battery_capacity
        self.energy_consumed = 0.0
        self.total_flight_time = 0.0
        self.total_distance = 0.0
        self.max_speed_reached = 0.0
        self.max_altitude = 0.0
        self.waypoints_passed = 0
    
    def get_telemetry(self) -> dict:
        """Get complete telemetry data"""
        return {
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "current_speed": self.current_speed,
            "is_flying": self.is_flying,
            "battery_percentage": self.battery_percentage,
            "battery_remaining_mah": self.battery_current,
            "flight_time_remaining": self.flight_time_remaining,
            "energy_consumed": self.energy_consumed,
            "total_flight_time": self.total_flight_time,
            "total_distance": self.total_distance,
            "max_altitude": self.max_altitude,
            "max_speed_reached": self.max_speed_reached,
        }
    
    def set_wind(self, wind_speed: float, wind_direction: float = 0.0):
        """Set wind conditions"""
        self.WIND_SPEED = wind_speed
        self.WIND_DIRECTION = wind_direction
        logger.info(f"Wind set to {wind_speed} m/s at {wind_direction}°")


# Global physics instance
_physics = None

def get_physics():
    """Get or create the global physics instance"""
    global _physics
    if _physics is None:
        _physics = DronePhysics()
    return _physics


def reset_physics():
    """Reset physics to initial state"""
    global _physics
    _physics = DronePhysics()
