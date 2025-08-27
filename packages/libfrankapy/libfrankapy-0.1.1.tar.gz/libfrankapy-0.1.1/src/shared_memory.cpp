/**
 * @file shared_memory.cpp
 * @brief Implementation of shared memory management for libfrankapy
 */

#include "shared_memory.hpp"

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <chrono>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <thread>

namespace libfrankapy {

/**
 * @brief SharedMemoryManager implementation
 */
SharedMemoryManager::SharedMemoryManager(bool create_new)
    : shm_fd_(-1), shared_data_(nullptr), is_creator_(create_new) {
  if (create_new) {
    // Remove existing shared memory if it exists
    shm_unlink(SHM_NAME);

    // Create new shared memory segment
    shm_fd_ = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd_ == -1) {
      throw std::runtime_error("Failed to create shared memory segment");
    }

    // Set the size of the shared memory segment
    if (ftruncate(shm_fd_, SHM_SIZE) == -1) {
      close(shm_fd_);
      shm_unlink(SHM_NAME);
      throw std::runtime_error("Failed to set shared memory size");
    }
  } else {
    // Open existing shared memory segment
    shm_fd_ = shm_open(SHM_NAME, O_RDWR, 0666);
    if (shm_fd_ == -1) {
      throw std::runtime_error("Failed to open shared memory segment");
    }
  }

  // Map the shared memory segment
  shared_data_ = static_cast<SharedMemorySegment*>(
      mmap(nullptr, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd_, 0));

  if (shared_data_ == MAP_FAILED) {
    close(shm_fd_);
    if (is_creator_) {
      shm_unlink(SHM_NAME);
    }
    throw std::runtime_error("Failed to map shared memory");
  }

  // Initialize the shared memory if we created it
  if (create_new) {
    // Use placement new to initialize the structures
    new (&shared_data_->state) RealtimeState();
    new (&shared_data_->command) ControlCommand();
    new (&shared_data_->config) RealtimeConfig();

    shared_data_->initialized.store(true);
    shared_data_->sequence_number.store(0);

    std::cout << "Shared memory segment created and initialized" << std::endl;
  } else {
    // Wait for initialization if opening existing segment
    auto start_time = std::chrono::steady_clock::now();
    while (!shared_data_->initialized.load()) {
      auto current_time = std::chrono::steady_clock::now();
      auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                         current_time - start_time)
                         .count();

      if (elapsed > 10) {  // 10 second timeout
        throw std::runtime_error(
            "Timeout waiting for shared memory initialization");
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    std::cout << "Connected to existing shared memory segment" << std::endl;
  }
}

/**
 * @brief Destructor - cleans up shared memory
 */
SharedMemoryManager::~SharedMemoryManager() {
  if (shared_data_ != nullptr) {
    munmap(shared_data_, SHM_SIZE);
  }

  if (shm_fd_ != -1) {
    close(shm_fd_);
  }

  // Only unlink if we created the segment
  if (is_creator_) {
    shm_unlink(SHM_NAME);
    std::cout << "Shared memory segment destroyed" << std::endl;
  }
}

/**
 * @brief Get pointer to shared memory segment
 */
SharedMemorySegment* SharedMemoryManager::get_shared_data() {
  return shared_data_;
}

/**
 * @brief Check if shared memory is properly initialized
 */
bool SharedMemoryManager::is_initialized() const {
  return shared_data_ != nullptr && shared_data_->initialized.load();
}

/**
 * @brief Update sequence number for synchronization
 */
void SharedMemoryManager::increment_sequence() {
  if (shared_data_) {
    shared_data_->sequence_number.fetch_add(1);
  }
}

/**
 * @brief Get current sequence number
 */
uint64_t SharedMemoryManager::get_sequence() const {
  return shared_data_ ? shared_data_->sequence_number.load() : 0;
}

/**
 * @brief Utility functions for working with shared memory data
 */
namespace shared_memory_utils {

/**
 * @brief Copy joint positions from array to atomic array
 */
void set_joint_positions(std::array<std::atomic<double>, 7>& atomic_array,
                         const std::array<double, 7>& values) {
  for (size_t i = 0; i < 7; ++i) {
    atomic_array[i].store(values[i]);
  }
}

/**
 * @brief Copy joint positions from atomic array to regular array
 */
std::array<double, 7> get_joint_positions(
    const std::array<std::atomic<double>, 7>& atomic_array) {
  std::array<double, 7> result;
  for (size_t i = 0; i < 7; ++i) {
    result[i] = atomic_array[i].load();
  }
  return result;
}

/**
 * @brief Copy Cartesian position from array to atomic array
 */
void set_cartesian_position(std::array<std::atomic<double>, 3>& atomic_array,
                            const std::array<double, 3>& values) {
  for (size_t i = 0; i < 3; ++i) {
    atomic_array[i].store(values[i]);
  }
}

/**
 * @brief Copy Cartesian position from atomic array to regular array
 */
std::array<double, 3> get_cartesian_position(
    const std::array<std::atomic<double>, 3>& atomic_array) {
  std::array<double, 3> result;
  for (size_t i = 0; i < 3; ++i) {
    result[i] = atomic_array[i].load();
  }
  return result;
}

/**
 * @brief Copy quaternion from array to atomic array
 */
void set_quaternion(std::array<std::atomic<double>, 4>& atomic_array,
                    const std::array<double, 4>& values) {
  for (size_t i = 0; i < 4; ++i) {
    atomic_array[i].store(values[i]);
  }
}

/**
 * @brief Copy quaternion from atomic array to regular array
 */
std::array<double, 4> get_quaternion(
    const std::array<std::atomic<double>, 4>& atomic_array) {
  std::array<double, 4> result;
  for (size_t i = 0; i < 4; ++i) {
    result[i] = atomic_array[i].load();
  }
  return result;
}

/**
 * @brief Get current timestamp in microseconds
 */
uint64_t get_current_timestamp() {
  auto now = std::chrono::high_resolution_clock::now();
  auto duration = now.time_since_epoch();
  return std::chrono::duration_cast<std::chrono::microseconds>(duration)
      .count();
}

/**
 * @brief Update timestamp in shared memory structure
 */
void update_timestamp(std::atomic<uint64_t>& timestamp) {
  timestamp.store(get_current_timestamp());
}

/**
 * @brief Check if timestamp is recent (within timeout)
 */
bool is_timestamp_recent(uint64_t timestamp, uint64_t timeout_us) {
  uint64_t current = get_current_timestamp();
  return (current - timestamp) < timeout_us;
}

}  // namespace shared_memory_utils

}  // namespace libfrankapy
