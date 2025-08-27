# Testing Guide

libfrankapy employs comprehensive testing to ensure reliability, safety, and performance.

## Testing Philosophy

### Safety First

- All safety-critical code must be thoroughly tested
- Hardware-in-the-loop testing for real robot scenarios
- Simulation testing for dangerous edge cases
- Automated safety validation

### Test-Driven Development

- Write tests before implementing features
- Use tests to define expected behavior
- Refactor with confidence using test coverage
- Maintain high test coverage (>90%)

### Continuous Integration

- All tests run on every commit
- Multiple Python versions tested
- Cross-platform compatibility
- Performance regression detection

## Test Structure

### Test Organization

```
tests/
├── unit/                 # Unit tests
│   ├── test_robot.py
│   ├── test_control.py
│   ├── test_state.py
│   └── test_exceptions.py
├── integration/          # Integration tests
│   ├── test_robot_control.py
│   ├── test_state_monitoring.py
│   └── test_error_handling.py
├── system/              # System tests
│   ├── test_full_workflow.py
│   ├── test_safety_systems.py
│   └── test_performance.py
├── performance/         # Performance tests
│   ├── test_latency.py
│   ├── test_throughput.py
│   └── test_memory.py
├── fixtures/            # Test fixtures and data
├── mocks/              # Mock objects
└── conftest.py         # Pytest configuration
```

### Test Categories

**Unit Tests**

- Test individual functions and classes
- Fast execution (< 1ms per test)
- No external dependencies
- High coverage of edge cases

**Integration Tests**

- Test component interactions
- Mock external dependencies
- Validate data flow
- Test error propagation

**System Tests**

- End-to-end testing
- Real or simulated robot
- Complete workflows
- Performance validation

**Performance Tests**

- Latency measurements
- Throughput benchmarks
- Memory usage analysis
- Regression detection

## Unit Testing

### Python Unit Tests

```python
import pytest
import numpy as np
from unittest.mock import Mock, patch
from libfrankapy import FrankaRobot
from libfrankapy.exceptions import ConnectionError

class TestFrankaRobot:
    """Test suite for FrankaRobot class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.robot = FrankaRobot()
        
    def test_initialization(self):
        """Test robot initialization."""
        assert self.robot.is_connected is False
        assert self.robot.control_mode is None
        
    def test_connect_success(self):
        """Test successful robot connection."""
        with patch('libfrankapy.robot.libfranka') as mock_franka:
            mock_franka.Robot.return_value = Mock()
            
            self.robot.connect("192.168.1.1")
            
            assert self.robot.is_connected is True
            mock_franka.Robot.assert_called_once_with("192.168.1.1")
            
    def test_connect_failure(self):
        """Test robot connection failure."""
        with patch('libfrankapy.robot.libfranka') as mock_franka:
            mock_franka.Robot.side_effect = Exception("Connection failed")
            
            with pytest.raises(ConnectionError):
                self.robot.connect("192.168.1.1")
                
    def test_joint_limits_validation(self):
        """Test joint limits validation."""
        # Valid joint angles
        valid_joints = [0, -0.785, 0, -2.356, 0, 1.571, 0.785]
        assert self.robot._validate_joint_limits(valid_joints) is True
        
        # Invalid joint angles (exceeds limits)
        invalid_joints = [0, -3.0, 0, -2.356, 0, 1.571, 0.785]
        assert self.robot._validate_joint_limits(invalid_joints) is False
        
    @pytest.mark.parametrize("joint_angles,expected", [
        ([0, 0, 0, 0, 0, 0, 0], True),
        ([2.9, -1.8, 2.9, -0.1, 2.9, 3.8, 2.9], True),
        ([3.0, -1.8, 2.9, -0.1, 2.9, 3.8, 2.9], False),  # Exceeds limit
    ])
    def test_joint_validation_parametrized(self, joint_angles, expected):
        """Parametrized test for joint validation."""
        result = self.robot._validate_joint_limits(joint_angles)
        assert result == expected
```

### C++ Unit Tests

