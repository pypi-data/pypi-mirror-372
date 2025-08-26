"""Contains all functions that are used to calculate the next step.
"""
from numpy import abs, amax, c_, diag, dot, r_, sum, sqrt, tril, triu, zeros, savez
from numpy.linalg import cholesky, LinAlgError, norm, solve

from .hessian import hessian_wrapper, scaler_wrapper
from .history import history_wrapper


# PYTHON PORT ANNOTATION
# Renamed delinv to scaleinv as del is a keyword in Python.
# Removed parameter dim, as it was not used.
def inv_tGammPhiTPhi_product2(mem, u_vec, S_mat, Y_mat, scaleinv, omega):
    """TODO

    Parameters
    ----------
    mem : int
        TODO
    u_vec : array_like
        TODO
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    scaleinv : float
        The initial scaling.
    omega : float
        TODO

    Returns
    -------
    array_like
        TODO

    See Also
    --------
    TRFBGS1
    """
    # Build the pieces:
    tau = scaleinv + omega
    # PYTHON PORT ANNOTATION
    # Removed all variables for transposed matrices, that were only used once.
    YtY_mat = dot(Y_mat.T, Y_mat)
    St_mat = S_mat.T
    StS_mat = dot(St_mat, S_mat)
    StY_mat = dot(St_mat, Y_mat)
    D_mat = diag(diag(StY_mat))
    Rbar_mat = triu(StY_mat, 0)
    L_mat = tril(StY_mat, -1)
    K_mat = YtY_mat + tau*D_mat
    try:
        K_mat = cholesky(K_mat).T
    except LinAlgError:
        print('Not positive definite')
    Kt_mat = K_mat.T
    E_mat = scaleinv*Rbar_mat - omega*L_mat
    Et_mat = E_mat.T
    B_mat = omega*scaleinv*StS_mat\
            + dot(E_mat, solve(K_mat, solve(Kt_mat, Et_mat)))

    # print('--- in inv_tGammPhiTPhi_product2:29 ---')
    # print('S_mat =\n', S_mat)
    # print('StS_mat =\n', StS_mat)
    # print('B_mat =\n', B_mat)
    # print('--- out inv_tGammPhiTPhi_product2:33 ---')

    try:
        B_mat = cholesky(B_mat).T
    except LinAlgError:
        print('Not positive definite')
    Bt_mat = B_mat.T

    # print('--- in inv_tGammPhiTPhi_product2:34 ---')
    # print('K_mat =\n', K_mat)
    # print('E_Mat =\n', E_mat)
    # print('B_mat =\n', B_mat)
    # print('--- out inv_tGammPhiTPhi_product2:38 ---')

    # Execute inverse multiplication:
    u01_vec = u_vec[0:mem]
    u02_vec = u_vec[mem:2*mem]

    u11_vec = solve(Bt_mat, u01_vec)
    u11_vec = solve(B_mat, u11_vec)

    u21_vec = dot(Et_mat, u11_vec)
    u21_vec = solve(Kt_mat, u21_vec)
    u21_vec = solve(K_mat, u21_vec)

    u12_vec = solve(Kt_mat, u02_vec)
    u12_vec = solve(K_mat, u12_vec)

    u22_vec = dot(E_mat, u12_vec)
    u22_vec = solve(Bt_mat, u22_vec)
    u22_vec = solve(B_mat, u22_vec)

    u32_vec = dot(Et_mat, u22_vec)
    u32_vec = solve(Kt_mat, u32_vec)
    u32_vec = solve(K_mat, u32_vec)

    v_vec = u11_vec - u22_vec
    v_vec = r_[v_vec, u32_vec - u21_vec - u12_vec]

    return v_vec


