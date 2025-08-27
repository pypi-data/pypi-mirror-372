# Contributing Guide

Thank you for your interest in the libfrankapy project! We welcome various forms of contributions, including but not limited to:

- 🐛 Bug reports
- 💡 New feature suggestions
- 📝 Documentation improvements
- 🔧 Code fixes
- ✨ New features
- 🧪 Writing tests
- 📖 Documentation translation

## 📋 Before You Start

Before starting to contribute, please ensure you have:

1. Read the project [README.md](README.md)
2. Understood the project [license](LICENSE)
3. Checked existing [Issues](https://github.com/yourusername/libfrankapy/issues) and [Pull Requests](https://github.com/yourusername/libfrankapy/pulls)

## 🚀 Development Environment Setup

### 1. Fork and Clone Repository

```bash
# Fork the repository to your GitHub account, then clone
git clone https://github.com/yourusername/libfrankapy.git
cd libfrankapy

# Add upstream repository
git remote add upstream https://github.com/originalowner/libfrankapy.git
```

### 2. Setup Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Or on Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Environment

```bash
# Run tests to ensure environment is working
pytest

# Run code quality checks
flake8 libfrankapy/
mypy libfrankapy/

# Build C++ extensions
python setup.py build_ext --inplace
```

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
# Ensure main branch is up to date
git checkout main
git pull upstream main

# Create new feature branch
git checkout -b feature/your-feature-name
# Or fix branch
git checkout -b fix/issue-number-description
```

### 2. Development

- Follow project code style and conventions
- Write clear commit messages
- Add tests for new features
- Update relevant documentation

### 3. Commit Changes

```bash
# Add changed files
git add .

# Commit changes (pre-commit will automatically run checks)
git commit -m "feat: add new feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 4. Create Pull Request

1. Navigate to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the PR template
4. Wait for code review

## 📝 Code Style Guide

### Python Code

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide:

```python
# Good example
class FrankaRobot:
    """Franka robot control class.

    Args:
        robot_ip: Robot IP address
        realtime_config: Real-time configuration parameters
    """

    def __init__(self, robot_ip: str, realtime_config: Optional[RealtimeConfig] = None) -> None:
        self._robot_ip = robot_ip
        self._config = realtime_config or RealtimeConfig()
        self._is_connected = False

    def connect(self) -> bool:
        """Connect to robot.

        Returns:
            Whether connection was successful
        """
        try:
            # Connection logic
            self._is_connected = True
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
```

**Key Points:**

- Use 4 spaces for indentation
- Line length should not exceed 88 characters
- Use type hints
- Write clear docstrings
- Use meaningful variable names

### C++ Code

We follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html):

```cpp
// Good example
class RealtimeController {
 public:
  explicit RealtimeController(const RealtimeConfig& config);

  bool StartControl();
  void StopControl();

  RobotState GetCurrentState() const;

 private:
  std::unique_ptr<franka::Robot> robot_;
  std::atomic<bool> is_running_{false};
  RealtimeConfig config_;

  void ControlLoop();
};
```

**Key Points:**

- Use 2 spaces for indentation
- Class names use PascalCase
- Function names use PascalCase
- Variable names use snake_case, private members end with underscore
- Use smart pointers for memory management
- Add appropriate const modifiers

## 🧪 Testing Guide

### Writing Tests

We use pytest for Python testing:

```python
import pytest
from libfrankapy import FrankaRobot
from libfrankapy.exceptions import ConnectionError

class TestFrankaRobot:
    """Tests for FrankaRobot class."""

    def test_init_with_valid_ip(self):
        """Test initialization with valid IP."""
        robot = FrankaRobot("192.168.1.100")
        assert robot.robot_ip == "192.168.1.100"
        assert not robot.is_connected()

    def test_init_with_invalid_ip(self):
        """Test initialization with invalid IP."""
        with pytest.raises(ValueError):
            FrankaRobot("invalid-ip")

    @pytest.mark.integration
    def test_connect_to_real_robot(self):
        """Integration test: connect to real robot."""
        # This test requires a real robot
        robot = FrankaRobot("192.168.1.100")
        assert robot.connect()
        assert robot.is_connected()
        robot.disconnect()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_robot.py

# Run specific test
pytest tests/test_robot.py::TestFrankaRobot::test_init_with_valid_ip

# Run tests with coverage
pytest --cov=libfrankapy --cov-report=html

# Skip integration tests (require real hardware)
pytest -m "not integration"
```

