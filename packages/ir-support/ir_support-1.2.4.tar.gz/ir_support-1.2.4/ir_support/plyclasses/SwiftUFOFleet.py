##  @file
#   @brief A UFO Fleet simulation for Swift simulator. Modified from the original UFOFleet class for Matplotlib by Ho Minh Quang Ngo. 
#   Tested on Ubuntu + Chrome.
#   @author Adam Scicluna
#   @date Jul 1, 2025

import numpy as np
import spatialmath.base as spbase
from typing import Optional, Union, List, Tuple
from spatialmath import SE3
from ir_support.functions import line_plane_intersection
import os
import swift
import spatialgeometry as sg
import trimesh

# ---------------------------------------------------------------------------------------#
class SwiftUFOFleet:
    '''
    A random fleet of UFOs for Swift simulator
    '''
    def __init__(self, swift_env, num_ufos: int = 2):
        """
        Initialise the UFO fleet simulation for Swift

        Parameters:
        ____________
        `swift_env`: Swift environment object
            The Swift simulator environment
        `num_ufos`: int, optional
            Number of UFOs. Default is 2
        """
        self.swift = swift_env
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self._dae = os.path.join(current_dir, "ufo.dae")
        self._hit_dae = os.path.join(current_dir, "hit_ufo.dae")
        
        # Simulation parameters
        self._ranges = [-5, 5, -5, 5, 0, 10]  # Visualisable range
        self._max_health = 20
        self._ship_radius = 0.8
        self._num_traj_steps = 5
        self._single_call = 0
        
        # UFO fleet data
        self.num_ufos = num_ufos
        self.ufo_list = []
        self._traj_list = []
        
        # Initialise the fleet
        self._generate_ufo_list()
        self._add_ufos_to_swift()
        self._generate_ufos_trajectory()


    def _generate_ufo_list(self):
        """
        Generate UFO data structures with paired normal/red UFOs
        Each 'UFO' in the fleet will have a 'duplicated' UFO but
        coloured red, to indicate when the UFO is being hit. This
        is because Swift handles moving objects much better than
        recolouring or deleting objects on the fly.

        E.g. SwiftUFOFleet(10) creates 10 UFO's and 10 'duplicates',
        so 20 Swift objects in total.
        """
        for i in range(self.num_ufos):
            ufo_base = self._generate_random_transform()
            
            # Create paired UFOs - one normal, one red
            ufo = {
                'id': i,
                'base': ufo_base,
                'health': self._max_health,
                'normal_ufo': None,    # Normal colored UFO
                'red_ufo': None,       # Red colored UFO  
                'is_hit': False,       # Track hit state
                'visible': True
            }
            self.ufo_list.append(ufo)


    def _add_ufos_to_swift(self):
        """
        Add paired UFO meshes to Swift environment
        """
        for ufo in self.ufo_list:
            try:
                # Create normal UFO at visible position
                normal_ufo = self._create_single_ufo(ufo['base'], normal_color=True)
                ufo['normal_ufo'] = normal_ufo
                
                # Create red UFO at hidden position (Z = -100)
                hidden_pose = ufo['base'].copy()
                hidden_pose[2, 3] = -100  # Hide it way below
                red_ufo = self._create_single_ufo(hidden_pose, normal_color=False)
                ufo['red_ufo'] = red_ufo
                
            except Exception as e:
                print(f"Error creating UFO pair {ufo['id']}: {e}")
        
    
    def _create_single_ufo(self, pose: np.ndarray, normal_color: bool = True):
        """Create a single UFO using DAE files"""
        try:
            # Choose the appropriate DAE file
            dae_file = self._dae if normal_color else self._hit_dae
            
            # Create mesh object from DAE file
            mesh_obj = sg.Mesh(
                filename=dae_file,
                pose=SE3(pose)
            )
            self.swift.add(mesh_obj)
            return mesh_obj
            
        except Exception as e:
            print(f"Error loading DAE file: {e}")
            raise


    def step(self):
        """
        Execute one simulation step - equivalent to plot_single_random_step in original
        """
        for i in range(self.num_ufos):
            # Skip if UFO is destroyed
            if self.ufo_list[i]['health'] < 1:
                continue
                
            # Update UFO position
            try:
                self.ufo_list[i]['base'] = self._traj_list[i][self._single_call]
                self._update_ufo_pose(i)
            except Exception as e:
                print(f'STEP - Error updating UFO {i} pose: {e}')
            
        self._single_call += 1
        if self._single_call >= self._num_traj_steps:
            try:
                self._generate_ufos_trajectory()
                self._single_call = 0
            except Exception as e:
                print(f'STEP - Error generating trajectories: {e}')

        # Let Swift update the visualisation (only once per step)
        try:
            self.swift.step()
        except Exception as e:
            print(f'STEP - Error in swift.step(): {e}')
            raise  # Re-raise to see full traceback


    def _update_ufo_pose(self, ufo_index: int):
        """Update UFO pose in Swift environment - only move the visible one"""
        ufo = self.ufo_list[ufo_index]
        if not ufo['visible'] or ufo['health'] < 1:
            return
            
        visible_pos = ufo['base']
        hidden_pos = visible_pos.copy()
        hidden_pos[2, 3] = -100
        
        # Update both UFOs, but only the "active" one will be visible
        if ufo['is_hit']:
            # Red UFO should be visible
            self._update_single_ufo_pose(ufo['red_ufo'], visible_pos)
            self._update_single_ufo_pose(ufo['normal_ufo'], hidden_pos)
        else:
            # Normal UFO should be visible
            self._update_single_ufo_pose(ufo['normal_ufo'], visible_pos)
            self._update_single_ufo_pose(ufo['red_ufo'], hidden_pos)


    def run_simulation(self, num_steps: int = 100, real_time: bool = True):
        """
        Run the simulation for a specified number of steps
        
        Parameters:
        ____________
        `num_steps`: int
            Number of simulation steps
        `real_time`: bool
            Whether to run in real-time or as fast as possible

        Can be removed, as it only moves around the UFOs, which isn't
        needed for the Lab Exercises.
        """
        if real_time:
            # Use Swift's built-in real-time execution
            for _ in range(num_steps):
                self.step()
                # Swift handles timing automatically in real-time mode
        else:
            # Run as fast as possible
            for _ in range(num_steps):
                self.step()

    
    def set_hit(self, ufo_hit_index: List[int]):
        """Set UFOs as getting hit using position swapping"""
        # First, handle UFOs that are no longer being hit
        for i, ufo in enumerate(self.ufo_list):
            if ufo['health'] < 1 or not ufo['visible']:
                continue
                
            # If UFO was hit but is no longer being hit, swap back to normal
            if ufo['is_hit'] and i not in ufo_hit_index:
                self._swap_ufo_visibility(i, show_red=False)
                ufo['is_hit'] = False
        
        # Then handle newly hit UFOs
        for index in ufo_hit_index:
            if index >= len(self.ufo_list) or self.ufo_list[index]['health'] < 1:
                continue

            # Reduce health
            self.ufo_list[index]['health'] -= 1
            
            # If not already showing red, swap to red UFO
            if not self.ufo_list[index]['is_hit']:
                self._swap_ufo_visibility(index, show_red=True)
                self.ufo_list[index]['is_hit'] = True

        self._remove_dead()


    def _swap_ufo_visibility(self, ufo_index: int, show_red: bool):
        """
        Swap UFO visibility by moving normal/red versions
        This is done by 'hiding' one version of the UFO at an extreme location,
        and swapping poses based on if the UFO is currently hit.
        """
        ufo = self.ufo_list[ufo_index]
        visible_pos = ufo['base']
        hidden_pos = visible_pos.copy()
        hidden_pos[2, 3] = -100  # Hidden position
        
        if show_red:
            # Move red UFO to visible position, normal UFO to hidden position
            self._update_single_ufo_pose(ufo['red_ufo'], visible_pos)
            self._update_single_ufo_pose(ufo['normal_ufo'], hidden_pos)
        else:
            # Move normal UFO to visible position, red UFO to hidden position  
            self._update_single_ufo_pose(ufo['normal_ufo'], visible_pos)
            self._update_single_ufo_pose(ufo['red_ufo'], hidden_pos)


    def _update_single_ufo_pose(self, ufo_obj, pose):
        """Update pose for a single UFO mesh object"""
        ufo_obj.T = pose


    def _remove_dead(self):
        """
        Remove destroyed UFOs from simulation
        Due to how Swift currently handles removal of objects in the update step,
        we actually just move the UFO to Z = -100 to 'hide' it. Once consistent
        updates are complete, they can be removed manually. In tests, having
        100 objects did not cause any significant slowing of the simulator.
        """
        for ufo in self.ufo_list:
            if ufo['health'] == 0 and ufo['visible']:
                # Move both UFOs to explosion position briefly
                explosion_pos = ufo['base'].copy()
                self._update_single_ufo_pose(ufo['red_ufo'], explosion_pos)  # Show red for explosion
                
                # Then hide both UFOs
                hidden_pos = explosion_pos.copy()
                hidden_pos[2, 3] = -100
                
                self._update_single_ufo_pose(ufo['normal_ufo'], hidden_pos)
                self._update_single_ufo_pose(ufo['red_ufo'], hidden_pos)
                        
                ufo['visible'] = False
                ufo['health'] = -1

        self.swift.step()   # Update environment

    def is_destroy_all(self) -> bool:
        """Check if all UFOs are destroyed"""
        for ufo in self.ufo_list:
            if ufo['health'] >= 1:
                return False
        return True

    def _generate_ufos_trajectory(self):
        """Generate trajectories for all UFOs"""
        def traj_generator(T1, T2, num_steps):
            trajectory = []
            step = 1/num_steps
            for i in np.arange(0, 1 + step, step):
                trajectory.append(spbase.trinterp(T1, T2, i))
            return trajectory
        
        self._traj_list = []
        
        for i in range(self.num_ufos):
            if self.ufo_list[i]['health'] < 1:
                # Dead UFOs don't get new trajectories
                self._traj_list.append([self.ufo_list[i]['base']] * self._num_traj_steps)
                continue
                
            # Generate random movement
            z = np.random.uniform(-1, 1)
            current_z = self.ufo_list[i]['base'][2, 3]
            
            if current_z >= self._ranges[5]:
                z = -1
            elif current_z <= 2:
                z = 1
                
            goal_tr = (self.ufo_list[i]['base'] @ 
                      spbase.trotz(np.random.uniform(-np.pi, np.pi)) @ 
                      spbase.transl(2, 2, z))
            
            # Ensure goal is within bounds
            while not (self._ranges[0] <= goal_tr[0, 3] <= self._ranges[1] and 
                      self._ranges[2] <= goal_tr[1, 3] <= self._ranges[3]):
                goal_tr = (self.ufo_list[i]['base'] @ 
                          spbase.trotz(np.random.uniform(-np.pi, np.pi)) @ 
                          spbase.transl(2, 2, z))
            
            self._traj_list.append(traj_generator(self.ufo_list[i]['base'], goal_tr, self._num_traj_steps))

    def _generate_random_transform(self):
        """Generate random transform within specified ranges"""
        x = np.random.uniform(self._ranges[0], self._ranges[1])
        y = np.random.uniform(self._ranges[2], self._ranges[3])
        z = np.random.uniform(2, self._ranges[5])
        yaw = np.random.uniform(-np.pi, np.pi)
        transform = SE3(x, y, z) * SE3.Rz(yaw)
        return transform.A

