cmake_minimum_required(VERSION 3.16)
project(
  libfrankapy
  VERSION 0.1.1
  LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set build type to Release if not specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Threads REQUIRED)

# Find libfranka
find_package(Franka REQUIRED)
if(NOT Franka_FOUND)
  message(FATAL_ERROR "libfranka not found. Please install libfranka first.")
endif()

# Find Poco
find_package(Poco REQUIRED COMPONENTS Foundation)
if(NOT Poco_FOUND)
  message(
    FATAL_ERROR "Poco not found. Please install Poco development libraries.")
endif()

# Find pybind11
find_package(pybind11 REQUIRED)
if(NOT pybind11_FOUND)
  message(FATAL_ERROR "pybind11 not found. Please install pybind11.")
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src ${EIGEN3_INCLUDE_DIRS}
                    ${Franka_INCLUDE_DIRS} ${Poco_INCLUDE_DIRS})

# Source files
set(LIBFRANKAPY_SOURCES src/shared_memory.cpp src/realtime_controller.cpp
                        src/motion_generators.cpp)

# Header files
set(LIBFRANKAPY_HEADERS src/shared_memory.hpp src/realtime_controller.hpp)

# Create static library for C++ components
add_library(libfrankapy_core STATIC ${LIBFRANKAPY_SOURCES})

# Link libraries to the core library
target_link_libraries(
  libfrankapy_core ${Franka_LIBRARIES} ${Poco_LIBRARIES} Threads::Threads
  rt # Real-time library for shared memory
)

# Set target properties
set_target_properties(
  libfrankapy_core
  PROPERTIES CXX_STANDARD 17
             CXX_STANDARD_REQUIRED ON
             POSITION_INDEPENDENT_CODE ON)

# Compiler-specific options
target_compile_options(libfrankapy_core PRIVATE -Wall -Wextra -Wpedantic
                                                -Wno-unused-parameter)

# Add real-time compilation flags
target_compile_definitions(libfrankapy_core PRIVATE _GNU_SOURCE EIGEN_MPL2_ONLY)

# Python bindings module
pybind11_add_module(_libfrankapy_core src/python_bindings.cpp
                    ${LIBFRANKAPY_SOURCES})

# Link libraries to Python module
target_link_libraries(
  _libfrankapy_core PRIVATE ${Franka_LIBRARIES} ${Poco_LIBRARIES}
                            Threads::Threads rt)

# Set Python module properties
set_target_properties(_libfrankapy_core PROPERTIES CXX_STANDARD 17
                                                   CXX_STANDARD_REQUIRED ON)

# Compiler-specific options for Python module
target_compile_options(
  _libfrankapy_core PRIVATE -Wall -Wextra -Wpedantic -Wno-unused-parameter
                            -fvisibility=hidden)

# Add compile definitions for Python module
target_compile_definitions(
  _libfrankapy_core PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO} _GNU_SOURCE
                            EIGEN_MPL2_ONLY)

# Installation rules
install(
  TARGETS libfrankapy_core
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin)

install(FILES ${LIBFRANKAPY_HEADERS} DESTINATION include/libfrankapy)

# Optional: Build examples
option(BUILD_EXAMPLES "Build example programs" OFF)
if(BUILD_EXAMPLES)
  add_subdirectory(examples)
endif()

# Optional: Build tests
option(BUILD_TESTS "Build test programs" OFF)
if(BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "Configuration Summary:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "  libfranka found: ${Franka_FOUND}")
message(STATUS "  Poco found: ${Poco_FOUND}")
message(STATUS "  pybind11 found: ${pybind11_FOUND}")
message(STATUS "  Build examples: ${BUILD_EXAMPLES}")
message(STATUS "  Build tests: ${BUILD_TESTS}")
message(STATUS "")
