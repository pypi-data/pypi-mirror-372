"""Provides the class Resimitpo that is an unconstrained optimiser for
real-valued functions.

Running Resimitpo
===============

Resimitpo is written for Python 3 (but works with Python 2.7) and has
the following dependencies:

   * `numpy`
   * `matplotlib`

You should also add the location of your resimitpo folder to the
``PYTHONPATH`` environment variable.

To use Resimitpo with your project copy the `driver.py` file from the
resimitpo folder to any destination you like and edit it with the
function you want optimised.

Running the Tests
=================

To run the tests you will need to have MATLAB, the `matlab` module for
Python installed (the module can be found with your installed MATLAB
program in `<path-to-matlab>/extern/engines/python`) and pytest
installed.  To run the test you then execute

  >>> py.test <test_file>
"""

### MODULE FUNCTION IMPORTS ###

# Resimitpo
from .resimitpo import Resimitpo

# Hessian products and Scaler
from .hessian import BFGS1_product, invBFGS1_product, Broyden1_product,\
    invBroyden1_product, Broyden2_product, invBroyden2_product,\
    delta_MSB2, delta_invBFGS

# History
from .history import fdSY_mat, cdSY_mat

# Step finder
from .step_finder import Dogleg_QN, Explicit_TR
