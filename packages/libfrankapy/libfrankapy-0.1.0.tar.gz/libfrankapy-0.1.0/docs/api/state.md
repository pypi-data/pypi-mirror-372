# State API

This module provides classes for representing robot state information.

## Core State Classes

### RobotState

Main class containing complete robot state information.

```python
class RobotState:
    def __init__(self)
```

#### Attributes

- `timestamp` (float): State timestamp in seconds
- `joint_state` (JointState): Joint space state information
- `cartesian_state` (CartesianState): Cartesian space state information
- `force_state` (ForceState): Force/torque measurements
- `error_state` (ErrorState): Error and safety information
- `control_state` (ControlState): Control system status

#### Methods

##### is_valid()

Check if the state data is valid.

```python
def is_valid(self) -> bool
```

**Returns:**
- `bool`: True if state is valid

##### to_dict()

Convert state to dictionary format.

```python
def to_dict(self) -> dict
```

**Returns:**
- `dict`: State data as dictionary

### JointState

Contains joint space state information.

```python
class JointState:
    def __init__(self)
```

#### Attributes

- `positions` (np.ndarray): Joint positions in radians (7 elements)
- `velocities` (np.ndarray): Joint velocities in rad/s (7 elements)
- `accelerations` (np.ndarray): Joint accelerations in rad/s² (7 elements)
- `efforts` (np.ndarray): Joint torques in Nm (7 elements)
- `commanded_positions` (np.ndarray): Commanded joint positions
- `commanded_velocities` (np.ndarray): Commanded joint velocities

#### Methods

##### get_joint_position()

Get position of a specific joint.

```python
def get_joint_position(self, joint_index: int) -> float
```

**Parameters:**
- `joint_index` (int): Joint index (0-6)

**Returns:**
- `float`: Joint position in radians

##### get_joint_velocity()

Get velocity of a specific joint.

```python
def get_joint_velocity(self, joint_index: int) -> float
```

**Parameters:**
- `joint_index` (int): Joint index (0-6)

**Returns:**
- `float`: Joint velocity in rad/s

### CartesianState

Contains Cartesian space state information.

```python
class CartesianState:
    def __init__(self)
```

#### Attributes

- `pose` (np.ndarray): End-effector pose as 4x4 transformation matrix
- `position` (np.ndarray): End-effector position [x, y, z]
- `orientation` (np.ndarray): End-effector orientation as quaternion [x, y, z, w]
- `velocity` (np.ndarray): End-effector velocity [vx, vy, vz, wx, wy, wz]
- `acceleration` (np.ndarray): End-effector acceleration
- `forces` (np.ndarray): Applied forces and torques [fx, fy, fz, tx, ty, tz]

#### Methods

##### get_position()

Get end-effector position.

```python
def get_position(self) -> np.ndarray
```

**Returns:**
- `np.ndarray`: Position vector [x, y, z]

##### get_orientation_matrix()

Get orientation as rotation matrix.

```python
def get_orientation_matrix(self) -> np.ndarray
```

**Returns:**
- `np.ndarray`: 3x3 rotation matrix

##### get_orientation_euler()

Get orientation as Euler angles.

```python
def get_orientation_euler(self, convention: str = 'xyz') -> np.ndarray
```

**Parameters:**
- `convention` (str): Euler angle convention

**Returns:**
- `np.ndarray`: Euler angles [roll, pitch, yaw]

### ForceState

Contains force and torque measurements.

```python
class ForceState:
    def __init__(self)
```

#### Attributes

- `external_forces` (np.ndarray): External forces/torques [fx, fy, fz, tx, ty, tz]
- `contact_forces` (np.ndarray): Contact forces at end-effector
- `joint_torques` (np.ndarray): Measured joint torques
- `gravity_compensation` (np.ndarray): Gravity compensation torques
- `coriolis_compensation` (np.ndarray): Coriolis compensation torques

#### Methods

##### get_force_magnitude()

Get magnitude of external force.

```python
def get_force_magnitude(self) -> float
```

**Returns:**
- `float`: Force magnitude in Newtons

##### get_torque_magnitude()

Get magnitude of external torque.

```python
def get_torque_magnitude(self) -> float
```

**Returns:**
- `float`: Torque magnitude in Nm

### ErrorState

