# Utilities API

This module provides utility functions and helper classes for common robotics operations in libfrankapy.

## Mathematical Utilities

### Transformation Functions

#### pose_to_matrix()

Convert pose representation to transformation matrix.

```python
def pose_to_matrix(position: np.ndarray, 
                  orientation: np.ndarray, 
                  format: str = 'quaternion') -> np.ndarray
```

**Parameters:**
- `position` (np.ndarray): 3D position [x, y, z]
- `orientation` (np.ndarray): Orientation (quaternion, euler, or rotation matrix)
- `format` (str): Orientation format ('quaternion', 'euler', 'matrix')

**Returns:**
- `np.ndarray`: 4x4 transformation matrix

#### matrix_to_pose()

Convert transformation matrix to pose representation.

```python
def matrix_to_pose(matrix: np.ndarray, 
                  format: str = 'quaternion') -> Tuple[np.ndarray, np.ndarray]
```

**Parameters:**
- `matrix` (np.ndarray): 4x4 transformation matrix
- `format` (str): Desired orientation format

**Returns:**
- `Tuple[np.ndarray, np.ndarray]`: Position and orientation

#### quaternion_to_euler()

Convert quaternion to Euler angles.

```python
def quaternion_to_euler(quaternion: np.ndarray, 
                        sequence: str = 'xyz') -> np.ndarray
```

**Parameters:**
- `quaternion` (np.ndarray): Quaternion [w, x, y, z]
- `sequence` (str): Euler angle sequence

**Returns:**
- `np.ndarray`: Euler angles [roll, pitch, yaw]

#### euler_to_quaternion()

Convert Euler angles to quaternion.

```python
def euler_to_quaternion(euler: np.ndarray, 
                        sequence: str = 'xyz') -> np.ndarray
```

**Parameters:**
- `euler` (np.ndarray): Euler angles [roll, pitch, yaw]
- `sequence` (str): Euler angle sequence

**Returns:**
- `np.ndarray`: Quaternion [w, x, y, z]

### Interpolation Functions

#### linear_interpolation()

Perform linear interpolation between two points.

```python
def linear_interpolation(start: np.ndarray, 
                        end: np.ndarray, 
                        t: float) -> np.ndarray
```

**Parameters:**
- `start` (np.ndarray): Start point
- `end` (np.ndarray): End point
- `t` (float): Interpolation parameter [0, 1]

**Returns:**
- `np.ndarray`: Interpolated point

#### slerp()

Spherical linear interpolation for quaternions.

```python
def slerp(q1: np.ndarray, 
         q2: np.ndarray, 
         t: float) -> np.ndarray
```

**Parameters:**
- `q1` (np.ndarray): Start quaternion
- `q2` (np.ndarray): End quaternion
- `t` (float): Interpolation parameter [0, 1]

**Returns:**
- `np.ndarray`: Interpolated quaternion

#### pose_interpolation()

Interpolate between two poses.

```python
def pose_interpolation(pose1: np.ndarray, 
                      pose2: np.ndarray, 
                      t: float) -> np.ndarray
```

**Parameters:**
- `pose1` (np.ndarray): Start pose (4x4 matrix)
- `pose2` (np.ndarray): End pose (4x4 matrix)
- `t` (float): Interpolation parameter [0, 1]

**Returns:**
- `np.ndarray`: Interpolated pose (4x4 matrix)

### Trajectory Generation

#### generate_joint_trajectory()

Generate smooth joint trajectory.

```python
def generate_joint_trajectory(start_joints: np.ndarray,
                             end_joints: np.ndarray,
                             duration: float,
                             frequency: float = 100.0,
                             profile: str = 'cubic') -> np.ndarray
```

**Parameters:**
- `start_joints` (np.ndarray): Start joint positions
- `end_joints` (np.ndarray): End joint positions
- `duration` (float): Trajectory duration in seconds
- `frequency` (float): Trajectory frequency in Hz
- `profile` (str): Velocity profile ('linear', 'cubic', 'quintic')

