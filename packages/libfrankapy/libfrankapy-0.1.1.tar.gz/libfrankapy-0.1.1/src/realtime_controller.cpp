/**
 * @file realtime_controller.cpp
 * @brief Implementation of real-time controller for Franka robot
 */

#include "realtime_controller.hpp"

#include <pthread.h>
#include <sched.h>

#include <Eigen/Dense>
#include <algorithm>
#include <cmath>
#include <iostream>

namespace libfrankapy {

// RealtimeController implementation

RealtimeController::RealtimeController(const std::string& robot_ip)
    : robot_ip_(robot_ip) {
  std::cout << "RealtimeController created for robot: " << robot_ip_
            << std::endl;
}

RealtimeController::~RealtimeController() {
  disconnect();
  std::cout << "RealtimeController destroyed" << std::endl;
}

bool RealtimeController::connect() {
  std::lock_guard<std::mutex> lock(connection_mutex_);

  if (connected_.load()) {
    std::cout << "Already connected to robot" << std::endl;
    return true;
  }

  try {
    // Create shared memory (as creator)
    shared_memory_ = std::make_shared<SharedMemoryManager>(true);

    // Connect to robot
    robot_ = std::make_unique<franka::Robot>(robot_ip_);
    model_ = std::make_unique<franka::Model>(robot_->loadModel());

    // Try to connect to gripper (optional)
    try {
      gripper_ = std::make_unique<franka::Gripper>(robot_ip_);
      std::cout << "Gripper connected successfully" << std::endl;
    } catch (const franka::Exception& e) {
      std::cout << "Gripper not available: " << e.what() << std::endl;
      gripper_.reset();
    }

    // Set default behavior
    robot_->setCollisionBehavior(
        {{20.0, 20.0, 18.0, 18.0, 16.0, 14.0,
          12.0}},  // lower_torque_thresholds_acceleration
        {{20.0, 20.0, 18.0, 18.0, 16.0, 14.0,
          12.0}},  // upper_torque_thresholds_acceleration
        {{20.0, 20.0, 18.0, 18.0, 16.0, 14.0,
          12.0}},  // lower_torque_thresholds_nominal
        {{20.0, 20.0, 18.0, 18.0, 16.0, 14.0,
          12.0}},  // upper_torque_thresholds_nominal
        {{20.0, 20.0, 20.0, 25.0, 25.0,
          25.0}},  // lower_force_thresholds_acceleration
        {{20.0, 20.0, 20.0, 25.0, 25.0,
          25.0}},  // upper_force_thresholds_acceleration
        {{20.0, 20.0, 20.0, 25.0, 25.0,
          25.0}},  // lower_force_thresholds_nominal
        {{20.0, 20.0, 20.0, 25.0, 25.0, 25.0}}
        // upper_force_thresholds_nominal
    );

    // Set joint impedance
    robot_->setJointImpedance({{3000, 3000, 3000, 2500, 2500, 2000, 2000}});

    // Set Cartesian impedance
    robot_->setCartesianImpedance({{3000, 3000, 3000, 300, 300, 300}});

    connected_.store(true);

    // Update shared memory with connection status
    auto shared_data = shared_memory_->get_shared_data();
    shared_data->state.is_connected.store(true);
    shared_data->state.has_error.store(false);
    libfrankapy::shared_memory_utils::update_timestamp(
        shared_data->state.timestamp);

    std::cout << "Successfully connected to robot" << std::endl;
    return true;

  } catch (const franka::Exception& e) {
    handle_robot_error("Failed to connect to robot: " + std::string(e.what()),
                       -1);
    return false;
  } catch (const std::exception& e) {
    handle_robot_error("Connection error: " + std::string(e.what()), -2);
    return false;
  }
}

void RealtimeController::disconnect() {
  std::lock_guard<std::mutex> lock(connection_mutex_);

  if (!connected_.load()) {
    return;
  }

  // Stop control loop first
  stop_control();

  // Update shared memory
  if (shared_memory_) {
    auto shared_data = shared_memory_->get_shared_data();
    shared_data->state.is_connected.store(false);
    shared_data->state.control_mode.store(static_cast<int>(ControlMode::IDLE));
    libfrankapy::shared_memory_utils::update_timestamp(
        shared_data->state.timestamp);
  }

  // Cleanup robot connections
  gripper_.reset();
  model_.reset();
  robot_.reset();

  connected_.store(false);

  std::cout << "Disconnected from robot" << std::endl;
}

bool RealtimeController::is_connected() const { return connected_.load(); }

bool RealtimeController::start_control() {
  if (!connected_.load()) {
    std::cerr << "Cannot start control: not connected to robot" << std::endl;
    return false;
  }

  if (control_running_.load()) {
    std::cout << "Control loop already running" << std::endl;
    return true;
  }

  should_stop_.store(false);
  emergency_stop_requested_.store(false);

  // Start control thread
  control_thread_ =
      std::make_unique<std::thread>(&RealtimeController::control_loop, this);

  // Wait for control loop to start
  std::unique_lock<std::mutex> lock(control_mutex_);
  control_cv_.wait(lock, [this] { return control_running_.load(); });

  std::cout << "Real-time control loop started" << std::endl;
  return true;
}

void RealtimeController::stop_control() {
  if (!control_running_.load()) {
    return;
  }

  should_stop_.store(true);

  if (control_thread_ && control_thread_->joinable()) {
    control_thread_->join();
  }

  control_thread_.reset();

  std::cout << "Real-time control loop stopped" << std::endl;
}

bool RealtimeController::is_control_running() const {
  return control_running_.load();
}

void RealtimeController::emergency_stop() {
  emergency_stop_requested_.store(true);

  if (shared_memory_) {
    auto shared_data = shared_memory_->get_shared_data();
    shared_data->state.emergency_stop.store(true);
    libfrankapy::shared_memory_utils::update_timestamp(
        shared_data->state.timestamp);
  }

  std::cout << "Emergency stop requested" << std::endl;
}

std::shared_ptr<SharedMemoryManager> RealtimeController::get_shared_memory()
    const {
  return shared_memory_;
}

void RealtimeController::control_loop() {
  setup_realtime_thread();

  control_start_time_ = std::chrono::high_resolution_clock::now();
  control_running_.store(true);

  // Notify that control loop has started
  {
    std::lock_guard<std::mutex> lock(control_mutex_);
    control_cv_.notify_all();
  }

  try {
    // Main control loop
    robot_->control([this](const franka::RobotState& robot_state,
                           franka::Duration /* period */)
                        -> franka::JointPositions {
      // Check for stop conditions
      if (should_stop_.load() || emergency_stop_requested_.load()) {
        return franka::MotionFinished(franka::JointPositions(robot_state.q_d));
      }

      // Update shared memory with current state
      update_shared_state(robot_state);

      // Process control commands
      process_control_commands(robot_state);

      // Check safety limits
      if (!check_safety_limits(robot_state)) {
        emergency_stop();
        return franka::MotionFinished(franka::JointPositions(robot_state.q_d));
      }

      // Update control frequency
      update_control_frequency();

      // Return current desired positions (no motion by default)
      return franka::JointPositions(robot_state.q_d);
    });

  } catch (const franka::ControlException& e) {
    handle_robot_error("Control exception: " + std::string(e.what()), -2);
  } catch (const franka::Exception& e) {
    handle_robot_error("Robot exception: " + std::string(e.what()), -3);
  } catch (const std::exception& e) {
    handle_robot_error("Control loop error: " + std::string(e.what()), -4);
  }

  control_running_.store(false);
  std::cout << "Control loop finished" << std::endl;
}

void RealtimeController::setup_realtime_thread() {
  if (!realtime_utils::set_realtime_priority(80)) {
    std::cerr << "Warning: Failed to set real-time priority" << std::endl;
  }
}

void RealtimeController::update_shared_state(
    const franka::RobotState& robot_state) {
  if (!shared_memory_) return;

  auto shared_data = shared_memory_->get_shared_data();
  auto& state = shared_data->state;

  // Update timestamp
  libfrankapy::shared_memory_utils::update_timestamp(state.timestamp);

  // Update joint state
  for (size_t i = 0; i < 7; ++i) {
    state.joint_positions[i].store(robot_state.q[i]);
    state.joint_velocities[i].store(robot_state.dq[i]);
    state.joint_torques[i].store(robot_state.tau_J[i]);
  }

  // Update Cartesian state
  for (size_t i = 0; i < 3; ++i) {
    state.cartesian_position[i].store(robot_state.O_T_EE[12 + i]);
  }

  // Convert rotation matrix to quaternion
  Eigen::Matrix3d rotation;
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      rotation(i, j) = robot_state.O_T_EE[4 * j + i];
    }
  }

  Eigen::Quaterniond quat(rotation);
  state.cartesian_orientation[0].store(quat.x());
  state.cartesian_orientation[1].store(quat.y());
  state.cartesian_orientation[2].store(quat.z());
  state.cartesian_orientation[3].store(quat.w());

  // Update external wrench
  for (size_t i = 0; i < 6; ++i) {
    state.external_wrench[i].store(robot_state.O_F_ext_hat_K[i]);
  }

  // Update control state
  state.control_frequency.store(actual_control_frequency_.load());
  state.is_valid.store(true);

  // Check if robot is moving
  bool moving = false;
  for (size_t i = 0; i < 7; ++i) {
    if (std::abs(robot_state.dq[i]) > 0.01) {
      moving = true;
      break;
    }
  }
  state.is_moving.store(moving);
}

