##  @file
#   @brief A cow herd simulation.
#   @author Ho Minh Quang Ngo
#   @date Feb 5, 2023

import numpy as np
import matplotlib.pyplot as plt
import spatialmath.base as spbase
from spatialmath import SE3
from typing import Optional, Union, List, Tuple
import ir_support.plyprocess as plyp
import os

# ---------------------------------------------------------------------------------------#
class RobotCow:
    '''
    A random herd of cows
    '''
    def __init__(self, num_cows:int = 2, # Default input cow number is 2
                 plot_type:Optional[str]= 'surface'):
        """
        Initialize the cow herd simulation

        Parameters:
        ____________
        `num_cows`: int, optional
            Number of cows. Default is 2
        `plot_type`: str, optional
            Plotting type for cow object, 'scatter' or 'surface'. Default is 'surface'
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self._plyfile = os.path.join(current_dir, "cow.ply")
        self._ranges = [-5, 5, -5, 5, 0, 10] # Visualizable range of the field
        self._mesh_simplify = 10 # Factor to simplify the mesh data
        self._cow_plotdata = {}
        self._traj_list = [] # List of trajectory for each cow
        self._num_traj_steps = 10 # Default number of step in a trajectory
        self._single_call = 0 # Number of times the 'plot_single_random_step' has been called, reset when finish current trajectory

        # plt.close('all')
        spbase.plotvol3(dim = self._ranges, equal= True, grid= True)

        self._plot_type = plot_type
        self.num_cows = num_cows
        self.cow_list = []

        self._get_ply_plot_data()
        self._generate_cow_list()
        self._plot_cow_list()
        self._generate_cows_trajectory()
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
        self._cow_plotdata['vertices'] = plyp.transform_vertices(vertices, spbase.transl(0,0,0.2) @ spbase.trotx(np.pi/2))
        self._cow_plotdata['color'] = vertices_color
        self._cow_plotdata['faces'] = faces
        self._cow_plotdata['faces_color'] = faces_color
        self._cow_plotdata['num'] = np.size(self._cow_plotdata['vertices'],0)

    def _generate_cow_list(self):
        for _ in range(self.num_cows):
            cow_base = self._generate_random_transform()
            cow_vertices = plyp.transform_vertices(self._cow_plotdata['vertices'], cow_base)
            cow = {'base': cow_base,
                   'vertices': cow_vertices,
                   'color':self._cow_plotdata['color']}
            self.cow_list.append(cow)

    def _plot_cow_list(self):
        if self._plot_type == 'scatter':
            for cow in self.cow_list:
                cow['plot_object'] = plyp.place_object(vertices= cow['vertices'], vertices_color= cow['color'], sizes = np.ones(self._cow_plotdata['num'])*0.2)
                # cow['plot_object'].set_edgecolors((0.23,0.23,0.21, 0.8))
        elif self._plot_type == 'surface':
            for cow in self.cow_list:
                cow['plot_object'] = plyp.place_object(vertices= cow['vertices'], faces= self._cow_plotdata['faces'],
                                                  faces_color= self._cow_plotdata['faces_color'], simplified= self._mesh_simplify, output= 'surface')
                cow['plot_object'].set_facecolors((0.5,0.1,0.1))

    def plot_single_random_step(self):
        """
        Plot a single random step for all cows
        """
        for i in range(self.num_cows):
            self.cow_list[i]['base'] = self._traj_list[i][self._single_call]
            self.animate(i)

        self._single_call += 1
        if self._single_call == self._num_traj_steps:
            self._generate_cows_trajectory()
            self._single_call = 0

    def animate(self, cow_index:int):
        """
        Animate the cow at index `cow_index`
        """
        self.cow_list[cow_index]['vertices'] = plyp.transform_vertices(self._cow_plotdata['vertices'], self.cow_list[cow_index]['base'])
        plyp.set_vertices(self.cow_list[cow_index]['plot_object'], self.cow_list[cow_index]['vertices'], self._cow_plotdata['faces'])

    def test_plot_many_step(self, num_steps:int, delay:float):
        """
        Test the plot of many steps for all cows

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

    def _generate_cows_trajectory(self):
        def traj_generator(T1, T2, num_steps):
            trajectory = []
            step = 1/num_steps
            for i in np.arange(0, 1 + step, step):
                trajectory.append(spbase.trinterp(T1, T2, i))
            return trajectory

        self._traj_list = [] # Reset the list of trajectories
        for cow in self.cow_list:
            delta = np.random.uniform(-np.pi/12, np.pi/12)
            goal_tr = cow['base'] @ spbase.trotz(delta) @ spbase.transl(1.5,0,0)
            only_rotate = False
            if not (self._ranges[0] <= goal_tr[0,3] <= self._ranges[1] and self._ranges[2] <= goal_tr[1,3] <= self._ranges[3]):
                goal_tr = cow['base'] @ spbase.transl(-0.2,0,0) @ spbase.trotz(np.pi)
                only_rotate = True

            if only_rotate:
                rot_traj = traj_generator(cow['base'], goal_tr, self._num_traj_steps)
                self._traj_list.append(rot_traj)
            else:
                rot_traj = traj_generator(cow['base'], cow['base'] @ spbase.trotz(delta), 3)
                trans_traj = traj_generator(rot_traj[-1], goal_tr, self._num_traj_steps - 3)
                self._traj_list.append(rot_traj + trans_traj)

    # ---------------------------------------------------------------------------------------#
    def _generate_random_transform(self):
        '''
        Generate a random transform from given range in xy plane
        :return: SE3 transformation matrix
        :rtype: SE3 object NDArray object
        '''
        # Generate random point coordinates
        x = np.random.uniform(self._ranges[0], self._ranges[1])
        y = np.random.uniform(self._ranges[2], self._ranges[3])
        yaw = np.random.uniform(-np.pi, np.pi)
        transform = SE3(x,y,0) * SE3.Rz(yaw)
        return transform.A

