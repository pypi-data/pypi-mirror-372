Control API
===========

The control module provides various control interfaces and algorithms for robot motion control.

.. currentmodule:: libfrankapy.control

Control Classes
---------------

JointController
^^^^^^^^^^^^^^^

.. autoclass:: JointController
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`JointController` provides joint-space control functionality.

.. code-block:: python

   from libfrankapy.control import JointController
   
   controller = JointController(robot)
   controller.move_to_position(target_joints, speed_factor=0.1)

CartesianController
^^^^^^^^^^^^^^^^^^^

.. autoclass:: CartesianController
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`CartesianController` provides Cartesian-space control functionality.

.. code-block:: python

   from libfrankapy.control import CartesianController
   
   controller = CartesianController(robot)
   controller.move_to_pose(target_pose, speed_factor=0.1)

ForceController
^^^^^^^^^^^^^^^

.. autoclass:: ForceController
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`ForceController` provides force/torque control functionality.

.. code-block:: python

   from libfrankapy.control import ForceController
   
   controller = ForceController(robot)
   controller.apply_force(force_vector)

TrajectoryController
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: TrajectoryController
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`TrajectoryController` provides trajectory execution functionality.

.. code-block:: python

   from libfrankapy.control import TrajectoryController
   
   controller = TrajectoryController(robot)
   controller.execute_trajectory(waypoints, duration)

Control Algorithms
------------------

Motion Generators
^^^^^^^^^^^^^^^^^

.. autoclass:: MotionGenerator
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: JointMotionGenerator
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CartesianMotionGenerator
   :members:
   :undoc-members:
   :show-inheritance:

Trajectory Planning
^^^^^^^^^^^^^^^^^^^

.. autoclass:: TrajectoryPlanner
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: JointTrajectoryPlanner
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CartesianTrajectoryPlanner
   :members:
   :undoc-members:
   :show-inheritance:

Impedance Control
^^^^^^^^^^^^^^^^^

.. autoclass:: ImpedanceController
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`ImpedanceController` provides compliant motion control.

.. code-block:: python

   from libfrankapy.control import ImpedanceController
   
   # Configure impedance parameters
   stiffness = [3000, 3000, 3000, 300, 300, 300]  # N/m and Nm/rad
   damping = [89, 89, 89, 17, 17, 17]  # Ns/m and Nms/rad
   
   controller = ImpedanceController(robot)
   controller.set_impedance(stiffness, damping)
   controller.start_impedance_control()

Configuration Classes
---------------------

JointControlConfig
^^^^^^^^^^^^^^^^^^

.. autoclass:: JointControlConfig
   :members:
   :undoc-members:
   :show-inheritance:

Configuration for joint-space control parameters.

.. code-block:: python

   from libfrankapy.control import JointControlConfig
   
   config = JointControlConfig(
       max_velocity=[2.0, 2.0, 2.0, 2.0, 2.5, 2.5, 2.5],
       max_acceleration=[15.0, 7.5, 10.0, 12.5, 15.0, 20.0, 20.0],
       position_tolerance=0.01
   )

CartesianControlConfig
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: CartesianControlConfig
   :members:
   :undoc-members:
   :show-inheritance:

Configuration for Cartesian-space control parameters.

.. code-block:: python

   from libfrankapy.control import CartesianControlConfig
   
   config = CartesianControlConfig(
       max_translation_velocity=0.2,
       max_rotation_velocity=0.5,
       position_tolerance=0.001
   )

ForceControlConfig
^^^^^^^^^^^^^^^^^^

.. autoclass:: ForceControlConfig
   :members:
   :undoc-members:
   :show-inheritance:

Configuration for force control parameters.

.. code-block:: python

   from libfrankapy.control import ForceControlConfig
   
   config = ForceControlConfig(
       max_force=[20.0, 20.0, 20.0],
       max_torque=[10.0, 10.0, 10.0],
       force_filter_cutoff=10.0
   )

Utility Functions
-----------------

Trajectory Generation
^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: generate_joint_trajectory
.. autofunction:: generate_cartesian_trajectory
.. autofunction:: interpolate_trajectory

Motion Planning
^^^^^^^^^^^^^^^

.. autofunction:: plan_joint_motion
.. autofunction:: plan_cartesian_motion
.. autofunction:: check_trajectory_feasibility

Kinematics
^^^^^^^^^^

.. autofunction:: forward_kinematics
.. autofunction:: inverse_kinematics
.. autofunction:: compute_jacobian
.. autofunction:: compute_mass_matrix

Examples
--------

Joint Space Control
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   from libfrankapy.control import JointController, JointControlConfig
   
   def joint_control_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           # Configure joint control
           config = JointControlConfig(
               max_velocity=[1.5, 1.5, 1.5, 1.5, 2.0, 2.0, 2.0],
               position_tolerance=0.005
           )
           
           controller = JointController(robot)
           controller.set_config(config)
           
           # Define waypoints
           waypoints = [
               [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.5, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.0, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785]
           ]
           
           # Execute motion
           for waypoint in waypoints:
               controller.move_to_position(waypoint, speed_factor=0.2)
               
       finally:
           robot.stop_control()
           robot.disconnect()

Cartesian Space Control
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   from libfrankapy.control import CartesianController
   import numpy as np
   
   def cartesian_control_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           controller = CartesianController(robot)
           
           # Get current pose
           current_pose = robot.get_cartesian_state().pose
           
           # Create circular trajectory
           radius = 0.05  # 5cm radius
           num_points = 20
           
           for i in range(num_points):
               angle = 2 * np.pi * i / num_points
               
               target_pose = current_pose.copy()
               target_pose[0, 3] += radius * np.cos(angle)
               target_pose[1, 3] += radius * np.sin(angle)
               
               controller.move_to_pose(target_pose, speed_factor=0.1)
               
       finally:
           robot.stop_control()
           robot.disconnect()

Force Control
^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   from libfrankapy.control import ForceController
   import numpy as np
   import time
   
   def force_control_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           controller = ForceController(robot)
           controller.start_force_control()
           
           # Apply controlled contact force
           target_force = np.array([0, 0, -5.0, 0, 0, 0])  # 5N downward
           
           for i in range(500):  # 5 seconds at 100Hz
               # Get current forces
               current_forces = robot.get_force_state().forces
               
               # Simple force control
               force_error = target_force - current_forces
               control_force = 0.1 * force_error  # Proportional control
               
               controller.apply_force(control_force)
               time.sleep(0.01)
           
           controller.stop_force_control()
           
       finally:
           robot.stop_control()
           robot.disconnect()

Trajectory Execution
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import libfrankapy as fp
   from libfrankapy.control import TrajectoryController, generate_joint_trajectory
   
   def trajectory_execution_example():
       robot = fp.FrankaRobot("192.168.1.100")
       
       try:
           robot.connect()
           robot.start_control()
           
           controller = TrajectoryController(robot)
           
           # Define waypoints
           waypoints = [
               [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.5, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.5, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.0, -0.285, 0.0, -2.356, 0.0, 1.571, 0.785],
               [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
           ]
           
           # Generate smooth trajectory
           trajectory = generate_joint_trajectory(
               waypoints=waypoints,
               duration=10.0,
               max_velocity=[2.0, 2.0, 2.0, 2.0, 2.5, 2.5, 2.5]
           )
           
           # Execute trajectory
           controller.execute_trajectory(trajectory)
           
       finally:
           robot.stop_control()
           robot.disconnect()

See Also
--------

* :doc:`robot` - Main robot interface
* :doc:`state` - Robot state information
* :doc:`../examples` - More control examples
* :doc:`../configuration` - Control configuration options