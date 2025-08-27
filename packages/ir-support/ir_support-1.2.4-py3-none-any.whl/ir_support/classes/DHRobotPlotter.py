import roboticstoolbox as rtb
import numpy as np
from spatialgeometry import Cylinder
from spatialmath import SE3
import swift

class CylindricalDHRobotPlot:
    """
    Creates cylindrical link visualization for DHRobot in Swift simulator
    Attaches cylinders as link geometry instead of individual objects
    """
    
    def __init__(self, robot, cylinder_radius=0.02, color="#3478f6", multicolor=False):
        self.robot = robot
        self.cylinder_radius = cylinder_radius
        self.multicolor = multicolor
        
        # Handle color options
        if multicolor:
            self.colors = self._generate_color_palette(len(robot.links))
        elif isinstance(color, list):
            self.colors = color
        else:
            self.colors = [color]  # Single color for all links

        
    def _generate_color_palette(self, num_colors):
        """Generate a distinct color palette for multi-colored links"""
        import colorsys
        
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            saturation = 0.8
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            # Convert to hex or named color for Swift
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
            )
            colors.append(hex_color)
        return colors
    
    
    def create_cylinders(self):
        """Create cylindrical links and attach them as link geometry"""
        # Get robot segments (same approach as RobotPlot)
        segments = self.robot.segments()
        
        # Compute all link frame transformations at current configuration
        T = self.robot.fkine_all(self.robot.q)
        
        # Track which links get geometry
        geometry_assigned = []
        
        for segment in segments:
            linkframes = []
            for link in segment:
                if link is None:
                    linkframes.append(self.robot.base)
                else:
                    linkframes.append(T[link.number])
            
            # Create cylinders between consecutive frames in each segment
            for i in range(len(linkframes) - 1):
                start_frame = linkframes[i]
                end_frame = linkframes[i + 1]
                
                # Determine which link this cylinder represents
                if i < len(segment) - 1 and segment[i + 1] is not None:
                    link_index = segment[i + 1].number - 1  # Convert to 0-based indexing
                    color_index = link_index % len(self.colors)
                    
                    # Calculate cylinder directly in link's local coordinate system
                    cylinder = self._create_cylinder_for_link(
                        start_frame, end_frame, T[link_index + 1], 
                        color=self.colors[color_index]
                    )
                    
                    if cylinder is not None and link_index < len(self.robot.links):
                        # Attach to link (cylinder is already in local coordinates)
                        self.robot.links[link_index].geometry = [cylinder]
                        geometry_assigned.append(link_index)
        
        return self.robot
    
    
    def _create_cylinder_for_link(self, start_frame, end_frame, link_frame, color=None):
        """Create a cylinder in the link's local coordinate system"""
        # Transform start and end points to link's local coordinate system
        link_inv = link_frame.inv()
        local_start = link_inv * start_frame.t
        local_end = link_inv * end_frame.t
        
        # Calculate direction vector and length in local coordinates
        direction_vector = local_end - local_start
        length = np.linalg.norm(direction_vector)
        
        # Only create cylinder if there's significant length
        if length < 0.001:
            return None
        
        # Calculate cylinder center in local coordinates
        center = (local_start + local_end) / 2
        
        # Calculate orientation: align cylinder z-axis with direction vector
        direction_unit = direction_vector / length
        
        # FIX: Ensure both vectors are 1D arrays for dot product
        direction_unit = direction_unit.flatten()  # Convert to 1D array
        z_axis = np.array([0, 0, 1])
        
        if np.abs(np.dot(direction_unit, z_axis)) > 0.9999:
            # Direction is already aligned with z-axis
            rotation = np.eye(3)
        else:
            # Calculate rotation to align z-axis with direction
            v = np.cross(z_axis, direction_unit)
            s = np.linalg.norm(v)
            c = np.dot(z_axis, direction_unit)
            
            if s > 1e-10:  # Not parallel
                vx = np.array([[0, -v[2], v[1]],
                              [v[2], 0, -v[0]],
                              [-v[1], v[0], 0]])
                rotation = np.eye(3) + vx + np.dot(vx, vx) * ((1 - c) / (s * s))
            else:
                rotation = np.eye(3)
        
        # FIX: Ensure center is also flattened to avoid shape issues
        center = center.flatten()
        
        # Create transformation matrix in local coordinates
        cylinder_pose = SE3.Rt(rotation, center)
        
        # Use provided color or default
        if color is None:
            color = self.colors[0] if self.colors else "#3478f6"
        
        # Create cylinder geometry in local coordinates
        cylinder = Cylinder(
            radius=self.cylinder_radius,
            length=length,
            pose=cylinder_pose,
            color=color
        )
        
        return cylinder
    
    
    def update(self, q):
        """Update robot configuration - geometry will move automatically"""
        self.robot.q = q
        # No need to recreate geometry, just update joint angles
        # The Swift environment will handle the visualization update
        return self.robot
    
    
    def clear_geometry(self):
        """Remove geometry from all links"""
        for link in self.robot.links:
            if hasattr(link, 'geometry'):
                link.geometry = []



