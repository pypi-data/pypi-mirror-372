Exceptions API
==============

The exceptions module defines custom exception classes for error handling in libfrankapy.

.. currentmodule:: libfrankapy.exceptions

Exception Hierarchy
-------------------

libfrankapy uses a hierarchical exception system to provide detailed error information:

.. code-block:: text

   Exception
   └── FrankaException
       ├── ConnectionError
       ├── ControlError
       │   ├── JointLimitError
       │   ├── VelocityLimitError
       │   ├── AccelerationLimitError
       │   ├── ForceLimitError
       │   └── CollisionError
       ├── SafetyError
       │   ├── ProtectiveStopError
       │   ├── EmergencyStopError
       │   └── SafetyLimitError
       ├── CommunicationError
       ├── ConfigurationError
       └── RobotError
           ├── HardwareError
           ├── SoftwareError
           └── CalibrationError

Base Exception Classes
----------------------

FrankaException
^^^^^^^^^^^^^^^

.. autoclass:: FrankaException
   :members:
   :undoc-members:
   :show-inheritance:

Base exception class for all libfrankapy exceptions.

.. code-block:: python

   import libfrankapy as fp
   
   try:
       robot = fp.FrankaRobot("192.168.1.100")
       robot.connect()
   except fp.FrankaException as e:
       print(f"Franka error: {e}")
       print(f"Error code: {e.error_code}")
       print(f"Error details: {e.details}")

Connection Exceptions
---------------------

ConnectionError
^^^^^^^^^^^^^^^

.. autoclass:: ConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when connection to the robot fails.

.. code-block:: python

   try:
       robot = fp.FrankaRobot("192.168.1.100")
       robot.connect()
   except fp.ConnectionError as e:
       print(f"Failed to connect to robot: {e}")
       # Try alternative connection or notify user

CommunicationError
^^^^^^^^^^^^^^^^^^

.. autoclass:: CommunicationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when communication with the robot is lost or corrupted.

.. code-block:: python

   try:
       state = robot.get_robot_state()
   except fp.CommunicationError as e:
       print(f"Communication error: {e}")
       # Attempt to reconnect
       robot.reconnect()

Control Exceptions
------------------

ControlError
^^^^^^^^^^^^

.. autoclass:: ControlError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for control-related errors.

JointLimitError
^^^^^^^^^^^^^^^

.. autoclass:: JointLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when joint limits are exceeded.

.. code-block:: python

   try:
       # This will exceed joint limits
       invalid_joints = [5.0, 0, 0, 0, 0, 0, 0]
       robot.move_to_joint(invalid_joints)
   except fp.JointLimitError as e:
       print(f"Joint limit exceeded: {e}")
       print(f"Violating joint: {e.joint_index}")
       print(f"Attempted value: {e.attempted_value}")
       print(f"Limit: {e.limit_value}")

VelocityLimitError
^^^^^^^^^^^^^^^^^^

.. autoclass:: VelocityLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when velocity limits are exceeded.

.. code-block:: python

   try:
       # Move too fast
       robot.move_to_joint(target_joints, speed_factor=2.0)
   except fp.VelocityLimitError as e:
       print(f"Velocity limit exceeded: {e}")
       # Reduce speed and retry
       robot.move_to_joint(target_joints, speed_factor=0.5)

AccelerationLimitError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: AccelerationLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when acceleration limits are exceeded.

ForceLimitError
^^^^^^^^^^^^^^^

.. autoclass:: ForceLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when force or torque limits are exceeded.

.. code-block:: python

   try:
       # Apply excessive force
       high_force = [0, 0, -100.0, 0, 0, 0]  # 100N downward
       robot.set_cartesian_force(high_force)
   except fp.ForceLimitError as e:
       print(f"Force limit exceeded: {e}")
       print(f"Applied force: {e.applied_force}")
       print(f"Force limit: {e.force_limit}")

CollisionError
^^^^^^^^^^^^^^

.. autoclass:: CollisionError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when a collision is detected.

.. code-block:: python

   try:
       robot.move_to_pose(target_pose)
   except fp.CollisionError as e:
       print(f"Collision detected: {e}")
       print(f"Collision forces: {e.collision_forces}")
       
       # Stop motion and recover
       robot.stop_motion()
       robot.recover_from_errors()

Safety Exceptions
-----------------

SafetyError
^^^^^^^^^^^

.. autoclass:: SafetyError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for safety-related errors.

ProtectiveStopError
^^^^^^^^^^^^^^^^^^^

.. autoclass:: ProtectiveStopError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when the robot enters protective stop mode.

.. code-block:: python

   try:
       robot.move_to_joint(target_joints)
   except fp.ProtectiveStopError as e:
       print(f"Protective stop triggered: {e}")
       print(f"Reason: {e.stop_reason}")
       
       # Wait and attempt recovery
       time.sleep(1.0)
       robot.recover_from_errors()

