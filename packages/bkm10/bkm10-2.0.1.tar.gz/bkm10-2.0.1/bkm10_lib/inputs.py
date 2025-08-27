"""
Entry point for the BKM10Inputs dataclass.
"""

# (1): Import the specialized `dataclass` library:
from dataclasses import dataclass

# (2): Define the dataclass right away:
@dataclass
class BKM10Inputs:
    """
    Welcome to the `BKKM10Inputs` dataclass! 

    ## Description:
    We use this dataclass to handle the passage of the 
    "kinematic settings" that parametrize the DVCS cross section 
    according to the BKM10 formalism. That means, in order to
    obtain a cross section at the end of your calculation, you 
    must instantiate this dataclass.
    """

    # (1): Q^{2}: photon virtuality:
    squared_Q_momentum_transfer: float

    # (2): x_{B}: Bjorken's x:
    x_Bjorken: float

    # (3): t: hadron momentum transfer: (p - p')^{2}:
    squared_hadronic_momentum_transfer_t: float

    # (4): ...
    lab_kinematics_k: float
