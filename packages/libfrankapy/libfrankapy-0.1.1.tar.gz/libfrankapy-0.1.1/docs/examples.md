# Examples

This section provides comprehensive examples demonstrating various features of libfrankapy.

## Basic Control Examples

### Simple Joint Movement

```python
import libfrankapy as fp
import time

def simple_joint_movement():
    robot = fp.FrankaRobot("192.168.1.100")
    
    try:
        robot.connect()
        robot.start_control()
        
        # Define some joint positions
        positions = [
            [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],  # Home
            [0.5, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],  # Move joint 1
            [0.0, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],  # Move joint 2
            [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],  # Back to home
        ]
        
        for i, pos in enumerate(positions):
            print(f"Moving to position {i+1}...")
            robot.move_to_joint(pos, speed_factor=0.2)
            time.sleep(1.0)
            
    finally:
        robot.stop_control()
        robot.disconnect()

if __name__ == "__main__":
    simple_joint_movement()
```

### Cartesian Space Control

```python
import libfrankapy as fp
import numpy as np

def cartesian_movement():
    robot = fp.FrankaRobot("192.168.1.100")
    
    try:
        robot.connect()
        robot.start_control()
        
        # Get current pose
        current_pose = robot.get_robot_state().cartesian_state.pose
        print(f"Current pose:\n{current_pose}")
        
        # Create a square trajectory in XY plane
        square_size = 0.1  # 10cm square
        
        waypoints = [
            current_pose,  # Start position
        ]
        
        # Generate square waypoints
        for dx, dy in [(square_size, 0), (0, square_size), (-square_size, 0), (0, -square_size)]:
            new_pose = waypoints[-1].copy()
            new_pose[0, 3] += dx  # X translation
            new_pose[1, 3] += dy  # Y translation
            waypoints.append(new_pose)
        
        # Execute square trajectory
        for i, pose in enumerate(waypoints[1:]):
            print(f"Moving to waypoint {i+1}...")
            robot.move_to_pose(pose, speed_factor=0.1)
            
    finally:
        robot.stop_control()
        robot.disconnect()

if __name__ == "__main__":
    cartesian_movement()
```

## Advanced Examples

### Force Control

```python
import libfrankapy as fp
import numpy as np
import time

def force_control_example():
    robot = fp.FrankaRobot("192.168.1.100")
    
    try:
        robot.connect()
        robot.start_control()
        
        # Set up force control parameters
        force_threshold = 10.0  # Newtons
        contact_force = np.array([0, 0, -5.0, 0, 0, 0])  # 5N downward force
        
        # Start force control mode
        robot.start_force_control()
        
        # Monitor forces and react
        start_time = time.time()
        while time.time() - start_time < 10.0:  # Run for 10 seconds
            state = robot.get_robot_state()
            current_forces = state.cartesian_state.forces
            
            # Check if contact is detected
            if np.linalg.norm(current_forces[:3]) > force_threshold:
                print(f"Contact detected! Forces: {current_forces[:3]}")
                # Apply controlled contact force
                robot.set_cartesian_force(contact_force)
            else:
                # No contact, maintain position
                robot.set_cartesian_force(np.zeros(6))
            
            time.sleep(0.01)  # 100Hz control loop
        
        # Stop force control
        robot.stop_force_control()
        
    finally:
        robot.stop_control()
        robot.disconnect()

if __name__ == "__main__":
    force_control_example()
```

### Trajectory Following