bool RealtimeController::process_control_commands(
    const franka::RobotState& /* robot_state */) {
  if (!shared_memory_) return false;

  auto shared_data = shared_memory_->get_shared_data();
  auto& command = shared_data->command;

  // Check for new command
  if (!command.new_command.load()) {
    return false;
  }

  // Get command ID
  uint64_t command_id = command.command_id.load();
  if (command_id == last_command_id_) {
    return false;  // Already processed this command
  }

  // Validate command
  if (!validate_control_command(command)) {
    command.command_acknowledged.store(true);
    command.new_command.store(false);
    return false;
  }

  // Process command based on type
  ControlMode cmd_type = static_cast<ControlMode>(command.command_type.load());

  try {
    switch (cmd_type) {
      case ControlMode::JOINT_POSITION: {
        std::array<double, 7> target_positions;
        for (size_t i = 0; i < 7; ++i) {
          target_positions[i] = command.target_joint_positions[i].load();
        }
        execute_joint_position_control(
            target_positions, command.joint_speed_factor.load(),
            command.joint_acceleration_factor.load());
        break;
      }

      case ControlMode::CARTESIAN_POSITION: {
        std::array<double, 7> target_pose;
        for (size_t i = 0; i < 3; ++i) {
          target_pose[i] = command.target_cartesian_position[i].load();
        }
        for (size_t i = 0; i < 4; ++i) {
          target_pose[3 + i] = command.target_cartesian_orientation[i].load();
        }
        execute_cartesian_position_control(
            target_pose, command.cartesian_speed_factor.load(),
            static_cast<MotionType>(command.motion_type.load()));
        break;
      }

      case ControlMode::IDLE:
      default:
        // Do nothing for idle mode
        break;
    }

    // Acknowledge command
    last_command_id_ = command_id;
    command.command_acknowledged.store(true);
    command.new_command.store(false);

    return true;

  } catch (const std::exception& e) {
    handle_robot_error("Command execution error: " + std::string(e.what()), -5);
    command.command_acknowledged.store(true);
    command.new_command.store(false);
    return false;
  }
}

