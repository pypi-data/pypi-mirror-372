"""
The entry point for the dataclass `CFFInputs`
"""

# (1): Import the specialized `dataclass` library:
from dataclasses import dataclass

# (2): 
from bkm10_lib import backend

# (3): Immediately define the CFFInputs dataclass:
@dataclass
class CFFInputs:
    """
    Welcome to the `CFFInputs` dataclass!

    ## Description:
    The CFFs (Compton Form Factors) live inside the BKM10 cross section.
    They are unknown functions that also parametrize the DVCS process. Please
    read the "notes" section below for motivation behind why we use it. What is
    relevant for the programmer here is that these CFFs *must* be supplied in 
    order to return a cross section. You need to make at least a *guess* for
    what their values are.

    ## Notes:
    The CFFs enter the cross section through loop integration of a perturbativley hard 
    interaction and a more general structure function called a GPD (generalized parton
    distribution) over the parton momentum fraction (which we call x). A lot of this 
    business of measuring DVCS cross sections is really about figuring out the form of
    the CFFs and the GPDs. However, in order to make predictions about the cross-section,
    these functions require input themselves.
    """
    
    # (1): The CFF H --- Requires Re[H] and Im[H], so it's of `complex` type:
    compton_form_factor_h: complex

    # (2): The CFF H_tilde --- Requires Re[Ht] and Im[Ht]:
    compton_form_factor_h_tilde: complex

    # (3): The CFF E --- Requires Re[E] and Im[E]:
    compton_form_factor_e: complex

    # (4): The CFF E_tilde --- Requires Re[Et] and Im[Et]:
    compton_form_factor_e_tilde: complex

    def conjugate(self):
        """
        ## Description:
        Computes the complex conjugate each of the CFFs in this dataclasss.
        """

        conjugate_function = backend.math.conj

        return CFFInputs(
            compton_form_factor_h = conjugate_function(self.compton_form_factor_h),
            compton_form_factor_h_tilde = conjugate_function(self.compton_form_factor_h_tilde),
            compton_form_factor_e = conjugate_function(self.compton_form_factor_e),
            compton_form_factor_e_tilde = conjugate_function(self.compton_form_factor_e_tilde),
        )
