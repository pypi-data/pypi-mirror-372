# my_package/__init__.py
# from pygator.module import *
# from ._version import __version__

# pygator/__init__.py
import numpy as np

def multiply_abcd(*matrices, reverse=True, q_in=None):
    """
    Multiply an arbitrary number of ABCD matrices and optionally 
    propagate a Gaussian beam q-parameter.

    Parameters
    ----------
    *matrices : array-like
        Any number of 2x2 numpy arrays representing ABCD matrices.
        Example: multiply_abcd(M1, M2, M3)

    reverse : bool, optional (default=True)
        If True, multiply in reverse order (optical convention: 
        beam hits last matrix first).
        If False, multiply in given order.

    q_in : complex or None, optional
        Input Gaussian beam q-parameter. If provided, the output q 
        after propagation is also returned.

    Returns
    -------
    result : ndarray
        2x2 numpy array representing the combined ABCD matrix.

    q_out : complex (optional)
        Output q-parameter if q_in is given.
    """

    # Ensure all are numpy arrays
    mats = [np.array(M, dtype=float) for M in matrices]

    # Reverse order if needed
    if reverse:
        mats = mats[::-1]

    # Multiply sequentially
    result = np.eye(2)
    for M in mats:
        result = result @ M

    if q_in is not None:
        A, B, C, D = result.ravel()
        q_out = (A * q_in + B) / (C * q_in + D)
        return result, q_out

    return result


def multiply_matrices(*matrices, reverse=False, q_in=None):
    """
    Multiply an arbitrary number of square matrices.
    Works for 2x2 (ABCD, Jones), 3x3, NxN, etc.
    
    Parameters
    ----------
    *matrices : list of ndarray
        Matrices to multiply.
    reverse : bool, optional
        If True, multiply in reverse order (last applied first).
    q_in : complex, optional
        If provided, applies ABCD transformation (only valid for 2x2 matrices).
    
    Returns
    -------
    M_total : ndarray
        Product of all matrices.
    q_out : complex or None
        If q_in is given and matrices are 2x2, return output q.
    """
    
    if reverse:
        matrices = matrices[::-1]
    
    # Ensure all matrices are numpy arrays (allowing complex)
    mats = [np.array(M, dtype=complex) for M in matrices]
    
    # Infer dimension from first matrix
    n = mats[0].shape[0]
    M_total = np.eye(n, dtype=complex)
    
    for M in mats:
        M_total = M @ M_total
    
    # If q_in is provided and we are in 2x2 land, apply ABCD transform
    if q_in is not None and n == 2:
        A, B, C, D = M_total[0,0], M_total[0,1], M_total[1,0], M_total[1,1]
        q_out = (A * q_in + B) / (C * q_in + D)
        return M_total, q_out
    
    return M_total
