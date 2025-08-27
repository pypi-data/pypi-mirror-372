# Robot API

This module provides the main robot interface for libfrankapy.

## FrankaRobot Class

The `FrankaRobot` class is the main interface for controlling Franka Emika robots.

### Key Features

- Real-time robot control at 1kHz
- Joint and Cartesian space control
- Force/impedance control capabilities
- Comprehensive safety monitoring
- State monitoring and logging
- Error handling and recovery

### Constructor

```python
class FrankaRobot:
    def __init__(self, robot_ip: str, realtime_config: Optional[RealtimeConfig] = None)
```

**Parameters:**
- `robot_ip` (str): IP address of the Franka robot
- `realtime_config` (Optional[RealtimeConfig]): Real-time configuration parameters

### Connection Methods

#### connect()

Establish connection to the robot.

```python
def connect(self) -> None
```

**Raises:**
- `FrankaException`: If connection fails

#### disconnect()

Disconnect from the robot.

```python
def disconnect(self) -> None
```

#### start_control()

Start the real-time control loop.

```python
def start_control(self) -> None
```

**Raises:**
- `FrankaException`: If control cannot be started

#### stop_control()

Stop the real-time control loop.

```python
def stop_control(self) -> None
```

### State Query Methods

#### get_robot_state()

Get the current robot state.

```python
def get_robot_state(self) -> RobotState
```

**Returns:**
- `RobotState`: Current robot state including joint positions, velocities, forces, etc.

#### get_joint_positions()

Get current joint positions.

```python
def get_joint_positions(self) -> np.ndarray
```

**Returns:**
- `np.ndarray`: Array of 7 joint positions in radians

#### get_cartesian_pose()

Get current end-effector pose.

```python
def get_cartesian_pose(self) -> np.ndarray
```

**Returns:**
- `np.ndarray`: 4x4 transformation matrix representing end-effector pose

### Motion Control Methods

#### move_to_joint()

Move to specified joint positions.

```python
def move_to_joint(self, 
                  target_positions: List[float], 
                  speed_factor: float = 0.1,
                  acceleration_factor: float = 0.1,
                  timeout: float = 30.0) -> bool
```

**Parameters:**
- `target_positions` (List[float]): Target joint positions (7 values in radians)
- `speed_factor` (float): Speed scaling factor (0.0 to 1.0)
- `acceleration_factor` (float): Acceleration scaling factor (0.0 to 1.0)
- `timeout` (float): Maximum time to wait for motion completion

**Returns:**
- `bool`: True if motion completed successfully

**Raises:**
- `FrankaException`: If motion fails or times out

#### move_to_pose()

Move to specified Cartesian pose.

```python
def move_to_pose(self,
                 target_pose: np.ndarray,
                 speed_factor: float = 0.1,
                 motion_type: int = 0,
                 timeout: float = 30.0) -> bool
```

**Parameters:**
- `target_pose` (np.ndarray): 4x4 transformation matrix or [x, y, z, qx, qy, qz, qw]
- `speed_factor` (float): Speed scaling factor (0.0 to 1.0)
- `motion_type` (int): Motion planning type (0=linear, 1=joint)
- `timeout` (float): Maximum time to wait for motion completion

**Returns:**
- `bool`: True if motion completed successfully

#### execute_joint_trajectory()

Execute a joint space trajectory.

```python
def execute_joint_trajectory(self,
                            waypoints: List[List[float]],
                            duration: float,
                            speed_factor: float = 0.1) -> bool
```

**Parameters:**
- `waypoints` (List[List[float]]): List of joint position waypoints
- `duration` (float): Total trajectory duration in seconds
- `speed_factor` (float): Speed scaling factor

**Returns:**
- `bool`: True if trajectory completed successfully

### Force Control Methods

#### start_force_control()

Start force control mode.

```python
def start_force_control(self) -> None
```

#### stop_force_control()

Stop force control mode.

```python
def stop_force_control(self) -> None
```

#### set_cartesian_force()

Set desired Cartesian forces and torques.

```python
def set_cartesian_force(self, forces: np.ndarray) -> None
```

**Parameters:**
- `forces` (np.ndarray): 6-element array [fx, fy, fz, tx, ty, tz]

### Safety and Error Handling

#### stop()

Immediately stop robot motion.

```python
def stop(self) -> None
```

#### recover_from_errors()

Attempt to recover from robot errors.

```python
def recover_from_errors(self) -> bool
```

**Returns:**
- `bool`: True if recovery was successful

#### is_in_error_state()

Check if robot is in error state.

```python
def is_in_error_state(self) -> bool
```

**Returns:**
- `bool`: True if robot has errors

### Configuration Methods

#### set_joint_limits()

Set joint position limits.

```python
def set_joint_limits(self, 
                     lower_limits: List[float],
                     upper_limits: List[float]) -> None
```

#### set_cartesian_limits()

Set Cartesian workspace limits.

```python
def set_cartesian_limits(self,
                        position_limits: List[float],
                        orientation_limits: List[float]) -> None
```

## Examples

### Basic Robot Control

```python
import libfrankapy as fp
import numpy as np

# Create robot instance
robot = fp.FrankaRobot("192.168.1.100")

try:
    # Connect and start control
    robot.connect()
    robot.start_control()
    
    # Get current state
    state = robot.get_robot_state()
    print(f"Current joint positions: {state.joint_state.positions}")
    
    # Move to home position
    home_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
    robot.move_to_joint(home_joints, speed_factor=0.2)
    
    # Move in Cartesian space
    current_pose = robot.get_cartesian_pose()
    target_pose = current_pose.copy()
    target_pose[2, 3] += 0.1  # Move up 10cm
    robot.move_to_pose(target_pose, speed_factor=0.1)
    
except fp.FrankaException as e:
    print(f"Robot error: {e}")
    robot.recover_from_errors()
    
finally:
    robot.stop_control()
    robot.disconnect()
```

### Force Control Example

```python
import libfrankapy as fp
import numpy as np
import time

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Start force control
    robot.start_force_control()
    
    # Apply downward force
    force = np.array([0, 0, -5.0, 0, 0, 0])  # 5N downward
    robot.set_cartesian_force(force)
    
    # Hold for 5 seconds
    time.sleep(5.0)
    
    # Stop force control
    robot.stop_force_control()
    
finally:
    robot.stop_control()
    robot.disconnect()
```

### Trajectory Execution

```python
import libfrankapy as fp

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Define trajectory waypoints
    waypoints = [
        [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
        [0.5, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
        [0.0, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],
        [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
    ]
    
    # Execute trajectory over 10 seconds
    robot.execute_joint_trajectory(waypoints, duration=10.0, speed_factor=0.3)
    
finally:
    robot.stop_control()
    robot.disconnect()
```

## See Also

- [State API](/api/state) - Robot state representations
- [Control API](/api/control) - Control algorithms
- [Exceptions API](/api/exceptions) - Error handling
