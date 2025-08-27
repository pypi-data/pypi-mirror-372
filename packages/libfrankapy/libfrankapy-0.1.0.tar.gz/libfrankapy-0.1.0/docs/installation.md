# Installation

This guide will help you install libfrankapy on your system.

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **C++ Compiler**: GCC 9+ with C++17 support
- **CMake**: 3.16 or higher
- **Real-time Kernel**: PREEMPT_RT kernel (recommended for real-time control)

## Dependencies

### System Dependencies

Install the required system packages:

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  cmake \
  git \
  libpoco-dev \
  libeigen3-dev \
  libfmt-dev \
  pkg-config
```

### Libfranka Installation

libfrankapy requires libfranka to be installed:

```bash
git clone --recurse-submodules https://github.com/frankarobotics/libfranka.git
cd libfranka
git checkout 0.15.0
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/opt/libfranka \
      -DBUILD_TESTS=OFF \
      -DBUILD_EXAMPLES=OFF ..
make -j$(nproc)
sudo make install
```

### Python Dependencies

Install Python dependencies:

```bash
pip install numpy>=1.19.0 pybind11>=2.10.0
```

## Installation Methods

### From PyPI (Recommended)

```bash
pip install libfrankapy
```

### From Source

```bash
git clone https://github.com/han-xudong/libfrankapy.git
cd libfrankapy
pip install -e .
```

### Development Installation

For development purposes:

```bash
git clone https://github.com/han-xudong/libfrankapy.git
cd libfrankapy
pip install -e ".[dev]"
```

## Verification

Verify your installation:

```python
import libfrankapy as fp
print(fp.__version__)
```

## Troubleshooting

### Common Issues

**Missing libfranka**

If you get errors about missing libfranka, ensure it's installed in the correct location and CMAKE_PREFIX_PATH is set:

```bash
export CMAKE_PREFIX_PATH="/opt/libfranka:$CMAKE_PREFIX_PATH"
```

**Permission Errors**

For real-time control, you may need to set up proper permissions:

```bash
sudo usermod -a -G realtime $USER
```

**Build Errors**

Ensure all dependencies are installed and your compiler supports C++17.
