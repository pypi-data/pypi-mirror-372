import numpy as np
import matplotlib.pyplot as plt

def draw_possible_ellipse_given_foci(focus1:np.ndarray, focus2:np.ndarray, a=None, ax=None):
    """
    Simple custom function to draw an ellipse with 2 given focii

    Parameters
    ----------
    focus1 : np.ndarray
        First focus of the ellipse
    focus2 : np.ndarray
        Second focus of the ellipse
    a : float, optional
        Default length for semi-major axis of the ellipse, by default 0.75 * distance between focii
    ax : matplotlib.axes.Axes, optional
        Axes to plot the ellipse, by default None
    """

    # Calculate the distance from center to each focus
    c = np.linalg.norm(focus1 - focus2) / 2.0

    # Calculate the default semi-major axis
    if a is None or a < c:
        a = c * 1.5

    # Calculate the center of the ellipse
    center = (focus1 + focus2) / 2.0

    # Calculate the semi-major axis
    b = np.sqrt(a**2 - c**2)

    # Calculate the orientation angle of the ellipse
    angle = np.arctan2(focus2[1] - focus1[1], focus2[0] - focus1[0])

    # Generate an array of angles from 0 to 2*pi
    angles = np.linspace(0, 2*np.pi, 100)

    # Calculate the coordinates of points on the rotated ellipse
    x_rotated = center[0] + a * np.cos(angles) * np.cos(angle) - b * np.sin(angles) * np.sin(angle)
    y_rotated = center[1] + a * np.cos(angles) * np.sin(angle) + b * np.sin(angles) * np.cos(angle)

    # Plot the ellipse
    if ax is None:
        ax = plt.gca()
    ax.plot(x_rotated, y_rotated, 'g')