**Returns:**
- `np.ndarray`: Joint trajectory (N x 7)

#### generate_cartesian_trajectory()

Generate smooth Cartesian trajectory.

```python
def generate_cartesian_trajectory(start_pose: np.ndarray,
                                 end_pose: np.ndarray,
                                 duration: float,
                                 frequency: float = 100.0,
                                 profile: str = 'cubic') -> np.ndarray
```

**Parameters:**
- `start_pose` (np.ndarray): Start pose (4x4 matrix)
- `end_pose` (np.ndarray): End pose (4x4 matrix)
- `duration` (float): Trajectory duration in seconds
- `frequency` (float): Trajectory frequency in Hz
- `profile` (str): Velocity profile

**Returns:**
- `np.ndarray`: Pose trajectory (N x 4 x 4)

#### generate_circular_trajectory()

Generate circular trajectory in Cartesian space.

```python
def generate_circular_trajectory(center: np.ndarray,
                                radius: float,
                                normal: np.ndarray,
                                start_angle: float = 0.0,
                                end_angle: float = 2*np.pi,
                                num_points: int = 100) -> np.ndarray
```

**Parameters:**
- `center` (np.ndarray): Circle center [x, y, z]
- `radius` (float): Circle radius
- `normal` (np.ndarray): Circle normal vector
- `start_angle` (float): Start angle in radians
- `end_angle` (float): End angle in radians
- `num_points` (int): Number of trajectory points

**Returns:**
- `np.ndarray`: Circular trajectory points (N x 3)

## Validation Utilities

### Joint Validation

#### validate_joint_positions()

Validate joint positions against limits.

```python
def validate_joint_positions(joints: np.ndarray,
                           joint_limits: Optional[np.ndarray] = None) -> bool
```

**Parameters:**
- `joints` (np.ndarray): Joint positions to validate
- `joint_limits` (Optional[np.ndarray]): Joint limits (7x2 array)

**Returns:**
- `bool`: True if joints are within limits

#### validate_joint_velocities()

Validate joint velocities against limits.

```python
def validate_joint_velocities(velocities: np.ndarray,
                             velocity_limits: Optional[np.ndarray] = None) -> bool
```

**Parameters:**
- `velocities` (np.ndarray): Joint velocities to validate
- `velocity_limits` (Optional[np.ndarray]): Velocity limits

**Returns:**
- `bool`: True if velocities are within limits

### Pose Validation

#### validate_pose()

Validate pose matrix.

```python
def validate_pose(pose: np.ndarray) -> bool
```

**Parameters:**
- `pose` (np.ndarray): 4x4 transformation matrix

**Returns:**
- `bool`: True if pose is valid

#### validate_workspace_position()

Validate if position is within workspace.

```python
def validate_workspace_position(position: np.ndarray,
                               workspace_bounds: Optional[dict] = None) -> bool
```

**Parameters:**
- `position` (np.ndarray): 3D position to validate
- `workspace_bounds` (Optional[dict]): Workspace boundary definition

**Returns:**
- `bool`: True if position is within workspace

### Safety Validation

#### check_collision_risk()

Check if motion poses collision risk.

```python
def check_collision_risk(current_pose: np.ndarray,
                        target_pose: np.ndarray,
                        obstacles: Optional[List[dict]] = None) -> bool
```

**Parameters:**
- `current_pose` (np.ndarray): Current end-effector pose
- `target_pose` (np.ndarray): Target end-effector pose
- `obstacles` (Optional[List[dict]]): List of obstacle definitions

**Returns:**
- `bool`: True if collision risk exists

#### validate_force_limits()

Validate force/torque values against safety limits.

```python
def validate_force_limits(forces: np.ndarray,
                         force_limits: Optional[np.ndarray] = None) -> bool
```

**Parameters:**
- `forces` (np.ndarray): Force/torque values [Fx, Fy, Fz, Tx, Ty, Tz]
- `force_limits` (Optional[np.ndarray]): Force/torque limits