Contains error and safety information.

```python
class ErrorState:
    def __init__(self)
```

#### Attributes

- `has_errors` (bool): True if robot has errors
- `error_codes` (List[int]): List of active error codes
- `error_messages` (List[str]): Human-readable error messages
- `safety_state` (SafetyState): Safety system status
- `emergency_stop_active` (bool): True if emergency stop is active

#### Methods

##### get_error_description()

Get description of current errors.

```python
def get_error_description(self) -> str
```

**Returns:**
- `str`: Formatted error description

##### is_recoverable()

Check if errors are recoverable.

```python
def is_recoverable(self) -> bool
```

**Returns:**
- `bool`: True if errors can be recovered

### ControlState

Contains control system status information.

```python
class ControlState:
    def __init__(self)
```

#### Attributes

- `control_mode` (ControlMode): Current control mode
- `is_connected` (bool): True if robot is connected
- `is_control_active` (bool): True if control loop is active
- `control_frequency` (float): Actual control frequency in Hz
- `communication_quality` (float): Communication quality (0.0 to 1.0)

## Utility Classes

### SafetyState

Contains safety system information.

```python
class SafetyState:
    def __init__(self)
```

#### Attributes

- `joint_position_limits_violated` (List[bool]): Joint limit violations
- `joint_velocity_limits_violated` (List[bool]): Velocity limit violations
- `cartesian_position_limits_violated` (bool): Cartesian limit violations
- `force_limits_violated` (bool): Force limit violations
- `collision_detected` (bool): True if collision is detected

### ControlMode

Enumeration of control modes.

```python
class ControlMode(Enum):
    IDLE = 0
    POSITION_CONTROL = 1
    VELOCITY_CONTROL = 2
    FORCE_CONTROL = 3
    IMPEDANCE_CONTROL = 4
    TRAJECTORY_CONTROL = 5
```

## State Utilities

### State Conversion Functions

#### pose_to_transform()

Convert pose representation to transformation matrix.

```python
def pose_to_transform(position: np.ndarray, 
                     orientation: np.ndarray) -> np.ndarray
```

**Parameters:**
- `position` (np.ndarray): Position vector [x, y, z]
- `orientation` (np.ndarray): Quaternion [x, y, z, w]

**Returns:**
- `np.ndarray`: 4x4 transformation matrix

#### transform_to_pose()

Convert transformation matrix to pose representation.

```python
def transform_to_pose(transform: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```

**Parameters:**
- `transform` (np.ndarray): 4x4 transformation matrix

**Returns:**
- `Tuple[np.ndarray, np.ndarray]`: Position and quaternion

#### euler_to_quaternion()

Convert Euler angles to quaternion.

```python
def euler_to_quaternion(euler: np.ndarray, 
                        convention: str = 'xyz') -> np.ndarray
```

**Parameters:**
- `euler` (np.ndarray): Euler angles [roll, pitch, yaw]
- `convention` (str): Euler angle convention

**Returns:**
- `np.ndarray`: Quaternion [x, y, z, w]

#### quaternion_to_euler()

Convert quaternion to Euler angles.

```python
def quaternion_to_euler(quaternion: np.ndarray, 
                       convention: str = 'xyz') -> np.ndarray
```

**Parameters:**
- `quaternion` (np.ndarray): Quaternion [x, y, z, w]
- `convention` (str): Euler angle convention

**Returns:**
- `np.ndarray`: Euler angles [roll, pitch, yaw]

## Examples

### Basic State Monitoring

```python
import libfrankapy as fp
import time

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Monitor robot state
    for i in range(100):
        state = robot.get_robot_state()
        
        print(f"Time: {state.timestamp:.3f}")
        print(f"Joint 1 position: {state.joint_state.positions[0]:.3f} rad")
        print(f"End-effector position: {state.cartesian_state.position}")
        print(f"External forces: {state.force_state.external_forces[:3]}")
        
        if state.error_state.has_errors:
            print(f"Errors: {state.error_state.get_error_description()}")
        
        time.sleep(0.1)
        
finally:
    robot.stop_control()
    robot.disconnect()
```

### State Data Logging

