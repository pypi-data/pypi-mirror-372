#!/usr/bin/env python3
"""Setup script for libfrankapy.

This script builds the C++ extension module and installs the Python package.
"""

import os
import platform
import subprocess  # nosec B404
import sys
from pathlib import Path

import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

# Package information
PACKAGE_NAME = "libfrankapy"
VERSION = "0.1.1"
AUTHOR = "libfrankapy Team"
AUTHOR_EMAIL = "support@libfrankapy.org"
DESCRIPTION = "Python bindings for libfranka with real-time control"
URL = "https://github.com/libfrankapy/libfrankapy"

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Check if we're on a supported platform
if platform.system() != "Linux":
    raise RuntimeError("libfrankapy only supports Linux with PREEMPT_RT kernel")


# Check for required system libraries
def check_library(lib_name, pkg_config_name=None):
    """Check if a system library is available."""
    import glob

    # First try pkg-config if available
    if pkg_config_name:
        try:
            subprocess.check_call(  # nosec B603 B607
                ["pkg-config", "--exists", pkg_config_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"Found {lib_name} via pkg-config ({pkg_config_name})")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"pkg-config check failed for {pkg_config_name}")

    # Get additional search paths from CMAKE_PREFIX_PATH
    search_paths = ["/usr/lib", "/usr/local/lib", "/opt/lib", "/opt/libfranka/lib"]

    # Add common system library paths
    search_paths.extend(
        [
            "/usr/lib/x86_64-linux-gnu",
            "/usr/local/lib/x86_64-linux-gnu",
            "/lib/x86_64-linux-gnu",
        ]
    )

    # Add paths from CMAKE_PREFIX_PATH environment variable
    cmake_prefix_path = os.environ.get("CMAKE_PREFIX_PATH", "")
    if cmake_prefix_path:
        for path in cmake_prefix_path.split(":"):
            if path.strip():
                lib_path = os.path.join(path.strip(), "lib")
                if lib_path not in search_paths:
                    search_paths.append(lib_path)

    print(f"Searching for {lib_name} in paths: {search_paths}")

    # Try to find the library in all search locations
    for lib_dir in search_paths:
        if not os.path.exists(lib_dir):
            continue

        # Check for exact match first
        exact_path = f"{lib_dir}/lib{lib_name}.so"
        if os.path.exists(exact_path):
            print(f"Found {lib_name} at {exact_path}")
            return True

        # Check for versioned libraries (e.g., libPocoFoundation.so.xx)
        pattern = f"{lib_dir}/lib{lib_name}.so*"
        matches = glob.glob(pattern)
        if matches:
            print(f"Found {lib_name} with versioned files: {matches}")
            return True

        # For debugging: list all files in the directory that might match
        try:
            all_files = os.listdir(lib_dir)
            matching_files = [f for f in all_files if lib_name.lower() in f.lower()]
            if matching_files:
                print(f"Found potential matches in {lib_dir}: {matching_files}")
        except (OSError, PermissionError):
            pass

    print(f"Library {lib_name} not found in any search path")
    return False


# Check for required dependencies
# Note: PocoFoundation might be named differently in different distributions
required_libs = [
    ("franka", None),
    ("PocoFoundation", "poco-foundation"),
    ("eigen3", "eigen3"),
]

# Special handling for Poco libraries


