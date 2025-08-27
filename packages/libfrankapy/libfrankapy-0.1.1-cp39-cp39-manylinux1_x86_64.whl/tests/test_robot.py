#!/usr/bin/env python3
"""Tests for FrankaRobot class.

These tests verify the basic functionality of the FrankaRobot class
without requiring actual hardware.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

import libfrankapy as fp
from libfrankapy.control import RealtimeConfig
from libfrankapy.exceptions import StateError
from libfrankapy.robot import FrankaRobot


class TestFrankaRobot:
    """Test cases for FrankaRobot class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.robot_ip = "192.168.1.100"
        self.config = RealtimeConfig()

    def test_robot_initialization(self):
        """Test robot initialization."""
        robot = FrankaRobot(self.robot_ip)
        assert robot.robot_ip == self.robot_ip
        assert robot.realtime_config is not None
        assert not robot._connected
        assert not robot._control_running

    def test_robot_initialization_with_config(self):
        """Test robot initialization with custom config."""
        robot = FrankaRobot(self.robot_ip, self.config)
        assert robot.robot_ip == self.robot_ip
        assert robot.realtime_config == self.config

    def test_invalid_robot_ip(self):
        """Test initialization with invalid IP."""
        with pytest.raises(ValueError):
            FrankaRobot("")

        with pytest.raises(ValueError):
            FrankaRobot(None)

    @patch("libfrankapy.robot.RealtimeController")
    def test_connection_success(self, mock_controller_class):
        """Test successful robot connection."""
        # Mock controller
        mock_controller = Mock()
        mock_controller.connect.return_value = True
        mock_controller_class.return_value = mock_controller

        # Mock state reader
        with patch("libfrankapy.robot.SharedMemoryReader") as mock_reader_class:
            mock_reader = Mock()
            mock_reader_class.return_value = mock_reader

            robot = FrankaRobot(self.robot_ip)
            result = robot.connect()

            assert result is True
            assert robot._connected is True
            mock_controller.connect.assert_called_once()
            mock_reader.connect.assert_called_once()

    @patch("libfrankapy.robot.RealtimeController")
    def test_connection_failure(self, mock_controller_class):
        """Test failed robot connection."""
        # Mock controller that fails to connect
        mock_controller = Mock()
        mock_controller.connect.return_value = False
        mock_controller_class.return_value = mock_controller

        with patch("libfrankapy.robot.SharedMemoryReader"):
            robot = FrankaRobot(self.robot_ip)
            result = robot.connect()

            assert result is False
            assert robot._connected is False

    @patch("libfrankapy.robot.RealtimeController")
    def test_start_control_without_connection(self, mock_controller_class):
        """Test starting control without connection."""
        robot = FrankaRobot(self.robot_ip)

        with pytest.raises(StateError):
            robot.start_control()

    @patch("libfrankapy.robot.RealtimeController")
    def test_move_to_joint_validation(self, mock_controller_class):
        """Test joint motion parameter validation."""
        robot = FrankaRobot(self.robot_ip)
        robot._connected = True
        robot._control_running = True

        # Use safe joint positions for testing
        safe_joint_positions = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]

        # Test invalid number of joints
        with pytest.raises(ValueError):
            robot.move_to_joint([1, 2, 3])  # Only 3 joints instead of 7

        # Test invalid speed factor
        with pytest.raises(ValueError):
            robot.move_to_joint(safe_joint_positions, speed_factor=1.5)

        # Test invalid acceleration factor
        with pytest.raises(ValueError):
            robot.move_to_joint(safe_joint_positions, acceleration_factor=-0.1)

        # Test invalid timeout
        with pytest.raises(ValueError):
            robot.move_to_joint(safe_joint_positions, timeout=-1)

    @patch("libfrankapy.robot.RealtimeController")
    def test_move_to_pose_validation(self, mock_controller_class):
        """Test Cartesian motion parameter validation."""
        robot = FrankaRobot(self.robot_ip)
        robot._connected = True
        robot._control_running = True

        # Use safe Cartesian pose for testing [x, y, z, qx, qy, qz, qw]
        safe_pose = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0]

        # Test invalid pose length
        with pytest.raises(ValueError):
            robot.move_to_pose([1, 2, 3])  # Only 3 elements instead of 7

        # Test invalid speed factor
        with pytest.raises(ValueError):
            robot.move_to_pose(safe_pose, speed_factor=2.0)

        # Test invalid timeout
        with pytest.raises(ValueError):
            robot.move_to_pose(safe_pose, timeout=0)

    def test_context_manager(self):
        """Test robot as context manager."""
        with patch("libfrankapy.robot.RealtimeController"):
            with patch("libfrankapy.robot.SharedMemoryReader"):
                with patch.object(FrankaRobot, "connect", return_value=True):
                    with patch.object(FrankaRobot, "disconnect") as mock_disconnect:
                        with FrankaRobot(self.robot_ip) as robot:
                            assert isinstance(robot, FrankaRobot)

                        mock_disconnect.assert_called_once()

    @patch("libfrankapy.robot.RealtimeController")
    def test_emergency_stop(self, mock_controller_class):
        """Test emergency stop functionality."""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        robot = FrankaRobot(self.robot_ip)
        robot._connected = True

        robot.emergency_stop()
        mock_controller.emergency_stop.assert_called_once()

    @patch("libfrankapy.robot.RealtimeController")
    def test_get_joint_state(self, mock_controller_class):
        """Test getting joint state."""
        # Mock controller with state data
        mock_controller = Mock()
        mock_controller.get_joint_positions.return_value = np.array(
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        )
        mock_controller.get_joint_velocities.return_value = np.array(
            [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
        )
        mock_controller.get_joint_torques.return_value = np.array(
            [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
        )
        mock_controller.get_timestamp.return_value = 1234567890000000  # microseconds
        mock_controller_class.return_value = mock_controller

        robot = FrankaRobot(self.robot_ip)
        robot._connected = True

        joint_state = robot.get_joint_state()

        assert isinstance(joint_state, fp.JointState)
        assert len(joint_state.positions) == 7
        assert len(joint_state.velocities) == 7
        assert len(joint_state.efforts) == 7
        assert joint_state.timestamp > 0

    @patch("libfrankapy.robot.RealtimeController")
    def test_get_cartesian_pose(self, mock_controller_class):
        """Test getting Cartesian pose."""
        # Mock controller with pose data
        mock_controller = Mock()
        mock_controller.get_cartesian_position.return_value = np.array([0.5, 0.0, 0.5])
        mock_controller.get_cartesian_orientation.return_value = np.array(
            [0.0, 0.0, 0.0, 1.0]
        )
        mock_controller.get_timestamp.return_value = 1234567890000000
        mock_controller_class.return_value = mock_controller

        robot = FrankaRobot(self.robot_ip)
        robot._connected = True

        pose = robot.get_cartesian_pose()

        assert isinstance(pose, fp.CartesianPose)
        assert len(pose.position) == 3
        assert len(pose.orientation) == 4
        assert pose.timestamp > 0

    def test_home_position(self):
        """Test home position creation."""
        from libfrankapy.utils import create_home_position

        home_pos = create_home_position()
        assert len(home_pos) == 7
        assert all(isinstance(x, float) for x in home_pos)

    def test_joint_validation(self):
        """Test joint position validation."""
        from libfrankapy.utils import validate_joint_positions

        # Valid positions
        valid_positions = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        assert validate_joint_positions(valid_positions)

        # Invalid number of joints
        assert not validate_joint_positions([0, 1, 2])

        # Positions outside limits
        invalid_positions = [5.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        assert not validate_joint_positions(invalid_positions)

    def test_cartesian_validation(self):
        """Test Cartesian pose validation."""
        from libfrankapy.utils import validate_cartesian_pose

        # Valid pose (7 elements: position + quaternion)
        valid_pose = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0]
        assert validate_cartesian_pose(valid_pose)

        # Valid pose (6 elements: position + Euler angles)
        valid_pose_euler = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
        assert validate_cartesian_pose(valid_pose_euler)

        # Invalid number of elements
        assert not validate_cartesian_pose([0, 1, 2])

        # Position outside workspace
        invalid_pose = [2.0, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0]
        assert not validate_cartesian_pose(invalid_pose)

    def test_quaternion_normalization(self):
        """Test quaternion normalization."""
        from libfrankapy.utils import normalize_quaternion

        # Unnormalized quaternion
        qx, qy, qz, qw = 0.5, 0.5, 0.5, 0.5
        norm_qx, norm_qy, norm_qz, norm_qw = normalize_quaternion(qx, qy, qz, qw)

        # Check normalization
        magnitude = (norm_qx**2 + norm_qy**2 + norm_qz**2 + norm_qw**2) ** 0.5
        assert abs(magnitude - 1.0) < 1e-10

    def test_distance_calculations(self):
        """Test distance calculation utilities."""
        from libfrankapy.utils import compute_cartesian_distance, compute_joint_distance

        # Joint distance
        pos1 = [0.0] * 7
        pos2 = [0.1] * 7
        distance = compute_joint_distance(pos1, pos2)
        expected = (7 * 0.1**2) ** 0.5
        assert abs(distance - expected) < 1e-10

        # Cartesian distance
        pose1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        pose2 = [0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        pos_dist, ori_dist = compute_cartesian_distance(pose1, pose2)
        assert abs(pos_dist - 0.1) < 1e-10


class TestRealtimeConfig:
    """Test cases for RealtimeConfig class."""

    def test_default_config(self):
        """Test default configuration."""
        config = RealtimeConfig()
        assert config.control_frequency == 1000
        assert config.filter_cutoff == 100.0
        assert not config.enable_logging
        assert config.log_frequency == 100

    def test_custom_config(self):
        """Test custom configuration."""
        config = RealtimeConfig(
            control_frequency=500,
            filter_cutoff=50.0,
            enable_logging=True,
            log_frequency=50,
        )
        assert config.control_frequency == 500
        assert config.filter_cutoff == 50.0
        assert config.enable_logging
        assert config.log_frequency == 50

    def test_invalid_config(self):
        """Test invalid configuration parameters."""
        with pytest.raises(ValueError):
            RealtimeConfig(control_frequency=0)

        with pytest.raises(ValueError):
            RealtimeConfig(filter_cutoff=-1.0)

        with pytest.raises(ValueError):
            RealtimeConfig(log_frequency=0)

        with pytest.raises(ValueError):
            RealtimeConfig(control_frequency=100, log_frequency=200)


if __name__ == "__main__":
    pytest.main([__file__])
