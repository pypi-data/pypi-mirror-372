"""Contains all implementations of hessian products.

Hessian functions
=================

Some introductory text.

.. autofunction:: resimitpo.hessian.BFGS1_product
.. autofunction:: resimitpo.hessian.Broyden1_product
.. autofunction:: resimitpo.hessian.Broyden2_product
.. autofunction:: resimitpo.hessian.invBFGS1_product
.. autofunction:: resimitpo.hessian.invBroyden1_product
.. autofunction:: resimitpo.hessian.invBroyden2_product
.. autofunction:: resimitpo.hessian_wrapper


Scaler functions
================

These functions are used to determine the `scale` variable for the
hessian functions.

.. autofunction:: resimitpo.hessian.delta_invBFGS
.. autofunction:: resimitpo.hessian.delta_MSB2
.. autofunction:: resimitpo.hessian.scaler_wrapper

"""
from numpy import abs, c_, dot, diag, eye, r_, sqrt, tril, triu, zeros
from numpy.linalg import cholesky, norm, solve
from numpy.random import random, seed


# PYTHON PORT ANNOTATION
# Removed parameters dim and mem, as the value can be obtained from
# the shape of S_mat/Y_mat.
def delta_MSB2(S_mat, Y_mat, alpha):
    """Scaling for the MSB2 matrix.

    Parameters
    ----------
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    alpha : float
        A regularisation parameter.

    Returns
    -------
    float
        TODO

    See Also
    --------
    delta_invBFGS : Alternative function.
    resimitpo.resimitpo.Normsqresid, resimitpo.step_finder.Step_generator
    """
    dim = Y_mat.shape[1]
    # normalize the columns of Y_mat for stability
    ny = zeros(dim)
    for j in range(dim):
        ny[j] = 1./norm(Y_mat[:, j])

    # PYTHON PORT ANNOTATION
    # In Python we can't modify the input parameters as they are
    # just references to the originals in the calling function.
    Yc_mat = dot(Y_mat, diag(ny))
    Sc_mat = dot(S_mat, diag(ny))

    # Look into doing a Cholesky factorization of Y'Y for stability
    M_mat = solve(dot(Yc_mat.T, Yc_mat) + alpha*eye(dim, dim), Yc_mat.T)
    seed(5489)   # sets the same seed for the same 'random' vector
    v0_vec = random(S_mat.shape[0])   # used to compute Rayleigh quotient

    delta0 = 0
    delta = 10

    RQ_iter = 0
    v_vec = dot(Sc_mat, dot(M_mat, v0_vec))
    while abs((delta - delta0)/delta) > 1e-5 and RQ_iter < 10:
        RQ_iter += 1
        v0_vec = v_vec/sqrt(dot(v_vec, v_vec))
        delta0 = delta
        v_vec = dot(Sc_mat, dot(M_mat, v0_vec))
        delta = dot(v0_vec, v_vec)

    return abs(delta)


# PYTHON PORT ANNOTATION
# Removed parameter dim, as the value can be obtained from
# the shape of S_mat/Y_mat.
def delta_invBFGS(mem, S_mat, Y_mat):
    """Scaling for the inverse BFGS matrix

    Parameters
    ----------
    mem : int
        The step to use.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.

    Returns
    -------
    float
        TODO

    See Also
    --------
    BFGS1_product : TODO
    delta_MSB2 : Alternative function.
    """
    # print('--- in delta_invBFGS:58 ---')
    # print('S_mat[:dim, mem-1] =', S_mat[:dim, mem-1])
    # print('Y_mat[:dim, mem-1] =', Y_mat[:dim, mem-1])
    # print('--- out delta_invBFGS:61 ---')
    return abs(dot(S_mat[:, mem-1], Y_mat[:, mem-1]))\
        / dot(Y_mat[:, mem-1], Y_mat[:, mem-1])


def scaler_wrapper(Scaler, mem, S_mat, Y_mat, alpha):
    """A wrapper for all scaler functions.

    Used to have unified function calls.

    Parameters
    ----------
    Scaler : function
        The scaler function to use.
    mem : int
        The step to use.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.

    Returns
    -------
    float
        TODO

    See Also
    --------
    delta_MSB2, delta_invBFGS
    """
    if Scaler is delta_invBFGS:
        return delta_invBFGS(mem, S_mat, Y_mat)

    if Scaler is delta_MSB2:
        return delta_MSB2(S_mat, Y_mat, alpha)


