"""Example of a driver for Resimitpo.

To create a resimitpo driver for your own project, copy this file and
add in your function and options.
"""
import matplotlib.pyplot as plt
from numpy import abs, amax, array, load, zeros
from numpy.linalg import norm

from resimitpo import Resimitpo, BFGS1_product, Broyden1_product,\
    Broyden2_product, Dogleg_QN, Explicit_TR, cdSY_mat, fdSY_mat


def objective(x):
    """Example objective (Engvall function).

    Replace this code with your actual function.

    Parameters
    ----------
    x : array_like
        The point to evaluate the function at (2 dimensional).

    Returns
    -------
    f : float
        The function value at `x`.
    Df : array_like
        The gradient vector of ``f`` at ``x``.

    Notes
    -----
    In your implementation you may use any number of parameters and
    return values. But resimitpo will always need the function value
    and the gradient vector.
    """
    f = x[0]**4 + x[1]**4 + 2*x[0]**2*x[1]**2 - 4*x[0] + 3
    Df = zeros(2)
    Df[0] = 4*x[0]**3 + 4*x[0]*x[1]**2 - 4
    Df[1] = 4*x[1]**3 + 4*x[0]**2*x[1]

    return f, Df


def plot_result():
    """Example of a custom plot function for the result.

    Replace this code with your actual plotting routine.
    """
    pass


def driver():
    # You can either implement your function in the objective function
    # provided above, or import your function from a different module
    # and set it here.
    Objective = objective

    # ========== SAMSARA ==========
    resimitpo = Resimitpo()

    # --- OPTIONS ---
    params = {}
    # Extra output from resimitpo.
    params['verbose'] = True
    # A regularisation parameter.
    params['alpha_0'] = 5e-12
    # ...
    params['gamma'] = .5
    # ...
    params['c'] = .01
    # ...
    params['beta'] = .9999999
    # ...
    params['eta1'] = .995
    # ...
    params['eta2'] = .8
    # ...
    params['eta3'] = .25
    # The maximum steps to look back. Must be an integer.
    params['maxmem'] = 8
    # The initial radius of the trust region.
    params['tr'] = 1e+15

    tols = {}
    # Gradient norm tolerance
    # This is used as a stopping criteria for SAMSARA. It must be a
    # real number greater than zero.
    tols['ngrad_TOL'] = 1e-6
    # Step size tolerance
    # This is used as a stopping criteria for SAMSARA. It must be a
    # real number greater than zero.
    tols['step_TOL'] = 1e-12
    # Maximum number of iterations
    # This is used as a stopping criteria for SAMSARA. It must be
    # an integer greater than zero.
    tols['Maxit'] = 1000

    opts = {}
    # Hessian method
    # Quasi-Newton methods for estimation of the function's Hessian.
    # Broyden implementations use Dogleg_QN lin search methods
    # while BFGS implementations use Explicit_TR.
    # Methods available:
    #     - BFGS1_product
    #     - Broyden1_product
    #     - Broyden2_product
    opts['QN_method'] = BFGS1_product
    # Step finder
    # Optional: Default is Dogleg_QN
    # Methods available:
    #     - Dogleg_QN
    #     - Explicit_TR
    opts['Step_finder'] = Explicit_TR
    # History
    # Ordering methods for S, Y matrices in limited memory application.
    # Finite difference ordering, fdSY_mat, is recommended for Broyden
    # implementations. For BFGS implementations, use conjugate
    # direction ordering, cdSY_mat.
    opts['History'] = cdSY_mat
    # Trust Region Adjust
    # Select the method for adjustment of the trust region in optimazation.
    opts['update_conditions'] = 'Trust Region'
    # Initial Step Scaler
    # The norm of the initial step taken in the Cauchy direction.
    # This multiplied against the normalized gradient to yield the
    # initial direction vector in order to generate the first step
    # taken by SAMSARA.
    # Assign a value of 0.0D0 to use the default value which is the
    # minimum of 1D-1 or the norm(1d-1*gradient).
    opts['initial_step'] = 1e+5*tols['step_TOL']

    resimitpo.load_options(params, tols, opts)

    # ========== STARTING VALUES ==========
    # The starting vector. Set it to an appropriate value.
    xold_vec = array([.5, 2.])
    # The starting function value and gradient vector.
    fold, gradfold_vec = Objective(xold_vec)

    # The next point.
    xnew_vec = None
    # The next function value.
    fnew = None
    # The next gradient vector.
    gradfnew_vec = None
    # Keep at this value, so that the main loop executes at least once.
    stepsize = 999.
    # Keep at this value, so that the main loop executes at least once.
    ngradfnew = 999.

    # ========== MAIN LOOP ==========
    # --- Tolerances ---
    # The lower bound for the gradient vector norm.
    ngrad_TOL = 2e-14
    # The lower bound for the stepsize.
    step_TOL = 2e-17
    # The maximum number of iterations.
    Maxit = 500
    # Number of current iterations
    it = 0

    while it < Maxit and ngradfnew > ngrad_TOL and stepsize > step_TOL:
        xnew_vec, xold_vec, fold, gradfold_vec, stepsize =\
            resimitpo.run(xold_vec, xnew_vec, fold, fnew, gradfold_vec,
                        gradfnew_vec)
        it += 1
        fnew, gradfnew_vec = Objective(xnew_vec)
        ngradfnew = norm(gradfnew_vec)

    if stepsize <= step_TOL:
        print('Algorithm stagnated:  stepsize tolerance violated.')
    if ngradfnew <= ngrad_TOL:
        print('Algorithm stagnated:  gradient norm tolerance violated.')
    if it >= Maxit:
        print('Algorithm exceeded:  maximum step count violated.')

    # TODO(benedikt) Rework from here
    # You can save some of the values of resimitpo.
    # resimitpo.save()

    # You can now plot your results.
    # plot_result()

    # Return the optimal values.
    return xnew_vec, fnew


# Entry point into the driver.
if __name__ == '__main__':
    driver()
