# Exceptions API

This module provides custom exception classes for error handling in libfrankapy.

## Exception Hierarchy

```
FrankaException
├── ConnectionException
├── ControlException
│   ├── MotionException
│   ├── ForceException
│   └── TrajectoryException
├── SafetyException
│   ├── CollisionException
│   ├── JointLimitException
│   └── WorkspaceLimitException
├── CommunicationException
└── ConfigurationException
```

## Base Exception Classes

### FrankaException

Base exception class for all libfrankapy errors.

```python
class FrankaException(Exception):
    def __init__(self, message: str, error_code: Optional[int] = None)
```

**Parameters:**
- `message` (str): Error description
- `error_code` (Optional[int]): Numeric error code

#### Attributes

- `message` (str): Error message
- `error_code` (Optional[int]): Numeric error code
- `timestamp` (float): Time when error occurred
- `recoverable` (bool): Whether error is recoverable

#### Methods

##### get_error_info()

Get detailed error information.

```python
def get_error_info(self) -> dict
```

**Returns:**
- `dict`: Error information including message, code, timestamp

##### is_recoverable()

Check if the error is recoverable.

```python
def is_recoverable(self) -> bool
```

**Returns:**
- `bool`: True if error can be recovered

## Connection Exceptions

### ConnectionException

Raised when robot connection fails.

```python
class ConnectionException(FrankaException):
    def __init__(self, message: str, robot_ip: str)
```

**Parameters:**
- `message` (str): Error description
- `robot_ip` (str): IP address of the robot

#### Attributes

- `robot_ip` (str): Robot IP address
- `connection_timeout` (float): Connection timeout value

#### Common Causes

- Robot is not reachable on the network
- Robot is already connected to another client
- Network configuration issues
- Robot is in error state

#### Example

```python
try:
    robot = fp.FrankaRobot("192.168.1.100")
    robot.connect()
except fp.ConnectionException as e:
    print(f"Failed to connect to robot at {e.robot_ip}: {e.message}")
    if e.error_code == 1001:  # Robot busy
        print("Robot is already connected to another client")
```

## Control Exceptions

### ControlException

Base class for control-related errors.

```python
class ControlException(FrankaException):
    def __init__(self, message: str, control_mode: Optional[str] = None)
```

**Parameters:**
- `message` (str): Error description
- `control_mode` (Optional[str]): Active control mode when error occurred

### MotionException

Raised when motion commands fail.

```python
class MotionException(ControlException):
    def __init__(self, message: str, target_position: Optional[np.ndarray] = None)
```

**Parameters:**
- `message` (str): Error description
- `target_position` (Optional[np.ndarray]): Target position that caused the error

#### Attributes

- `target_position` (Optional[np.ndarray]): Failed target position
- `current_position` (Optional[np.ndarray]): Position when error occurred

#### Common Causes

- Target position is unreachable
- Motion would violate joint limits
- Motion would cause collision
- Invalid motion parameters

#### Example

```python
try:
    target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
    robot.move_to_joint(target_joints)
except fp.MotionException as e:
    print(f"Motion failed: {e.message}")
    if e.target_position is not None:
        print(f"Failed target: {e.target_position}")
```

### ForceException

Raised when force control operations fail.

```python
class ForceException(ControlException):
    def __init__(self, message: str, applied_force: Optional[np.ndarray] = None)
```

**Parameters:**
- `message` (str): Error description
- `applied_force` (Optional[np.ndarray]): Force that caused the error

#### Attributes

- `applied_force` (Optional[np.ndarray]): Force/torque values
- `force_limit` (Optional[float]): Force limit that was exceeded

### TrajectoryException

Raised when trajectory execution fails.

```python
class TrajectoryException(ControlException):
    def __init__(self, message: str, waypoint_index: Optional[int] = None)
```

**Parameters:**
- `message` (str): Error description
- `waypoint_index` (Optional[int]): Index of problematic waypoint

#### Attributes

- `waypoint_index` (Optional[int]): Failed waypoint index
- `trajectory_progress` (float): Progress when error occurred (0.0 to 1.0)

## Safety Exceptions

### SafetyException

Base class for safety-related errors.

```python
class SafetyException(FrankaException):
    def __init__(self, message: str, safety_violation: str)
```

**Parameters:**
- `message` (str): Error description
- `safety_violation` (str): Type of safety violation

### CollisionException

Raised when collision is detected.

```python
class CollisionException(SafetyException):
    def __init__(self, message: str, collision_force: Optional[float] = None)
```

**Parameters:**
- `message` (str): Error description
- `collision_force` (Optional[float]): Magnitude of collision force

#### Attributes

- `collision_force` (Optional[float]): Force magnitude at collision
- `collision_joint` (Optional[int]): Joint where collision was detected
- `collision_direction` (Optional[np.ndarray]): Direction of collision force

#### Example

```python
try:
    robot.move_to_pose(target_pose)
except fp.CollisionException as e:
    print(f"Collision detected: {e.message}")
    print(f"Collision force: {e.collision_force}N")
    robot.recover_from_errors()
```

### JointLimitException

Raised when joint limits are violated.

