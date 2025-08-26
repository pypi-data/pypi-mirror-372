# -*- coding: utf8 -*-
# Development on Resimitpo began in 2007 with funding from the National
# Science Foundation of the USA, DMS-0712796.
#
# Contributors include:
#
# Russell Luke (main author)
# Institute for Numerical and Applied  Mathematics, University of Göttingen
#
# Student helpers:
# Rachael Bailine (Matlab and Fortran version),  University of Delaware
# Patrick Rowe (Fortran version), University of Delaware
# Brian Rife (Fortran version), University of Delaware
# Marco Bedolla (Fortran version), University of Delaware
# Benedikt Rascher-Friesenhausen (Python version), University of Göttingen
#
# Special thanks to Laurence Marks at Northwestern University and
# Peter Blaha at the Technical University of Vienna who provided much
# of the inspiration for Resimitpo.
"""
Contains all implementations of history functions.

History functions
=================

.. autofunction:: resimitpo.history.fdSY_mat
.. autofunction:: resimitpo.history.cdSY_mat
"""
from numpy import repeat


# PYTHON PORT ANNOTATION
# Removed parameter K, as it's value can be obtained from
# the shape of x_mat.
def fdSY_mat(mem, x_mat, gradf_mat):
    """Finite difference history ordering.

    Finite difference history ordering for limited memory matrix
    secant methods.

    Parameters
    ----------
    mem : int
        TODO
    x_mat : array_like
        The matrix of iterates.
    gradf_mat : array_like
        The matrix of gradients.

    Returns
    -------
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.

    See Also
    --------
    cdSY_mat : Alternative function.
    history_wrapper : Wrapper to call this function.
    """
    # PYTHON PORT ANNOTATION
    # In the MATLAB code tmp_mat will always contain the mem-th column of
    # x_mat, repeated mem-1 times.
    tmp_mat = repeat(x_mat[:, mem-1], mem-1).reshape((-1, mem-1))
    S_mat = x_mat[:, 0:mem-1] - tmp_mat
    # PYTHON PORT ANNOTATION
    # In the MATLAB code tmp_mat will always contain the mem-th column of
    # gradf_mat, repeated mem-1 times.
    tmp_mat = repeat(gradf_mat[:, mem-1], mem-1).reshape((-1, mem-1))
    Y_mat = gradf_mat[:, 0:mem-1] - tmp_mat

    return S_mat, Y_mat


# PYTHON PORT ANNOTATION
# Removed parameter K, as it's value can be obtained from
# the shape of x_mat.
def cdSY_mat(mem, x_mat, gradf_mat):
    """
    Conjugate direction history ordering.

    Conjugate direction history ordering for limited memory matrix
    secant methods.

    Parameters
    ----------
    mem : int
        TODO
    x_mat : array_like
        The matrix of iterates.
    gradf_mat : array_like
        The matrix of gradients.

    Returns
    -------
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.

    See Also
    --------
    fdSY_mat : Alternative function.
    history_wrapper : Wrapper to call this function.
    """
    S_mat = x_mat[:, 1:mem] - x_mat[:, 0:mem-1]
    Y_mat = gradf_mat[:, 1:mem] - gradf_mat[:, 0:mem-1]

    return S_mat, Y_mat


def history_wrapper(History, mem, x_mat, gradf_mat):
    """Wrapper for all history functions.

    Provides a unified function call for all history functions.

    Parameters
    ----------
    mem : int
        TODO
    x_mat : array_like
        The matrix of iterates.
    gradf_mat : array_like
        The matrix of gradients.

    Returns
    -------
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.

    See Also
    --------
    fdSY_mat, cdSY_mat
    """
    if History is fdSY_mat:
        return fdSY_mat(mem, x_mat, gradf_mat)

    if History is cdSY_mat:
        return cdSY_mat(mem, x_mat, gradf_mat)
