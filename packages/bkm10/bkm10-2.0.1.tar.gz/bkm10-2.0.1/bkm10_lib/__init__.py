"""
# BKM10 Library
The fundamental package for computing (cross sections using the
BKM10 formalism)!

## Description:
A Python library to help nuclear physicists use the BKM formalism in predicting
cross-sections, asymmetries, and comparing GPD models.
"""

# (1): Expose the cross-section calculator class:
from .core import DifferentialCrossSection

# (2): Expose the BKM formalism class... in case people want that:
from .formalism import BKMFormalism

# (3): Expose the dataclass `CFFInputs`... for getting familiar with it:
from .cff_inputs import CFFInputs

# (4): Expose the dataclass `BKM10Inputs` in order to evaluate the cross section:
from .inputs import BKM10Inputs

# (5): Expose the backend: This is important if the user is using TensorFlow:
from .backend import math
