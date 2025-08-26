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
"""Contains the Resimitpo class and some helper functions.

Helper
======

.. autofunction:: resimitpo.resimitpo.is_empty
.. autofunction:: resimitpo.resimitpo.Normsqresid

Resimitpo
=======

This is the main object the user will interact with.

.. autoclass:: resimitpo.resimitpo.Resimitpo
   :members:
   :private-members:
   :special-members: __init__
"""
from numpy import arange, c_, dot, load, ndarray, ones, savez, zeros
from numpy.linalg import norm
import matplotlib.pyplot as plt

from .hessian import BFGS1_product, invBFGS1_product,\
    Broyden1_product, invBroyden1_product, Broyden2_product,\
    invBroyden2_product, hessian_wrapper, delta_MSB2,\
    delta_invBFGS, scaler_wrapper
from .history import fdSY_mat, cdSY_mat, history_wrapper
from .memory import Memory_update
from .step_finder import Dogleg_QN, Explicit_TR, Step_length_update,\
    Step_generator


def is_empty(x):
    """Checks if a variable holds any information.

    Determines if `x` is `None` or an empty array.

    This function is used to check whether new function and gradient
    values have been given to Resimitpo.  This function exists because
    of the `isemtpy` function in MATLAB, that is being used in the
    MATLAB implementation of Resimitpo.

    Parameters
    ----------
    x
        The variable to be checked.

    Returns
    -------
    bool
        `True` if `x` is either `None` or an empty array. `False` otherwise.

    """
    if x is None:
        return True
    # ndarrays of scalars have a '__len__' attribute, but no len() function.
    if isinstance(x, ndarray):
        if x.size == 0:
            return True
    elif hasattr(x, '__len__') and len(x) == 0:
        return True
    return False


# PYTHON PORT ANNOTATION
# Removed dim and maxmem from parameter list, as they can be obtained by
# reading the dimensions of x_mat.
def Normsqresid(Scaler, History, Hessian_product, HessianT_product,
                mem, spsd, x_mat, gradf_mat,
                gradfnew_vec, alpha_0):
    """Computes the normsquared residual of the gradient or otherwise
    vector-values function.

    Parameters
    ----------
    Scaler : function
        TODO
    History : function
        TODO
    Hessian_product : function
        TODO
    HessianT_product : function
        TODO
    mem : int
        TODO
    spsd : int
        TODO
    x_mat : array_like
        TODO
    gradf_mat : array_like
        TODO
    gradfnew_vec : array_like
        TODO
    alpha_0 : float
        TODO

    Returns
    -------
    f0 : float
        TODO
    gradf0_vec : array_like
        TODO

    See Also
    --------
    delta_invBFGS, delta_MSB2, cdSY_mat, fdSY_mat, BFGS1_product,
    invBFGS1_product, Broyden1_product, invBroyden1_product,
    Broyden2_product, invBroyden2_product
    """
    dim = x_mat.shape[0]
    ######################################################################
    # compute the norm-squared residual
    ######################################################################
    f0 = .5*dot(gradfnew_vec, gradfnew_vec)

    ######################################################################
    # approximate the gradient of the norm-squared residual
    ######################################################################
    # PYTHON PORT ANNOTATION
    # In all used test problems (Burke, JWST, Rosenbrock) this code
    # was never executed.
    if mem > 0:
        S_mat = zeros((dim, mem))
        Y_mat = zeros((dim, mem))
        S_mat, Y_mat = history_wrapper(mem+1, x_mat[:, -mem-1:-1],
                                       gradf_mat[:, -mem-1:-1])
        delta = scaler_wrapper(Scaler, mem, S_mat, Y_mat, alpha_0)
        alpha = alpha_0
        if spsd >= 0:
            gradf0_vec = gradf_mat[:, -1]
        else:
            gradf0_vec = hessian_wrapper(HessianT_product, mem,
                                         gradf_mat[:, -1], S_mat,
                                         Y_mat, delta, alpha)
            # which means I have to write a butt-load of
            # Hessian_transpose products.
    else:
        # no information
        gradf0_vec = gradfnew_vec.copy()

    return f0, gradf0_vec


