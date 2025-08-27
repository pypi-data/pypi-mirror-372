#!/usr/bin/env python3
"""State monitoring example for libfrankapy.

This example demonstrates how to monitor robot state in real-time,
including joint positions, forces, and system status.
"""

import threading
import time
from typing import Optional

import numpy as np

import libfrankapy as fp


class RobotStateMonitor:
    """Real-time robot state monitor."""

    def __init__(self, robot: fp.FrankaRobot, update_rate: float = 10.0):
        """Initialize state monitor.

        Args:
            robot: FrankaRobot instance
            update_rate: Update frequency in Hz
        """
        self.robot = robot
        self.update_interval = 1.0 / update_rate
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # State history for analysis
        self.position_history = []
        self.force_history = []
        self.timestamp_history = []

        # Statistics
        self.max_force = 0.0
        self.max_velocity = 0.0
        self.total_distance = 0.0
        self.last_position = None

    def start_monitoring(self):
        """Start real-time monitoring."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("State monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("State monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Get current robot state
                state = self.robot.get_robot_state()

                # Update statistics
                self._update_statistics(state)

                # Print current state
                self._print_state(state)

                # Store history
                self._store_history(state)

                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.update_interval)

    def _update_statistics(self, state: fp.RobotState):
        """Update monitoring statistics."""
        # Calculate force magnitude
        if state.external_wrench:
            force_magnitude = np.linalg.norm(state.external_wrench.force)
            self.max_force = max(self.max_force, force_magnitude)

        # Calculate velocity magnitude
        velocity_magnitude = np.linalg.norm(state.joint_state.velocities)
        self.max_velocity = max(self.max_velocity, velocity_magnitude)

        # Calculate distance traveled
        current_position = np.array(state.cartesian_pose.position)
        if self.last_position is not None:
            distance = np.linalg.norm(current_position - self.last_position)
            self.total_distance += distance
        self.last_position = current_position

    def _print_state(self, state: fp.RobotState):
        """Print current robot state."""
        # Clear screen (works on most terminals)
        print("\033[2J\033[H", end="")

        print("=" * 60)
        print("           libfrankapy Real-time State Monitor")
        print("=" * 60)

        # Robot status
        print(f"Robot Mode: {state.robot_mode}")
        print(f"Control Frequency: {state.control_frequency: .1f} Hz")
        print(f"Moving: {'Yes' if self.robot.is_moving() else 'No'}")
        print(f"Error: {'Yes' if self.robot.has_error() else 'No'}")
        if self.robot.has_error():
            print(f"Error Code: {self.robot.get_error_code()}")

        print("\n--- Joint State ---")
        joint_pos = np.array(state.joint_state.positions)
        joint_vel = np.array(state.joint_state.velocities)
        joint_torques = np.array(state.joint_state.efforts)

        print(f"Positions (rad): {joint_pos: .3f}")
        print(f"Velocities (rad/s): {joint_vel: .3f}")
        print(f"Torques (Nm): {joint_torques: .3f}")

        print("\n--- Cartesian State ---")
        cart_pos = np.array(state.cartesian_pose.position)
        cart_ori = np.array(state.cartesian_pose.orientation)

        print(f"Position (m): {cart_pos: .4f}")
        print(f"Orientation (quat): {cart_ori: .4f}")

        # Convert quaternion to Euler angles for display
        try:
            from libfrankapy.utils import quaternion_to_euler

            roll, pitch, yaw = quaternion_to_euler(*cart_ori)
            euler_deg = np.degrees([roll, pitch, yaw])
            print(f"Orientation (deg): {euler_deg: .1f}")
        except Exception:  # nosec B110
            # Silently ignore conversion errors - quaternion display is optional
            pass

        print("\n--- External Forces ---")
        if state.external_wrench:
            ext_force = np.array(state.external_wrench.force)
            ext_torque = np.array(state.external_wrench.torque)
            force_magnitude = np.linalg.norm(ext_force)
            torque_magnitude = np.linalg.norm(ext_torque)

            print(f"Force (N): {ext_force: .2f}")
            print(f"Torque (Nm): {ext_torque: .2f}")
            print(f"Force Magnitude: {force_magnitude: .2f} N")
            print(f"Torque Magnitude: {torque_magnitude: .2f} Nm")
        else:
            print("No external wrench data")

        print("\n--- Statistics ---")
        print(f"Max Force: {self.max_force: .2f} N")
        print(f"Max Velocity: {self.max_velocity: .3f} rad/s")
        print(f"Total Distance: {self.total_distance: .4f} m")
        print(f"History Length: {len(self.position_history)}")

        print("\n--- Controls ---")
        print("Press Ctrl+C to stop monitoring")
        print("Press 'e' + Enter for emergency stop")

    def _store_history(self, state: fp.RobotState):
        """Store state history for analysis."""
        self.position_history.append(state.cartesian_pose.position.copy())
        if state.external_wrench:
            self.force_history.append(state.external_wrench.force.copy())
        self.timestamp_history.append(state.timestamp)

        # Limit history size
        max_history = 1000
        if len(self.position_history) > max_history:
            self.position_history.pop(0)
            if self.force_history:
                self.force_history.pop(0)
            self.timestamp_history.pop(0)

    def get_statistics(self):
        """Get monitoring statistics."""
        return {
            "max_force": self.max_force,
            "max_velocity": self.max_velocity,
            "total_distance": self.total_distance,
            "history_length": len(self.position_history),
        }

    def save_history(self, filename: str):
        """Save state history to file."""
        try:
            import json

            data = {
                "positions": self.position_history,
                "forces": self.force_history,
                "timestamps": self.timestamp_history,
                "statistics": self.get_statistics(),
            }

            with open(filename, "w") as f:
                json.dump(data, f, indent=2)

            print(f"History saved to {filename}")
        except Exception as e:
            print(f"Failed to save history: {e}")


def input_thread(monitor: RobotStateMonitor, robot: fp.FrankaRobot):
    """Handle user input in separate thread."""
    while monitor.monitoring:
        try:
            user_input = input().strip().lower()
            if user_input == "e":
                print("Emergency stop activated!")
                robot.emergency_stop()
                break
            elif user_input == "q":
                break
        except Exception:
            break


def setup_robot(robot_ip):
    """Setup and connect to robot."""
    print("libfrankapy State Monitoring Example")
    print(f"Connecting to robot at {robot_ip}...")

    robot = fp.FrankaRobot(robot_ip)

    if not robot.connect():
        print("Failed to connect to robot")
        return None

    if not robot.start_control():
        print("Failed to start control loop")
        return None

    print("Robot connected and ready for monitoring")
    return robot


def run_monitoring(robot):
    """Run the monitoring process."""
    monitor = RobotStateMonitor(robot, update_rate=10.0)
    monitor.start_monitoring()

    input_thread_handle = threading.Thread(target=input_thread, args=(monitor, robot))
    input_thread_handle.daemon = True
    input_thread_handle.start()

    try:
        while monitor.monitoring:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")

    monitor.stop_monitoring()
    return monitor


def print_final_stats(monitor):
    """Print final statistics and save history."""
    print("\n=== Final Statistics ===")
    stats = monitor.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    timestamp = int(time.time())
    filename = f"robot_state_history_{timestamp}.json"
    monitor.save_history(filename)
    print("\n=== Monitoring Example Completed ===")


def main():
    """Main example function."""
    robot_ip = "192.168.1.100"
    robot = None

    try:
        robot = setup_robot(robot_ip)
        if robot is None:
            return

        monitor = run_monitoring(robot)
        print_final_stats(monitor)

    except fp.ConnectionError as e:
        print(f"Connection error: {e}")
    except fp.ControlError as e:
        print(f"Control error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if robot is not None:
            print("Disconnecting from robot...")
            robot.disconnect()
            print("Disconnected")


if __name__ == "__main__":
    main()
