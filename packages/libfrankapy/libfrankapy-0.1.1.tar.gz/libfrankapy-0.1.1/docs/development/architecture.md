# Architecture Overview

libfrankapy is designed as a high-performance Python interface for Franka Emika robots, combining the ease of Python with the real-time capabilities of C++.

## Design Principles

### Real-time Performance

- Critical control loops implemented in C++
- Python bindings for high-level interface
- Minimal latency for robot communication
- Deterministic timing for safety-critical operations

### Safety First

- Multiple layers of safety checks
- Graceful error handling and recovery
- Emergency stop capabilities
- Workspace and force limiting

### Modular Design

- Loosely coupled components
- Plugin architecture for extensions
- Clear separation of concerns
- Easy to test and maintain

## System Architecture

### Overall Structure

```
┌─────────────────────────────────────────┐
│              Python Layer              │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Robot     │  │    Control      │   │
│  │  Interface  │  │   Algorithms    │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
                     │
                PyBind11 Bindings
                     │
┌─────────────────────────────────────────┐
│               C++ Layer                │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  Real-time  │  │   libfranka     │   │
│  │  Control    │  │  Communication  │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
                     │
                Network (FCI)
                     │
┌─────────────────────────────────────────┐
│            Franka Robot                │
└─────────────────────────────────────────┘
```

## Core Components

### Python Layer

**Robot Interface** (`libfrankapy.robot`)

- High-level robot control API
- State monitoring and logging
- Configuration management
- Error handling and recovery

**Control Algorithms** (`libfrankapy.control`)

- Joint space controllers
- Cartesian space controllers
- Force/impedance controllers
- Trajectory generation and execution

**State Management** (`libfrankapy.state`)

- Robot state representation
- State monitoring and callbacks
- Data logging and analysis
- State interpolation and prediction

### C++ Layer

**Real-time Control** (`src/control/`)

- Low-latency control loops
- Safety monitoring
- Motion generation
- Force control algorithms

**Communication** (`src/communication/`)

- libfranka interface
- Network protocol handling
- Error detection and reporting
- State synchronization

## Data Flow

### Control Commands

1. Python user code calls high-level API
2. Commands validated and preprocessed
3. Passed to C++ layer via PyBind11
4. C++ layer executes real-time control
5. Commands sent to robot via libfranka

### State Updates

1. Robot state received via libfranka
2. C++ layer processes and validates state
3. State passed to Python layer
4. Python callbacks and monitoring triggered
5. State logged and analyzed

## Thread Architecture

### Main Threads

**Control Thread** (C++, Real-time)

- 1kHz control loop
- Highest priority
- Minimal allocations
- Direct robot communication

**State Thread** (C++, High priority)

- State monitoring and validation
- Safety checks
- Error detection
- State broadcasting

**Python Thread** (Python, Normal priority)

- User code execution
- High-level planning
- Data analysis
- Visualization

**Logging Thread** (C++, Low priority)

- Data recording
- File I/O
- Network logging
- Performance monitoring

## Memory Management

### Real-time Constraints

- Pre-allocated buffers for control loops
- Lock-free data structures where possible
- Minimal dynamic allocation in real-time paths
- Memory pools for frequent allocations

### Python Integration

- Efficient data copying between Python and C++
- NumPy array integration
- Reference counting for shared data
- Garbage collection considerations

## Error Handling

### Error Propagation

1. Hardware errors detected by libfranka
2. C++ layer catches and categorizes errors
3. Safety actions triggered immediately
4. Errors propagated to Python layer
5. User-defined error handlers called
6. Recovery procedures executed

### Safety Mechanisms

- Joint limit monitoring
- Cartesian workspace limits
- Force/torque limits
- Velocity and acceleration limits
- Emergency stop capabilities
- Automatic error recovery

## Extensibility

### Plugin Architecture

- Custom controllers can be added
- Plugin discovery and loading
- Configuration-based activation
- Runtime plugin management

### Custom Algorithms

- User-defined control algorithms
- Custom state estimators
- Application-specific safety checks
- Domain-specific trajectory generators

## Performance Considerations

### Latency Optimization

- Minimal layers between user code and robot
- Efficient serialization/deserialization
- Optimized memory access patterns
- Cache-friendly data structures

### Throughput Optimization

- Batch processing where possible
- Vectorized operations
- Parallel processing for non-real-time tasks
- Efficient logging and data storage

## Testing Architecture

### Test Levels

**Unit Tests**

- Individual component testing
- Mock robot interfaces
- Isolated algorithm testing
- Performance benchmarks

**Integration Tests**