# Enhanced version that also adds spheres at joints - WIP: CURRENTLY CAUSES SEG FAULT
class EnhancedCylindricalDHRobotPlot(CylindricalDHRobotPlot):
    """Enhanced version that also adds spheres at joints as geometry"""
    
    def __init__(self, robot, cylinder_radius=0.02, joint_radius=0.03, 
                 cylinder_color="#3478f6", joint_color="red", multicolor=False):
        super().__init__(robot, cylinder_radius, cylinder_color, multicolor)
        self.joint_radius = joint_radius
        self.joint_color = joint_color
    
    def create_cylinders(self):
        """Create both cylinders and joint spheres as link geometry"""
        # First create cylinders
        robot = super().create_cylinders()
        
        # Then add joint spheres
        self._add_joint_spheres()
        
        return robot
    
    def _add_joint_spheres(self):
        """Add spheres at joint locations as additional geometry"""
        from spatialgeometry import Sphere
        
        for i, link in enumerate(self.robot.links):
            # Create a sphere at the origin of each link frame
            joint_sphere = Sphere(
                radius=self.joint_radius,
                color=self.joint_color
            )
            
            # Add sphere to existing geometry or create new geometry list
            if hasattr(link, 'geometry') and isinstance(link.geometry, list):
                link.geometry.append(joint_sphere)
            else:
                # If there's existing geometry that's not a list, preserve it
                existing = getattr(link, 'geometry', [])
                if existing and not isinstance(existing, list):
                    existing = [existing]
                elif not existing:
                    existing = []
                
                link.geometry = existing + [joint_sphere]


# Usage examples
def demo_geometry_robot():
    """Demonstrate robot with geometry attached to links"""
    import time
    
    # Create a DHRobot
    robot = rtb.models.DH.Panda()
    
    # Create Swift environment
    env = swift.Swift()
    env.launch(realtime=True)
    
    print("Creating cylindrical robot with link geometry...")
    
    # Create cylindrical visualization
    cyl_viz = CylindricalDHRobotPlot(robot, cylinder_radius=0.05, multicolor=True)
    robot_with_geometry = cyl_viz.create_cylinders()
    
    # Add robot to environment (only once!)
    env.add(robot_with_geometry)
    
    print("Animating robot...")
    
    # Generate some trajectory
    q_start = robot.qz
    q_end = robot.qr
    
    for i in range(100):
        # Interpolate between start and end configurations
        alpha = (np.sin(i * 0.1) + 1) / 2  # Smooth oscillation
        q = q_start + alpha * (q_end - q_start)
        
        # Update robot configuration
        robot.q = q
        
        # Environment step (robot geometry updates automatically)
        env.step()
        time.sleep(0.05)
    
    env.hold()


# Convenience factory functions
def create_geometry_robot(robot, cylinder_radius=0.02, multicolor=True):
    """Create a robot with cylindrical geometry attached to links"""
    cyl_viz = CylindricalDHRobotPlot(robot, cylinder_radius, multicolor=multicolor)
    return cyl_viz.create_cylinders()


def create_enhanced_geometry_robot(robot, cylinder_radius=0.02, joint_radius=0.03, multicolor=True):
    """Create a robot with both cylindrical links and joint spheres"""
    enhanced_viz = EnhancedCylindricalDHRobotPlot(
        robot, 
        cylinder_radius=cylinder_radius, 
        joint_radius=joint_radius,
        multicolor=multicolor
    )
    return enhanced_viz.create_cylinders()


if __name__ == "__main__":
    demo_geometry_robot()