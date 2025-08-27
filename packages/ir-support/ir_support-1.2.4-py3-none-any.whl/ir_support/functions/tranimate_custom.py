import numpy as np
import matplotlib.pyplot as plt
from spatialmath.base import trinterp, tranimate
from typing import Generator, Optional, Union, List, Tuple

def tranimate_custom(T1: np.ndarray, T2: np.ndarray,
                     speed: int = 1, dim: Optional[Union[List[float], Tuple[float, ...]]] = None,
                     hold: bool = False) -> None:
    """
    Supported function to animate motion from transform T1 to T2 (SE3)

    :param T1: initial SE3 matrix
    :type T1: SE3 ndarray
    :param T2: final SE3 matrix
    :type T2: SE3 ndarray
    :param speed: Speed of the animation from 1 to 100. Default is 1
    :type speed: int
    :param dim: plot volume
    :type dim: list or tuple, [a] or [a1,a2] or [a,a2,b1,b2,c1,c2], default is [-2,2],
                or the absolute maximum translation value between two transforms [0, max]
    :param hold: keep the current frame or not, False by default
    :type hold: bool
    """
    # Clamp speed and convert to step count (higher speed = fewer steps)
    speed = max(1, min(speed, 100))
    steps = int(np.interp(speed, [0, 100], [100, 5]))  # 1% → 100 steps, 100% → 1 steps,     
    print(f"Animating from T1 {T1[0:3, 3]} to T2 {T2[0:3, 3]} with {steps} steps at speed {speed}.")

    t1_max = np.max([np.fabs(x) for x in T1[0:3, 3]])
    t2_max = np.max([np.fabs(x) for x in T2[0:3, 3]])
    max_value = np.max([t1_max, t2_max])
    if dim is None:
        if max_value > 2:
            dim = [0, max_value]
        else:
            dim = [-2, 2]

    # Get or create 3D axis
    fig = plt.gcf()

    # Try to find an existing 3D axes
    ax = None
    for candidate in fig.axes:
        if hasattr(candidate, 'get_zlim'):  # crude check for 3D axes
            ax = candidate
            # print("Reusing existing 3D axes.")
            break

    if ax is None:
        ax = fig.add_subplot(111, projection='3d')
        # print("Created new 3D axes.")
        ax.set_xlim(dim[0], dim[1])
        ax.set_ylim(dim[0], dim[1])
        ax.set_zlim(dim[0], dim[1])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_box_aspect([1, 1, 1])

    # Step through the animation
    artists = []
    for s in np.linspace(0, 1, steps):
        T = trinterp(start=T1, end=T2, s=s)

        # Remove previous artists (if any)
        for a in artists: getattr(a, 'remove', lambda: None)()

        # Extract origin and axis directions from transform
        origin = T[:3, 3]
        x_axis = T[:3, 0]
        y_axis = T[:3, 1]
        z_axis = T[:3, 2]

        # Draw axes as quivers
        artists = []
        artists.append(ax.quiver(*origin, *x_axis, color='r', length=1, normalize=True))
        artists.append(ax.quiver(*origin, *y_axis, color='g', length=1, normalize=True))
        artists.append(ax.quiver(*origin, *z_axis, color='b', length=1, normalize=True))

        # print("Current step:", s, "T:", T[0:3, 3])
        plt.pause(0.01)

    # Remove final frame if hold is False
    if not hold:
    #     plt.cla()
        for a in artists: getattr(a, 'remove', lambda: None)()
        plt.draw()


# This function is deprecated, use tranimate_custom instead
# But it is being temporarily kept for testing purposes
def tranimate_custom_old(T1: np.ndarray, T2: np.ndarray,
                     speed: int = 1, dim: Optional[Union[List[float], Tuple[float, ...]]] = None,
                     hold: bool = False) -> None:
    """
    Supported function to animate motion from transform T1 to T2 (SE3)

    :param T1: initial SE3 matrix
    :type T1: SE3 ndarray
    :param T2: final SE3 matrix
    :type T2: SE3 ndarray
    :param speed: Speed of the animation from 1 to 100. Default is 1
    :type speed: int
    :param dim: plot volume
    :type dim: list or tuple, [a] or [a1,a2] or [a,a2,b1,b2,c1,c2], default is [-2,2],
                or the absolute maximum translation value between two transforms [0, max]
    :param hold: keep the current frame or not, False by default
    :type hold: bool
    """
    valid_speed = int(max(1, min(speed, 100))) # check the speed input
    step_num = -valid_speed + 101
    step = 1/step_num
    def generator_transforms():
        """
        Supported function which is a generator to interpolate from transform T1 to T2
        """
        for i in np.arange(0, 1 + step, step):
            interp_step = i
            if i > 1: interp_step = 1
            yield trinterp(start= T1, end= T2, s= interp_step)

    t1_max = np.max([np.fabs(x) for x in T1[0:3, 3]])
    t2_max = np.max([np.fabs(x) for x in T2[0:3, 3]])
    max_value = np.max([t1_max, t2_max])
    if dim is None:
        if max_value > 2:
            dim = [0, max_value]
        else:
            dim = [-2, 2]
    tranimate(generator_transforms(), dim= dim, wait= True)
    if not hold:
        plt.cla()