**Returns:**
- `bool`: True if forces are within limits

## Conversion Utilities

### Unit Conversions

#### degrees_to_radians()

Convert degrees to radians.

```python
def degrees_to_radians(degrees: Union[float, np.ndarray]) -> Union[float, np.ndarray]
```

#### radians_to_degrees()

Convert radians to degrees.

```python
def radians_to_degrees(radians: Union[float, np.ndarray]) -> Union[float, np.ndarray]
```

### Coordinate System Conversions

#### robot_to_world()

Convert from robot coordinate system to world coordinates.

```python
def robot_to_world(robot_pose: np.ndarray,
                   world_transform: np.ndarray) -> np.ndarray
```

**Parameters:**
- `robot_pose` (np.ndarray): Pose in robot coordinates
- `world_transform` (np.ndarray): Robot-to-world transformation

**Returns:**
- `np.ndarray`: Pose in world coordinates

#### world_to_robot()

Convert from world coordinates to robot coordinate system.

```python
def world_to_robot(world_pose: np.ndarray,
                   world_transform: np.ndarray) -> np.ndarray
```

**Parameters:**
- `world_pose` (np.ndarray): Pose in world coordinates
- `world_transform` (np.ndarray): Robot-to-world transformation

**Returns:**
- `np.ndarray`: Pose in robot coordinates

## Data Processing Utilities

### Filtering

#### low_pass_filter()

Apply low-pass filter to data.

```python
def low_pass_filter(data: np.ndarray,
                    cutoff_frequency: float,
                    sampling_frequency: float,
                    order: int = 2) -> np.ndarray
```

**Parameters:**
- `data` (np.ndarray): Input data
- `cutoff_frequency` (float): Cutoff frequency in Hz
- `sampling_frequency` (float): Sampling frequency in Hz
- `order` (int): Filter order

**Returns:**
- `np.ndarray`: Filtered data

#### moving_average()

Apply moving average filter.

```python
def moving_average(data: np.ndarray,
                  window_size: int) -> np.ndarray
```

**Parameters:**
- `data` (np.ndarray): Input data
- `window_size` (int): Window size for averaging

**Returns:**
- `np.ndarray`: Filtered data

### Data Analysis

#### calculate_trajectory_metrics()

Calculate trajectory performance metrics.

```python
def calculate_trajectory_metrics(planned: np.ndarray,
                               actual: np.ndarray) -> dict
```

**Parameters:**
- `planned` (np.ndarray): Planned trajectory
- `actual` (np.ndarray): Actual trajectory

**Returns:**
- `dict`: Metrics including RMS error, max error, etc.

#### analyze_force_data()

Analyze force/torque data.

```python
def analyze_force_data(force_data: np.ndarray,
                      time_stamps: np.ndarray) -> dict
```

**Parameters:**
- `force_data` (np.ndarray): Force/torque measurements
- `time_stamps` (np.ndarray): Time stamps

**Returns:**
- `dict`: Analysis results including statistics and features

## Configuration Utilities

### Parameter Loading

#### load_robot_config()

Load robot configuration from file.

```python
def load_robot_config(config_file: str) -> dict
```

**Parameters:**
- `config_file` (str): Path to configuration file

**Returns:**
- `dict`: Robot configuration parameters

#### save_robot_config()

Save robot configuration to file.

```python
def save_robot_config(config: dict, config_file: str) -> None
```

**Parameters:**
- `config` (dict): Configuration parameters
- `config_file` (str): Path to save configuration

### Default Parameters

#### get_default_joint_limits()

Get default joint limits for Franka robot.

```python
def get_default_joint_limits() -> np.ndarray
```

**Returns:**
- `np.ndarray`: Joint limits (7x2 array)

#### get_default_velocity_limits()

Get default velocity limits.

```python
def get_default_velocity_limits() -> np.ndarray
```

**Returns:**
- `np.ndarray`: Velocity limits

