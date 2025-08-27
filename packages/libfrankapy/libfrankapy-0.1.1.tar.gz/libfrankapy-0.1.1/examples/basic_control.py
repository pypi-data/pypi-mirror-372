#!/usr/bin/env python3
"""Basic control example for libfrankapy.

This example demonstrates basic robot connection, state reading,
and simple motion commands.
"""

import time

import numpy as np

import libfrankapy as fp


def connect_robot(robot_ip):
    """Connect to the robot and start control loop."""
    print("libfrankapy Basic Control Example")
    print(f"Connecting to robot at {robot_ip}...")

    robot = fp.FrankaRobot(robot_ip)

    if not robot.connect():
        print("Failed to connect to robot")
        return None

    print("Successfully connected to robot")

    if not robot.start_control():
        print("Failed to start control loop")
        return None

    print("Control loop started")
    return robot


def print_robot_state(robot):
    """Print current robot state information."""
    print("\n=== Initial Robot State ===")
    state = robot.get_robot_state()
    print(f"Robot mode: {state.robot_mode}")
    print(f"Control frequency: {state.control_frequency: .1f} Hz")
    print(f"Joint positions: {np.array(state.joint_state.positions): .3f}")
    print(f"End-effector position: {np.array(state.cartesian_pose.position): .3f}")

    if robot.has_error():
        print(f"Robot has error (code: {robot.get_error_code()})")
        return False
    return True


def perform_joint_motion(robot):
    """Perform joint space motion example."""
    print("\n=== Joint Space Motion ===")
    target_joints = [0.0, -0.3, 0.0, -2.2, 0.0, 1.9, 0.785]

    print(f"Moving to joint configuration: {np.array(target_joints): .3f}")
    robot.move_to_joint(target_joints, speed_factor=0.1)
    print("Joint motion completed")

    current_state = robot.get_joint_state()
    print(f"Current joint positions: {np.array(current_state.positions): .3f}")
    time.sleep(1.0)


def perform_cartesian_motion(robot):
    """Perform Cartesian space motion example."""
    print("\n=== Cartesian Space Motion ===")
    current_pose = robot.get_cartesian_pose()
    print(f"Current position: {np.array(current_pose.position): .3f}")
    print(f"Current orientation: {np.array(current_pose.orientation): .3f}")

    target_position = current_pose.position.copy()
    target_position[2] += 0.1  # Move up 10cm
    target_pose = target_position + current_pose.orientation

    print(f"Moving to position: {np.array(target_position): .3f}")
    robot.move_to_pose(target_pose, speed_factor=0.1)
    print("Cartesian motion completed")

    final_pose = robot.get_cartesian_pose()
    print(f"Final position: {np.array(final_pose.position): .3f}")
    time.sleep(1.0)


def run_example(robot):
    """Run the main example sequence."""
    if not print_robot_state(robot):
        return

    print("\n=== Moving to Home Position ===")
    robot.move_to_home(speed_factor=0.1)
    print("Moved to home position")
    time.sleep(1.0)

    perform_joint_motion(robot)
    perform_cartesian_motion(robot)

    print("\n=== Returning to Home ===")
    robot.move_to_home(speed_factor=0.1)
    print("Returned to home position")

    print("\n=== Example Completed Successfully ===")


def handle_exceptions(robot):
    """Handle cleanup in case of exceptions."""
    if robot is not None:
        robot.emergency_stop()


def main():
    """Main example function."""
    robot_ip = "192.168.1.100"
    robot = None

    try:
        robot = connect_robot(robot_ip)
        if robot is None:
            return

        run_example(robot)

    except fp.ConnectionError as e:
        print(f"Connection error: {e}")
    except fp.ControlError as e:
        print(f"Control error: {e}")
    except fp.SafetyError as e:
        print(f"Safety error: {e}")
    except fp.TimeoutError as e:
        print(f"Timeout error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        handle_exceptions(robot)
    except Exception as e:
        print(f"Unexpected error: {e}")
        handle_exceptions(robot)

    finally:
        if robot is not None:
            print("Disconnecting from robot...")
            robot.disconnect()
            print("Disconnected")


if __name__ == "__main__":
    main()