# PYTHON PORT ANNOTATION
# Renamed del to scale, as del is a keyword in Python.
# Removed parameter dim, as it was not needed.
def TRBFGS1(mem, u_vec, ngrad, S_mat, Y_mat, tr, scale):
    """TODO

    Parameters
    ----------
    mem : int
        How many steps to look back.
    u_vec : array_like
        The negative gradient vector.
    ngrad : float
        The norm of the current gradient.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    tr : float
        The radius of the trust region.
    scale : float
        The initial scaling.

    Returns
    -------
    d_vec : array_like
        The next step.

    See Also
    --------
    Explicit_TR : Calling function.
    inv_tGammPhiTPhi_product2 : Used in this function.
    """
    # PYTHON PORT ANNOTATION
    # Removed temp_mat, if it was only used once before reassignment.
    scaleinv = 1./scale
    Phi_mat = c_[scaleinv*S_mat, Y_mat]
    v0_vec = dot(Phi_mat.T, u_vec)
    # OPT Remove temp_mat
    temp_mat = S_mat.T
    StS_mat = dot(temp_mat, S_mat)
    StY_mat = dot(temp_mat, Y_mat)
    # PYTHON PORT ANNOTATION
    # Replaced spdiags with diag, as the sparsity of the matrix was
    # never used.
    # TODO(benedikt) Check that sparsity is never used.
    D_mat = diag(diag(StY_mat))
    YtY_mat = dot(Y_mat.T, Y_mat)
    temp_mat = scaleinv*StY_mat
    Psi_mat = r_[c_[scaleinv**2*StS_mat, temp_mat], c_[temp_mat.T, YtY_mat]]
    temp_mat = tril(StY_mat, -1)
    Gamma_mat = r_[c_[scaleinv*StS_mat, temp_mat], c_[temp_mat.T, -D_mat]]

    # savez('py_vars.npz', Phi_mat=Phi_mat, v0_vec=v0_vec,
    #       StS_mat=StS_mat, StY_mat=StY_mat, D_mat=D_mat,
    #       YtY_mat=YtY_mat, Psi_mat=Psi_mat, Gamma_mat=Gamma_mat,
    #       u_vec=u_vec)
    # print('--- in TRBFGS1:86 ---')
    # print('Psi_mat =\n', Psi_mat)
    # print('Gamma_mat =\n', Gamma_mat)
    # print('--- out TRBFGS1:88 ---')

    Maxit_TRsub = 12
    # Maxit_TRsub = 0
    Tol_TRsub = 1e-10
    Iter_TRsub = 0
    dmu = 1.
    mu_max = ngrad/tr
    mu0 = mu_max/2.
    while Iter_TRsub <= Maxit_TRsub and abs(dmu) > Tol_TRsub:
        Iter_TRsub += 1
        tau = scaleinv + mu0
        v1_vec = inv_tGammPhiTPhi_product2(mem, v0_vec, S_mat, Y_mat,
                                           scaleinv, mu0)
        v2_vec = dot(Gamma_mat, v1_vec)
        v2_vec = inv_tGammPhiTPhi_product2(mem, v2_vec, S_mat, Y_mat,
                                           scaleinv, mu0)

        # print('--- in TRBFGS1:106 ---')
        # print('Iter_TRsub =', Iter_TRsub)
        # print('v1_vec =\n', v1_vec)
        # print('v2_vec =\nf', v2_vec)
        # print('--- out TRBFGS1:109 ---')

        temp = dot(v0_vec, v1_vec)
        sigma = dot(v1_vec, dot(Psi_mat, v1_vec)) + 2*temp + ngrad**2
        # savez('py_vars.npz', v1_vec=v1_vec, v2_vec=v2_vec,
        #       v0_vec=v0_vec, S_mat=S_mat, Y_mat=Y_mat, scaleinv=scaleinv,
        #       mu0=mu0, sigma=sigma)
        if sigma < 0 or Iter_TRsub == Maxit_TRsub:
            sigma = 0.

        # PYTHON PORT ANNOTATION
        # Removed sqrtsigma, as it was only used once.
        temp = sqrt(sigma) - tau*tr
        Delta = sigma + tau*(dot(v1_vec, dot(Psi_mat, v2_vec))
                             + dot(v0_vec, v2_vec))
        dmu = (sigma/Delta)*(temp/tr)
        mu1 = mu0 + dmu
        if mu1 >= 0:
            if mu1 >= mu_max:
                if mu1 == mu_max:
                    print('Upper bound on mu is wrong.')
                else:
                    mu0 = mu_max
            else:
                mu0 = mu1
        else:
            mu0 = .2*mu0
        # savez('py_vars.npz', temp=temp, Delta=Delta, dmu=dmu, mu1=mu1, mu0=mu0)

    # savez('py_vars.npz', dmu=dmu, mu0=mu0, mu_max=mu_max,
    #       v1_vec=v1_vec, tau=tau)
    temp = dot(Phi_mat, v1_vec)
    d_vec = (u_vec + temp)/tau

    return d_vec