def check_poco_library():
    """Special check for Poco Foundation library with multiple naming patterns."""
    import glob

    # Try pkg-config first
    for pkg_name in ["poco-foundation", "poco", "libpoco-foundation"]:
        try:
            subprocess.check_call(  # nosec B603 B607
                ["pkg-config", "--exists", pkg_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"Found Poco via pkg-config ({pkg_name})")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    # Get search paths
    search_paths = ["/usr/lib", "/usr/local/lib", "/opt/lib", "/opt/libfranka/lib"]
    search_paths.extend(
        [
            "/usr/lib/x86_64-linux-gnu",
            "/usr/local/lib/x86_64-linux-gnu",
            "/lib/x86_64-linux-gnu",
        ]
    )

    # Add CMAKE_PREFIX_PATH
    cmake_prefix_path = os.environ.get("CMAKE_PREFIX_PATH", "")
    if cmake_prefix_path:
        for path in cmake_prefix_path.split(":"):
            if path.strip():
                lib_path = os.path.join(path.strip(), "lib")
                if lib_path not in search_paths:
                    search_paths.append(lib_path)

    print(f"Searching for Poco libraries in paths: {search_paths}")

    # Try different naming patterns for Poco
    poco_patterns = [
        "libPocoFoundation.so*",
        "libpoco_foundation.so*",
        "libpocofoundation.so*",
        "libPoco.so*",
        "libpoco.so*",
    ]

    for lib_dir in search_paths:
        if not os.path.exists(lib_dir):
            continue

        for pattern in poco_patterns:
            full_pattern = os.path.join(lib_dir, pattern)
            matches = glob.glob(full_pattern)
            if matches:
                print(f"Found Poco library: {matches}")
                return True

        # List all poco-related files for debugging
        try:
            all_files = os.listdir(lib_dir)
            poco_files = [f for f in all_files if "poco" in f.lower()]
            if poco_files:
                print(f"Found Poco-related files in {lib_dir}: {poco_files}")
        except (OSError, PermissionError):
            pass

    print("No Poco Foundation library found")
    return False


missing_libs = []
for lib_name, pkg_name in required_libs:
    if lib_name == "PocoFoundation":
        # Use special Poco detection function
        if not check_poco_library():
            missing_libs.append(lib_name)
    else:
        if not check_library(lib_name, pkg_name):
            missing_libs.append(lib_name)

if missing_libs:
    print("Error: Missing required system libraries:")
    for lib in missing_libs:
        print(f"  - {lib}")
    print("\nPlease install the missing libraries and try again.")
    print("See README.md for installation instructions.")
    sys.exit(1)


# Get include directories
def get_include_dirs():
    """Get include directories for compilation."""
    include_dirs = [
        # pybind11 includes
        pybind11.get_include(),
        # Local source directory
        "src",
        # libfranka include directory
        "/opt/libfranka/include",
    ]

    # Add paths from CMAKE_PREFIX_PATH environment variable
    cmake_prefix_path = os.environ.get("CMAKE_PREFIX_PATH", "")
    if cmake_prefix_path:
        for path in cmake_prefix_path.split(":"):
            if path.strip():
                inc_path = os.path.join(path.strip(), "include")
                if os.path.exists(inc_path) and inc_path not in include_dirs:
                    include_dirs.append(inc_path)

    # Try to get Eigen3 include directory
    try:
        eigen_include = (
            subprocess.check_output(  # nosec B603 B607
                ["pkg-config", "--cflags-only-I", "eigen3"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .replace("-I", "")
        )
        if eigen_include:
            include_dirs.append(eigen_include)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to common locations
        for path in ["/usr/include/eigen3", "/usr/local/include/eigen3"]:
            if os.path.exists(path):
                include_dirs.append(path)
                break

    return include_dirs


# Get library directories and libraries
def get_libraries():
    """Get libraries to link against."""
    libraries = ["franka", "PocoFoundation", "pthread", "rt"]
    library_dirs = ["/usr/lib", "/usr/local/lib", "/opt/libfranka/lib"]

    # Add paths from CMAKE_PREFIX_PATH environment variable
    cmake_prefix_path = os.environ.get("CMAKE_PREFIX_PATH", "")
    if cmake_prefix_path:
        for path in cmake_prefix_path.split(":"):
            if path.strip():
                lib_path = os.path.join(path.strip(), "lib")
                if lib_path not in library_dirs:
                    library_dirs.append(lib_path)

    return libraries, library_dirs


# Define the extension module
def create_extension():
    """Create the pybind11 extension."""

    # Source files
    sources = [
        "src/python_bindings.cpp",
        "src/shared_memory.cpp",
        "src/realtime_controller.cpp",
        "src/motion_generators.cpp",
    ]

    # Get compilation parameters
    include_dirs = get_include_dirs()
    libraries, library_dirs = get_libraries()

    # Compiler flags
    extra_compile_args = [
        "-std=c++17",
        "-O3",
        "-Wall",
        "-Wextra",
        "-fPIC",
        "-fvisibility=hidden",
        "-DWITH_PYTHON_BINDINGS",
        "-DEIGEN_MPL2_ONLY",
        "-D_GNU_SOURCE",
    ]

    # Linker flags
    extra_link_args = [
        "-Wl,--as-needed",
    ]

    # Create extension
    ext = Pybind11Extension(
        "libfrankapy._libfrankapy_core",
        sources=sources,
        include_dirs=include_dirs,
        libraries=libraries,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=17,
    )

    return ext


# Custom build command
class CustomBuildExt(build_ext):
    """Custom build extension command."""

    def build_extensions(self):
        """Build the extensions with custom settings."""

        # Check compiler
        compiler_type = self.compiler.compiler_type
        if compiler_type == "unix":
            # Add optimization flags for release builds
            # Note: Removed -march=native and -mtune=native for CI compatibility
            for ext in self.extensions:
                # Only add safe optimization flags that work in CI environments
                # -O3 is already included in base compile args, so only add -DNDEBUG
                if "-DNDEBUG" not in ext.extra_compile_args:
                    ext.extra_compile_args.append("-DNDEBUG")

        # Call parent build
        super().build_extensions()

    def run(self):
        """Run the build process."""
        print("Building libfrankapy C++ extension...")
        super().run()
        print("Build completed successfully!")


# Setup configuration
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    # Package configuration
    packages=find_packages(),
    package_data={
        "libfrankapy": ["py.typed"],
    },
    # Extension modules
    ext_modules=[create_extension()],
    cmdclass={"build_ext": CustomBuildExt},
    # Dependencies (defined in pyproject.toml)
    python_requires=">=3.9",
    # Metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",

        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="robotics franka robot-control real-time panda",
    # Entry points
    entry_points={
        "console_scripts": [
            "libfrankapy-info=libfrankapy.utils:print_system_info",
        ],
    },
    # Include additional files
    include_package_data=True,
    zip_safe=False,
    # Project URLs
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}/docs",
    },
)
