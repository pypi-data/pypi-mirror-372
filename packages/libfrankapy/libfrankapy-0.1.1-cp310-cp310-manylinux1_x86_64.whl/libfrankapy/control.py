"""Control data structures for libfrankapy.

This module defines data classes for robot control configuration,
trajectory planning, and safety limits.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ControlMode(Enum):
    """Robot control modes."""

    IDLE = "IDLE"
    JOINT_POSITION = "JOINT_POSITION"
    CARTESIAN_POSITION = "CARTESIAN_POSITION"
    JOINT_VELOCITY = "JOINT_VELOCITY"
    CARTESIAN_VELOCITY = "CARTESIAN_VELOCITY"
    TORQUE = "TORQUE"
    TRAJECTORY = "TRAJECTORY"


class MotionType(Enum):
    """Types of motion for Cartesian control."""

    LINEAR = "LINEAR"
    JOINT_INTERPOLATED = "JOINT_INTERPOLATED"
    CIRCULAR = "CIRCULAR"


@dataclass
class SafetyLimits:
    """Safety limits for robot operation.

    Attributes:
        max_joint_velocity: Maximum joint velocities [rad/s]
        max_joint_acceleration: Maximum joint accelerations [rad/s²]
        max_joint_jerk: Maximum joint jerks [rad/s³]
        max_cartesian_velocity: Maximum Cartesian velocity [m/s, rad/s]
        max_cartesian_acceleration: Maximum Cartesian acceleration [m/s², rad/s²]
        max_force: Maximum external force [N]
        max_torque: Maximum external torque [Nm]
        collision_threshold: Collision detection threshold
    """

    max_joint_velocity: list[float] = field(default_factory=lambda: [2.175] * 7)
    max_joint_acceleration: list[float] = field(default_factory=lambda: [15.0] * 7)
    max_joint_jerk: list[float] = field(default_factory=lambda: [7500.0] * 7)
    max_cartesian_velocity: list[float] = field(
        default_factory=lambda: [1.7, 2.5, 2.5, 2.5, 2.5, 2.5]
    )
    max_cartesian_acceleration: list[float] = field(
        default_factory=lambda: [13.0, 25.0, 25.0, 25.0, 25.0, 25.0]
    )
    max_force: list[float] = field(default_factory=lambda: [20.0, 20.0, 20.0])
    max_torque: list[float] = field(default_factory=lambda: [25.0, 25.0, 25.0])
    collision_threshold: float = 20.0

    def __post_init__(self) -> None:
        """Validate safety limits after initialization."""
        if len(self.max_joint_velocity) != 7:
            raise ValueError("max_joint_velocity must have 7 values")
        if len(self.max_joint_acceleration) != 7:
            raise ValueError("max_joint_acceleration must have 7 values")
        if len(self.max_joint_jerk) != 7:
            raise ValueError("max_joint_jerk must have 7 values")
        if len(self.max_cartesian_velocity) != 6:
            raise ValueError("max_cartesian_velocity must have 6 values")
        if len(self.max_cartesian_acceleration) != 6:
            raise ValueError("max_cartesian_acceleration must have 6 values")
        if len(self.max_force) != 3:
            raise ValueError("max_force must have 3 values")
        if len(self.max_torque) != 3:
            raise ValueError("max_torque must have 3 values")


@dataclass
class RealtimeConfig:
    """Configuration for real-time control.

    Attributes:
        control_frequency: Control loop frequency in Hz
        filter_cutoff: Low-pass filter cutoff frequency in Hz
        safety_limits: Safety limits configuration
        enable_logging: Enable real-time logging
        log_frequency: Logging frequency in Hz
    """

    control_frequency: int = 1000  # Hz
    filter_cutoff: float = 100.0  # Hz
    safety_limits: SafetyLimits = field(default_factory=SafetyLimits)
    enable_logging: bool = False
    log_frequency: int = 100  # Hz

    def __post_init__(self) -> None:
        """Validate real-time configuration."""
        if self.control_frequency <= 0:
            raise ValueError("control_frequency must be positive")
        if self.filter_cutoff <= 0:
            raise ValueError("filter_cutoff must be positive")
        if self.log_frequency <= 0:
            raise ValueError("log_frequency must be positive")
        if self.log_frequency > self.control_frequency:
            raise ValueError("log_frequency cannot exceed control_frequency")


@dataclass
class TrajectoryPoint:
    """Single point in a trajectory.

    Attributes:
        positions: Joint positions or Cartesian pose
        velocities: Joint velocities or Cartesian velocities
        accelerations: Joint accelerations or Cartesian accelerations
        time_from_start: Time from trajectory start in seconds
    """

    positions: list[float]
    velocities: Optional[list[float]] = None
    accelerations: Optional[list[float]] = None
    time_from_start: float = 0.0

    def __post_init__(self) -> None:
        """Validate trajectory point."""
        if len(self.positions) not in [7, 6]:  # 7 for joints, 6 for Cartesian
            raise ValueError("positions must have 7 (joints) or 6 (Cartesian) values")

        if self.velocities is not None and len(self.velocities) != len(self.positions):
            raise ValueError("velocities must match positions length")

        if self.accelerations is not None and len(self.accelerations) != len(
            self.positions
        ):
            raise ValueError("accelerations must match positions length")


@dataclass
class Trajectory:
    """Robot trajectory definition.

    Attributes:
        points: List of trajectory points
        control_mode: Type of control (joint or Cartesian)
        motion_type: Type of motion for Cartesian trajectories
        speed_factor: Global speed scaling factor (0.0 to 1.0)
        acceleration_factor: Global acceleration scaling factor (0.0 to 1.0)
    """

    points: list[TrajectoryPoint]
    control_mode: ControlMode = ControlMode.JOINT_POSITION
    motion_type: MotionType = MotionType.JOINT_INTERPOLATED
    speed_factor: float = 1.0
    acceleration_factor: float = 1.0

    def __post_init__(self) -> None:
        """Validate trajectory."""
        if not self.points:
            raise ValueError("Trajectory must have at least one point")

        if not (0.0 <= self.speed_factor <= 1.0):
            raise ValueError("speed_factor must be between 0.0 and 1.0")

        if not (0.0 <= self.acceleration_factor <= 1.0):
            raise ValueError("acceleration_factor must be between 0.0 and 1.0")

        # Validate that all points have consistent dimensions
        expected_dim = len(self.points[0].positions)
        for i, point in enumerate(self.points):
            if len(point.positions) != expected_dim:
                raise ValueError(f"Point {i} has inconsistent dimensions")

    @property
    def duration(self) -> float:
        """Total trajectory duration in seconds."""
        if not self.points:
            return 0.0
        return self.points[-1].time_from_start

    @property
    def is_joint_trajectory(self) -> bool:
        """Check if this is a joint space trajectory."""
        return len(self.points[0].positions) == 7

    @property
    def is_cartesian_trajectory(self) -> bool:
        """Check if this is a Cartesian space trajectory."""
        return len(self.points[0].positions) == 6


@dataclass
class MotionCommand:
    """Command for robot motion.

    Attributes:
        command_id: Unique command identifier
        command_type: Type of motion command
        target_positions: Target positions (joint or Cartesian)
        speed_factor: Speed scaling factor
        acceleration_factor: Acceleration scaling factor
        motion_type: Type of motion for Cartesian commands
        timeout: Command timeout in seconds
    """

    command_id: int
    command_type: ControlMode
    target_positions: list[float]
    speed_factor: float = 0.1
    acceleration_factor: float = 0.1
    motion_type: MotionType = MotionType.JOINT_INTERPOLATED
    timeout: float = 30.0

    def __post_init__(self) -> None:
        """Validate motion command."""
        if len(self.target_positions) not in [7, 6]:
            raise ValueError(
                "target_positions must have 7 (joints) or 6 (Cartesian) values"
            )

        if not (0.0 <= self.speed_factor <= 1.0):
            raise ValueError("speed_factor must be between 0.0 and 1.0")

        if not (0.0 <= self.acceleration_factor <= 1.0):
            raise ValueError("acceleration_factor must be between 0.0 and 1.0")

        if self.timeout <= 0.0:
            raise ValueError("timeout must be positive")
