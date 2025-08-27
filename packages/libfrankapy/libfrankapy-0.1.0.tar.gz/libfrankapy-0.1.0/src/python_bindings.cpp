/**
 * @file python_bindings.cpp
 * @brief Pybind11 bindings for libfrankapy
 *
 * This file defines the Python bindings for the C++ real-time controller
 * and shared memory communication system.
 */

#include <pybind11/chrono.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "realtime_controller.hpp"
#include "shared_memory.hpp"

namespace py = pybind11;
using namespace py::literals;

namespace libfrankapy {

/**
 * @brief Python wrapper for RealtimeController
 *
 * This class provides a Python-friendly interface to the C++ RealtimeController
 * while maintaining the real-time performance of the underlying system.
 */
class PyRealtimeController {
 public:
  PyRealtimeController(const std::string& robot_ip) : controller_(robot_ip) {}

  bool connect() { return controller_.connect(); }

  void disconnect() { controller_.disconnect(); }

  bool is_connected() const { return controller_.is_connected(); }

  bool start_control() { return controller_.start_control(); }

  void stop_control() { controller_.stop_control(); }

  bool is_control_running() const { return controller_.is_control_running(); }

  void emergency_stop() { controller_.emergency_stop(); }

  // State query methods
  py::array_t<double> get_joint_positions() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    auto positions = libfrankapy::shared_memory_utils::get_joint_positions(
        shared_data->state.joint_positions);

    return py::cast(positions);
  }

  py::array_t<double> get_joint_velocities() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    std::array<double, 7> velocities;
    for (size_t i = 0; i < 7; ++i) {
      velocities[i] = shared_data->state.joint_velocities[i].load();
    }