# ---------------------------------------------------------------------------------------#
def place_fence(position: Union[List[float], Tuple[float, float, float]] = [0, 0, 0],
                orientation: Optional[float] = 0,
                plot_type: Optional[str] = 'surface',
                scale: Union[List[float], Tuple[float, float, float]] = [1, 1, 1]):
    '''
    Place a fence read from 'fenceFinal.ply' into current environment

    :param position: position of the fence. Default is [0,0,0]
    :type position: list or tuple of 3
    :param orientation: yaw angle in degree. Default is 0
    :type orientation: float
    :param plot_type: 'scatter' or 'surface'. Default is 'surface'
    :type plot_type: str
    :param scale: scale of the fence in x, y, z direction. Default is [1,1,1]
    :type scale: list or tuple of 3    
    :return: an object into current drawing environment
    :rtype: 3Dplot object
    '''
    if not hasattr(place_fence,'vertices') and not hasattr(place_fence, 'vertices_color'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plyfile = os.path.join(current_dir, "fenceFinal.ply")
        fence_data = plyp.get_ply_data(plyfile)
        place_fence.vertices = fence_data['vertices']
        place_fence.vertices_color = fence_data['vertices_color']
        place_fence.faces = fence_data['faces']
        place_fence.faces_color = fence_data['faces_color']
        place_fence.sizes = np.ones(np.size(place_fence.vertices,0))*1
        place_fence.linewidths = np.ones(np.size(place_fence.vertices,0))*2.5
        place_fence.linestyles = ['--','--',':']

    vertices = place_fence.vertices.copy()
    # vertices = plyp.transform_vertices(vertices, spbase.transl(position) @ spbase.trotz(orientation * np.pi/180))
    scale_matrix = np.diag([*scale, 1])
    transform = spbase.transl(position) @ spbase.trotz(orientation * np.pi/180)    
    vertices[:, :3] = vertices[:, :3] @ scale_matrix[:3, :3].T
    vertices = plyp.transform_vertices(vertices, transform)

    if plot_type == 'scatter':
        fence = plyp.place_object(vertices= vertices, vertices_color = place_fence.vertices_color,
                            sizes = place_fence.sizes, linestyles = place_fence.linestyles, linewidths = place_fence.linewidths)
    elif plot_type == 'surface':
        fence = plyp.place_object(vertices= vertices, faces= place_fence.faces, faces_color= place_fence.faces_color, output = 'surface')
    else:
        raise ValueError('Invalid plot type!')
    return fence

# ---------------------------------------------------------------------------------------#
if __name__ == '__main__':
    cow_herd = RobotCow(5)
    place_fence([0,5,0],90)
    input("Press any key to continue\n")
    cow_herd.test_plot_many_step(1000, 0.01)
    print(cow_herd.cow_list[0]['base'])
    plt.show()

