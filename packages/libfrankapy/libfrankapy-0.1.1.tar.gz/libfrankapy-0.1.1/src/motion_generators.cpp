/**
 * @file motion_generators.cpp
 * @brief Implementation of motion generators for joint and Cartesian control
 */

#include <pthread.h>
#include <sys/mman.h>

#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <iostream>

#include "realtime_controller.hpp"

namespace libfrankapy {

// JointPositionMotionGenerator implementation

JointPositionMotionGenerator::JointPositionMotionGenerator(
    const std::array<double, 7>& target_positions, double speed_factor,
    double acceleration_factor)
    : target_positions_(target_positions),
      speed_factor_(speed_factor),
      acceleration_factor_(acceleration_factor),
      time_(0.0),
      total_time_(0.0),
      initialized_(false),
      finished_(false) {
  // Clamp factors to valid range
  speed_factor_ = realtime_utils::clamp(speed_factor_, 0.01, 1.0);
  acceleration_factor_ = realtime_utils::clamp(acceleration_factor_, 0.01, 1.0);
}

franka::JointPositions JointPositionMotionGenerator::operator()(
    const franka::RobotState& robot_state, franka::Duration period) {
  if (!initialized_) {
    initial_positions_ = robot_state.q;
    calculate_trajectory_time(initial_positions_);
    initialized_ = true;
    std::cout << "Joint motion initialized, duration: " << total_time_ << "s"
              << std::endl;
  }

  if (finished_) {
    return franka::MotionFinished(franka::JointPositions(target_positions_));
  }

  time_ += period.toSec();

  if (time_ >= total_time_) {
    finished_ = true;
    return franka::MotionFinished(franka::JointPositions(target_positions_));
  }

  // Smooth trajectory using quintic polynomial
  double t_normalized = time_ / total_time_;
  double s = 10 * std::pow(t_normalized, 3) - 15 * std::pow(t_normalized, 4) +
             6 * std::pow(t_normalized, 5);

  std::array<double, 7> desired_positions;
  for (size_t i = 0; i < 7; ++i) {
    desired_positions[i] = initial_positions_[i] +
                           s * (target_positions_[i] - initial_positions_[i]);
  }

  return franka::JointPositions(desired_positions);
}

void JointPositionMotionGenerator::calculate_trajectory_time(
    const std::array<double, 7>& current_positions) {
  // Calculate maximum joint displacement
  double max_displacement = 0.0;
  for (size_t i = 0; i < 7; ++i) {
    double displacement = std::abs(target_positions_[i] - current_positions[i]);
    max_displacement = std::max(max_displacement, displacement);
  }

  // Base time calculation on maximum displacement and speed factor
  // Assume maximum joint velocity of 2.0 rad/s at full speed
  double max_velocity = 2.0 * speed_factor_;

  // Calculate time needed for the motion
  total_time_ = max_displacement / max_velocity;

  // Apply acceleration factor (longer time for smoother motion)
  total_time_ /= acceleration_factor_;

  // Minimum time constraint
  total_time_ = std::max(total_time_, 0.5);

  // Maximum time constraint
  total_time_ = std::min(total_time_, 30.0);
}

// CartesianPositionMotionGenerator implementation

CartesianPositionMotionGenerator::CartesianPositionMotionGenerator(
    const std::array<double, 16>& target_pose, double speed_factor,
    MotionType motion_type)
    : target_pose_(target_pose),
      speed_factor_(speed_factor),
      motion_type_(motion_type),
      time_(0.0),
      total_time_(0.0),
      initialized_(false),
      finished_(false) {
  // Clamp speed factor to valid range
  speed_factor_ = realtime_utils::clamp(speed_factor_, 0.01, 1.0);
}

franka::CartesianPose CartesianPositionMotionGenerator::operator()(
    const franka::RobotState& robot_state, franka::Duration period) {
  if (!initialized_) {
    initial_pose_ = robot_state.O_T_EE;
    calculate_trajectory_time(initial_pose_);
    initialized_ = true;
    std::cout << "Cartesian motion initialized, duration: " << total_time_
              << "s" << std::endl;
  }

  if (finished_) {
    return franka::MotionFinished(franka::CartesianPose(target_pose_));
  }

  time_ += period.toSec();

  if (time_ >= total_time_) {
    finished_ = true;
    return franka::MotionFinished(franka::CartesianPose(target_pose_));
  }

  // Interpolate pose
  double t_normalized = time_ / total_time_;
  std::array<double, 16> desired_pose =
      interpolate_pose(initial_pose_, target_pose_, t_normalized);

  return franka::CartesianPose(desired_pose);
}

void CartesianPositionMotionGenerator::calculate_trajectory_time(
    const std::array<double, 16>& current_pose) {
  // Calculate position distance
  double position_distance = 0.0;
  for (size_t i = 0; i < 3; ++i) {
    double diff = target_pose_[12 + i] - current_pose[12 + i];
    position_distance += diff * diff;
  }
  position_distance = std::sqrt(position_distance);

  // Calculate orientation distance (simplified)
  double orientation_distance = 0.0;
  for (size_t i = 0; i < 9; ++i) {
    if (i % 4 != 3) {  // Skip the last column
      double diff = target_pose_[i] - current_pose[i];
      orientation_distance += diff * diff;
    }
  }
  orientation_distance = std::sqrt(orientation_distance);

  // Base time calculation
  double max_linear_velocity = 0.5 * speed_factor_;   // m/s
  double max_angular_velocity = 1.0 * speed_factor_;  // rad/s

  double time_for_position = position_distance / max_linear_velocity;
  double time_for_orientation = orientation_distance / max_angular_velocity;

  total_time_ = std::max(time_for_position, time_for_orientation);

  // Constraints
  total_time_ = std::max(total_time_, 0.5);
  total_time_ = std::min(total_time_, 30.0);
}

std::array<double, 16> CartesianPositionMotionGenerator::interpolate_pose(
    const std::array<double, 16>& start, const std::array<double, 16>& end,
    double t) {
  // Smooth interpolation using quintic polynomial
  double s = 10 * std::pow(t, 3) - 15 * std::pow(t, 4) + 6 * std::pow(t, 5);

  std::array<double, 16> result;

  if (motion_type_ == MotionType::LINEAR) {
    // Linear interpolation for position
    for (size_t i = 12; i < 15; ++i) {
      result[i] = start[i] + s * (end[i] - start[i]);
    }
    result[15] = 1.0;

    // SLERP for orientation (simplified - using matrix interpolation)
    for (size_t i = 0; i < 12; ++i) {
      if (i % 4 != 3) {
        result[i] = start[i] + s * (end[i] - start[i]);
      } else {
        result[i] = 0.0;
      }
    }
    result[3] = result[7] = result[11] = 0.0;

  } else {
    // Joint-interpolated motion (simplified)
    for (size_t i = 0; i < 16; ++i) {
      if (i == 15) {
        result[i] = 1.0;
      } else if (i % 4 == 3 && i < 12) {
        result[i] = 0.0;
      } else {
        result[i] = start[i] + s * (end[i] - start[i]);
      }
    }
  }

  return result;
}

// Utility functions implementation

namespace realtime_utils {

bool set_realtime_priority(int priority) {
  struct sched_param param;
  param.sched_priority = priority;

  if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
    std::cerr << "Failed to set real-time priority: " << strerror(errno)
              << std::endl;
    return false;
  }

  // Lock memory to prevent page faults
  if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
    std::cerr << "Warning: Failed to lock memory: " << strerror(errno)
              << std::endl;
  }

  return true;
}

double calculate_joint_distance(const std::array<double, 7>& pos1,
                                const std::array<double, 7>& pos2) {
  double distance = 0.0;
  for (size_t i = 0; i < 7; ++i) {
    double diff = pos1[i] - pos2[i];
    distance += diff * diff;
  }
  return std::sqrt(distance);
}

double calculate_cartesian_distance(const std::array<double, 16>& pose1,
                                    const std::array<double, 16>& pose2) {
  // Position distance
  double pos_distance = 0.0;
  for (size_t i = 12; i < 15; ++i) {
    double diff = pose1[i] - pose2[i];
    pos_distance += diff * diff;
  }

  return std::sqrt(pos_distance);
}

}  // namespace realtime_utils

}  // namespace libfrankapy