    return py::cast(velocities);
  }

  py::array_t<double> get_joint_torques() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    std::array<double, 7> torques;
    for (size_t i = 0; i < 7; ++i) {
      torques[i] = shared_data->state.joint_torques[i].load();
    }

    return py::cast(torques);
  }

  py::array_t<double> get_cartesian_position() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    auto position = libfrankapy::shared_memory_utils::get_cartesian_position(
        shared_data->state.cartesian_position);

    return py::cast(position);
  }

  py::array_t<double> get_cartesian_orientation() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    auto orientation = libfrankapy::shared_memory_utils::get_quaternion(
        shared_data->state.cartesian_orientation);

    return py::cast(orientation);
  }

  py::array_t<double> get_external_wrench() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    auto shared_data = shared_memory->get_shared_data();
    std::array<double, 6> wrench;
    for (size_t i = 0; i < 6; ++i) {
      wrench[i] = shared_data->state.external_wrench[i].load();
    }

    return py::cast(wrench);
  }

  bool is_moving() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return false;
    }

    auto shared_data = shared_memory->get_shared_data();
    return shared_data->state.is_moving.load();
  }

  bool has_error() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return true;
    }

    auto shared_data = shared_memory->get_shared_data();
    return shared_data->state.has_error.load();
  }

  int get_error_code() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return -999;
    }

    auto shared_data = shared_memory->get_shared_data();
    return shared_data->state.error_code.load();
  }

  double get_control_frequency() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return 0.0;
    }

    auto shared_data = shared_memory->get_shared_data();
    return shared_data->state.control_frequency.load();
  }

  uint64_t get_timestamp() {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return 0;
    }

    auto shared_data = shared_memory->get_shared_data();
    return shared_data->state.timestamp.load();
  }

  // Control command methods
  bool send_joint_position_command(const py::array_t<double>& target_positions,
                                   double speed_factor = 0.1,
                                   double acceleration_factor = 0.1,
                                   double timeout = 30.0) {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    // Validate input
    if (target_positions.size() != 7) {
      throw std::invalid_argument("target_positions must have 7 elements");
    }

    auto shared_data = shared_memory->get_shared_data();
    auto& command = shared_data->command;

    // Wait for previous command to be acknowledged
    auto start_time = std::chrono::steady_clock::now();
    while (command.new_command.load()) {
      auto current_time = std::chrono::steady_clock::now();
      auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                         current_time - start_time)
                         .count();
      if (elapsed > 1000) {  // 1 second timeout
        return false;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    // Set command parameters
    static uint64_t command_counter = 0;
    command.command_id.store(++command_counter);
    command.command_type.store(static_cast<int>(ControlMode::JOINT_POSITION));

    // Set target positions
    auto positions_ptr = target_positions.unchecked<1>();
    for (size_t i = 0; i < 7; ++i) {
      command.target_joint_positions[i].store(positions_ptr(i));
    }

    command.joint_speed_factor.store(speed_factor);
    command.joint_acceleration_factor.store(acceleration_factor);
    command.timeout.store(timeout);

    libfrankapy::shared_memory_utils::update_timestamp(command.timestamp);
    command.command_acknowledged.store(false);
    command.new_command.store(true);

    return true;
  }

  bool send_cartesian_position_command(
      const py::array_t<double>& target_position,
      const py::array_t<double>& target_orientation, double speed_factor = 0.1,
      int motion_type = 0,  // LINEAR
      double timeout = 30.0) {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      throw std::runtime_error("Shared memory not available");
    }

    // Validate input
    if (target_position.size() != 3) {
      throw std::invalid_argument("target_position must have 3 elements");
    }
    if (target_orientation.size() != 4) {
      throw std::invalid_argument(
          "target_orientation must have 4 elements (quaternion)");
    }

    auto shared_data = shared_memory->get_shared_data();
    auto& command = shared_data->command;

    // Wait for previous command to be acknowledged
    auto start_time = std::chrono::steady_clock::now();
    while (command.new_command.load()) {
      auto current_time = std::chrono::steady_clock::now();
      auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                         current_time - start_time)
                         .count();
      if (elapsed > 1000) {  // 1 second timeout
        return false;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    // Set command parameters
    static uint64_t command_counter = 0;
    command.command_id.store(++command_counter);
    command.command_type.store(
        static_cast<int>(ControlMode::CARTESIAN_POSITION));

    // Set target position
    auto position_ptr = target_position.unchecked<1>();
    for (size_t i = 0; i < 3; ++i) {
      command.target_cartesian_position[i].store(position_ptr(i));
    }

    // Set target orientation
    auto orientation_ptr = target_orientation.unchecked<1>();
    for (size_t i = 0; i < 4; ++i) {
      command.target_cartesian_orientation[i].store(orientation_ptr(i));
    }

    command.cartesian_speed_factor.store(speed_factor);
    command.motion_type.store(motion_type);
    command.timeout.store(timeout);

    libfrankapy::shared_memory_utils::update_timestamp(command.timestamp);
    command.command_acknowledged.store(false);
    command.new_command.store(true);

    return true;
  }

  bool wait_for_command_completion(double timeout = 30.0) {
    auto shared_memory = controller_.get_shared_memory();
    if (!shared_memory) {
      return false;
    }

    auto shared_data = shared_memory->get_shared_data();

    auto start_time = std::chrono::steady_clock::now();
    while (shared_data->state.is_moving.load()) {
      auto current_time = std::chrono::steady_clock::now();
      auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                         current_time - start_time)
                         .count();
      if (elapsed > timeout) {
        return false;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    return true;
  }

 private:
  RealtimeController controller_;
};

/**
 * @brief Python wrapper for SharedMemoryManager (read-only access)
 */
class PySharedMemoryReader {
 public:
  PySharedMemoryReader() : shared_memory_(false) {}

  bool connect() {
    try {
      shared_memory_ = SharedMemoryManager(false);  // Open existing
      return true;
    } catch (const std::exception& e) {
      return false;
    }
  }

  bool is_connected() { return shared_memory_.is_initialized(); }

  py::dict get_robot_state() {
    if (!shared_memory_.is_initialized()) {
      throw std::runtime_error("Not connected to shared memory");
    }

    auto shared_data = shared_memory_.get_shared_data();
    auto& state = shared_data->state;

    py::dict result;

    // Joint state
    std::vector<double> joint_positions(7), joint_velocities(7),
        joint_torques(7);
    for (size_t i = 0; i < 7; ++i) {
      joint_positions[i] = state.joint_positions[i].load();
      joint_velocities[i] = state.joint_velocities[i].load();
      joint_torques[i] = state.joint_torques[i].load();
    }

    result["joint_positions"] = joint_positions;
    result["joint_velocities"] = joint_velocities;
    result["joint_torques"] = joint_torques;

    // Cartesian state
    std::vector<double> cartesian_position(3), cartesian_orientation(4);
    for (size_t i = 0; i < 3; ++i) {
      cartesian_position[i] = state.cartesian_position[i].load();
    }
    for (size_t i = 0; i < 4; ++i) {
      cartesian_orientation[i] = state.cartesian_orientation[i].load();
    }

    result["cartesian_position"] = cartesian_position;
    result["cartesian_orientation"] = cartesian_orientation;

    // External wrench
    std::vector<double> external_wrench(6);
    for (size_t i = 0; i < 6; ++i) {
      external_wrench[i] = state.external_wrench[i].load();
    }
    result["external_wrench"] = external_wrench;

    // Status
    result["is_connected"] = state.is_connected.load();
    result["is_moving"] = state.is_moving.load();
    result["has_error"] = state.has_error.load();
    result["error_code"] = state.error_code.load();
    result["control_frequency"] = state.control_frequency.load();
    result["timestamp"] = state.timestamp.load();

    return result;
  }

 private:
  SharedMemoryManager shared_memory_;
};

}  // namespace libfrankapy

