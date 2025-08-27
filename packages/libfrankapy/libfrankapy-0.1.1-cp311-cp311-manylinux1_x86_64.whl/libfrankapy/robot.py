"""Main robot interface for libfrankapy.

This module provides the high-level Python interface for controlling
Franka robots through the real-time C++ backend.
"""

import threading
from typing import Any, Callable, Optional, Union

import numpy as np

from .control import MotionType, RealtimeConfig, Trajectory
from .exceptions import (
    ConnectionError,
    ControlError,
    SafetyError,
    StateError,
    TimeoutError,
)
from .state import CartesianPose, ForceTorque, JointState, RobotState
from .utils import (
    create_home_position,
    normalize_quaternion,
    validate_cartesian_pose,
    validate_joint_positions,
)

try:
    from ._libfrankapy_core import RealtimeController, SharedMemoryReader
except ImportError:
    # Fallback for development/testing
    class _FallbackRealtimeController:
        """Fallback implementation of RealtimeController for development/testing.

        This class provides a mock implementation when the C++ extension
        is not available, allowing for development and testing without
        hardware dependencies.
        """

        def __init__(self, robot_ip: str):
            """Initialize the controller.

            Args:
                robot_ip: IP address of the robot
            """
            self.robot_ip = robot_ip
            self._connected = False
            self._control_running = False

        def connect(self) -> bool:
            """Connect to the robot.

            Returns:
                True if connection successful
            """
            self._connected = True
            return True

        def disconnect(self) -> None:
            """Disconnect from the robot."""
            self._connected = False

        def is_connected(self) -> bool:
            """Check if robot is connected.

            Returns:
                True if connected
            """
            return self._connected

        def start_control(self) -> bool:
            """Start the control loop.

            Returns:
                True if control started successfully
            """
            self._control_running = True
            return True

        def stop_control(self) -> None:
            """Stop the control loop."""
            self._control_running = False

        def is_control_running(self) -> bool:
            """Check if control loop is running.

            Returns:
                True if control is running
            """
            return self._control_running

        def emergency_stop(self) -> None:
            """Trigger emergency stop."""

        def get_joint_positions(self) -> np.ndarray[Any, np.dtype[np.floating[Any]]]:
            """Get current joint positions.

            Returns:
                Array of joint positions
            """
            return np.zeros(7, dtype=np.float64)

        def send_joint_position_command(self, *args: Any, **kwargs: Any) -> bool:
            """Send joint position command.

            Returns:
                True if command sent successfully
            """
            return True

    class _FallbackSharedMemoryReader:
        """Fallback implementation of SharedMemoryReader for development/testing.

        This class provides a mock implementation for reading robot state
        when the C++ extension is not available.
        """

        def connect(self) -> bool:
            """Connect to shared memory.

            Returns:
                True if connection successful
            """
            return True

        def get_robot_state(self) -> dict[str, Any]:
            """Get current robot state.

            Returns:
                Dictionary containing robot state information
            """
            return {}