```python
import libfrankapy as fp
import numpy as np
import matplotlib.pyplot as plt
import time

def trajectory_following():
    robot = fp.FrankaRobot("192.168.1.100")
    
    try:
        robot.connect()
        robot.start_control()
        
        # Generate a smooth trajectory
        duration = 5.0  # seconds
        frequency = 0.5  # Hz
        amplitude = 0.1  # meters
        
        # Time points
        dt = 0.01
        t = np.arange(0, duration, dt)
        
        # Get starting position
        start_pose = robot.get_robot_state().cartesian_state.pose
        
        # Generate sinusoidal trajectory in Y direction
        y_trajectory = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Execute trajectory
        positions = []
        for i, y_offset in enumerate(y_trajectory):
            target_pose = start_pose.copy()
            target_pose[1, 3] += y_offset
            
            robot.set_cartesian_pose(target_pose)
            
            # Record actual position
            actual_pose = robot.get_robot_state().cartesian_state.pose
            positions.append(actual_pose[1, 3] - start_pose[1, 3])
            
            time.sleep(dt)
        
        # Plot results
        plt.figure(figsize=(10, 6))
        plt.plot(t, y_trajectory, label='Desired', linewidth=2)
        plt.plot(t, positions, label='Actual', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Y Position (m)')
        plt.title('Trajectory Following Performance')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    finally:
        robot.stop_control()
        robot.disconnect()

if __name__ == "__main__":
    trajectory_following()
```

### Real-time State Monitoring

```python
import libfrankapy as fp
import numpy as np
import time
import threading

class RobotMonitor:
    def __init__(self, robot_ip):
        self.robot = fp.FrankaRobot(robot_ip)
        self.monitoring = False
        self.data = {
            'timestamps': [],
            'joint_positions': [],
            'cartesian_pose': [],
            'forces': []
        }
    
    def start_monitoring(self):
        self.robot.connect()
        self.robot.start_control()
        self.monitoring = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.robot.stop_control()
        self.robot.disconnect()
    
    def _monitor_loop(self):
        while self.monitoring:
            try:
                state = self.robot.get_robot_state()
                timestamp = time.time()
                
                self.data['timestamps'].append(timestamp)
                self.data['joint_positions'].append(state.joint_state.positions.copy())
                self.data['cartesian_pose'].append(state.cartesian_state.pose.copy())
                self.data['forces'].append(state.cartesian_state.forces.copy())
                
                # Print current state
                print(f"Time: {timestamp:.2f}, "
                      f"Joint 1: {state.joint_state.positions[0]:.3f}, "
                      f"Force Z: {state.cartesian_state.forces[2]:.2f}")
                
                time.sleep(0.01)  # 100Hz monitoring
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break

def monitoring_example():
    monitor = RobotMonitor("192.168.1.100")
    
    try:
        monitor.start_monitoring()
        
        # Let it monitor for 10 seconds
        time.sleep(10.0)
        
    finally:
        monitor.stop_monitoring()
        
        # Print summary
        print(f"Collected {len(monitor.data['timestamps'])} data points")
        if monitor.data['timestamps']:
            duration = monitor.data['timestamps'][-1] - monitor.data['timestamps'][0]
            print(f"Monitoring duration: {duration:.2f} seconds")
            print(f"Average sampling rate: {len(monitor.data['timestamps'])/duration:.1f} Hz")

if __name__ == "__main__":
    monitoring_example()
```

## Error Handling Examples

### Robust Robot Control

```python
import libfrankapy as fp
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_robot_control():
    robot = fp.FrankaRobot("192.168.1.100")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connection attempt {attempt + 1}")
            robot.connect()
            robot.start_control()
            
            # Your robot control code here
            target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
            robot.move_to_joint(target_joints, speed_factor=0.1)
            
            logger.info("Robot control completed successfully")
            break
            
        except fp.FrankaException as e:
            logger.error(f"Robot error on attempt {attempt + 1}: {e}")
            
            try:
                robot.recover_from_errors()
                logger.info("Error recovery attempted")
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
            
            if attempt == max_retries - 1:
                logger.error("Max retries reached, giving up")
                raise
            
            time.sleep(2.0)  # Wait before retry
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
            
        finally:
            try:
                robot.stop_control()
                robot.disconnect()
                logger.info("Robot disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

if __name__ == "__main__":
    robust_robot_control()
```

These examples demonstrate the key features and best practices for using libfrankapy. Always remember to:

- Use proper error handling
- Disconnect the robot properly
- Start with low speed factors for safety
- Monitor robot state during operation
- Implement emergency stop procedures
