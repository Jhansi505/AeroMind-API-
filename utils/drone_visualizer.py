"""
Advanced 3D Drone Simulator Visualization
Shows realistic drone flight with 3D model, velocity vectors, and multiple views
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class DroneVisualizer:
    """Advanced 3D drone simulator with realistic visualization"""
    
    def __init__(self):
        self.positions = [[0, 0, 0]]  # Flight path
        self.fig = None
        self.ax_3d = None
        self.ax_side = None
        self.ax_top = None
        self.ax_telemetry = None
        # Animation tuning parameters
        # speed_factor > 1.0 => faster animation, < 1.0 => slower
        self.anim_speed_factor = 1.0
        # base values used to compute steps and pause time
        self._base_step_scale = 20.0
        self._min_steps = 6
        self._max_steps = 200
        self._base_frame_delay = 0.02
        
    def add_position(self, x: float, y: float, z: float):
        """Add a new position to the trajectory"""
        # Smoothly animate from current position to new position by appending
        # intermediate points so the drone appears to move.
        import numpy as _np

        start = _np.array(self.positions[-1], dtype=float)
        end = _np.array([x, y, z], dtype=float)
        dist = _np.linalg.norm(end - start)

        if dist < 1e-3:
            # negligible movement
            self.positions.append([x, y, z])
            self.update_plot()
            return

        # Compute steps and frame delay using configurable parameters
        steps = int(max(self._min_steps, min(self._max_steps, dist * self._base_step_scale)))
        # Apply speed factor: larger speed_factor reduces pause time (faster)
        frame_delay = max(0.001, self._base_frame_delay / max(1e-6, self.anim_speed_factor))

        for t in _np.linspace(0.0, 1.0, steps + 1)[1:]:
            interp = (1.0 - t) * start + t * end
            self.positions.append([float(interp[0]), float(interp[1]), float(interp[2])])
            self.update_plot()
            try:
                plt.pause(frame_delay)
            except Exception:
                # In case interactive mode isn't available, just continue
                pass

    def set_animation_speed(self, speed_factor: float):
        """Set animation speed factor. Values >1 speed up, <1 slow down."""
        try:
            v = float(speed_factor)
            if v <= 0:
                raise ValueError("speed_factor must be > 0")
            self.anim_speed_factor = v
        except Exception:
            raise

    def get_animation_speed(self) -> float:
        return float(self.anim_speed_factor)
        
    def get_current_position(self):
        """Get the current drone position"""
        return self.positions[-1]
    
    def start_visualization(self):
        """Initialize the simulator visualization"""
        plt.ion()
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.suptitle('🚁 Autonomous Drone Flight Simulator', fontsize=16, fontweight='bold')
        
        self.ax_3d = self.fig.add_subplot(2, 2, 1, projection='3d')
        self.ax_top = self.fig.add_subplot(2, 2, 2)
        self.ax_side = self.fig.add_subplot(2, 2, 3)
        self.ax_telemetry = self.fig.add_subplot(2, 2, 4)
        self.ax_telemetry.axis('off')
        
        self.update_plot()
        plt.tight_layout()
        plt.show(block=False)
    
    def _draw_drone_model(self, ax, x: float, y: float, z: float, scale: float = 1.0):
        """Draw a 3D quadcopter drone model"""
        rotor_length = 0.3 * scale
        rotor_positions = [
            (rotor_length, rotor_length, 0),      # Front-right
            (-rotor_length, rotor_length, 0),     # Front-left
            (-rotor_length, -rotor_length, 0),    # Back-left
            (rotor_length, -rotor_length, 0),     # Back-right
        ]
        
        colors = ['red', 'red', 'blue', 'blue']
        
        for i, (rx, ry, rz) in enumerate(rotor_positions):
            rotor_x = [x, x + rx]
            rotor_y = [y, y + ry]
            rotor_z = [z, z + rz]
            ax.plot(rotor_x, rotor_y, rotor_z, color=colors[i], linewidth=3, alpha=0.8)
            
            theta = np.linspace(0, 2*np.pi, 20)
            prop_radius = 0.15 * scale
            prop_x = x + rx + prop_radius * np.cos(theta)
            prop_y = y + ry + prop_radius * np.sin(theta)
            prop_z = z + rz + np.zeros_like(theta)
            ax.plot(prop_x, prop_y, prop_z, color=colors[i], linewidth=2, alpha=0.6)
        
        ax.scatter([x], [y], [z], c='black', s=200, marker='o', zorder=10)
    
    def _draw_velocity_vector(self, ax, position: list, velocity: list, scale: float = 2.0):
        """Draw velocity vector arrow"""
        x, y, z = position
        speed = np.sqrt(sum(v**2 for v in velocity))
        
        if speed > 0.1:
            vel_normalized = np.array(velocity) / speed * scale
            ax.quiver(x, y, z, vel_normalized[0], vel_normalized[1], vel_normalized[2],
                     color='green', arrow_length_ratio=0.3, linewidth=2, alpha=0.7)
    
    def update_plot(self):
        """Update all visualization views"""
        if self.ax_3d is None:
            return
        
        positions = np.array(self.positions)
        current = positions[-1]
        
        self.ax_3d.clear()
        self.ax_top.clear()
        self.ax_side.clear()
        self.ax_telemetry.clear()
        
        self._draw_3d_view(positions, current)
        self._draw_top_view(positions, current)
        self._draw_side_view(positions, current)
        self._draw_telemetry(current, positions)
        
        plt.draw()
        plt.pause(0.001)
    
    def _draw_3d_view(self, positions: np.ndarray, current: list):
        """Draw main 3D perspective view"""
        ax = self.ax_3d
        
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
               'b-', linewidth=2, label='Flight Path', alpha=0.7)
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], 
                  c='red', marker='o', s=30, label='Waypoints', alpha=0.5)
        ax.scatter(0, 0, 0, c='orange', marker='s', s=100, label='Home', zorder=5)
        
        self._draw_drone_model(ax, current[0], current[1], current[2], scale=2.0)
        
        if current[2] > 0.1:
            ax.plot([current[0], current[0]], [current[1], current[1]], [0, current[2]], 
                   'k--', alpha=0.3, linewidth=1)
        
        from utils.physics import get_physics
        physics = get_physics()
        self._draw_velocity_vector(ax, current, physics.velocity, scale=3.0)
        
        max_range = max(np.ptp(positions[:, 0]), np.ptp(positions[:, 1]), 
                       np.ptp(positions[:, 2]), 50)
        mid_x = np.mean(positions[:, 0])
        mid_y = np.mean(positions[:, 1])
        mid_z = np.mean(positions[:, 2])
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(0, max(mid_z + max_range, 100))
        
        ax.set_xlabel('X (meters)', fontsize=10)
        ax.set_ylabel('Y (meters)', fontsize=10)
        ax.set_zlabel('Z (meters)', fontsize=10)
        ax.set_title('3D Flight View', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _draw_top_view(self, positions: np.ndarray, current: list):
        """Draw top-down view"""
        ax = self.ax_top
        
        ax.plot(positions[:, 0], positions[:, 1], 'b-', linewidth=2, label='Flight Path', alpha=0.7)
        ax.scatter(positions[:, 0], positions[:, 1], c='red', marker='o', s=30, alpha=0.5)
        ax.scatter(0, 0, c='orange', marker='s', s=100, label='Home', zorder=5)
        ax.scatter(current[0], current[1], c='green', marker='^', s=300, 
                  label='Drone', zorder=5, edgecolors='darkgreen', linewidth=2)
        
        from utils.physics import get_physics
        physics = get_physics()
        speed = np.sqrt(physics.velocity[0]**2 + physics.velocity[1]**2)
        if speed > 0.1:
            vel_scale = 10
            ax.arrow(current[0], current[1], 
                    physics.velocity[0] * vel_scale, physics.velocity[1] * vel_scale,
                    head_width=2, head_length=1.5, fc='green', ec='green', alpha=0.7)
        
        max_range = max(np.ptp(positions[:, 0]), np.ptp(positions[:, 1]), 50)
        mid_x = np.mean(positions[:, 0])
        mid_y = np.mean(positions[:, 1])
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_xlabel('X (meters)', fontsize=10)
        ax.set_ylabel('Y (meters)', fontsize=10)
        ax.set_title('Top-Down View', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _draw_side_view(self, positions: np.ndarray, current: list):
        """Draw side view"""
        ax = self.ax_side
        
        ax.plot(positions[:, 0], positions[:, 2], 'b-', linewidth=2, label='Flight Path', alpha=0.7)
        ax.scatter(positions[:, 0], positions[:, 2], c='red', marker='o', s=30, alpha=0.5)
        
        max_x = np.max(np.abs(positions[:, 0]))
        ax.plot([-max_x-10, max_x+10], [0, 0], 'k-', linewidth=3, label='Ground')
        
        ax.scatter(0, 0, c='orange', marker='s', s=100, label='Home', zorder=5)
        ax.scatter(current[0], current[2], c='green', marker='^', s=300, 
                  label='Drone', zorder=5, edgecolors='darkgreen', linewidth=2)
        ax.plot([current[0], current[0]], [0, current[2]], 'g--', linewidth=2, alpha=0.5)
        
        max_range = max(np.ptp(positions[:, 0]), np.ptp(positions[:, 2]), 50)
        mid_x = np.mean(positions[:, 0])
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(0, max(np.max(positions[:, 2]) + 20, 100))
        ax.set_xlabel('X (meters)', fontsize=10)
        ax.set_ylabel('Altitude Z (meters)', fontsize=10)
        ax.set_title('Side View (X-Z)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _draw_telemetry(self, current: list, positions: np.ndarray):
        """Draw telemetry panel"""
        from utils.physics import get_physics
        
        physics = get_physics()
        telemetry = physics.get_telemetry()
        
        ax = self.ax_telemetry
        ax.axis('off')
        
        total_distance = np.sum(np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1)))
        waypoints = len(positions)
        
        telemetry_text = f"""