class FrankaRobot:
    """High-level interface for Franka robot control.

    This class provides a Python interface to the Franka robot while
    maintaining real-time performance through a C++ backend.

    Attributes:
        robot_ip: IP address of the robot
        realtime_config: Configuration for real-time control
    """

    def __init__(self, robot_ip: str, realtime_config: Optional[RealtimeConfig] = None):
        """Initialize FrankaRobot.

        Args:
            robot_ip: IP address of the Franka robot
            realtime_config: Optional real-time configuration

        Raises:
            ConfigurationError: If robot_ip is invalid
        """
        if not robot_ip or not isinstance(robot_ip, str):
            raise ValueError("robot_ip must be a valid IP address string")

        self.robot_ip = robot_ip
        self.realtime_config = realtime_config or RealtimeConfig()

        # Internal state
        self._controller: Optional[RealtimeController] = None
        self._state_reader: Optional[SharedMemoryReader] = None
        self._connected = False
        self._control_running = False
        self._last_state_update = 0.0
        self._state_cache: Optional[RobotState] = None
        self._state_lock = threading.Lock()

        # Initialize C++ controller
        try:
            self._controller = RealtimeController(robot_ip)
            self._state_reader = SharedMemoryReader()
        except NameError:
            # Use fallback classes if C++ extension not available
            self._controller = _FallbackRealtimeController(robot_ip)
            self._state_reader = _FallbackSharedMemoryReader()
        except Exception as e:
            raise ConnectionError(f"Failed to initialize robot controller: {e}")

    def connect(self) -> bool:
        """Connect to the robot.

        Returns:
            True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        if self._connected:
            return True

        if not self._controller:
            raise ConnectionError("Controller not initialized")

        try:
            success = self._controller.connect()
            if success:
                self._connected = True
                # Connect state reader to shared memory
                if self._state_reader:
                    self._state_reader.connect()
                print(f"Successfully connected to robot at {self.robot_ip}")
            return bool(success)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to robot: {e}")

    def disconnect(self) -> None:
        """Disconnect from the robot."""
        if not self._connected:
            return

        try:
            # Stop control loop first
            if self._control_running:
                self.stop_control()

            if self._controller:
                self._controller.disconnect()

            self._connected = False
            self._control_running = False
            print("Disconnected from robot")

        except Exception as e:
            print(f"Warning: Error during disconnect: {e}")

    def is_connected(self) -> bool:
        """Check if robot is connected.

        Returns:
            True if connected, False otherwise
        """
        if not self._controller:
            return False

        try:
            connected = self._controller.is_connected()
            self._connected = connected
            return bool(connected)
        except Exception:
            self._connected = False
            return False

    def start_control(self) -> bool:
        """Start the real-time control loop.

        Returns:
            True if control started successfully, False otherwise

        Raises:
            StateError: If robot is not connected
            ControlError: If control loop fails to start
        """
        if not self._connected:
            raise StateError("Robot must be connected before starting control")

        if self._control_running:
            return True

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            success = self._controller.start_control()
            if success:
                self._control_running = True
                print("Real-time control loop started")
            return bool(success)
        except Exception as e:
            raise ControlError(f"Failed to start control loop: {e}")

    def stop_control(self) -> None:
        """Stop the real-time control loop."""
        if not self._control_running:
            return

        try:
            if self._controller:
                self._controller.stop_control()
            self._control_running = False
            print("Real-time control loop stopped")
        except Exception as e:
            print(f"Warning: Error stopping control: {e}")

    def is_control_running(self) -> bool:
        """Check if control loop is running.

        Returns:
            True if control is running, False otherwise
        """
        if not self._controller:
            return False

        try:
            running = self._controller.is_control_running()
            self._control_running = running
            return bool(running)
        except Exception:
            self._control_running = False
            return False

    def emergency_stop(self) -> None:
        """Emergency stop - immediately halt all motion.

        This function can be called at any time to stop the robot.
        """
        try:
            if self._controller:
                self._controller.emergency_stop()
            print("Emergency stop activated")
        except Exception as e:
            print(f"Error during emergency stop: {e}")

    def get_joint_state(self) -> JointState:
        """Get current joint state.

        Returns:
            Current joint state with positions, velocities, and efforts

        Raises:
            StateError: If robot is not connected or state is invalid
        """
        self._ensure_connected()

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            positions = self._controller.get_joint_positions()
            velocities = self._controller.get_joint_velocities()
            torques = self._controller.get_joint_torques()
            timestamp = self._controller.get_timestamp() / 1e6  # Convert to seconds

            return JointState(
                positions=positions.tolist(),
                velocities=velocities.tolist(),
                efforts=torques.tolist(),
                timestamp=timestamp,
            )
        except Exception as e:
            raise StateError(f"Failed to get joint state: {e}")

    def get_cartesian_pose(self) -> CartesianPose:
        """Get current end-effector pose.

        Returns:
            Current Cartesian pose with position and orientation

        Raises:
            StateError: If robot is not connected or state is invalid
        """
        self._ensure_connected()

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            position = self._controller.get_cartesian_position()
            orientation = self._controller.get_cartesian_orientation()
            timestamp = self._controller.get_timestamp() / 1e6  # Convert to seconds

            return CartesianPose(
                position=position.tolist(),
                orientation=orientation.tolist(),
                timestamp=timestamp,
            )
        except Exception as e:
            raise StateError(f"Failed to get Cartesian pose: {e}")

    def get_robot_state(self) -> RobotState:
        """Get complete robot state.

        Returns:
            Complete robot state including joint state, pose, and forces

        Raises:
            StateError: If robot is not connected or state is invalid
        """
        self._ensure_connected()

        try:
            # Get individual state components
            joint_state = self.get_joint_state()
            cartesian_pose = self.get_cartesian_pose()

            # Get additional state information
            if not self._controller:
                raise StateError("Controller not initialized")
            external_wrench_array = self._controller.get_external_wrench()
            external_wrench = ForceTorque(
                force=external_wrench_array[:3].tolist(),
                torque=external_wrench_array[3:].tolist(),
                timestamp=joint_state.timestamp,
            )

            # Determine robot mode
            if self._controller.is_moving():
                robot_mode = "MOVING"
            elif self._controller.has_error():
                robot_mode = "ERROR"
            elif self.is_control_running():
                robot_mode = "READY"
            else:
                robot_mode = "IDLE"

            control_frequency = self._controller.get_control_frequency()

            return RobotState(
                joint_state=joint_state,
                cartesian_pose=cartesian_pose,
                external_wrench=external_wrench,
                robot_mode=robot_mode,
                control_frequency=control_frequency,
                timestamp=joint_state.timestamp,
            )

        except Exception as e:
            raise StateError(f"Failed to get robot state: {e}")

    def get_joint_torques(self) -> list[float]:
        """Get current joint torques.

        Returns:
            List of 7 joint torques in Nm

        Raises:
            StateError: If robot is not connected
        """
        self._ensure_connected()

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            torques = self._controller.get_joint_torques()
            return list(torques.tolist())
        except Exception as e:
            raise StateError(f"Failed to get joint torques: {e}")

    def is_moving(self) -> bool:
        """Check if robot is currently moving.

        Returns:
            True if robot is moving, False otherwise
        """
        if not self._connected or not self._controller:
            return False

        try:
            return bool(self._controller.is_moving())
        except Exception:
            return False

    def has_error(self) -> bool:
        """Check if robot has an error.

        Returns:
            True if robot has an error, False otherwise
        """
        if not self._connected or not self._controller:
            return True

        try:
            return bool(self._controller.has_error())
        except Exception:
            return True

    def get_error_code(self) -> int:
        """Get current error code.

        Returns:
            Error code (0 if no error)
        """
        if not self._connected or not self._controller:
            return -999

        try:
            return int(self._controller.get_error_code())
        except Exception:
            return -999

    def get_control_frequency(self) -> float:
        """Get current control loop frequency.

        Returns:
            Control frequency in Hz
        """
        if not self._connected or not self._controller:
            return 0.0

        try:
            return float(self._controller.get_control_frequency())
        except Exception:
            return 0.0

    def _ensure_connected(self) -> None:
        """Ensure robot is connected, raise exception if not.

        Raises:
            StateError: If robot is not connected
        """
        if not self._connected:
            raise StateError("Robot is not connected")

        if not self._controller:
            raise StateError("Controller not initialized")

    def _ensure_control_running(self) -> None:
        """Ensure control loop is running, raise exception if not.

        Raises:
            StateError: If control loop is not running
        """
        self._ensure_connected()

        if not self._control_running:
            raise StateError("Control loop is not running")

    def _wait_for_motion_completion(self, timeout: float = 30.0) -> bool:
        """Wait for current motion to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if motion completed, False if timeout
        """
        if not self._controller:
            return False

        try:
            return bool(self._controller.wait_for_command_completion(timeout))
        except Exception:
            return False

    def __enter__(self) -> "FrankaRobot":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()

    def move_to_joint(
        self,
        joint_positions: list[float],
        speed_factor: float = 0.1,
        acceleration_factor: float = 0.1,
        timeout: float = 30.0,
        wait: bool = True,
    ) -> bool:
        """Move robot to target joint configuration.

        Args:
            joint_positions: Target joint positions in radians [q1, q2, ..., q7]
            speed_factor: Speed scaling factor (0.0 to 1.0)
            acceleration_factor: Acceleration scaling factor (0.0 to 1.0)
            timeout: Maximum time for motion in seconds
            wait: Whether to wait for motion completion

        Returns:
            True if motion command sent successfully, False otherwise

        Raises:
            StateError: If robot is not ready for motion
            ControlError: If motion command fails
            SafetyError: If joint positions are unsafe
        """
        self._ensure_control_running()

        # Validate input parameters
        if len(joint_positions) != 7:
            raise ValueError("joint_positions must have exactly 7 elements")

        if not validate_joint_positions(joint_positions):
            raise SafetyError("Joint positions are outside safe limits")

        if not (0.0 <= speed_factor <= 1.0):
            raise ValueError("speed_factor must be between 0.0 and 1.0")

        if not (0.0 <= acceleration_factor <= 1.0):
            raise ValueError("acceleration_factor must be between 0.0 and 1.0")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        # Check if robot has errors
        if self.has_error():
            raise StateError(f"Robot has error (code: {self.get_error_code()})")

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            # Send joint position command
            positions_array: np.ndarray[Any, np.dtype[np.floating[Any]]] = np.array(
                joint_positions, dtype=np.float64
            )
            success = self._controller.send_joint_position_command(
                positions_array, speed_factor, acceleration_factor, timeout
            )

            if not success:
                raise ControlError("Failed to send joint position command")

            # Wait for completion if requested
            if wait:
                if not self._wait_for_motion_completion(timeout):
                    raise TimeoutError(
                        f"Motion did not complete within {timeout} seconds"
                    )

            return True

        except Exception as e:
            if isinstance(e, (StateError, ControlError, SafetyError, TimeoutError)):
                raise
            raise ControlError(f"Joint motion failed: {e}")

    def move_to_pose(
        self,
        target_pose: list[float],
        speed_factor: float = 0.1,
        motion_type: Union[MotionType, str] = MotionType.LINEAR,
        timeout: float = 30.0,
        wait: bool = True,
    ) -> bool:
        """Move robot to target Cartesian pose.

        Args:
            target_pose: Target pose [x, y, z, qx, qy, qz, qw] in meters and quaternion
            speed_factor: Speed scaling factor (0.0 to 1.0)
            motion_type: Type of motion (LINEAR, JOINT_INTERPOLATED, CIRCULAR)
            timeout: Maximum time for motion in seconds
            wait: Whether to wait for motion completion

        Returns:
            True if motion command sent successfully, False otherwise

        Raises:
            StateError: If robot is not ready for motion
            ControlError: If motion command fails
            SafetyError: If target pose is unsafe
        """
        self._ensure_control_running()

        # Validate input parameters
        if len(target_pose) != 7:
            raise ValueError(
                "target_pose must have exactly 7 elements [x, y, z, qx, qy, qz, qw]"
            )

        if not validate_cartesian_pose(target_pose):
            raise SafetyError("Target pose is outside safe workspace")

        if not (0.0 <= speed_factor <= 1.0):
            raise ValueError("speed_factor must be between 0.0 and 1.0")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        # Convert motion_type to integer if needed
        if isinstance(motion_type, str):
            motion_type = MotionType[motion_type.upper()]
        motion_type_int = (
            motion_type.value if hasattr(motion_type, "value") else motion_type
        )

        # Normalize quaternion
        position = target_pose[:3]
        qx, qy, qz, qw = normalize_quaternion(*target_pose[3:])

        # Check if robot has errors
        if self.has_error():
            raise StateError(f"Robot has error (code: {self.get_error_code()})")

        if not self._controller:
            raise StateError("Controller not initialized")

        try:
            # Send Cartesian position command
            position_array: np.ndarray[Any, np.dtype[np.floating[Any]]] = np.array(
                position, dtype=np.float64
            )
            orientation_array: np.ndarray[Any, np.dtype[np.floating[Any]]] = np.array(
                [qx, qy, qz, qw], dtype=np.float64
            )

            success = self._controller.send_cartesian_position_command(
                position_array,
                orientation_array,
                speed_factor,
                motion_type_int,
                timeout,
            )

            if not success:
                raise ControlError("Failed to send Cartesian position command")

            # Wait for completion if requested
            if wait:
                if not self._wait_for_motion_completion(timeout):
                    raise TimeoutError(
                        f"Motion did not complete within {timeout} seconds"
                    )

            return True

        except Exception as e:
            if isinstance(e, (StateError, ControlError, SafetyError, TimeoutError)):
                raise
            raise ControlError(f"Cartesian motion failed: {e}")

    def execute_trajectory(
        self,
        trajectory: Trajectory,
        callback: Optional[Callable[[int, Any], None]] = None,
    ) -> bool:
        """Execute a predefined trajectory.

        Args:
            trajectory: Trajectory object containing waypoints
            callback: Optional callback function called during execution

        Returns:
            True if trajectory executed successfully, False otherwise

        Raises:
            StateError: If robot is not ready for motion
            ControlError: If trajectory execution fails
        """
        self._ensure_control_running()

        if not trajectory.points:
            raise ValueError("Trajectory must contain at least one point")

        # Check if robot has errors
        if self.has_error():
            raise StateError(f"Robot has error (code: {self.get_error_code()})")

        try:
            # Execute trajectory point by point
            for i, point in enumerate(trajectory.points):
                if callback:
                    callback(i, point)

                # Determine motion type based on trajectory
                if trajectory.is_joint_trajectory:
                    success = self.move_to_joint(
                        point.positions,
                        speed_factor=trajectory.speed_factor,
                        acceleration_factor=trajectory.acceleration_factor,
                        timeout=30.0,
                        wait=True,
                    )
                else:
                    # Convert 6-DOF pose to 7-DOF (assume identity quaternion if not provided)
                    if len(point.positions) == 6:
                        pose = point.positions[:3] + [
                            0.0,
                            0.0,
                            0.0,
                            1.0,
                        ]  # [x,y,z,qx,qy,qz,qw]
                    else:
                        pose = point.positions

                    success = self.move_to_pose(
                        pose,
                        speed_factor=trajectory.speed_factor,
                        motion_type=trajectory.motion_type,
                        timeout=30.0,
                        wait=True,
                    )

                if not success:
                    raise ControlError(f"Failed to execute trajectory point {i}")

            return True

        except Exception as e:
            if isinstance(e, (StateError, ControlError, SafetyError, TimeoutError)):
                raise
            raise ControlError(f"Trajectory execution failed: {e}")

    def move_to_home(self, speed_factor: float = 0.1, wait: bool = True) -> bool:
        """Move robot to home position.

        Args:
            speed_factor: Speed scaling factor (0.0 to 1.0)
            wait: Whether to wait for motion completion

        Returns:
            True if motion successful, False otherwise
        """
        home_position = create_home_position()
        return self.move_to_joint(home_position, speed_factor=speed_factor, wait=wait)

    def stop_motion(self) -> None:
        """Stop current motion gracefully.

        This function stops the current motion but does not trigger
        an emergency stop.
        """
        try:
            if self._controller and self._connected:
                # Send stop command by sending current position as target
                current_state = self.get_joint_state()
                self.move_to_joint(
                    current_state.positions, speed_factor=0.01, wait=False
                )
        except Exception as e:
            print(f"Warning: Error stopping motion: {e}")

    def __del__(self) -> None:
        """Destructor - ensure clean disconnect."""
        try:
            self.disconnect()
        except Exception:
            # Ignore exceptions during cleanup to prevent issues in destructor
            # This is safe because __del__ should not raise exceptions
            pass  # nosec B110


# Make classes available at module level for testing
try:
    from ._libfrankapy_core import RealtimeController, SharedMemoryReader
except ImportError:
    RealtimeController = _FallbackRealtimeController
    SharedMemoryReader = _FallbackSharedMemoryReader