```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "libfrankapy/control/joint_controller.h"
#include "libfrankapy/state/robot_state.h"

using namespace libfrankapy;
using ::testing::_;
using ::testing::Return;

class MockRobotInterface : public RobotInterface {
public:
    MOCK_METHOD(bool, sendJointCommand, (const std::array<double, 7>& joints), (override));
    MOCK_METHOD(RobotState, getCurrentState, (), (const, override));
};

class JointControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        mock_robot = std::make_shared<MockRobotInterface>();
        controller = std::make_unique<JointController>(mock_robot);
    }

    std::shared_ptr<MockRobotInterface> mock_robot;
    std::unique_ptr<JointController> controller;
};

TEST_F(JointControllerTest, ValidJointCommand) {
    std::array<double, 7> target_joints = {0, -0.785, 0, -2.356, 0, 1.571, 0.785};
    
    EXPECT_CALL(*mock_robot, sendJointCommand(target_joints))
        .WillOnce(Return(true));
        
    bool result = controller->moveToJoint(target_joints, 5.0);
    EXPECT_TRUE(result);
}

TEST_F(JointControllerTest, InvalidJointLimits) {
    std::array<double, 7> invalid_joints = {5.0, -0.785, 0, -2.356, 0, 1.571, 0.785};
    
    EXPECT_THROW(controller->moveToJoint(invalid_joints, 5.0), std::invalid_argument);
}

TEST_F(JointControllerTest, TrajectoryGeneration) {
    std::array<double, 7> start = {0, 0, 0, 0, 0, 0, 0};
    std::array<double, 7> end = {0, -0.785, 0, -2.356, 0, 1.571, 0.785};
    
    auto trajectory = controller->generateTrajectory(start, end, 5.0);
    
    EXPECT_GT(trajectory.size(), 0);
    EXPECT_EQ(trajectory.front().joints, start);
    EXPECT_EQ(trajectory.back().joints, end);
}
```

## Integration Testing

### Robot Control Integration

```python
import pytest
import time
from libfrankapy import FrankaRobot
from libfrankapy.control import JointController, CartesianController
from libfrankapy.state import RobotState

@pytest.mark.integration
class TestRobotControlIntegration:
    """Integration tests for robot control."""
    
    @pytest.fixture(autouse=True)
    def setup_robot(self, robot_simulator):
        """Setup robot for integration tests."""
        self.robot = FrankaRobot()
        self.robot.connect(robot_simulator.ip_address)
        yield
        self.robot.disconnect()
        
    def test_joint_to_cartesian_control_flow(self):
        """Test switching between joint and Cartesian control."""
        # Start with joint control
        joint_controller = JointController(self.robot)
        home_joints = [0, -0.785, 0, -2.356, 0, 1.571, 0.785]
        
        joint_controller.move_to_joint(home_joints, duration=3.0)
        
        # Verify position reached
        state = self.robot.get_state()
        np.testing.assert_allclose(state.joint_positions, home_joints, atol=0.01)
        
        # Switch to Cartesian control
        cartesian_controller = CartesianController(self.robot)
        current_pose = state.cartesian_pose
        target_pose = current_pose.copy()
        target_pose[2] += 0.1  # Move up 10cm
        
        cartesian_controller.move_to_pose(target_pose, duration=2.0)
        
        # Verify Cartesian position
        final_state = self.robot.get_state()
        np.testing.assert_allclose(
            final_state.cartesian_pose[:3], 
            target_pose[:3], 
            atol=0.005
        )
        
    def test_state_monitoring_during_motion(self):
        """Test state monitoring during robot motion."""
        states = []
        
        def state_callback(state: RobotState):
            states.append(state.copy())
            
        # Start state monitoring
        self.robot.start_state_monitoring(state_callback, frequency=100)
        
        # Execute motion
        target_joints = [0.1, -0.785, 0.1, -2.356, 0.1, 1.571, 0.785]
        self.robot.move_to_joint(target_joints, duration=5.0)
        
        # Stop monitoring
        self.robot.stop_state_monitoring()
        
        # Verify state data
        assert len(states) > 400  # Should have ~500 states for 5 seconds
        
        # Check state progression
        start_state = states[0]
        end_state = states[-1]
        
        # Verify motion occurred
        joint_diff = np.abs(np.array(end_state.joint_positions) - 
                           np.array(start_state.joint_positions))
        assert np.any(joint_diff > 0.05)  # Significant motion occurred
```