╔══════════════════════════════════════════════════════════╗
║           🚁 DRONE TELEMETRY DISPLAY                     ║
╠══════════════════════════════════════════════════════════╣
║ POSITION & VELOCITY                                      ║
║   X: {current[0]:8.2f} m   |  Vx: {telemetry['velocity'][0]:7.2f} m/s
║   Y: {current[1]:8.2f} m   |  Vy: {telemetry['velocity'][1]:7.2f} m/s
║   Z: {current[2]:8.2f} m   |  Vz: {telemetry['velocity'][2]:7.2f} m/s
║   Speed: {telemetry['current_speed']:6.2f} m/s
╠══════════════════════════════════════════════════════════╣
║ BATTERY & POWER                                          ║
║   Battery: {telemetry['battery_percentage']:5.1f}% | {telemetry['battery_remaining_mah']:6.0f} mAh
║   Flight Time Remaining: {telemetry['flight_time_remaining']:4.1f} minutes
║   Energy Consumed: {telemetry['energy_consumed']:6.2f} Wh
╠══════════════════════════════════════════════════════════╣
║ FLIGHT STATISTICS                                        ║
║   Max Speed: {telemetry['max_speed_reached']:6.2f} m/s
║   Max Altitude: {telemetry['max_altitude']:7.2f} m
║   Total Distance: {total_distance:7.2f} m
║   Waypoints Passed: {waypoints:3d}
║   Total Flight Time: {telemetry['total_flight_time']:6.1f} s
╠══════════════════════════════════════════════════════════╣
║ STATUS: {'🟢 FLYING' if telemetry['is_flying'] else '🔴 LANDED'}
╚══════════════════════════════════════════════════════════╝
        """
        
        ax.text(0.05, 0.95, telemetry_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def stop_visualization(self):
        """Stop the visualization"""
        if self.fig:
            plt.close(self.fig)


_visualizer = None

def get_visualizer():
    """Get or create the global visualizer instance"""
    global _visualizer
    if _visualizer is None:
        _visualizer = DroneVisualizer()
    return _visualizer