# PYTHON PORT ANNOTATION
# Renamed iter to it, as iter is a keyword in Python.
def Step_generator(Step_finder, Scaler, History, Hessian_product,
                   invHessian_product, it, mem, c, beta, gamma, x_mat,
                   gradf_mat, ngradf_vec, stepsize_vec, tr, trstep,
                   alpha_0, verbose):
    """Calculates the direction of the next step and it's inital length.

    Parameters
    ----------
    Step_finder : function
        TODO
    Scaler : function
        TODO
    History : function
        TODO
    Hessian_product : function
        TODO
    invHessian_product : function
        TODO
    it : int
        The current iteration.
    mem : int
        TODO
    c : float
        TODO
    beta : float
        TODO
    gamma : float
        TODO
    x_mat : array_like
        TODO
    gradf_mat : array_like
        TODO
    ngradf_vec : array_like
        TODO
    stepsize_vec : array_like
        TODO
    tr : float
        TODO
    trstep : int
        TODO
    alpha_0 : float
        TODO
    verbose : bool
        TODO

    Returns
    -------
    d_vec : array_like
        The next step.
    """
    dim = x_mat.shape[0]
    ######################################################################
    # choose search direction and length:
    ######################################################################
    if mem > 0:
        S_mat = zeros((dim, mem))
        Y_mat = zeros((dim, mem))
        # print('--- in Step_generator:23 ---')
        # print('x_mat[:, -mem-2:-1] =', x_mat[:, -mem-2:-1])
        # print('gradf_mat[:, -mem-2:-1] =',
        #       gradf_mat[:, -mem-2:-1])
        # print('--- out Step_generator:27 ---')
        S_mat, Y_mat = history_wrapper(History, mem+1,
                                       x_mat[:, -mem-2:-1],
                                       gradf_mat[:, -mem-2:-1])
        delta = scaler_wrapper(Scaler, mem, S_mat, Y_mat, alpha_0)
        alpha = alpha_0
        # print('--- in Step_generator:33 ---')
        # print('S_mat =', S_mat)
        # print('Y_mat =', Y_mat)
        # print('delta =', delta)
        # print('--- out Step_generator:37 ---')
        d_vec = step_wrapper(Step_finder, Hessian_product,
                             invHessian_product, mem,
                             gradf_mat[:, -2],
                             ngradf_vec[it], S_mat, Y_mat, tr,
                             delta, alpha, verbose)
        stepsize_vec[it] = norm(d_vec)
        # savez('py_vars.npz', gradf_mat=gradf_mat, ngradf_vec=ngradf_vec,
        #       tr=tr, alpha=alpha)
    else:
        # steepest descent direction
        delta = 0
        alpha = alpha_0
        # if we get to this option, the step MUST have been accepted
        # and iter updated
        d_vec = -stepsize_vec[it]*gradf_mat[:, -2]/ngradf_vec[it]

    if abs(stepsize_vec[it] - tr) < 1e-11:
        trstep += 1

    DDf = dot(gradf_mat[:, -2], d_vec)
    while DDf > 0:
        if verbose:
            print('The Step generator yields a direction of nondescent. ')

        # shrink memory and try again
        if mem > 2:
            S_mat = S_mat[:, 1:mem]
            Y_mat = Y_mat[:, 1:mem]
            delta = scaler_wrapper(Scaler, mem-1, S_mat, Y_mat, alpha_0)
            alpha = alpha_0
            d_vec = step_wrapper(Step_finder, Hessian_product,
                                 invHessian_product, mem-1,
                                 gradf_mat[:, -2],
                                 ngradf_vec[it], S_mat, Y_mat,
                                 tr, delta, alpha)
        else:
            # steepest descent
            d_vec = -gamma*stepsize_vec[it]*gradf_mat[:, -2]\
                    / ngradf_vec[it]

        mem -= 1
        DDf = dot(gradf_mat[:, -2], d_vec)

    ##################################################
    # end choose search direction and length:
    ##################################################
    cDDf = c*DDf
    bDDf = beta*DDf

    return delta, alpha, d_vec, stepsize_vec, trstep, DDf, cDDf, bDDf, mem


