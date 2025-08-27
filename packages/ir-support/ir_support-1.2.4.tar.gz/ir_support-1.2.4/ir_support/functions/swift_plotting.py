import numpy as np
from spatialmath import SE3
from spatialgeometry import Cylinder
from roboticstoolbox import Robot
import time
import keyboard

def add_frame_cylinders(env, length=0.1, radius=0.005):
    """
    Adds coordinate frame cylinders to the Swift environment.
    
    Parameters:
    - env: The Swift environment to which the cylinders will be added.
    - length: Length of the cylinders representing the axes.
    - radius: Radius of the cylinders.
    
    Returns:
    - List of Cylinder objects representing the axes.
    """
    if length <= 0 or radius <= 0:
        raise ValueError("Length and radius must be positive values.")
    if not isinstance(env, object):
        raise TypeError("The provided environment is not a valid Swift environment.")
    if not hasattr(env, 'add'):
        raise TypeError("The provided environment does not have an 'add' method.")
    
    cylinders = create_frame_cylinders(length, radius)
    for c in cylinders:
        env.add(c)
    return cylinders

def create_frame_cylinders(length=0.1, radius=0.005):
    """Creates coordinate frame cylinders representing the X, Y, and Z axes.
    Parameters:
    - length: Length of the cylinders.
    - radius: Radius of the cylinders.
    Returns:
    - List of Cylinder objects representing the axes.
    """
    if length <= 0 or radius <= 0:
        raise ValueError("Length and radius must be positive values.")
    
    x_axis = Cylinder(length=length, radius=radius, color=[1, 0, 0])  # red
    y_axis = Cylinder(length=length, radius=radius, color=[0, 1, 0])  # green
    z_axis = Cylinder(length=length, radius=radius, color=[0, 0, 1])  # blue
    return [x_axis, y_axis, z_axis]

def update_frame_cylinders(cylinders, T, length=0.1):
    """Updates the position and orientation of the coordinate frame cylinders.
    Parameters:
    - cylinders: List of Cylinder objects representing the axes.
    - T: The transformation matrix representing the new position and orientation.
    - length: Length of the cylinders.
    """
    if len(cylinders) != 3:
        raise ValueError("Expected 3 cylinders for X, Y, and Z axes.")
    # Update the transformation for each cylinder
    cylinders[0].T = T * SE3.Ry(np.pi/2) * SE3.Tz(length/2)  # X-axis
    cylinders[1].T = T * SE3.Rx(-np.pi/2) * SE3.Tz(length/2)   # Y-axis
    cylinders[2].T = T * SE3.Tz(length/2)                     # Z-axis


def keyboard_joint_control_loop(robot, env, update_fn=None, step=0.05):
    """
    Control robot joints using arrow keys.
    Calls `update_fn(q, T)` whenever robot.q changes.

    Controls:
        ← → : select joint
        ↑ ↓ : increment/decrement joint
        space: reset joints to zero
        q : quit loop
    """
    joint_index = 0
    robot.q = robot.q if robot.q is not None else [0.0] * robot.n

    print("\nControls:")
    print("  → and ← to change joint")
    print("  ↑ and ↓ to move joint")
    print("  space to reset all joints to zero\n")
    print("  q to quit\n")

    print_updated_joint_state = False

    while True:
        if keyboard.is_pressed("right"):
            joint_index = (joint_index + 1) % robot.n
            print(f"Selected joint: {joint_index}")
            time.sleep(0.2)

        elif keyboard.is_pressed("left"):
            joint_index = (joint_index - 1) % robot.n
            print(f"Selected joint: {joint_index}")
            time.sleep(0.2)

        elif keyboard.is_pressed("up"):
            robot.q[joint_index] += step
            print_updated_joint_state = True

        elif keyboard.is_pressed("down"):
            robot.q[joint_index] -= step
            print_updated_joint_state = True

        elif keyboard.is_pressed("space"):
            robot.q = [0.0] * robot.n
            print("Resetting all joints to zero.")
            print_updated_joint_state = True

        elif keyboard.is_pressed("q"):
            print("Exiting.")
            break

        T = robot.fkine(robot.q)
        if update_fn:
            update_fn(robot.q, T)

        if print_updated_joint_state:
            print_updated_joint_state = False
            print("Updated joint state:", "  ".join([f"q[{i}]={robot.q[i]:.3f}" for i in range(robot.n)]))

        env.step(0.02)
