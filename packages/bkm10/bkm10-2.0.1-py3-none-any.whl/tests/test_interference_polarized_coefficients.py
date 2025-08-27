"""
## Description:
A testing suite for proving that the functions computing the coefficients for the
longitudinally-polarized target are returning real, finite, and accurate values.

## Notes:

1. 2025/07/24:
    - All tests pasted with current Mathematica values.
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
class TestPolarizedCoefficients(unittest.TestCase):
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
        
    def test_calculate_c_0_plus_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 0)$.
        We call it "CLPPP0" for C (series) LP (longitudinally-polarized [target]) PP (++) 0 (n = 0).
        """
        c0pp = self.bkm_formalism.calculate_c_0_plus_plus_longitudinally_polarized()

        # (X): Verify that C_{++}^{LP}(n = 0) is a *finite* number:
        self.assert_is_finite(c0pp)
        
        # (X); Verify that C_{++}^{LP}(n = 0) is not a NaN:
        self.assert_no_nans(c0pp)

        # (X): Verify that C_{++}^{LP}(n = 0) is real:
        self.assert_is_real(c0pp)

        _MATHEMATICA_RESULT = 0.057338590283762814

        self.assert_approximately_equal(c0pp, expected = _MATHEMATICA_RESULT)

    def test_calculate_c_0_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 0)$.
        We call it "CLPVPP0" for C (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 0 (n = 0).
        """
        c0ppv = self.bkm_formalism.calculate_c_0_plus_plus_longitudinally_polarized_v()

        # (X): Verify that C_{++}^{LP, V}(n = 0) is a *finite* number:
        self.assert_is_finite(c0ppv)
        
        # (X); Verify that C_{++}^{LP, V}(n = 0) is not a NaN:
        self.assert_no_nans(c0ppv)

        # (X): Verify that C_{++}^{LP, V}(n = 0) is real:
        self.assert_is_real(c0ppv)

        _MATHEMATICA_RESULT = -0.11083877974118175

        self.assert_approximately_equal(c0ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 0)$.
        We call it "CLPAPP0" for C (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 0 (n = 0).
        """
        c0ppa = self.bkm_formalism.calculate_c_0_plus_plus_longitudinally_polarized_a()

        # (X): Verify that C_{++}^{LP, A}(n = 0) is a *finite* number:
        self.assert_is_finite(c0ppa)
        
        # (X); Verify that C_{++}^{LP, A}(n = 0) is not a NaN:
        self.assert_no_nans(c0ppa)

        # (X): Verify that C_{++}^{LP, A}(n = 0) is real:
        self.assert_is_real(c0ppa)

        _MATHEMATICA_RESULT = -0.020719510401278708

        self.assert_approximately_equal(c0ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_plus_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 1)$.
        We call it "CLPPP1" for C (series) LP (longitudinally-polarized [target]) PP (++) 1 (n = 1).amples:
        None
        """
        c1pp = self.bkm_formalism.calculate_c_1_plus_plus_longitudinally_polarized()

        # (X): Verify that C_{++}^{LP}(n = 1) is a *finite* number:
        self.assert_is_finite(c1pp)
        
        # (X); Verify that C_{++}^{LP}(n = 1) is not a NaN:
        self.assert_no_nans(c1pp)

        # (X): Verify that C_{++}^{LP}(n = 1) is real:
        self.assert_is_real(c1pp)

        _MATHEMATICA_RESULT = -0.1423854729987041

        self.assert_approximately_equal(c1pp, expected = _MATHEMATICA_RESULT)

    def test_calculate_c_1_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 1)$.
        We call it "CLPVPP1" for C (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 1 (n = 1).
        """
        c1ppv = self.bkm_formalism.calculate_c_1_plus_plus_longitudinally_polarized_v()

        # (X): Verify that C_{++}^{LP, V}(n = 1) is a *finite* number:
        self.assert_is_finite(c1ppv)
        
        # (X); Verify that C_{++}^{LP, V}(n = 1) is not a NaN:
        self.assert_no_nans(c1ppv)

        # (X): Verify that C_{++}^{LP, V}(n = 1) is real:
        self.assert_is_real(c1ppv)

        _MATHEMATICA_RESULT = -0.03826898637315565

        self.assert_approximately_equal(c1ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP, A}(n = 1)$.
        We call it "CLPAPP1" for C (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 1 (n = 1).
        """
        c1ppa = self.bkm_formalism.calculate_c_1_plus_plus_longitudinally_polarized_a()

        # (X): Verify that C_{++}^{LP, A}(n = 1) is a *finite* number:
        self.assert_is_finite(c1ppa)
        
        # (X); Verify that C_{++}^{LP, A}(n = 1) is not a NaN:
        self.assert_no_nans(c1ppa)

        # (X): Verify that C_{++}^{LP, A}(n = 1) is real:
        self.assert_is_real(c1ppa)

        _MATHEMATICA_RESULT = -0.010009435464345648

        self.assert_approximately_equal(c1ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 2)$.
        We call it "CLPPP2" for C (series) LP (longitudinally-polarized [target]) PP (++) 2 (n = 2).
        """
        c2pp = self.bkm_formalism.calculate_c_2_plus_plus_longitudinally_polarized()

        # (X): Verify that C_{++}^{LP}(n = 2) is a *finite* number:
        self.assert_is_finite(c2pp)
        
        # (X); Verify that C_{++}^{LP}(n = 2) is not a NaN:
        self.assert_no_nans(c2pp)

        # (X): Verify that C_{++}^{LP}(n = 2) is real:
        self.assert_is_real(c2pp)

        _MATHEMATICA_RESULT = 0.0012220373655056997

        self.assert_approximately_equal(c2pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP}(n = 2)$.
        We call it "CLPVPP2" for C (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 2 (n = 2).
        """
        c2ppv = self.bkm_formalism.calculate_c_2_plus_plus_longitudinally_polarized_v()

        # (X): Verify that C_{++}^{LP, V}(n = 2) is a *finite* number:
        self.assert_is_finite(c2ppv)
        
        # (X); Verify that C_{++}^{LP, V}(n = 2) is not a NaN:
        self.assert_no_nans(c2ppv)

        # (X): Verify that C_{++}^{LP, V}(n = 2) is real:
        self.assert_is_real(c2ppv)

        _MATHEMATICA_RESULT = -0.0014399130108895203

        self.assert_approximately_equal(c2ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{LP, A}(n = 2)$.
        We call it "CLPAPP2" for C (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 2 (n = 2).
        """
        c2ppa = self.bkm_formalism.calculate_c_2_plus_plus_longitudinally_polarized_a()

        # (X): Verify that C_{++}^{LP, A}(n = 2) is a *finite* number:
        self.assert_is_finite(c2ppa)
        
        # (X); Verify that C_{++}^{LP, A}(n = 2) is not a NaN:
        self.assert_no_nans(c2ppa)

        # (X): Verify that C_{++}^{LP, A}(n = 2) is real:
        self.assert_is_real(c2ppa)

        _MATHEMATICA_RESULT = -0.00025947949074194774

        self.assert_approximately_equal(c2ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP}(n = 0)$.
        We call it "CLP0P0" for C (series) LP (longitudinally-polarized [target]) 0P (0+) 0 (n = 0).
        """
        c00p = self.bkm_formalism.calculate_c_0_zero_plus_longitudinally_polarized()

        # (X): Verify that C_{0+}^{LP}(n = 0) is a *finite* number:
        self.assert_is_finite(c00p)
        
        # (X); Verify that C_{0+}^{LP}(n = 0) is not a NaN:
        self.assert_no_nans(c00p)

        # (X): Verify that C_{0+}^{LP}(n = 0) is real:
        self.assert_is_real(c00p)

        _MATHEMATICA_RESULT = -0.006869758061985178

        self.assert_approximately_equal(c00p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP, V}(n = 0)$.
        We call it "CLPV0P0" for C (series) LP (longitudinally-polarized [target]) V (vector) 0P (0+) 0 (n = 0).
        """
        c00pv = self.bkm_formalism.calculate_c_0_zero_plus_longitudinally_polarized_v()

        # (X): Verify that C_{0+}^{LP, V}(n = 0) is a *finite* number:
        self.assert_is_finite(c00pv)
        
        # (X); Verify that C_{0+}^{LP, V}(n = 0) is not a NaN:
        self.assert_no_nans(c00pv)

        # (X): Verify that C_{0+}^{LP, V}(n = 0) is real:
        self.assert_is_real(c00pv)

        _MATHEMATICA_RESULT = -0.0038500841885851004

        self.assert_approximately_equal(c00pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP, A}(n = 0)$.
        We call it "CLPA0P0" for C (series) LP (longitudinally-polarized [target]) A (axial vector) 0P (0+) 0 (n = 0).
        """
        c00pa = self.bkm_formalism.calculate_c_0_zero_plus_longitudinally_polarized_a()

        # (X): Verify that C_{0+}^{LP, A}(n = 0) is a *finite* number:
        self.assert_is_finite(c00pa)
        
        # (X); Verify that C_{0+}^{LP, A}(n = 0) is not a NaN:
        self.assert_no_nans(c00pa)

        # (X): Verify that C_{0+}^{LP, A}(n = 0) is real:
        self.assert_is_real(c00pa)

        _MATHEMATICA_RESULT = 0.0032084034904875836

        self.assert_approximately_equal(c00pa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_zero_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP}(n = 1)$.
        We call it "CLP0P1" for C (series) LP (longitudinally-polarized [target]) 0P (0+) 0 (n = 1).
        """
        c10p = self.bkm_formalism.calculate_c_1_zero_plus_longitudinally_polarized()

        # (X): Verify that C_{0+}^{LP}(n = 1) is a *finite* number:
        self.assert_is_finite(c10p)
        
        # (X); Verify that C_{0+}^{LP}(n = 1) is not a NaN:
        self.assert_no_nans(c10p)

        # (X): Verify that C_{0+}^{LP}(n = 1) is real:
        self.assert_is_real(c10p)

        _MATHEMATICA_RESULT = -0.0007823645434023494

        self.assert_approximately_equal(c10p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_zero_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP, V}(n = 1)$.
        We call it "CLPV0P1" for C (series) LP (longitudinally-polarized [target]) V (vector) 0P (0+) 1 (n = 1).
        """
        c10pv = self.bkm_formalism.calculate_c_1_zero_plus_longitudinally_polarized_v()

        # (X): Verify that C_{0+}^{LP, V}(n = 1) is a *finite* number:
        self.assert_is_finite(c10pv)
        
        # (X); Verify that C_{0+}^{LP, V}(n = 1) is not a NaN:
        self.assert_no_nans(c10pv)

        # (X): Verify that C_{0+}^{LP, V}(n = 1) is real:
        self.assert_is_real(c10pv)

        _MATHEMATICA_RESULT = -0.002568110094701144

        self.assert_approximately_equal(c10pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP}(n = 2)$.
        We call it "CLP0P2" for C (series) LP (longitudinally-polarized [target]) 0P (0+) 2 (n = 2).
        """
        c20p = self.bkm_formalism.calculate_c_2_zero_plus_longitudinally_polarized()

        # (X): Verify that C_{0+}^{LP}(n = 2) is a *finite* number:
        self.assert_is_finite(c20p)
        
        # (X); Verify that C_{0+}^{LP}(n = 2) is not a NaN:
        self.assert_no_nans(c20p)

        # (X): Verify that C_{0+}^{LP}(n = 2) is real:
        self.assert_is_real(c20p)

        _MATHEMATICA_RESULT = -0.1078956119147084

        self.assert_approximately_equal(c20p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP, V}(n = 2)$.
        We call it "CLPV0P2" for C (series) LP (longitudinally-polarized [target]) V (vector) 0P (0+) 2 (n = 2).
        """
        c20pv = self.bkm_formalism.calculate_c_2_zero_plus_longitudinally_polarized_v()

        # (X): Verify that C_{0+}^{LP, V}(n = 2) is a *finite* number:
        self.assert_is_finite(c20pv)
        
        # (X); Verify that C_{0+}^{LP, V}(n = 2) is not a NaN:
        self.assert_no_nans(c20pv)

        # (X): Verify that C_{0+}^{LP, V}(n = 2) is real:
        self.assert_is_real(c20pv)

        _MATHEMATICA_RESULT = -0.006869758061985178

        self.assert_approximately_equal(c20pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{LP, A}(n = 2)$.
        We call it "CLPA0P2" for C (series) LP (longitudinally-polarized [target]) A (axial vector) 0P (0+) 2 (n = 2).
        """
        c20pa = self.bkm_formalism.calculate_c_2_zero_plus_longitudinally_polarized_a()

        # (X): Verify that C_{0+}^{LP, A}(n = 2) is a *finite* number:
        self.assert_is_finite(c20pa)
        
        # (X); Verify that C_{0+}^{LP, A}(n = 2) is not a NaN:
        self.assert_no_nans(c20pa)

        # (X): Verify that C_{0+}^{LP, A}(n = 2) is real:
        self.assert_is_real(c20pa)

        _MATHEMATICA_RESULT = -0.0032084034904875836

        self.assert_approximately_equal(c20pa, expected = _MATHEMATICA_RESULT)

    def test_calculate_s_1_plus_plus_lp(self):
        """
        ## Description: Test the function corresponding to the BKM10 coefficient called $S_{++}^{LP}(n = 1)$.
        We call it "SLPPP1" for S (series) LP (longitudinally-polarized [target]) PP (++) 1 (n = 1).
        """
        s1pp = self.bkm_formalism.calculate_s_1_plus_plus_longitudinally_polarized()

        # (X): Verify that S_{++}^{LP}(n = 1) is a *finite* number:
        self.assert_is_finite(s1pp)
        
        # (X); Verify that S_{++}^{LP}(n = 1) is not a NaN:
        self.assert_no_nans(s1pp)

        # (X): Verify that S_{++}^{LP}(n = 1) is real:
        self.assert_is_real(s1pp)

        _MATHEMATICA_RESULT = 0.3253161693376573

        self.assert_approximately_equal(s1pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, V}(n = 1)$.
        We call it "SLPVPP0" for S (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 1 (n = 1).
        """
        s1ppv = self.bkm_formalism.calculate_s_1_plus_plus_longitudinally_polarized_v()

        # (X): Verify that S_{++}^{LP, V}(n = 1) is a *finite* number:
        self.assert_is_finite(s1ppv)
        
        # (X); Verify that S_{++}^{LP, V}(n = 1) is not a NaN:
        self.assert_no_nans(s1ppv)

        # (X): Verify that S_{++}^{LP, V}(n = 1) is real:
        self.assert_is_real(s1ppv)

        _MATHEMATICA_RESULT = -0.05363324965763076

        self.assert_approximately_equal(s1ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, A}(n = 1)$.
        We call it "SLPAPP0" for S (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 1 (n = 1).
        """
        s1ppa = self.bkm_formalism.calculate_s_1_plus_plus_longitudinally_polarized_a()

        # (X): Verify that S_{++}^{LP, A}(n = 1) is a *finite* number:
        self.assert_is_finite(s1ppa)
        
        # (X); Verify that S_{++}^{LP, A}(n = 1) is not a NaN:
        self.assert_no_nans(s1ppa)

        # (X): Verify that S_{++}^{LP, A}(n = 1) is real:
        self.assert_is_real(s1ppa)

        _MATHEMATICA_RESULT = -0.01201485411255754

        self.assert_approximately_equal(s1ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP}(n = 2)$.
        We call it "SLPPP2" for S (series) LP (longitudinally-polarized [target]) PP (++) 2 (n = 2).
        """
        s2pp = self.bkm_formalism.calculate_s_2_plus_plus_longitudinally_polarized()

        # (X): Verify that S_{++}^{LP}(n = 2) is a *finite* number:
        self.assert_is_finite(s2pp)
        
        # (X); Verify that S_{++}^{LP}(n = 2) is not a NaN:
        self.assert_no_nans(s2pp)

        # (X): Verify that S_{++}^{LP}(n = 2) is real:
        self.assert_is_real(s2pp)

        _MATHEMATICA_RESULT = 0.0025135056852941154

        self.assert_approximately_equal(s2pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, V}(n = 2)$.
        We call it "SLPVP2" for S (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 2 (n = 2).
        """
        s2ppv = self.bkm_formalism.calculate_s_2_plus_plus_longitudinally_polarized_v()

        # (X): Verify that S_{++}^{LP, V}(n = 2) is a *finite* number:
        self.assert_is_finite(s2ppv)
        
        # (X); Verify that S_{++}^{LP, V}(n = 2) is not a NaN:
        self.assert_no_nans(s2ppv)

        # (X): Verify that S_{++}^{LP, V}(n = 2) is real:
        self.assert_is_real(s2ppv)

        _MATHEMATICA_RESULT = -0.0023426591075341226

        self.assert_approximately_equal(s2ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, A}(n = 2)$.
        We call it "SLPAPP2" for S (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 2 (n = 2).
        """
        s2ppa = self.bkm_formalism.calculate_s_2_plus_plus_longitudinally_polarized_a()

        # (X): Verify that S_{++}^{LP, A}(n = 2) is a *finite* number:
        self.assert_is_finite(s2ppa)
        
        # (X); Verify that S_{++}^{LP, A}(n = 2) is not a NaN:
        self.assert_no_nans(s2ppa)

        # (X): Verify that S_{++}^{LP, A}(n = 2) is real:
        self.assert_is_real(s2ppa)

        _MATHEMATICA_RESULT = -0.0023619336723292813

        self.assert_approximately_equal(s2ppa, expected = _MATHEMATICA_RESULT)

    def test_calculate_s_3_plus_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP}(n = 3)$.
        We call it "SLPPP3" for S (series) LP (longitudinally-polarized [target]) PP (++) 3 (n = 3).
        """
        s2pp = self.bkm_formalism.calculate_s_3_plus_plus_longitudinally_polarized()

        # (X): Verify that S_{++}^{LP}(n = 3) is a *finite* number:
        self.assert_is_finite(s2pp)
        
        # (X); Verify that S_{++}^{LP}(n = 3) is not a NaN:
        self.assert_no_nans(s2pp)

        # (X): Verify that S_{++}^{LP}(n = 3) is real:
        self.assert_is_real(s2pp)

        _MATHEMATICA_RESULT = 0.00013037936762590332

        self.assert_approximately_equal(s2pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_3_plus_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, V}(n = 3)$.
        We call it "SLPVP3" for S (series) LP (longitudinally-polarized [target]) V (vector) PP (++) 3 (n = 3).
        """
        s2ppv = self.bkm_formalism.calculate_s_3_plus_plus_longitudinally_polarized_v()

        # (X): Verify that S_{++}^{LP, V}(n = 3) is a *finite* number:
        self.assert_is_finite(s2ppv)
        
        # (X); Verify that S_{++}^{LP, V}(n = 3) is not a NaN:
        self.assert_no_nans(s2ppv)

        # (X): Verify that S_{++}^{LP, V}(n = 3) is real:
        self.assert_is_real(s2ppv)

        _MATHEMATICA_RESULT = 0.00009015949522840459

        self.assert_approximately_equal(s2ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_3_plus_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{LP, A}(n = 3)$.
        We call it "SLPAPP3" for S (series) LP (longitudinally-polarized [target]) A (axial vector) PP (++) 3 (n = 3).
        """
        s2ppa = self.bkm_formalism.calculate_s_3_plus_plus_longitudinally_polarized_a()

        # (X): Verify that S_{++}^{LP, A}(n = 3) is a *finite* number:
        self.assert_is_finite(s2ppa)
        
        # (X); Verify that S_{++}^{LP, A}(n = 3) is not a NaN:
        self.assert_no_nans(s2ppa)

        # (X): Verify that S_{++}^{LP, A}(n = 3) is real:
        self.assert_is_real(s2ppa)

        _MATHEMATICA_RESULT = -0.00007798120264796309

        self.assert_approximately_equal(s2ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP}(n = 1)$.
        We call it "SLP0P1" for S (series) LP (longitudinally-polarized [target]) 0P (0+) 1 (n = 1).
        """
        s10p = self.bkm_formalism.calculate_s_1_zero_plus_longitudinally_polarized()

        # (X): Verify that S_{0+}^{LP}(n = 1) is a *finite* number:
        self.assert_is_finite(s10p)
        
        # (X); Verify that S_{0+}^{LP}(n = 1) is not a NaN:
        self.assert_no_nans(s10p)

        # (X): Verify that S_{0+}^{LP}(n = 1) is real:
        self.assert_is_real(s10p)

        _MATHEMATICA_RESULT = -0.2519725231997644

        self.assert_approximately_equal(s10p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP, V}(n = 1)$.
        We call it "SLP0PV2" for S (series) LP (longitudinally-polarized [target]) V (vector) 0P (0+) 1 (n = 1).
        """
        s10pv = self.bkm_formalism.calculate_s_1_zero_plus_longitudinally_polarized_v()

        # (X): Verify that S_{0+}^{LP, V}(n = 1) is a *finite* number:
        self.assert_is_finite(s10pv)
        
        # (X); Verify that S_{0+}^{LP, V}(n = 1) is not a NaN:
        self.assert_no_nans(s10pv)

        # (X): Verify that S_{0+}^{LP, V}(n = 1) is real:
        self.assert_is_real(s10pv)

        _MATHEMATICA_RESULT = 0.3927132135828341

        self.assert_approximately_equal(s10pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP, A}(n = 1)$.
        We call it "SLP0PA2" for S (series) LP (longitudinally-polarized [target]) A (axial vector) 0P (0+) 1 (n = 1).
        """
        s10pa = self.bkm_formalism.calculate_s_1_zero_plus_longitudinally_polarized_a()

        # (X): Verify that S_{0+}^{LP, A}(n = 1) is a *finite* number:
        self.assert_is_finite(s10pa)
        
        # (X); Verify that S_{0+}^{LP, A}(n = 1) is not a NaN:
        self.assert_no_nans(s10pa)

        # (X): Verify that S_{0+}^{LP, A}(n = 1) is real:
        self.assert_is_real(s10pa)

        _MATHEMATICA_RESULT = 0.06950063146046895

        self.assert_approximately_equal(s10pa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_zero_plus_lp(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP}(n = 2)$.
        We call it "SLP0P2" for S (series) LP (longitudinally-polarized [target]) 0P (0+) 2 (n = 2).
        """
        s20p = self.bkm_formalism.calculate_s_2_zero_plus_longitudinally_polarized()

        # (X): Verify that S_{0+}^{LP}(n = 2) is a *finite* number:
        self.assert_is_finite(s20p)
        
        # (X); Verify that S_{0+}^{LP}(n = 2) is not a NaN:
        self.assert_no_nans(s20p)

        # (X): Verify that S_{0+}^{LP}(n = 2) is real:
        self.assert_is_real(s20p)

        _MATHEMATICA_RESULT = 0.2956829006254369

        self.assert_approximately_equal(s20p, expected = _MATHEMATICA_RESULT)

    def test_calculate_s_2_zero_plus_lp_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP, V}(n = 2)$.
        We call it "SLP0PV2" for S (series) LP (longitudinally-polarized [target]) V (vector) 0P (0+) 2 (n = 2).
        """
        s20pv = self.bkm_formalism.calculate_s_2_zero_plus_longitudinally_polarized_v()

        # (X): Verify that S_{0+}^{LP, V}(n = 2) is a *finite* number:
        self.assert_is_finite(s20pv)
        
        # (X); Verify that S_{0+}^{LP, V}(n = 2) is not a NaN:
        self.assert_no_nans(s20pv)

        # (X): Verify that S_{0+}^{LP, V}(n = 2) is real:
        self.assert_is_real(s20pv)

        _MATHEMATICA_RESULT = 0.018826252099746914

        self.assert_approximately_equal(s20pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_zero_plus_lp_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{LP, A}(n = 2)$.
        We call it "SLP0PA2" for S (series) LP (longitudinally-polarized [target]) A (axial vector) 0P (0+) 2 (n = 2).
        """
        s20pa = self.bkm_formalism.calculate_s_2_zero_plus_longitudinally_polarized_a()

        # (X): Verify that S_{0+}^{LP, A}(n = 2) is a *finite* number:
        self.assert_is_finite(s20pa)
        
        # (X); Verify that S_{0+}^{LP, A}(n = 2) is not a NaN:
        self.assert_no_nans(s20pa)

        # (X): Verify that S_{0+}^{LP, A}(n = 2) is real:
        self.assert_is_real(s20pa)

        _MATHEMATICA_RESULT = 0.00879248037625543

        self.assert_approximately_equal(s20pa, expected = _MATHEMATICA_RESULT)

if __name__ == "__main__":
    unittest.main()
