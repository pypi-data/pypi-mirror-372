##  @file
#   @brief This file contains the necessary functions for plotting ply file using plyfile package.
#   @author Ho Minh Quang Ngo
#   @date Jul 25, 2023
from typing import Optional, Union, List, Any
import numpy as np
import matplotlib.pyplot as plt
import warnings
import spatialmath.base as spbase
from plyfile import PlyData
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Path3DCollection
from trimesh import Trimesh

# ---------------------------------------------------------------------------------------#
def place_object(ply_file_path: Optional[str] = None,
                 vertices: Optional[np.ndarray] = None,
                 vertices_color: Optional[np.ndarray] = None,
                 faces: Optional[np.ndarray] = None,
                 faces_color: Optional[np.ndarray] = None,
                 output: str = 'scatter',
                 ax: Optional[plt.Axes] = None,
                 simplified: int = 1,
                 **kwargs: Any) -> Union[Path3DCollection, Poly3DCollection]:
    """
    Read a ply file and plot that object into current active axes. If there is no current active axes, a new one is created

    Parameters
    ----------
    :param ply_file_path: directory to the ply file. No need to input vertices and faces information if this param is supplied
    :type: string
    :param vertices: object's input vertices
    :type vertices: NDArray of N-vertices of the object (Nx3)
    :param vertices_color: object's input vertices color
    :type vertices_color: NDArray of N-vertex color of the object (Nx3)
    :param faces: face data in form of vertex indices array
    :type faces: NDAarray of face data - M faces x vertex index for each face
    :param faces_color: color data for each fay
    :type faces: NDAarray of face data color - N faces x color each face
    :param output: Output object type. 'scatter' for pointcloud or 'surface' for mesh object. Default to 'scatter'
    :param ax: current axes to plot on, default to None will create new 3D axes or plot on current active axes
    :param simplified: factor for simplifying the mesh object (i.e simplified = 10 will reduces the number of faces 10 times)
                       Applied for 'surface' output only. Cannot ensure coloring

    :kwargs: all attributes of the return object can go with set_ (i.e input 'sizes = 1', then it will do set_sizes(1))

    Return
    ----------
    an object of `mpl_toolkits.mplot3d.art3d.Path3DCollection` if default output
    or `mpl_toolkits.mplot3d.art3d.Poly3DCollection`if 'surface' output
    """

    if ply_file_path is not None:
        # Read the PLY file
        if simplified > 1 and output == 'surface':
            plydata = get_ply_data(ply_file_path, simplified)
        else:
            plydata = get_ply_data(ply_file_path)
        vertices = plydata['vertices']
        vertices_color = plydata['vertices_color']
        faces = plydata['faces']
        faces_color = plydata['faces_color']
    elif vertices is None:
        raise ValueError("Either ply_file_path or vertices must be provided!")
    elif output == 'surface' and faces is None:
        raise ValueError("Need face data!")

    if vertices_color is None:
        vertices_color = default_color_array(np.size(vertices,0))
    if faces_color is None and faces is not None:
        faces_color = default_color_array(np.size(faces,0))

    # Check for available current axes
    if ax is None:
        existing_axes = plt.gcf().axes
        if len(existing_axes) == 0: # If no current axes, then create one
            ax = plt.gcf().add_subplot(projection = '3d')
        else: # If there is a current axes, plot one that one
            ax = plt.gca()

    # Warning if plotting on a 2D axes
    if (ax.__class__.__name__ == 'Axes'):
        warnings.warn("Plotting on 2D axes")

    if output == 'scatter':
        # Plot the vertices as a 3D scatter plot into current active axes
        scatter_object = ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c = vertices_color)
        plot_object = scatter_object
    elif output == 'surface':
        # Plot the vertices as a 3D surface plot into current active axes
        try:
            mesh_object = Poly3DCollection(vertices[faces], linewidths=0.1, facecolors = faces_color, edgecolors='k')
        except ValueError:
            mesh_object = Poly3DCollection([vertices[indices] for indices in faces], linewidths=0.1, facecolors = faces_color, edgecolors='k')

        ax.add_collection(mesh_object)
        plot_object = mesh_object
    else:
        raise ValueError('Output is "shape" or "scatter"')

    for attr in kwargs:
        try:
            getattr(plot_object, f'set_{attr}')(kwargs[attr])
        except:
            print(f"Cannot set {attr}")
    return plot_object

