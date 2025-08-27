Robot API
=========

The :class:`FrankaRobot` class is the main interface for controlling Franka robots.

.. currentmodule:: libfrankapy

FrankaRobot Class
-----------------

.. autoclass:: FrankaRobot
   :members:
   :undoc-members:
   :show-inheritance:

Class Overview
^^^^^^^^^^^^^^

The :class:`FrankaRobot` class provides a high-level Python interface for controlling Franka robotic arms. It handles connection management, real-time control, safety monitoring, and state feedback.

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   
   # Create robot instance
   robot = fp.FrankaRobot("192.168.1.100")
   
   # Connect and start control
   robot.connect()
   robot.start_control()
   
   try:
       # Your control code here
       state = robot.get_robot_state()
       print(f"Current position: {state.joint_state.positions}")
   finally:
       robot.stop_control()
       robot.disconnect()

Constructor
^^^^^^^^^^^

.. automethod:: FrankaRobot.__init__

Connection Management
^^^^^^^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.connect
.. automethod:: FrankaRobot.disconnect
.. automethod:: FrankaRobot.is_connected
.. automethod:: FrankaRobot.start_control
.. automethod:: FrankaRobot.stop_control
.. automethod:: FrankaRobot.is_control_active

State Information
^^^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.get_robot_state
.. automethod:: FrankaRobot.get_joint_state
.. automethod:: FrankaRobot.get_cartesian_state
.. automethod:: FrankaRobot.get_force_state
.. automethod:: FrankaRobot.get_robot_model

Joint Space Control
^^^^^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.move_to_joint
.. automethod:: FrankaRobot.set_joint_position
.. automethod:: FrankaRobot.set_joint_velocity
.. automethod:: FrankaRobot.set_joint_torque
.. automethod:: FrankaRobot.execute_joint_trajectory

Cartesian Space Control
^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.move_to_pose
.. automethod:: FrankaRobot.set_cartesian_pose
.. automethod:: FrankaRobot.set_cartesian_velocity
.. automethod:: FrankaRobot.set_cartesian_force
.. automethod:: FrankaRobot.execute_cartesian_trajectory

Force Control
^^^^^^^^^^^^^

.. automethod:: FrankaRobot.start_force_control
.. automethod:: FrankaRobot.stop_force_control
.. automethod:: FrankaRobot.set_force_torque
.. automethod:: FrankaRobot.set_impedance_control

Safety and Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.recover_from_errors
.. automethod:: FrankaRobot.get_last_error
.. automethod:: FrankaRobot.clear_errors
.. automethod:: FrankaRobot.emergency_stop
.. automethod:: FrankaRobot.is_in_error_state

Configuration
^^^^^^^^^^^^^

.. automethod:: FrankaRobot.set_joint_control_config
.. automethod:: FrankaRobot.set_cartesian_control_config
.. automethod:: FrankaRobot.set_safety_config
.. automethod:: FrankaRobot.set_realtime_config
.. automethod:: FrankaRobot.get_config

Utility Methods
^^^^^^^^^^^^^^^

.. automethod:: FrankaRobot.home
.. automethod:: FrankaRobot.get_jacobian
.. automethod:: FrankaRobot.forward_kinematics
.. automethod:: FrankaRobot.inverse_kinematics
.. automethod:: FrankaRobot.get_mass_matrix
.. automethod:: FrankaRobot.get_coriolis_forces
.. automethod:: FrankaRobot.get_gravity_forces

Properties
^^^^^^^^^^

.. autoproperty:: FrankaRobot.ip_address
.. autoproperty:: FrankaRobot.is_connected
.. autoproperty:: FrankaRobot.is_control_active
.. autoproperty:: FrankaRobot.control_mode
.. autoproperty:: FrankaRobot.robot_model

Examples
^^^^^^^^

Basic Robot Control
"""""""""""""""""""

.. code-block:: python

   import libfrankapy as fp
   import numpy as np
   
   def basic_control_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Get current state
           state = robot.get_robot_state()
           print(f"Current joints: {state.joint_state.positions}")
           
           # Move to home position
           home_joints = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
           robot.move_to_joint(home_joints, speed_factor=0.1)
           
           # Get current end-effector pose
           current_pose = robot.get_cartesian_state().pose
           print(f"Current pose:\n{current_pose}")
           
           # Move 10cm up
           target_pose = current_pose.copy()
           target_pose[2, 3] += 0.1
           robot.move_to_pose(target_pose, speed_factor=0.1)
           
       finally:
           robot.stop_control()
           robot.disconnect()

Force Control Example
"""""""""""""""""""""

.. code-block:: python

   import libfrankapy as fp
   import numpy as np
   import time
   
   def force_control_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Start force control mode
           robot.start_force_control()
           
           # Apply downward force
           force_vector = np.array([0, 0, -5.0, 0, 0, 0])  # 5N downward
           
           for i in range(1000):  # 10 seconds at 100Hz
               robot.set_cartesian_force(force_vector)
               
               # Monitor contact forces
               state = robot.get_robot_state()
               contact_forces = state.cartesian_state.forces
               
               if np.linalg.norm(contact_forces[:3]) > 10.0:
                   print("Contact detected!")
                   break
               
               time.sleep(0.01)
           
           robot.stop_force_control()
           
       finally:
           robot.stop_control()
           robot.disconnect()

Error Handling Example
""""""""""""""""""""""

.. code-block:: python

   import libfrankapy as fp
   
   def error_handling_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Attempt potentially problematic operation
           unsafe_joints = [5.0, 0, 0, 0, 0, 0, 0]  # Beyond joint limits
           robot.move_to_joint(unsafe_joints)
           
       except fp.FrankaException as e:
           print(f"Robot error: {e}")
           
           # Check if robot is in error state
           if robot.is_in_error_state():
               print("Robot is in error state, attempting recovery...")
               
               # Get error details
               error = robot.get_last_error()
               print(f"Error details: {error}")
               
               # Attempt recovery
               robot.recover_from_errors()
               print("Recovery completed")
           
       finally:
           robot.stop_control()
           robot.disconnect()

See Also
^^^^^^^^

* :doc:`control` - Control interfaces and algorithms
* :doc:`state` - Robot state representations
* :doc:`exceptions` - Exception handling
* :doc:`../examples` - More comprehensive examples