# PYTHON PORT ANNOTATION
# Renamed iter to it as iter is a keyword in Python.
def Step_length_update(History, Hessian_product, update_conditions,
                       mem, it, x_mat, f_vec,
                       gradf_mat, d_vec, mu_vec, stepsize_vec, tr,
                       delta, alpha, eta1, eta2, eta3, cDDf, DDfnew,
                       bDDf, orthog_TOL, lower_step_bound, gamma):
    """Trust region adjustment routine.

    Parameters
    ----------
    History : function
        TODO
    Hessian_product : function
        TODO
    update_conditions : str
        TODO
    mem : int
        TODO
    it : int
        The current iteration.
    x_mat : array_like
        TODO
    f_vec : array_like
        TODO
    gradf_mat : array_like
        TODO
    d_vec : array_like
        TODO
    mu_vec : array_like
        TODO
    stepsize_vec : array_like
        TODO
    tr : float
        TODO
    delta : float
        TODO
    alpha : float
        TODO
    eta1 : float
        TODO
    eta2 : float
        TODO
    eta3 : float
        TODO
    cDDf : float
        TODO
    DDfnew : float
        TODO
    bDDf : float
        TODO
    orthog_TOL : float
        TODO
    lower_step_bound : float
        TODO
    gamma : float
        TODO

    Returns
    -------
    tr : float
        TODO
    mu_vec : array_like
        TODO
    cDDf : float
        TODO
    lower_step_bound : float
        TODO
    d_vec : array_like
        TODO
    stepsize_vec : array_like
        TODO
    accept : int
        TODO
    """
    # print('--- in Step_length_update:86 ---')
    # print('update_conditions =', update_conditions)
    # print('mem =', mem)
    # print('--- out Step_length_update:89 ---')
    if update_conditions == 'Exact':
        ##################################################
        # exact line search via bisection
        ##################################################
        if mu_vec[it] == 0:
            tr = 1e+15
            lower_step_bound = 0
            mu_vec[it] = 1

        min_d = lower_step_bound
        max_d = tr
        nd = stepsize_vec[it]
        if abs(DDfnew)/stepsize_vec[it] <= orthog_TOL:
            accept = 1
        else:
            accept = -2
            if f_vec[it+1] <= f_vec[it] and DDfnew/nd < -orthog_TOL:
                # step too short:
                if abs(nd-max_d)/(max_d-min_d) < 1e-2:
                    max_d = 1e+7*max_d
                    tr = max_d
                    d_vec = 2*d_vec
                else:
                    # increase step length by one half the interval to
                    # the outer bound
                    d_vec = min(nd+max_d/2., 10.*nd)*d_vec/nd
                min_d = nd
            elif f_vec[it+1] <= f_vec[it] and DDfnew/nd > orthog_TOL:
                # step too long, but not by too much:
                # decrease step length by one half the interval to the
                # inner bound
                d_vec = (nd+min_d)/2.*(d_vec/nd)
                max_d = nd
                tr = max_d
            elif f_vec[it+1] > f_vec[it]:
                # step too long, by a lot:
                # decrease step length by one half the current steplength
                max_d = nd
                tr = max_d
                d_vec = .5*(min_d+nd)*(d_vec/nd)

        lower_step_bound = min_d
        stepsize_vec[it] = norm(d_vec)

    # do backtracking linesearch/ adjust the trust region
    else:
        if mem > 0:
            S_mat, Y_mat = history_wrapper(History, mem+1,
                                           x_mat[:, -mem-2:-1],
                                           gradf_mat[:, -mem-2:-1])

        ##################################################
        # Adjust trust region:
        ##################################################
        # actual change/predicted change
        # look-back - this is a type of nonmonotone trust region adjustment
        p = max(mem-1, 1)
        pind = max(it-p, 0)
        # PYTHON PORT ANNOTATION
        # Added initialisation of pred here, so that it always exists.
        pred = 0.
        if mem > 0:
            pred = dot(gradf_mat[:, -2], d_vec) \
                   + .5*dot(d_vec, hessian_wrapper(Hessian_product, mem,
                                                   d_vec, S_mat, Y_mat, delta,
                                                   alpha))
            actual = f_vec[it+1] - f_vec[it]
            mu_vec[it] = actual/pred
            if abs(pred-actual)/abs(pred) > 1e+5:
                print('Warning: step length may be too small -- resimitpo results might be at numerical accuracy.')
                print('Try increasing your step length tolerance.')
        else:
            mu_vec[it] = (f_vec[it+1]-f_vec[it])\
                               / dot(gradf_mat[:, -2], d_vec)

        # savez('py_vars.npz', mem=mem, mu_vec=mu_vec, pred=pred,
        #       stepsize_vec=stepsize_vec, tr=tr, pind=pind)
        if mem > 0:
            if mu_vec[it] <= 0 or pred > 0:
                tr = min(.1*stepsize_vec[it-1], .1*tr)
                accept = -1
            elif sum(mu_vec[pind+1:it+1])/(it-pind) >= eta1:
                tr = min(5.*tr, 1e+15)
                accept = 1
            elif sum(mu_vec[pind+1:it+1])/(it-pind) >= eta2:
                tr = min(2.*tr, 1e+15)
                accept = 1
            elif sum(mu_vec[pind+1:it+1])/(it-pind) > eta3:
                # Nocedal & Wright would suggest leaving tr the same
                tr = 1.2*tr
                accept = 1
            else:
                tr = min(stepsize_vec[it], .25*tr)
                if f_vec[it+1] <= amax(f_vec[max(0, it-p):it+1])\
                   + cDDf and DDfnew >= bDDf:
                    accept = 1
                elif f_vec[it+1] <= amax(f_vec[max(0, it-p):it+1])\
                     and stepsize_vec[it] < 2.*stepsize_vec[it-1]:
                    # still got decrease, so will keep the
                    # information, but not advance the point
                    accept = 0
                else:
                    # no decrease and stepsize might be too small,
                    # shrink memory and don't keep info
                    accept = -1
        else:
            max_d = tr
            nd = stepsize_vec[it]
            if lower_step_bound >= max_d:
                min_d = 0
            else:
                min_d = lower_step_bound
            # weakness of this method.  In general don't know what max_d
            # should be, and if you underestimate the routine will stagnate.
            if abs(nd-max_d)/(max_d-min_d) < 1e-2:
                max_d *= 1e+7
                tr = max_d

            ##################################################
            # nonmonotone bisection line search
            ##################################################
            p = max(mem, 1)
            # TODO(benedikt) DELETE ME
            # print('--- start Step_length_update:203 ---')
            # print('f_vec =', f_vec)
            # print('p =', p)
            # print('it =', it)
            # print('f_vec[max(0, it-p):it] =', f_vec[max(0, it-p):it])
            # print('--- end Step_length_update:208 ---')
            if f_vec[it+1] <= amax(f_vec[max(0, it-p):it+1])+cDDf\
               and DDfnew >= bDDf:
                # Wolfe conditions satisfied, do not change step.
                accept = 1
            else:
                accept = -2
                if f_vec[it+1] <= amax(f_vec[max(0, it-p):it+1])+cDDf\
                   and DDfnew < bDDf:
                    # probably underestimating the upper bound
                    if (max_d-min_d)/max_d <= 1e-2:
                        max_d *= 10.
                        tr = max_d
                    # step too short:
                    # increase step length to the outer bound
                    d_vec = min(.1*nd + .9*max_d, 100.*nd)*d_vec/nd
                    min_d = nd
                    accept = 1
                elif f_vec[it+1] <= amax(f_vec[max(0, it-p):it+1])\
                     and DDfnew >= bDDf:
                    # step too long, but not by too much:
                    # decrease step length by one half the
                    # interval to the inner bound
                    d_vec = (nd+min_d)/2.*(d_vec/nd)
                    max_d = nd
                    tr = max_d
                elif f_vec[it+1] >= f_vec[it]:
                    # step too long, by a lot:
                    # decrease step length by one half the current steplength
                    max_d = nd
                    d_vec = .5*(min_d+nd)*(d_vec/nd)
                    tr = max_d
                    cDDf *= gamma
            lower_step_bound = min_d
            stepsize_vec[it] = norm(d_vec)
        ##################################################
        # end trust region adjust
        ##################################################

    # savez('py_vars.npz', tr=tr, mu_vec=mu_vec, cDDf=cDDf,
    #       lower_step_bound=lower_step_bound, d_vec=d_vec,
    #       stepsize_vec=stepsize_vec, accept=accept)

    return tr, mu_vec, cDDf, lower_step_bound, d_vec, stepsize_vec, accept


