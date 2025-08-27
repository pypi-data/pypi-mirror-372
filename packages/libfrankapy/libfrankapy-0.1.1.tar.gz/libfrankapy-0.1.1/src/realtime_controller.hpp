/**
 * @file realtime_controller.hpp
 * @brief Real-time controller for Franka robot with shared memory communication
 *
 * This file defines the real-time controller that manages the libfranka control
 * loop while communicating with Python through shared memory.
 */

#pragma once

#include <franka/exception.h>
#include <franka/gripper.h>
#include <franka/model.h>
#include <franka/robot.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <thread>

#include "shared_memory.hpp"

namespace libfrankapy {

/**
 * @brief Real-time controller for Franka robot
 *
 * This class manages the real-time control loop for the Franka robot,
 * handling communication between the Python interface and libfranka.
 */
class RealtimeController {
 public:
  /**
   * @brief Constructor
   * @param robot_ip IP address of the Franka robot
   */
  explicit RealtimeController(const std::string& robot_ip);

  /**
   * @brief Destructor
   */
  ~RealtimeController();

  /**
   * @brief Connect to the robot and initialize shared memory
   * @return true if connection successful, false otherwise
   */
  bool connect();

  /**
   * @brief Disconnect from robot and cleanup
   */
  void disconnect();

  /**
   * @brief Check if controller is connected to robot
   * @return true if connected, false otherwise
   */
  bool is_connected() const;

  /**
   * @brief Start the real-time control loop
   * @return true if started successfully, false otherwise
   */
  bool start_control();

  /**
   * @brief Stop the real-time control loop
   */
  void stop_control();

  /**
   * @brief Check if control loop is running
   * @return true if running, false otherwise
   */
  bool is_control_running() const;

  /**
   * @brief Emergency stop - immediately halt all motion
   */
  void emergency_stop();

  /**
   * @brief Get shared memory manager
   * @return pointer to shared memory manager
   */
  std::shared_ptr<SharedMemoryManager> get_shared_memory() const;

 private:
  // Robot connection
  std::string robot_ip_;
  std::unique_ptr<franka::Robot> robot_;
  std::unique_ptr<franka::Model> model_;
  std::unique_ptr<franka::Gripper> gripper_;

  // Shared memory
  std::shared_ptr<SharedMemoryManager> shared_memory_;

  // Control thread management
  std::unique_ptr<std::thread> control_thread_;
  std::atomic<bool> control_running_{false};
  std::atomic<bool> should_stop_{false};
  std::atomic<bool> emergency_stop_requested_{false};

  // Synchronization
  mutable std::mutex connection_mutex_;
  std::condition_variable control_cv_;
  std::mutex control_mutex_;

  // Control state
  std::atomic<bool> connected_{false};
  ControlMode current_control_mode_{ControlMode::IDLE};
  uint64_t last_command_id_{0};

  // Timing
  std::chrono::high_resolution_clock::time_point control_start_time_;
  std::atomic<double> actual_control_frequency_{0.0};

  /**
   * @brief Main control loop function (runs in separate thread)
   */
  void control_loop();

  /**
   * @brief Initialize real-time thread settings
   */
  void setup_realtime_thread();

  /**
   * @brief Update robot state in shared memory
   * @param robot_state Current robot state from libfranka
   */
  void update_shared_state(const franka::RobotState& robot_state);

  /**
   * @brief Process control commands from shared memory
   * @param robot_state Current robot state
   * @return true if new command was processed
   */
  bool process_control_commands(const franka::RobotState& robot_state);

  /**
   * @brief Execute joint position control
   * @param target_positions Target joint positions
   * @param speed_factor Speed scaling factor
   * @param acceleration_factor Acceleration scaling factor
   */
  void execute_joint_position_control(
      const std::array<double, 7>& target_positions, double speed_factor,
      double acceleration_factor);

  /**
   * @brief Execute Cartesian position control
   * @param target_pose Target Cartesian pose [x, y, z, qx, qy, qz, qw]
   * @param speed_factor Speed scaling factor
   * @param motion_type Type of motion (linear, joint-interpolated)
   */
  void execute_cartesian_position_control(
      const std::array<double, 7>& target_pose, double speed_factor,
      MotionType motion_type);

