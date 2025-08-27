# Contributing to libfrankapy

We welcome contributions to libfrankapy! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- CMake 3.16 or higher
- C++17 compatible compiler
- libfranka installed
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork:

```bash
git clone https://github.com/yourusername/libfrankapy.git
cd libfrankapy
```

3. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies:

```bash
pip install -e ".[dev]"
```

5. Install pre-commit hooks:

```bash
pre-commit install
```

## Development Workflow

1. Create a new branch for your feature:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Run tests:

```bash
pytest
```

4. Run linting:

```bash
flake8 libfrankapy/
black libfrankapy/
isort libfrankapy/
```

5. Commit your changes:

```bash
git add .
git commit -m "Add your descriptive commit message"
```

6. Push to your fork:

```bash
git push origin feature/your-feature-name
```

7. Create a Pull Request on GitHub

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Use meaningful variable and function names
- Keep functions focused and small (< 50 lines when possible)

#### Example Python Code Style

```python
from typing import Optional, List
import numpy as np

def move_to_joint(self, 
                  target_joints: np.ndarray,
                  speed_factor: float = 0.1,
                  timeout: Optional[float] = None) -> bool:
    """Move robot to target joint positions.
    
    Args:
        target_joints: Target joint positions in radians (7,)
        speed_factor: Speed factor for motion (0.0 to 1.0)
        timeout: Maximum time to wait for completion
        
    Returns:
        True if motion completed successfully
        
    Raises:
        MotionException: If motion fails
        ValidationError: If target_joints are invalid
    """
    if not self._validate_joint_positions(target_joints):
        raise ValidationError("Invalid joint positions")
        
    return self._execute_joint_motion(target_joints, speed_factor, timeout)
```

### C++ Code

- Follow Google C++ Style Guide
- Use modern C++17 features
- Use RAII for resource management
- Write clear, self-documenting code
- Use const correctness

#### Example C++ Code Style

```cpp
#include <memory>
#include <vector>
#include <franka/robot.h>

namespace libfrankapy {

class RobotController {
public:
    explicit RobotController(const std::string& robot_ip);
    ~RobotController() = default;
    
    // Non-copyable, movable
    RobotController(const RobotController&) = delete;
    RobotController& operator=(const RobotController&) = delete;
    RobotController(RobotController&&) = default;
    RobotController& operator=(RobotController&&) = default;
    
    bool MoveToJoint(const std::array<double, 7>& target_joints,
                     double speed_factor = 0.1);
    
private:
    std::unique_ptr<franka::Robot> robot_;
    bool ValidateJointPositions(const std::array<double, 7>& joints) const;
};

}  // namespace libfrankapy
```

## Testing

All contributions must include appropriate tests:

- Unit tests for individual functions/classes
- Integration tests for component interactions
- System tests for end-to-end functionality
- Performance tests for critical paths

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_robot.py

# Run with coverage
pytest --cov=libfrankapy

# Run performance tests
pytest tests/performance/

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests

#### Unit Test Example

```python
import pytest
import numpy as np
from libfrankapy import FrankaRobot
from libfrankapy.exceptions import ValidationError

class TestFrankaRobot:
    def test_validate_joint_positions_valid(self):
        """Test validation with valid joint positions."""
        robot = FrankaRobot("192.168.1.100")
        valid_joints = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
        
        assert robot._validate_joint_positions(valid_joints) is True
    
    def test_validate_joint_positions_invalid(self):
        """Test validation with invalid joint positions."""
        robot = FrankaRobot("192.168.1.100")
        invalid_joints = np.array([5.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
        
        assert robot._validate_joint_positions(invalid_joints) is False
    
    def test_move_to_joint_invalid_input(self):
        """Test move_to_joint with invalid input."""
        robot = FrankaRobot("192.168.1.100")
        invalid_joints = np.array([5.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
        
        with pytest.raises(ValidationError):
            robot.move_to_joint(invalid_joints)
```

#### Integration Test Example

```python
import pytest
import numpy as np
from libfrankapy import FrankaRobot

@pytest.mark.integration
class TestRobotIntegration:
    @pytest.fixture
    def robot(self):
        """Create robot instance for testing."""
        robot = FrankaRobot("192.168.1.100")
        robot.connect()
        yield robot
        robot.disconnect()
    
    def test_full_motion_sequence(self, robot):
        """Test complete motion sequence."""
        # Get initial position
        initial_joints = robot.get_joint_positions()
        
        # Move to target position
        target_joints = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
        success = robot.move_to_joint(target_joints)
        assert success is True
        
        # Verify position
        current_joints = robot.get_joint_positions()
        np.testing.assert_allclose(current_joints, target_joints, atol=0.01)
        
        # Return to initial position
        robot.move_to_joint(initial_joints)
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=libfrankapy
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    system: System tests
    performance: Performance tests
    slow: Slow running tests
```

## Documentation

All code changes should include documentation updates:

- Update docstrings for modified functions
- Add examples for new features
- Update README if necessary
- Add changelog entries