## System Testing

### Full Workflow Tests

```python
@pytest.mark.system
@pytest.mark.slow
class TestFullWorkflow:
    """System tests for complete workflows."""
    
    def test_pick_and_place_workflow(self, robot_with_gripper):
        """Test complete pick and place workflow."""
        robot = robot_with_gripper
        
        # Define positions
        home_position = [0, -0.785, 0, -2.356, 0, 1.571, 0.785]
        pick_position = [0.5, 0.0, 0.2]  # Above object
        place_position = [0.3, 0.3, 0.2]  # Target location
        
        # 1. Move to home position
        robot.move_to_joint(home_position, duration=3.0)
        
        # 2. Move to pick position
        robot.move_to_cartesian(pick_position, duration=2.0)
        
        # 3. Lower to grasp
        grasp_position = pick_position.copy()
        grasp_position[2] -= 0.05  # Lower 5cm
        robot.move_to_cartesian(grasp_position, duration=1.0)
        
        # 4. Close gripper
        robot.gripper.close()
        time.sleep(0.5)
        
        # 5. Lift object
        robot.move_to_cartesian(pick_position, duration=1.0)
        
        # 6. Move to place position
        robot.move_to_cartesian(place_position, duration=3.0)
        
        # 7. Lower object
        place_down_position = place_position.copy()
        place_down_position[2] -= 0.05
        robot.move_to_cartesian(place_down_position, duration=1.0)
        
        # 8. Open gripper
        robot.gripper.open()
        time.sleep(0.5)
        
        # 9. Lift and return home
        robot.move_to_cartesian(place_position, duration=1.0)
        robot.move_to_joint(home_position, duration=3.0)
        
        # Verify final position
        final_state = robot.get_state()
        np.testing.assert_allclose(
            final_state.joint_positions, 
            home_position, 
            atol=0.01
        )
```

## Performance Testing

### Latency Tests

```python
@pytest.mark.performance
class TestPerformance:
    """Performance tests for libfrankapy."""
    
    def test_command_latency(self, robot):
        """Test command execution latency."""
        latencies = []
        
        for _ in range(100):
            start_time = time.perf_counter()
            
            # Send simple joint command
            robot.set_joint_velocities([0.1, 0, 0, 0, 0, 0, 0])
            
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000)  # Convert to ms
            
        avg_latency = np.mean(latencies)
        max_latency = np.max(latencies)
        
        # Performance requirements
        assert avg_latency < 1.0, f"Average latency {avg_latency:.2f}ms exceeds 1ms"
        assert max_latency < 5.0, f"Max latency {max_latency:.2f}ms exceeds 5ms"
        
    def test_state_update_frequency(self, robot):
        """Test state update frequency."""
        states = []
        start_time = time.time()
        
        def state_callback(state):
            states.append((time.time(), state))
            
        robot.start_state_monitoring(state_callback, frequency=1000)
        time.sleep(5.0)  # Collect for 5 seconds
        robot.stop_state_monitoring()
        
        # Calculate actual frequency
        timestamps = [s[0] for s in states]
        intervals = np.diff(timestamps)
        avg_frequency = 1.0 / np.mean(intervals)
        
        # Should be close to requested 1000 Hz
        assert avg_frequency > 950, f"Frequency {avg_frequency:.1f}Hz below target"
        assert avg_frequency < 1050, f"Frequency {avg_frequency:.1f}Hz above target"
```

### Memory and Resource Tests