# ---------------------------------------------------------------------------------------#
def check_intersections(ee_tr: np.ndarray, 
                       cone_ends: List[np.ndarray], 
                       ufo_fleet: SwiftUFOFleet) -> List[int]:
    """
    Check for UFOs hit by the ray (unchanged from original)
    """
    ufo_hit_index = []
    ray_start = spbase.transl(ee_tr)

    for ray_end in cone_ends:
        for ufo_index, ufo in enumerate(ufo_fleet.ufo_list):
            if ufo['health'] < 1:
                continue
                
            ufo_point = spbase.transl(ufo['base'])
            ufo_normal = [0, 0, 1]

            intersection_point, check = line_plane_intersection(
                ufo_normal, ufo_point, ray_start, ray_end
            )

            if (check != 1 or 
                ufo_fleet._ship_radius < distance_between_points(intersection_point, ufo_point)):
                continue
            
            ufo_hit_index.append(ufo_index)
    
    return ufo_hit_index


def distance_between_points(point1: Union[np.ndarray, List[float]], 
                           point2: Union[np.ndarray, List[float]]) -> float:
    """Calculate distance between two points (unchanged from original)"""
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.linalg.norm(point1 - point2)

# ---------------------------------------------------------------------------------------#
# Usage example
if __name__ == '__main__':
    # Create Swift environment
    env = swift.Swift()
    env.launch(realtime=True)
    
    # Create UFO fleet
    ufo_fleet = SwiftUFOFleet(env, num_ufos=5)
    
    # Run simulation
    print("Starting UFO fleet simulation...")
    ufo_fleet.run_simulation(num_steps=200, real_time=True)
    
    print("Simulation complete!")
    print(f"First UFO pose: {SE3(ufo_fleet.ufo_list[0]['base'])}")