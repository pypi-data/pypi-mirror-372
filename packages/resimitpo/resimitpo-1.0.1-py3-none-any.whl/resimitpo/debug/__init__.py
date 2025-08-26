"""

Extending resimitpo
-----------------
Any functions from additional modules have to be imported in this file.

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
