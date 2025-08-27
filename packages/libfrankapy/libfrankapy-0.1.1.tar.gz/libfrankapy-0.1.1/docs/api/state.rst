State API
=========

The state module provides classes and functions for representing and accessing robot state information.

.. currentmodule:: libfrankapy.state

State Classes
-------------

RobotState
^^^^^^^^^^

.. autoclass:: RobotState
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`RobotState` class contains complete robot state information including joint states, Cartesian pose, forces, and system status.

.. code-block:: python

   import libfrankapy as fp
   
   robot = fp.FrankaRobot("192.168.1.100")
   robot.connect()
   robot.start_control()
   
   # Get complete robot state
   state = robot.get_robot_state()
   print(f"Joint positions: {state.joint_state.positions}")
   print(f"End-effector pose: {state.cartesian_state.pose}")
   print(f"Contact forces: {state.cartesian_state.forces}")

JointState
^^^^^^^^^^

.. autoclass:: JointState
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`JointState` class represents joint-space state information.

.. code-block:: python

   # Access joint state information
   joint_state = state.joint_state
   
   print(f"Positions: {joint_state.positions}")  # 7 joint angles in radians
   print(f"Velocities: {joint_state.velocities}")  # 7 joint velocities in rad/s
   print(f"Torques: {joint_state.torques}")  # 7 joint torques in Nm
   print(f"Desired torques: {joint_state.desired_torques}")

CartesianState
^^^^^^^^^^^^^^

.. autoclass:: CartesianState
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`CartesianState` class represents Cartesian-space state information.

.. code-block:: python

   # Access Cartesian state information
   cartesian_state = state.cartesian_state
   
   print(f"Pose matrix: {cartesian_state.pose}")  # 4x4 transformation matrix
   print(f"Position: {cartesian_state.position}")  # [x, y, z] in meters
   print(f"Orientation: {cartesian_state.orientation}")  # Quaternion [w, x, y, z]
   print(f"Linear velocity: {cartesian_state.linear_velocity}")  # [vx, vy, vz] in m/s
   print(f"Angular velocity: {cartesian_state.angular_velocity}")  # [wx, wy, wz] in rad/s
   print(f"Forces: {cartesian_state.forces}")  # [fx, fy, fz, tx, ty, tz]

ForceState
^^^^^^^^^^

.. autoclass:: ForceState
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`ForceState` class represents force and torque information.

.. code-block:: python

   # Access force state information
   force_state = state.force_state
   
   print(f"External forces: {force_state.external_forces}")  # Forces from environment
   print(f"Contact forces: {force_state.contact_forces}")  # Detected contact forces
   print(f"Joint torques: {force_state.joint_torques}")  # Measured joint torques
   print(f"Gravity compensation: {force_state.gravity_torques}")  # Gravity compensation torques

SystemState
^^^^^^^^^^^

.. autoclass:: SystemState
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`SystemState` class represents system status and error information.

.. code-block:: python

   # Access system state information
   system_state = state.system_state
   
   print(f"Control mode: {system_state.control_mode}")
   print(f"Robot mode: {system_state.robot_mode}")
   print(f"Safety state: {system_state.safety_state}")
   print(f"Errors: {system_state.errors}")
   print(f"Warnings: {system_state.warnings}")

Utility Classes
---------------

Pose
^^^^

.. autoclass:: Pose
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`Pose` class provides utilities for working with 6D poses.

.. code-block:: python

   from libfrankapy.state import Pose
   import numpy as np
   
   # Create pose from position and orientation
   position = [0.5, 0.0, 0.3]  # meters
   orientation = [0, 0, 0, 1]  # quaternion [x, y, z, w]
   
   pose = Pose.from_position_quaternion(position, orientation)
   print(f"Transformation matrix:\n{pose.matrix}")
   
   # Convert between representations
   euler_angles = pose.to_euler_angles()  # Roll, pitch, yaw
   axis_angle = pose.to_axis_angle()  # Axis-angle representation

Transform
^^^^^^^^^

.. autoclass:: Transform
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`Transform` class provides utilities for coordinate transformations.

.. code-block:: python

   from libfrankapy.state import Transform
   
   # Create transform
   transform = Transform.from_matrix(pose_matrix)
   
   # Apply transform to points
   point = [0.1, 0.2, 0.3]
   transformed_point = transform.apply_to_point(point)
   
   # Compose transforms
   combined_transform = transform1 * transform2