// Pybind11 module definition
PYBIND11_MODULE(_libfrankapy_core, m) {
  m.doc() = "libfrankapy core C++ bindings";

  // Enums
  py::enum_<libfrankapy::ControlMode>(m, "ControlMode")
      .value("IDLE", libfrankapy::ControlMode::IDLE)
      .value("JOINT_POSITION", libfrankapy::ControlMode::JOINT_POSITION)
      .value("CARTESIAN_POSITION", libfrankapy::ControlMode::CARTESIAN_POSITION)
      .value("JOINT_VELOCITY", libfrankapy::ControlMode::JOINT_VELOCITY)
      .value("CARTESIAN_VELOCITY", libfrankapy::ControlMode::CARTESIAN_VELOCITY)
      .value("TORQUE", libfrankapy::ControlMode::TORQUE)
      .value("TRAJECTORY", libfrankapy::ControlMode::TRAJECTORY);

  py::enum_<libfrankapy::MotionType>(m, "MotionType")
      .value("LINEAR", libfrankapy::MotionType::LINEAR)
      .value("JOINT_INTERPOLATED", libfrankapy::MotionType::JOINT_INTERPOLATED)
      .value("CIRCULAR", libfrankapy::MotionType::CIRCULAR);

  // Main controller class
  py::class_<libfrankapy::PyRealtimeController>(m, "RealtimeController")
      .def(py::init<const std::string&>(), "robot_ip"_a)
      .def("connect", &libfrankapy::PyRealtimeController::connect)
      .def("disconnect", &libfrankapy::PyRealtimeController::disconnect)
      .def("is_connected", &libfrankapy::PyRealtimeController::is_connected)
      .def("start_control", &libfrankapy::PyRealtimeController::start_control)
      .def("stop_control", &libfrankapy::PyRealtimeController::stop_control)
      .def("is_control_running",
           &libfrankapy::PyRealtimeController::is_control_running)
      .def("emergency_stop", &libfrankapy::PyRealtimeController::emergency_stop)

      // State queries
      .def("get_joint_positions",
           &libfrankapy::PyRealtimeController::get_joint_positions)
      .def("get_joint_velocities",
           &libfrankapy::PyRealtimeController::get_joint_velocities)
      .def("get_joint_torques",
           &libfrankapy::PyRealtimeController::get_joint_torques)
      .def("get_cartesian_position",
           &libfrankapy::PyRealtimeController::get_cartesian_position)
      .def("get_cartesian_orientation",
           &libfrankapy::PyRealtimeController::get_cartesian_orientation)
      .def("get_external_wrench",
           &libfrankapy::PyRealtimeController::get_external_wrench)
      .def("is_moving", &libfrankapy::PyRealtimeController::is_moving)
      .def("has_error", &libfrankapy::PyRealtimeController::has_error)
      .def("get_error_code", &libfrankapy::PyRealtimeController::get_error_code)
      .def("get_control_frequency",
           &libfrankapy::PyRealtimeController::get_control_frequency)
      .def("get_timestamp", &libfrankapy::PyRealtimeController::get_timestamp)

      // Control commands
      .def("send_joint_position_command",
           &libfrankapy::PyRealtimeController::send_joint_position_command,
           "target_positions"_a, "speed_factor"_a = 0.1,
           "acceleration_factor"_a = 0.1, "timeout"_a = 30.0)
      .def("send_cartesian_position_command",
           &libfrankapy::PyRealtimeController::send_cartesian_position_command,
           "target_position"_a, "target_orientation"_a, "speed_factor"_a = 0.1,
           "motion_type"_a = 0, "timeout"_a = 30.0)
      .def("wait_for_command_completion",
           &libfrankapy::PyRealtimeController::wait_for_command_completion,
           "timeout"_a = 30.0);

  // Shared memory reader
  py::class_<libfrankapy::PySharedMemoryReader>(m, "SharedMemoryReader")
      .def(py::init<>())
      .def("connect", &libfrankapy::PySharedMemoryReader::connect)
      .def("is_connected", &libfrankapy::PySharedMemoryReader::is_connected)
      .def("get_robot_state",
           &libfrankapy::PySharedMemoryReader::get_robot_state);

  // Utility functions
  m.def("get_current_timestamp",
        &libfrankapy::shared_memory_utils::get_current_timestamp);
  m.def("is_timestamp_recent",
        &libfrankapy::shared_memory_utils::is_timestamp_recent, "timestamp"_a,
        "timeout_us"_a = 1000000);
}
