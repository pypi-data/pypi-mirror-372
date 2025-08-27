# Quick Start

This guide will help you get started with libfrankapy quickly.

## Basic Setup

First, make sure you have libfrankapy installed and your Franka robot is properly configured.

## Connecting to the Robot

```python
import libfrankapy as fp

# Create robot instance
robot = fp.FrankaRobot("192.168.1.100")  # Replace with your robot's IP

# Connect to the robot
robot.connect()

# Start control mode
robot.start_control()
```

## Basic Robot Control

### Getting Robot State

```python
# Get current robot state
state = robot.get_robot_state()

print(f"Joint positions: {state.joint_state.positions}")
print(f"End-effector pose: {state.cartesian_state.pose}")
print(f"Forces: {state.cartesian_state.forces}")
```

### Joint Space Movement

```python
# Define target joint positions (7 joints)
target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]

# Move to target position
robot.move_to_joint(target_joints, speed_factor=0.1)
```

### Cartesian Space Movement

```python
import numpy as np

# Get current pose
current_pose = robot.get_robot_state().cartesian_state.pose

# Move 10cm in Z direction
target_pose = current_pose.copy()
target_pose[2, 3] += 0.1  # Z translation

robot.move_to_pose(target_pose, speed_factor=0.1)
```

### Trajectory Control

```python
# Define waypoints
waypoints = [
    [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
    [0.1, -0.685, 0.1, -2.256, 0.1, 1.671, 0.885],
    [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
]

# Execute trajectory
robot.execute_joint_trajectory(waypoints, duration=5.0)
```

## Safety and Error Handling

Always use proper error handling:

```python
import libfrankapy as fp

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Your robot control code here
    target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
    robot.move_to_joint(target_joints, speed_factor=0.1)
    
except fp.FrankaException as e:
    print(f"Robot error: {e}")
    robot.recover_from_errors()
    
except Exception as e:
    print(f"General error: {e}")
    
finally:
    # Always disconnect properly
    robot.stop_control()
    robot.disconnect()
```

## Complete Example

Here's a complete example that demonstrates basic robot control:

```python
#!/usr/bin/env python3

import libfrankapy as fp
import numpy as np
import time

def main():
    # Robot configuration
    robot_ip = "192.168.1.100"
    
    # Create robot instance
    robot = fp.FrankaRobot(robot_ip)
    
    try:
        # Connect and start control
        print("Connecting to robot...")
        robot.connect()
        robot.start_control()
        print("Connected successfully!")
        
        # Get initial state
        initial_state = robot.get_robot_state()
        print(f"Initial joint positions: {initial_state.joint_state.positions}")
        
        # Move to home position
        home_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        print("Moving to home position...")
        robot.move_to_joint(home_joints, speed_factor=0.1)
        
        # Wait a moment
        time.sleep(1.0)
        
        # Move in Cartesian space
        print("Moving in Cartesian space...")
        current_pose = robot.get_robot_state().cartesian_state.pose
        
        # Move up 5cm
        target_pose = current_pose.copy()
        target_pose[2, 3] += 0.05
        robot.move_to_pose(target_pose, speed_factor=0.1)
        
        # Move back down
        robot.move_to_pose(current_pose, speed_factor=0.1)
        
        print("Demo completed successfully!")
        
    except fp.FrankaException as e:
        print(f"Robot error: {e}")
        robot.recover_from_errors()
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Clean shutdown
        print("Disconnecting...")
        robot.stop_control()
        robot.disconnect()
        print("Disconnected.")

if __name__ == "__main__":
    main()
```

## Next Steps

- Check out the [examples](/examples) for more advanced usage
- Read the [Robot API](/api/robot) documentation for complete API reference
- Learn about [installation](/installation) options
- Explore [architecture](/development/architecture) for understanding the internals