# PYTHON PORT ANNOTATION
# Renamed del to scale, as del is a keyword in Python.
def Dogleg_QN(Hessian_product, invHessian_product, mem, grad_vec,
              ngrad, S_mat, Y_mat, tr, scale, alpha):
    """Stable Quasi-Newton Dogleg.

    Dogleg subroutine for line search methods.

    Parameters
    ----------
    Hessian_product : function
        The dogleg method.
    invHessian_product : function
        The quasi newton method.
    mem : int
        How far to look back.
    grad_vec : array_like
        The current gradient.
    ngrad : float
        The norm of the current gradient.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matix of gradients.
    tr : float
        The radius of the trust region.
    scale : float
        The initial scaling.
    alpha : float
        A regularisation parameter.

    Returns
    -------
    d_vec : array_like
        The next step. Equals the step calculated with the quasi
    newton method, if that step already is within the trust region.

    Notes
    -----
    Solves the following problem:
    """
    dn = hessian_wrapper(invHessian_product, mem, -grad_vec,
                         S_mat, Y_mat, scale, alpha)
    # print('--- in Dogleg_QN:22 ---')
    # print('dn =', dn)
    # print('--- out Dogleg_QN:24 ---')
    if norm(dn) <= tr:   # to turn on  set <= 1e+15
        ddl = dn
    else:
        # initialization
        u = -grad_vec/ngrad
        v = hessian_wrapper(Hessian_product, mem, u, S_mat,
                            Y_mat, scale, alpha)
        w = dot(u, v)
        # predicted change at constrained solution
        b = -tr*ngrad + .5*(tr**2)*w
        # t_star solves min{-t ||grad_f||
        # + 1/2*t^2* grad_f'*H*grad_f/||grad_f||^2}
        # => t_star = ||grad_f||^3/grad_f'*H*grad_f
        # from first order necessary conditions for optimality
        t_star = ngrad/w
        if t_star < 0 or t_star > tr:
            if b > 0:
                t = 0
            else:
                t = tr
        else:
            # predicted change at unconstrained solution
            c = -.5*(ngrad**2)/w
            # only want the t that solves
            # min{-t ||grad_f|| + 1/2*t^2* grad_f'*H*grad_f/||grad_f||^2}
            # on [0, tr]
            if c < 0 or b < 0:
                if c < b:
                    t = t_star
                else:
                    t = tr
            else:
                t = 0

        dsd = t*u

        # PYTHON PORT ANNOTATION
        # Replaced norm(dsd-dn)**2 with dot(dsd-dn, dsd-dn).
        # TODO(benedikt) add in extra variables for dsd-dn and dot(dsd-dn, dsd)
        tmp = dot(dsd-dn, dsd-dn)
        disc = dot(dsd-dn, dsd)**2 + tmp*(tr**2 - dot(dsd, dsd))
        lamb = max((sqrt(disc) - dot(dn-dsd, dsd))/tmp, 0)
        ddl = lamb*dn + (1-lamb)*dsd

    return ddl


