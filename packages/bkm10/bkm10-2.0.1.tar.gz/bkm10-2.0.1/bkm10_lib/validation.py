"""

"""

from bkm10_lib.inputs import BKM10Inputs
from bkm10_lib.cff_inputs import CFFInputs

def validate_configuration(configuration_dictionary: dict, verbose: bool):
    """
    ## Description:
    Validate user's dict of initialization parameters.
    
    ## Parameters:
    configuration_dictionary (dict):
        a dict of user-requests DNN parameters that 
        will be used to attempt to build a TF network.

    verbose (boolean):
        Do you want to see all output of this function evaluation?

    ## Notes
    
    """

    required_keys = [
        "kinematics",
        "cff_inputs",
        "target_polarization", 
        "lepton_beam_polarization"
        ]
    
    for key in required_keys:
        if key not in configuration_dictionary:
            raise ValueError(f"Missing required key in config: {key}")
    
    kinematic_settings = configuration_dictionary["kinematics"]

    if not kinematic_settings:
        raise ValueError("> Missing 'kinematics' key.")

    if not isinstance(kinematic_settings, BKM10Inputs):
        raise TypeError("> 'kinematics' key must be a BKM10Inputs instance.")

    cff_settings = configuration_dictionary["cff_inputs"]

    if not cff_settings:
        raise ValueError("> Missing 'cff_inputs' key.")

    if not isinstance(cff_settings, CFFInputs):
        raise TypeError("> 'cff_inputs' key must be a CFFInputs instance.")
    
    target_polarization = configuration_dictionary["target_polarization"]

    if target_polarization is None:
        raise ValueError("> Missing 'target_polarization' key.")

    if target_polarization != 0. and target_polarization != 0.5 and target_polarization != -0.5:
        raise TypeError("> 'target_polarization' key must be a *float* of -1.0, 0.0, or 1.0 only.")
    
    lepton_beam_polarization = configuration_dictionary["lepton_beam_polarization"]

    if lepton_beam_polarization is None:
        raise ValueError("> Missing 'lepton_beam_polarization' key.")

    if lepton_beam_polarization != 0. and lepton_beam_polarization != 1.0 and lepton_beam_polarization != -1.0:
        raise TypeError("> 'lepton_beam_polarization' key must be a *float* of -0.5, 0.0, or 0.5 only.")
    
    return configuration_dictionary