"""
## Description:
A testing suite for proving that the functions computing the coefficients for the
longitudinally-polarized target are returning real, finite, and accurate values.

## Notes:

1. 2025/07/24:
    - All DVCS tests pasted with current Mathematica values. Nice!
"""

# (X): Native Library | unittest:
import unittest

# (X): External Library | NumPy:
import numpy as np

# (X): Self-Import | BKM10Inputs:
from bkm10_lib.inputs import BKM10Inputs

# (X): Self-Import | CFFInputs:
from bkm10_lib.cff_inputs import CFFInputs

# (X): Self-Import | DifferentialCrossSection
from bkm10_lib.core import DifferentialCrossSection

# (X): Self-Import | BKMFormalism
from bkm10_lib.formalism import BKMFormalism


# (X): Define a class that inherits unittest's TestCase:
class TestDVCSCoefficients(unittest.TestCase):
    """
    ## Description:
    We need to verify that all of the coefficients that go into computation of the 
    BKM10 cross-section are correct. There are a LOT of them, so this test is important.

    ## Detailed Description:
    Later!
    """

    # (X): Specify a value for k (the beam energy):
    TEST_LAB_K = 5.75

    # (X): Specify a Q^{2} value:
    TEST_Q_SQUARED = 1.82

    # (X): Specify an x_{B} value:
    TEST_X_BJORKEN = 0.34

    # (X): Specify a t value.
    # | [NOTE]: This number is usually negative:
    TEST_T_VALUE = -.17

    # (X): Specify the CFF H values:
    CFF_H = complex(-0.897, 2.421)

    # (X): Specify the CFF H-tilde values:
    CFF_H_TILDE = complex(2.444, 1.131)

    # (X): Specify the CFF E values:
    CFF_E = complex(-0.541, 0.903)

    # (X): Specify the CFF E-tilde values:
    CFF_E_TILDE = complex(2.207, 5.383)

    # (X): Specify a starting value for azimuthal phi:
    STARTING_PHI_VALUE_IN_DEGREES = 0

    # (X): Specify a final value for azimuthal phi:
    ENDING_PHI_VALUE_IN_DEGREES = 360

    # (X): Specify *how many* values of phi you want to evaluate the cross-section
    # | at. [NOTE]: This determines the *length* of the array:
    NUMBER_OF_PHI_POINTS = 15

    @classmethod
    def setUpClass(cls):

        # (X): Provide the BKM10 inputs to the dataclass:
        cls.test_kinematics = BKM10Inputs(
            lab_kinematics_k = cls.TEST_LAB_K,
            squared_Q_momentum_transfer = cls.TEST_Q_SQUARED,
            x_Bjorken = cls.TEST_X_BJORKEN,
            squared_hadronic_momentum_transfer_t = cls.TEST_T_VALUE)

        # (X): Provide the CFF inputs to the dataclass:
        cls.test_cff_inputs = CFFInputs(
            compton_form_factor_h = cls.CFF_H,
            compton_form_factor_h_tilde = cls.CFF_H_TILDE,
            compton_form_factor_e = cls.CFF_E,
            compton_form_factor_e_tilde = cls.CFF_E_TILDE)
        
        # (X): Specify the target polarization *as a float*:
        cls.target_polarization = 0.5

        # (X): Specify the beam polarization *as a float*:
        cls.lepton_polarization = 1.0

        # (X): We are using the WW relations in this computation:
        cls.ww_setting = True

        # (X): Using the setting we wrote earlier, we now need to construct
        cls.configuration = {
            "kinematics": cls.test_kinematics,
            "cff_inputs": cls.test_cff_inputs,
            "target_polarization": cls.target_polarization,
            "lepton_beam_polarization": cls.lepton_polarization,
            "using_ww": cls.ww_setting
        }
        
        # (X): *Initialize* the cross-section class.
        # | [NOTE]: This does NOT compute the cross-section automatically.
        cls.cross_section = DifferentialCrossSection(
            configuration = cls.configuration)

        # (X): Initialize an array of phi-values in preparation to evaluate the
        # | cross-section at.
        cls.phi_values = np.linspace(
            start = cls.STARTING_PHI_VALUE_IN_DEGREES,
            stop = cls.ENDING_PHI_VALUE_IN_DEGREES,
            num = cls.NUMBER_OF_PHI_POINTS)
        
        # (X): Initialize a `BKMFormalism` class. This enables us to
        # | fully disentangle each of the coefficients.
        cls.bkm_formalism = BKMFormalism(
            inputs = cls.test_kinematics,
            cff_values = cls.test_cff_inputs,
            
            # (X): [NOTE]: All the S-coeffcicients are sensitive to lambda, so
            # | they will be 0 if you do not make this value 1.0.
            lepton_polarization = cls.lepton_polarization,
            target_polarization = cls.target_polarization,
            using_ww = True)
    
    def assert_is_finite(self, value):
        """
        ## Description:
        A general test in the suite that verifies that all the
        numbers in an array are *finite* (as opposed to Inf.-type or NaN)

        ## Notes:
        "NaN" means "not a number." Having NaN values in an array causes problems in
        functions that are designed to perform arithmetic.
        """
        self.assertTrue(
            expr = np.isfinite(value).all(),
            msg = "Value contains NaNs or infinities/Inf.")

    def assert_no_nans(self, value):
        """
        ## Description:
        A general test in the suite that determines if an array has NaNs.
        
        ## Notes:
        "NaN" means "not a number." Having NaN values in an array causes problems in
        functions that are designed to perform arithmetic.
        """
        self.assertFalse(
            expr = np.isnan(value).any(),
            msg = "> [ERROR]: Value contains NaNs")

    def assert_no_negatives(self, value):
        """
        ## Description:
        A general test in the suite that determines if an array has negative values
        in it.

        ## Notes:
        There *are* important negative quantities, and several coefficients are indeed
        negative. But cross-sections, for example, should be positive.
        """
        self.assertTrue(
            expr = (value >= 0).all(),
            msg = "> [ERROR]: Value contains negative values")

    def assert_is_real(self, value):
        """
        ## Description:
        A general test in the suite that determines that an array has
        all real values.
        """
        self.assertTrue(
            expr = np.isreal(value).all(),
            msg = "> [ERROR]: Value contains complex components")

    def assert_approximately_equal(self, value, expected, tolerance = 1e-8):
        """
        ## Description:
        A general test in the suite that determines if a *number* (`value`) is approximately
        equal to what is expected (`expected`). "Approximately equal" is quantified with the 
        parameter `tolerance`.
        """
        self.assertTrue(
            np.allclose(value, expected, rtol = tolerance, atol = tolerance),
            f"> [ERROR]: Expected {expected}, got {value}")
        
    def test_calculate_dvcs_c0_coefficient(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient c_{0}^{DVCS}.
        """
        c0dvcs = self.bkm_formalism.compute_dvcs_c0_coefficient()

        # (X): Verify that c_{0}^{DVCS} is a *finite* number:
        self.assert_is_finite(c0dvcs)
        
        # (X); Verify that c_{0}^{DVCS} is not a NaN:
        self.assert_no_nans(c0dvcs)

        # (X): Verify that c_{0}^{DVCS} is real:
        self.assert_is_real(c0dvcs)

        _MATHEMATICA_RESULT = 0.2059041946153708

        self.assert_approximately_equal(c0dvcs, expected = _MATHEMATICA_RESULT)

    def test_calculate_dvcs_c1_coefficient(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient c_{1}^{DVCS}.
        """
        c1dvcs = self.bkm_formalism.compute_dvcs_c1_coefficient()

        # (X): Verify that c_{1}^{DVCS} is a *finite* number:
        self.assert_is_finite(c1dvcs)
        
        # (X); Verify that c_{1}^{DVCS} is not a NaN:
        self.assert_no_nans(c1dvcs)

        # (X): Verify that c_{1}^{DVCS} is real:
        self.assert_is_real(c1dvcs)

        _MATHEMATICA_RESULT = 0.04673377354751275

        self.assert_approximately_equal(c1dvcs, expected = _MATHEMATICA_RESULT)

    def test_calculate_dvcs_s1_coefficient(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient s_{1}^{DVCS}.
        """
        s1dvcs = self.bkm_formalism.compute_dvcs_s1_coefficient()

        # (X): Verify that s_{1}^{DVCS} is a *finite* number:
        self.assert_is_finite(s1dvcs)
        
        # (X); Verify that s_{1}^{DVCS} is not a NaN:
        self.assert_no_nans(s1dvcs)

        # (X): Verify that s_{1}^{DVCS} is real:
        self.assert_is_real(s1dvcs)

        _MATHEMATICA_RESULT = 4.652736729956417e-16

        self.assert_approximately_equal(s1dvcs, expected = _MATHEMATICA_RESULT)