class Resimitpo():
    """TODO
    """
    def __init__(self, verbose=False, alpha_0=5e-9, gamma=.5, c=.01,
                 beta=.99, eta1=.995, eta2=.8, eta3=.05, maxmem=9,
                 tr=1e+15, ngrad_TOL=1e-6, step_TOL=1e-14, Maxit=500,
                 orthog_TOL=1e-6, QN_method=BFGS1_product,
                 Step_finder=None, History=cdSY_mat,
                 update_conditions='Trust Region', initial_step=1e-9):
        """Sets default values.

        Parameters
        ----------
        verbose : bool, optional
            Turn additional output on or off. Default: False
        alpha_0 : float, optional
            TODO Default: 5e-9
        gamma : float, optional
            TODO Default: .5
        c : float, optional
            TODO Default: .01
        beta : float, optional
            TODO Default: .99
        eta1 : float, optional
            TODO Default: .995
        eta2 : float, optional
            TODO Default: .8
        eta3 : float, optional
            TODO Default: .05
        maxmem : int, optional
            The maximum steps to look back. Default: 9
        tr : float, optional
            The initial radius of the trust region. Default: 1e+15
        ngrad_TOL : float, optional
            The gradient norm tolerance. This is used as a stopping
            criteria for Resimitpo. Must be positive. Default: 1e-6
        step_TOL : float, optional
            The step size tolerance. This is used as a stopping
            criteria for Resimitpo. Must be positive. Default: 1e-14
        Maxit : int, optional
            The maximum number of iterations. This is used as a stopping
            criteria for Resimitpo. Must be positive. Default: 500
        QN_method : function, optional
            Quasi-Newton method for estimation of the function's
            Hessian. Broyden implementations use
            :func:`resimitpo.step_finder.Dogleg_QN` lin search methods while
            BFGS implementations use
            :func:`resimitpo.step_finder.Explicit_TR`.
            Methods available are:

               * :func:`resimitpo.hessian.BFGS1_product`
               * :func:`resimitpo.hessian.Broyden1_product`
               * :func:`resimitpo.hessian.Broyden2_product`

            Default: :func:`resimitpo.hessian.BFGS1_product`
        Step_finder : function, optional
            The step finder. Available methods are:

               * :func:`resimitpo.step_finder.Dogleg_QN`
               * :func:`resimitpo.step_finder.Explicit_TR`

            If None, the step finder will be set depending on the
            `QN_method`. Default: None
        History : function, optional
            Ordering method for S, Y matrices in limited memory
            application. Finite difference ordering,
            :func:`resimitpo.history.fdSY_mat`, is recommended for
            Broyden implementations. For BFGS implementations, use
            conjugate direction ordering,
            :func:`resimitpo.history.cdSY_mat`. Default:
            :func:`resimitpo.history.cdSY_mat`
        update_conditions : str, optional
            Select the method for adjustment of the trust region in
            optimazation. Default: 'Trust Region'
        initial_step : float, optional
            The norm of the inital step taken in the Cauchy
            direction. This multiplied against the normailzed gradient
            to yield the initial direction vector in order to generate
            the first step taken by Resimitpo.

            Assign a value of 0 to use the default value which is the
            minimum of 1e-1 or the norm(1d-1*gradient). Default: 1e-9

        """
        # Declare Parameters
        self.x0_vec = None
        self.xnew_vec = None
        self.f0 = None
        self.fnew = None
        self.gradf0_vec = None
        self.gradfnew_vec = None

        # Set options
        self.verbose = verbose
        self.alpha_0 = alpha_0
        self.gamma = gamma
        self.c = c
        self.beta = beta
        self.eta1 = eta1
        self.eta2 = eta2
        self.eta3 = eta3
        self.maxmem = maxmem
        self.tr = tr
        self.ngrad_TOL = ngrad_TOL
        self.step_TOL = step_TOL
        self.Maxit = Maxit
        self.orthog_TOL = orthog_TOL
        self.QN_method = QN_method
        self.Step_finder = Step_finder
        self.History = History
        self.update_conditions = update_conditions
        self.initial_step = initial_step

        self.__validate_options()
        self.__set_methods()

        # Controls if `__first_step` is called in `run` or not.
        # Will be set to `True` in `run` after the first iteration.
        self.hist = False

    def __validate_options(self):
        """Validates the set parameters.

        Raises
        ------
        ValueError
            If `step_TOL` is not positive.
        """
        if not (0 < self.c < 1):
            print('The slope modification parameter c in the\
            backtracking subroutine is not in (0,1).')
            print('Setting c to the default, c=0.001.')
            self.c = .001
        if not (0 < self.beta < 1):
            print('The slope modification parameter beta in the\
            backtracking subroutine is not in (0,1).')
            print('Setting beta to the default, beta=0.99.')
            self.beta = .99
        if not (0 < self.gamma < 1):
            print('The backtracking parameter gamma is not in (0,1).')
            print('Setting gamma to the default, gamma=0.5.')
            self.gamma = .5
        if not (self.eta1 > self.eta2 and self.eta1 < 1):
            print('The trust region parameter eta1 is not in (eta2,1).')
            print('Setting to the default, eta1=0.995.')
            self.eta1 = .995
        if not (self.eta2 > self.eta3 and self.eta2 < self.eta1):
            print('The trust region parameter eta2 is not in (eta3,eta1).')
            print('Setting to the default, eta2=0.8.')
            self.eta2 = .8
        if not (self.eta3 > 0 and self.eta3 < self.eta2):
            print('The trust region parameter eta3 is not in (0,eta2).')
            print('Setting to the default, eta3=0.05.')
            self.eta3 = .05
        if self.alpha_0 <= 1e-15:
            print('WARNING: the regularization parameter is probably\
            too small.')
            print('We recommended choosing alpha_0>= 5e-12.')
        if self.step_TOL <= 0:
            raise ValueError('The termination criteria step_TOL sent to the\
            backtracking line search is not positive.',
                             'step_TOL = ' + str(self.step_TOL))

    def __set_methods(self):
        """Sets the methods to use.
        """
        if not (self.History in [cdSY_mat, fdSY_mat]):
            self.History = cdSY_mat
        if self.QN_method is Broyden1_product:
            self.spsd = 0
            self.Hessian_product = Broyden1_product
            self.HessianT_product = Broyden1_product
            self.invHessian_product = invBroyden1_product
            self.Scaler = delta_MSB2
            if self.Step_finder is None:
                self.Step_finder = Dogleg_QN
        elif self.QN_method is Broyden2_product:
            self.spsd = 0
            self.Hessian_product = invBroyden2_product
            self.HessianT_product = invBroyden2_product
            self.invHessian_product = Broyden2_product
            self.Scaler = delta_MSB2
            if self.Step_finder is None:
                self.Step_finder = Dogleg_QN
        elif self.QN_method is BFGS1_product:
            self.spsd = 1
            self.Hessian_product = BFGS1_product
            self.HessianT_product = BFGS1_product
            self.invHessian_product = invBFGS1_product
            self.Scaler = delta_invBFGS
            if self.Step_finder is None:
                self.Step_finder = Explicit_TR
            if self.History is fdSY_mat:
                print('Finite difference history ordering not consistent\
                with BFGS,')
                print('   changing to conjugate direction history ordering,\
                cdSY_mat.')
                self.History = cdSY_mat
        else:
            # PYTHON PORT ANNOTATION
            # Changed messages to only mention the currently ported methods.
            # Also changed the error message to be more precise.
            print('No such method.  Current options are:')
            print('        Broyden1_product, Broyden2_product, BFGS1_product.')
            raise ValueError('No such QN_method.',
                             'QN_method = ' + str(self.QN_method))

    def __first_step(self):
        """Initialise variables.
        """
        print('First iteration: initialising...')
        ##################################################
        # Initialisation
        ##################################################
        # PYTHON PORT ANNOTATION
        # Removed fcounter, S_mat, Y_mat, as they weren't used.
        self.it = 0   # Python indexing is 0 based
        self.trstep = 0
        self.mem = -1
        # the maxmem column is a temporary storage area
        self.stepsize_vec = zeros(self.Maxit+1)
        ngradf0 = norm(self.gradf0_vec)
        if is_empty(self.gradfnew_vec):
            # automatically generate the first step
            self.d_vec = (-self.initial_step/ngradf0)*self.gradf0_vec
            self.xnew_vec = self.x0_vec + self.d_vec
            self.gradfnew_vec = 999.*ones(self.dim)
        else:
            self.d_vec = self.xnew_vec - self.x0_vec

        stepsize = norm(self.d_vec)
        self.stepsize_vec[self.it] = stepsize
        self.mu_vec = zeros(self.Maxit+1)
        self.lower_step_bound = 0.
        self.alpha = self.alpha_0
        self.delta = 1.
        self.tr = stepsize
        self.x_mat = zeros((self.dim, self.maxmem+1))
        self.x_mat[:, -2:] = c_[self.x0_vec, self.xnew_vec]
        self.gradf_mat = zeros((self.dim, self.maxmem+1))
        self.gradf_mat[:, -2:] = c_[self.gradf0_vec,
                                    self.gradfnew_vec]
        self.f_vec = zeros(self.Maxit+1)
        if is_empty(self.f0):
            ############################################################
            #   norm squared residual minimization if f0 and fnew empty:
            ############################################################
            self.f0, self.gradf0_vec =\
                Normsqresid(self.Scaler, self.History,
                            self.Hessian_product,
                            self.HessianT_product, self.mem,
                            self.spsd, self.x_mat,
                            self.gradf_mat, self.gradf0_vec,
                            self.alpha_0)
            if is_empty(self.gradfnew_vec):
                # send back to calling driver to get gradfnew
                self.fnew = 999.
            else:
                self.fnew, self.gradfnew =\
                    Normsqresid(self.Scaler, self.History,
                                self.Hessian_product,
                                self.HessianT_product, self.mem,
                                self.spsd, self.x_mat, self.gradf_mat,
                                self.gradfnew_vec, self.alpha_0)
        if is_empty(self.fnew):
            # send back to calling driver to get gradfnew
            self.fnew = 999.

        self.f_vec[self.it] = self.f0
        self.f_vec[self.it+1] = self.fnew
        self.ngradf_vec = zeros(self.Maxit+1)
        self.ngradf_vec[self.it] = ngradf0
        self.ngradf_vec[self.it+1] = norm(self.gradfnew_vec)
        self.DDf = dot(self.gradf_mat[:, -2], self.d_vec)
        self.cDDf = self.c*self.DDf
        self.bDDf = self.beta*self.DDf

    def __prepare_step(self):
        """Get missing function values.
        """
        if is_empty(self.fnew):
            ############################################################
            #   norm squared residual minimization if f0 and fnew empty:
            ############################################################
            self.fnew, self.gradfnew_vec =\
                Normsqresid(self.Scaler, self.History,
                            self.Hessian_product,
                            self.HessianT_product, self.mem,
                            self.spsd, self.x_mat, self.gradf_mat,
                            self.gradfnew_vec, self.alpha_0)
        self.f_vec[self.it+1] = self.fnew
        self.gradf_mat[:, -1] = self.gradfnew_vec
        self.ngradf_vec[self.it+1] = norm(self.gradfnew_vec)

    def __next_step(self):
        """Compute next point.
        """
        DDfnew = dot(self.gradf_mat[:, -1], self.d_vec)

        #################################################################
        #   ADJUST STEP LENGTH/TRUST REGION and determine Update criteria
        ##################################################################
        self.tr, self.mu_vec, self.cDDf, self.lower_step_bound, self.d_vec,\
            self.stepsize_vec, accept_step =\
            Step_length_update(self.History, self.Hessian_product,
                               self.update_conditions, self.mem,
                               self.it, self.x_mat, self.f_vec,
                               self.gradf_mat, self.d_vec,
                               self.mu_vec, self.stepsize_vec,
                               self.tr, self.delta, self.alpha,
                               self.eta1, self.eta2, self.eta3,
                               self.cDDf, DDfnew, self.bDDf,
                               self.orthog_TOL, self.lower_step_bound,
                               self.gamma)

        #####################################################
        #  Update the memory
        #####################################################
        self.x_mat, self.f_vec, self.gradf_mat, self.ngradf_vec,\
            self.stepsize_vec, self.mem =\
            Memory_update(self.x_mat, self.f_vec, self.gradf_mat,
                          self.ngradf_vec, self.stepsize_vec,
                          self.mem, self.spsd, self.it,
                          accept_step)

        if accept_step > -2:
            # If criteria satisfied, then update and increment iterates
            if accept_step >= 0:
                #####################################################
                # reset lower_step_bound increment it
                #####################################################
                self.lower_step_bound = 0.
                self.it += 1

            #####################################################
            # choose new search direction (and length):
            #####################################################
            self.delta, self.alpha, self.d_vec, self.stepsize_vec,\
                self.trstep, self.DDf, self.cDDf, self.bDDf, self.mem =\
                Step_generator(self.Step_finder, self.Scaler,
                               self.History, self.Hessian_product,
                               self.invHessian_product, self.it,
                               self.mem, self.c, self.beta,
                               self.gamma, self.x_mat, self.gradf_mat,
                               self.ngradf_vec, self.stepsize_vec,
                               self.tr, self.trstep, self.alpha_0,
                               self.verbose)

    def __update_step(self):
        """Updates the the matrix of steps.
        """
        # update the proposed step
        self.x_mat[:, self.maxmem] = self.x_mat[:, self.maxmem-1] + self.d_vec
        if self.verbose:
            print('iteration:', self.it, '; trust region:',
                  self.tr, '; memory:', self.mem)

        # PYTHON PORT ANNOTATION
        # Inverted condition for improved readabilty.
        if not (self.it < self.Maxit):
            print('Warning:   Maxit specified in OPTIONS_tolerances.m \
            is smaller')
            print('  than the maximum iterations specified in the driver \
            program.')
            print('  Increase the Maxit in OPTIONS_tolerances to at least \
            that of')
            print('  the driver program.')
            # PYTHON PORT ANNOTATION
            # Added an error message.
            raise ValueError('Iterations reached maximum defined in Maxit',
                             'i = ' + str(self.it),
                             'Maxit = ' + str(self.Maxit))
        self.__set_methods()

    def run(self, x0_vec, xnew_vec, f0, fnew, gradf0_vec, gradfnew_vec):
        """Computes the next point. Main routine of the Resimitpo toolbox.

        Parameters
        ----------
        x0_vec : array_like
            TODO
        xnew_vec : array_like
            TODO
        f0 : float
            TODO
        fnew : float
            TODO
        gradf0_vec : array_like
            TODO
        gradfnew_vec : array_like
            TODO

        Returns
        -------
        xnew_vec : array_like
            The new point.
        x0_vec : array_like
            The old point.
        f0 : float
            The old function value.
        gradf0_vec : array_like
            The old gradient vector.
        stepsize : float
            The length of the last step.
        """
        self.dim = x0_vec.shape[0]

        self.x0_vec = x0_vec
        self.xnew_vec = xnew_vec
        self.f0 = f0
        self.fnew = fnew
        self.gradf0_vec = gradf0_vec
        self.gradfnew_vec = gradfnew_vec

        # first iteration
        if not self.hist:
            self.__first_step()
            self.hist = True
        else:
            self.__prepare_step()
            self.__next_step()

        self.__update_step()

        self.xnew_vec = self.x_mat[:, self.maxmem]
        self.x0_vec = self.x_mat[:, self.maxmem-1]
        self.f0 = self.f_vec[self.it]
        self.gradf0_vec = self.gradf_mat[:, self.maxmem-1]
        stepsize = self.stepsize_vec[self.it]

        return self.xnew_vec, self.x0_vec, self.f0, self.gradf0_vec, stepsize

    def save(self, filename='state.npz', **kwargs):
        """Saves some values of Resimitpo.

        Saves `dim`, `mem`, `it`, `tr`, `x_mat`, `gradf_mat`, `f_vec`,
        `ngradf_vec`, `stepsize_vec` into a file.  This is not needed
        in python since this information can be appended to the Resimitpo class.
        It was used in Fortran and Matlab implementations.

        Parameters
        ----------
        filename : 'state.npz', optional
            The file to write to.
        **kwargs : dict, optional
            Additional variables to be saved.

        See Also
        --------
        plot : If the saved file is given as a parameter, `plot` will
               use it's values instead of the local ones.
        """
        savez(filename, dim=self.dim, mem=self.mem, it=self.it,
              tr=self.tr, x_mat=self.x_mat, gradf_mat=self.gradf_mat,
              f_vec=self.f_vec, ngradf_vec=self.ngradf_vec,
              stepsize_vec=self.stepsize_vec, **kwargs)

    def plot(self, fopt=0., state_file=None):
        """Displays a standard plot for `Resimitpo`.

        If `state_file` is given, then it's values we be used for the
        plot.  Otherwise the values of the current instance of
        `Resimitpo` will be used.

        Parameters
        ----------
        objective : function
            The function resimitpo was minimising.
        state_file : None, optional
            The name of a save file created by the `save` function.

        See Also
        --------
        save : Used to create the `state_file`.
        """
        if state_file is not None:
            try:
                state = load(state_file)
            except:
                print('No such file:', state_file)
                return
            if 'fopt' in state.keys():
                fopt = state['fopt']
            f_vec = state['f_vec']
            ngradf_vec = state['ngradf_vec']
            it = state['it']
        elif self.hist:
            f_vec = self.f_vec
            ngradf_vec = self.ngradf_vec
            stepsize_vec = self.stepsize_vec
            it = self.it
        else:
            print('Nothing to plot yet!')
            print('Try calling resimitpo.run() first or use a state_file.')
            return

        t = arange(it+1)

        plt.subplot(221)
        f_adj = f_vec[:it+1] - fopt
        plt.semilogy(t, f_adj[t])
        plt.title('Function value')
        plt.xlabel('iterations')
        plt.ylabel('f(x)')

        plt.subplot(222)
        plt.semilogy(t, ngradf_vec[t])
        plt.title('gradient norm')
        plt.xlabel('iteration')
        plt.ylabel('log(gradient norm)')

        plt.subplot(223)
        plt.semilogy(t, stepsize_vec[t])
        plt.title('stepsize')
        plt.xlabel('iterations')
        plt.ylabel('||x_{k+1}-x_k||')

        plt.show()
