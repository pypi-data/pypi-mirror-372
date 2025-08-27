# API Reference

This section provides detailed documentation for all libfrankapy classes and functions.

## Core Classes

### [Robot](/api/robot)
The main robot interface class for controlling Franka robots.

### [Control](/api/control)
Control-related classes and functions for robot motion control.

### [State](/api/state)
Classes for representing robot state information.

### [Exceptions](/api/exceptions)
Custom exception classes for error handling.

## Quick Reference

### Basic Usage

```python
import libfrankapy as fp

# Create robot instance
robot = fp.FrankaRobot("192.168.1.100")

# Connect and control
robot.connect()
robot.start_control()

# Get robot state
state = robot.get_robot_state()

# Move robot
target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
robot.move_to_joint(target_joints, speed_factor=0.1)

# Cleanup
robot.stop_control()
robot.disconnect()
```

### Common Patterns

#### Safe Robot Operation

```python
try:
    robot.connect()
    robot.start_control()
    # Your robot code here
except fp.FrankaException as e:
    print(f"Robot error: {e}")
    robot.recover_from_errors()
finally:
    robot.stop_control()
    robot.disconnect()
```

#### State Monitoring

```python
state = robot.get_robot_state()
print(f"Joint positions: {state.joint_state.positions}")
print(f"End-effector pose: {state.cartesian_state.pose}")
print(f"Forces: {state.cartesian_state.forces}")
```

## Module Structure

```
libfrankapy/
├── robot.py          # Main robot interface
├── control.py        # Control algorithms
├── state.py          # State representations
├── exceptions.py     # Custom exceptions
└── utils.py          # Utility functions
```

## Type Hints

libfrankapy provides comprehensive type hints for better IDE support and code safety:

```python
from typing import List, Optional
import numpy as np

def move_robot(robot: fp.FrankaRobot, 
               positions: List[float], 
               speed: float = 0.1) -> bool:
    """Move robot to specified joint positions."""
    return robot.move_to_joint(positions, speed_factor=speed)
```

## Error Handling

All libfrankapy functions can raise `FrankaException` or its subclasses. Always use proper error handling:

```python
try:
    robot.move_to_joint(target_positions)
except fp.FrankaException as e:
    print(f"Robot error: {e}")
    # Handle robot-specific errors
except Exception as e:
    print(f"General error: {e}")
    # Handle other errors
```

## Performance Considerations

- The C++ control loop runs at 1kHz for real-time performance
- Python code should not be used in time-critical control loops
- Use shared memory for efficient data exchange
- Monitor system resources when running long operations

## Thread Safety

libfrankapy is designed to be thread-safe for most operations. However:

- Only one control thread should be active at a time
- State queries can be performed from multiple threads
- Use proper synchronization for shared data

## Next Steps

- [Robot API](/api/robot) - Detailed robot interface documentation
- [Control API](/api/control) - Control algorithms and functions
- [State API](/api/state) - Robot state representations
- [Exceptions API](/api/exceptions) - Error handling classes
