##  @file
#   @brief A UFO Fleet simulation.
#   @author Ho Minh Quang Ngo
#   @date Jul 4, 2023

import numpy as np
import matplotlib.pyplot as plt
import spatialmath.base as spbase
from typing import Optional, Union, List, Tuple
from spatialmath import SE3
from ir_support.functions import line_plane_intersection
import ir_support.plyprocess as plyp
import os

# ---------------------------------------------------------------------------------------#
class UFOFLeet:
    '''
    A random fleet of ufos
    '''
    def __init__(self, num_ufos:int = 2,
                 plot_type:Optional[str] = 'scatter'): # Default input ufo number is 2, scatter plot type
        """
        Initialize the UFO fleet simulation

        Parameters:
        ____________
        `num_ufos`: int, optional
            Number of UFOs. Default is 2
        `plot_type`: str, optional
            Plotting type for UFO object, 'scatter' or 'surface'. Default is 'scatter'
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self._plyfile = os.path.join(current_dir, "Haneubu+uf.ply")
        self._ranges = [-5, 5, -5, 5, 0, 10] # Visualizable range of the field
        self._mesh_simplify = 5 # Factor to simplify the mesh data
        self._ufo_plotdata = {}
        self._traj_list = [] # List of trajectory for each ufo
        self._num_traj_steps = 5 # Default number of step in a trajectory
        self._single_call = 0 # Number of times the 'plot_single_random_step' has been called, reset when finish current trajectory

        self._max_health = 20 # Max health points
        self._ship_radius = 0.8 # Radius of the UFO
        # plt.close('all')
        spbase.plotvol3(dim = self._ranges, equal= True, grid= True)

        self.num_ufos = num_ufos
        self._plot_type = plot_type
        self.ufo_list = []

        self._get_ply_plot_data()
        self._generate_ufo_list()
        self._plot_ufo_list()
        self._generate_ufos_trajectory()
        plt.pause(0.01)

    def _get_ply_plot_data(self):
        if self._plot_type == 'surface':
            plydata = plyp.get_ply_data(self._plyfile, self._mesh_simplify)
        else:
            plydata = plyp.get_ply_data(self._plyfile)
        vertices = plydata['vertices']
        vertices_color = plydata['vertices_color']
        faces = plydata['faces']
        faces_color = plydata['faces_color']
        self._ufo_plotdata['vertices'] = plyp.transform_vertices(vertices, spbase.transl(0,0,0.2))
        self._ufo_plotdata['color'] = vertices_color
        self._ufo_plotdata['faces'] = faces
        self._ufo_plotdata['faces_color'] = faces_color
        self._ufo_plotdata['num'] = np.size(self._ufo_plotdata['vertices'],0)

    def _generate_ufo_list(self):
        for _ in range(self.num_ufos):
            ufo_base = self._generate_random_transform()
            ufo_vertices = plyp.transform_vertices(self._ufo_plotdata['vertices'], ufo_base)
            ufo = {'base': ufo_base,
                   'vertices': ufo_vertices,
                   'color':self._ufo_plotdata['color'],
                   'health': self._max_health}
            self.ufo_list.append(ufo)

    def _plot_ufo_list(self):
        if self._plot_type == 'scatter':
            for ufo in self.ufo_list:
                ufo['plot_object'] = plyp.place_object(vertices= ufo['vertices'], vertices_color= ufo['color'],
                                                sizes = np.ones(self._ufo_plotdata['num'])*5, linewidths = 1)
                ufo['plot_object'].set_edgecolors((0.23,0.23,0.21, 0.8))
        elif self._plot_type == 'surface':
            for ufo in self.ufo_list:
                ufo['plot_object'] = plyp.place_object(vertices= ufo['vertices'], faces= self._ufo_plotdata['faces'],
                                                  faces_color= self._ufo_plotdata['faces_color'], output= 'surface', linewidth = 0.05)

    def plot_single_random_step(self):
        """
        Plot a single random step for all UFOs
        """
        for i in range(self.num_ufos):
            # If either 0 or -1 health left then don't plot a move
            if self.ufo_list[i]['health'] < 1:
                continue
            self.ufo_list[i]['base'] = self._traj_list[i][self._single_call]
            self.animate(i)

        self._single_call += 1
        if self._single_call == self._num_traj_steps:
            self._generate_ufos_trajectory()
            self._single_call = 0

    def animate(self, ufo_index:int):
        """
        Animate the UFO movement at index `ufo_index`
        """
        self.ufo_list[ufo_index]['vertices'] = plyp.transform_vertices(self._ufo_plotdata['vertices'], self.ufo_list[ufo_index]['base'])
        plyp.set_vertices(self.ufo_list[ufo_index]['plot_object'], self.ufo_list[ufo_index]['vertices'], self._ufo_plotdata['faces'])

    def test_plot_many_step(self, num_steps:int, delay:float):
        """
        Test the plot of many steps for all UFOs

        Parameters:
        ____________
        `num_steps`: int
            Number of steps to plot
        `delay`: float
            Delay between each step
        """
        for _ in range(num_steps):
            self.plot_single_random_step()
            plt.pause(delay)

    def _remove_dead(self):
        for ufo in self.ufo_list:
            if ufo['health'] == 0:
                # Make big and red (explode)
                plyp.scale_object(ufo['plot_object'], 2) # now only work with 'scatter' object
                ufo['plot_object'].set_facecolors((0.4,0.1,0.1,0.8))
                plt.draw()
                plt.pause(0.1)

                # Then make UFO invisible
                ufo['plot_object'].set_visible(False)

                # Don't try and remove again
                ufo['health'] = -1

    def set_hit(self, ufo_hit_index:int):
        """
        Set the UFOs at index `ufo_hit_index` as getting hit

        """
        if ufo_hit_index is []:
            return None
        for index in ufo_hit_index:
            if self.ufo_list[index]['health'] < 1:
                continue
            self.ufo_list[index]['health'] -= 1

            # Shift to red
            self.ufo_list[index]['plot_object'].set_facecolors((0.4,0.1,0.1,0.5))
            if self._plot_type == 'scatter':
                self.ufo_list[index]['plot_object'].set_edgecolors((0.5,0.1,0.1, 0.8))
            plt.pause(0.1)

            # Then get back to default color
            if self._plot_type == 'scatter':
                self.ufo_list[index]['plot_object'].set_facecolors(self._ufo_plotdata['color'])
                self.ufo_list[index]['plot_object'].set_edgecolors((0.23,0.23,0.21, 0.8))
            else:
                self.ufo_list[index]['plot_object'].set_facecolors(self._ufo_plotdata['faces_color'])

        self._remove_dead()

    def is_destroy_all(self):
        """
        Check if all UFOs are destroyed
        """
        is_destroy_all = True
        for ufo in self.ufo_list:
            if ufo['health'] >= 1:
                return False
        return is_destroy_all

    def _generate_ufos_trajectory(self):
        def traj_generator(T1, T2, num_steps):
            trajectory = []
            step = 1/num_steps
            for i in np.arange(0, 1 + step, step):
                trajectory.append(spbase.trinterp(T1, T2, i))
            return trajectory

        self._traj_list = [] # Reset the list of trajectories

        for i in range(self.num_ufos):
            z = np.random.uniform(-1, 1)
            if self.ufo_list[i]['base'][2,3] >= self._ranges[5]:
                z = -1
            elif  self.ufo_list[i]['base'][2,3] <= 2:
                z = 1
            goal_tr = self.ufo_list[i]['base'] @ spbase.trotz(np.random.uniform(-np.pi, np.pi)) @ spbase.transl(2,2,z)
            while not (self._ranges[0] <= goal_tr[0,3] <= self._ranges[1] and self._ranges[2] <= goal_tr[1,3] <= self._ranges[3]):
                goal_tr = self.ufo_list[i]['base'] @ spbase.trotz(np.random.uniform(-np.pi, np.pi)) @ spbase.transl(2,2,z)

            self._traj_list.append(traj_generator(self.ufo_list[i]['base'], goal_tr, self._num_traj_steps))

    def _generate_random_transform(self):
        '''
        Generate a random transform from given range in xy plane

        :return: SE3 transformation matrix
        :rtype: SE3 object NDArray object
        '''
        # Generate random point coordinates
        x = np.random.uniform(self._ranges[0], self._ranges[1])
        y = np.random.uniform(self._ranges[2], self._ranges[3])
        z = np.random.uniform(2, self._ranges[5])
        yaw = np.random.uniform(-np.pi, np.pi)
        transform = SE3(x,y,z) * SE3.Rz(yaw)
        return transform.A

# ---------------------------------------------------------------------------------------#
def check_intersections(ee_tr:np.ndarray,
                        cone_ends:List[np.ndarray],
                        ufo_fleet:UFOFLeet) -> List[int]:
    """
    Check for UFOs hit by the ray

    Parameters:
    ____________
    `ee_tr`: ndarray
        End-effector transformation matrix
    `cone_ends`: list
        List of end points of the cone
    `ufo_fleet`: UFOFleet
        UFO fleet object
    """

    ufo_hit_index = []

    # Ray from the cone
    ray_start = spbase.transl(ee_tr)

    for ray_end in cone_ends:
        for ufo_index, ufo in enumerate(ufo_fleet.ufo_list):
            # Disk representing the UFO
            ufo_point = spbase.transl(ufo['base'])
            ufo_normal =  [0,0,1]

            # Check intersection of the line with the plane.
            intersection_point, check = line_plane_intersection(ufo_normal, ufo_point, ray_start, ray_end)

            # Check for an intersection which is also close to the ufo center
            if check != 1 or ufo_fleet._ship_radius < distance_between_points(intersection_point, ufo_point) or ufo['health'] < 1:
                continue

            ufo_hit_index.append(ufo_index)

    return ufo_hit_index


def distance_between_points(point1:Union[np.ndarray, List[float]],
                            point2:Union[np.ndarray, List[float]]) -> float:
    # Convert the points to NumPy arrays
    point1 = np.array(point1)
    point2 = np.array(point2)

    distance = np.linalg.norm(point1 - point2)

    return distance

# ---------------------------------------------------------------------------------------#
if __name__ == '__main__':
    ufo_fleet = UFOFLeet(10,'surface')
    input("Press Enter to continue\n")
    ufo_fleet.test_plot_many_step(100, 0.01)
    print("Pose of the first UFO:\n",SE3(ufo_fleet.ufo_list[0]['base']))
    plt.show()
