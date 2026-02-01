# 🚁 Quick Start Guide - Enhanced Features

## What's New?

You've successfully integrated:
- ✅ **GPS Navigation** (geopy)
- ✅ **Path Planning** (networkx)  
- ✅ **Realistic Physics** (dronekit - ready for future use)

## 🎯 Try These New Commands!

### 1. GPS Navigation
```
Mission Command > move to GPS coordinates 37.7749, -122.4194, 50
Mission Command > where am I in GPS?
```

### 2. Smart Path Planning (Obstacle Avoidance)
```
Mission Command > add obstacle at 50, 50, 15 with radius 10
Mission Command > plan path to 100, 100, 20
```
The drone will automatically avoid obstacles!

### 3. No-Fly Zones
```
Mission Command > add no-fly zone from x 20 to 40, y 20 to 40, z 0 to 50
Mission Command > plan path to 30, 30, 25
```
The path will route around the restricted area!

### 4. Complete Delivery Mission Example
```
Mission Command > load package
Mission Command > takeoff to 20 meters
Mission Command > add obstacle at 50, 30, 15 with radius 8
Mission Command > plan path to 100, 50, 15
Mission Command > drop payload at customer location
Mission Command > return to base and land
```

## 📋 Full Command List

### Basic Navigation
- `takeoff to [height] meters`
- `move forward/backward/left/right [distance] meters`
- `move to coordinates [x], [y], [z]`
- `land`
- `return to home`

### GPS Navigation (NEW!)
- `move to GPS [lat], [lon], [altitude]`
- `get current GPS` or `where am I in GPS?`

### Path Planning (NEW!)
- `plan path to [x], [y], [z]` - Optimal path with obstacle avoidance
- `add obstacle at [x], [y], [z] with radius [r]` - Add obstacle
- `add no-fly zone from x [min] to [max], y [min] to [max], z [min] to [max]`

### Delivery Mission
- `load payload` or `load package`
- `drop payload at [location name]`
- `deliver to location [x], [y], [z]`
- `return to base and land`
- `check payload status`
- `list delivery locations`

## 🎮 How It Works

### GPS Conversion
- Base GPS is set to: **37.7749°N, 122.4194°W** (San Francisco)
- You can change this in `utils/gps_utils.py`
- XYZ coordinates are relative to this base point

### Path Planning
- Uses A* algorithm for optimal paths
- Grid resolution: 5 meters (adjustable)
- Automatically avoids obstacles and no-fly zones
- Simplifies paths to reduce waypoints

### Visualization
- Blue line: Flight path
- Red dots: Waypoints
- Green triangle: Current position
- Orange square: Origin/Base

## 🔧 Advanced Configuration

### Change GPS Base Location
Edit `utils/gps_utils.py`:
```python
# Change to your location
BASE_GPS = (YOUR_LAT, YOUR_LON)
```

### Adjust Path Planning Resolution
Edit `utils/path_planner.py`:
```python
# Smaller = more precise, but slower
PathPlanner(grid_size=200, resolution=5)
```

## 🚀 Example Mission Scenarios

### Scenario 1: Simple Delivery
```
load package
takeoff to 25 meters
move to coordinates 80, 60, 25
drop payload at warehouse A
return to base and land
```

### Scenario 2: Obstacle Avoidance
```
takeoff to 30 meters
add obstacle at 50, 50, 20 with radius 15
plan path to 100, 100, 30
drop payload at location B
plan path to 0, 0, 30
land
```

### Scenario 3: GPS Navigation
```
takeoff to 50 meters
move to GPS 37.7750, -122.4195, 50
get current GPS
return to home
```

### Scenario 4: Multiple Deliveries
```
load payload
takeoff to 20 meters
deliver to location 50, 30, 15 at house 1
move to coordinates 0, 0, 20
load payload
deliver to location 80, 60, 15 at house 2
return to base and land
list delivery locations
```

## 📊 What to Expect

When you run commands:
1. **3D Graph Updates** - Real-time visualization
2. **Path Planning** - Shows optimized route
3. **Console Output** - Confirms each action
4. **GPS Conversion** - Automatic XYZ ↔ GPS conversion

## 🐛 Troubleshooting

**Graph not updating?**
- Make sure matplotlib window is visible
- Try resizing the window

**Path planning not avoiding obstacles?**
- Increase obstacle radius
- Check that obstacle is between start and goal

**GPS coordinates seem wrong?**
- Verify base GPS location in `gps_utils.py`
- Check lat/lon format (decimal degrees)

## 🎯 Next Steps

1. **Run the app**: `python main.py`
2. **Try basic commands** first
3. **Add obstacles** and test path planning
4. **Try GPS navigation**
5. **Run a complete delivery mission**

Enjoy your enhanced autonomous drone system! 🚁✨