#### get_default_force_limits()

Get default force/torque limits.

```python
def get_default_force_limits() -> np.ndarray
```

**Returns:**
- `np.ndarray`: Force/torque limits

## Logging Utilities

### Data Logging

#### RobotDataLogger

Class for logging robot data.

```python
class RobotDataLogger:
    def __init__(self, log_file: str, buffer_size: int = 1000)
```

**Parameters:**
- `log_file` (str): Path to log file
- `buffer_size` (int): Buffer size for data

#### Methods

##### log_state()

Log robot state.

```python
def log_state(self, state: RobotState, timestamp: Optional[float] = None) -> None
```

##### log_command()

Log robot command.

```python
def log_command(self, command: dict, timestamp: Optional[float] = None) -> None
```

##### save_log()

Save logged data to file.

```python
def save_log(self) -> None
```

##### load_log()

Load logged data from file.

```python
def load_log(self, log_file: str) -> dict
```

## Examples

### Basic Transformations

```python
import libfrankapy as fp
import numpy as np

# Create a pose from position and orientation
position = np.array([0.5, 0.0, 0.4])
quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # No rotation

# Convert to transformation matrix
pose_matrix = fp.utils.pose_to_matrix(position, quaternion, format='quaternion')
print(f"Pose matrix:\n{pose_matrix}")

# Convert back to position and quaternion
pos, quat = fp.utils.matrix_to_pose(pose_matrix, format='quaternion')
print(f"Position: {pos}")
print(f"Quaternion: {quat}")

# Convert quaternion to Euler angles
euler = fp.utils.quaternion_to_euler(quaternion)
print(f"Euler angles: {euler}")
```

### Trajectory Generation

```python
import libfrankapy as fp
import numpy as np
import matplotlib.pyplot as plt

# Generate joint trajectory
start_joints = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
end_joints = np.array([0.5, -0.5, 0.2, -2.0, 0.1, 1.8, 1.0])

trajectory = fp.utils.generate_joint_trajectory(
    start_joints, end_joints, 
    duration=5.0, 
    frequency=100.0, 
    profile='cubic'
)

print(f"Trajectory shape: {trajectory.shape}")

# Plot trajectory
time_points = np.linspace(0, 5.0, trajectory.shape[0])
plt.figure(figsize=(12, 8))
for i in range(7):
    plt.subplot(3, 3, i+1)
    plt.plot(time_points, trajectory[:, i])
    plt.title(f'Joint {i+1}')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (rad)')
plt.tight_layout()
plt.show()
```

### Circular Trajectory

```python
import libfrankapy as fp
import numpy as np

# Generate circular trajectory
center = np.array([0.5, 0.0, 0.4])
radius = 0.1
normal = np.array([0.0, 0.0, 1.0])  # Circle in XY plane

circle_points = fp.utils.generate_circular_trajectory(
    center, radius, normal, 
    start_angle=0.0, 
    end_angle=2*np.pi, 
    num_points=100
)

print(f"Circle trajectory shape: {circle_points.shape}")

# Convert to poses (assuming constant orientation)
orientation = np.array([1.0, 0.0, 0.0, 0.0])  # No rotation
poses = []

for point in circle_points:
    pose = fp.utils.pose_to_matrix(point, orientation, format='quaternion')
    poses.append(pose)

poses = np.array(poses)
print(f"Pose trajectory shape: {poses.shape}")
```

### Data Validation

```python
import libfrankapy as fp
import numpy as np

# Validate joint positions
test_joints = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])

if fp.utils.validate_joint_positions(test_joints):
    print("Joint positions are valid")
else:
    print("Joint positions exceed limits")

# Validate pose matrix
test_pose = np.eye(4)
test_pose[0:3, 3] = [0.5, 0.0, 0.4]

if fp.utils.validate_pose(test_pose):
    print("Pose is valid")
else:
    print("Invalid pose matrix")

# Check workspace position
test_position = np.array([0.8, 0.0, 0.2])

if fp.utils.validate_workspace_position(test_position):
    print("Position is within workspace")
else:
    print("Position is outside workspace")
```

