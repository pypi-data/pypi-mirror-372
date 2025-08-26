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
"""Contains the memory update rountine for
:class:`resimitpo.resimitpo.Resimitpo`.

Memory update
=============

.. autofunction:: resimitpo.memory.Memory_update
"""
from numpy import dot
from numpy.linalg import norm


# PYTHON PORT ANNOTATION
# Renamed iter to it, as iter is a keyword in Python.
# Removed parameter maxmem, as it is not needed in Python.
def Memory_update(x_mat, f_vec, gradf_mat, ngradf_vec, stepsize_vec,
                  mem, psd, it, accept_step):
    """Memory update routine.

    Parameters
    ----------
    x_mat : array_like, modified
        TODO. Gets modified.
    f_vec : array_like, modified
        TODO. Gets modified.
    gradf_mat : array_like, modified
        TODO. Gets modified.
    ngradf_vec : array_like, modified
        TODO. Gets modified.
    stepsize_vec : array_like, modified
        TODO. Gets modified.
    mem : int
        TODO
    psd : int
        TODO
    it : int
        The current iteration.
    accept_step : int
        TODO

    Returns
    -------
    x_mat : array_like
        TODO
    f_vec : array_like
        TODO
    gradf_mat : array_like
        TODO
    ngradf_vec : array_like
        TODO
    stepsize_vec : array_like
        TODO
    mem : int
        TODO
    """
    ######################################################################
    # Update the memory
    ######################################################################
    if psd == 1:
        # extra check that sty>0 for BFGS-based methods
        s_vec = x_mat[:, -1] - x_mat[:, -2]
        y_vec = gradf_mat[:, -1] - gradf_mat[:, -2]
        sty = dot(s_vec, y_vec)
        sty_tol = norm(y_vec)*norm(s_vec)*1e-12

        if sty <= sty_tol:
            # lost positive defniniteness:  delete old memory elements
            if accept_step == 1:
                # still made progress, so keep new point and reset history
                mem = 0
                x_mat[:, -2] = x_mat[:, -1]
                gradf_mat[:, -2] = gradf_mat[:, -1]
                # PYTHON PORT ANNOTATION
                # Replaced sqrt(dot(...)) with norm(...).
                ngradf_vec[it+1] = norm(gradf_mat[:, -1])
            elif accept_step == 0:
                # did not make progress, reset history starting from
                # current point
                mem = 0
                ngradf_vec[it+1] = ngradf_vec[it]

        else:
            if accept_step == 0:
                # No progress, but keep new information.
                # Recenter the steps: keep the current step the center
                #    and move the new information back in the memory
                f_vec[it], f_vec[it+1] = \
                    f_vec[it+1], f_vec[it]
                ngradf_vec[it+1] = ngradf_vec[it]
                # PYTHON PORT ANNOTATION
                # Replaced sqrt(dot(...)) with norm(...).
                ngradf_vec[it] = norm(gradf_mat[:, -1])

                # update memory
                mem = min(mem+1, x_mat.shape[1]-2)
                x_mat[:, 0:-2] = x_mat[:, 1:-1]
                x_mat[:, -2] = x_mat[:, -1]
                gradf_mat[:, 0:-2] = gradf_mat[:, 1:]
                gradf_mat[:, -2] = gradf_mat[:, -1]
                # PYTHON PORT ANNOTATION
                # Replaced sqrt(dot(...)) with norm(...).
                ngradf_vec[it+1] = norm(gradf_mat[:, -1])
            elif accept_step == -1:
                # No progress, don't take the step and shrink memory.
                # update memory
                mem = max(mem-1, 0)
                ngradf_vec[it+1] = ngradf_vec[it]
            elif accept_step == -2:
                # did not make progress, reset history starting from
                # current point
                mem = 0
                ngradf_vec[it+1] = ngradf_vec[it]
            elif accept_step == 1:
                # step accepted --> model working
                # take the proposed step and update memory
                mem = min(mem+1, x_mat.shape[1]-2)
                x_mat[:, 0:-2] = x_mat[:, 1:-1]
                x_mat[:, -2] = x_mat[:, -1]
                gradf_mat[:, 0:-2] = gradf_mat[:, 1:-1]
                gradf_mat[:, -2] = gradf_mat[:, -1]
                # PYTHON PORT ANNOTATION
                # Replaced sqrt(dot(...)) with norm(...).
                ngradf_vec[it+1] = norm(gradf_mat[:, -1])

    elif accept_step == 0:
        # step not acctepted --> past information
        # is no good, but don't throw away new information.
        # Recenter the steps: keep the current step the center
        #    and move the new information back in the memory
        f_vec[it], f_vec[it+1] = f_vec[it+1], f_vec[it]
        ngradf_vec[it+1] = ngradf_vec[it]
        # PYTHON PORT ANNOTATION
        # Replaced sqrt(dot(...)) with norm(...).
        ngradf_vec[it] = norm(gradf_mat[:, -1])

        # update memory
        mem = min(mem+1, x_mat.shape[1]-2)
        x_mat[:, 0:-2] = x_mat[:, 1:-1]
        x_mat[:, -2] = x_mat[:, -1]
        gradf_mat[:, 0:-2] = gradf_mat[:, 1:-1]
        gradf_mat[:, -2] = gradf_mat[:, -1]
        # PYTHON PORT ANNOTATION
        # Replaced sqrt(dot(...)) with norm(...).
        ngradf_vec[it+1] = norm(gradf_mat[:, -1])
    elif accept_step == -1:
        # No progress, don't take the step and shrink memory.
        # update memory
        mem = max(mem-1, 0)
        ngradf_vec[it+1] = ngradf_vec[it]
    elif accept_step == -2:
        # did not make progress, reset history starting from
        # current point
        mem = 0
        ngradf_vec[it+1] = ngradf_vec[it]
    elif accept_step == 1:
        # model working
        # take the proposed step and update memory
        mem = min(mem+1, x_mat.shape[1]-2)

    stepsize_vec[it+1] = stepsize_vec[it]

    return x_mat, f_vec, gradf_mat, ngradf_vec, stepsize_vec, mem