# ---------------------------------------------------------------------------------------#
def get_ply_data(ply_file_path:str, simplified:float = 1):
    """
    Read a ply file and get the vertices, faces and vertices color, faces color data

    Parameters
    ----------
    :param ply_file_path: directory to the ply file
    :type: string
    :param simplified: factor for simplifying the mesh object (i.e simplified = 10 will reduces the number of faces 10 times)
                    Applied for 'surface' output only. Cannot ensure coloring

    Return
    ----------
    NDArray Nx3 vertices, NDArray Nx3 vertex color, NDArray Nx3 faces, NDArray Nx3 face colors
    """

    # Read the PLY file
    plydata = PlyData.read(ply_file_path)

    # Access the vertex data
    vertex_data = plydata['vertex']
    is_vertex_color =  'red' in vertex_data and 'green' in vertex_data and 'blue' in vertex_data # Check whether the file contains color

    # Extract the vertices as a NumPy array
    vertices = []
    vertices_color = []
    for vertex in vertex_data:
        vertices.append((vertex['x'], vertex['y'], vertex['z']))
        if is_vertex_color: # If the file has color for vertices, retrieve the data
            vertices_color.append(([vertex['red'],vertex['green'],vertex['blue']]))
    vertices = np.array(vertices)
    vertices_color = np.array(vertices_color)

    # Correct the colour, or set default color
    if is_vertex_color: # If the color exists, try change them to 0-1 RGB range
        if np.any(np.abs(vertices_color) > 1):
            vertices_color = vertices_color/255
    else: # Else set a default color
        vertices_color = default_color_array(np.size(vertices,0))

    # Get the face data in form of vertex-indices list
    # faces = np.array([list(indices) for indices in plydata['face']['vertex_indices']], dtype=int)
    faces = []
    for indices in plydata['face']['vertex_indices']:
        faces.append(np.array(list(indices), dtype= int))

    # Get the face color if exist
    faces_color = []
    is_faces_color = 'red' in plydata['face'] and 'green' in plydata['face'] and 'blue' in plydata['face']

    if is_faces_color:
        faces_color = np.column_stack((plydata['face']['red'], plydata['face']['green'], plydata['face']['blue']))
        # Correct the face color:
        if np.any(np.abs(faces_color) > 1):
            faces_color = faces_color/255
    # elif is_vertex_color:
    #     faces_color = vertices_color
    else:
        faces_color = default_color_array(len(faces))

    # Simplified output if required
    if simplified > 1:
        simplified_mesh = Trimesh(vertices = vertices,
                                  faces= faces).simplify_quadric_decimation(int(len(faces)/simplified))
        vertices = simplified_mesh.vertices
        faces = simplified_mesh.faces

    return {'vertices': vertices, 'vertices_color': vertices_color,
            'faces': faces, 'faces_color': faces_color}

# ---------------------------------------------------------------------------------------#
def get_vertices(scatter_object: Path3DCollection) -> np.ndarray:
    """
    Get vertices array of a Path3DCollection object

    Parameter
    ----------
    :param scatter_object: input object
    :type scatter_object: `mpl_toolkits.mplot3d.art3d.Path3DCollection`

    Return
    ----------
    NDArray of N-vertices of the object (Nx3)
    """
    x_array = scatter_object._offsets3d[0]
    y_array = scatter_object._offsets3d[1]
    z_array = scatter_object._offsets3d[2]
    return np.transpose(np.vstack((x_array, y_array, z_array)))

# ---------------------------------------------------------------------------------------#
def set_vertices(input_object: Union[Path3DCollection, Poly3DCollection],
                 vertices: np.ndarray,
                 faces: Optional[np.ndarray] = None) -> None:
    """
    Update the pointcloud of the object by an new array of vertices (3xN or Nx3)

    Parameter
    ----------
    :param input_object: input object
    :type input_object: `mpl_toolkits.mplot3d.art3d.Path3DCollection` or `mpl_toolkits.mplot3d.art3d.Poly3DCollection`
    :param vertices: object's desired vertices
    :type vertices: NDArray of N-vertices of the object
    :param faces: face data in form of vertex indices array
    :type faces NDAarray of face data - M faces x vertex index for each face
    """
    if isinstance(input_object, Path3DCollection):
        input_object._offsets3d = (vertices[:,0], vertices[:,1], vertices[:,2])
    elif isinstance(input_object, Poly3DCollection):
        if faces is not None:
            try:
                input_object.set_verts([vertices[indices] for indices in faces])
            except ValueError:
                pass
        else:
            input_object.set_verts(vertices)
    else:
        raise ValueError('Unknown type of object!')