EmergencyStopError
^^^^^^^^^^^^^^^^^^

.. autoclass:: EmergencyStopError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when emergency stop is activated.

.. code-block:: python

   try:
       robot.move_to_joint(target_joints)
   except fp.EmergencyStopError as e:
       print(f"Emergency stop activated: {e}")
       # Manual intervention required
       print("Please release emergency stop and restart robot")

SafetyLimitError
^^^^^^^^^^^^^^^^

.. autoclass:: SafetyLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when safety limits are violated.

Configuration Exceptions
-------------------------

ConfigurationError
^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when configuration parameters are invalid.

.. code-block:: python

   try:
       config = fp.JointControlConfig(
           max_velocity=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]  # Too high
       )
   except fp.ConfigurationError as e:
       print(f"Invalid configuration: {e}")
       print(f"Parameter: {e.parameter_name}")
       print(f"Value: {e.parameter_value}")
       print(f"Valid range: {e.valid_range}")

Robot Exceptions
----------------

RobotError
^^^^^^^^^^

.. autoclass:: RobotError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for robot hardware/software errors.

HardwareError
^^^^^^^^^^^^^

.. autoclass:: HardwareError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when hardware errors occur.

.. code-block:: python

   try:
       robot.start_control()
   except fp.HardwareError as e:
       print(f"Hardware error: {e}")
       print(f"Component: {e.component}")
       print(f"Error details: {e.hardware_details}")
       # May require hardware inspection

SoftwareError
^^^^^^^^^^^^^

.. autoclass:: SoftwareError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when software errors occur.

CalibrationError
^^^^^^^^^^^^^^^^

.. autoclass:: CalibrationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when calibration issues are detected.

Utility Functions
-----------------

Error Handling Utilities
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: get_error_description
.. autofunction:: is_recoverable_error
.. autofunction:: suggest_recovery_action
.. autofunction:: log_error

Error Recovery
^^^^^^^^^^^^^^

.. autofunction:: attempt_error_recovery
.. autofunction:: reset_robot_state
.. autofunction:: clear_error_history

Examples
--------

Comprehensive Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   import time
   
   def robust_robot_control():
       robot = fp.FrankaRobot("192.168.1.100")
       max_retries = 3
       retry_count = 0
       
       while retry_count < max_retries:
           try:
               # Attempt connection
               robot.connect()
               robot.start_control()
               
               # Perform robot operations
               target_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
               robot.move_to_joint(target_joints, speed_factor=0.1)
               
               print("Operation completed successfully")
               break
               
           except fp.ConnectionError as e:
               print(f"Connection failed (attempt {retry_count + 1}): {e}")
               retry_count += 1
               time.sleep(2.0)  # Wait before retry
               
           except fp.JointLimitError as e:
               print(f"Joint limit error: {e}")
               print(f"Violating joint {e.joint_index}: {e.attempted_value}")
               # Modify target and retry
               target_joints[e.joint_index] = e.limit_value * 0.9
               
           except fp.CollisionError as e:
               print(f"Collision detected: {e}")
               robot.stop_motion()
               robot.recover_from_errors()
               print("Recovered from collision, stopping operation")
               break
               
           except fp.ProtectiveStopError as e:
               print(f"Protective stop: {e}")
               time.sleep(1.0)
               robot.recover_from_errors()
               
           except fp.EmergencyStopError as e:
               print(f"Emergency stop: {e}")
               print("Manual intervention required")
               break
               
           except fp.FrankaException as e:
               print(f"General Franka error: {e}")
               if fp.is_recoverable_error(e):
                   print("Attempting recovery...")
                   robot.recover_from_errors()
               else:
                   print("Non-recoverable error, stopping")
                   break
               
           except Exception as e:
               print(f"Unexpected error: {e}")
               break
               
           finally:
               # Always clean up
               try:
                   robot.stop_control()
                   robot.disconnect()
               except:
                   pass
       
       if retry_count >= max_retries:
           print("Maximum retries exceeded")

Specific Error Handling
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   
   def handle_specific_errors():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Potentially problematic operations
           operations = [
               lambda: robot.move_to_joint([5.0, 0, 0, 0, 0, 0, 0]),  # Joint limit
               lambda: robot.set_cartesian_force([0, 0, -100, 0, 0, 0]),  # Force limit
               lambda: robot.move_to_joint(target, speed_factor=2.0),  # Velocity limit
           ]
           
           for i, operation in enumerate(operations):
               try:
                   print(f"Executing operation {i + 1}...")
                   operation()
                   
               except fp.JointLimitError as e:
                   print(f"Joint limit error in operation {i + 1}:")
                   print(f"  Joint {e.joint_index}: {e.attempted_value} > {e.limit_value}")
                   
               except fp.ForceLimitError as e:
                   print(f"Force limit error in operation {i + 1}:")
                   print(f"  Applied: {e.applied_force}, Limit: {e.force_limit}")
                   
               except fp.VelocityLimitError as e:
                   print(f"Velocity limit error in operation {i + 1}:")
                   print(f"  Requested speed factor: {e.speed_factor}")
                   
       finally:
           robot.stop_control()
           robot.disconnect()