- Component interaction testing
- End-to-end data flow
- Error handling scenarios
- Configuration validation

**System Tests**

- Full system testing with robot
- Real-world scenarios
- Performance validation
- Safety system testing

## Future Enhancements

### Planned Features

- Multi-robot coordination
- Advanced trajectory optimization
- Machine learning integration
- Cloud connectivity
- Enhanced visualization tools
- Mobile robot support

### Architecture Evolution

- Microservice architecture
- Distributed computing support
- Real-time networking
- Edge computing integration

## Component Details

### Control System Components

#### Motion Generators

```cpp
class MotionGenerator {
public:
    virtual franka::MotionGeneratorCommand operator()(
        const franka::RobotState& robot_state,
        franka::Duration period
    ) = 0;
    
    virtual bool is_finished() const = 0;
};
```

#### Force Controllers

```cpp
class ForceController {
public:
    virtual franka::TorqueCommand operator()(
        const franka::RobotState& robot_state,
        franka::Duration period
    ) = 0;
    
    virtual void set_target_force(const Eigen::Vector6d& force) = 0;
};
```

### State Management

#### State Representation

```python
class RobotState:
    def __init__(self):
        self.joint_positions: np.ndarray
        self.joint_velocities: np.ndarray
        self.cartesian_pose: np.ndarray
        self.cartesian_velocity: np.ndarray
        self.external_forces: np.ndarray
        self.timestamp: float
```

#### State Callbacks

```python
class StateCallback:
    def on_state_update(self, state: RobotState) -> None:
        pass
    
    def on_error(self, error: Exception) -> None:
        pass
```

### Communication Layer

#### Network Protocol

- UDP-based communication with robot
- 1kHz update rate
- Packet loss detection and recovery
- Latency monitoring

#### Message Types

```cpp
enum class MessageType {
    JOINT_COMMAND,
    CARTESIAN_COMMAND,
    FORCE_COMMAND,
    STATE_UPDATE,
    ERROR_REPORT,
    CONFIGURATION
};
```

### Safety System

#### Safety Monitors

```cpp
class SafetyMonitor {
public:
    virtual bool check_safety(const franka::RobotState& state) = 0;
    virtual void on_violation(const SafetyViolation& violation) = 0;
};
```

#### Emergency Stop

```cpp
class EmergencyStop {
public:
    void trigger(const std::string& reason);
    bool is_active() const;
    void reset();
};
```

## Configuration Management

### Configuration Files

```yaml
# robot_config.yaml
robot:
  ip_address: "192.168.1.100"
  control_frequency: 1000.0
  
safety:
  joint_limits:
    position: [[-2.8973, 2.8973], ...]
    velocity: [-2.1750, 2.1750]
  
  workspace_limits:
    x: [0.2, 0.8]
    y: [-0.4, 0.4]
    z: [0.1, 0.8]
    
control:
  default_speed_factor: 0.1
  trajectory_interpolation: "cubic"
  force_control_gains:
    kp: [100, 100, 100, 10, 10, 10]
    kd: [10, 10, 10, 1, 1, 1]
```

### Runtime Configuration

```python
import libfrankapy as fp

# Load configuration
config = fp.load_config("robot_config.yaml")

# Create robot with configuration
robot = fp.FrankaRobot(config)

# Override specific settings
robot.set_speed_factor(0.05)
robot.set_force_control_gains(kp=[150, 150, 150, 15, 15, 15])
```

## Debugging and Diagnostics

### Logging System

```python
import logging
import libfrankapy as fp

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('libfrankapy')

# Enable detailed logging
fp.set_log_level(fp.LogLevel.DEBUG)
fp.enable_performance_logging(True)
```

### Performance Monitoring

```python
# Monitor control loop timing
stats = robot.get_performance_stats()
print(f"Average control latency: {stats.avg_latency_ms:.2f}ms")
print(f"Max control latency: {stats.max_latency_ms:.2f}ms")
print(f"Packet loss rate: {stats.packet_loss_rate:.2%}")
```

### Error Diagnostics

```python
# Get detailed error information
try:
    robot.move_to_joint(target_joints)
except fp.FrankaException as e:
    error_info = e.get_diagnostic_info()
    print(f"Error code: {error_info.code}")
    print(f"Error message: {error_info.message}")
    print(f"Stack trace: {error_info.stack_trace}")
    print(f"Robot state at error: {error_info.robot_state}")
```

## See Also

- [Contributing Guide](/development/contributing) - How to contribute to the project
- [Testing Guide](/development/testing) - Testing procedures and guidelines
- [API Reference](/api/) - Detailed API documentation
- [Examples](/examples) - Usage examples and tutorials
