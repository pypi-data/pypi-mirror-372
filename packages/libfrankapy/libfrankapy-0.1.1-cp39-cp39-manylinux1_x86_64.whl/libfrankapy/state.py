"""State data structures for libfrankapy.

This module defines data classes for representing robot state information,
including joint states, Cartesian poses, and complete robot state.
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class JointState:
    """Represents the state of robot joints.

    Attributes:
        positions: Joint positions in radians [q1, q2, ..., q7]
        velocities: Joint velocities in rad/s [dq1, dq2, ..., dq7]
        efforts: Joint torques in Nm [tau1, tau2, ..., tau7]
        timestamp: Time when state was captured (seconds since epoch)
    """

    positions: list[float]  # 7 joint angles in radians
    velocities: list[float]  # 7 joint velocities in rad/s
    efforts: list[float]  # 7 joint torques in Nm
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Validate joint state data after initialization."""
        if len(self.positions) != 7:
            raise ValueError(f"Expected 7 joint positions, got {len(self.positions)}")
        if len(self.velocities) != 7:
            raise ValueError(f"Expected 7 joint velocities, got {len(self.velocities)}")
        if len(self.efforts) != 7:
            raise ValueError(f"Expected 7 joint efforts, got {len(self.efforts)}")

        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class CartesianPose:
    """Represents Cartesian pose of robot end-effector.

    Attributes:
        position: Cartesian position [x, y, z] in meters
        orientation: Quaternion orientation [qx, qy, qz, qw]
        timestamp: Time when pose was captured (seconds since epoch)
    """

    position: list[float]  # [x, y, z] in meters
    orientation: list[float]  # [qx, qy, qz, qw] quaternion
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Validate Cartesian pose data after initialization."""
        if len(self.position) != 3:
            raise ValueError(f"Expected 3 position values, got {len(self.position)}")
        if len(self.orientation) != 4:
            raise ValueError(
                f"Expected 4 orientation values, got {len(self.orientation)}"
            )

        if self.timestamp == 0.0:
            self.timestamp = time.time()

    @property
    def x(self) -> float:
        """X coordinate in meters."""
        return self.position[0]

    @property
    def y(self) -> float:
        """Y coordinate in meters."""
        return self.position[1]

    @property
    def z(self) -> float:
        """Z coordinate in meters."""
        return self.position[2]

    @property
    def qx(self) -> float:
        """Quaternion x component."""
        return self.orientation[0]

    @property
    def qy(self) -> float:
        """Quaternion y component."""
        return self.orientation[1]

    @property
    def qz(self) -> float:
        """Quaternion z component."""
        return self.orientation[2]

    @property
    def qw(self) -> float:
        """Quaternion w component."""
        return self.orientation[3]


@dataclass
class ForceTorque:
    """Represents force and torque measurements.

    Attributes:
        force: External force [fx, fy, fz] in Newtons
        torque: External torque [tx, ty, tz] in Nm
        timestamp: Time when measurement was taken
    """

    force: list[float]  # [fx, fy, fz] in N
    torque: list[float]  # [tx, ty, tz] in Nm
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Validate force/torque data after initialization."""
        if len(self.force) != 3:
            raise ValueError(f"Expected 3 force values, got {len(self.force)}")
        if len(self.torque) != 3:
            raise ValueError(f"Expected 3 torque values, got {len(self.torque)}")

        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class RobotState:
    """Complete robot state information.

    Attributes:
        joint_state: Current joint state
        cartesian_pose: Current end-effector pose
        external_wrench: External forces and torques
        robot_mode: Current robot operating mode
        control_frequency: Current control loop frequency in Hz
        timestamp: Time when state was captured
    """

    joint_state: JointState
    cartesian_pose: CartesianPose
    external_wrench: Optional[ForceTorque] = None
    robot_mode: str = "IDLE"
    control_frequency: float = 1000.0
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Validate robot state after initialization."""
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    @property
    def is_moving(self) -> bool:
        """Check if robot is currently moving."""
        # Consider robot moving if any joint velocity > threshold
        velocity_threshold = 0.01  # rad/s
        return any(abs(v) > velocity_threshold for v in self.joint_state.velocities)

    @property
    def is_in_contact(self) -> bool:
        """Check if robot is in contact with environment."""
        if self.external_wrench is None:
            return False

        # Consider in contact if external force/torque > threshold
        force_threshold: float = 5.0  # N
        torque_threshold: float = 1.0  # Nm

        force_magnitude: float = sum(f**2 for f in self.external_wrench.force) ** 0.5
        torque_magnitude: float = (
            sum(t**2 for t in self.external_wrench.torque) ** 0.5
        )

        return bool(
            force_magnitude > force_threshold or torque_magnitude > torque_threshold
        )
