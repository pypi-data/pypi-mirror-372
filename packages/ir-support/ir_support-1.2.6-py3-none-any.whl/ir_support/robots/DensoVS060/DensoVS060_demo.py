# Denso VS060 Robot Demo
# This script demonstrates the Denso VS060 robot using the Swift simulator.
# It creates a robot instance, launches the Swift environment, and adds the robot to the environment.
# It also sets up a coordinate frame at the end-effector and allows for keyboard control of
# the robot's joints with real-time updates to the end-effector's coordinate frame.
from ir_support.robots import DensoVS060
from ir_support.functions import create_frame_cylinders, update_frame_cylinders, add_frame_cylinders, keyboard_joint_control_loop
import swift
import numpy as np

robot = DensoVS060()
env = swift.Swift()
env.launch(realtime=True)
env.add(robot)

ee_coordinate_frame_cylinders = add_frame_cylinders(env, length=0.1, radius=0.005)
update_frame_cylinders(ee_coordinate_frame_cylinders, robot.fkine(robot.q))

def update_visuals(q, T):
    update_frame_cylinders(ee_coordinate_frame_cylinders, T)

keyboard_joint_control_loop(robot, env, update_visuals, step=0.05)
