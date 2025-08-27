"""
## Description:
A testing suite for proving that the functions computing the coefficients for the unpolarized
target are returning real, finite, and accurate values.

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
class TestUnpolarizedCoefficients(unittest.TestCase):
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
        cls.target_polarization = 0.

        # (X): Specify the beam polarization *as a float*:
        cls.lepton_polarization = 0.0

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
            lepton_polarization = 1.0,
            target_polarization = 0.0,
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
        
    def test_calculate_c_0_plus_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 0)$.
        We call it "CunpPP0" for C (series) unp (unpolarized [target]) PP (++) 0 (n = 0).
        """
        c0pp = self.bkm_formalism.calculate_c_0_plus_plus_unpolarized()

        # (X): Verify that C_{++}^{unp}(n = 0) is a *finite* number:
        self.assert_is_finite(c0pp)
        
        # (X); Verify that C_{++}^{unp}(n = 0) is not a NaN:
        self.assert_no_nans(c0pp)

        # (X): Verify that C_{++}^{unp}(n = 0) is real:
        self.assert_is_real(c0pp)

        _MATHEMATICA_RESULT = 0.41930759273043816

        self.assert_approximately_equal(c0pp, expected = _MATHEMATICA_RESULT)

    def test_calculate_c_0_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 0)$.
        We call it "CunpVPP0" for C (series) unp (unpolarized [target]) V (vector) PP (++) 0 (n = 0).
        """
        c0ppv = self.bkm_formalism.calculate_c_0_plus_plus_unpolarized_v()

        # (X): Verify that C_{++}^{unp, V}(n = 0) is a *finite* number:
        self.assert_is_finite(c0ppv)
        
        # (X); Verify that C_{++}^{unp, V}(n = 0) is not a NaN:
        self.assert_no_nans(c0ppv)

        # (X): Verify that C_{++}^{unp, V}(n = 0) is real:
        self.assert_is_real(c0ppv)

        _MATHEMATICA_RESULT = -0.12251628051653782

        self.assert_approximately_equal(c0ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 0)$.
        We call it "CunpAPP0" for C (series) unp (unpolarized [target]) A (axial vector) PP (++) 0 (n = 0).
        """
        c0ppa = self.bkm_formalism.calculate_c_0_plus_plus_unpolarized_a()

        # (X): Verify that C_{++}^{unp, A}(n = 0) is a *finite* number:
        self.assert_is_finite(c0ppa)
        
        # (X); Verify that C_{++}^{unp, A}(n = 0) is not a NaN:
        self.assert_no_nans(c0ppa)

        # (X): Verify that C_{++}^{unp, A}(n = 0) is real:
        self.assert_is_real(c0ppa)

        _MATHEMATICA_RESULT = -0.6653497452048907

        self.assert_approximately_equal(c0ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_plus_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 1)$.
        We call it "CunpPP1" for C (series) unp (unpolarized [target]) PP (++) 1 (n = 1).amples:
        None
        """
        c1pp = self.bkm_formalism.calculate_c_1_plus_plus_unpolarized()

        # (X): Verify that C_{++}^{unp}(n = 1) is a *finite* number:
        self.assert_is_finite(c1pp)
        
        # (X); Verify that C_{++}^{unp}(n = 1) is not a NaN:
        self.assert_no_nans(c1pp)

        # (X): Verify that C_{++}^{unp}(n = 1) is real:
        self.assert_is_real(c1pp)

        _MATHEMATICA_RESULT = -0.4054747518042577

        self.assert_approximately_equal(c1pp, expected = _MATHEMATICA_RESULT)

    def test_calculate_c_1_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 1)$.
        We call it "CunpVPP1" for C (series) unp (unpolarized [target]) V (vector) PP (++) 1 (n = 1).
        """
        c1ppv = self.bkm_formalism.calculate_c_1_plus_plus_unpolarized_v()

        # (X): Verify that C_{++}^{unp, V}(n = 1) is a *finite* number:
        self.assert_is_finite(c1ppv)
        
        # (X); Verify that C_{++}^{unp, V}(n = 1) is not a NaN:
        self.assert_no_nans(c1ppv)

        # (X): Verify that C_{++}^{unp, V}(n = 1) is real:
        self.assert_is_real(c1ppv)

        _MATHEMATICA_RESULT = -0.06051421738686888

        self.assert_approximately_equal(c1ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp, A}(n = 1)$.
        We call it "CunpAPP1" for C (series) unp (unpolarized [target]) A (axial vector) PP (++) 1 (n = 1).
        """
        c1ppa = self.bkm_formalism.calculate_c_1_plus_plus_unpolarized_a()

        # (X): Verify that C_{++}^{unp, A}(n = 1) is a *finite* number:
        self.assert_is_finite(c1ppa)
        
        # (X); Verify that C_{++}^{unp, A}(n = 1) is not a NaN:
        self.assert_no_nans(c1ppa)

        # (X): Verify that C_{++}^{unp, A}(n = 1) is real:
        self.assert_is_real(c1ppa)

        _MATHEMATICA_RESULT = -0.18943390904546398

        self.assert_approximately_equal(c1ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 2)$.
        We call it "CunpPP2" for C (series) unp (unpolarized [target]) PP (++) 2 (n = 2).
        """
        c2pp = self.bkm_formalism.calculate_c_2_plus_plus_unpolarized()

        # (X): Verify that C_{++}^{unp}(n = 2) is a *finite* number:
        self.assert_is_finite(c2pp)
        
        # (X); Verify that C_{++}^{unp}(n = 2) is not a NaN:
        self.assert_no_nans(c2pp)

        # (X): Verify that C_{++}^{unp}(n = 2) is real:
        self.assert_is_real(c2pp)

        _MATHEMATICA_RESULT = 0.012752925202806235

        self.assert_approximately_equal(c2pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 2)$.
        We call it "CunpVPP2" for C (series) unp (unpolarized [target]) V (vector) PP (++) 2 (n = 2).
        """
        c2ppv = self.bkm_formalism.calculate_c_2_plus_plus_unpolarized_v()

        # (X): Verify that C_{++}^{unp, V}(n = 2) is a *finite* number:
        self.assert_is_finite(c2ppv)
        
        # (X); Verify that C_{++}^{unp, V}(n = 2) is not a NaN:
        self.assert_no_nans(c2ppv)

        # (X): Verify that C_{++}^{unp, V}(n = 2) is real:
        self.assert_is_real(c2ppv)

        _MATHEMATICA_RESULT = -0.00476937398971525

        self.assert_approximately_equal(c2ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp, A}(n = 2)$.
        We call it "CunpAPP2" for C (series) unp (unpolarized [target]) A (axial vector) PP (++) 2 (n = 2).
        """
        c2ppa = self.bkm_formalism.calculate_c_2_plus_plus_unpolarized_a()

        # (X): Verify that C_{++}^{unp, A}(n = 2) is a *finite* number:
        self.assert_is_finite(c2ppa)
        
        # (X); Verify that C_{++}^{unp, A}(n = 2) is not a NaN:
        self.assert_no_nans(c2ppa)

        # (X): Verify that C_{++}^{unp, A}(n = 2) is real:
        self.assert_is_real(c2ppa)

        _MATHEMATICA_RESULT = -0.005182877093365479

        self.assert_approximately_equal(c2ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_3_plus_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp}(n = 3)$.
        We call it "CunpPP3" for C (series) unp (unpolarized [target]) PP (++) 3 (n = 3).
        """
        c3pp = self.bkm_formalism.calculate_c_3_plus_plus_unpolarized()

        # (X): Verify that C_{++}^{unp}(n = 3) is a *finite* number:
        self.assert_is_finite(c3pp)
        
        # (X); Verify that C_{++}^{unp}(n = 3) is not a NaN:
        self.assert_no_nans(c3pp)

        # (X): Verify that C_{++}^{unp}(n = 3) is real:
        self.assert_is_real(c3pp)

        _MATHEMATICA_RESULT = 0.00028845009320500685

        self.assert_approximately_equal(c3pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_3_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp, V}(n = 3)$.
        We call it "CunpVPP3" for C (series) unp (unpolarized [target]) V (vector) PP (++) 3 (n = 3).
        """
        c3ppv = self.bkm_formalism.calculate_c_3_plus_plus_unpolarized_v()

        # (X): Verify that C_{++}^{unp, V}(n = 3) is a *finite* number:
        self.assert_is_finite(c3ppv)
        
        # (X); Verify that C_{++}^{unp, V}(n = 3) is not a NaN:
        self.assert_no_nans(c3ppv)

        # (X): Verify that C_{++}^{unp, V}(n = 3) is real:
        self.assert_is_real(c3ppv)

        _MATHEMATICA_RESULT = -0.00017252488320532806

        self.assert_approximately_equal(c3ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_3_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{++}^{unp, A}(n = 3)$.
        We call it "CunpAPP3" for C (series) unp (unpolarized [target]) A (axial vector) PP (++) 3 (n = 3).
        """
        c3ppa = self.bkm_formalism.calculate_c_3_plus_plus_unpolarized_a()

        # (X): Verify that C_{++}^{unp, A}(n = 3) is a *finite* number:
        self.assert_is_finite(c3ppa)
        
        # (X); Verify that C_{++}^{unp, A}(n = 3) is not a NaN:
        self.assert_no_nans(c3ppa)

        # (X): Verify that C_{++}^{unp, A}(n = 3) is real:
        self.assert_is_real(c3ppa)

        _MATHEMATICA_RESULT = 0.00019946802377942044

        self.assert_approximately_equal(c3ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp}(n = 0)$.
        We call it "Cunp0P0" for C (series) unp (unpolarized [target]) 0P (0+) 0 (n = 0).
        """
        c00p = self.bkm_formalism.calculate_c_0_zero_plus_unpolarized()

        # (X): Verify that C_{0+}^{unp}(n = 0) is a *finite* number:
        self.assert_is_finite(c00p)
        
        # (X); Verify that C_{0+}^{unp}(n = 0) is not a NaN:
        self.assert_no_nans(c00p)

        # (X): Verify that C_{0+}^{unp}(n = 0) is real:
        self.assert_is_real(c00p)

        _MATHEMATICA_RESULT = 0.21243317252244243

        self.assert_approximately_equal(c00p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, V}(n = 0)$.
        We call it "CunpV0P0" for C (series) unp (unpolarized [target]) V (vector) 0P (0+) 0 (n = 0).
        """
        c00pv = self.bkm_formalism.calculate_c_0_zero_plus_unpolarized_v()

        # (X): Verify that C_{0+}^{unp, V}(n = 0) is a *finite* number:
        self.assert_is_finite(c00pv)
        
        # (X); Verify that C_{0+}^{unp, V}(n = 0) is not a NaN:
        self.assert_no_nans(c00pv)

        # (X): Verify that C_{0+}^{unp, V}(n = 0) is real:
        self.assert_is_real(c00pv)

        _MATHEMATICA_RESULT = -0.05992954624455699

        self.assert_approximately_equal(c00pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_0_zero_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, A}(n = 0)$.
        We call it "CunpA0P0" for C (series) unp (unpolarized [target]) A (axial vector) 0P (0+) 0 (n = 0).
        """
        c00pa = self.bkm_formalism.calculate_c_0_zero_plus_unpolarized_a()

        # (X): Verify that C_{0+}^{unp, A}(n = 0) is a *finite* number:
        self.assert_is_finite(c00pa)
        
        # (X); Verify that C_{0+}^{unp, A}(n = 0) is not a NaN:
        self.assert_no_nans(c00pa)

        # (X): Verify that C_{0+}^{unp, A}(n = 0) is real:
        self.assert_is_real(c00pa)

        _MATHEMATICA_RESULT = -0.19946517626656324

        self.assert_approximately_equal(c00pa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_zero_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp}(n = 1)$.
        We call it "Cunp0P1" for C (series) unp (unpolarized [target]) 0P (0+) 0 (n = 1).
        """
        c10p = self.bkm_formalism.calculate_c_1_zero_plus_unpolarized()

        # (X): Verify that C_{0+}^{unp}(n = 1) is a *finite* number:
        self.assert_is_finite(c10p)
        
        # (X); Verify that C_{0+}^{unp}(n = 1) is not a NaN:
        self.assert_no_nans(c10p)

        # (X): Verify that C_{0+}^{unp}(n = 1) is real:
        self.assert_is_real(c10p)

        _MATHEMATICA_RESULT = 0.5951521249440364

        self.assert_approximately_equal(c10p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_zero_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, V}(n = 1)$.
        We call it "CunpV0P1" for C (series) unp (unpolarized [target]) V (vector) 0P (0+) 1 (n = 1).
        """
        c10pv = self.bkm_formalism.calculate_c_1_zero_plus_unpolarized_v()

        # (X): Verify that C_{0+}^{unp, V}(n = 1) is a *finite* number:
        self.assert_is_finite(c10pv)
        
        # (X); Verify that C_{0+}^{unp, V}(n = 1) is not a NaN:
        self.assert_no_nans(c10pv)

        # (X): Verify that C_{0+}^{unp, V}(n = 1) is real:
        self.assert_is_real(c10pv)

        _MATHEMATICA_RESULT = -0.1674768238263991

        self.assert_approximately_equal(c10pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_1_zero_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, A}(n = 1)$.
        We call it "CunpA0P1" for C (series) unp (unpolarized [target]) A (axial vector) 0P (0+) 1 (n = 1).
        """
        c10pa = self.bkm_formalism.calculate_c_1_zero_plus_unpolarized_a()

        # (X): Verify that C_{0+}^{unp, A}(n = 1) is a *finite* number:
        self.assert_is_finite(c10pa)
        
        # (X); Verify that C_{0+}^{unp, A}(n = 1) is not a NaN:
        self.assert_no_nans(c10pa)

        # (X): Verify that C_{0+}^{unp, A}(n = 1) is real:
        self.assert_is_real(c10pa)

        _MATHEMATICA_RESULT = -0.8807587542823425

        self.assert_approximately_equal(c10pa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp}(n = 2)$.
        We call it "Cunp0P2" for C (series) unp (unpolarized [target]) 0P (0+) 2 (n = 2).
        """
        c20p = self.bkm_formalism.calculate_c_2_zero_plus_unpolarized()

        # (X): Verify that C_{0+}^{unp}(n = 2) is a *finite* number:
        self.assert_is_finite(c20p)
        
        # (X); Verify that C_{0+}^{unp}(n = 2) is not a NaN:
        self.assert_no_nans(c20p)

        # (X): Verify that C_{0+}^{unp}(n = 2) is real:
        self.assert_is_real(c20p)

        _MATHEMATICA_RESULT = -0.6532897993773489

        self.assert_approximately_equal(c20p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, V}(n = 2)$.
        We call it "CunpV0P2" for C (series) unp (unpolarized [target]) V (vector) 0P (0+) 2 (n = 2).
        """
        c20pv = self.bkm_formalism.calculate_c_2_zero_plus_unpolarized_v()

        # (X): Verify that C_{0+}^{unp, V}(n = 2) is a *finite* number:
        self.assert_is_finite(c20pv)
        
        # (X); Verify that C_{0+}^{unp, V}(n = 2) is not a NaN:
        self.assert_no_nans(c20pv)

        # (X): Verify that C_{0+}^{unp, V}(n = 2) is real:
        self.assert_is_real(c20pv)

        _MATHEMATICA_RESULT = -0.019976515414852337

        self.assert_approximately_equal(c20pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_c_2_zero_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $C_{0+}^{unp, A}(n = 2)$.
        We call it "CunpA0P1" for C (series) unp (unpolarized [target]) A (axial vector) 0P (0+) 2 (n = 2).
        """
        c20pa = self.bkm_formalism.calculate_c_2_zero_plus_unpolarized_a()

        # (X): Verify that C_{0+}^{unp, A}(n = 2) is a *finite* number:
        self.assert_is_finite(c20pa)
        
        # (X); Verify that C_{0+}^{unp, A}(n = 2) is not a NaN:
        self.assert_no_nans(c20pa)

        # (X): Verify that C_{0+}^{unp, A}(n = 2) is real:
        self.assert_is_real(c20pa)

        _MATHEMATICA_RESULT = -0.04104505925226267

        self.assert_approximately_equal(c20pa, expected = _MATHEMATICA_RESULT)

    def test_calculate_s_1_plus_plus_unpolarized(self):
        """
        ## Description: Test the function corresponding to the BKM10 coefficient called $S_{++}^{unp}(n = 1)$.
        We call it "SunpPP1" for S (series) unp (unpolarized [target]) PP (++) 1 (n = 1).
        """
        s1pp = self.bkm_formalism.calculate_s_1_plus_plus_unpolarized()

        # (X): Verify that S_{++}^{unp}(n = 1) is a *finite* number:
        self.assert_is_finite(s1pp)
        
        # (X); Verify that S_{++}^{unp}(n = 1) is not a NaN:
        self.assert_no_nans(s1pp)

        # (X): Verify that S_{++}^{unp}(n = 1) is real:
        self.assert_is_real(s1pp)

        _MATHEMATICA_RESULT = 0.409671773905892

        self.assert_approximately_equal(s1pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{unp, V}(n = 1)$.
        We call it "SunpVPP0" for S (series) unp (unpolarized [target]) V (vector) PP (++) 1 (n = 1).
        """
        s1ppv = self.bkm_formalism.calculate_s_1_plus_plus_unpolarized_v()

        # (X): Verify that S_{++}^{unp, V}(n = 1) is a *finite* number:
        self.assert_is_finite(s1ppv)
        
        # (X); Verify that S_{++}^{unp, v}(n = 1) is not a NaN:
        self.assert_no_nans(s1ppv)

        # (X): Verify that S_{++}^{unp, V}(n = 1) is real:
        self.assert_is_real(s1ppv)

        _MATHEMATICA_RESULT = -0.00029050091110817124

        self.assert_approximately_equal(s1ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{unp, A}(n = 1)$.
        We call it "SunpAPP0" for S (series) unp (unpolarized [target]) A (axial vector) PP (++) 1 (n = 1).
        """
        s1ppa = self.bkm_formalism.calculate_s_1_plus_plus_unpolarized_a()

        # (X): Verify that S_{++}^{unp, A}(n = 1) is a *finite* number:
        self.assert_is_finite(s1ppa)
        
        # (X); Verify that S_{++}^{unp, A}(n = 1) is not a NaN:
        self.assert_no_nans(s1ppa)

        # (X): Verify that S_{++}^{unp, A}(n = 1) is real:
        self.assert_is_real(s1ppa)

        _MATHEMATICA_RESULT = -0.03884447591949268

        self.assert_approximately_equal(s1ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{unp}(n = 2)$.
        We call it "SunpPP2" for S (series) unp (unpolarized [target]) PP (++) 2 (n = 2).
        """
        s2pp = self.bkm_formalism.calculate_s_2_plus_plus_unpolarized()

        # (X): Verify that S_{++}^{unp}(n = 2) is a *finite* number:
        self.assert_is_finite(s2pp)
        
        # (X); Verify that S_{++}^{unp}(n = 2) is not a NaN:
        self.assert_no_nans(s2pp)

        # (X): Verify that S_{++}^{unp}(n = 2) is real:
        self.assert_is_real(s2pp)

        _MATHEMATICA_RESULT = 0.0027036240349894262

        self.assert_approximately_equal(s2pp, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{unp, V}(n = 2)$.
        We call it "SunpVP2" for S (series) unp (unpolarized [target]) V (vector) PP (++) 2 (n = 2).
        """
        s2ppv = self.bkm_formalism.calculate_s_2_plus_plus_unpolarized_v()

        # (X): Verify that S_{++}^{unp, V}(n = 2) is a *finite* number:
        self.assert_is_finite(s2ppv)
        
        # (X); Verify that S_{++}^{unp, v}(n = 2) is not a NaN:
        self.assert_no_nans(s2ppv)

        # (X): Verify that S_{++}^{unp, V}(n = 2) is real:
        self.assert_is_real(s2ppv)

        _MATHEMATICA_RESULT = -0.0005740699978240397

        self.assert_approximately_equal(s2ppv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_plus_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{++}^{unp, A}(n = 2)$.
        We call it "SunpAPP2" for S (series) unp (unpolarized [target]) A (axial vector) PP (++) 2 (n = 2).
        """
        s2ppa = self.bkm_formalism.calculate_s_2_plus_plus_unpolarized_a()

        # (X): Verify that S_{++}^{unp, A}(n = 2) is a *finite* number:
        self.assert_is_finite(s2ppa)
        
        # (X); Verify that S_{++}^{unp, A}(n = 2) is not a NaN:
        self.assert_no_nans(s2ppa)

        # (X): Verify that S_{++}^{unp, A}(n = 2) is real:
        self.assert_is_real(s2ppa)

        _MATHEMATICA_RESULT = -0.0031928305319066487

        self.assert_approximately_equal(s2ppa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp}(n = 1)$.
        We call it "Sunp0P1" for S (series) unp (unpolarized [target]) 0P (0+) 1 (n = 1).
        """
        s10p = self.bkm_formalism.calculate_s_1_zero_plus_unpolarized()

        # (X): Verify that S_{0+}^{unp}(n = 1) is a *finite* number:
        self.assert_is_finite(s10p)
        
        # (X); Verify that S_{0+}^{unp}(n = 1) is not a NaN:
        self.assert_no_nans(s10p)

        # (X): Verify that S_{0+}^{unp}(n = 1) is real:
        self.assert_is_real(s10p)

        _MATHEMATICA_RESULT = 0.05498776908654213

        self.assert_approximately_equal(s10p, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp, V}(n = 1)$.
        We call it "Sunp0PV2" for S (series) unp (unpolarized [target]) V (vector) 0P (0+) 1 (n = 1).
        """
        s10pv = self.bkm_formalism.calculate_s_1_zero_plus_unpolarized_v()

        # (X): Verify that S_{0+}^{unp, V}(n = 1) is a *finite* number:
        self.assert_is_finite(s10pv)
        
        # (X); Verify that S_{0+}^{unp, V}(n = 1) is not a NaN:
        self.assert_no_nans(s10pv)

        # (X): Verify that S_{0+}^{unp, V}(n = 1) is real:
        self.assert_is_real(s10pv)

        _MATHEMATICA_RESULT = -0.00426598684793811

        self.assert_approximately_equal(s10pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_1_zero_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp, A}(n = 1)$.
        We call it "Sunp0PA2" for S (series) unp (unpolarized [target]) A (axial vector) 0P (0+) 1 (n = 1).
        """
        s10pa = self.bkm_formalism.calculate_s_1_zero_plus_unpolarized_a()

        # (X): Verify that S_{0+}^{unp, A}(n = 1) is a *finite* number:
        self.assert_is_finite(s10pa)
        
        # (X); Verify that S_{0+}^{unp, A}(n = 1) is not a NaN:
        self.assert_no_nans(s10pa)

        # (X): Verify that S_{0+}^{unp, A}(n = 1) is real:
        self.assert_is_real(s10pa)

        _MATHEMATICA_RESULT = 0.0008508303918169414

        self.assert_approximately_equal(s10pa, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_zero_plus_unpolarized(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp}(n = 2)$.
        We call it "Sunp0P2" for S (series) unp (unpolarized [target]) 0P (0+) 2 (n = 2).
        """
        s20p = self.bkm_formalism.calculate_s_2_zero_plus_unpolarized()

        # (X): Verify that S_{0+}^{unp}(n = 2) is a *finite* number:
        self.assert_is_finite(s20p)
        
        # (X); Verify that S_{0+}^{unp}(n = 2) is not a NaN:
        self.assert_no_nans(s20p)

        # (X): Verify that S_{0+}^{unp}(n = 2) is real:
        self.assert_is_real(s20p)

        _MATHEMATICA_RESULT = 0.23838748372787139

        self.assert_approximately_equal(s20p, expected = _MATHEMATICA_RESULT)

    def test_calculate_s_2_zero_plus_unpolarized_V(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp, V}(n = 2)$.
        We call it "Sunp0PV2" for S (series) unp (unpolarized [target]) V (vector) 0P (0+) 2 (n = 2).
        """
        s20pv = self.bkm_formalism.calculate_s_2_zero_plus_unpolarized_v()

        # (X): Verify that S_{0+}^{unp, V}(n = 2) is a *finite* number:
        self.assert_is_finite(s20pv)
        
        # (X); Verify that S_{0+}^{unp, V}(n = 2) is not a NaN:
        self.assert_no_nans(s20pv)

        # (X): Verify that S_{0+}^{unp, V}(n = 2) is real:
        self.assert_is_real(s20pv)

        _MATHEMATICA_RESULT = 0.007289492730387789

        self.assert_approximately_equal(s20pv, expected = _MATHEMATICA_RESULT)
        
    def test_calculate_s_2_zero_plus_unpolarized_A(self):
        """
        ## Description: Test the function that corresponds to the BKM10 coefficient called $S_{0+}^{unp, A}(n = 2)$.
        We call it "Sunp0PA2" for S (series) unp (unpolarized [target]) A (axial vector) 0P (0+) 2 (n = 2).
        """
        s20pa = self.bkm_formalism.calculate_s_2_zero_plus_unpolarized_a()

        # (X): Verify that S_{0+}^{unp, A}(n = 2) is a *finite* number:
        self.assert_is_finite(s20pa)
        
        # (X); Verify that S_{0+}^{unp, A}(n = 2) is not a NaN:
        self.assert_no_nans(s20pa)

        # (X): Verify that S_{0+}^{unp, A}(n = 2) is real:
        self.assert_is_real(s20pa)

        _MATHEMATICA_RESULT = 0.01388732444214517

        self.assert_approximately_equal(s20pa, expected = _MATHEMATICA_RESULT)

if __name__ == "__main__":
    unittest.main()