Enumerations
------------

ControlMode
^^^^^^^^^^^

.. autoclass:: ControlMode
   :members:
   :undoc-members:

Enumeration of available control modes.

.. code-block:: python

   from libfrankapy.state import ControlMode
   
   # Check current control mode
   if state.system_state.control_mode == ControlMode.JOINT_POSITION:
       print("Robot is in joint position control mode")
   elif state.system_state.control_mode == ControlMode.CARTESIAN_POSE:
       print("Robot is in Cartesian pose control mode")
   elif state.system_state.control_mode == ControlMode.FORCE_CONTROL:
       print("Robot is in force control mode")

RobotMode
^^^^^^^^^

.. autoclass:: RobotMode
   :members:
   :undoc-members:

Enumeration of robot operational modes.

.. code-block:: python

   from libfrankapy.state import RobotMode
   
   # Check robot mode
   if state.system_state.robot_mode == RobotMode.IDLE:
       print("Robot is idle")
   elif state.system_state.robot_mode == RobotMode.MOVE:
       print("Robot is moving")
   elif state.system_state.robot_mode == RobotMode.GUIDING:
       print("Robot is in guiding mode")

SafetyState
^^^^^^^^^^^

.. autoclass:: SafetyState
   :members:
   :undoc-members:

Enumeration of safety states.

.. code-block:: python

   from libfrankapy.state import SafetyState
   
   # Check safety state
   if state.system_state.safety_state == SafetyState.NORMAL:
       print("Robot is in normal operation")
   elif state.system_state.safety_state == SafetyState.PROTECTIVE_STOP:
       print("Robot is in protective stop")
   elif state.system_state.safety_state == SafetyState.EMERGENCY_STOP:
       print("Robot is in emergency stop")

Utility Functions
-----------------

State Conversion
^^^^^^^^^^^^^^^^

.. autofunction:: joint_state_to_dict
.. autofunction:: cartesian_state_to_dict
.. autofunction:: robot_state_to_dict
.. autofunction:: dict_to_joint_state
.. autofunction:: dict_to_cartesian_state
.. autofunction:: dict_to_robot_state

Pose Utilities
^^^^^^^^^^^^^^

.. autofunction:: matrix_to_pose
.. autofunction:: pose_to_matrix
.. autofunction:: quaternion_to_matrix
.. autofunction:: matrix_to_quaternion
.. autofunction:: euler_to_matrix
.. autofunction:: matrix_to_euler

State Monitoring
^^^^^^^^^^^^^^^^

.. autofunction:: is_motion_finished
.. autofunction:: is_contact_detected
.. autofunction:: is_force_exceeded
.. autofunction:: get_motion_progress

Examples
--------

State Monitoring
^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   import time
   
   def state_monitoring_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Monitor robot state for 10 seconds
           start_time = time.time()
           
           while time.time() - start_time < 10.0:
               state = robot.get_robot_state()
               
               # Print joint information
               joint_pos = state.joint_state.positions
               joint_vel = state.joint_state.velocities
               
               print(f"Joint 1: pos={joint_pos[0]:.3f}, vel={joint_vel[0]:.3f}")
               
               # Print Cartesian information
               ee_pos = state.cartesian_state.position
               ee_forces = state.cartesian_state.forces[:3]
               
               print(f"EE position: {ee_pos}")
               print(f"EE forces: {ee_forces}")
               
               # Check for contact
               force_magnitude = np.linalg.norm(ee_forces)
               if force_magnitude > 5.0:
                   print("Contact detected!")
               
               time.sleep(0.1)  # 10Hz monitoring
               
       finally:
           robot.stop_control()
           robot.disconnect()

Pose Manipulation
^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   from libfrankapy.state import Pose
   import numpy as np
   
   def pose_manipulation_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Get current pose
           current_state = robot.get_cartesian_state()
           current_pose = Pose.from_matrix(current_state.pose)
           
           print(f"Current position: {current_pose.position}")
           print(f"Current orientation (euler): {current_pose.to_euler_angles()}")
           
           # Create relative motion
           relative_translation = [0.1, 0.0, 0.0]  # 10cm in X
           relative_rotation = [0.0, 0.0, 0.1]  # 0.1 rad around Z
           
           # Apply relative motion
           new_pose = current_pose.copy()
           new_pose.translate(relative_translation)
           new_pose.rotate_euler(relative_rotation)
           
           # Move to new pose
           robot.move_to_pose(new_pose.matrix, speed_factor=0.1)
           
       finally:
           robot.stop_control()
           robot.disconnect()

