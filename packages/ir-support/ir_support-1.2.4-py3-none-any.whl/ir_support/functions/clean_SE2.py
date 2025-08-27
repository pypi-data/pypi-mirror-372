from spatialmath import SE2
import numpy as np

def clean_SE2(T):
    """
    Return an SE2 object with an orthogonalized rotation matrix.

    Parameters
    ----------
    T : SE2 or np.ndarray
        A 3x3 SE(2) matrix or SE2 object.

    Returns
    -------
    SE2
        A new SE2 object with a corrected, orthogonal rotation.

    Raises
    ------
    ValueError
        If T is not a valid 3x3 homogeneous transformation.
    """
    if hasattr(T, 'A'):
        T = T.A  # Extract matrix if T is an SE2 object

    R = T[0:2, 0:2]
    U, _, Vt = np.linalg.svd(R)
    T[0:2, 0:2] = U @ Vt  # Re-orthogonalize rotation
    return SE2(T)