void RealtimeController::execute_joint_position_control(
    const std::array<double, 7>& target_positions, double speed_factor,
    double acceleration_factor) {
  JointPositionMotionGenerator motion_generator(target_positions, speed_factor,
                                                acceleration_factor);

  robot_->control(motion_generator);
}

void RealtimeController::execute_cartesian_position_control(
    const std::array<double, 7>& target_pose, double speed_factor,
    MotionType motion_type) {
  // Convert pose to transformation matrix
  std::array<double, 16> target_transform;

  // Set rotation part from quaternion
  double qx = target_pose[3], qy = target_pose[4], qz = target_pose[5],
         qw = target_pose[6];

  target_transform[0] = 1 - 2 * (qy * qy + qz * qz);
  target_transform[1] = 2 * (qx * qy - qz * qw);
  target_transform[2] = 2 * (qx * qz + qy * qw);
  target_transform[3] = 0;

  target_transform[4] = 2 * (qx * qy + qz * qw);
  target_transform[5] = 1 - 2 * (qx * qx + qz * qz);
  target_transform[6] = 2 * (qy * qz - qx * qw);
  target_transform[7] = 0;

  target_transform[8] = 2 * (qx * qz - qy * qw);
  target_transform[9] = 2 * (qy * qz + qx * qw);
  target_transform[10] = 1 - 2 * (qx * qx + qy * qy);
  target_transform[11] = 0;

  // Set translation part
  target_transform[12] = target_pose[0];
  target_transform[13] = target_pose[1];
  target_transform[14] = target_pose[2];
  target_transform[15] = 1;

  CartesianPositionMotionGenerator motion_generator(target_transform,
                                                    speed_factor, motion_type);

  robot_->control(motion_generator);
}