# PYTHON PORT ANNOTATION
# Renamed del to scale, as del is a keyword in Python.
def Explicit_TR(invHessian_product, mem, grad_vec, ngrad,
                S_mat, Y_mat, tr, scale, alpha, verbose):
    """Stable Explicit Trust Region.

    Stable Explicit Trust Region for Symmetric PSD matrix secant methods.

    Parameters
    ----------
    invHessian_product : function
        The quasi newton method.
    mem : int
        How many steps to look back.
    grad_vec : array_like
        The current gradient.
    ngrad : float
        The norm of the current gradient.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    tr : float
        The radius of the trust region.
    scale : float
        The initial scaling.
    alpha : float
        A regularisation parameter.
    verbose : bool
        If additional output should be printed.

    Returns
    -------
    d_vec : array_like
        The next step.

    See Also
    --------
    TRBFGS1, Dogleg_QN
    """
    TRsub = TRBFGS1
    dn_vec = hessian_wrapper(invHessian_product, mem, -grad_vec,
                             S_mat, Y_mat, scale, alpha)
    # print('--- in Explicit_TR:84 ---')
    # print('dn_vec =\n', dn_vec)
    # print('--- out Explicit_TR:86 ---')
    if norm(dn_vec) <= tr:   # to turn on  set <= 1e+15
        d_vec = dn_vec
    else:
        if verbose:
            print('in trust region subproblem')

        d_vec = TRsub(mem, -grad_vec, ngrad, S_mat, Y_mat, tr, scale)

    # savez('py_vars.npz', dn_vec=dn_vec, d_vec=d_vec)
    return d_vec