def BFGS1_product(u_vec, S_mat, Y_mat, scale):
    """An implementation of the BFGS algorithm.

    Parameters
    ----------
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    delta_invBFGS : TODO
    Broyden1_product, Broyden2_product
    """
    STY_mat = dot(S_mat.T, Y_mat)
    D_mat = diag(diag(STY_mat))
    L_mat = tril(STY_mat, -1)

    Di_mat = diag(diag(STY_mat)**(-1))
    R_mat = 1./scale*dot(S_mat.T, S_mat) + dot(L_mat, dot(Di_mat, L_mat.T))
    R_mat = cholesky(R_mat).T

    Dsqrt_mat = diag(diag(STY_mat)**.5)
    Disqrt_mat = diag(diag(STY_mat)**(-.5))
    Phi_mat = c_[Y_mat, (1./scale)*S_mat]
    Gam1_mat = r_[c_[-Dsqrt_mat, dot(Disqrt_mat, L_mat.T)],
                  c_[zeros(D_mat.shape), R_mat]]
    Gam2_mat = r_[c_[Dsqrt_mat, zeros(D_mat.shape)],
                  c_[-dot(L_mat, Disqrt_mat), R_mat.T]]

    v_vec = dot(Phi_mat.T, u_vec)
    v_vec = solve(Gam2_mat, v_vec)
    v_vec = solve(Gam1_mat, v_vec)
    v_vec = (1./scale)*u_vec - dot(Phi_mat, v_vec)

    return v_vec


def invBFGS1_product(u_vec, S_mat, Y_mat, scale):
    """Stable inverse-BFGS matrix product.

    Parameters
    ----------
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    invBroyden1_product, invBroyden2_product
    """
    # Prevent problems with oriented vectors
    U_vec = u_vec.flatten()
    STY_mat = dot(S_mat.T, Y_mat)
    D_mat = diag(diag(STY_mat))
    R_mat = triu(STY_mat + 1e-11*eye(STY_mat.shape[0], STY_mat.shape[1]), 0)
    Rt_mat = R_mat.T

    v1_vec = dot(S_mat.T, U_vec)
    v2_vec = scale * dot(Y_mat.T, U_vec)
    v3_vec = solve(R_mat, v1_vec)
    v3_vec = dot(D_mat + scale*dot(Y_mat.T, Y_mat), v3_vec) - v2_vec
    v3_vec = solve(Rt_mat, v3_vec)
    v2_vec = -solve(R_mat, v1_vec)
    v_vec = scale*U_vec + dot(S_mat, v3_vec) + scale*dot(Y_mat, v2_vec)

    return v_vec


def Broyden1_product(mem, u_vec, S_mat, Y_mat, scale):
    """An implementation of Broyden's method.

    Parameters
    ----------
    mem : int
        TODO
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    Broyden2_product, BFGS1_product
    """
    tmpzw = dot(S_mat[:, mem-1], u_vec) / dot(S_mat[:, mem-1], S_mat[:, mem-1])
    # Ensure, that Wtmp_vec.shape = (x,) and not (x,1). In the latter case
    # we would have to transpose Wtmp_vec in every addition later on to not
    # suddenly get a matrix as a result of the operation.
    Wtmp_vec = u_vec.flatten()
    Ztmp_vec = tmpzw*Y_mat[:, mem-1]

    # PYTHON PORT ANNOTATION
    # Changed the order of the loop for improved readability.
    for j in range(mem-1, 0, -1):
        Wtmp_vec = Wtmp_vec - tmpzw*S_mat[:, j]
        tmpzw = dot(S_mat[:, j-1], Wtmp_vec) / dot(S_mat[:, j-1],
                                                   S_mat[:, j-1])
        Ztmp_vec = Ztmp_vec + tmpzw*Y_mat[:, j-1]

    Wtmp_vec = Wtmp_vec - tmpzw*S_mat[:, 0]
    v_vec = scale*Wtmp_vec + Ztmp_vec

    return v_vec


