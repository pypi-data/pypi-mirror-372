import numpy as np

def orthogonalize_rotation(R: np.ndarray) -> np.ndarray:
    """
    Orthogonalize a 2x2 or 3x3 rotation matrix using the Gram-Schmidt process.

    Parameters:
    ____________

    `R`: np.ndarray
        A 2x2 or 3x3 rotation matrix to be orthogonalized

    """
    if R.shape == (2, 2):
        # Extract the columns of the rotation matrix
        c1, c2 = R[:, 0], R[:, 1]

        # Orthogonalize the columns using Gram-Schmidt process
        u1 = c1 / np.linalg.norm(c1)
        u2 = c2 - np.dot(u1, c2) * u1
        u2 = u2 / np.linalg.norm(u2)

        # Construct the orthogonalized rotation matrix
        orthogonalized_R = np.column_stack((u1, u2))

    elif R.shape == (3, 3):
        # Extract the columns of the rotation matrix
        c1, c2, c3 = R[:, 0], R[:, 1], R[:, 2]

        # Orthogonalize the columns using Gram-Schmidt process
        u1 = c1 / np.linalg.norm(c1)
        u2 = c2 - np.dot(u1, c2) * u1
        u2 = u2 / np.linalg.norm(u2)
        u3 = c3 - np.dot(u1, c3) * u1 - np.dot(u2, c3) * u2
        u3 = u3 / np.linalg.norm(u3)

        # Construct the orthogonalized rotation matrix
        orthogonalized_R = np.column_stack((u1, u2, u3))

    else:
        raise ValueError("Input matrix must be either 2x2 or 3x3.")

    return orthogonalized_R