```python
import libfrankapy as fp
import numpy as np
import json
import time

class StateLogger:
    def __init__(self):
        self.data = []
    
    def log_state(self, state: fp.RobotState):
        state_dict = {
            'timestamp': state.timestamp,
            'joint_positions': state.joint_state.positions.tolist(),
            'joint_velocities': state.joint_state.velocities.tolist(),
            'cartesian_position': state.cartesian_state.position.tolist(),
            'cartesian_orientation': state.cartesian_state.orientation.tolist(),
            'external_forces': state.force_state.external_forces.tolist(),
            'control_mode': state.control_state.control_mode.value,
            'has_errors': state.error_state.has_errors
        }
        self.data.append(state_dict)
    
    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_statistics(self):
        if not self.data:
            return {}
        
        positions = np.array([d['joint_positions'] for d in self.data])
        velocities = np.array([d['joint_velocities'] for d in self.data])
        
        return {
            'duration': self.data[-1]['timestamp'] - self.data[0]['timestamp'],
            'samples': len(self.data),
            'avg_joint_positions': np.mean(positions, axis=0).tolist(),
            'max_joint_velocities': np.max(np.abs(velocities), axis=0).tolist(),
            'error_count': sum(1 for d in self.data if d['has_errors'])
        }

# Usage
robot = fp.FrankaRobot("192.168.1.100")
logger = StateLogger()

try:
    robot.connect()
    robot.start_control()
    
    # Log data for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10.0:
        state = robot.get_robot_state()
        logger.log_state(state)
        time.sleep(0.01)  # 100Hz logging
    
    # Save and analyze data
    logger.save_to_file('robot_state_log.json')
    stats = logger.get_statistics()
    print(f"Logged {stats['samples']} samples over {stats['duration']:.2f} seconds")
    print(f"Average joint positions: {stats['avg_joint_positions']}")
    
finally:
    robot.stop_control()
    robot.disconnect()
```

### State-based Safety Monitoring

```python
import libfrankapy as fp
import numpy as np

class SafetyMonitor:
    def __init__(self):
        self.force_threshold = 20.0  # Newtons
        self.velocity_threshold = 2.0  # rad/s
        self.position_limits = {
            'x': (-0.8, 0.8),
            'y': (-0.8, 0.8),
            'z': (0.1, 1.2)
        }
    
    def check_safety(self, state: fp.RobotState) -> dict:
        safety_status = {
            'safe': True,
            'warnings': [],
            'errors': []
        }
        
        # Check force limits
        force_magnitude = state.force_state.get_force_magnitude()
        if force_magnitude > self.force_threshold:
            safety_status['safe'] = False
            safety_status['errors'].append(f"Excessive force: {force_magnitude:.1f}N")
        
        # Check velocity limits
        max_velocity = np.max(np.abs(state.joint_state.velocities))
        if max_velocity > self.velocity_threshold:
            safety_status['warnings'].append(f"High velocity: {max_velocity:.2f} rad/s")
        
        # Check workspace limits
        pos = state.cartesian_state.position
        for axis, (min_val, max_val) in self.position_limits.items():
            axis_idx = {'x': 0, 'y': 1, 'z': 2}[axis]
            if not (min_val <= pos[axis_idx] <= max_val):
                safety_status['safe'] = False
                safety_status['errors'].append(f"Workspace limit violated: {axis}={pos[axis_idx]:.3f}")
        
        # Check robot errors
        if state.error_state.has_errors:
            safety_status['safe'] = False
            safety_status['errors'].append(state.error_state.get_error_description())
        
        return safety_status

# Usage
robot = fp.FrankaRobot("192.168.1.100")
safety_monitor = SafetyMonitor()

try:
    robot.connect()
    robot.start_control()
    
    while True:
        state = robot.get_robot_state()
        safety_status = safety_monitor.check_safety(state)
        
        if not safety_status['safe']:
            print("SAFETY VIOLATION!")
            for error in safety_status['errors']:
                print(f"  ERROR: {error}")
            robot.stop()
            break
        
        if safety_status['warnings']:
            for warning in safety_status['warnings']:
                print(f"  WARNING: {warning}")
        
        time.sleep(0.01)
        
finally:
    robot.stop_control()
    robot.disconnect()
```

## See Also

- [Robot API](/api/robot) - Main robot interface
- [Control API](/api/control) - Control algorithms
- [Exceptions API](/api/exceptions) - Error handling
