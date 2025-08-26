# Resimitpo (formerly Samsara)

1.  [Documentation](#orgedf932c)
2.  [Tutorial](#orge926c85)
3.  [Credits](#org87931d4)

The original package was named ``Samsara``, but the name has been changed to ``Resimitpo`` in order to avoid conflicts with another python
API under the name of Samsara.  If it helps, ``resimitpo`` is "optimiser" backwards.  It is also German for "Resi with butt".

Resimitpo is a reverse communication nonlinear optimization solver for smooth unconstrained objectives. Resimitpo is just an oracle
that suggests a step (direction and length) using previous information provided to it by the calling routine. It does not execute
function evaluations or gradient calculations,
but it does build a model of the function being optimized, based on the steps, gradients and function values (if available) passed to it by the user. 
This repository contains the Python version of Resimitpo.

This package is available on PyPI and can be installed with the command

```sh
pip install resimitpo
```


<a id="orgedf932c"></a>

## Documentation


<a id="orge926c85"></a>

## Tutorial

The file `examples/example.py` contains a running example of how to use Resimitpo. This document tries to explain how all the moving pieces in the example fit together.

The first step is importing resimitpo

```python
import matplotlib.pyplot as plt
from numpy import abs, amax, array, load, zeros
from numpy.linalg import norm

from resimitpo import Resimitpo, BFGS1_product, Broyden1_product,\
  Broyden2_product, Dogleg_QN, Explicit_TR, cdSY_mat, fdSY_mat
```

In order to use Resimitpo, we need an objective function to minimize and its gradient. For this example we will use Rosenbrocks's function

```math
f(x, y) = 100(y-x^2)^2+(1-x)^2
```

```python
def Objective(x):
    f = 100*(x[1]-x[0]**2)**2 + (1-x[0])**2
    Df = zeros(2)
    Df[0] = -400*(x[1]-x[0]**2)*x[0] - 2*(1-x[0])
    Df[1] = 200*(x[1]-x[0]**2)
    return f, Df
```

The next step is to create the options dictionary that will be passed to the solver.

```python
ngrad_TOL = 6e-6   # eps**(1/3)
step_TOL = 4e-11   # eps**(2/3)
Maxit = 500
options = {}
options['verbose'] = True
options['alpha_0'] = 5e-12
options['gamma'] = .5
options['c'] = .01
options['beta'] = .9999999
options['eta1'] = .995
options['eta2'] = .8
options['eta3'] = .25
options['maxmem'] = 8
options['tr'] = 1e+15
options['ngrad_TOL'] = ngrad_TOL
options['step_TOL'] = step_TOL
options['Maxit'] = Maxit
options['QN_method'] = BFGS1_product
options['Step_finder'] = Explicit_TR
options['History'] = cdSY_mat
options['update_conditions'] = 'Trust Region'
options['initial_step'] = 1e+5*options['step_TOL']
```

We need to unpack this dictionary as parameters in the constructor of the `Resimitpo` class.

```python
resimitpo = Resimitpo(**options)
```

Now that the `Resimitpo` object was created we need to provide the initial configuration of the main loop.

```python
xold_vec = array([.5, 2.])
fold, gradfold_vec = Objective(xold_vec)
xnew_vec = None
fnew = None
gradfnew_vec = None
stepsize = 999.
ngradfnew = 999.
it = 0
```

The main loop of the program has to call the oracle in order to obtain a new point candidate. In this example we will accept the candidate unconditionally.

```python
while it < Maxit and ngradfnew > ngrad_TOL and stepsize > step_TOL:
    xnew_vec, xold_vec, fold, gradfold_vec, stepsize =\
	resimitpo.run(xold_vec, xnew_vec, fold, fnew, gradfold_vec,
		    gradfnew_vec)
    it += 1
    fnew, gradfnew_vec = Objective(xnew_vec)
    ngradfnew = norm(gradfnew_vec)
```

```
First iteration: initialising...
iteration: 0 ; trust region: 4e-06 ; memory: -1
iteration: 1 ; trust region: 40.0 ; memory: 0
iteration: 2 ; trust region: 40.0 ; memory: 1
iteration: 2 ; trust region: 4e-07 ; memory: 0
iteration: 2 ; trust region: 19.193508015823596 ; memory: 0
iteration: 2 ; trust region: 9.596754007911798 ; memory: 0
iteration: 2 ; trust region: 4.798377003955899 ; memory: 0
iteration: 2 ; trust region: 2.3991885019779495 ; memory: 0
iteration: 3 ; trust region: 2.3991885019779495 ; memory: 1
iteration: 4 ; trust region: 0.4894454502747553 ; memory: 2
iteration: 5 ; trust region: 2.4472272513737763 ; memory: 3
iteration: 6 ; trust region: 12.236136256868882 ; memory: 4
iteration: 7 ; trust region: 61.18068128434441 ; memory: 5
iteration: 8 ; trust region: 305.903406421722 ; memory: 6
iteration: 9 ; trust region: 1529.5170321086102 ; memory: 7
iteration: 10 ; trust region: 7647.585160543051 ; memory: 7
iteration: 11 ; trust region: 38237.925802715254 ; memory: 7
iteration: 12 ; trust region: 191189.62901357625 ; memory: 7
iteration: 13 ; trust region: 955948.1450678813 ; memory: 7
iteration: 14 ; trust region: 4779740.725339407 ; memory: 7
iteration: 15 ; trust region: 23898703.626697034 ; memory: 7
iteration: 16 ; trust region: 119493518.13348517 ; memory: 7
iteration: 17 ; trust region: 597467590.6674259 ; memory: 7
in trust region subproblem
iteration: 17 ; trust region: 0.004495650683068379 ; memory: 6
in trust region subproblem
iteration: 17 ; trust region: 0.0004495650683068379 ; memory: 5
in trust region subproblem
iteration: 18 ; trust region: 0.0022478253415341896 ; memory: 6
in trust region subproblem
iteration: 19 ; trust region: 0.011239126707670948 ; memory: 7
iteration: 20 ; trust region: 0.056195633538354745 ; memory: 7
iteration: 21 ; trust region: 0.11239126707670949 ; memory: 7
iteration: 22 ; trust region: 0.22478253415341898 ; memory: 7
```

The last step in using Resimitpo is to output the results

```python
if stepsize <= options['step_TOL']:
    print('Algorithm stagnated:  stepsize tolerance violated.')
if it >= options['Maxit']:
    print('Algorithm exceeded:  maximum step count violated.')

print('iterations:', it, '; optimal value:', fnew)
```

    iterations: 30 ; optimal value: 1.8348194092063077e-17

and to plot the behavior of the function values.

```python
resimitpo.plot(fopt=fnew)
plt.savefig('./resimitpo_results.png')
```

![Plot Results](python/doc/resimitpo_results.png "Plots")

<a id="org87931d4"></a>

## Credits

Development on Resimitpo began in 2007 with funding from the National Science Foundation of the USA, DMS-0712796.

Contributors include:

-   Russell Luke (main author), Institute for Numerical and Applied Mathematics, University of Göttingen

-   Student helpers:
    -   Rachael Bailine (Matlab and Fortran version), University of Delaware
    -   Patrick Rowe (Fortran version), University of Delaware
    -   Brian Rife (Fortran version), University of Delaware
    -   Marco Bedolla (Fortran version), University of Delaware
    -   Benedikt Rascher-Friesenhausen (Python version), University of Göttingen
    -   Titus Pinta, University of Göttingen

Special thanks to Laurence Marks at Northwestern University and Peter Blaha at the Technical University of Vienna who provided much of the inspiration for Resimitpo.