bool RealtimeController::check_safety_limits(
    const franka::RobotState& robot_state) {
  // Check joint limits
  const std::array<double, 7> joint_limits_lower = {
      -2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973};
  const std::array<double, 7> joint_limits_upper = {
      2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973};

  for (size_t i = 0; i < 7; ++i) {
    if (robot_state.q[i] < joint_limits_lower[i] ||
        robot_state.q[i] > joint_limits_upper[i]) {
      handle_robot_error("Joint limit violation on joint " + std::to_string(i),
                         -10);
      return false;
    }
  }

  // Check velocity limits
  const double max_joint_velocity = 2.175;  // rad/s
  for (size_t i = 0; i < 7; ++i) {
    if (std::abs(robot_state.dq[i]) > max_joint_velocity) {
      handle_robot_error(
          "Joint velocity limit violation on joint " + std::to_string(i), -11);
      return false;
    }
  }

  return true;
}

void RealtimeController::handle_robot_error(const std::string& error_message,
                                            int error_code) {
  std::cerr << "Robot error [" << error_code << "]: " << error_message
            << std::endl;

  if (shared_memory_) {
    auto shared_data = shared_memory_->get_shared_data();
    shared_data->state.has_error.store(true);
    shared_data->state.error_code.store(error_code);
    libfrankapy::shared_memory_utils::update_timestamp(
        shared_data->state.timestamp);
  }
}

void RealtimeController::update_control_frequency() {
  static auto last_time = std::chrono::high_resolution_clock::now();
  static int counter = 0;

  counter++;

  if (counter >= 1000) {  // Update every 1000 cycles
    auto current_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
                        current_time - last_time)
                        .count();

    double frequency = 1000000.0 * counter / duration;
    actual_control_frequency_.store(frequency);

    last_time = current_time;
    counter = 0;
  }
}

bool RealtimeController::validate_control_command(
    const ControlCommand& command) {
  // Basic validation - can be extended
  ControlMode cmd_type = static_cast<ControlMode>(command.command_type.load());

  switch (cmd_type) {
    case ControlMode::JOINT_POSITION:
      // Validate joint positions are within limits
      for (size_t i = 0; i < 7; ++i) {
        double pos = command.target_joint_positions[i].load();
        if (std::isnan(pos) || std::isinf(pos)) {
          return false;
        }
      }
      break;

    case ControlMode::CARTESIAN_POSITION:
      // Validate Cartesian pose
      for (size_t i = 0; i < 3; ++i) {
        double pos = command.target_cartesian_position[i].load();
        if (std::isnan(pos) || std::isinf(pos)) {
          return false;
        }
      }
      break;

    default:
      break;
  }

  return true;
}

// Motion generators implementation will be continued in the next part...

}  // namespace libfrankapy