Force Analysis
^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   import numpy as np
   import matplotlib.pyplot as plt
   import time
   
   def force_analysis_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Collect force data
           forces_data = []
           timestamps = []
           
           start_time = time.time()
           
           # Collect data for 5 seconds
           while time.time() - start_time < 5.0:
               state = robot.get_robot_state()
               forces = state.cartesian_state.forces
               
               forces_data.append(forces.copy())
               timestamps.append(time.time() - start_time)
               
               time.sleep(0.01)  # 100Hz sampling
           
           # Analyze force data
           forces_array = np.array(forces_data)
           
           # Calculate statistics
           mean_forces = np.mean(forces_array, axis=0)
           std_forces = np.std(forces_array, axis=0)
           max_forces = np.max(np.abs(forces_array), axis=0)
           
           print(f"Mean forces: {mean_forces[:3]}")
           print(f"Force std dev: {std_forces[:3]}")
           print(f"Max forces: {max_forces[:3]}")
           
           # Plot force data
           plt.figure(figsize=(12, 8))
           
           for i in range(3):
               plt.subplot(2, 2, i+1)
               plt.plot(timestamps, forces_array[:, i])
               plt.title(f'Force {["X", "Y", "Z"][i]}')
               plt.xlabel('Time (s)')
               plt.ylabel('Force (N)')
               plt.grid(True)
           
           # Plot force magnitude
           plt.subplot(2, 2, 4)
           force_magnitude = np.linalg.norm(forces_array[:, :3], axis=1)
           plt.plot(timestamps, force_magnitude)
           plt.title('Force Magnitude')
           plt.xlabel('Time (s)')
           plt.ylabel('Force (N)')
           plt.grid(True)
           
           plt.tight_layout()
           plt.show()
           
       finally:
           robot.stop_control()
           robot.disconnect()

State Logging
^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   import csv
   import time
   
   def state_logging_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Open CSV file for logging
           with open('robot_state_log.csv', 'w', newline='') as csvfile:
               fieldnames = [
                   'timestamp', 'joint_pos_0', 'joint_pos_1', 'joint_pos_2',
                   'joint_pos_3', 'joint_pos_4', 'joint_pos_5', 'joint_pos_6',
                   'ee_pos_x', 'ee_pos_y', 'ee_pos_z',
                   'ee_force_x', 'ee_force_y', 'ee_force_z',
                   'control_mode', 'robot_mode'
               ]
               
               writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
               writer.writeheader()
               
               start_time = time.time()
               
               # Log data for 30 seconds
               while time.time() - start_time < 30.0:
                   state = robot.get_robot_state()
                   
                   # Prepare data row
                   row = {
                       'timestamp': time.time() - start_time,
                       'control_mode': state.system_state.control_mode.name,
                       'robot_mode': state.system_state.robot_mode.name
                   }
                   
                   # Add joint positions
                   for i, pos in enumerate(state.joint_state.positions):
                       row[f'joint_pos_{i}'] = pos
                   
                   # Add end-effector position
                   ee_pos = state.cartesian_state.position
                   row['ee_pos_x'] = ee_pos[0]
                   row['ee_pos_y'] = ee_pos[1]
                   row['ee_pos_z'] = ee_pos[2]
                   
                   # Add forces
                   forces = state.cartesian_state.forces
                   row['ee_force_x'] = forces[0]
                   row['ee_force_y'] = forces[1]
                   row['ee_force_z'] = forces[2]
                   
                   writer.writerow(row)
                   
                   time.sleep(0.01)  # 100Hz logging
           
           print("State logging completed. Data saved to robot_state_log.csv")
           
       finally:
           robot.stop_control()
           robot.disconnect()

See Also
--------

* :doc:`robot` - Main robot interface
* :doc:`control` - Control interfaces
* :doc:`exceptions` - Exception handling
* :doc:`../examples` - More state