##  @file
#   @brief Rough version of UR3 Robot on a linear rail defined by standard static DH parameters with 3D model
#   @author Adam Scicluna
#   @date August 23, 2025

import swift
import roboticstoolbox as rtb
import spatialmath.base as spb
from spatialmath import SE3
from ir_support.robots.DHRobot3D import DHRobot3D
import time
import os

# Useful variables
from math import pi

# -----------------------------------------------------------------------------------#
class LinearUR3(DHRobot3D):
    def __init__(self):
        """
        UR3 Robot on a Linear Rail.
        See the use of `UR3` and base class `DHRobot3D`

        """
        # DH links
        links = self._create_DH()

        # Names of the robot link files in the directory
        link3D_names = dict(link0 = 'base_rail', color0 = (0.2,0.2,0.2,1),      # color option only takes effect for stl file
                            link1 = 'slider_rail', color1 = (0.1,0.1,0.1,1),
                            link2 = 'shoulder_ur3',
                            link3 = 'upperarm_ur3',
                            link4 = 'forearm_ur3',
                            link5 = 'wrist1_ur3',
                            link6 = 'wrist2_ur3',
                            link7 = 'wrist3_ur3')

        # A joint config and the 3D object transforms to match that config
        qtest = [0,0,-pi/2,0,0,0,0]
        qtest_transforms = [spb.transl(0,0,0),
                            spb.trotx(-pi/2),
                            spb.transl(0,0.146,0) @ spb.rpy2tr(0,pi,pi, order='xyz'),
                            spb.transl(0,0.146,-0.13) @ spb.rpy2tr(0,0,-pi/2, order='xyz'),
                            spb.transl(0,0.39,-0.0378) @ spb.rpy2tr(0,0,-pi/2, order='xyz'),
                            spb.transl(0,0.603,-0.0378) @ spb.rpy2tr(0,pi/2,-pi/2, order='xyz'),
                            spb.transl(0,0.603,-0.1225) @ spb.rpy2tr(0,pi/2,-pi/2, order='xyz'),
                            spb.transl(0.08535,0.603,-0.1225) @ spb.rpy2tr(0,pi/2,-pi/2, order='xyz')]

        current_path = os.path.abspath(os.path.dirname(__file__))
        super().__init__(links, link3D_names, name = 'LinearUR3', link3d_dir = current_path, qtest = qtest, qtest_transforms = qtest_transforms)
        self.base = self.base * SE3.Rx(pi/2) * SE3.Ry(pi/2)
        self.q = qtest

    # -----------------------------------------------------------------------------------#
    def _create_DH(self):
        """
        Create robot's standard DH model
        """
        links = [rtb.PrismaticDH(theta= pi, a= 0, alpha= pi/2, qlim= [-0.8, 0])]    # Prismatic Link
        a = [0, -0.24365, -0.21325, 0, 0, 0]
        d = [0.146, 0, 0, 0.121, 0.083, 0.0819]     # Static UR3: [0.1519, 0, 0, 0.11235, 0.08535, 0.0819]
        alpha = [pi/2, 0, 0, pi/2, -pi/2, 0]
        offset = [0,0,0,0,0,0]
        qlim = [[-2*pi, 2*pi] for _ in range(6)]
        for i in range(6):
            link = rtb.RevoluteDH(d=d[i], a=a[i], alpha=alpha[i], offset=offset[i], qlim=qlim[i])
            links.append(link)
        return links

    # -----------------------------------------------------------------------------------#
    def test(self):
        """
        Test the class by adding 3d objects into a new Swift window and do a simple movement
        """
        env = swift.Swift()
        env.launch(realtime= True)
        self.q = self._qtest
        self.add_to_env(env)

        q_goal = [self.q[i]-pi/3 for i in range(self.n)]
        q_goal[0] = -0.8 # Move the rail link
        qtraj = rtb.jtraj(self.q, q_goal, 50).q
        # fig = self.plot(self.q, limits= [-1,1,-1,1,-1,1])
        # fig._add_teach_panel(self, self.q)
        for q in qtraj:
            self.q = q
            env.step(0.02)
            # fig.step(0.01)
        # fig.hold()
        env.hold()
        time.sleep(3)

# ---------------------------------------------------------------------------------------#
if __name__ == "__main__":
    r = LinearUR3()
    input("Press enter to test movement of LinearUR3")
    r.test()