```python
import psutil
import gc

@pytest.mark.performance
class TestMemoryUsage:
    """Memory usage and resource tests."""
    
    def test_memory_leak_detection(self, robot):
        """Test for memory leaks during extended operation."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(1000):
            # Create and destroy objects
            state = robot.get_state()
            joints = state.joint_positions
            
            # Trigger garbage collection periodically
            if i % 100 == 0:
                gc.collect()
                
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 10MB)
        assert memory_increase < 10 * 1024 * 1024, \
            f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"
            
    def test_resource_cleanup(self, robot):
        """Test proper resource cleanup."""
        initial_handles = len(psutil.Process().open_files())
        
        # Create and destroy many robot connections
        for _ in range(10):
            temp_robot = FrankaRobot()
            temp_robot.connect("192.168.1.1")
            temp_robot.disconnect()
            del temp_robot
            
        gc.collect()
        final_handles = len(psutil.Process().open_files())
        
        # File handle count should not increase significantly
        assert final_handles <= initial_handles + 2, \
            f"File handles increased from {initial_handles} to {final_handles}"
```

## Test Configuration

### Pytest Configuration

```python
# conftest.py
import pytest
import numpy as np
from unittest.mock import Mock
from libfrankapy import FrankaRobot
from libfrankapy.simulation import RobotSimulator

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "system: mark test as system test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring real hardware"
    )

@pytest.fixture(scope="session")
def robot_simulator():
    """Provide robot simulator for testing."""
    simulator = RobotSimulator()
    simulator.start()
    yield simulator
    simulator.stop()

@pytest.fixture
def mock_robot():
    """Provide mock robot for unit testing."""
    robot = Mock(spec=FrankaRobot)
    robot.is_connected = True
    robot.get_state.return_value = create_mock_state()
    return robot

def create_mock_state():
    """Create mock robot state."""
    state = Mock()
    state.joint_positions = [0, -0.785, 0, -2.356, 0, 1.571, 0.785]
    state.cartesian_pose = [0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0]
    state.external_force = [0, 0, 0, 0, 0, 0]
    state.timestamp = 0.0
    return state
```

### Test Data and Fixtures

```python
# fixtures/robot_configurations.py
import numpy as np

# Standard robot configurations
HOME_POSITION = [0, -0.785, 0, -2.356, 0, 1.571, 0.785]
READY_POSITION = [0, -0.785, 0, -1.571, 0, 1.571, 0]
EXTENDED_POSITION = [0, 0, 0, -1.571, 0, 1.571, 0]

# Test trajectories
SIMPLE_TRAJECTORY = [
    [0, -0.785, 0, -2.356, 0, 1.571, 0.785],
    [0.1, -0.785, 0, -2.356, 0, 1.571, 0.785],
    [0.2, -0.785, 0, -2.356, 0, 1.571, 0.785],
]

# Cartesian poses
WORKSPACE_POSES = [
    [0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0],  # Center
    [0.3, 0.3, 0.3, 1.0, 0.0, 0.0, 0.0],  # Corner
    [0.7, 0.0, 0.3, 1.0, 0.0, 0.0, 0.0],  # Extended
]
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=libfrankapy --cov-report=xml
        
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Test Configuration Files

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
    hardware: Tests requiring real hardware
```

```toml
# pyproject.toml
[tool.coverage.run]
source = ["libfrankapy"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Test Reporting

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=libfrankapy --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Generate XML report for CI
pytest --cov=libfrankapy --cov-report=xml
```

### Performance Reports

```bash
# Run performance tests with profiling
pytest tests/performance/ --profile --profile-svg

# Generate performance report
python scripts/generate_performance_report.py

# Benchmark comparison
pytest-benchmark compare
```

### Test Result Analysis

```python
# scripts/analyze_test_results.py
import json
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_test_results(results_file):
    """Analyze test results and generate reports."""
    with open(results_file) as f:
        results = json.load(f)
    
    # Extract metrics
    total_tests = results['summary']['total']
    passed_tests = results['summary']['passed']
    failed_tests = results['summary']['failed']
    
    # Generate plots
    plt.figure(figsize=(10, 6))
    
    # Test results pie chart
    plt.subplot(1, 2, 1)
    plt.pie([passed_tests, failed_tests], 
            labels=['Passed', 'Failed'],
            colors=['green', 'red'],
            autopct='%1.1f%%')
    plt.title('Test Results')
    
    # Performance trends
    plt.subplot(1, 2, 2)
    # Plot performance data...
    
    plt.tight_layout()
    plt.savefig('test_results.png')
    
if __name__ == '__main__':
    analyze_test_results('test_results.json')
```