  /**
   * @brief Check safety limits
   * @param robot_state Current robot state
   * @return true if within limits, false if violation detected
   */
  bool check_safety_limits(const franka::RobotState& robot_state);

  /**
   * @brief Handle robot errors and exceptions
   * @param error_message Error description
   * @param error_code Error code
   */
  void handle_robot_error(const std::string& error_message, int error_code = 0);

  /**
   * @brief Convert franka::RobotState to our shared memory format
   * @param franka_state Robot state from libfranka
   * @param shared_state Our shared memory state structure
   */
  void convert_robot_state(const franka::RobotState& franka_state,
                           RealtimeState& shared_state);

  /**
   * @brief Calculate control frequency
   */
  void update_control_frequency();

  /**
   * @brief Validate control command parameters
   * @param command Control command to validate
   * @return true if valid, false otherwise
   */
  bool validate_control_command(const ControlCommand& command);
};

/**
 * @brief Motion generator for joint position control
 */
class JointPositionMotionGenerator {
 public:
  JointPositionMotionGenerator(const std::array<double, 7>& target_positions,
                               double speed_factor = 0.1,
                               double acceleration_factor = 0.1);

  franka::JointPositions operator()(const franka::RobotState& robot_state,
                                    franka::Duration period);

  bool is_finished() const { return finished_; }

 private:
  std::array<double, 7> target_positions_;
  std::array<double, 7> initial_positions_;
  double speed_factor_;
  double acceleration_factor_;
  double time_;
  double total_time_;
  bool initialized_;
  bool finished_;

  void calculate_trajectory_time(
      const std::array<double, 7>& current_positions);
};

/**
 * @brief Motion generator for Cartesian position control
 */
class CartesianPositionMotionGenerator {
 public:
  CartesianPositionMotionGenerator(const std::array<double, 16>& target_pose,
                                   double speed_factor = 0.1,
                                   MotionType motion_type = MotionType::LINEAR);

  franka::CartesianPose operator()(const franka::RobotState& robot_state,
                                   franka::Duration period);

  bool is_finished() const { return finished_; }

 private:
  std::array<double, 16> target_pose_;
  std::array<double, 16> initial_pose_;
  double speed_factor_;
  MotionType motion_type_;
  double time_;
  double total_time_;
  bool initialized_;
  bool finished_;

  void calculate_trajectory_time(const std::array<double, 16>& current_pose);
  std::array<double, 16> interpolate_pose(const std::array<double, 16>& start,
                                          const std::array<double, 16>& end,
                                          double t);
};

/**
 * @brief Utility functions for real-time control
 */
namespace realtime_utils {

/**
 * @brief Set real-time thread priority
 * @param priority Priority level (1-99, higher is more priority)
 * @return true if successful, false otherwise
 */
bool set_realtime_priority(int priority = 80);

/**
 * @brief Convert Eigen matrix to std::array
 */
template <typename T, size_t N>
std::array<T, N> eigen_to_array(const Eigen::Matrix<T, N, 1>& eigen_vec) {
  std::array<T, N> result;
  for (size_t i = 0; i < N; ++i) {
    result[i] = eigen_vec[i];
  }
  return result;
}

/**
 * @brief Convert std::array to Eigen matrix
 */
template <typename T, size_t N>
Eigen::Matrix<T, N, 1> array_to_eigen(const std::array<T, N>& array) {
  Eigen::Matrix<T, N, 1> result;
  for (size_t i = 0; i < N; ++i) {
    result[i] = array[i];
  }
  return result;
}

/**
 * @brief Calculate joint space distance
 */
double calculate_joint_distance(const std::array<double, 7>& pos1,
                                const std::array<double, 7>& pos2);

/**
 * @brief Calculate Cartesian space distance
 */
double calculate_cartesian_distance(const std::array<double, 16>& pose1,
                                    const std::array<double, 16>& pose2);

/**
 * @brief Clamp value between min and max
 */
template <typename T>
T clamp(T value, T min_val, T max_val) {
  return std::max(min_val, std::min(value, max_val));
}

}  // namespace realtime_utils

}  // namespace libfrankapy
