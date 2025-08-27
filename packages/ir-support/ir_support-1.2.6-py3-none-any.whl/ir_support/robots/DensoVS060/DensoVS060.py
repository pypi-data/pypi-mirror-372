from roboticstoolbox import Robot
from spatialmath import SE3
from pathlib import Path

"""
To see a live Swift demo with interactive joint controls and end-effector frame plotting,
run `DensoVS060_demo.py` from this folder.
"""

def DensoVS060(base_offset=0.2):
    tld = Path(__file__).parent
    urdf_file = "DensoVS060.urdf"
    links, name, urdf_string, resolved_path = Robot.URDF_read(urdf_file, tld=str(tld))
    robot = Robot(links, name=name)
    robot.q = [0.0] * robot.n
    robot.base = robot.base @ SE3(0, 0, base_offset)
    return robot
