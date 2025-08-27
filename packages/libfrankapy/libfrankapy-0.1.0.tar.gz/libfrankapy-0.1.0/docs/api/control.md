# Control API

This module provides control algorithms and utilities for robot motion control.

## Control Classes

### MotionGenerator

Base class for motion generation algorithms.

```python
class MotionGenerator:
    def __init__(self, control_frequency: float = 1000.0)
```

#### Methods

##### generate_motion()

Generate motion commands for the current control cycle.

```python
def generate_motion(self, current_state: RobotState) -> MotionCommand
```

**Parameters:**
- `current_state` (RobotState): Current robot state

**Returns:**
- `MotionCommand`: Motion command for this control cycle

### JointMotionGenerator

Generates smooth joint space motions.

```python
class JointMotionGenerator(MotionGenerator):
    def __init__(self, 
                 target_positions: List[float],
                 max_velocity: float = 1.0,
                 max_acceleration: float = 1.0)
```

**Parameters:**
- `target_positions` (List[float]): Target joint positions
- `max_velocity` (float): Maximum joint velocity
- `max_acceleration` (float): Maximum joint acceleration

### CartesianMotionGenerator

Generates smooth Cartesian space motions.

```python
class CartesianMotionGenerator(MotionGenerator):
    def __init__(self,
                 target_pose: np.ndarray,
                 max_velocity: float = 0.1,
                 max_acceleration: float = 0.1)
```

**Parameters:**
- `target_pose` (np.ndarray): Target end-effector pose (4x4 matrix)
- `max_velocity` (float): Maximum Cartesian velocity
- `max_acceleration` (float): Maximum Cartesian acceleration

### ForceController

Implements force/impedance control algorithms.

```python
class ForceController:
    def __init__(self,
                 stiffness: np.ndarray,
                 damping: np.ndarray)
```

**Parameters:**
- `stiffness` (np.ndarray): 6x6 stiffness matrix
- `damping` (np.ndarray): 6x6 damping matrix

#### Methods

##### compute_control_force()

Compute control forces based on desired and actual states.

```python
def compute_control_force(self,
                         desired_pose: np.ndarray,
                         current_pose: np.ndarray,
                         desired_velocity: np.ndarray,
                         current_velocity: np.ndarray) -> np.ndarray
```

**Returns:**
- `np.ndarray`: 6-element force/torque vector

## Trajectory Planning

### TrajectoryPlanner

Plans smooth trajectories between waypoints.

```python
class TrajectoryPlanner:
    def __init__(self, max_velocity: float, max_acceleration: float)
```

#### Methods

##### plan_joint_trajectory()

Plan a joint space trajectory.

```python
def plan_joint_trajectory(self,
                         waypoints: List[List[float]],
                         duration: float) -> JointTrajectory
```

**Parameters:**
- `waypoints` (List[List[float]]): List of joint position waypoints
- `duration` (float): Total trajectory duration

**Returns:**
- `JointTrajectory`: Planned trajectory object

##### plan_cartesian_trajectory()

Plan a Cartesian space trajectory.

```python
def plan_cartesian_trajectory(self,
                             waypoints: List[np.ndarray],
                             duration: float) -> CartesianTrajectory
```

**Parameters:**
- `waypoints` (List[np.ndarray]): List of pose waypoints
- `duration` (float): Total trajectory duration

**Returns:**
- `CartesianTrajectory`: Planned trajectory object

## Control Utilities

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
- `t` (float): Interpolation parameter (0.0 to 1.0)

**Returns:**
- `np.ndarray`: Interpolated point

#### cubic_interpolation()

Perform cubic spline interpolation.

```python
def cubic_interpolation(waypoints: List[np.ndarray],
                       t: float) -> np.ndarray
```

**Parameters:**
- `waypoints` (List[np.ndarray]): Control points
- `t` (float): Interpolation parameter

**Returns:**
- `np.ndarray`: Interpolated point