```python
class JointLimitException(SafetyException):
    def __init__(self, message: str, joint_index: int, limit_type: str)
```

**Parameters:**
- `message` (str): Error description
- `joint_index` (int): Index of joint that violated limit
- `limit_type` (str): Type of limit (position, velocity, acceleration)

#### Attributes

- `joint_index` (int): Joint index (0-6)
- `limit_type` (str): Type of limit violation
- `current_value` (Optional[float]): Current joint value
- `limit_value` (Optional[float]): Limit that was exceeded

### WorkspaceLimitException

Raised when workspace limits are violated.

```python
class WorkspaceLimitException(SafetyException):
    def __init__(self, message: str, position: np.ndarray)
```

**Parameters:**
- `message` (str): Error description
- `position` (np.ndarray): Position that violated workspace

#### Attributes

- `position` (np.ndarray): End-effector position
- `workspace_bounds` (Optional[dict]): Workspace boundary definition

## Communication Exceptions

### CommunicationException

Raised when communication with robot fails.

```python
class CommunicationException(FrankaException):
    def __init__(self, message: str, communication_error: str)
```

**Parameters:**
- `message` (str): Error description
- `communication_error` (str): Type of communication error

#### Attributes

- `communication_error` (str): Error type
- `packet_loss` (Optional[float]): Packet loss percentage
- `latency` (Optional[float]): Communication latency

#### Common Causes

- Network connectivity issues
- High network latency
- Packet loss
- Robot firmware issues

## Configuration Exceptions

### ConfigurationException

Raised when configuration is invalid.

```python
class ConfigurationException(FrankaException):
    def __init__(self, message: str, parameter_name: str)
```

**Parameters:**
- `message` (str): Error description
- `parameter_name` (str): Name of invalid parameter

#### Attributes

- `parameter_name` (str): Invalid parameter name
- `parameter_value` (Optional[Any]): Invalid parameter value
- `valid_range` (Optional[tuple]): Valid parameter range

## Error Handling Utilities

### Error Recovery Functions

#### recover_from_error()

Attempt to recover from specific error types.

```python
def recover_from_error(robot: FrankaRobot, 
                      exception: FrankaException) -> bool
```

**Parameters:**
- `robot` (FrankaRobot): Robot instance
- `exception` (FrankaException): Exception to recover from

**Returns:**
- `bool`: True if recovery was successful

#### get_recovery_strategy()

Get recommended recovery strategy for an error.

```python
def get_recovery_strategy(exception: FrankaException) -> str
```

**Parameters:**
- `exception` (FrankaException): Exception to analyze

**Returns:**
- `str`: Recommended recovery strategy

### Error Logging

#### log_error()

Log error information for debugging.

```python
def log_error(exception: FrankaException, 
              context: Optional[dict] = None) -> None
```

**Parameters:**
- `exception` (FrankaException): Exception to log
- `context` (Optional[dict]): Additional context information

## Examples

### Comprehensive Error Handling

```python
import libfrankapy as fp
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_robot_operation(robot_ip: str):
    robot = fp.FrankaRobot(robot_ip)
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Connection phase
            logger.info(f"Attempting to connect (attempt {attempt + 1})")
            robot.connect()
            robot.start_control()
            
            # Control phase
            target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
            robot.move_to_joint(target_joints, speed_factor=0.1)
            
            logger.info("Operation completed successfully")
            return True
            
        except fp.ConnectionException as e:
            logger.error(f"Connection failed: {e.message}")
            if e.error_code == 1001:  # Robot busy
                logger.info("Waiting for robot to become available...")
                time.sleep(5.0)
            elif not e.is_recoverable():
                logger.error("Unrecoverable connection error")
                break
                
        except fp.CollisionException as e:
            logger.error(f"Collision detected: {e.message}")
            logger.info(f"Collision force: {e.collision_force}N")
            
            try:
                robot.recover_from_errors()
                logger.info("Recovered from collision")
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                break
                
        except fp.MotionException as e:
            logger.error(f"Motion failed: {e.message}")
            if e.target_position is not None:
                logger.info(f"Failed target: {e.target_position}")
            
            # Try with reduced speed
            try:
                robot.move_to_joint(target_joints, speed_factor=0.05)
                logger.info("Motion succeeded with reduced speed")
                return True
            except Exception:
                logger.error("Motion failed even with reduced speed")
                
        except fp.SafetyException as e:
            logger.error(f"Safety violation: {e.message}")
            logger.error(f"Safety violation type: {e.safety_violation}")
            
            if isinstance(e, fp.JointLimitException):
                logger.error(f"Joint {e.joint_index} {e.limit_type} limit exceeded")
            elif isinstance(e, fp.WorkspaceLimitException):
                logger.error(f"Workspace limit exceeded at position: {e.position}")
            
            # Safety violations usually require manual intervention
            break
            
        except fp.CommunicationException as e:
            logger.error(f"Communication error: {e.message}")
            if e.packet_loss and e.packet_loss > 0.1:
                logger.warning(f"High packet loss: {e.packet_loss*100:.1f}%")
            
            # Wait and retry for communication issues
            time.sleep(2.0)
            
        except fp.FrankaException as e:
            logger.error(f"General robot error: {e.message}")
            if e.error_code:
                logger.error(f"Error code: {e.error_code}")
            
            # Log error for debugging
            fp.log_error(e, {'attempt': attempt + 1, 'robot_ip': robot_ip})
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
            
        finally:
            try:
                robot.stop_control()
                robot.disconnect()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
    
    logger.error(f"Operation failed after {max_retries} attempts")
    return False

# Usage
if __name__ == "__main__":
    success = robust_robot_operation("192.168.1.100")
    if success:
        print("Robot operation completed successfully")
    else:
        print("Robot operation failed")
```