### Data Logging

```python
import libfrankapy as fp
import time

# Create robot and logger
robot = fp.FrankaRobot("192.168.1.100")
logger = fp.utils.RobotDataLogger("robot_data.log")

try:
    robot.connect()
    robot.start_control()
    
    # Log data during operation
    for i in range(100):
        state = robot.get_state()
        logger.log_state(state)
        
        # Perform some operation
        time.sleep(0.01)
    
    # Save logged data
    logger.save_log()
    print("Data logged successfully")
    
finally:
    robot.stop_control()
    robot.disconnect()

# Load and analyze logged data
logged_data = logger.load_log("robot_data.log")
print(f"Logged {len(logged_data['states'])} states")

# Extract joint positions over time
joint_positions = []
for state_data in logged_data['states']:
    joint_positions.append(state_data['joint_positions'])

joint_positions = np.array(joint_positions)
print(f"Joint position data shape: {joint_positions.shape}")
```

### Force Data Analysis

```python
import libfrankapy as fp
import numpy as np
import matplotlib.pyplot as plt

# Simulate force data
time_stamps = np.linspace(0, 10, 1000)
force_data = np.zeros((1000, 6))

# Add some simulated force patterns
force_data[:, 2] = 5.0 + 2.0 * np.sin(2 * np.pi * 0.5 * time_stamps)  # Fz
force_data[:, 0] = 1.0 * np.random.normal(0, 0.1, 1000)  # Fx noise

# Analyze force data
analysis = fp.utils.analyze_force_data(force_data, time_stamps)

print(f"Force statistics:")
print(f"Mean force: {analysis['mean_force']}")
print(f"Max force: {analysis['max_force']}")
print(f"RMS force: {analysis['rms_force']}")

# Apply filtering
filtered_force = fp.utils.low_pass_filter(
    force_data, 
    cutoff_frequency=2.0, 
    sampling_frequency=100.0
)

# Plot results
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, force_data[:, 2], label='Raw Fz')
plt.plot(time_stamps, filtered_force[:, 2], label='Filtered Fz')
plt.legend()
plt.ylabel('Force (N)')
plt.title('Force Data Analysis')

plt.subplot(2, 1, 2)
plt.plot(time_stamps, force_data[:, 0], label='Raw Fx')
plt.plot(time_stamps, filtered_force[:, 0], label='Filtered Fx')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Force (N)')

plt.tight_layout()
plt.show()
```

### Configuration Management

```python
import libfrankapy as fp

# Load robot configuration
config = fp.utils.load_robot_config("robot_config.yaml")
print(f"Loaded configuration: {config}")

# Get default parameters
joint_limits = fp.utils.get_default_joint_limits()
velocity_limits = fp.utils.get_default_velocity_limits()
force_limits = fp.utils.get_default_force_limits()

print(f"Joint limits shape: {joint_limits.shape}")
print(f"Velocity limits: {velocity_limits}")
print(f"Force limits: {force_limits}")

# Create custom configuration
custom_config = {
    'robot_ip': '192.168.1.100',
    'control_frequency': 1000.0,
    'joint_limits': joint_limits.tolist(),
    'velocity_limits': velocity_limits.tolist(),
    'force_limits': force_limits.tolist(),
    'safety_settings': {
        'collision_threshold': 10.0,
        'workspace_bounds': {
            'x_min': 0.2, 'x_max': 0.8,
            'y_min': -0.4, 'y_max': 0.4,
            'z_min': 0.1, 'z_max': 0.8
        }
    }
}

# Save configuration
fp.utils.save_robot_config(custom_config, "custom_config.yaml")
print("Configuration saved")
```

## See Also

- [Robot API](/api/robot) - Main robot interface
- [Control API](/api/control) - Control system components
- [State API](/api/state) - Robot state representations
- [Examples](/examples) - Usage examples
