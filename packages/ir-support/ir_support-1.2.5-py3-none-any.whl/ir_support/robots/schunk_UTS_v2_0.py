from spatialmath import SE3
from roboticstoolbox import DHLink, DHRobot
# Useful variables
from math import pi, radians

def schunk_UTS_v2_0()->DHRobot:
    l1 = DHLink(d=-0.38, a=0, alpha=-pi/2, offset=0, qlim=[radians(-117), radians(117)])
    l2 = DHLink(d=0, a=0.385, alpha=pi, offset=pi/2, qlim=[radians(-115), radians(115)])
    l3 = DHLink(d=0, a=0, alpha=pi/2, offset=-pi/2, qlim=[radians(-110), radians(110)])
    l4 = DHLink(d=-0.445, a=0, alpha=pi/2, offset=0, qlim=[radians(-200), radians(200)])
    l5 = DHLink(d=0, a=0, alpha=-pi/2, offset=0, qlim=[radians(-107), radians(107)])
    l6 = DHLink(d=-0.2106, a=0, alpha=pi, offset=0, qlim=[radians(-200), radians(200)])
    blaster_robot = DHRobot([l1,l2,l3,l4,l5,l6])
    blaster_robot.base = SE3.Rz(-pi/2) * SE3.Rx(pi)
    return blaster_robot