def invBroyden1_product(u_vec, S_mat, Y_mat, scale, alpha):
    """An implementation of the inverse Broyden's method.

    Parameters
    ----------
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.
    alpha : float
        A regularization parameter.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    invBFGS1_product, invBroyden2_product
    """
    dim = Y_mat.shape[1]
    # Prevent problems with oriented vectors
    U_vec = u_vec.flatten()
    M_mat = -tril(dot(S_mat.T, S_mat), -1)
    v_vec = solve(M_mat + scale*dot(S_mat.T, Y_mat) + alpha*eye(dim, dim),
                  scale*dot(S_mat.T, U_vec))
    v_vec = scale*U_vec - dot(scale*Y_mat - S_mat, v_vec)

    return v_vec


def Broyden2_product(mem, u_vec, S_mat, Y_mat, scale):
    """An implementation of Broyden's method.

    Parameters
    ----------
    mem : int
        How many old steps to consider.
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    Broyden1_product, BFGS1_product
    """
    tmpzw = dot(Y_mat[:, mem-1], u_vec) / dot(Y_mat[:, mem-1], Y_mat[:, mem-1])
    # Ensure, that Wtmp_vec.shape = (x,) and not (x,1). In the latter case
    # we would have to transpose Wtmp_vec in every addition later on to not
    # suddenly get a matrix as a result of the operation.
    Wtmp_vec = u_vec.flatten()
    Ztmp_vec = tmpzw*S_mat[:, mem-1]

    # PYTHON PORT ANNOTATION
    # Changed the order of the loop for improved readability.
    for j in range(mem-1, 0, -1):
        Wtmp_vec = Wtmp_vec - tmpzw*Y_mat[:, j]
        tmpzw = dot(Y_mat[:, j-1], Wtmp_vec) / dot(Y_mat[:, j-1],
                                                   Y_mat[:, j-1])
        Ztmp_vec = Ztmp_vec + tmpzw*S_mat[:, j-1]

    Wtmp_vec = Wtmp_vec - tmpzw*Y_mat[:, 0]
    v_vec = scale*Wtmp_vec + Ztmp_vec

    return v_vec


def invBroyden2_product(u_vec, S_mat, Y_mat, scale, alpha):
    """An implementation of the inverse Broyden's method.

    Parameters
    ----------
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradient differences.
    scale : float
        The initial scaling.
    alpha : float
        A regularization parameter.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    invBFGS1_product, invBroyden1_product
    """
    dim = Y_mat.shape[1]
    # Prevent problems with oriented vectors
    U_vec = u_vec.flatten()
    M_mat = -tril(dot(Y_mat.T, Y_mat), -1)
    v_vec = solve(M_mat + 1./scale*dot(Y_mat.T, S_mat) + alpha*eye(dim, dim),
                  1./scale*dot(Y_mat.T, U_vec))
    v_vec = 1./scale*U_vec - dot(1./scale*S_mat - Y_mat, v_vec)

    return v_vec


def hessian_wrapper(Hessian_product, mem, u_vec, S_mat, Y_mat,
                    scale, alpha):
    """Wrapper for all hessian functions in this module.

    Used to have unified parameters across all function calls.

    Parameters
    ----------
    Hessian_product : function
        The hessian function to use.
    mem : int
        The step to use.
    u_vec : array_like
        The vector to be multiplied.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    scale : float
        The initial scaling.
    alpha : float
        A regularisation parameter.

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    BFGS1_product, invBFGS1_product, Broyden1_product, invBroyden1_product,
    Broyden2_product, invBroyden2_product
    """
    if Hessian_product is BFGS1_product:
        return BFGS1_product(u_vec, S_mat, Y_mat, scale)

    if Hessian_product is invBFGS1_product:
        return invBFGS1_product(u_vec, S_mat, Y_mat, scale)

    if Hessian_product is Broyden1_product:
        return Broyden1_product(mem, u_vec, S_mat, Y_mat, scale)

    if Hessian_product is invBroyden1_product:
        return invBroyden1_product(u_vec, S_mat, Y_mat, scale, alpha)

    if Hessian_product is Broyden2_product:
        return Broyden2_product(mem, u_vec, S_mat, Y_mat, scale)

    if Hessian_product is invBroyden2_product:
        return invBroyden2_product(u_vec, S_mat, Y_mat, scale, alpha)
