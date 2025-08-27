# Development Guide

Welcome to the libfrankapy development guide. This section contains comprehensive information for developers who want to contribute to or understand the internals of libfrankapy.

## Overview

libfrankapy is designed as a high-performance Python interface for Franka Emika robots, combining the ease of Python with the real-time capabilities of C++. This development guide will help you understand the architecture, contribute effectively, and maintain high code quality.

## Getting Started

If you're new to libfrankapy development, we recommend starting with:

1. **[Architecture Overview](./architecture)** - Understand the system design and core components
2. **[Contributing Guide](./contributing)** - Learn how to set up your development environment and contribute
3. **[Testing Guide](./testing)** - Understand our testing philosophy and practices

## Development Topics

### [Architecture](./architecture)

Learn about the system architecture, including:
- Design principles and philosophy
- Core components and their interactions
- Thread architecture and real-time considerations
- Memory management and performance optimization
- Extensibility and plugin architecture

### [Contributing](./contributing)

Everything you need to know to contribute:
- Development environment setup
- Coding standards and best practices
- Pull request workflow
- Code review process
- Release procedures

### [Testing](./testing)

Comprehensive testing guidelines:
- Testing philosophy and strategy
- Unit, integration, and system testing
- Performance and safety testing
- Continuous integration setup
- Test writing best practices

## Quick Links

- **Repository**: [GitHub](https://github.com/iamlab-cmu/libfrankapy)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/iamlab-cmu/libfrankapy/issues)
- **Discussions**: [Community Discussions](https://github.com/iamlab-cmu/libfrankapy/discussions)
- **API Documentation**: [API Reference](/api/)

## Development Principles

### Safety First
- All safety-critical code must be thoroughly tested
- Multiple layers of safety checks
- Graceful error handling and recovery
- Emergency stop capabilities

### Performance
- Real-time performance for critical control loops
- Minimal latency for robot communication
- Efficient memory management
- Optimized data structures and algorithms

### Reliability
- Comprehensive testing at all levels
- Robust error handling
- Deterministic behavior
- Extensive validation and verification

### Maintainability
- Clean, readable code
- Comprehensive documentation
- Modular design
- Clear separation of concerns

## Community

We welcome contributions from the robotics community! Whether you're fixing bugs, adding features, improving documentation, or helping other users, your contributions are valuable.

### How to Get Involved

1. **Start Small**: Look for "good first issue" labels in our GitHub repository
2. **Join Discussions**: Participate in community discussions and help answer questions
3. **Report Issues**: Help us improve by reporting bugs and suggesting enhancements
4. **Share Examples**: Contribute examples and tutorials for other users
5. **Improve Documentation**: Help us keep our documentation up-to-date and comprehensive

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our Code of Conduct when participating in our community.

## Resources

### External Documentation
- [Franka Control Interface (FCI)](https://frankaemika.github.io/docs/)
- [libfranka Documentation](https://frankaemika.github.io/libfranka/)
- [Franka Emika Robot Documentation](https://frankaemika.github.io/docs/)

### Development Tools
- **Build System**: CMake for C++ components, setuptools for Python
- **Testing**: pytest for Python, Google Test for C++
- **Documentation**: VitePress for this documentation site
- **CI/CD**: GitHub Actions for continuous integration
- **Code Quality**: pre-commit hooks, linting, and formatting tools

### Related Projects
- [franka_ros](https://github.com/frankaemika/franka_ros) - ROS integration for Franka robots
- [panda-gym](https://github.com/qgallouedec/panda-gym) - Gymnasium environments for Franka Panda
- [frankapy](https://github.com/iamlab-cmu/frankapy) - Original Python interface (predecessor)

## Support

If you need help with development:

1. **Check the Documentation**: Start with this guide and the API reference
2. **Search Issues**: Look for similar issues or questions in our GitHub repository
3. **Ask Questions**: Open a discussion or issue if you can't find the answer
4. **Join the Community**: Connect with other developers and users

We're here to help you succeed in contributing to libfrankapy!
