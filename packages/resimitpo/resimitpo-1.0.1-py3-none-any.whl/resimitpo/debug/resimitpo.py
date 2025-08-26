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
    # TODO(benedikt) This code is never executed!
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
        gradf0_vec = gradfnew_vec

    return f0, gradf0_vec


class Resimitpo():
    def __init__(self):
        """Sets default values.
        """
        # Declare Parameters
        self.x0_vec = None
        self.xnew_vec = None
        self.f0 = None
        self.fnew = None
        self.gradf0_vec = None
        self.gradfnew_vec = None

        # TODO(benedikt) DELETE ME
        self.debug_file = 'py_vars.npz'
        self.debug = 'step_generator'
        self.TMP = {}
        self.TMP['mem_1'] = -100.
        self.TMP['mem_2'] = -100.
        self.TMP['fnew_1'] = -100.
        self.TMP['gradfnew_1'] = -100.
        self.TMP['tr_slu'] = -100.
        self.TMP['mu_vec_slu'] = -100.
        self.TMP['cDDf_slu'] = -100.
        self.TMP['lower_step_bound_slu'] = -100.
        self.TMP['d_vec_slu'] = -100.
        self.TMP['stepsize_vec_slu'] = -100.
        self.TMP['accept_step_slu'] = -100.
        self.TMP['x_mat_mu'] = -100.
        self.TMP['f_vec_mu'] = -100.
        self.TMP['gradf_mat_mu'] = -100.
        self.TMP['ngradf_vec_mu'] = -100.
        self.TMP['stepsize_vec_mu'] = -100.
        self.TMP['delta_sg'] = -100.
        self.TMP['alpha_sg'] = -100.
        self.TMP['d_vec_sg'] = -100.
        self.TMP['stepsize_vec_sg'] = -100.
        self.TMP['trstep_sg'] = -100.
        self.TMP['DDf_sg'] = -100.
        self.TMP['cDDf_sg'] = -100.
        self.TMP['bDDf_sg'] = -100.
        self.TMP['x_mat_ns'] = -100.
        self.TMP['f_vec_ns'] = -100.
        self.TMP['gradf_mat_ns'] = -100.
        self.TMP['d_vec_ns'] = -100.
        self.TMP['mu_vec_ns'] = -100.
        self.TMP['stepsize_vec_ns'] = -100.
        self.TMP['tr_ns'] = -100.
        self.TMP['delta_ns'] = -100.
        self.TMP['alpha_ns'] = -100.
        self.TMP['eta1_ns'] = -100.
        self.TMP['eta2_ns'] = -100.
        self.TMP['eta3_ns'] = -100.
        self.TMP['cDDf_ns'] = -100.
        self.TMP['DDfnew_ns'] = -100.
        self.TMP['bDDf_ns'] = -100.
        self.TMP['orthog_TOL_ns'] = -100.
        self.TMP['lower_step_bound_ns'] = -100.
        self.TMP['gamma_ns'] = -100.
        self.TMP['d_vec_us'] = -100.
        self.TMP['x_mat_us'] = -100.

        params = {}
        params['verbose'] = True
        params['alpha_0'] = 5e-9
        params['gamma'] = .5
        params['c'] = .01
        params['beta'] = .99
        params['eta1'] = .995
        params['eta2'] = .8
        params['eta3'] = .05
        # params['eta4'] = .025
        params['maxmem'] = 9
        # params['lookback'] = 0
        params['tr'] = 1e+15

        tols = {}
        tols['ngrad_TOL'] = 1e-6
        tols['step_TOL'] = 1e-14
        tols['Maxit'] = 500
        tols['orthog_TOL'] = 1e-6

        opts = {}
        opts['QN_method'] = BFGS1_product
        opts['Step_finder'] = None
        opts['History'] = cdSY_mat
        opts['update_conditions'] = 'Trust Region'
        opts['initial_step'] = 1e+5*tols['step_TOL']

        self.load_options(params, tols, opts)

        self.hist = False

    def __validate_options(self):
        """Validates the set parameters.
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
            self.Step_finder = Dogleg_QN
        elif self.QN_method is Broyden2_product:
            self.spsd = 0
            self.Hessian_product = invBroyden2_product
            self.HessianT_product = invBroyden2_product
            self.invHessian_product = Broyden2_product
            self.Scaler = delta_MSB2
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
            self.d_vec = -self.initial_step*self.gradf0_vec/ngradf0
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
        self.TMP['fnew_1'] = self.fnew
        self.TMP['gradfnew_1'] = self.gradfnew_vec

    def __next_step(self):
        """Compute next point.
        """
        DDfnew = dot(self.gradf_mat[:, -1], self.d_vec)

        self.TMP['x_mat_ns'] = self.x_mat.copy()
        self.TMP['f_vec_ns'] = self.f_vec.copy()
        self.TMP['gradf_mat_ns'] = self.gradf_mat.copy()
        self.TMP['d_vec_ns'] = self.d_vec.copy()
        self.TMP['mu_vec_ns'] = self.mu_vec.copy()
        self.TMP['stepsize_vec_ns'] = self.stepsize_vec.copy()
        self.TMP['tr_ns'] = self.tr
        self.TMP['delta_ns'] = self.delta
        self.TMP['alpha_ns'] = self.alpha
        self.TMP['eta1_ns'] = self.eta1
        self.TMP['eta2_ns'] = self.eta2
        self.TMP['eta3_ns'] = self.eta3
        self.TMP['cDDf_ns'] = self.cDDf
        self.TMP['DDfnew_ns'] = DDfnew
        self.TMP['bDDf_ns'] = self.bDDf
        self.TMP['orthog_TOL_ns'] = self.orthog_TOL
        self.TMP['lower_step_bound_ns'] = self.lower_step_bound
        self.TMP['gamma_ns'] = self.gamma
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

        self.TMP['tr_slu'] = self.tr
        self.TMP['mu_vec_slu'] = self.mu_vec.copy()
        self.TMP['cDDf_slu'] = self.cDDf
        self.TMP['lower_step_bound_slu'] = self.lower_step_bound
        self.TMP['d_vec_slu'] = self.d_vec.copy()
        self.TMP['stepsize_vec_slu'] = self.stepsize_vec.copy()
        self.TMP['accept_step_slu'] = accept_step

        #####################################################
        #  Update the memory
        #####################################################
        self.x_mat, self.f_vec, self.gradf_mat, self.ngradf_vec,\
            self.stepsize_vec, self.mem =\
            Memory_update(self.x_mat, self.f_vec, self.gradf_mat,
                          self.ngradf_vec, self.stepsize_vec,
                          self.mem, self.spsd, self.it,
                          accept_step)

        self.TMP['mem_1'] = self.mem
        self.TMP['x_mat_mu'] = self.x_mat.copy()
        self.TMP['f_vec_mu'] = self.f_vec.copy()
        self.TMP['gradf_mat_mu'] = self.gradf_mat.copy()
        self.TMP['ngradf_vec_mu'] = self.ngradf_vec.copy()
        self.TMP['stepsize_vec_mu'] = self.stepsize_vec.copy()

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

            self.TMP['mem_2'] = self.mem
            self.TMP['delta_sg'] = self.delta
            self.TMP['alpha_sg'] = self.alpha
            self.TMP['d_vec_sg'] = self.d_vec.copy()
            self.TMP['stepsize_vec_sg'] = self.stepsize_vec.copy()
            self.TMP['trstep_sg'] = self.trstep
            self.TMP['DDf_sg'] = self.DDf
            self.TMP['cDDf_sg'] = self.cDDf
            self.TMP['bDDf_sg'] = self.bDDf

    # TODO(benedikt) Integrate with run()?
    def __update_step(self):
        """Updates the the matrix of steps.
        """
        # update the proposed step
        self.x_mat[:, self.maxmem] = self.x_mat[:, self.maxmem-1] + self.d_vec
        self.TMP['d_vec_us'] = self.d_vec.copy()
        self.TMP['x_mat_us'] = self.x_mat.copy()
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

    def load_options(self, params, tols, opts):
        """Set options.
        """
        for k, v in params.items():
            if k == 'verbose':
                self.verbose = v
            if k == 'alpha_0':
                self.alpha_0 = v
            if k == 'gamma':
                self.gamma = v
            if k == 'c':
                self.c = v
            if k == 'beta':
                self.beta = v
            if k == 'eta1':
                self.eta1 = v
            if k == 'eta2':
                self.eta2 = v
            if k == 'eta3':
                self.eta3 = v
            # if k == 'eta4':
            #     self.eta4 = v
            if k == 'maxmem':
                self.maxmem = v
            if k == 'tr':
                self.tr = v

        for k, v in tols.items():
            if k == 'ngrad_TOL':
                self.ngrad_TOL = v
            if k == 'step_TOL':
                self.step_TOL = v
            if k == 'Maxit':
                self.Maxit = v
            if k == 'orthog_TOL':
                self.orthog_TOL = v

        for k, v in opts.items():
            if k == 'QN_method':
                self.QN_method = v
            if k == 'Step_finder':
                self.Step_finder = v
            if k == 'History':
                self.History = v
            if k == 'update_conditions':
                self.update_conditions = v
            if k == 'initial_step':
                self.initial_step = v

        self.__validate_options()
        self.__set_methods()

    def run(self, x0_vec, xnew_vec, f0, fnew, gradf0_vec, gradfnew_vec):
        """Computes the next point. Main routine of the SAMSARA toolbox.

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

        # TODO(benedikt) DELETE ME
        if self.debug == 'final':
            # final values
            savez(self.debug_file, xnew_vec=self.xnew_vec,
                  x0_vec=self.x0_vec, f0=self.f0,
                  gradf0_vec=self.gradf0_vec, stepsize=stepsize,
                  tr=self.tr, mem=self.mem)
        elif self.debug == 'step_length_update':
            # Step_length_update
            savez(self.debug_file, mu_vec_slu=self.TMP['mu_vec_slu'],
                  cDDf_slu=self.TMP['cDDf_slu'],
                  lower_step_bound_slu=self.TMP['lower_step_bound_slu'],
                  d_vec_slu=self.TMP['d_vec_slu'],
                  stepsize_vec_slu=self.TMP['stepsize_vec_slu'],
                  accept_step_slu=self.TMP['accept_step_slu'],
                  tr_slu=self.TMP['tr_slu'])
        elif self.debug == 'next_step':
            # __next_step beginning
            savez(self.debug_file, x_mat_ns=self.TMP['x_mat_ns'],
                  f_vec_ns=self.TMP['f_vec_ns'],
                  gradf_mat_ns=self.TMP['gradf_mat_ns'],
                  d_vec_ns=self.TMP['d_vec_ns'],
                  mu_vec_ns=self.TMP['mu_vec_ns'],
                  stepsize_vec_ns=self.TMP['stepsize_vec_ns'],
                  tr_ns=self.TMP['tr_ns'],
                  delta_ns=self.TMP['delta_ns'],
                  alpha_ns=self.TMP['alpha_ns'],
                  eta1_ns=self.TMP['eta1_ns'],
                  eta2_ns=self.TMP['eta2_ns'],
                  eta3_ns=self.TMP['eta3_ns'],
                  cDDf_ns=self.TMP['cDDf_ns'],
                  DDfnew_ns=self.TMP['DDfnew_ns'],
                  bDDf_ns=self.TMP['bDDf_ns'],
                  orthog_TOL_ns=self.TMP['orthog_TOL_ns'],
                  lower_step_bound_ns=self.TMP['lower_step_bound_ns'],
                  gamma_ns=self.TMP['gamma_ns'])
        elif self.debug == 'memory_update':
            # Memory_update
            savez(self.debug_file, x_mat_mu=self.TMP['x_mat_mu'],
                  f_vec_mu=self.TMP['f_vec_mu'],
                  gradf_mat_mu=self.TMP['gradf_mat_mu'],
                  ngradf_vec_mu=self.TMP['ngradf_vec_mu'],
                  stepsize_vec_mu=self.TMP['stepsize_vec_mu'],
                  accept_step_slu=self.TMP['accept_step_slu'])
        elif self.debug == 'step_generator':
            # Step_generator
            savez(self.debug_file, delta_sg=self.TMP['delta_sg'],
                  alpha_sg=self.TMP['alpha_sg'],
                  d_vec_sg=self.TMP['d_vec_sg'],
                  stepsize_vec_sg=self.TMP['stepsize_vec_sg'],
                  trstep_sg=self.TMP['trstep_sg'],
                  DDf_sg=self.TMP['DDf_sg'],
                  cDDf_sg=self.TMP['cDDf_sg'],
                  bDDf_sg=self.TMP['bDDf_sg'])
        elif self.debug == 'update_step':
            savez(self.debug_file, d_vec_us=self.TMP['d_vec_us'],
                  x_mat_us=self.TMP['x_mat_us'])
        else:
            # we always need a file for debug_driver
            # savez(self.debug_file, x_mat=self.x_mat)
            pass

        return self.xnew_vec, self.x0_vec, self.f0, self.gradf0_vec, stepsize

    def save(self, filename='state.npz'):
        """Saves some values of resimitpo.

        Saves `dim`, `f_vec`, `ngradf_vec`, `it`, `stepsize_vec`,
        `mu_vec` to the file indicated by `filename`.

        Parameters
        ----------
        filename : Optional[str]
            The file to write to. Default: `state.npz`
        """
        savez(filename, dim=self.dim, f_vec=self.f_vec,
              ngradf_vec=self.ngradf_vec, it=self.it,
              stepsize_vec=self.stepsize_vec, mu_vec=self.mu_vec)

    def plot(self, objective, state_file=None):
        """Displays a standard plot for `Resimitpo`.

        If `state_file` is given, then it's values we be used for the
        plot. Otherwise the valuues of the current instance of
        `Resimitpo` will be used.

        Parameters
        ----------
        objective : function
            The function resimitpo was minimising.
        state_file : Optional[str]
            A save file created by ``save``.

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
            dim = state['dim']
            f_vec = state['f_vec']
            ngradf_vec = state['ngradf_vec']
            it = state['it']
        elif self.hist:
            dim = self.dim
            f_vec = self.f_vec
            ngradf_vec = self.ngradf_vec
            stepsize_vec = self.stepsize_vec
            it = self.it
        else:
            print('Nothing to plot yet!')
            print('Try calling resimitpo.run() first.')
            return

        t = arange(it+1)
        f_opt, _ = objective(ones(dim))

        plt.subplot(221)
        f_adj = abs(f_vec[:it+1] - f_opt)
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