Error Logging and Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   import logging
   import json
   from datetime import datetime
   
   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('robot_errors.log'),
           logging.StreamHandler()
       ]
   )
   
   def log_robot_errors():
       robot = fp.FrankaRobot("192.168.1.100")
       error_history = []
       
       try:
           robot.connect()
           robot.start_control()
           
           # Simulate various operations that might fail
           risky_operations = [
               ("joint_limit_test", lambda: robot.move_to_joint([5.0, 0, 0, 0, 0, 0, 0])),
               ("force_test", lambda: robot.set_cartesian_force([0, 0, -50, 0, 0, 0])),
               ("speed_test", lambda: robot.move_to_joint(target, speed_factor=1.5)),
           ]
           
           for operation_name, operation in risky_operations:
               try:
                   logging.info(f"Starting operation: {operation_name}")
                   operation()
                   logging.info(f"Operation {operation_name} completed successfully")
                   
               except fp.FrankaException as e:
                   # Log error details
                   error_info = {
                       'timestamp': datetime.now().isoformat(),
                       'operation': operation_name,
                       'error_type': type(e).__name__,
                       'error_message': str(e),
                       'error_code': getattr(e, 'error_code', None),
                       'details': getattr(e, 'details', {})
                   }
                   
                   error_history.append(error_info)
                   
                   logging.error(f"Error in {operation_name}: {e}")
                   logging.error(f"Error details: {json.dumps(error_info, indent=2)}")
                   
                   # Attempt recovery if possible
                   if fp.is_recoverable_error(e):
                       logging.info("Attempting error recovery...")
                       robot.recover_from_errors()
                       logging.info("Recovery completed")
                   else:
                       logging.warning("Error is not recoverable")
       
       finally:
           robot.stop_control()
           robot.disconnect()
           
           # Save error history
           with open('error_history.json', 'w') as f:
               json.dump(error_history, f, indent=2)
           
           logging.info(f"Session completed. {len(error_history)} errors logged.")

Custom Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   
   class RobotOperationManager:
       def __init__(self, robot_ip):
           self.robot = fp.FrankaRobot(robot_ip)
           self.error_count = 0
           self.max_errors = 5
       
       def safe_execute(self, operation, operation_name="unknown"):
           """Safely execute a robot operation with error handling."""
           try:
               result = operation()
               print(f"Operation '{operation_name}' completed successfully")
               return result
               
           except fp.EmergencyStopError:
               print("EMERGENCY STOP - Manual intervention required")
               raise  # Re-raise emergency stop
               
           except fp.CollisionError as e:
               print(f"Collision detected during '{operation_name}': {e}")
               self.robot.stop_motion()
               self.robot.recover_from_errors()
               return None
               
           except fp.SafetyError as e:
               print(f"Safety error during '{operation_name}': {e}")
               self.robot.recover_from_errors()
               return None
               
           except fp.ControlError as e:
               print(f"Control error during '{operation_name}': {e}")
               self.error_count += 1
               
               if self.error_count >= self.max_errors:
                   print("Too many control errors, stopping operations")
                   raise
               
               return None
               
           except fp.FrankaException as e:
               print(f"Franka error during '{operation_name}': {e}")
               self.error_count += 1
               return None
       
       def execute_sequence(self, operations):
           """Execute a sequence of operations with error handling."""
           results = []
           
           for i, (name, operation) in enumerate(operations):
               print(f"Executing step {i+1}: {name}")
               result = self.safe_execute(operation, name)
               results.append(result)
               
               if result is None:
                   print(f"Step {i+1} failed, continuing with next step")
           
           return results
   
   # Usage example
   def main():
       manager = RobotOperationManager("192.168.1.100")
       
       try:
           manager.robot.connect()
           manager.robot.start_control()
           
           operations = [
               ("move_to_home", lambda: manager.robot.move_to_joint([0, -0.785, 0, -2.356, 0, 1.571, 0.785])),
               ("move_up", lambda: manager.robot.move_to_pose(get_raised_pose(), speed_factor=0.1)),
               ("apply_force", lambda: manager.robot.set_cartesian_force([0, 0, -5, 0, 0, 0])),
           ]
           
           results = manager.execute_sequence(operations)
           print(f"Sequence completed. Results: {results}")
           
       finally:
           manager.robot.stop_control()
           manager.robot.disconnect()

See Also
--------

* :doc:`robot` - Main robot interface
* :doc:`control` - Control interfaces
* :doc:`state` - Robot state information
* :doc:`../examples` - Error handling examples