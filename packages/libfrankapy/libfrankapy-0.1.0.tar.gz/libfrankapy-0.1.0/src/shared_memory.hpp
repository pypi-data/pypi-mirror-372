/**
 * @file shared_memory.hpp
 * @brief Shared memory data structures for real-time communication between
 * Python and C++
 *
 * This file defines atomic data structures used for communication between the
 * Python high-level interface and the C++ real-time control loop through shared
 * memory.
 */

#pragma once

#include <Eigen/Dense>
#include <array>
#include <atomic>
#include <cstdint>
#include <memory>
#include <string>

namespace libfrankapy {

// Forward declaration
class SharedMemoryManager;

/**
 * @brief Control modes for robot operation
 */
enum class ControlMode : int {
  IDLE = 0,
  JOINT_POSITION = 1,
  CARTESIAN_POSITION = 2,
  JOINT_VELOCITY = 3,
  CARTESIAN_VELOCITY = 4,
  TORQUE = 5,
  TRAJECTORY = 6
};

/**
 * @brief Motion types for Cartesian control
 */
enum class MotionType : int {
  LINEAR = 0,
  JOINT_INTERPOLATED = 1,
  CIRCULAR = 2
};

/**
 * @brief Real-time robot state data structure
 *
 * This structure contains all robot state information that is continuously
 * updated by the real-time control loop and read by the Python interface.
 * All members are atomic to ensure thread-safe access.
 */
struct RealtimeState {
  // Timestamp and validity
  std::atomic<uint64_t> timestamp{0};
  std::atomic<bool> is_valid{false};

  // Joint state (7 DOF)
  std::array<std::atomic<double>, 7> joint_positions;
  std::array<std::atomic<double>, 7> joint_velocities;
  std::array<std::atomic<double>, 7> joint_torques;

  // Cartesian state
  std::array<std::atomic<double>, 3> cartesian_position;     // [x, y, z]
  std::array<std::atomic<double>, 4> cartesian_orientation;  // [qx, qy, qz, qw]
  std::array<std::atomic<double>, 3> cartesian_velocity;     // [vx, vy, vz]
  std::array<std::atomic<double>, 3>
      cartesian_angular_velocity;  // [wx, wy, wz]

  // External forces and torques
  std::array<std::atomic<double>, 6>
      external_wrench;  // [fx, fy, fz, tx, ty, tz]

  // Control state
  std::atomic<int> control_mode{static_cast<int>(ControlMode::IDLE)};
  std::atomic<bool> emergency_stop{false};
  std::atomic<bool> is_moving{false};
  std::atomic<double> control_frequency{1000.0};

  // Robot status
  std::atomic<bool> is_connected{false};
  std::atomic<bool> has_error{false};
  std::atomic<int> error_code{0};

  /**
   * @brief Initialize all atomic variables to default values
   */
  RealtimeState() {
    // Initialize joint arrays
    for (size_t i = 0; i < 7; ++i) {
      joint_positions[i].store(0.0);
      joint_velocities[i].store(0.0);
      joint_torques[i].store(0.0);
    }

    // Initialize Cartesian arrays
    for (size_t i = 0; i < 3; ++i) {
      cartesian_position[i].store(0.0);
      cartesian_velocity[i].store(0.0);
      cartesian_angular_velocity[i].store(0.0);
    }

    // Initialize quaternion to identity
    cartesian_orientation[0].store(0.0);  // qx
    cartesian_orientation[1].store(0.0);  // qy
    cartesian_orientation[2].store(0.0);  // qz
    cartesian_orientation[3].store(1.0);  // qw

    // Initialize external wrench
    for (size_t i = 0; i < 6; ++i) {
      external_wrench[i].store(0.0);
    }
  }
};

/**
 * @brief Control command data structure
 *
 * This structure contains commands sent from Python to the C++ real-time
 * control loop. All members are atomic to ensure thread-safe access.
 */
struct ControlCommand {
  // Command metadata
  std::atomic<uint64_t> command_id{0};
  std::atomic<int> command_type{static_cast<int>(ControlMode::IDLE)};
  std::atomic<bool> new_command{false};
  std::atomic<bool> command_acknowledged{false};
  std::atomic<uint64_t> timestamp{0};

  // Joint control commands
  std::array<std::atomic<double>, 7> target_joint_positions;
  std::array<std::atomic<double>, 7> target_joint_velocities;
  std::atomic<double> joint_speed_factor{0.1};
  std::atomic<double> joint_acceleration_factor{0.1};

  // Cartesian control commands
  std::array<std::atomic<double>, 3> target_cartesian_position;
  std::array<std::atomic<double>, 4> target_cartesian_orientation;
  std::array<std::atomic<double>, 3> target_cartesian_velocity;
  std::atomic<double> cartesian_speed_factor{0.1};
  std::atomic<int> motion_type{static_cast<int>(MotionType::LINEAR)};

  // Trajectory control
  std::atomic<uint64_t> trajectory_id{0};
  std::atomic<bool> trajectory_active{false};

  // Safety and control parameters
  std::atomic<double> timeout{30.0};
  std::atomic<bool> enable_safety_limits{true};
  std::atomic<bool> stop_command{false};