### Safety Functions

#### check_joint_limits()

Check if joint positions are within limits.

```python
def check_joint_limits(positions: np.ndarray,
                      lower_limits: np.ndarray,
                      upper_limits: np.ndarray) -> bool
```

**Returns:**
- `bool`: True if all joints are within limits

#### check_velocity_limits()

Check if joint velocities are within limits.

```python
def check_velocity_limits(velocities: np.ndarray,
                         max_velocities: np.ndarray) -> bool
```

**Returns:**
- `bool`: True if all velocities are within limits

#### check_workspace_limits()

Check if end-effector is within workspace limits.

```python
def check_workspace_limits(pose: np.ndarray,
                          workspace_limits: dict) -> bool
```

**Parameters:**
- `pose` (np.ndarray): End-effector pose
- `workspace_limits` (dict): Workspace boundary definition

**Returns:**
- `bool`: True if pose is within workspace

## Examples

### Custom Motion Generator

```python
import libfrankapy as fp
import numpy as np

class SinusoidalMotionGenerator(fp.MotionGenerator):
    def __init__(self, amplitude: float, frequency: float):
        super().__init__()
        self.amplitude = amplitude
        self.frequency = frequency
        self.start_time = None
        self.start_position = None
    
    def generate_motion(self, current_state):
        if self.start_time is None:
            self.start_time = current_state.timestamp
            self.start_position = current_state.joint_state.positions.copy()
        
        t = current_state.timestamp - self.start_time
        offset = self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        
        target_positions = self.start_position.copy()
        target_positions[0] += offset  # Move first joint
        
        return fp.MotionCommand(joint_positions=target_positions)

# Usage
robot = fp.FrankaRobot("192.168.1.100")
motion_gen = SinusoidalMotionGenerator(amplitude=0.1, frequency=0.5)

try:
    robot.connect()
    robot.start_control()
    robot.set_motion_generator(motion_gen)
    
    # Run for 10 seconds
    time.sleep(10.0)
    
finally:
    robot.stop_control()
    robot.disconnect()
```

### Force Control with Compliance

```python
import libfrankapy as fp
import numpy as np

# Create force controller with compliance
stiffness = np.diag([1000, 1000, 500, 100, 100, 100])  # Lower Z stiffness
damping = np.diag([50, 50, 25, 5, 5, 5])

force_controller = fp.ForceController(stiffness, damping)

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Get initial pose
    initial_pose = robot.get_cartesian_pose()
    
    # Desired pose (10cm lower)
    desired_pose = initial_pose.copy()
    desired_pose[2, 3] -= 0.1
    
    # Control loop
    for _ in range(1000):  # 1 second at 1kHz
        current_state = robot.get_robot_state()
        current_pose = current_state.cartesian_state.pose
        current_velocity = current_state.cartesian_state.velocity
        
        # Compute control force
        control_force = force_controller.compute_control_force(
            desired_pose, current_pose,
            np.zeros(6), current_velocity
        )
        
        robot.set_cartesian_force(control_force)
        time.sleep(0.001)  # 1ms
        
finally:
    robot.stop_control()
    robot.disconnect()
```

### Trajectory Planning and Execution

```python
import libfrankapy as fp
import numpy as np

# Create trajectory planner
planner = fp.TrajectoryPlanner(max_velocity=1.0, max_acceleration=0.5)

# Define waypoints
waypoints = [
    [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
    [0.5, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
    [0.5, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],
    [0.0, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],
    [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
]

# Plan trajectory
trajectory = planner.plan_joint_trajectory(waypoints, duration=8.0)

robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    
    # Execute planned trajectory
    robot.execute_trajectory(trajectory)
    
finally:
    robot.stop_control()
    robot.disconnect()
```

## See Also

- [Robot API](/api/robot) - Main robot interface
- [State API](/api/state) - Robot state representations
- [Examples](/examples) - Usage examples