def scale_object(input_object: Path3DCollection,
                 scale: Union[List[float], float]) -> None:
    """
    Scale an object by a scale, which is a list [x,y,z] or a scalar

    Parameter
    ----------
    :param input_object: input object
    :type scatter_object: `mpl_toolkits.mplot3d.art3d.Path3DCollection`
    :param scale: desired scale for input object
    :type scale: list of 3 or a scalar
    """
    if isinstance(input_object, Path3DCollection):
        xyz_original = input_object._offsets3d
        if isinstance(scale, list) and len(scale) == 3:
            # Scale all axes by corresponding value in scale
            x_scaled = xyz_original[0] * scale[0]
            y_scaled = xyz_original[1] * scale[1]
            z_scaled = xyz_original[2] * scale[2]
        elif isinstance(scale, (int, float)):
            # Scale all axes by the same scalar value
            x_scaled = xyz_original[0] * scale
            y_scaled = xyz_original[1] * scale
            z_scaled = xyz_original[2] * scale
        else:
            raise ValueError("Invalid scale argument")
        input_object._offsets3d = (x_scaled, y_scaled, z_scaled)

    elif isinstance(input_object, Poly3DCollection):
        pass

    else:
        raise ValueError('Invalid input object type')

def transform_vertices(vertices: np.ndarray,
                       transform: np.ndarray) -> np.ndarray:
    """
    Update an array of vertices (Nx3) by a transform

    Parameter
    ----------
    :param vertices: object's input vertices
    :type vertices: NDArray of N-vertices of the object (Nx3)
    :param transform: transform to update the object'vertices
    :type transform: SE3 Array

    Return
    ----------
    NDArray of N-vertices of the object after transform (Nx3)

    """
    num_vertices = np.size(vertices, 0)

    ## To do a matrix multiplication, we have to change the vertices array into homogeneous form and transpose it
    # Switch to homogeneous form
    one_col = np.ones([num_vertices, 1])
    new_vertices = np.hstack((vertices, one_col))
    new_vertices = np.transpose(new_vertices)

    # Do matrix multiplication
    new_vertices = transform @ np.array(new_vertices)
    new_vertices = np.transpose(new_vertices)

    return new_vertices[:,:-1]

def move_object(scatter_object: Path3DCollection,
                transform: np.ndarray) -> None:
    """
    Move the input object by a transform

    Parameter
    ----------
    :param scatter_object: input object
    :type scatter_object: `mpl_toolkits.mplot3d.art3d.Path3DCollection`
    :param transform: transform in global frame to move the object
    :type transform: SE3 Array

    """
    # Get vertices of the object
    vertices = get_vertices(scatter_object)
    num_vertices = np.size(vertices, 0)

    ## To do a matrix multiplication, we have to change the vertices array into homogeneous form and transpose it
    # Switch to homogeneous form
    one_col = np.ones([num_vertices, 1])
    vertices = np.hstack((vertices, one_col))
    vertices = np.transpose(vertices)

    # Do matrix multiplication
    vertices = transform @ np.array(vertices)

    # Update the object position
    scatter_object._offsets3d = (vertices[0, :], vertices[1, :], vertices[2, :])

def default_color_array(size: int) -> np.ndarray:
    """
    Create an array of size x 3 RGB color [0-1]
    """
    values = np.linspace(0, 1, size)
    # Create the color array with RGB values
    color = np.zeros((size, 3))
    color[:, 0] = values  # Red component
    color[:, 1] = 1-values   # Green component
    color[:, 2] = 0.5  # Blue component
    return color

# ---------------------------------------------------------------------------------------#
if __name__ == "__main__":
    # Plot a test object in the current directory
    spbase.plotvol3([-2,2])
    my_object = place_object(ply_file_path = 'cow.ply', simplified= 5, output= 'surface', linewidth = 0.01)
    # Show the plot
    plt.show()