### Building Documentation

```bash
cd docs
npm run docs:dev  # Development server
npm run docs:build  # Build static site
npm run docs:preview  # Preview built site
```

### Documentation Style

#### Docstring Format

```python
def complex_function(param1: str, 
                    param2: Optional[int] = None,
                    param3: List[float] = None) -> Dict[str, Any]:
    """Brief description of the function.
    
    Longer description explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to None.
        param3: Description of param3. Defaults to None.
        
    Returns:
        Description of return value and its structure.
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> result = complex_function("test", param2=42)
        >>> print(result["status"])
        "success"
        
    Note:
        Any additional notes or warnings about the function.
    """
    pass
```

## Pull Request Guidelines

Before submitting a pull request:

1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Rebase on latest main branch
5. Write clear commit messages
6. Include description of changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Breaking change

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Performance impact assessed

## Documentation
- [ ] Docstrings updated
- [ ] README updated (if needed)
- [ ] Changelog entry added
- [ ] Examples updated (if needed)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No breaking changes (or clearly documented)
- [ ] Tests pass locally
- [ ] Linting passes
```

### Commit Message Format

```
type(scope): brief description

Longer description explaining the change in detail.
Include motivation for the change and contrast with
previous behavior.

Fixes #123
Closes #456
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**
```
feat(robot): add force control capabilities

Implement force control interface allowing users to specify
target forces and torques. Includes safety limits and
automatic error recovery.

Fixes #234
```

```
fix(control): resolve trajectory interpolation bug

Fix issue where cubic interpolation was producing
incorrect velocities at trajectory waypoints.

Closes #456
```

## Code Review Process

1. All PRs require at least one review from a maintainer
2. Maintainers will review within 48 hours
3. Address feedback promptly
4. Squash commits before merge
5. Ensure CI passes before merge

### Review Checklist

**For Reviewers:**
- [ ] Code follows project standards
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact is acceptable
- [ ] Breaking changes are documented

**For Contributors:**
- [ ] Address all review comments
- [ ] Update tests if requested
- [ ] Rebase on latest main
- [ ] Squash related commits

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord server for real-time chat
- **Documentation**: Check existing docs and examples
- **Email**: Contact maintainers directly for sensitive issues

### Issue Templates

#### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.8.10]
- libfrankapy version: [e.g. 1.2.3]
- Robot model: [e.g. Franka Panda]

**Additional context**
Any other context about the problem.
```

#### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Steps

1. **Prepare Release**
   ```bash
   # Update version numbers
   bump2version minor  # or major/patch
   
   # Update changelog
   git add CHANGELOG.md
   git commit -m "docs: update changelog for v1.2.0"
   ```

2. **Create Release**
   ```bash
   # Create and push tag
   git tag v1.2.0
   git push origin v1.2.0
   
   # Create GitHub release
   gh release create v1.2.0 --generate-notes
   ```

3. **Build and Upload**
   ```bash
   # Build packages
   python -m build
   
   # Upload to PyPI
   twine upload dist/*
   ```

4. **Update Documentation**
   ```bash
   # Deploy documentation
   cd docs
   npm run docs:build
   npm run docs:deploy
   ```

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New force control interface
- Support for custom trajectory generators
- Performance monitoring tools

### Changed
- Improved error handling in robot interface
- Updated documentation structure

### Fixed
- Trajectory interpolation bug
- Memory leak in state monitoring

### Deprecated
- Old configuration format (will be removed in v2.0)

### Removed
- Legacy API methods

### Security
- Fixed potential buffer overflow in C++ layer
```

## Development Tools

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/isort
    rev: 5.11.4
    hooks:
      - id: isort
      
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Development Scripts

```bash
#!/bin/bash
# scripts/dev-setup.sh

set -e

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run initial tests
pytest

echo "Development environment ready!"
```

```bash
#!/bin/bash
# scripts/run-tests.sh

set -e

echo "Running test suite..."

# Run linting
flake8 libfrankapy/
black --check libfrankapy/
isort --check-only libfrankapy/

# Run tests
pytest --cov=libfrankapy --cov-report=term-missing

# Run performance tests
pytest tests/performance/ -m performance

echo "All tests passed!"
```

## Best Practices

### Code Organization

- Keep modules focused and cohesive
- Use clear, descriptive names
- Minimize dependencies between modules
- Follow the single responsibility principle

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Include context in error reports
- Implement graceful degradation

### Performance

- Profile critical code paths
- Use appropriate data structures
- Minimize memory allocations in real-time code
- Cache expensive computations

### Security

- Validate all inputs
- Use secure communication protocols
- Avoid hardcoded credentials
- Follow principle of least privilege

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication

- Be respectful and constructive
- Ask questions when unclear
- Provide helpful feedback
- Share knowledge and experience

### Recognition

We recognize contributors through:
- Contributor list in README
- Release notes acknowledgments
- Community highlights
- Maintainer nominations

Thank you for contributing to libfrankapy!