# PYTHON PORT ANNOTATION
# Renamed del to scale, as del is a keyword in Python.
def step_wrapper(step_finder, Hessian_product, invHessian_product, mem,
                 grad_vec, ngrad, S_mat, Y_mat, tr, scale, alpha,
                 verbose):
    """A wrapper for all step finding functions.

    The wrapper provides a unified function call for all step finders.

    Parameters
    ----------
    step_finder : function
        The step finder to use (Dogleg_QN, Explicit_TR).
    Hessian_product : function
        The dogleg method for Dogleg_QN.
    invHessian_product : function
        The quasi newton method.
    mem : int
        How many steps to look back.
    grad_vec : array_like
        The current gradient.
    ngrad : float
        The norm of the current gradient.
    S_mat : array_like
        The matrix of steps.
    Y_mat : array_like
        The matrix of gradients.
    tr : float
        The radius of the trust region.
    scale : float
        The initial scaling.
    alpha : float
        A regularisation parameter.
    verbose : bool
        If additional output should be printed.

    Returns
    -------
    d_vec - array_like
        The next step as calculated by the `step_finder`.

    See Also
    --------
    Dogleg_QN, Explicit_TR
    """
    if step_finder is Explicit_TR:
        return Explicit_TR(invHessian_product, mem, grad_vec, ngrad,
                           S_mat, Y_mat, tr, scale, alpha, verbose)

    if step_finder is Dogleg_QN:
        return Dogleg_QN(Hessian_product, invHessian_product, mem,
                         grad_vec, ngrad, S_mat, Y_mat, tr, scale, alpha)
