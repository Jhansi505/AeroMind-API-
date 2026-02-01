from utils.drone_visualizer import get_visualizer

# Payload tracking
_payload_loaded = False
_delivery_locations = {}

def load_payload(item_name: str = "package") -> str:
    """Load payload onto drone"""
    global _payload_loaded
    _payload_loaded = True
    return f"[MISSION] Payload '{item_name}' loaded successfully."

def drop_payload(location_name: str = "current location") -> str:
    """Drop payload at current location"""
    global _payload_loaded
    visualizer = get_visualizer()
    current = visualizer.get_current_position()
    
    if not _payload_loaded:
        return "[MISSION] ERROR: No payload loaded!"
    
    _payload_loaded = False
    _delivery_locations[location_name] = current.copy()
    
    return f"[MISSION] Payload dropped at {location_name} - Coordinates: ({current[0]:.1f}, {current[1]:.1f}, {current[2]:.1f})"

def deliver_to_location(x: float, y: float, z: float, location_name: str = "delivery point") -> str:
    """Fly to location and drop payload"""
    from tools.navigation_tools import move_to_location
    
    if not _payload_loaded:
        return "[MISSION] ERROR: No payload loaded! Use load_payload first."
    
    # Move to location
    move_result = move_to_location(x, y, z)
    
    # Drop payload
    drop_result = drop_payload(location_name)
    
    return f"{move_result}\n{drop_result}"

def return_to_base_and_land() -> str:
    """Return to home base (0,0) and land"""
    from tools.navigation_tools import return_to_home
    
    result = return_to_home()
    return f"{result}\n[MISSION] Landing at base."

def check_payload_status() -> str:
    """Check if payload is loaded"""
    status = "LOADED" if _payload_loaded else "EMPTY"
    return f"[MISSION] Payload status: {status}"

def list_delivery_locations() -> str:
    """List all delivery locations"""
    if not _delivery_locations:
        return "[MISSION] No deliveries made yet."
    
    locations = "\n".join([f"  - {name}: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})" 
                          for name, pos in _delivery_locations.items()])
    return f"[MISSION] Delivery locations:\n{locations}"

def verify_delivery_otp(otp: int) -> bool:
    VALID_OTP = 1234
    return otp == VALID_OTP

def update_delivery_status(status: str) -> str:
    return f"[MISSION STATUS] {status}"