## Best Practices

### Test Writing

- **Write descriptive test names**: Use clear, descriptive names that explain what is being tested
- **Use arrange-act-assert pattern**: Structure tests with clear setup, execution, and verification phases
- **Test one thing per test**: Each test should focus on a single behavior or outcome
- **Use parametrized tests for multiple inputs**: Reduce code duplication with pytest.mark.parametrize
- **Mock external dependencies**: Isolate units under test from external systems
- **Clean up resources in teardown**: Ensure proper cleanup to prevent test interference

### Safety Testing

- **Test all safety limits**: Verify joint limits, workspace boundaries, force limits
- **Verify emergency stop functionality**: Test emergency stop in various scenarios
- **Test error recovery scenarios**: Ensure proper recovery from error conditions
- **Validate workspace boundaries**: Test behavior at workspace limits
- **Test force/torque limits**: Verify safety limits are enforced

### Performance Testing

- **Establish performance baselines**: Set clear performance expectations
- **Test under realistic conditions**: Use realistic loads and scenarios
- **Monitor for regressions**: Track performance over time
- **Profile critical paths**: Identify and optimize bottlenecks
- **Test memory usage patterns**: Detect memory leaks and excessive usage

### Test Maintenance

- **Keep tests up to date**: Update tests when code changes
- **Remove obsolete tests**: Clean up tests for removed functionality
- **Refactor test code**: Apply same quality standards to test code
- **Document test requirements**: Explain complex test setups and requirements
- **Review test coverage**: Regularly assess and improve test coverage

## Running Tests

### Local Development

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/system/
pytest tests/performance/

# Run tests with specific markers
pytest -m "not slow"
pytest -m "unit or integration"
pytest -m performance

# Run tests with coverage
pytest --cov=libfrankapy --cov-report=html

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_robot.py

# Run specific test method
pytest tests/unit/test_robot.py::TestFrankaRobot::test_connect_success
```

### Continuous Integration

```bash
# Full CI test suite
pytest tests/ --cov=libfrankapy --cov-report=xml --junitxml=test-results.xml

# Performance regression tests
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

# Safety validation tests
pytest tests/system/test_safety_systems.py -v
```

### Test Environment Setup

```bash
# Setup test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install -e ".[test]"

# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-benchmark

# Setup robot simulator for testing
python scripts/setup_test_robot.py
```

## Troubleshooting Tests

### Common Issues

**Test Failures**
- Check test dependencies and setup
- Verify mock configurations
- Review test data and fixtures
- Check for timing issues in integration tests

**Performance Test Issues**
- Ensure consistent test environment
- Check for background processes affecting performance
- Verify hardware requirements are met
- Review performance baselines

**CI/CD Issues**
- Check environment variables and secrets
- Verify dependency installation
- Review platform-specific issues
- Check test timeouts and resource limits

### Debugging Tests

```python
# Add debugging to tests
import pytest
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Use pytest debugging
pytest --pdb  # Drop into debugger on failure
pytest --pdbcls=IPython.terminal.debugger:Pdb  # Use IPython debugger

# Add print statements for debugging
def test_debug_example():
    result = some_function()
    print(f"Debug: result = {result}")  # Will be captured by pytest
    assert result == expected

# Use pytest fixtures for debugging
@pytest.fixture
def debug_robot(robot):
    robot.enable_debug_logging()
    yield robot
    robot.disable_debug_logging()
```

## See Also

- [Architecture Guide](/development/architecture) - System architecture overview
- [Contributing Guide](/development/contributing) - How to contribute to the project
- [API Reference](/api/) - Detailed API documentation
- [Examples](/examples) - Usage examples and tutorials
