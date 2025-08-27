"""Utility functions for libfrankapy.

This module provides utility functions for coordinate transformations, validation,
and common operations used throughout the libfrankapy package.
"""

import math
from typing import Union


def validate_joint_positions(positions: list[float]) -> bool:
    """Validate joint positions are within safe ranges.

    Args:
        positions: List of 7 joint positions in radians

    Returns:
        True if positions are valid, False otherwise
    """
    if len(positions) != 7:
        return False

    # Franka Emika Panda joint limits (radians)
    joint_limits = [
        (-2.8973, 2.8973),  # Joint 1
        (-1.7628, 1.7628),  # Joint 2
        (-2.8973, 2.8973),  # Joint 3
        (-3.0718, -0.0698),  # Joint 4
        (-2.8973, 2.8973),  # Joint 5
        (-0.0175, 3.7525),  # Joint 6
        (-2.8973, 2.8973),  # Joint 7
    ]

    for i, (pos, (min_limit, max_limit)) in enumerate(zip(positions, joint_limits)):
        if not (min_limit <= pos <= max_limit):
            return False

    return True


def validate_cartesian_pose(pose: list[float]) -> bool:
    """Validate Cartesian pose format and values.

    Args:
        pose: List of 7 values [x, y, z, qx, qy, qz, qw] or 6 values [x, y, z, rx, ry, rz]

    Returns:
        True if pose is valid, False otherwise
    """
    if len(pose) == 7:
        # Quaternion format [x, y, z, qx, qy, qz, qw]
        position = pose[:3]
        quaternion = pose[3:]

        # Check quaternion normalization
        quat_norm = sum(q**2 for q in quaternion) ** 0.5
        if abs(quat_norm - 1.0) > 0.01:
            return False

    elif len(pose) == 6:
        # Euler angles format [x, y, z, rx, ry, rz]
        position = pose[:3]

    else:
        return False

    # Basic workspace limits (approximate for Franka Panda)
    x, y, z = position
    if not (-0.855 <= x <= 0.855):
        return False
    if not (-0.855 <= y <= 0.855):
        return False
    if not (0.0 <= z <= 1.19):
        return False

    return True


def quaternion_to_euler(
    qx: float, qy: float, qz: float, qw: float
) -> tuple[float, float, float]:
    """Convert quaternion to Euler angles (roll, pitch, yaw).

    Args:
        qx, qy, qz, qw: Quaternion components

    Returns:
        Tuple of (roll, pitch, yaw) in radians
    """
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


def euler_to_quaternion(
    roll: float, pitch: float, yaw: float
) -> tuple[float, float, float, float]:
    """Convert Euler angles to quaternion.

    Args:
        roll, pitch, yaw: Euler angles in radians

    Returns:
        Tuple of (qx, qy, qz, qw) quaternion components
    """
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return qx, qy, qz, qw


def normalize_quaternion(
    qx: float, qy: float, qz: float, qw: float
) -> tuple[float, float, float, float]:
    """Normalize a quaternion.

    Args:
        qx, qy, qz, qw: Quaternion components

    Returns:
        Normalized quaternion (qx, qy, qz, qw)
    """
    norm = math.sqrt(qx**2 + qy**2 + qz**2 + qw**2)
    if norm == 0:
        return 0.0, 0.0, 0.0, 1.0

    return qx / norm, qy / norm, qz / norm, qw / norm


def interpolate_joint_positions(
    start: list[float], end: list[float], t: float
) -> list[float]:
    """Linearly interpolate between two joint configurations.

    Args:
        start: Starting joint positions
        end: Ending joint positions
        t: Interpolation parameter (0.0 to 1.0)

    Returns:
        Interpolated joint positions
    """
    if len(start) != 7 or len(end) != 7:
        raise ValueError("Joint positions must have 7 values")

    if not (0.0 <= t <= 1.0):
        raise ValueError("Interpolation parameter t must be between 0.0 and 1.0")

    return [s + t * (e - s) for s, e in zip(start, end)]


def compute_joint_distance(pos1: list[float], pos2: list[float]) -> float:
    """Compute distance between two joint configurations.

    Args:
        pos1, pos2: Joint positions to compare

    Returns:
        Euclidean distance between joint configurations
    """
    if len(pos1) != 7 or len(pos2) != 7:
        raise ValueError("Joint positions must have 7 values")

    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))


def compute_cartesian_distance(
    pose1: list[float], pose2: list[float]
) -> tuple[float, float]:
    """Compute distance between two Cartesian poses.

    Args:
        pose1, pose2: Cartesian poses [x, y, z, qx, qy, qz, qw]

    Returns:
        Tuple of (position_distance, orientation_distance)
    """
    if len(pose1) != 7 or len(pose2) != 7:
        raise ValueError("Cartesian poses must have 7 values")

    # Position distance
    pos_dist = math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pose1[:3], pose2[:3])))

    # Orientation distance (quaternion angle)
    q1 = pose1[3:]
    q2 = pose2[3:]
    dot_product = sum(q1i * q2i for q1i, q2i in zip(q1, q2))
    dot_product = max(-1.0, min(1.0, abs(dot_product)))  # Clamp to [-1, 1]
    ori_dist = 2 * math.acos(dot_product)

    return pos_dist, ori_dist


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between minimum and maximum bounds.

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def degrees_to_radians(degrees: Union[float, list[float]]) -> Union[float, list[float]]:
    """Convert degrees to radians.

    Args:
        degrees: Angle(s) in degrees

    Returns:
        Angle(s) in radians
    """
    if isinstance(degrees, list):
        return [math.radians(d) for d in degrees]
    return math.radians(degrees)


def radians_to_degrees(radians: Union[float, list[float]]) -> Union[float, list[float]]:
    """Convert radians to degrees.

    Args:
        radians: Angle(s) in radians

    Returns:
        Angle(s) in degrees
    """
    if isinstance(radians, list):
        return [math.degrees(r) for r in radians]
    return math.degrees(radians)


def create_home_position() -> list[float]:
    """Create a safe home joint configuration.

    Returns:
        Home joint positions in radians
    """
    return [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]


def create_ready_position() -> list[float]:
    """Create a ready joint configuration for manipulation.

    Returns:
        Ready joint positions in radians
    """
    return [0.0, -0.3, 0.0, -2.2, 0.0, 1.9, 0.785]