### Error-specific Recovery

```python
import libfrankapy as fp

def handle_specific_errors(robot: fp.FrankaRobot):
    try:
        # Some robot operation
        robot.move_to_joint([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
        
    except fp.CollisionException as e:
        print(f"Collision detected with force {e.collision_force}N")
        
        # Move away from collision
        current_joints = robot.get_joint_positions()
        safe_joints = current_joints.copy()
        safe_joints[e.collision_joint] -= 0.1  # Move joint away
        
        robot.recover_from_errors()
        robot.move_to_joint(safe_joints, speed_factor=0.05)
        
    except fp.JointLimitException as e:
        print(f"Joint {e.joint_index} {e.limit_type} limit exceeded")
        
        # Move to safe position
        safe_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        robot.move_to_joint(safe_joints, speed_factor=0.1)
        
    except fp.WorkspaceLimitException as e:
        print(f"Workspace limit exceeded at {e.position}")
        
        # Move to workspace center
        center_pose = np.eye(4)
        center_pose[0:3, 3] = [0.5, 0.0, 0.4]  # Safe position
        robot.move_to_pose(center_pose, speed_factor=0.1)
        
    except fp.CommunicationException as e:
        print(f"Communication error: {e.communication_error}")
        
        # Reconnect if communication is lost
        robot.disconnect()
        time.sleep(1.0)
        robot.connect()
        robot.start_control()
```

### Custom Exception Handler

```python
import libfrankapy as fp
from typing import Callable, Dict, Type

class RobotErrorHandler:
    def __init__(self):
        self.handlers: Dict[Type[fp.FrankaException], Callable] = {
            fp.ConnectionException: self._handle_connection_error,
            fp.CollisionException: self._handle_collision_error,
            fp.MotionException: self._handle_motion_error,
            fp.SafetyException: self._handle_safety_error,
        }
    
    def handle_error(self, robot: fp.FrankaRobot, error: fp.FrankaException) -> bool:
        """Handle robot error and return True if recovery was successful."""
        error_type = type(error)
        
        # Find the most specific handler
        for exception_type, handler in self.handlers.items():
            if isinstance(error, exception_type):
                return handler(robot, error)
        
        # Default handler
        return self._handle_generic_error(robot, error)
    
    def _handle_connection_error(self, robot: fp.FrankaRobot, 
                               error: fp.ConnectionException) -> bool:
        print(f"Handling connection error: {error.message}")
        
        if error.error_code == 1001:  # Robot busy
            print("Waiting for robot to become available...")
            time.sleep(5.0)
            try:
                robot.connect()
                return True
            except Exception:
                return False
        
        return False
    
    def _handle_collision_error(self, robot: fp.FrankaRobot, 
                              error: fp.CollisionException) -> bool:
        print(f"Handling collision: force = {error.collision_force}N")
        
        try:
            robot.recover_from_errors()
            # Move to safe position
            safe_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
            robot.move_to_joint(safe_joints, speed_factor=0.05)
            return True
        except Exception:
            return False
    
    def _handle_motion_error(self, robot: fp.FrankaRobot, 
                           error: fp.MotionException) -> bool:
        print(f"Handling motion error: {error.message}")
        
        # Try with reduced speed
        if error.target_position is not None:
            try:
                robot.move_to_joint(error.target_position, speed_factor=0.05)
                return True
            except Exception:
                return False
        
        return False
    
    def _handle_safety_error(self, robot: fp.FrankaRobot, 
                           error: fp.SafetyException) -> bool:
        print(f"Handling safety error: {error.safety_violation}")
        
        # Safety errors usually require manual intervention
        robot.stop()
        return False
    
    def _handle_generic_error(self, robot: fp.FrankaRobot, 
                            error: fp.FrankaException) -> bool:
        print(f"Handling generic error: {error.message}")
        
        if error.is_recoverable():
            try:
                robot.recover_from_errors()
                return True
            except Exception:
                return False
        
        return False

# Usage
error_handler = RobotErrorHandler()
robot = fp.FrankaRobot("192.168.1.100")

try:
    robot.connect()
    robot.start_control()
    # Robot operations...
    
except fp.FrankaException as e:
    success = error_handler.handle_error(robot, e)
    if success:
        print("Error handled successfully")
    else:
        print("Error handling failed")
        
finally:
    robot.stop_control()
    robot.disconnect()
```

## See Also

- [Robot API](/api/robot) - Main robot interface
- [State API](/api/state) - Robot state representations
- [Examples](/examples) - Usage examples with error handling
