import numpy as np
from typing import Union, List, Tuple

def line_plane_intersection(plane_normal:Union[np.ndarray, List[float]],
                            point_on_plane:Union[np.ndarray, List[float]],
                            point1_on_line:Union[np.ndarray, List[float]],
                            point2_on_line:Union[np.ndarray, List[float]],)->Tuple[np.ndarray, int]:
    """
    Given a plane (normal and point) and two points that make up another line, get the intersection
    - Check == 0 if there is no intersection
    - Check == 1 if there is a line plane intersection between the two points
    - Check == 2 if the segment lies in the plane (always intersecting)
    - Check == 3 if there is intersection point which lies outside line segment

    Parameters
    ----------
    plane_normal : np.ndarray
        Normal vector of the plane
    point_on_plane : np.ndarray
        Point on the plane
    point1_on_line : np.ndarray
        First point on the line
    point2_on_line : np.ndarray
        Second point on the line
    """

    intersection_point = [0,0,0]
    u = np.array(point2_on_line) - np.array(point1_on_line)
    w = np.array(point1_on_line) - np.array(point_on_plane)
    D = np.dot(np.array(plane_normal), u)
    N = -np.dot(np.array(plane_normal), w)
    check = 0

    if np.abs(D) < pow(10,-7):                          # The segment is parallel to plane
        if N == 0:                                      # The segment lies in plane
            check = 2
            return intersection_point, check
        else:
            return intersection_point, check            # No intersection

    # Compute the intersection parameter
    sI = N/D
    intersection_point = point1_on_line + sI * u

    if sI < 0 or sI > 1:
        check = 3                                       # The intersection point lies outside the segment, so there is no intersection
    else:
        check = 1

    return intersection_point, check