  /**
   * @brief Initialize all atomic variables to default values
   */
  ControlCommand() {
    // Initialize joint arrays
    for (size_t i = 0; i < 7; ++i) {
      target_joint_positions[i].store(0.0);
      target_joint_velocities[i].store(0.0);
    }

    // Initialize Cartesian arrays
    for (size_t i = 0; i < 3; ++i) {
      target_cartesian_position[i].store(0.0);
      target_cartesian_velocity[i].store(0.0);
    }

    // Initialize quaternion to identity
    target_cartesian_orientation[0].store(0.0);  // qx
    target_cartesian_orientation[1].store(0.0);  // qy
    target_cartesian_orientation[2].store(0.0);  // qz
    target_cartesian_orientation[3].store(1.0);  // qw
  }
};

/**
 * @brief Configuration for real-time control
 */
struct RealtimeConfig {
  std::atomic<int> control_frequency{1000};  // Hz
  std::atomic<double> filter_cutoff{100.0};  // Hz
  std::atomic<bool> enable_logging{false};
  std::atomic<int> log_frequency{100};  // Hz

  // Safety limits
  std::array<std::atomic<double>, 7> max_joint_velocity;
  std::array<std::atomic<double>, 7> max_joint_acceleration;
  std::array<std::atomic<double>, 6> max_cartesian_velocity;
  std::array<std::atomic<double>, 6> max_cartesian_acceleration;
  std::array<std::atomic<double>, 3> max_force;
  std::array<std::atomic<double>, 3> max_torque;
  std::atomic<double> collision_threshold{20.0};

  /**
   * @brief Initialize configuration with default safety limits
   */
  RealtimeConfig() {
    // Default joint velocity limits (rad/s)
    for (size_t i = 0; i < 7; ++i) {
      max_joint_velocity[i].store(2.175);
      max_joint_acceleration[i].store(15.0);
    }

    // Default Cartesian velocity limits
    max_cartesian_velocity[0].store(1.7);  // vx
    max_cartesian_velocity[1].store(1.7);  // vy
    max_cartesian_velocity[2].store(1.7);  // vz
    max_cartesian_velocity[3].store(2.5);  // wx
    max_cartesian_velocity[4].store(2.5);  // wy
    max_cartesian_velocity[5].store(2.5);  // wz

    // Default Cartesian acceleration limits
    max_cartesian_acceleration[0].store(13.0);  // ax
    max_cartesian_acceleration[1].store(13.0);  // ay
    max_cartesian_acceleration[2].store(13.0);  // az
    max_cartesian_acceleration[3].store(25.0);  // alpha_x
    max_cartesian_acceleration[4].store(25.0);  // alpha_y
    max_cartesian_acceleration[5].store(25.0);  // alpha_z

    // Default force/torque limits
    for (size_t i = 0; i < 3; ++i) {
      max_force[i].store(20.0);   // N
      max_torque[i].store(25.0);  // Nm
    }
  }
};

/**
 * @brief Shared memory segment containing all communication data
 */
struct SharedMemorySegment {
  RealtimeState state;
  ControlCommand command;
  RealtimeConfig config;

  // Synchronization
  std::atomic<bool> initialized{false};
  std::atomic<uint64_t> sequence_number{0};
};

/**
 * @brief Shared memory manager class
 */
class SharedMemoryManager {
 public:
  static constexpr const char* SHM_NAME = "/libfrankapy_shared_memory";
  static constexpr size_t SHM_SIZE = sizeof(SharedMemorySegment);

  /**
   * @brief Constructor - creates or opens shared memory segment
   * @param create_new If true, creates new segment; if false, opens existing
   */
  explicit SharedMemoryManager(bool create_new = false);

  /**
   * @brief Destructor - cleans up shared memory
   */
  ~SharedMemoryManager();

  /**
   * @brief Get pointer to shared memory segment
   */
  SharedMemorySegment* get_shared_data();

  /**
   * @brief Check if shared memory is properly initialized
   */
  bool is_initialized() const;

  /**
   * @brief Update sequence number for synchronization
   */
  void increment_sequence();

  /**
   * @brief Get current sequence number
   */
  uint64_t get_sequence() const;

 private:
  int shm_fd_;
  SharedMemorySegment* shared_data_;
  bool is_creator_;
};

/**
 * @brief Utility functions for working with shared memory data
 */
namespace shared_memory_utils {

/**
 * @brief Copy joint positions from array to atomic array
 */
void set_joint_positions(std::array<std::atomic<double>, 7>& atomic_array,
                         const std::array<double, 7>& values);

/**
 * @brief Copy joint positions from atomic array to regular array
 */
std::array<double, 7> get_joint_positions(
    const std::array<std::atomic<double>, 7>& atomic_array);

/**
 * @brief Copy Cartesian position from array to atomic array
 */
void set_cartesian_position(std::array<std::atomic<double>, 3>& atomic_array,
                            const std::array<double, 3>& values);

/**
 * @brief Copy Cartesian position from atomic array to regular array
 */
std::array<double, 3> get_cartesian_position(
    const std::array<std::atomic<double>, 3>& atomic_array);

/**
 * @brief Copy quaternion from array to atomic array
 */
void set_quaternion(std::array<std::atomic<double>, 4>& atomic_array,
                    const std::array<double, 4>& values);

/**
 * @brief Copy quaternion from atomic array to regular array
 */
std::array<double, 4> get_quaternion(
    const std::array<std::atomic<double>, 4>& atomic_array);

/**
 * @brief Get current timestamp in microseconds
 */
uint64_t get_current_timestamp();

/**
 * @brief Update timestamp in shared memory structure
 */
void update_timestamp(std::atomic<uint64_t>& timestamp);

/**
 * @brief Check if timestamp is recent (within timeout)
 */
bool is_timestamp_recent(uint64_t timestamp, uint64_t timeout_us = 1000000);

}  // namespace shared_memory_utils

}  // namespace libfrankapy