## 📚 Documentation Guide

### API Documentation

We use Google-style docstrings:

```python
def move_to_joint(self, joint_positions: List[float],
                  speed_factor: float = 0.1,
                  acceleration_factor: float = 0.1) -> bool:
    """Move robot to specified joint positions.

    Args:
        joint_positions: Target joint position list containing 7 joint angles (radians)
        speed_factor: Speed factor, range [0.01, 1.0], default 0.1
        acceleration_factor: Acceleration factor, range [0.01, 1.0], default 0.1

    Returns:
        Whether motion was executed successfully

    Raises:
        ValueError: When joint position count is incorrect
        ConnectionError: When robot is not connected
        SafetyError: When target position exceeds safety limits

    Example:
        >>> robot = FrankaRobot("192.168.1.100")
        >>> robot.connect()
        >>> target = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        >>> success = robot.move_to_joint(target, speed_factor=0.2)
        >>> print(f"Motion successful: {success}")
    """
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## 🐛 Bug Reports

When reporting bugs, please include the following information:

1. **Environment Information**:
   - Operating system version
   - Python version
   - libfrankapy version
   - libfranka version
   - Robot model

2. **Reproduction Steps**:
   - Detailed step-by-step instructions
   - Minimal code example
   - Expected behavior vs actual behavior

3. **Error Information**:
   - Complete error stack trace
   - Relevant log output

### Bug Report Template

```markdown
## Bug Description
Briefly describe the issue encountered.

## Reproduction Steps
1. Execute '...'
2. Call '....'
3. Observe error

## Expected Behavior
Describe what you expected to happen.

## Actual Behavior
Describe what actually happened.

## Environment Information
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.9.0]
- libfrankapy: [e.g. 1.0.0]
- libfranka: [e.g. 0.15.0]
- Robot: [e.g. Franka Panda]

## Additional Information
Add any other information that might help resolve the issue.
```

## 💡 Feature Requests

When proposing new features, please consider:

1. **Use Cases**: Describe specific usage scenarios
2. **API Design**: Provide expected API interface
3. **Implementation Complexity**: Assess implementation difficulty
4. **Backward Compatibility**: Ensure existing functionality is not broken

## 🔍 Code Review

### Review Checklist

As a reviewer, please check:

- [ ] Code follows project style guidelines
- [ ] Includes appropriate tests
- [ ] Documentation is updated
- [ ] No security issues introduced
- [ ] Performance impact is acceptable
- [ ] Backward compatibility is maintained

### Review Feedback

Provide constructive feedback:

```markdown
# Good feedback examples

## Suggestion
Consider using `std::unique_ptr` instead of raw pointers for memory management to avoid memory leaks.

```cpp
// Suggested improvement
std::unique_ptr<franka::Robot> robot_;
```

## Issue

This function lacks error handling. What happens if robot connection fails?

## Praise

Excellent test coverage! These boundary condition tests are valuable.
```

## 📦 Release Process

### Version Number Rules

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH`
- `MAJOR`: Incompatible API changes
- `MINOR`: Backward-compatible feature additions
- `PATCH`: Backward-compatible bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version number is updated
- [ ] Release tag is created
- [ ] Published to PyPI

## 🤝 Community Guidelines

We are committed to creating a friendly and inclusive community environment:

- **Respect Others**: Maintain politeness and professionalism with all participants
- **Constructive Communication**: Provide useful feedback and suggestions
- **Patient Assistance**: Help new contributors learn and grow
- **Open Mindset**: Accept different viewpoints and approaches

## 📞 Getting Help

If you need help:

- 📖 Check the [documentation](https://libfrankapy.readthedocs.io/)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/libfrankapy/discussions)
- 🐛 Report issues in [Issues](https://github.com/yourusername/libfrankapy/issues)
- 📧 Send email to [support@libfrankapy.org](mailto:support@libfrankapy.org)

## 🙏 Acknowledgments

Thanks to all developers who have contributed to the libfrankapy project! Your contributions make this project better.

---

Thank you again for your contributions! 🎉
