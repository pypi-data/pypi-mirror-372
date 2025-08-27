"""
Entry point for the `BKM10Formalism`.
"""

# 3rd Party Library | NumPy:
import numpy as np

from bkm10_lib import backend

from bkm10_lib.inputs import BKM10Inputs

from bkm10_lib.cff_inputs import CFFInputs

from bkm10_lib.constants import _MASS_OF_PROTON_IN_GEV

from bkm10_lib.constants import _MASS_OF_PROTON_SQUARED_IN_GEV_SQUARED

from bkm10_lib.constants import _ELECTRIC_FORM_FACTOR_CONSTANT

from bkm10_lib.constants import  _PROTON_MAGNETIC_MOMENT

from bkm10_lib.constants import _ELECTROMAGNETIC_FINE_STRUCTURE_CONSTANT

class BKMFormalism:
    """
    Welcome to the `BKMFormalism` class!

    ## Description:
    This class enables one to compute all the relevant (sub-)quantities that go into
    calculation of the four-fold differential cross-section that describes the DVCS 
    process. At the moment, we are only evaluating the cross-section according to the
    "BKM10" formalism in contrast to the "BKM02" formalism. In the future, we aim
    to implement the option to use the BKM02 formalism through the parameter `formalism_version`.

    ## Detailed Description:
    Do you need more detail? If so, let the developers know!
    
    ## Notes:
    In order to use this class, one must use the datatypes `BKM10Inputs` and `CFFInputs`. 
    These are "independent variables" that go into (numerical) evaluation of the cross-
    section.
    """

    @property
    def math(self):
        """
        ## Description:
        If you intend to use this library with TensorFlow, you cannot use NumPy array operations nicely. Instead,
        you have to go through the pain of making normal floats like `5.0` entire TensorFlow constants. Thanks, Obama.
        So, depending on how a user is using the library, we inform the "backend" setting to use either NumPy or
        TensorFlow.
        """
        return backend.math

    def __init__(
            self,
            inputs: BKM10Inputs,
            cff_values: CFFInputs,
            lepton_polarization: float,
            target_polarization: float,
            using_ww: bool = False,
            bh_on: bool = True,
            dvcs_on: bool = True,
            interference_on: bool = True,
            formalism_version: str = "10",
            verbose: bool = False,
            debugging: bool = False):
        """
        ## Description:
        Initialize the `BKMFormalism` class!

        :param BKM10Inputs inputs:
            Kinematic inputs, usually Q^{2}, x_{B}, and t.

        :param CFFInputs cff_values:
            Compton Form factor setting

        :param float lepton_polarization:
            The BKM10 formalism uses +1.0, 0.0, or -1.0. Nothing else!

        :param float target_polarization:
            The BKM10 formalism uses +0.5, 0.0, or -0.5. Nothing else!

        :param bool using_ww:
            The "WW" relations are a mathematical approximation that you may choose 
            to use or not. Make sure you know what this does (physically)!

        :param bool bh_on:
            `True` to keep the|BH|^{2} term in the computation; `False` otherwise.

        :param bool dvcs_on:
            `True` to keep the |DVCS|^{2} term in the computation; `False` otherwise.

        :param bool interference_on:
            `True` to keep the I(nterference) term in the computation; `False` otherwise.
        
        :param str formalism_version:
            Default is "10." Currently, this parameter has NO EFFECT! Read the 
            description of the class to learn why.

        :param bool verbose:
            A parameter that enables frequent print statements that show you "where" 
            the code is and some of the outputs.

        :param bool debugging:
            A parameter that will print virtually EVERYTHING! Careful!
        """

        # (X): Collect the inputs:
        self.kinematics = inputs

        # (X): Obtain the BKM formalism version (either 10 or 02):
        self.fomalism_version = formalism_version

        # (X): Obtain the value of the lepton polarization:
        self.lepton_polarization = lepton_polarization

        # (X): Obtain the value of the hadron polarization:
        self.target_polarization = target_polarization

        # (X): Obtain the CFF values:
        self.cff_values = cff_values

        # (X): Do we turn the BH^{2} contribution on?
        self.bh_on = bh_on

        # (X): Do we turn the DVCS^{2} contribution on?
        self.dvcs_on = dvcs_on

        # (X): Do we turn the interference contribution on?
        self.interference_on = interference_on
        
        # (X): Are we using the WW relations for the CFFs?
        self.using_ww = using_ww

        # (X): Define a verbose parameter:
        self.verbose = verbose

        # (X): Define a debugging parameter: DO NOT USE THIS!
        self.debugging = debugging

        # (X): Derived Quantity | self.epsilon:
        self.epsilon = self._calculate_epsilon()

        # (X): Derived Quantity | y:
        self.lepton_energy_fraction = self._calculate_lepton_energy_fraction()

        # (X): Derived Quantity | xi:
        self.skewness_parameter = self._calculate_skewness_parameter()

        # (X): Derived Quantity | t_minimum:
        self.t_minimum = self._calculate_t_minimum()

        # (X): Derived Quantity | t':
        self.t_prime = self._calculate_t_prime()

        # (X): Derived Quantity | K_tilde:
        self.k_tilde = self._calculate_k_tilde()

        # (X): Derived Quantity | K:
        self.kinematic_k = self._calculate_k()

        # (X): Derived Form Factor | Electric Form Factor F_{E}:
        self.electric_form_factor = self._calculate_electric_form_factor()

        # (X): Derived Form Factor | Magnetic Form Factor F_{G}:
        self.magnetic_form_factor = self._calculate_magnetic_form_factor()

        # (X): Derived Form Factor | Electric Form Factor F_{2}:
        self.pauli_form_factor = self._calculate_pauli_form_factor()

        # (X): Derived Form Factor | Electric Form Factor F_{1}:
        self.dirac_form_factor = self._calculate_dirac_form_factor()

        # (X): Obtain the effective CFFs:
        self.effective_cff_values = self.compute_cff_effective(self.cff_values)

    def _calculate_epsilon(self) -> float:
        """
        ## Description
        Calculate self.epsilon, which is just a ratio of kinematic quantities:
        epsilon := 2 * m_{p} * x_{B} / Q

        ## Parameters:
        squared_Q_momentum_transfer: (float)
            kinematic momentum transfer to the hadron. 

        x_Bjorken: (float)
            kinematic Bjorken X

        verbose: (bool)
            Debugging console output.
        
        ## Notes:
        None!

        ## Examples:
        None!
        """
        try:

            # (1): Calculate self.epsilon right away:
            epsilon = (2. * self.kinematics.x_Bjorken * _MASS_OF_PROTON_IN_GEV) / self.math.sqrt(self.kinematics.squared_Q_momentum_transfer)

            # (1.1): If verbose, print the result:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated epsilon to be: {epsilon}")

            # (2): Return self.epsilon:
            return epsilon
        
        except Exception as ERROR:
            print(f"> Error in computing kinematic self.epsilon:\n> {ERROR}")
            return 0.0
        
    def _calculate_lepton_energy_fraction(self) -> float:
        """
        ## Description:
        Calculate y, which measures the lepton energy fraction.
        y^{2} := \frac{ \sqrt{Q^{2}} }{ \sqrt{\self.epsilon^{2}} k }

        ## Parameters:
        epsilon : (float)
            derived kinematics

        squared_Q_momentum_transfer: (float)
            Q^{2} momentum transfer to the hadron

        kinematics_k: (float)
            lepton momentum loss

        verbose: (bool)
            Debugging console output.

        ## Notes:
        """
        try:

            # (1): Calculate the y right away:
            lepton_energy_fraction = self.math.sqrt(self.kinematics.squared_Q_momentum_transfer) / (self.epsilon * self.kinematics.lab_kinematics_k)

            # (1.1): If verbose output, then print the result:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated y to be: {lepton_energy_fraction}")

            # (2): Return the calculation:
            return lepton_energy_fraction
        
        except Exception as ERROR:
            print(f"> Error in computing lepton_energy_fraction:\n> {ERROR}")
            return 0.

    def _calculate_skewness_parameter(self) -> float:
        """
        ## Description
        Calculate the Skewness Parameter
        x_{i} = x_{B} * (1 + \frac{ t Q^{2} }{ 2 } ) ... HUGE THING

        ## Parameters
        squared_Q_momentum_transfer: (float)
            kinematic momentum transfer to the hadron

        x_Bjorken: (float)
            kinematic Bjorken X

        verbose: (bool)
            Debugging console output.
        
        ## Notes:
        """
        try:

            # (1): The Numerator:
            numerator = (1. + (self.kinematics.squared_hadronic_momentum_transfer_t / (2. * self.kinematics.squared_Q_momentum_transfer)))

            # (2): The Denominator:
            denominator = (2. - self.kinematics.x_Bjorken + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (3): Calculate the Skewness Parameter:
            skewness_parameter = self.kinematics.x_Bjorken * numerator / denominator

            # (3.1): If verbose, print the output:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated skewness xi to be: {skewness_parameter}")

            # (4): Return Xi:
            return skewness_parameter

        except Exception as ERROR:
            print(f"> Error in computing skewness xi:\n> {ERROR}")
            return 0.
        
    def _calculate_t_minimum(self) -> float:
        """
        ## Description:
        Calculate t_{min}.

        ## Parameters:
        epsilon : (float)

        ## Returns:
        t_minimum : (float)
            t_minimum

        ## Notes:
        None!
        """

        try:

            # (1): Calculate 1 - x_{B}:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (2): Calculate the numerator:
            numerator = (2. * one_minus_xb * (1. - self.math.sqrt(1. + self.epsilon**2))) + self.epsilon**2

            # (3): Calculate the denominator:
            denominator = (4. * self.kinematics.x_Bjorken * one_minus_xb) + self.epsilon**2

            # (4): Obtain the t minimum
            t_minimum = -1. * self.kinematics.squared_Q_momentum_transfer * numerator / denominator

            # (4.1): If verbose, print the result:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated t_minimum to be: {t_minimum}")

            # (5): Print the result:
            return t_minimum

        except Exception as ERROR:
            print(f"> Error calculating t_minimum:\n> {ERROR}")
            return 0.    
    
    def _calculate_t_prime(self) -> float:
        """
        ## Description:
        Calculate t prime.

        ## Parameters:
        squared_hadronic_momentum_transfer_t: (float)

        squared_hadronic_momentum_transfer_t_minimum: (float)

        verbose: (float)

        ## Returns:
        self.t_prime: (float)

        ## Notes:
        None!
        """
        try:

            # (1): Obtain the self.t_prime immediately
            t_prime = self.kinematics.squared_hadronic_momentum_transfer_t - self.t_minimum

            # (1.1): If verbose, print the result:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated t prime to be: {t_prime}")

            # (2): Return self.t_prime
            return t_prime

        except Exception as ERROR:
            print(f"> Error calculating t_prime:\n> {ERROR}")
            return 0.
        
    def _calculate_k_tilde(self) -> float:
        """
        ## Description:
        Calculate K-tilde.
        
        ## Parameters:
        epsilon : (float)

        squared_Q_momentum_transfer: (float)

        x_Bjorken: (float)

        lepton_energy_fraction: (float)

        squared_hadronic_momentum_transfer_t: (float)

        squared_hadronic_momentum_transfer_t_minimum: (float)

        verbose: (bool)
            Debugging console output.

        ## Returns:
        k_tilde : (float)
            result of the operation
        
        ## Notes:
        """
        try:

            # (1): Calculate recurring quantity t_{min} - t
            tmin_minus_t = self.t_minimum - self.kinematics.squared_hadronic_momentum_transfer_t

            # (2): Calculate the duplicate quantity 1 - x_{B}
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (3): Calculate the crazy root quantity:
            second_root_quantity = (one_minus_xb * self.math.sqrt((1. + self.epsilon**2))) + ((tmin_minus_t * (self.epsilon**2 + (4. * one_minus_xb * self.kinematics.x_Bjorken))) / (4. * self.kinematics.squared_Q_momentum_transfer))
            
            # (6): Calculate K_tilde
            k_tilde = self.math.sqrt(tmin_minus_t) * self.math.sqrt(second_root_quantity)

            # (6.1): Print the result of the calculation:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated k_tilde to be: {k_tilde}")

            # (7) Return:
            return k_tilde

        except Exception as ERROR:
            print(f"> Error in calculating K_tilde:\n> {ERROR}")
            return 0.
        
    def _calculate_k(self) -> float:
        """
        ## Description:
        Calculate K. (Capital K, not lower-case k, which refers to the lepton
        beam energy.)
        """
        try:

            # (1): Calculate the amazing prefactor:
            prefactor = self.math.sqrt((1. - self.lepton_energy_fraction + (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)) / self.kinematics.squared_Q_momentum_transfer)

            # (2): Calculate the remaining part of the term:
            kinematic_k = prefactor * self.k_tilde

            # (2.1); If verbose, log the output:
            if self.verbose:
                print(f"> [VERBOSE]: Calculated kinematic K to be: {kinematic_k}")

            # (3): Return the value:
            return kinematic_k

        except Exception as ERROR:
            print(f"> Error in calculating derived kinematic K:\n> {ERROR}")
            return 0.

    def _calculate_electric_form_factor(self) -> float:
        """
        ## Description:
        The Electric Form Factor is quite mysterious still...

        ## Parameters:
        squared_hadronic_momentum_transfer_t: (float)

        verbose: (bool)
            Debugging console output.

        ## Returns:
        form_factor_electric : (float)
            result of the operation
        
        ## Notes:
        None!
        """
        
        try:
            
            # (1): Calculate the mysterious denominator:
            denominator = 1. - (self.kinematics.squared_hadronic_momentum_transfer_t / _ELECTRIC_FORM_FACTOR_CONSTANT)

            # (2): Calculate the F_{E}:
            form_factor_electric = 1. / (denominator**2)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                print(f"> [VERBOSE]: Successfully calculated electric form factor: {form_factor_electric}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated electric form factor as: {form_factor_electric}")

            return form_factor_electric

        except Exception as ERROR:
            print(f"> Error in calculating electric form factor:\n> {ERROR}")
            self.electric_form_factor = 0.

    def _calculate_magnetic_form_factor(self) -> float:
        """
        Description
        --------------
        The Magnetic Form Factor is calculated immediately with
        the Electric Form Factor. They are only related by the 
        gyromagnetic ratio.

        Parameters
        --------------
        electric_form_factor: (float)

        verbose: (bool)
            Debugging console output.

        Returns
        --------------
        form_factor_magnetic : (float)
            result of the operation
        
        Notes
        --------------
        """
        
        try:

            # (1): Calculate the F_{M}:
            form_factor_magnetic = _PROTON_MAGNETIC_MOMENT * self.electric_form_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                print(f"> [VERBOSE]: Successfully calculated magnetic form factor: {form_factor_magnetic}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated magnetic form factor as: {form_factor_magnetic}")

            return form_factor_magnetic

        except Exception as ERROR:
            print(f"> Error in calculating magnetic form factor:\n> {ERROR}")
            return 0.
        
    def _calculate_pauli_form_factor(self) -> float:
        """
        Description
        --------------
        We calculate the Pauli form factor, which is just a
        particular linear combination of the electromagnetic
        form factors.

        Parameters
        --------------
        squared_hadronic_momentum_transfer_t: (float)

        electric_form_factor: (float)

        magnetic_form_factor: (float)

        verbose: (bool)
            Debugging console output.

        Returns
        --------------
        pauli_form_factor : (float)
            result of the operation
        
        Notes
        --------------
        """
        
        try:

            # (1): Calculate tau:
            tau = -1. * self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2)

            # (2): Calculate the numerator:
            numerator = self.magnetic_form_factor - self.electric_form_factor

            # (3): Calculate the denominator:
            denominator = 1. + tau
        
            # (4): Calculate the Pauli form factor:
            pauli_form_factor = numerator / denominator

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                print(f"> [VERBOSE]: Successfully calculated Fermi form factor: {pauli_form_factor}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated Fermi form factor as: {pauli_form_factor}")

            return pauli_form_factor

        except Exception as ERROR:
            print(f"> Error in calculating Fermi form factor:\n> {ERROR}")
            return 0.

    def _calculate_dirac_form_factor(self) -> float:
        """
        Description
        --------------
        We calculate the Dirac form factor, which is
        even easier to get than the Fermi one.

        Parameters
        --------------
        magnetic_form_factor: (float)

        pauli_f2_form_factor: (float)

        verbose: (bool)
            Debugging console output.

        Returns
        --------------
        form_factor_magnetic : (float)
            result of the operation
        
        Notes
        --------------
        """
        
        try:
        
            # (1): Calculate the Dirac form factor:
            dirac_form_factor = self.magnetic_form_factor - self.pauli_form_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                print(f"> [VERBOSE]: Successfully calculated Dirac form factor: {dirac_form_factor}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated Dirac form factor as: {dirac_form_factor}")

            return dirac_form_factor

        except Exception as ERROR:
            print(f"> Error in calculating Dirac form factor:\n> {ERROR}")
            return 0.

    def compute_cff_effective(self, compton_form_factor: CFFInputs) -> CFFInputs:
        """
        ## Description:
        The CFF_{effective} is not actually easy to compute, but
        we are going to pretend it is and compute it as below. (All
        it needs is the skewness parameter.)

        ## Arguments:

            skewness_parameter: (float)

            compton_form_factor: (CFFInputs)

            verbose: (bool)
                Debugging console output.

        ## Returns:

            cff_effective : (CFFInputs)
                the effective CFF
        
        ## Notes:
        """
        def effective_cff_factor(cff):
            """
            ## Description:
            Dynamically comptute the effective CFFs giving attention
            to the datatypes. We required this modification to handle the case
            in which TF is used: There, something like `1.0 * cff` would throw
            a fit.
            """

            # (X): Determine the right datatype representaton to use for the float `1.0`:
            scalar_one = self.math.promote_scalar_to_dtype(1.0, cff)

            # (X): Determine the right datatype representaton to use for the float `2.0`:
            scalar_two = self.math.promote_scalar_to_dtype(2.0, cff)

            # (X): Determine the right datatype representaton to use for the thing called `cff`:
            skewness = self.math.promote_scalar_to_dtype(self.skewness_parameter, cff)

            # (X): Due to the structure of the prefactor, we require computation of the nice/unambiguous datatypes first:
            denominator = scalar_one + skewness

            # (X): If the WW relations are on...
            if self.using_ww:

                # (X): ...then return the coreect factor to the CFFs:
                return scalar_two * cff / denominator
            
            # (X): If the WW relations are off...
            else:
                
                # (X): ...then return a different factor:
                return -scalar_two * skewness * cff / denominator

        try:

            # (X): We now require *recasting* the effective CFFs into the CFFInputs dataclass:
            effective_cffs = CFFInputs(
                compton_form_factor_h       = effective_cff_factor(compton_form_factor.compton_form_factor_h),
                compton_form_factor_e       = effective_cff_factor(compton_form_factor.compton_form_factor_e),
                compton_form_factor_h_tilde = effective_cff_factor(compton_form_factor.compton_form_factor_h_tilde),
                compton_form_factor_e_tilde = effective_cff_factor(compton_form_factor.compton_form_factor_e_tilde)
            )
            
            if self.verbose:
                print("> [VERBOSE]: Computed effective CFFs using", "WW approximation" if self.using_ww else "non-WW expression")

            if self.debugging:
                print("> [DEBUGGING]: Computed effective CFFs using", f"WW approximation:\n{effective_cffs}" if self.using_ww else f"non-WW expression:\n{effective_cffs}")

            # (2): Return the output:
            return effective_cffs

        except Exception as ERROR:
            print(f"> Error in calculating F_effective:\n> {ERROR}")
            return 0.
    
    def compute_cross_section_prefactor(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the numerator of the prefactor
            numerator = _ELECTROMAGNETIC_FINE_STRUCTURE_CONSTANT**3 * self.lepton_energy_fraction**2 * self.kinematics.x_Bjorken

            # (2): Calculate the denominator of the prefactor:
            denominator = 8. * self.math.pi * self.kinematics.squared_Q_momentum_transfer**2 * self.math.sqrt(1. + self.epsilon**2)

            # (3): Construct the prefactor:
            prefactor = numerator / denominator

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                print(f"> Successfully BKM10 cross-section prefactor.")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated BKM10 cross-section prefactor to be:\n{prefactor}")

            # (4): Return the prefactor:
            return prefactor

        except Exception as ERROR:
            print(f"> Error calculating BKM10 cross section prefactor:\n> {ERROR}")
            return 0.
        
    def calculate_k_dot_delta(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        Equation (29) in the BKM Formalism, available
        at this link: https://arxiv.org/pdf/hep-ph/0112108.pdf

        ## Parameters:
        kinematic_k: (float)
        
        epsilon : (float)

        kinematics.squared_Q_momentum_transfer: (float)

        kinematics.x_Bjorken: (float)

        lepton_energy_fraction: (float)

        kinematics.squared_hadronic_momentum_transfer_t: (float)

        azimuthal_phi: (float)

        verbose: (bool)
            Debugging console output.

        ## Returns:
        k_dot_delta_result : (float)
            result of the operation
        
        ## Notes:
        (1): k-dot-delta shows up in computing the lepton
            propagators. It is Eq. (29) in the following
            paper: https://arxiv.org/pdf/hep-ph/0112108.pdf
        """
        try:
        
            # (1): The prefactor: \frac{Q^{2}}{2 y (1 + \varself.epsilon^{2})}
            prefactor = self.kinematics.squared_Q_momentum_transfer / (2. * self.lepton_energy_fraction * (1. + self.epsilon**2))

            # (2): Second term in parentheses: Phi-Dependent Term: 2 K self.math.cos(\phi)
            phi_dependence = 2. * self.kinematic_k * self.math.cos(phi_values)
            
            # (3): Prefactor of third term in parentheses: \frac{t}{Q^{2}}
            ratio_delta_to_q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (4): Second term in the third term's parentheses: x_{B} (2 - y)
            bjorken_scaling = self.kinematics.x_Bjorken * (2. - self.lepton_energy_fraction)

            # (5): Third term in the third term's parentheses: \frac{y \varself.epsilon^{2}}{2}
            ratio_y_epsilon = self.lepton_energy_fraction * self.epsilon**2 / 2.

            # (6): Adding up all the "correction" pieces to the prefactor, written as (1 + correction)
            correction = phi_dependence - (ratio_delta_to_q_squared * (1. - bjorken_scaling + ratio_y_epsilon)) + (ratio_y_epsilon)

            # (7): Writing it explicitly as "1 + correction"
            in_parentheses = 1. + correction

            # (8): The actual equation:
            k_dot_delta_result = -1. * prefactor * in_parentheses

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(k_dot_delta_result, list) or isinstance(k_dot_delta_result, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated k_dot_delta_result: {k_dot_delta_result[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated k_dot_delta_result: {k_dot_delta_result}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated k dot delta: {k_dot_delta_result}")

            # (9): Return the number:
            return k_dot_delta_result
        
        except Exception as E:
            print(f"> Error in calculating k.Delta:\n> {E}")
            return 0.
    
    def calculate_lepton_propagator_p1(self, phi_values: np.ndarray) -> np.ndarray:
        """
        Description
        --------------
        Equation (28) [first equation] divided through by
        Q^{2} according to the following paper:
        https://arxiv.org/pdf/hep-ph/0112108.pdf

        Parameters
        --------------
        k_dot_delta: (float)

        squared_Q_momentum_transfer: (float)

        verbose: (bool)
            Debugging console output.

        Notes
        --------------
        """
        try:
            p1_propagator = 1. + (2. * (self.calculate_k_dot_delta(phi_values) / self.kinematics.squared_Q_momentum_transfer))
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(p1_propagator, list) or isinstance(p1_propagator, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated p1 propagator: {p1_propagator[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated p1 propagator: {p1_propagator}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> Computed the P1 propagator to be:\n{p1_propagator}")

            return p1_propagator
        
        except Exception as E:
            print(f"> Error in computing p1 propagator:\n> {E}")
            return 0.
        
    def calculate_lepton_propagator_p2(self, phi_values: np.ndarray) -> np.ndarray:
        """
        Description
        --------------
        Equation (28) [second equation] divided through by
        Q^{2} according to the following paper:
        https://arxiv.org/pdf/hep-ph/0112108.pdf

        Parameters
        --------------
        k_dot_delta: (float)

        squared_Q_momentum_transfer: (float)

        verbose: (bool)
            Debugging console output.

        Notes
        --------------
        """
        try:
            p2_propagator = (-2. * (self.calculate_k_dot_delta(phi_values) / self.kinematics.squared_Q_momentum_transfer)) + (self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(p2_propagator, list) or isinstance(p2_propagator, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated p2_propagator: {p2_propagator[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated p2_propagator: {p2_propagator}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> Computed the P2 propagator to be:\n{p2_propagator}")

            return p2_propagator
        
        except Exception as E:
            print(f"> Error in computing p2 propagator:\n> {E}")
            return 0.
    
    def compute_c0_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the first coefficient in the BKM mode expansion: c_{0}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """

        # (1): We compute the c_{0}^{BH} coefficient:
        bh_c0_contribution = self.compute_bh_c0_coefficient() if self.bh_on else 0.0

        # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (3): We compute the c_{0}^{BH} coefficient:
        dvcs_c0_contribution = self.compute_dvcs_c0_coefficient() if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (5): We compute the c_{0}^{I} coefficient:
        interference_c0_contribution = self.compute_interference_c0_coefficient() if self.interference_on else 0.0

        # (6): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        c0_coefficient = (
            bh_prefactor * bh_c0_contribution + 
            dvcs_prefactor * dvcs_c0_contribution + 
            interference_prefactor * interference_c0_contribution)

        # (6): And return the coefficient:
        return c0_coefficient
    
    def compute_c1_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description
        We compute the second coefficient in the BKM mode expansion: c_{1}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
    
        # (1): We compute the c_{1}^{BH} coefficient:
        bh_c1_contribution = self.compute_bh_c1_coefficient() if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (2): We compute the c_{1}^{BH} coefficient:
        dvcs_c1_contribution = self.compute_dvcs_c1_coefficient() if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the c_{1}^{I} coefficient:
        interference_c1_contribution = self.compute_interference_c1_coefficient()

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        c1_coefficient = (
            bh_prefactor * bh_c1_contribution + 
            dvcs_prefactor * dvcs_c1_contribution + 
            interference_prefactor * interference_c1_contribution)

        # (6): And return the coefficient:
        return c1_coefficient
    
    def compute_c2_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the third coefficient in the BKM mode expansion: c_{2}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
        # (1): We compute the c_{2}^{BH} coefficient:
        bh_c2_contribution = self.compute_bh_c2_coefficient() if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (2): We compute the c_{2}^{BH} coefficient:
        dvcs_c2_contribution = 0. if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the c_{2}^{I} coefficient:
        interference_c2_contribution = self.compute_interference_c2_coefficient() if self.interference_on else 0.0

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        c2_coefficient = (
            bh_prefactor * bh_c2_contribution + 
            dvcs_prefactor * dvcs_c2_contribution + 
            interference_prefactor * interference_c2_contribution)

        # (6): And return the coefficient:
        return c2_coefficient
    
    def compute_c3_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the fourth coefficient in the BKM mode expansion: c_{3}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
        # (1): We compute the c_{3}^{BH} coefficient:
        bh_c3_contribution = 0. if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (2): We compute the c_{3}^{BH} coefficient:
        dvcs_c3_contribution = 0. if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the c_{3}^{I} coefficient:
        interference_c3_contribution = self.compute_interference_c3_coefficient() if self.interference_on else 0.0

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        c3_coefficient = (
            bh_prefactor * bh_c3_contribution + 
            dvcs_prefactor * dvcs_c3_contribution + 
            interference_prefactor * interference_c3_contribution)

        # (6): And return the coefficient:
        return c3_coefficient
    
    def compute_s1_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the fifth coefficient in the BKM mode expansion: s_{1}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
        # (1): We compute the s_{1}^{BH} coefficient:
        bh_s1_contribution = self.compute_bh_s1_coefficient() if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (2): We compute the s_{1}^{BH} coefficient:
        dvcs_s1_contribution = self.compute_dvcs_s1_coefficient() if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the s_{1}^{I} coefficient:
        interference_s1_contribution = self.compute_interference_s1_coefficient() if self.interference_on else 0.0

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        s1_coefficient = (
            bh_prefactor * bh_s1_contribution + 
            dvcs_prefactor * dvcs_s1_contribution + 
            interference_prefactor * interference_s1_contribution)

        # (6): And return the coefficient:
        return s1_coefficient
    
    def compute_s2_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the sixth coefficient in the BKM mode expansion: s_{2}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
        # (1): We compute the s_{2}^{BH} coefficient:
        bh_s2_contribution = 0. if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (2): We compute the s_{2}^{BH} coefficient:
        dvcs_s2_contribution = 0. if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the s_{1}^{I} coefficient:
        interference_s2_contribution = self.compute_interference_s2_coefficient() if self.interference_on else 0.0

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        s2_coefficient = (
            bh_prefactor * bh_s2_contribution + 
            dvcs_prefactor * dvcs_s2_contribution + 
            interference_prefactor * interference_s2_contribution)

        # (6): And return the coefficient:
        return s2_coefficient
    
    def compute_s3_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the seventh coefficient in the BKM mode expansion: s_{3}
        The computation of this coefficient will not disambiguate between
        contributions from the three terms: BH squared, DVCS squared, and
        interference.

        ## Arguments:
        Later!

        ## Notes:
        Later!

        ## Examples:
        Later!
        """
        # (1): We compute the s_{3}^{BH} coefficient:
        bh_s3_contribution = 0. if self.bh_on else 0.0

         # (2): Compute the associated prefactor in front of the BH mode expansion:
        bh_prefactor = (
            1. / (
                self.kinematics.x_Bjorken**2 *
                self.lepton_energy_fraction**2 *
                (1. + self.epsilon**2)**2 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )
        
        # (3): We compute the s_{3}^{BH} coefficient:
        dvcs_s3_contribution = 0. if self.dvcs_on else 0.0

        # (4): Compute the associated prefactor in front of the BH mode expansion:
        dvcs_prefactor = (1. / (self.lepton_energy_fraction**2 * self.kinematics.squared_Q_momentum_transfer))

        # (3): We compute the s_{3}^{I} coefficient:
        interference_s3_contribution = self.compute_interference_s3_coefficient() if self.interference_on else 0.0

        # (4): THIS WILL CHANGE LATER! We compute the interference prefactor:
        interference_prefactor = (
            1. / (
                self.kinematics.x_Bjorken *
                self.lepton_energy_fraction**3 *
                self.kinematics.squared_hadronic_momentum_transfer_t *
                self.calculate_lepton_propagator_p1(phi_values) *
                self.calculate_lepton_propagator_p2(phi_values)
                )
            )

        # (5): Now, we sum together all the contributions:
        s3_coefficient = (
            bh_prefactor * bh_s3_contribution + 
            dvcs_prefactor * dvcs_s3_contribution + 
            interference_prefactor * interference_s3_contribution)

        # (6): And return the coefficient:
        return s3_coefficient
    
    def compute_bh_c0_coefficient(self) -> float:
        """
        ## Description:
        Calculates the coefficient c_{0}^{BH} involved in the mode expansion
        for the modulus squared of the Bethe-Heitler process in both the
        unpolarized and longitudinally-polarized target cases.

        ## Notes:
        1. Source for this function: https://arxiv.org/pdf/hep-ph/0112108

        2. We still have not implemented the transversely-polarized target case.
        """

        if self.target_polarization == 0.:

            # (1): Calculate the common appearance of F1 + F2:
            addition_of_form_factors_squared = (self.dirac_form_factor + self.pauli_form_factor)**2

            # (2): Calculate the common appearance of a weighted sum of F1 and F2:
            weighted_combination_of_form_factors = self.dirac_form_factor**2 - (self.kinematics.squared_hadronic_momentum_transfer_t * self.pauli_form_factor**2 / (4. * _MASS_OF_PROTON_IN_GEV**2))

            # (3): Calculate the common appearance of delta^{2} / Q^{2} = t / Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer
            
            # (4):  The first line that contributes to c^{(0)}_{BH}:
            first_line = 8. * self.kinematic_k**2 * (((2. + 3. * self.epsilon**2) * weighted_combination_of_form_factors / t_over_Q_squared) + (2. * self.kinematics.x_Bjorken**2 * addition_of_form_factors_squared))

            # (5): The first part of the second line:
            second_line_first_part = (2. + self.epsilon**2) * ((4. * self.kinematics.x_Bjorken**2 * _MASS_OF_PROTON_IN_GEV**2 / self.kinematics.squared_hadronic_momentum_transfer_t) * (1. + t_over_Q_squared)**2 + 4. * (1 - self.kinematics.x_Bjorken) * (1. + (self.kinematics.x_Bjorken * t_over_Q_squared))) * weighted_combination_of_form_factors
            
            # (6): The second part of the second line:
            second_line_second_part = 4. * self.kinematics.x_Bjorken**2 * (self.kinematics.x_Bjorken + (1. - self.kinematics.x_Bjorken + (self.epsilon**2 / 2.)) * (1 - t_over_Q_squared)**2 - self.kinematics.x_Bjorken * (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared**2) * addition_of_form_factors_squared

            # (7): The second line in its entirety, which is just a prefactor times the addition of the two parts calculated earlier:
            second_line = (2. - self.lepton_energy_fraction)**2 * (second_line_first_part + second_line_second_part)

            # (8): The third line:
            third_line = 8. * (1. + self.epsilon**2) * (1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)) * (2. * self.epsilon**2 * (1 - (self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2))) * weighted_combination_of_form_factors - self.kinematics.x_Bjorken**2 * (1 - t_over_Q_squared)**2 * addition_of_form_factors_squared)

            # (9): Add everything up to obtain the first coefficient:
            c_0_bh_coefficient = first_line + second_line + third_line

        elif self.target_polarization == 0.5:

            # (1): Calculate the common appearance of F1 + F2:
            sum_of_form_factors = (self.dirac_form_factor + self.pauli_form_factor)

            # (2): Calculate the frequent appearance of t/4mp
            t_over_four_mp_squared = self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2)

            # (3): Calculate the weighted sum of the F1 and F2:
            weighted_sum_of_form_factors = self.dirac_form_factor + t_over_four_mp_squared * self.pauli_form_factor

            # (4): Calculate the recurrent appearance of 1 - xb:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (5): Calculate the common appearance of delta^{2} / Q^{2} = t / Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (6): Calculate the derived quantity 1 - t/Q^{2}:
            one_minus_t_over_Q_squared = 1. - t_over_Q_squared

            # (7): Calculate the first term's first bracketed term:
            first_term_first_bracket = 0.5 * self.kinematics.x_Bjorken * (one_minus_t_over_Q_squared) - t_over_four_mp_squared

            # (8): Calculate the first term's second bracketed term:
            first_term_second_bracket = 2. - self.kinematics.x_Bjorken - (2. * (one_minus_xb)**2 * t_over_Q_squared) + (self.epsilon**2 * one_minus_t_over_Q_squared) - (self.kinematics.x_Bjorken * (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared**2)

            # (9): Calculate the first term (includes prefactor)
            first_term = 0.5 * sum_of_form_factors * first_term_first_bracket * first_term_second_bracket

            # (10): Calculate the first bracketed term in the second term:
            second_term_first_bracket = self.kinematics.x_Bjorken**2 * (1. + t_over_Q_squared)**2 / (4. * t_over_four_mp_squared) + ((1. - self.kinematics.x_Bjorken) * (1. + self.kinematics.x_Bjorken * t_over_Q_squared))

            # (11): Calculate the second term (including prefactor):
            second_term = (1. - (1. - self.kinematics.x_Bjorken) * t_over_Q_squared) * weighted_sum_of_form_factors * second_term_first_bracket

            # (12): Calculate the overall prefactor:
            prefactor = 8. * self.lepton_polarization * self.target_polarization * self.kinematics.x_Bjorken * (2. - self.lepton_energy_fraction) * self.lepton_energy_fraction * np.sqrt(1. + self.epsilon**2) * sum_of_form_factors / (1. - t_over_four_mp_squared)

            # (13): Calculate the entire coefficient:
            c_0_bh_coefficient = prefactor * (first_term + second_term)

        else:

            raise NotImplementedError("> Invalid target polarization value.")

        # (X): Return the coefficient:
        return c_0_bh_coefficient
    
    def compute_bh_c1_coefficient(self) -> float:
        """
        ## Description:
        Calculates the coefficient c_{1}^{BH} involved in the mode expansion
        for the modulus squared of the Bethe-Heitler process in both the
        unpolarized and longitudinally-polarized target cases.

        ## Notes:
        1. Source for this function: https://arxiv.org/pdf/hep-ph/0112108

        2. We still have not implemented the transversely-polarized target case.
        """
        
        if self.target_polarization == 0.0:
           
           # (1): Calculate the common appearance of F1 + F2:
            addition_of_form_factors_squared = (self.dirac_form_factor + self.pauli_form_factor)**2

            # (2): Calculate the common appearance of a weighted sum of F1 and F2:
            weighted_combination_of_form_factors = self.dirac_form_factor**2 - ((self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2)) * self.pauli_form_factor**2)
            
            # (3):  The first part of the first line:
            first_line_first_part = ((4. * self.kinematics.x_Bjorken**2 * _MASS_OF_PROTON_IN_GEV**2 / self.kinematics.squared_hadronic_momentum_transfer_t) - 2. * self.kinematics.x_Bjorken - self.epsilon**2) * weighted_combination_of_form_factors
            
            # (4): The first part of the second line:
            first_line_second_part = 2. * self.kinematics.x_Bjorken**2 * (1. - (1. - 2. * self.kinematics.x_Bjorken) * (self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer)) * addition_of_form_factors_squared

            # (5): Multiply by the prefactor to obtain c^{(1)}_{BH}
            c_1_bh_coefficient = 8. * self.kinematic_k * (2. - self.lepton_energy_fraction) * (first_line_first_part + first_line_second_part)
           
        elif self.target_polarization == 0.5:
           
           # (1): Calculate the common appearance of F1 + F2:
            sum_of_form_factors = (self.dirac_form_factor + self.pauli_form_factor)

            # (2): Calculate the frequent appearance of t/4mp
            t_over_four_mp_squared = self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2)

            # (3): Calculate the weighted sum of the F1 and F2:
            weighted_sum_of_form_factors = self.dirac_form_factor + t_over_four_mp_squared * self.pauli_form_factor

            # (4): Calculate the common appearance of delta^{2} / Q^{2} = t / Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the first term straight away:
            first_term = ((2. * t_over_four_mp_squared) - (self.kinematics.x_Bjorken * (1. - t_over_Q_squared))) * ((1. - self.kinematics.x_Bjorken + (self.kinematics.x_Bjorken * t_over_Q_squared))) * sum_of_form_factors

            # (6): Calculate the second term's bracketed quantity:
            second_term_bracket_term = 1. + self.kinematics.x_Bjorken - ((3. - 2. * self.kinematics.x_Bjorken) * (1. + self.kinematics.x_Bjorken * t_over_Q_squared)) - (self.kinematics.x_Bjorken**2 * (1. + t_over_Q_squared**2) / t_over_four_mp_squared)
            
            # (7): Calculate the second term in entirety:
            second_term = weighted_sum_of_form_factors * second_term_bracket_term
            
            # (8): Calculate the overall prefactor:
            prefactor = -8. * self.lepton_polarization * self.target_polarization * self.kinematics.x_Bjorken * self.lepton_energy_fraction * self.kinematic_k * np.sqrt(1. + self.epsilon**2) * sum_of_form_factors / (1. - t_over_four_mp_squared)

            # (13): Calculate the entire coefficient:
            c_1_bh_coefficient = prefactor * (first_term + second_term)
           
        else:
           
           raise NotImplementedError("> Invalid target polarization value!")
       
        return c_1_bh_coefficient
    
    def compute_bh_c2_coefficient(self) -> float:
        """
        ## Description:
        Calculates the coefficient c_{1}^{BH} involved in the mode expansion
        for the modulus squared of the Bethe-Heitler process in both the
        unpolarized and longitudinally-polarized target cases.

        ## Notes:
        1. Source for this function: https://arxiv.org/pdf/hep-ph/0112108

        2. We still have not implemented the transversely-polarized target case.
        """

        if self.target_polarization == 0.0:
           
           # (1): Calculate the common appearance of F1 + F2:
            addition_of_form_factors_squared = (self.dirac_form_factor + self.pauli_form_factor)**2

            # (2): Calculate the common appearance of a weighted sum of F1 and F2:
            weighted_combination_of_form_factors = self.dirac_form_factor**2 - ((self.kinematics.squared_hadronic_momentum_transfer_t/ (4. * _MASS_OF_PROTON_IN_GEV**2)) * self.pauli_form_factor**2)
            
            # (3): A quick scaling of the weighted sum of F1 and F2:
            first_part_of_contribution = (4. * _MASS_OF_PROTON_IN_GEV**2 / self.kinematics.squared_hadronic_momentum_transfer_t) * weighted_combination_of_form_factors
            
            # (4):  Multiply by the prefactor to obtain the coefficient.
            c_2_bh_coefficient = 8. * self.kinematics.x_Bjorken**2 * self.kinematic_k**2 * (first_part_of_contribution + 2. * addition_of_form_factors_squared)
           
        elif self.target_polarization == 0.5:
           
            # (X): Make sure you understand this! https://arxiv.org/pdf/hep-ph/0112108
            c_2_bh_coefficient = 0.
           
        else:
           
           raise NotImplementedError("> Invalid target polarization value!")
       
        return c_2_bh_coefficient
    
    def compute_bh_s1_coefficient(self) -> float:
        """
        ## Notes:
        1. Source for this function: https://arxiv.org/pdf/hep-ph/0112108

        2. We still have not implemented the transversely-polarized target case. This
        coefficient is 0 in the unpolarized and longitudinally-polarized target cases.
        """
        
        # (X): s_{0}^{BH} = 0 for unpolarized target.
        # | [NOTE]: We multiply by K to ensure its shape is
        # | the same as the other coefficients; i.e. this will return
        # | a "zeros-like" array:
        return 0. * self.kinematic_k

    def compute_dvcs_c0_coefficient(self) -> float:
        """
        ## Description:
        Calculates the coefficient c_{0}^{BH} involved in the mode expansion
        for the modulus squared of the Bethe-Heitler process in both the
        unpolarized and longitudinally-polarized target cases.

        ## Notes:
        1. Source for this function: https://arxiv.org/pdf/1005.5209

        2. This function is coded up according to the BKM10 formalism. The BKM02
        formalism version of this coefficient has not yet been implemented.
        """
        
        if self.target_polarization == 0.0:
           
           # (1): Calculate the first term's prefactor:
            first_term_prefactor = 2. * ( 2. - 2. * self.lepton_energy_fraction + self.lepton_energy_fraction**2 + (self.epsilon**2 * self.lepton_energy_fraction**2 / 2.)) / (1. + self.epsilon**2)

            # (2): Calcualte the second term's prefactor:
            second_term_prefactor = 16. * self.kinematic_k**2 / ((2. - self.kinematics.x_Bjorken)**2 * (1. + self.epsilon**2))

            # (3): Calculate the first term's Curly C contribution:
            first_term_curlyC_unp_DVCS = self.calculate_curly_c_unpolarized_dvcs(
                effective_cffs = False,
                effective_conjugate_cffs = False
            )
            
            # (4): Calculate the second terms' Curly C contribution:
            second_term_curlyC_unp_DVCS_effective_cffs = self.calculate_curly_c_unpolarized_dvcs(
                effective_cffs = True,
                effective_conjugate_cffs = True
            )

            # (5): Calculate the entire coefficient:
            c0_dvcs_unpolarized_coefficient = first_term_prefactor * first_term_curlyC_unp_DVCS + second_term_prefactor * second_term_curlyC_unp_DVCS_effective_cffs
           
        elif self.target_polarization == 0.5:
           
            # (1): Calculate the prefactor
            prefactor = 2. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) / np.sqrt(1. + self.epsilon**2)

            # (2): Calculate the Curly C contribution:
            curlyC_lp_contribution = self.calculate_curly_c_longitudinally_polarized_dvcs(
                effective_cffs = False,
                effective_conjugate_cffs = False
            )

            # (3): Return the entire thing:
            c0_dvcs_unpolarized_coefficient = prefactor * curlyC_lp_contribution
           
        else:
           
           raise NotImplementedError("> Invalid target polarization value!")
       
        return c0_dvcs_unpolarized_coefficient
    
    def compute_dvcs_c1_coefficient(self) -> float:
        """
        Later!
        """
        if self.target_polarization == 0.0:
           
           # (1): Calculate the first term's prefactor:
            prefactor = 8. * self.kinematic_k * (2. - self.lepton_energy_fraction) / ((2. - self.kinematics.x_Bjorken) * (1. + self.epsilon**2))

            # (2): Calculate the second terms' Curly C contribution:
            curlyC_unp_DVCS = self.calculate_curly_c_unpolarized_dvcs(
                effective_cffs = True,
                effective_conjugate_cffs = False
            ).real
            
            # (3): Calculate the entire coefficient:
            c1_dvcs_unpolarized_coefficient = prefactor * curlyC_unp_DVCS.real
           
        elif self.target_polarization == 0.5:
           
            # (1): Calculate the prefactor
            prefactor = 8. * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction / (np.sqrt(1. + self.epsilon**2) * (2. - self.kinematics.x_Bjorken))

            # (2): Return the entire thing:
            c1_dvcs_unpolarized_coefficient = prefactor * self.calculate_curly_c_longitudinally_polarized_dvcs(
                effective_cffs = True,
                effective_conjugate_cffs = False
            ).real
           
        else:
           
           raise NotImplementedError("> Invalid target polarization value!")
       
        return c1_dvcs_unpolarized_coefficient

    def compute_dvcs_s1_coefficient(self) -> float:
        """
        Later!
        """
        if self.target_polarization == 0.0:
           
           # (1): Calculate the first term's prefactor:
            prefactor = -8. * self.kinematic_k * self.lepton_polarization * self.lepton_energy_fraction * np.sqrt(1. + self.epsilon**2) / ((2. - self.kinematics.x_Bjorken) * (1. + self.epsilon**2))

            # (2): Calculate the second terms' Curly C contribution:
            s1_dvcs_unpolarized_coefficient = prefactor * self.calculate_curly_c_unpolarized_dvcs(
                effective_cffs = True,
                effective_conjugate_cffs = False
            ).real
           
        elif self.target_polarization == 0.5:
           
            # (1): Calculate the prefactor
            prefactor = -8. * self.target_polarization * self.kinematic_k * (2. - self.lepton_energy_fraction) / ((2. - self.kinematics.x_Bjorken) * (1. + self.epsilon**2))
            
            # (3): Return the entire thing:
            s1_dvcs_unpolarized_coefficient = prefactor * self.calculate_curly_c_longitudinally_polarized_dvcs(
                effective_cffs = True,
                effective_conjugate_cffs = False 
            ).imag
           
        else:
           
           raise NotImplementedError("> Invalid target polarization value!")
       
        return s1_dvcs_unpolarized_coefficient 
    
    def compute_interference_c0_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate C_{++}(n = 0) using the *unpolarized* prescription:
            c0_plus_plus = self.calculate_c_0_plus_plus_unpolarized()

            # (X): Calculate C_{++}^{V}(n = 0) using the *unpolarized* prescription:
            c0v_plus_plus = self.calculate_c_0_plus_plus_unpolarized_v()
            
            # (X): Calculate C_{++}^{A}(n = 0) using the *unpolarized* prescription:
            c0a_plus_plus = self.calculate_c_0_plus_plus_unpolarized_a()

            # (X): Calculate C_{0+}^{V}(n = 0) using the *unpolarized* prescription:
            c0_zero_plus = self.calculate_c_0_zero_plus_unpolarized()

            # (X): Calculate C_{0+}^{V}(n = 0) using the *unpolarized* prescription:
            c0v_zero_plus = self.calculate_c_0_zero_plus_unpolarized_v()

            # (X): Calculate C_{0+}^{A}(n = 0) using the *unpolarized* prescription:
            c0a_zero_plus = self.calculate_c_0_zero_plus_unpolarized_a()
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = True)

            # (X): Calculate C_{++}(n = 0) using the *longitudinally-polarized* prescription:
            c0_plus_plus = self.calculate_c_0_plus_plus_longitudinally_polarized()

            # (X): Calculate C_{++}^{V}(n = 0) using the *longitudinally-polarized* prescription:
            c0v_plus_plus = self.calculate_c_0_plus_plus_longitudinally_polarized_v()
            
            # (X): Calculate C_{++}^{A}(n = 0) using the *longitudinally-polarized* prescription:
            c0a_plus_plus = self.calculate_c_0_plus_plus_longitudinally_polarized_a()

            # (X): Calculate C_{0+}^{V}(n = 0) using the *longitudinally-polarized* prescription:
            c0_zero_plus = self.calculate_c_0_zero_plus_longitudinally_polarized()

            # (X): Calculate C_{0+}^{V}(n = 0) using the *longitudinally-polarized* prescription:
            c0v_zero_plus = self.calculate_c_0_zero_plus_longitudinally_polarized_v()

            # (X): Calculate C_{0+}^{A}(n = 0) using the *longitudinally-polarized* prescription:
            c0a_zero_plus = self.calculate_c_0_zero_plus_longitudinally_polarized_a()

        # (X): Calculate Curly C_{++}(n = 0):
        curly_c0_plus_plus = (
            self.math.safe_cast(curly_c_plus_plus, True)
            + self.math.safe_cast(c0v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(c0_plus_plus, True)
            + self.math.safe_cast(c0a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(c0_plus_plus, True)
        )

        # (X): Safe-cast the prefactor for Curly C_{0+}(n = 0):
        prefactor = self.math.safe_cast(
            self.k_tilde * self.math.sqrt(2. / self.kinematics.squared_Q_momentum_transfer) / (2. - self.kinematics.x_Bjorken),
            promote_to_complex_if_needed = True)

        # (X): Calculate Curly C_{0+}(n = 0):
        curly_c0_zero_plus = (prefactor *
                (
                self.math.safe_cast(curly_c_zero_plus, True)
                + self.math.safe_cast(c0v_zero_plus, True) * self.math.safe_cast(curly_cv_zero_plus, True) / self.math.safe_cast(c0_zero_plus, True)
                + self.math.safe_cast(c0a_zero_plus, True) * self.math.safe_cast(curly_ca_zero_plus, True) / self.math.safe_cast(c0_zero_plus, True)
                )
        )
        
        # (X): Compute the c_{0} coefficient with all of its required ingredients!
        c_0_interference_coefficient  = c0_plus_plus * self.math.real(curly_c0_plus_plus) + c0_zero_plus * self.math.real(curly_c0_zero_plus)

        # (X): Return the coefficient:
        return c_0_interference_coefficient
    
    def compute_interference_c1_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate C_{++}(n = 1) using the *unpolarized* prescription:
            c1_plus_plus = self.calculate_c_1_plus_plus_unpolarized()

            # (X): Calculate C_{++}^{V}(n = 1) using the *unpolarized* prescription:
            c1v_plus_plus = self.calculate_c_1_plus_plus_unpolarized_v()

            # (X): Calculate C_{++}^{A}(n = 1) using the *unpolarized* prescription:
            c1a_plus_plus = self.calculate_c_1_plus_plus_unpolarized_a()

            # (X): Calculate C_{0+}^{V}(n = 1) using the *unpolarized* prescription:
            c1_zero_plus = self.calculate_c_1_zero_plus_unpolarized()

            # (X): Calculate C_{0+}^{V}(n = 1) using the *unpolarized* prescription:
            c1v_zero_plus = self.calculate_c_1_zero_plus_unpolarized_v()

            # (X): Calculate C_{0+}^{A}(n = 1) using the *unpolarized* prescription:
            c1a_zero_plus = self.calculate_c_1_zero_plus_unpolarized_a()
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized()

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v()

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a()

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized()

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v()

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a()

            # (X): Calculate C_{++}(n = 1) using the *longitudinally-polarized* prescription:
            c1_plus_plus = self.calculate_c_1_plus_plus_longitudinally_polarized()

            # (X): Calculate C_{++}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            c1v_plus_plus = self.calculate_c_1_plus_plus_longitudinally_polarized_v()

            # (X): Calculate C_{++}^{A}(n = 1) using the *longitudinally-polarized* prescription:
            c1a_plus_plus = self.calculate_c_1_plus_plus_longitudinally_polarized_a()

            # (X): Calculate C_{0+}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            c1_zero_plus = self.calculate_c_1_zero_plus_longitudinally_polarized()

            # (X): Calculate C_{0+}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            c1v_zero_plus = self.calculate_c_1_zero_plus_longitudinally_polarized_v()

            # (X): C_{0+}^{A}(n = 1) is 0 in the *longitudinally-polarized* prescription:
            c1a_zero_plus = 0.

        # (X): Calculate Curly C_{++}(n = 1):
        curly_c1_plus_plus = (
            self.math.safe_cast(curly_c_plus_plus, True)
            + self.math.safe_cast(c1v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(c1_plus_plus, True)
            + self.math.safe_cast(c1a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(c1_plus_plus, True)
        )

        # (X): Safe-cast the prefactor for Curly C_{0+}(n = 1):
        prefactor = self.math.safe_cast(
            self.k_tilde * self.math.sqrt(2. / self.kinematics.squared_Q_momentum_transfer) / (2. - self.kinematics.x_Bjorken),
            promote_to_complex_if_needed = True)

        # (X): Calculate Curly C_{0+}(n = 1):
        curly_c1_zero_plus = (prefactor *
                (
                self.math.safe_cast(curly_c_zero_plus, True)
                + self.math.safe_cast(c1v_zero_plus, True) * self.math.safe_cast(curly_cv_zero_plus, True) / self.math.safe_cast(c1_zero_plus, True)
                + self.math.safe_cast(c1a_zero_plus, True) * self.math.safe_cast(curly_ca_zero_plus, True) / self.math.safe_cast(c1_zero_plus, True)
                )
        )
        
        # (X): Compute the c_{1} coefficient with all of its required ingredients!
        c_1_interference_coefficient  = c1_plus_plus * self.math.real(curly_c1_plus_plus) + c1_zero_plus * self.math.real(curly_c1_zero_plus)

        return c_1_interference_coefficient
    
    def compute_interference_c2_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate C_{++}^{V}(n = 2) using the *unpolarized* prescription:
            c2_plus_plus = self.calculate_c_2_plus_plus_unpolarized()

            # (X): Calculate C_{++}^{V}(n = 2) using the *unpolarized* prescription:
            c2v_plus_plus = self.calculate_c_2_plus_plus_unpolarized_v()

            # (X): Calculate C_{++}^{V}(n = 2) using the *unpolarized* prescription:
            c2a_plus_plus = self.calculate_c_2_plus_plus_unpolarized_a()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            c2_zero_plus = self.calculate_c_2_zero_plus_unpolarized()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            c2v_zero_plus = self.calculate_c_2_zero_plus_unpolarized_v()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            c2a_zero_plus = self.calculate_c_2_zero_plus_unpolarized_a()
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized()

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v()

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a()

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized()

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v()

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a()

            # (X): Calculate C_{++}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2_plus_plus = self.calculate_c_2_plus_plus_longitudinally_polarized()

            # (X): Calculate C_{++}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2v_plus_plus = self.calculate_c_2_plus_plus_longitudinally_polarized_v()

            # (X): Calculate C_{++}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2a_plus_plus = self.calculate_c_2_plus_plus_longitudinally_polarized_a()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2_zero_plus = self.calculate_c_2_zero_plus_longitudinally_polarized()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2v_zero_plus = self.calculate_c_2_zero_plus_longitudinally_polarized_v()

            # (X): Calculate C_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            c2a_zero_plus = self.calculate_c_2_zero_plus_longitudinally_polarized_a()
        
        # (X): Calculate Curly C_{++}(n = 0):
        curly_c2_plus_plus = (
            self.math.safe_cast(curly_c_plus_plus, True)
            + self.math.safe_cast(c2v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(c2_plus_plus, True)
            + self.math.safe_cast(c2a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(c2_plus_plus, True)
        )
        
        # (X): Safe-cast the prefactor for Curly C_{0+}(n = 2):
        prefactor = self.math.safe_cast(
            self.k_tilde * self.math.sqrt(2. / self.kinematics.squared_Q_momentum_transfer) / (2. - self.kinematics.x_Bjorken),
            promote_to_complex_if_needed = True)

        # (X): Calculate Curly C_{0+}(n = 2):
        curly_c2_zero_plus = (prefactor *
                (
                self.math.safe_cast(curly_c_zero_plus, True)
                + self.math.safe_cast(c2v_zero_plus, True) * self.math.safe_cast(curly_cv_zero_plus, True) / self.math.safe_cast(c2_zero_plus, True)
                + self.math.safe_cast(c2a_zero_plus, True) * self.math.safe_cast(curly_ca_zero_plus, True) / self.math.safe_cast(c2_zero_plus, True)
                )
        )
        
        # (X): Compute the c_{2} coefficient with all of its required ingredients!
        c_2_interference_coefficient  = c2_plus_plus * self.math.real(curly_c2_plus_plus) + c2_zero_plus * self.math.real(curly_c2_zero_plus)

        return c_2_interference_coefficient
    
    def compute_interference_c3_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate C_{++}^{V}(n = 3) using the *unpolarized* prescription:
            c3_plus_plus = self.calculate_c_3_plus_plus_unpolarized()

            # (X): Calculate C_{++}^{V}(n = 3) using the *unpolarized* prescription:
            c3v_plus_plus = self.calculate_c_3_plus_plus_unpolarized_v()

            # (X): Calculate C_{++}^{V}(n = 3) using the *unpolarized* prescription:
            c3a_plus_plus = self.calculate_c_3_plus_plus_unpolarized_a()

            # (X): Calculate C_{0+}^{V}(n = 3) is 0 in the *unpolarized* prescription:
            c3_zero_plus = 0.

            # (X): Calculate C_{0+}^{V}(n = 3) is 0 in the *unpolarized* prescription:
            c3v_zero_plus = 0.

            # (X): Calculate C_{0+}^{V}(n = 3) is 0 in the *unpolarized* prescription:
            c3a_zero_plus = 0.

            # (X): Calculate Curly C_{++}(n = 3):
            curly_c3_plus_plus = (
                self.math.safe_cast(curly_c_plus_plus, True)
                + self.math.safe_cast(c3v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(c3_plus_plus, True)
                + self.math.safe_cast(c3a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(c3_plus_plus, True)
            )
            
            # (X): Calculate Curly C_{0+}(n = 3):
            curly_c3_zero_plus = 0.
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = True)

            # (X): C_{++}^{V}(n = 3) is not given in the paper, which means it's 0:
            c3_plus_plus = 0.

            # (X): C_{++}^{V}(n = 3) is 0 (we are putting this here for completeness/consistency):
            c3v_plus_plus = 0.

            # (X): C_{++}^{V}(n = 3) is 0 (we are putting this here for completeness/consistency):
            c3a_plus_plus = 0.

            # (X): C_{0+}^{V}(n = 3) is 0 (we are putting this here for completeness/consistency):
            c3_zero_plus = 0.

            # (X): C_{0+}^{V}(n = 3) is 0 (we are putting this here for completeness/consistency):
            c3v_zero_plus = 0.

            # (X): C_{0+}^{V}(n = 3) is 0 (we are putting this here for completeness/consistency):
            c3a_zero_plus = 0.

            # (X): Curly C_{++}(n = 3) is 0 because all of its components are 0:
            curly_c3_plus_plus = 0.
            
            # (X): Curly C_{0+}(n = 3) is 0 for the same reason:
            curly_c3_zero_plus = 0.
        
        c_3_interference_coefficient  = c3_plus_plus * self.math.real(curly_c3_plus_plus) + c3_zero_plus * self.math.real(curly_c3_zero_plus)

        return c_3_interference_coefficient
    
    def compute_interference_s1_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate S_{++}(n = 1) using the *unpolarized* prescription:
            s1_plus_plus = self.calculate_s_1_plus_plus_unpolarized()

            # (X): Calculate S_{++}^{V}(n = 1) using the *unpolarized* prescription:
            s1v_plus_plus = self.calculate_s_1_plus_plus_unpolarized_v()

            # (X): Calculate S_{++}^{A}(n = 1) using the *unpolarized* prescription:
            s1a_plus_plus = self.calculate_s_1_plus_plus_unpolarized_a()

            # (X): Calculate S_{0+}^{V}(n = 1) using the *unpolarized* prescription:
            s1_zero_plus = self.calculate_s_1_zero_plus_unpolarized()

            # (X): Calculate S_{0+}^{V}(n = 1) using the *unpolarized* prescription:
            s1v_zero_plus = self.calculate_s_1_zero_plus_unpolarized_v()

            # (X): Calculate S_{0+}^{A}(n = 1) using the *unpolarized* prescription:
            s1a_zero_plus = self.calculate_s_1_zero_plus_unpolarized_a()
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = True)

            # (X): Calculate S_{++}(n = 1) using the *longitudinally-polarized* prescription:
            s1_plus_plus = self.calculate_s_1_plus_plus_longitudinally_polarized()

            # (X): Calculate S_{++}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            s1v_plus_plus = self.calculate_s_1_plus_plus_longitudinally_polarized_v()

            # (X): Calculate S_{++}^{A}(n = 1) using the *longitudinally-polarized* prescription:
            s1a_plus_plus = self.calculate_s_1_plus_plus_longitudinally_polarized_a()

            # (X): Calculate S_{0+}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            s1_zero_plus = self.calculate_s_1_zero_plus_longitudinally_polarized()

            # (X): Calculate S_{0+}^{V}(n = 1) using the *longitudinally-polarized* prescription:
            s1v_zero_plus = self.calculate_s_1_zero_plus_longitudinally_polarized_v()

            # (X): S_{0+}^{A}(n = 1) is 0 in the *longitudinally-polarized* prescription:
            s1a_zero_plus = self.calculate_s_1_plus_plus_longitudinally_polarized()

        # (X): Calculate Curly S_{++}(n = 1):
        curly_s1_plus_plus = (
            self.math.safe_cast(curly_c_plus_plus, True)
            + self.math.safe_cast(s1v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(s1_plus_plus, True)
            + self.math.safe_cast(s1a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(s1_plus_plus, True)
        )

        # (X): Safe-cast the prefactor for Curly S_{0+}(n = 1):
        prefactor = self.math.safe_cast(
            self.k_tilde * self.math.sqrt(2. / self.kinematics.squared_Q_momentum_transfer) / (2. - self.kinematics.x_Bjorken),
            promote_to_complex_if_needed = True)

        # (X): Calculate Curly S_{0+}(n = 1):
        curly_s1_zero_plus = (prefactor *
                (
                self.math.safe_cast(curly_c_zero_plus, True)
                + self.math.safe_cast(s1v_zero_plus, True) * self.math.safe_cast(curly_cv_zero_plus, True) / self.math.safe_cast(s1_zero_plus, True)
                + self.math.safe_cast(s1a_zero_plus, True) * self.math.safe_cast(curly_ca_zero_plus, True) / self.math.safe_cast(s1_zero_plus, True)
                )
        )
        
        # (X): Compute the s_{1} coefficient with all of its required ingredients!
        s_1_interference_coefficient  = s1_plus_plus * self.math.imag(curly_s1_plus_plus) + s1_zero_plus * self.math.imag(curly_s1_zero_plus)

        return s_1_interference_coefficient
    
    def compute_interference_s2_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate S_{++}^{V}(n = 2) using the *unpolarized* prescription:
            s2_plus_plus = self.calculate_s_2_plus_plus_unpolarized()

            # (X): Calculate S_{++}^{V}(n = 2) using the *unpolarized* prescription:
            s2v_plus_plus = self.calculate_s_2_plus_plus_unpolarized_v()

            # (X): Calculate S_{++}^{V}(n = 2) using the *unpolarized* prescription:
            s2a_plus_plus = self.calculate_s_2_plus_plus_unpolarized_a()

            # (X): Calculate S_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            s2_zero_plus = self.calculate_s_2_zero_plus_unpolarized()

            # (X): Calculate S_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            s2v_zero_plus = self.calculate_s_2_zero_plus_unpolarized_v()

            # (X): Calculate S_{0+}^{V}(n = 2) using the *unpolarized* prescription:
            s2a_zero_plus = self.calculate_s_2_zero_plus_unpolarized_a()
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = True)

            # (X): Calculate S_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            s2_zero_plus = self.calculate_s_2_zero_plus_longitudinally_polarized()

            # (X): Calculate S_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            s2v_zero_plus = self.calculate_s_2_zero_plus_longitudinally_polarized_v()

            # (X): Calculate S_{0+}^{V}(n = 2) using the *longitudinally-polarized* prescription:
            s2a_zero_plus = self.calculate_s_2_zero_plus_longitudinally_polarized_a()
        
        # (X): Calculate Curly S_{++}(n = 2):
        curly_s2_plus_plus = (
            self.math.safe_cast(curly_c_plus_plus, True)
            + self.math.safe_cast(s2v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(s2_plus_plus, True)
            + self.math.safe_cast(s2a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(s2_plus_plus, True)
        )
        
        # (X): Safe-cast the prefactor for Curly S_{0+}(n = 2):
        prefactor = self.math.safe_cast(
            self.k_tilde * self.math.sqrt(2. / self.kinematics.squared_Q_momentum_transfer) / (2. - self.kinematics.x_Bjorken),
            promote_to_complex_if_needed = True)

        # (X): Calculate Curly S_{0+}(n = 2):
        curly_s2_zero_plus = (prefactor *
                (
                self.math.safe_cast(curly_c_zero_plus, True)
                + self.math.safe_cast(s2v_zero_plus, True) * self.math.safe_cast(curly_cv_zero_plus, True) / self.math.safe_cast(s2_zero_plus, True)
                + self.math.safe_cast(s2a_zero_plus, True) * self.math.safe_cast(curly_ca_zero_plus, True) / self.math.safe_cast(s2_zero_plus, True)
                )
        )
        
        s_2_interference_coefficient = s2_plus_plus * self.math.imag(curly_s2_plus_plus) + s2_zero_plus * self.math.imag(curly_s2_zero_plus)

        return s_2_interference_coefficient
    
    def compute_interference_s3_coefficient(self) -> float:
        """
        Later!
        """

        if self.target_polarization == 0.:

            # (X): Calculate Curly C_{++} using the *unpolarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *unpolarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *unpolarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *unpolarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_unpolarized_interference(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *unpolarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_unpolarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *unpolarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_unpolarized_a(effective_cffs = True)

            # (X): Calculate S_{++}^{V}(n = 3) using the *unpolarized* prescription:
            s3_plus_plus = 0.

            # (X): Calculate S_{++}^{V}(n = 3) using the *unpolarized* prescription:
            s3v_plus_plus = 0.

            # (X): Calculate S_{++}^{V}(n = 3) using the *unpolarized* prescription:
            s3a_plus_plus = 0.

            # (X): Calculate S_{0+}^{V}(n = 3) using the *unpolarized* prescription:
            s3_zero_plus = 0.

            # (X): Calculate S_{0+}^{V}(n = 3) using the *unpolarized* prescription:
            s3v_zero_plus = 0.

            # (X): Calculate S_{0+}^{V}(n = 3) using the *unpolarized* prescription:
            s3a_zero_plus = 0.

            # (X): Calculate Curly S_{++}(n = 3):
            curly_s3_plus_plus = 0.

            # (X): Calculate Curly S_{0+}(n = 3):
            curly_s3_zero_plus = 0.
            
        elif self.target_polarization == 0.5:

            # (X): Calculate Curly C_{++} using the *longitudinally-polarized* prescription:
            curly_c_plus_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_plus_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = False)

            # (X): Calculate Curly C_{++}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_plus_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = False)

            # (X): Calculate Curly C_{0+} using the *longitudinally-polarized* prescription:
            curly_c_zero_plus = self.calculate_curly_c_longitudinally_polarized(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{V} using the *longitudinally-polarized* prescription:
            curly_cv_zero_plus = self.calculate_curly_c_longitudinally_polarized_v(effective_cffs = True)

            # (X): Calculate Curly C_{0+}^{A} using the *longitudinally-polarized* prescription:
            curly_ca_zero_plus = self.calculate_curly_c_longitudinally_polarized_a(effective_cffs = True)

            # (X): Calculate S{++}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3_plus_plus = self.calculate_s_3_plus_plus_longitudinally_polarized()

            # (X): Calculate C_{++}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3v_plus_plus = self.calculate_s_3_plus_plus_longitudinally_polarized_v()

            # (X): Calculate S_{++}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3a_plus_plus = self.calculate_s_3_plus_plus_longitudinally_polarized_a()

            # (X): Calculate S_{0+}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3_zero_plus = 0.

            # (X): Calculate S_{0+}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3v_zero_plus = 0.

            # (X): Calculate S_{0+}^{V}(n = 3) using the *longitudinally-polarized* prescription:
            s3a_zero_plus = 0.

            # (X): Calculate Curly S_{++}(n = 3):
            curly_s3_plus_plus = (
                self.math.safe_cast(curly_c_plus_plus, True)
                + self.math.safe_cast(s3v_plus_plus, True) * self.math.safe_cast(curly_cv_plus_plus, True) / self.math.safe_cast(s3_plus_plus, True)
                + self.math.safe_cast(s3a_plus_plus, True) * self.math.safe_cast(curly_ca_plus_plus, True) / self.math.safe_cast(s3_plus_plus, True)
            )
            
            # (X): Calculate Curly S_{0+}(n = 3):
            curly_s3_zero_plus = 0.
        
        s_3_interference_coefficient  = s3_plus_plus * self.math.imag(curly_s3_plus_plus) + s3_zero_plus * self.math.imag(curly_s3_zero_plus)

        return s_3_interference_coefficient
    
    def calculate_curly_c_unpolarized_dvcs(self, effective_cffs: bool = False, effective_conjugate_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            cffs_star = self.effective_cff_values.conjugate() if effective_conjugate_cffs else self.cff_values.conjugate()

            # (1): Calculate the appearance of Q^{2} + x_{B} t:
            sum_Q_squared_xb_t = self.kinematics.squared_Q_momentum_transfer + self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t

            # (2): Calculate (2 - x_{B})Q^{2} + x_{B} t:
            weighted_sum_Q_squared_xb_t = (2. - self.kinematics.x_Bjorken) * self.kinematics.squared_Q_momentum_transfer + self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t

            # (3): Calculate Q^{2} (Q^{2} + x_{B} t):
            Q_squared_times_sum = self.kinematics.squared_Q_momentum_transfer * sum_Q_squared_xb_t

            # (4): Calculate the first product of CFFs:
            cff_h_h_star_with_prefactor = cffs.compton_form_factor_h * cffs_star.compton_form_factor_h * 4. * (1. - self.kinematics.x_Bjorken)

            # (5): Calculate the second product of CFFs:
            cff_h_tilde_h_tilde_star = cffs.compton_form_factor_h_tilde * cffs_star.compton_form_factor_h_tilde

            # (6): Calculate the third product of CFFs:
            cff_h_e_star_plus_e_h_star = cffs.compton_form_factor_h * cffs_star.compton_form_factor_e + cffs.compton_form_factor_e * cffs_star.compton_form_factor_h

            # (7): Calculate the fourth product of CFFs:
            cff_h_tilde_e_tilde_star_plus_e_tilde_h_tilde_star = cffs.compton_form_factor_h_tilde * cffs_star.compton_form_factor_e_tilde + cffs.compton_form_factor_e_tilde * cffs_star.compton_form_factor_h_tilde
            
            # (8): Calculate the fifth product of CFFs:
            cff_e_e_star = cffs.compton_form_factor_e * cffs_star.compton_form_factor_e
            
            # (9): Calculate the sixth product of CFFs:
            cff_e_tilde_e_tilde_star = cffs.compton_form_factor_e_tilde * cffs_star.compton_form_factor_e_tilde

            # (10): Calculate the second bracket term:
            second_bracket_term = 4. * (1. - self.kinematics.x_Bjorken + ((2. * self.kinematics.squared_Q_momentum_transfer + self.kinematics.squared_hadronic_momentum_transfer_t) * self.epsilon**2 / (4. * sum_Q_squared_xb_t))) * cff_h_tilde_h_tilde_star

            # (11): Calculate the third_bracket term's prefactor
            third_bracket_term_prefactor = self.kinematics.x_Bjorken**2 * (self.kinematics.squared_Q_momentum_transfer + self.kinematics.squared_hadronic_momentum_transfer_t)**2 / Q_squared_times_sum

            # (12): Calculate the fourth bracket term (yes, we're skipping the third for a minute):
            fourth_bracket_term = self.kinematics.x_Bjorken**2 * self.kinematics.squared_Q_momentum_transfer * cff_h_tilde_e_tilde_star_plus_e_tilde_h_tilde_star / sum_Q_squared_xb_t

            # (13): Calculate the fifth bracket term:
            fifth_bracket_term = (weighted_sum_Q_squared_xb_t**2 * self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2 * Q_squared_times_sum) + third_bracket_term_prefactor) * cff_e_e_star

            # (14): Calculate the third bracket term:
            third_bracket_term  = third_bracket_term_prefactor * cff_h_e_star_plus_e_h_star

            # (15): Calculate the sixth bracket term:
            sixth_bracket_term = self.kinematics.x_Bjorken**2 * self.kinematics.squared_Q_momentum_transfer * self.kinematics.squared_hadronic_momentum_transfer_t * cff_e_tilde_e_tilde_star / (4. * _MASS_OF_PROTON_IN_GEV**2 * sum_Q_squared_xb_t)

            # (16): Return the entire thing:
            curly_C_unpolarized_dvcs = Q_squared_times_sum * (cff_h_h_star_with_prefactor + second_bracket_term - third_bracket_term - fourth_bracket_term - fifth_bracket_term - sixth_bracket_term) / weighted_sum_Q_squared_xb_t**2
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_unpolarized_dvcs, list) or isinstance(curly_C_unpolarized_dvcs, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_dvcs: {curly_C_unpolarized_dvcs[0]}")

                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_dvcs: {curly_C_unpolarized_dvcs}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated curly_C_unpolarized_dvcs to be:\n{curly_C_unpolarized_dvcs}")

            # (5): Return the output:
            return curly_C_unpolarized_dvcs
        
        except Exception as ERROR:
            print(f"> Error in calculating the Curly C DVCS: \n> {ERROR}")
            return 0.
    
    def calculate_curly_c_longitudinally_polarized_dvcs(
            self,
            effective_cffs: bool = False, 
            effective_conjugate_cffs: bool = False) -> float:
        """
        ## Description:
        Calculate the insane quantity Curly C_{LP}(F | F*).
        
        ## Arguments:
        1. `effective_cffs` (bool) 
            True/False: Pass in F_{eff} rather than F in the first argument of Curly C_{LP}(F | F*)

        2. `effective_conjugate_cffs` (bool)
            True/False: Pass in F_{eff} rather than F in the second argument of Curly C_{LP}(F | F*)
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            cffs_star = self.effective_cff_values.conjugate() if effective_conjugate_cffs else self.cff_values.conjugate()
        
            # (1): Calculate the appearance of Q^{2} + x_{B} t:
            sum_Q_squared_xb_t = self.kinematics.squared_Q_momentum_transfer + self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t

            # (2): Calculate 2 - x_{B}:
            two_minus_xb = 2. - self.kinematics.x_Bjorken

            # (3) Calculuate (2 - x_{B}) * Q^{2} + x_{B} t:
            weighted_sum_Q_squared_xb_t = two_minus_xb * self.kinematics.squared_Q_momentum_transfer + self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t

            # (4): Calculate the first product of CFFs:
            first_term_CFFs = cffs.compton_form_factor_h * cffs_star.compton_form_factor_h_tilde + cffs.compton_form_factor_h_tilde * cffs_star.compton_form_factor_h

            # (5): Calculate the second product of CFFs:
            second_term_CFFs =cffs. compton_form_factor_h * cffs_star.compton_form_factor_e_tilde + cffs.compton_form_factor_e_tilde * cffs_star.compton_form_factor_h + cffs.compton_form_factor_h_tilde * cffs_star.compton_form_factor_e + cffs.compton_form_factor_e * cffs_star.compton_form_factor_h_tilde

            # (6): Calculate the third product of CFFs:
            third_term_CFFs = cffs.compton_form_factor_h_tilde * cffs_star.compton_form_factor_e + cffs.compton_form_factor_e * cffs_star.compton_form_factor_h_tilde

            # (7): Calculate the fourth product of CFFs:
            fourth_term_CFFs = cffs.compton_form_factor_e * cffs_star.compton_form_factor_e_tilde + cffs.compton_form_factor_e_tilde * cffs_star.compton_form_factor_e

            # (8): Calculate the first term's prefactor:
            first_term_prefactor = 4. * (1. - self.kinematics.x_Bjorken + (self.epsilon**2 * ((3.  - 2. * self.kinematics.x_Bjorken) * self.kinematics.squared_Q_momentum_transfer + self.kinematics.squared_hadronic_momentum_transfer_t)) / (4. * sum_Q_squared_xb_t))

            # (9): Calculate the second term's prefactor:
            second_term_prefactor = self.kinematics.x_Bjorken**2 * (self.kinematics.squared_Q_momentum_transfer - (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t * (1. - 2. * self.kinematics.x_Bjorken))) / sum_Q_squared_xb_t

            # (10): Calculate the third term's prefactor:
            third_term_prefactor = self.kinematics.x_Bjorken * ((4. * (1. - self.kinematics.x_Bjorken) * sum_Q_squared_xb_t * self.kinematics.squared_hadronic_momentum_transfer_t) + (self.epsilon**2 * (self.kinematics.squared_Q_momentum_transfer + self.kinematics.squared_hadronic_momentum_transfer_t)**2)) / (2. * self.kinematics.squared_Q_momentum_transfer * sum_Q_squared_xb_t)

            # (11): Calculate the first part of the fourth term's perfactor:
            fourth_term_prefactor_first_part = weighted_sum_Q_squared_xb_t / sum_Q_squared_xb_t
            
            # (12): Calculate the second part of the fourth term's perfactor:
            fourth_term_prefactor_second_part = (self.kinematics.x_Bjorken**2 * (self.kinematics.squared_Q_momentum_transfer + self.kinematics.squared_hadronic_momentum_transfer_t)**2 / (2. * self.kinematics.squared_Q_momentum_transfer * weighted_sum_Q_squared_xb_t)) + (self.kinematics.squared_hadronic_momentum_transfer_t / (4. * _MASS_OF_PROTON_IN_GEV**2))
            
            # (13): Finish the fourth-term prefactor
            fourth_term_prefactor = self.kinematics.x_Bjorken * fourth_term_prefactor_first_part * fourth_term_prefactor_second_part

            # (14): Calculate the curly-bracket term:
            curly_bracket_term = first_term_CFFs * first_term_prefactor - second_term_CFFs * second_term_prefactor - third_term_CFFs * third_term_prefactor - fourth_term_CFFs * fourth_term_prefactor
            
            # (15): Calculate the prefactor:
            prefactor = self.kinematics.squared_Q_momentum_transfer * sum_Q_squared_xb_t / (np.sqrt(1. + self.epsilon**2) * weighted_sum_Q_squared_xb_t**2)

            # (16): Return the entire thing:
            curly_C_longitudinally_polarized_dvcs = prefactor * curly_bracket_term

            # (14): Return the coefficient:
            return curly_C_longitudinally_polarized_dvcs
        
        except Exception as ERROR:
            print(f"> Error in calculating curlyCDVCS for DVCS Amplitude Squared:\n> {ERROR}")
            return 0.
    
    def calculate_curly_c_unpolarized_interference(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate the first two terms: weighted CFFs:
            weighted_cffs = (self.dirac_form_factor * cffs.compton_form_factor_h) - (self.kinematics.squared_hadronic_momentum_transfer_t * self.pauli_form_factor * cffs.compton_form_factor_e / (4. * _MASS_OF_PROTON_IN_GEV**2))

            # (2): Calculate the next term:
            second_term = self.kinematics.x_Bjorken * (self.dirac_form_factor + self.pauli_form_factor) * cffs.compton_form_factor_h_tilde / (2. - self.kinematics.x_Bjorken + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (3): Add them together:
            curly_C_unpolarized_interference = weighted_cffs + second_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_unpolarized_interference, list) or isinstance(curly_C_unpolarized_interference, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference: {curly_C_unpolarized_interference[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference: {curly_C_unpolarized_interference}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated curly_C_unpolarized_interference to be:\n{curly_C_unpolarized_interference}")

            # (5): Return the output:
            return curly_C_unpolarized_interference

        except Exception as ERROR:
            print(f"> Error in calculating the Curly C interference unpolarized target: \n> {ERROR}")
            return 0.
        
    def calculate_curly_c_unpolarized_v(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate the first two terms: weighted CFFs:
            cff_term = cffs.compton_form_factor_h + cffs.compton_form_factor_e

            # (2): Calculate the next term:
            second_term = self.kinematics.x_Bjorken * (self.dirac_form_factor + self.pauli_form_factor) / (2. - self.kinematics.x_Bjorken + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (3): Add them together:
            curly_C_unpolarized_interference_V = cff_term * second_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_unpolarized_interference_V, list) or isinstance(curly_C_unpolarized_interference_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference_V: {curly_C_unpolarized_interference_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference_V: {curly_C_unpolarized_interference_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated Curly C interference V unpolarized target to be:\n{curly_C_unpolarized_interference_V}")

            # (5): Return the output:
            return curly_C_unpolarized_interference_V

        except Exception as ERROR:
            print(f"> Error in calculating the Curly C interference V unpolarized target: \n> {ERROR}")
            return 0.
        
    def calculate_curly_c_unpolarized_a(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate the next term:
            xb_modulation = self.kinematics.x_Bjorken * (self.dirac_form_factor + self.pauli_form_factor) / (2. - self.kinematics.x_Bjorken + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (2): Add them together:
            curly_C_unpolarized_interference_A = cffs.compton_form_factor_h_tilde * xb_modulation

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_unpolarized_interference_A, list) or isinstance(curly_C_unpolarized_interference_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference_A: {curly_C_unpolarized_interference_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_unpolarized_interference_A: {curly_C_unpolarized_interference_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated Curly C interference A unpolarized target to be:\n{curly_C_unpolarized_interference_A}")

            # (4): Return the output:
            return curly_C_unpolarized_interference_A

        except Exception as ERROR:
            print(f"> Error in calculating the Curly C interference A unpolarized target: \n> {ERROR}")
            return 0.
        
    def calculate_curly_c_longitudinally_polarized(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate a fancy quantity:
            ratio_of_xb_to_more_xb = self.kinematics.x_Bjorken / (2. - self.kinematics.x_Bjorken + self.kinematics.x_Bjorken * t_over_Q_squared)

            # (3): Calculate another fancy quantity that appears twice:
            x_Bjorken_correction = self.kinematics.x_Bjorken * (1. - t_over_Q_squared) / 2.

            # (4): Calculate the first appearance of CFFs:
            first_cff_contribution = ratio_of_xb_to_more_xb * (self.dirac_form_factor + self.pauli_form_factor) * (cffs.compton_form_factor_h + x_Bjorken_correction * cffs.compton_form_factor_e)

            # (5): Calculate the second appearance of CFFs:
            second_cff_contribution = (1. + (_MASS_OF_PROTON_IN_GEV**2 * self.kinematics.x_Bjorken * ratio_of_xb_to_more_xb * (3. + t_over_Q_squared) / self.kinematics.squared_Q_momentum_transfer)) * self.dirac_form_factor * cffs.compton_form_factor_h_tilde
            
            # (6): Calculate the third appearance of CFFs:
            third_cff_contribution = t_over_Q_squared * 2. * (1. - 2. * self.kinematics.x_Bjorken) * ratio_of_xb_to_more_xb * self.pauli_form_factor * cffs.compton_form_factor_h_tilde

            # (7): Calculate the fourth appearance of the CFFs:
            fourth_cff_contribution = ratio_of_xb_to_more_xb * (x_Bjorken_correction * self.dirac_form_factor + self.kinematics.squared_hadronic_momentum_transfer_t * self.pauli_form_factor / (4. * _MASS_OF_PROTON_IN_GEV**2)) * cffs.compton_form_factor_e_tilde

            # (8): Add together with the correct signs the entire thing
            curly_C_longitudinally_polarized_interference = first_cff_contribution + second_cff_contribution - third_cff_contribution - fourth_cff_contribution

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_longitudinally_polarized_interference, list) or isinstance(curly_C_longitudinally_polarized_interference, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_longitudinally_polarized_interference: {curly_C_longitudinally_polarized_interference[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_longitudinally_polarized_interference: {curly_C_longitudinally_polarized_interference}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated the curly C LP for interference to be:\n{curly_C_longitudinally_polarized_interference}")
            
            # (9): Return the output:
            return curly_C_longitudinally_polarized_interference

        except Exception as ERROR:
            print(f"> Error in calculating the curly C LP contribution amplitude squared\n> {ERROR}")
            return 0
        
    def calculate_curly_c_longitudinally_polarized_v(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate a fancy quantity:
            ratio_of_xb_to_more_xb = self.kinematics.x_Bjorken / (2. - self.kinematics.x_Bjorken + self.kinematics.x_Bjorken * t_over_Q_squared)

            # (3): Calculate the sum of form factors:
            sum_of_form_factors = self.dirac_form_factor + self.pauli_form_factor

            # (4): Calculate the entire thing:
            curly_C_V_longitudinally_polarized_interference = ratio_of_xb_to_more_xb * sum_of_form_factors * (cffs.compton_form_factor_h + (self.kinematics.x_Bjorken * (1. - t_over_Q_squared) * cffs.compton_form_factor_e / 2.))

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_V_longitudinally_polarized_interference, list) or isinstance(curly_C_V_longitudinally_polarized_interference, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_V_longitudinally_polarized_interference: {curly_C_V_longitudinally_polarized_interference[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_V_longitudinally_polarized_interference: {curly_C_V_longitudinally_polarized_interference}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated the curly C LP V for interference to be:\n{curly_C_V_longitudinally_polarized_interference}")
            
            # (5): Return the output:
            return curly_C_V_longitudinally_polarized_interference

        except Exception as ERROR:
            print(f"> Error in calculating the curly C LP V contribution amplitude squared\n> {ERROR}")
            return 0.
    
    def calculate_curly_c_longitudinally_polarized_a(self, effective_cffs: bool = False) -> float:
        """
        Later!
        """
        try:

            cffs = self.effective_cff_values if effective_cffs else self.cff_values

            # (1): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate a fancy quantity:
            ratio_of_xb_to_more_xb = self.kinematics.x_Bjorken / (2. - self.kinematics.x_Bjorken + self.kinematics.x_Bjorken * t_over_Q_squared)

            # (3): Calculate the sum of form factors:
            sum_of_form_factors = self.dirac_form_factor + self.pauli_form_factor
            
            # (4): Calculate the CFFs appearance:
            cff_appearance = cffs.compton_form_factor_h_tilde * (1. + (2. * self.kinematics.x_Bjorken * _MASS_OF_PROTON_SQUARED_IN_GEV_SQUARED / self.kinematics.squared_Q_momentum_transfer)) + (self.kinematics.x_Bjorken * cffs.compton_form_factor_e_tilde / 2.)

            # (5): Calculate the entire thing:
            curly_C_A_longitudinally_polarized_interference = ratio_of_xb_to_more_xb * sum_of_form_factors * cff_appearance

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(curly_C_A_longitudinally_polarized_interference, list) or isinstance(curly_C_A_longitudinally_polarized_interference, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated curly_C_A_longitudinally_polarized_interference: {curly_C_A_longitudinally_polarized_interference[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated curly_C_A_longitudinally_polarized_interference: {curly_C_A_longitudinally_polarized_interference}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated the curly C LP A for interference to be:\n{curly_C_A_longitudinally_polarized_interference}")
            
            # (6): Return the output:
            return curly_C_A_longitudinally_polarized_interference

        except Exception as ERROR:
            print(f"> Error in calculating the curly C LP A contribution amplitude squared\n> {ERROR}")
            return 0.

    def calculate_c_0_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate 1 + sqrt(1 + self.epsilon^{2}):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate 2 - x_{B}:
            two_minus_xb = 2. - self.kinematics.x_Bjorken

            # (5): Caluclate 2 - y:
            two_minus_y = 2. - self.lepton_energy_fraction

            # (6): Calculate the first term in the brackets:
            first_term_in_brackets = self.k_tilde**2 * two_minus_y**2 / (self.kinematics.squared_Q_momentum_transfer * root_one_plus_epsilon_squared)

            # (7): Calculate the first part of the second term in brackets:
            second_term_in_brackets_first_part = t_over_Q_squared * two_minus_xb * (1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.))
            
            # (8): Calculate the numerator of the second part of the second term in brackets:
            second_term_in_brackets_second_part_numerator = 2. * self.kinematics.x_Bjorken * t_over_Q_squared * (two_minus_xb + 0.5 * (root_one_plus_epsilon_squared - 1.) + 0.5 * self.epsilon**2 / self.kinematics.x_Bjorken) + self.epsilon**2
            
            # (9): Calculate the second part of the second term in brackets:
            second_term_in_brackets_second_part =  1. + second_term_in_brackets_second_part_numerator / (two_minus_xb * one_plus_root_epsilon_stuff)
            
            # (10): Calculate the prefactor:
            prefactor = -4. * two_minus_y * one_plus_root_epsilon_stuff / self.math.power(root_one_plus_epsilon_squared, 4)

            # (11): Calculate the coefficient
            c_0_plus_plus_unp = prefactor * (first_term_in_brackets + second_term_in_brackets_first_part * second_term_in_brackets_second_part)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_unp, list) or isinstance(c_0_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_unp: {c_0_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_unp: {c_0_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_unp to be:\n{c_0_plus_plus_unp}")

            # (12): Return the coefficient:
            return c_0_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Compute the first term in the brackets:
            first_term_in_brackets = (2. - self.lepton_energy_fraction)**2 * self.k_tilde**2 / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer)

            # (5): First multiplicative term in the second term in the brackets:
            second_term_first_multiplicative_term = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (6): Second multiplicative term in the second term in the brackets:
            second_term_second_multiplicative_term = one_plus_root_epsilon_stuff / 2.

            # (7): Third multiplicative term in the second term in the brackets:
            second_term_third_multiplicative_term = 1. + t_over_Q_squared

            # (8): Fourth multiplicative term numerator in the second term in the brackets:
            second_term_fourth_multiplicative_term = 1. + (root_one_plus_epsilon_squared - 1. + (2. * self.kinematics.x_Bjorken)) * t_over_Q_squared / one_plus_root_epsilon_stuff

            # (9): Fourth multiplicative term in its entirety:
            second_term_in_brackets = second_term_first_multiplicative_term * second_term_second_multiplicative_term * second_term_third_multiplicative_term * second_term_fourth_multiplicative_term

            # (10): The prefactor in front of the brackets:
            coefficient_prefactor = 8. * (2. - self.lepton_energy_fraction) * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**4

            # (11): The entire thing:
            c_0_plus_plus_V_unp = coefficient_prefactor * (first_term_in_brackets + second_term_in_brackets)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_V_unp, list) or isinstance(c_0_plus_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_V_unp: {c_0_plus_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_V_unp: {c_0_plus_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_V_unp to be:\n{c_0_plus_plus_V_unp}")

            # (12): Return the coefficient:
            return c_0_plus_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate 2 - y:
            two_minus_y = 2. - self.lepton_energy_fraction

            # (5): Calculate Ktilde^{2}/squaredQ:
            ktilde_over_Q_squared = self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer

            # (6): Calculate the first term in the curly brackets:
            curly_bracket_first_term = two_minus_y**2 * ktilde_over_Q_squared * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) / (2. * root_one_plus_epsilon_squared)

            # (7): Calculate inner parentheses term:
            deepest_parentheses_term = (self.kinematics.x_Bjorken * (2. + one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) / one_plus_root_epsilon_stuff + (one_plus_root_epsilon_stuff - 2.)) * t_over_Q_squared

            # (8): Calculate the square-bracket term:
            square_bracket_term = one_plus_root_epsilon_stuff * (one_plus_root_epsilon_stuff - self.kinematics.x_Bjorken + deepest_parentheses_term) / 2. - (2. * ktilde_over_Q_squared)

            # (9): Calculate the second bracket term:
            curly_bracket_second_term = (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) * square_bracket_term

            # (10): Calculate the prefactor: 
            coefficient_prefactor = 8. * two_minus_y * t_over_Q_squared / root_one_plus_epsilon_squared**4

            # (11): The entire thing:
            c_0_plus_plus_A_unp = coefficient_prefactor * (curly_bracket_first_term + curly_bracket_second_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_A_unp, list) or isinstance(c_0_plus_plus_A_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_A_unp: {c_0_plus_plus_A_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_A_unp: {c_0_plus_plus_A_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_A_unp to be:\n{c_0_plus_plus_A_unp}")

            # (12): Return the coefficient:
            return c_0_plus_plus_A_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_A_unp for Interference Term:\n> {ERROR}")
            return 0.
    
    def calculate_c_0_zero_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the bracket quantity:
            bracket_quantity = self.epsilon**2 + self.kinematics.squared_hadronic_momentum_transfer_t * (2. - 6.* self.kinematics.x_Bjorken - self.epsilon**2) / (3. * self.kinematics.squared_Q_momentum_transfer)
            
            # (2): Calculate part of the prefactor:
            prefactor = 12. * self.math.sqrt(2.) * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.math.sqrt(1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4)) / self.math.power(1. + self.epsilon**2, 2.5)
            
            # (3): Calculate the coefficient:
            c_0_zero_plus_unp = prefactor * bracket_quantity
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_unp, list) or isinstance(c_0_zero_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_unp: {c_0_zero_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_unp: {c_0_zero_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_unp to be:\n{c_0_zero_plus_unp}")

            # (4): Return the coefficient:
            return c_0_zero_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_zero_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate the main part of the thing:
            main_part = self.kinematics.x_Bjorken * t_over_Q_squared * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)

            # (3): Calculate the prefactor:
            prefactor = 24. * self.math.sqrt(2.) * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / (1. + self.epsilon**2)**2.5

            # (4): Stitch together the coefficient:
            c_0_zero_plus_V_unp = prefactor * main_part

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_V_unp, list) or isinstance(c_0_zero_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_V_unp: {c_0_zero_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_V_unp: {c_0_zero_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_V_unp to be:\n{c_0_zero_plus_V_unp}")

            # (5): Return the coefficient:
            return c_0_zero_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_zero_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate the recurrent quantity 8 - 6x_{B} + 5 self.epsilon^{2}:
            fancy_xb_epsilon_term = 8. - 6. * self.kinematics.x_Bjorken + 5. * self.epsilon**2

            # (3): Compute the bracketed term:
            brackets_term = 1. - t_over_Q_squared * (2. - 12. * self.kinematics.x_Bjorken * (1. - self.kinematics.x_Bjorken) - self.epsilon**2) / fancy_xb_epsilon_term

            # (4): Calculate the prefactor:
            prefactor = 4. * self.math.sqrt(2.) * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / self.math.power(1. + self.epsilon**2, 2.5)

            # (5): Stitch together the coefficient:
            c_0_zero_plus_A_unp = prefactor * t_over_Q_squared * fancy_xb_epsilon_term * brackets_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_A_unp, list) or isinstance(c_0_zero_plus_A_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_A_unp: {c_0_zero_plus_A_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_A_unp: {c_0_zero_plus_A_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_A_unp to be:\n{c_0_zero_plus_A_unp}")

            # (6): Return the coefficient:
            return c_0_zero_plus_A_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_A_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate 1 + sqrt(1 + self.epsilon^{2}):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate first term in first brackets
            first_bracket_first_term = (1. + (1. - self.kinematics.x_Bjorken) * (root_one_plus_epsilon_squared - 1.) / (2. * self.kinematics.x_Bjorken) + self.epsilon**2 / (4. * self.kinematics.x_Bjorken)) * self.kinematics.x_Bjorken * t_over_Q_squared

            # (5): Calculate the first bracket term:
            first_bracket_term = first_bracket_first_term - 3. * self.epsilon**2 / 4.

            # (6): Calculate the second bracket term:
            second_bracket_term = 1. - (1. - 3. * self.kinematics.x_Bjorken) * t_over_Q_squared + (1. - root_one_plus_epsilon_squared + 3. * self.epsilon**2) * self.kinematics.x_Bjorken * t_over_Q_squared / (one_plus_root_epsilon_stuff - self.epsilon**2)

            # (7): Calculate the crazy coefficient with all the y's:
            fancy_y_coefficient = 2. - 2. * self.lepton_energy_fraction + self.lepton_energy_fraction**2 + self.epsilon**2 * self.lepton_energy_fraction**2 / 2.

            # (8): Calculate the entire second term:
            second_term = -4. * self.kinematic_k * fancy_y_coefficient * (one_plus_root_epsilon_stuff - self.epsilon**2) * second_bracket_term / root_one_plus_epsilon_squared**5

            # (9): Calculate the first term:
            first_term = -16. * self.kinematic_k * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) * first_bracket_term / root_one_plus_epsilon_squared**5

            # (10): Calculate the coefficient
            c_1_plus_plus_unp = first_term + second_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_unp, list) or isinstance(c_1_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_unp: {c_1_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_unp: {c_1_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_unp to be:\n{c_1_plus_plus_unp}")

            # (12): Return the coefficient:
            return c_1_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the first bracket term:
            first_bracket_term = (2. - self.lepton_energy_fraction)**2 * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)

            # (4): Compute the first part of the second term in brackets:
            second_bracket_term_first_part = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (5): Compute the second part of the second term in brackets:
            second_bracket_term_second_part = 0.5 * (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (6): The prefactor in front of the brackets:
            coefficient_prefactor = 16. * self.kinematic_k * self.kinematics.x_Bjorken * t_over_Q_squared / self.math.power(root_one_plus_epsilon_squared, 5)

            # (7): The entire thing:
            c_1_plus_plus_V_unp = coefficient_prefactor * (first_bracket_term + second_bracket_term_first_part * second_bracket_term_second_part)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_V_unp, list) or isinstance(c_1_plus_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_V_unp: {c_1_plus_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_V_unp: {c_1_plus_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_V_unp to be:\n{c_1_plus_plus_V_unp}")

            # (12): Return the coefficient:
            return c_1_plus_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:
    
            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate 1 - x_{B}:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (5): Calculate 1 - 2 x_{B}:
            one_minus_2xb = 1. - 2. * self.kinematics.x_Bjorken

            # (6): Calculate a fancy, annoying quantity:
            fancy_y_stuff = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (7): Calculate the second contribution to the first term in brackets:
            first_bracket_term_second_part = 1. - one_minus_2xb * t_over_Q_squared + (4. * self.kinematics.x_Bjorken * one_minus_xb + self.epsilon**2) * t_prime_over_Q_squared / (4. * root_one_plus_epsilon_squared)

            # (8): Calculate the second bracket term:
            second_bracket_term = 1. - 0.5 * self.kinematics.x_Bjorken + 0.25 * (one_minus_2xb + root_one_plus_epsilon_squared) * (1. - t_over_Q_squared) + (4. * self.kinematics.x_Bjorken * one_minus_xb + self.epsilon**2) * t_prime_over_Q_squared / (2. * root_one_plus_epsilon_squared)

            # (9): Calculate the prefactor:
            prefactor = -16. * self.kinematic_k * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (10): The entire thing:
            c_1_plus_plus_A_unp = prefactor * (fancy_y_stuff * first_bracket_term_second_part - (2. - self.lepton_energy_fraction)**2 * second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_A_unp, list) or isinstance(c_1_plus_plus_A_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_A_unp: {c_1_plus_plus_A_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_A_unp: {c_1_plus_plus_A_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_A_unp to be:\n{c_1_plus_plus_A_unp}")

            # (11): Return the coefficient:
            return c_1_plus_plus_A_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_A_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_zero_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate 1 - x_{B}:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (5): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (6): Calculate the first term:
            first_bracket_term = (2. - self.lepton_energy_fraction)**2 * t_prime_over_Q_squared * (one_minus_xb + (one_minus_xb * self.kinematics.x_Bjorken + (self.epsilon**2 / 4.)) * t_prime_over_Q_squared / root_one_plus_epsilon_squared)
            
            # (7): Calculate the second term:
            second_bracket_term = y_quantity * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared) * (self.epsilon**2 - 2. * (1. + (self.epsilon**2 / (2. * self.kinematics.x_Bjorken))) * self.kinematics.x_Bjorken * t_over_Q_squared) / root_one_plus_epsilon_squared
            
            # (8): Calculate part of the prefactor:
            prefactor = 8. * self.math.sqrt(2. * y_quantity) / root_one_plus_epsilon_squared**4
            
            # (9): Calculate the coefficient:
            c_1_zero_plus_unp = prefactor * (first_bracket_term + second_bracket_term)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_zero_plus_unp, list) or isinstance(c_1_zero_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_unp: {c_1_zero_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_unp: {c_1_zero_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_zero_plus_unp to be:\n{c_1_zero_plus_unp}")

            # (9): Return the coefficient:
            return c_1_zero_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_1_zero_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_zero_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate the huge y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (3): Calculate the major part:
            major_part = (2 - self.lepton_energy_fraction)**2 * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer + (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)**2 * y_quantity

            # (4): Calculate the prefactor:
            prefactor = 16. * self.math.sqrt(2. * y_quantity) * self.kinematics.x_Bjorken * t_over_Q_squared / (1. + self.epsilon**2)**2.5

            # (5): Stitch together the coefficient:
            c_1_zero_plus_V_unp = prefactor * major_part

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_zero_plus_V_unp, list) or isinstance(c_1_zero_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_V_unp: {c_1_zero_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_V_unp: {c_1_zero_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_zero_plus_V_unp to be:\n{c_1_zero_plus_V_unp}")

            # (6): Return the coefficient:
            return c_1_zero_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_1_zero_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
    
    def calculate_c_1_zero_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate 1 - 2x_{B}:
            one_minus_2xb = 1. - 2. * self.kinematics.x_Bjorken

            # (4): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (5): Calculate the first part of the second term:
            second_term_first_part = (1. - one_minus_2xb * t_over_Q_squared) * y_quantity

            # (6); Calculate the second part of the second term:
            second_term_second_part = 4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2 + t_over_Q_squared * (4. * self.kinematics.x_Bjorken * (1. - self.kinematics.x_Bjorken) + self.epsilon**2)
            
            # (7): Calculate the first term:
            first_term = self.k_tilde**2 * one_minus_2xb * (2. - self.lepton_energy_fraction)**2 / self.kinematics.squared_Q_momentum_transfer
            
            # (8): Calculate part of the prefactor:
            prefactor = 8. * self.math.sqrt(2. * y_quantity) * t_over_Q_squared / root_one_plus_epsilon_squared**5
            
            # (9): Calculate the coefficient:
            c_1_zero_plus_unp_A = prefactor * (first_term + second_term_first_part * second_term_second_part)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_zero_plus_unp_A, list) or isinstance(c_1_zero_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_unp_A: {c_1_zero_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_unp_A: {c_1_zero_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_zero_plus_unp_A to be:\n{c_1_zero_plus_unp_A}")

            # (10): Return the coefficient:
            return c_1_zero_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating c_1_zero_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the first bracket quantity:
            first_bracket_term = 2. * self.epsilon**2 * self.k_tilde**2 / (root_one_plus_epsilon_squared * (1. + root_one_plus_epsilon_squared) * self.kinematics.squared_Q_momentum_transfer)
        
            # (4): Calculate the second bracket quantity:
            second_bracket_term = self.kinematics.x_Bjorken * self.t_prime * t_over_Q_squared * (1. - self.kinematics.x_Bjorken - 0.5 * (root_one_plus_epsilon_squared - 1.) + 0.5 * self.epsilon**2 / self.kinematics.x_Bjorken) / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the prefactor:
            prefactor = 8. * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) / root_one_plus_epsilon_squared**4
            
            # (6): Calculate the coefficient
            c_2_plus_plus_unp = prefactor * (first_bracket_term + second_bracket_term)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_unp, list) or isinstance(c_2_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_unp: {c_2_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_unp: {c_2_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_unp to be:\n{c_2_plus_plus_unp}")

            # (7): Return the coefficient:
            return c_2_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the major term:
            major_term = (4. * self.k_tilde**2 / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer)) + 0.5 * (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * (1. + t_over_Q_squared) * t_prime_over_Q_squared

            # (5): Calculate the prefactor: 
            prefactor = 8. * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (6): The entire thing:
            c_2_plus_plus_V_unp = prefactor * major_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_V_unp, list) or isinstance(c_2_plus_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_V_unp: {c_2_plus_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_V_unp: {c_2_plus_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_V_unp to be:\n{c_2_plus_plus_V_unp}")

            # (7): Return the coefficient:
            return c_2_plus_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the first bracket term:
            first_bracket_term = 4. * (1. - 2. * self.kinematics.x_Bjorken) * self.k_tilde**2 / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer)

            # (5): Calculate the second bracket term:
            second_bracket_term = (3.  - root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken + self.epsilon**2 / self.kinematics.x_Bjorken ) * self.kinematics.x_Bjorken * t_prime_over_Q_squared

            # (6): Calculate the prefactor: 
            prefactor = 4. * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (7): The entire thing:
            c_2_plus_plus_A_unp = prefactor * (first_bracket_term - second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_A_unp, list) or isinstance(c_2_plus_plus_A_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_A_unp: {c_2_plus_plus_A_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_A_unp: {c_2_plus_plus_A_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_A_unp to be:\n{c_2_plus_plus_A_unp}")

            # (8): Return the coefficient:
            return c_2_plus_plus_A_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_A_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_zero_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity self.epsilon^2/2:
            self.epsilon_squared_over_2 = self.epsilon**2 / 2.

            # (3): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (4): Calculate the bracket term:
            bracket_term = 1. + ((1. + self.epsilon_squared_over_2 / self.kinematics.x_Bjorken) / (1. + self.epsilon_squared_over_2)) * self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2. * y_quantity) * self.kinematic_k * (2. - self.lepton_energy_fraction) / root_one_plus_epsilon_squared**5
            
            # (6): Calculate the coefficient:
            c_2_zero_plus_unp = prefactor * (1. + self.epsilon_squared_over_2) * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_unp, list) or isinstance(c_2_zero_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp: {c_2_zero_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp: {c_2_zero_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_unp to be:\n{c_2_zero_plus_unp}")

            # (7): Return the coefficient:
            return c_2_zero_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
            
    def calculate_c_2_zero_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the annoying y quantity:
            y_quantity = self.math.sqrt(1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.))

            # (4): Calculate the prefactor:
            prefactor = 8. * self.math.sqrt(2.) * y_quantity * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**5
            
            # (5): Calculate the coefficient:
            c_2_zero_plus_unp_V = prefactor * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_unp_V, list) or isinstance(c_2_zero_plus_unp_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_V: {c_2_zero_plus_unp_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_V: {c_2_zero_plus_unp_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_unp_V to be:\n{c_2_zero_plus_unp_V}")

            # (6): Return the coefficient:
            return c_2_zero_plus_unp_V

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_unp_V for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_zero_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate 1 - x_{B}:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (5): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (6): Calculate the bracket term:
            bracket_term = one_minus_xb + 0.5 * t_prime_over_Q_squared * (4. * self.kinematics.x_Bjorken * one_minus_xb + self.epsilon**2) / root_one_plus_epsilon_squared
            
            # (7): Calculate part of the prefactor:
            prefactor = 8. * self.math.sqrt(2. * y_quantity) * self.kinematic_k * (2. - self.lepton_energy_fraction) * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (8): Calculate the coefficient:
            c_2_zero_plus_unp_A = prefactor * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_unp_A, list) or isinstance(c_2_zero_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_A: {c_2_zero_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_A: {c_2_zero_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_unp_A to be:\n{c_2_zero_plus_unp_A}")

            # (9): Return the coefficient:
            return c_2_zero_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_3_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the major term:
            major_term = (1. - self.kinematics.x_Bjorken) * t_over_Q_squared + 0.5 * (root_one_plus_epsilon_squared - 1.) * (1. + t_over_Q_squared)
        
            # (4): Calculate the "intermediate" term:
            intermediate_term = (root_one_plus_epsilon_squared - 1.) / root_one_plus_epsilon_squared**5

            # (5): Calculate the prefactor:
            prefactor = -8. * self.kinematic_k * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)
            
            # (6): Calculate the coefficient
            c_3_plus_plus_unp = prefactor * intermediate_term * major_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_3_plus_plus_unp, list) or isinstance(c_3_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_unp: {c_3_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_unp: {c_3_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_3_plus_plus_unp to be:\n{c_3_plus_plus_unp}")

            # (7): Return the coefficient:
            return c_3_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_3_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_3_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the major term:
            major_term = root_one_plus_epsilon_squared - 1. + (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared

            # (4): Calculate he prefactor:
            prefactor = -8. * self.kinematic_k * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**5
            
            # (5): The entire thing:
            c_3_plus_plus_V_unp = prefactor * major_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_3_plus_plus_V_unp, list) or isinstance(c_3_plus_plus_V_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_V_unp: {c_3_plus_plus_V_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_V_unp: {c_3_plus_plus_V_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_3_plus_plus_V_unp to be:\n{c_3_plus_plus_V_unp}")

            # (7): Return the coefficient:
            return c_3_plus_plus_V_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_3_plus_plus_V_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_3_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the main term:
            main_term = self.kinematics.squared_hadronic_momentum_transfer_t * self.t_prime * (self.kinematics.x_Bjorken * (1. - self.kinematics.x_Bjorken) + self.epsilon**2 / 4.) / self.kinematics.squared_Q_momentum_transfer**2

            # (2): Calculate the prefactor: 
            prefactor = 16. * self.kinematic_k * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) / (1. + self.epsilon**2)**2.5
            
            # (3): The entire thing:
            c_3_plus_plus_A_unp = prefactor * main_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_3_plus_plus_A_unp, list) or isinstance(c_3_plus_plus_A_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_A_unp: {c_3_plus_plus_A_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_3_plus_plus_A_unp: {c_3_plus_plus_A_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_3_plus_plus_A_unp to be:\n{c_3_plus_plus_A_unp}")

            # (4): Return the coefficient:
            return c_3_plus_plus_A_unp

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_A_unp for Interference Term:\n> {ERROR}")
            return 0.
    
    def calculate_s_1_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the quantity t'/Q^{2}:
            tPrime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the bracket term:
            bracket_term = 1. + ((1. - self.kinematics.x_Bjorken + 0.5 * (root_one_plus_epsilon_squared - 1.)) / root_one_plus_epsilon_squared**2) * tPrime_over_Q_squared
            
            # (4): Calculate the prefactor:
            prefactor = 8. * self.lepton_polarization * self.kinematic_k * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) / root_one_plus_epsilon_squared**2

            # (5): Calculate the coefficient
            s_1_plus_plus_unp = prefactor * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_unp, list) or isinstance(s_1_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp: {s_1_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp: {s_1_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_unp to be:\n{s_1_plus_plus_unp}")

            # (6): Return the coefficient:
            return s_1_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the bracket term:
            bracket_term = root_one_plus_epsilon_squared - 1. + (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared

            # (4): Calculate the prefactor:
            prefactor = -8. * self.lepton_polarization * self.kinematic_k * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**4

            # (5): Calculate the coefficient
            s_1_plus_plus_unp_V = prefactor * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_unp_V, list) or isinstance(s_1_plus_plus_unp_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp_V: {s_1_plus_plus_unp_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp_V: {s_1_plus_plus_unp_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_unp_V to be:\n{s_1_plus_plus_unp_V}")

            # (6): Return the coefficient:
            return s_1_plus_plus_unp_V

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_unp_V for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the quantity t'/Q^{2}:
            tPrime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the bracket term:
            one_minus_2xb = 1. - 2. * self.kinematics.x_Bjorken

            # (5): Calculate the bracket term:
            bracket_term = 1. - one_minus_2xb * (one_minus_2xb + root_one_plus_epsilon_squared) * tPrime_over_Q_squared / (2. * root_one_plus_epsilon_squared)

            # (6): Calculate the prefactor:
            prefactor = 8. * self.lepton_polarization * self.kinematic_k * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) * t_over_Q_squared / root_one_plus_epsilon_squared**2

            # (7): Calculate the coefficient
            s_1_plus_plus_unp_A = prefactor * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_unp_A, list) or isinstance(s_1_plus_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp_A: {s_1_plus_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_unp_A: {s_1_plus_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_unp_A to be:\n{s_1_plus_plus_unp_A}")

            # (8): Return the coefficient:
            return s_1_plus_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the  quantity (1 + self.epsilon^2)^{2}:
            root_one_plus_epsilon_squared = (1. + self.epsilon**2)**2

            # (2): Calculate the huge y quantity:
            y_quantity = self.math.sqrt(1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.))

            # (3): Calculate the coefficient
            s_1_zero_plus_unp = 8. * self.lepton_polarization * self.math.sqrt(2.) * (2. - self.lepton_energy_fraction) * self.lepton_energy_fraction * y_quantity * self.k_tilde**2 / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_unp, list) or isinstance(s_1_zero_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp: {s_1_zero_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp: {s_1_zero_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_unp to be:\n{s_1_zero_plus_unp}")

            # (4): Return the coefficient:
            return s_1_zero_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the quantity (1 + self.epsilon^2)^{2}:
            one_plus_epsilon_squared_squared = (1. + self.epsilon**2)**2

            # (2): Calculate the quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate a fancy, annoying quantity:
            fancy_y_stuff = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (4): Calculate the bracket term:
            bracket_term = 4. * (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared * (1. + self.kinematics.x_Bjorken * t_over_Q_squared) + self.epsilon**2 * (1. + t_over_Q_squared)**2

            # (5): Calculate the prefactor:
            prefactor = 4. * self.math.sqrt(2. * fancy_y_stuff) * self.lepton_polarization * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) * self.kinematics.x_Bjorken * t_over_Q_squared / one_plus_epsilon_squared_squared

            # (6): Calculate the coefficient
            s_1_zero_plus_unp_V = prefactor * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_unp_V, list) or isinstance(s_1_zero_plus_unp_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp_V: {s_1_zero_plus_unp_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp_V: {s_1_zero_plus_unp_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_unp_V to be:\n{s_1_zero_plus_unp_V}")

            # (7): Return the coefficient:
            return s_1_zero_plus_unp_V

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_unp_V for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the quantity (1 + self.epsilon^2)^{2}:
            one_plus_epsilon_squared_squared = (1. + self.epsilon**2)**2

            # (2): Calculate a fancy, annoying quantity:
            fancy_y_stuff = self.math.sqrt(1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (3): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2.) * self.lepton_polarization * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) * (1. - 2. * self.kinematics.x_Bjorken) / one_plus_epsilon_squared_squared

            # (4): Calculate the coefficient
            s_1_zero_plus_unp_A = prefactor * fancy_y_stuff * self.kinematics.squared_hadronic_momentum_transfer_t * self.kinematic_k**2 / self.kinematics.squared_Q_momentum_transfer
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_unp_A, list) or isinstance(s_1_zero_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp_A: {s_1_zero_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_unp_A: {s_1_zero_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_unp_A to be:\n{s_1_zero_plus_unp_A}")

            # (5): Return the coefficient:
            return s_1_zero_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_plus_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the quantity t'/Q^{2}:
            tPrime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate a fancy, annoying quantity:
            fancy_y_stuff = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (4): Calculate the first bracket term:
            first_bracket_term = (self.epsilon**2 - self.kinematics.x_Bjorken * (root_one_plus_epsilon_squared - 1.)) / (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken)

            # (5): Calculate the second bracket term:
            second_bracket_term = (2. * self.kinematics.x_Bjorken + self.epsilon**2) * tPrime_over_Q_squared / (2. * root_one_plus_epsilon_squared)

            # (6): Calculate the prefactor:
            prefactor = -4. * self.lepton_polarization * fancy_y_stuff * self.lepton_energy_fraction * (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * tPrime_over_Q_squared / root_one_plus_epsilon_squared**3

            # (7): Calculate the coefficient
            s_2_plus_plus_unp = prefactor * (first_bracket_term - second_bracket_term)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_unp, list) or isinstance(s_2_plus_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp: {s_2_plus_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp: {s_2_plus_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_unp to be:\n{s_2_plus_plus_unp}")

            # (6): Return the coefficient:
            return s_2_plus_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_plus_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate a fancy, annoying quantity:
            fancy_y_stuff = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (4): Calculate the bracket term:
            one_minus_2xb = 1. - 2. * self.kinematics.x_Bjorken

            # (5): Calculate the bracket term:
            bracket_term = root_one_plus_epsilon_squared - 1. + (one_minus_2xb + root_one_plus_epsilon_squared) * t_over_Q_squared

            # (6): Calculate the parentheses term:
            parentheses_term = 1. - one_minus_2xb * t_over_Q_squared

            # (7): Calculate the prefactor:
            prefactor = -4. * self.lepton_polarization * fancy_y_stuff * self.lepton_energy_fraction * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**4

            # (8): Calculate the coefficient
            s_2_plus_plus_unp_V = prefactor * parentheses_term * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_unp_V, list) or isinstance(s_2_plus_plus_unp_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp_V: {s_2_plus_plus_unp_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp_V: {s_2_plus_plus_unp_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_unp_V to be:\n{s_2_plus_plus_unp_V}")

            # (9): Return the coefficient:
            return s_2_plus_plus_unp_V

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_unp_V for Interference Term:\n> {ERROR}")
            return
        
    def calculate_s_2_plus_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the quantity t'/Q^{2}:
            tPrime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate a fancy, annoying quantity:
            fancy_y_stuff = 1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.

            # (5): Calculate the last term:
            last_term = 1. + (4. * (1. - self.kinematics.x_Bjorken) * self.kinematics.x_Bjorken + self.epsilon**2) * t_over_Q_squared / (4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2)

            # (6): Calculate the middle term:
            middle_term = 1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken

            # (7): Calculate the prefactor:
            prefactor = -8. * self.lepton_polarization * fancy_y_stuff * self.lepton_energy_fraction * t_over_Q_squared * tPrime_over_Q_squared / root_one_plus_epsilon_squared**4

            # (8): Calculate the coefficient
            s_2_plus_plus_unp_A = prefactor * middle_term * last_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_unp_A, list) or isinstance(s_2_plus_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp_A: {s_2_plus_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_unp_A: {s_2_plus_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_unp_A to be:\n{s_2_plus_plus_unp_A}")

            # (9): Return the coefficient:
            return s_2_plus_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_unpolarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity self.epsilon^2/2:
            self.epsilon_squared_over_2 = self.epsilon**2 / 2.

            # (3): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (4): Calculate the bracket term:
            bracket_term = 1. + ((1. + self.epsilon_squared_over_2 / self.kinematics.x_Bjorken) / (1. + self.epsilon_squared_over_2)) * self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the prefactor:
            prefactor = 8. * self.lepton_polarization * self.math.sqrt(2. * y_quantity) * self.kinematic_k * self.lepton_energy_fraction / root_one_plus_epsilon_squared**4
            
            # (6): Calculate the coefficient:
            s_2_zero_plus_unp = prefactor * (1. + self.epsilon_squared_over_2) * bracket_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_zero_plus_unp, list) or isinstance(s_2_zero_plus_unp, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_unp: {s_2_zero_plus_unp[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_unp: {s_2_zero_plus_unp}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_zero_plus_unp to be:\n{s_2_zero_plus_unp}")

            # (7): Return the coefficient:
            return s_2_zero_plus_unp

        except Exception as ERROR:
            print(f"> Error in calculating s_2_zero_plus_unp for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_unpolarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the annoying y quantity:
            y_quantity = self.math.sqrt(1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.))

            # (4): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2.) * self.lepton_polarization * y_quantity * self.kinematic_k * self.lepton_energy_fraction * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (5): Calculate the coefficient:
            s_2_zero_plus_unp_V = prefactor * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_zero_plus_unp_V, list) or isinstance(s_2_zero_plus_unp_V, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_unp_V: {s_2_zero_plus_unp_V[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_unp_V: {s_2_zero_plus_unp_V}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_zero_plus_unp_V to be:\n{s_2_zero_plus_unp_V}")

            # (6): Return the coefficient:
            return s_2_zero_plus_unp_V

        except Exception as ERROR:
            print(f"> Error in calculating s_2_zero_plus_unp_V for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_unpolarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate 1 - x_{B}:
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (4): Calculate the annoying y quantity:
            y_quantity = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (5): Calculate the main term:
            main_term = 4. * one_minus_xb + 2. * self.epsilon**2 + 4. * t_over_Q_squared * (4. * self.kinematics.x_Bjorken * one_minus_xb + self.epsilon**2)
            
            # (6): Calculate part of the prefactor:
            prefactor = -2. * self.math.sqrt(2. * y_quantity) * self.lepton_polarization * self.kinematic_k * self.lepton_energy_fraction * t_over_Q_squared / root_one_plus_epsilon_squared**4
            
            # (7): Calculate the coefficient:
            c_2_zero_plus_unp_A = prefactor * main_term
            
            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_unp_A, list) or isinstance(c_2_zero_plus_unp_A, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_A: {c_2_zero_plus_unp_A[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_unp_A: {c_2_zero_plus_unp_A}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_unp_A to be:\n{c_2_zero_plus_unp_A}")

            # (8): Return the coefficient:
            return c_2_zero_plus_unp_A

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_unp_A for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the first term in the brackets: 
            first_bracket_term = (2. - self.lepton_energy_fraction)**2 * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the first part of the second term in brackets:
            second_bracket_term_first_part = 1. - self.lepton_energy_fraction + (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (5): Calculate the second part of the second term in brackets:
            second_bracket_term_second_part = self.kinematics.x_Bjorken * t_over_Q_squared - (self.epsilon**2 * (1. - t_over_Q_squared) / 2.)

            # (6): Calculate the third part of the second term in brackets:
            second_bracket_term_third_part = 1. + t_over_Q_squared * ((root_one_plus_epsilon_squared - 1. + 2. * self.kinematics.x_Bjorken) / (1. + root_one_plus_epsilon_squared))

            # (7): Stitch together the second bracket term:
            second_bracket_term = second_bracket_term_first_part * second_bracket_term_second_part * second_bracket_term_third_part

            # (8): Calculate the prefactor:
            prefactor = -4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * (1. + root_one_plus_epsilon_squared) / root_one_plus_epsilon_squared**5

            # (9): Calculate the entire thing:
            c_0_plus_plus_LP = prefactor * (first_bracket_term + second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_LP, list) or isinstance(c_0_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_LP: {c_0_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_LP: {c_0_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_LP to be:\n{c_0_plus_plus_LP}")

            # (10): Return the coefficient:
            return c_0_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

                # (4): Calculate the first term in the brackets:
            first_bracket_term = (2. - self.lepton_energy_fraction)**2 * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) * self.k_tilde**2 / (self.kinematics.squared_Q_momentum_transfer * one_plus_root_epsilon_stuff)
            
            # (5): Calculate the first part of the second term in brackets:
            second_bracket_term_first_part = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (6): Calculate the second part of the second term in brackets:
            second_bracket_term_second_part = 2. - self.kinematics.x_Bjorken + 3. * self.epsilon**2 / 2

            # (7): Calculate the third part of the second term in brackets:
            second_bracket_term_third_part = 1. + (t_over_Q_squared * (4. * (1. - self.kinematics.x_Bjorken) * self.kinematics.x_Bjorken + self.epsilon**2) / (4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2))

            # (8): Calculate the fourth part of the second term in brackets:
            second_bracket_term_fourth_part = 1. + (t_over_Q_squared * (one_plus_root_epsilon_stuff - 2. + 2. * self.kinematics.x_Bjorken) / one_plus_root_epsilon_stuff)

            # (9): Stitch together the second bracket term:
            second_bracket_term = second_bracket_term_first_part * second_bracket_term_second_part * second_bracket_term_third_part * second_bracket_term_fourth_part

            # (10): Calculate the prefactor:
            prefactor = 4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * one_plus_root_epsilon_stuff * t_over_Q_squared / root_one_plus_epsilon_squared**5

            # (11): Calculate the entire thing:
            c_0_plus_plus_V_LP = prefactor * (first_bracket_term + second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_V_LP, list) or isinstance(c_0_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_V_LP: {c_0_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_V_LP: {c_0_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_V_LP to be:\n{c_0_plus_plus_V_LP}")

            # (12): Return the coefficient:
            return c_0_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.

    def calculate_c_0_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate the first term in the brackets: 
            first_bracket_term = 2. * (2. - self.lepton_energy_fraction)**2 * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer
            
            # (5): Calculate the first part of the second term in brackets:
            second_bracket_term_first_part = 1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)

            # (6): Calculate the second part of the second term in brackets:
            second_bracket_term_second_part = 1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared

            # (7): Calculate the third part of the second term in brackets:
            second_bracket_term_third_part = 1. + (t_over_Q_squared * (root_one_plus_epsilon_squared - 1. + 2. * self.kinematics.x_Bjorken) / one_plus_root_epsilon_stuff)

            # (8): Stitch together the second bracket term:
            second_bracket_term = second_bracket_term_first_part * one_plus_root_epsilon_stuff * second_bracket_term_second_part * second_bracket_term_third_part

            # (9): Calculate the prefactor:
            prefactor = 4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * self.kinematics.x_Bjorken * t_over_Q_squared / root_one_plus_epsilon_squared**5

            # (10): Calculate the entire thing:
            c_0_plus_plus_A_LP = prefactor * (first_bracket_term + second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_plus_plus_A_LP, list) or isinstance(c_0_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_A_LP: {c_0_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_plus_plus_A_LP: {c_0_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_plus_plus_A_LP to be:\n{c_0_plus_plus_A_LP}")

            # (11): Return the coefficient:
            return c_0_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.

    def calculate_c_0_zero_plus_longitudinally_polarized(self) -> float:
        """
        ## Description: 
        We calculate the coefficient C++(n = 0) for the longitudinally-polarized
        target.

        ## Arguments:
        
        1. self.lepton_polarization (float)

        The helicity of the lepton beam. The number, while a float, 
        is usually either -1.0 or +1.0.

        ## Returns:
        
        1. c_0_zero_plus_LP (float)

        ## Examples:
        None
        """

        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = 8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * (1. - self.kinematics.x_Bjorken) * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate everything:
            c_0_zero_plus_LP = prefactor * root_combination_of_y_and_epsilon * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_LP, list) or isinstance(c_0_zero_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_LP: {c_0_zero_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_LP: {c_0_zero_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_LP to be:\n{c_0_zero_plus_LP}")

            # (4): Return the coefficient:
            return c_0_zero_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_0_zero_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the modulation to C_{0+}^{LP}:
            modulating_factor = (self.kinematics.x_Bjorken - (self.kinematics.squared_hadronic_momentum_transfer_t * (1. - 2. * self.kinematics.x_Bjorken) / self.kinematics.squared_Q_momentum_transfer)) / (1. - self.kinematics.x_Bjorken)

            # (2): Calculate the C_{0+}^{LP} coefficient:
            c_0_zero_plus_LP = self.calculate_c_0_zero_plus_longitudinally_polarized()

            # (3): Calculate everything:
            c_0_zero_plus_V_LP = c_0_zero_plus_LP * modulating_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_V_LP, list) or isinstance(c_0_zero_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_V_LP: {c_0_zero_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_V_LP: {c_0_zero_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_V_LP to be:\n{c_0_zero_plus_V_LP}")

            # (4): Return the coefficient:
            return c_0_zero_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.

    def calculate_c_0_zero_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = -8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate t/Q^2:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate everything:
            c_0_zero_plus_A_LP = prefactor * root_combination_of_y_and_epsilon * self.kinematics.x_Bjorken * t_over_Q_squared * (1. + t_over_Q_squared)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_0_zero_plus_A_LP, list) or isinstance(c_0_zero_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_A_LP: {c_0_zero_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_0_zero_plus_A_LP: {c_0_zero_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_0_zero_plus_A_LP to be:\n{c_0_zero_plus_A_LP}")

            # (5): Return the coefficient:
            return c_0_zero_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_0_zero_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2) - self.epsilon^2:
            one_plus_root_epsilon_minus_epsilon_squared = one_plus_root_epsilon_stuff - self.epsilon**2

            # (4): Calculate the major term:
            major_factor = 1. - ((self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer) * (1. - 2. * self.kinematics.x_Bjorken * (one_plus_root_epsilon_stuff + 1.) / one_plus_root_epsilon_minus_epsilon_squared))

            # (5): Calculate the prefactor:
            prefactor = -4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * self.kinematic_k * (2. - self.lepton_energy_fraction) / root_one_plus_epsilon_squared**5

            # (6): Calculate the entire thing:
            c_1_plus_plus_LP = prefactor * one_plus_root_epsilon_minus_epsilon_squared * major_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_LP, list) or isinstance(c_1_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_LP: {c_1_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_LP: {c_1_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_LP to be:\n{c_1_plus_plus_LP}")

            # (7): Return the coefficient:
            return c_1_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity 1 - x_{B}
            one_minus_xb = 1. - self.kinematics.x_Bjorken

            # (3): Calculate the recurrent quantity sqrt(1 + self.epsilon^2) + 2(1 - x_{B})
            root_epsilon_and_xb_quantity = root_one_plus_epsilon_squared + 2. * one_minus_xb

            # (4): Calculate the numerator of the insane factor:
            bracket_factor_numerator = 1. + ((1. - self.epsilon**2) / root_one_plus_epsilon_squared) - (2. * self.kinematics.x_Bjorken * (1. + (4. * one_minus_xb / root_one_plus_epsilon_squared)))

            # (5): Calculate the denominator of the insane factor:
            bracket_factor_denominator = 2. * root_epsilon_and_xb_quantity

            # (6): Calculate the bracket factor:
            bracket_factor = 1. - (self.t_prime * bracket_factor_numerator / (self.kinematics.squared_Q_momentum_transfer * bracket_factor_denominator))

            # (7): Calculate the prefactor:
            prefactor = 8. * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) / root_one_plus_epsilon_squared**4

            # (8): Calculate the entire thing:
            c_1_plus_plus_V_LP = prefactor * root_epsilon_and_xb_quantity * self.kinematics.squared_hadronic_momentum_transfer_t * bracket_factor / self.kinematics.squared_Q_momentum_transfer

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_V_LP, list) or isinstance(c_1_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_V_LP: {c_1_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_V_LP: {c_1_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_V_LP to be:\n{c_1_plus_plus_V_LP}")

            # (7): Return the coefficient:
            return c_1_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (2): Calculate the major factor
            major_factor = self.kinematics.x_Bjorken * t_over_Q_squared * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)

            # (3): Calculate the prefactor:
            prefactor = 16. * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction * (2. - self.lepton_energy_fraction) / self.math.sqrt(1. + self.epsilon**2)**5

            # (4): Calculate the entire thing:
            c_1_plus_plus_A_LP = prefactor * major_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_plus_plus_A_LP, list) or isinstance(c_1_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_A_LP: {c_1_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_plus_plus_A_LP: {c_1_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_plus_plus_A_LP to be:\n{c_1_plus_plus_A_LP}")

            # (5): Return the coefficient:
            return c_1_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_1_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_zero_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = -8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * (1. - self.lepton_energy_fraction) * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate everything:
            c_1_zero_plus_LP = prefactor * root_combination_of_y_and_epsilon * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_zero_plus_LP, list) or isinstance(c_1_zero_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_LP: {c_1_zero_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_LP: {c_1_zero_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_zero_plus_LP to be:\n{c_1_zero_plus_LP}")

            # (4): Return the coefficient:
            return c_1_zero_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_1_zero_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_1_zero_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = 8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization  * (2. - self.lepton_energy_fraction) * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate everything:
            c_1_zero_plus_V_LP = prefactor * root_combination_of_y_and_epsilon * self.kinematics.squared_hadronic_momentum_transfer_t * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer**2

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_1_zero_plus_V_LP, list) or isinstance(c_1_zero_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_V_LP: {c_1_zero_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_1_zero_plus_V_LP: {c_1_zero_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_1_zero_plus_V_LP to be:\n{c_1_zero_plus_V_LP}")

            # (4): Return the coefficient:
            return c_1_zero_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_1_zero_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate one of the multiplicative factors:
            first_multiplicative_factor = (-1. * one_plus_root_epsilon_stuff + 2.) - t_over_Q_squared * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken)

            # (5): Calculate the second multiplicative factor:
            second_multiplicative_factor = self.kinematics.x_Bjorken * t_over_Q_squared - (self.epsilon**2 * (1. - t_over_Q_squared) / 2.)

            # (6): Calculate the prefactor:
            prefactor = -4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * (1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / root_one_plus_epsilon_squared**5

            # (6): Calculate the entire thing:
            c_2_plus_plus_LP = prefactor * first_multiplicative_factor * second_multiplicative_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_LP, list) or isinstance(c_2_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_LP: {c_2_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_LP: {c_2_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_LP to be:\n{c_2_plus_plus_LP}")

            # (7): Return the coefficient:
            return c_2_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate one of the multiplicative factors:
            first_multiplicative_factor = (one_plus_root_epsilon_stuff - 2.) + t_over_Q_squared * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken)

            # (5): Calculate the second multiplicative factor:
            second_multiplicative_factor = 1. + (t_over_Q_squared * (4. * (1. - self.kinematics.x_Bjorken) * self.kinematics.x_Bjorken + self.epsilon**2 ) / (4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2))

            # (6): Calculate the second multiplicative factor:
            third_multiplicative_factor = t_over_Q_squared * (4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2)

            # (7): Calculate the prefactor:
            prefactor = -2. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * (1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / root_one_plus_epsilon_squared**5

            # (8): Calculate the entire thing:
            c_2_plus_plus_V_LP = prefactor * first_multiplicative_factor * second_multiplicative_factor * third_multiplicative_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_V_LP, list) or isinstance(c_2_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_V_LP: {c_2_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_V_LP: {c_2_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_V_LP to be:\n{c_2_plus_plus_V_LP}")

            # (9): Return the coefficient:
            return c_2_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the recurrent quantity 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (4): Calculate one of the multiplicative factors:
            first_multiplicative_factor = (1. - root_one_plus_epsilon_squared) - t_over_Q_squared * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken)

            # (5): Calculate the second multiplicative factor:
            second_multiplicative_factor = self.kinematics.x_Bjorken * t_over_Q_squared * (1. - t_over_Q_squared * (1. - 2. * self.kinematics.x_Bjorken))

            # (6): Calculate the prefactor:
            prefactor = 4. * self.lepton_polarization * self.target_polarization * self.lepton_energy_fraction * (1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / root_one_plus_epsilon_squared**5

            # (7): Calculate the entire thing:
            c_2_plus_plus_A_LP = prefactor * first_multiplicative_factor * second_multiplicative_factor

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_plus_plus_A_LP, list) or isinstance(c_2_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_A_LP: {c_2_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_plus_plus_A_LP: {c_2_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_plus_plus_A_LP to be:\n{c_2_plus_plus_A_LP}")

            # (8): Return the coefficient:
            return c_2_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_zero_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = -8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate everything:
            c_2_zero_plus_LP = prefactor * root_combination_of_y_and_epsilon * (1. + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_LP, list) or isinstance(c_2_zero_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_LP: {c_2_zero_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_LP: {c_2_zero_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_LP to be:\n{c_2_zero_plus_LP}")

            # (4): Return the coefficient:
            return c_2_zero_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_zero_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = 8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate everything:
            c_2_zero_plus_V_LP = prefactor * root_combination_of_y_and_epsilon * (1. - self.kinematics.x_Bjorken ) * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_V_LP, list) or isinstance(c_2_zero_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_V_LP: {c_2_zero_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_V_LP: {c_2_zero_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_V_LP to be:\n{c_2_zero_plus_V_LP}")

            # (4): Return the coefficient:
            return c_2_zero_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_c_2_zero_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 2)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate the "prefactor":
            prefactor = 8. * self.math.sqrt(2.) * self.lepton_polarization * self.target_polarization * self.kinematic_k * self.lepton_energy_fraction / (1. + self.epsilon**2)**2

            # (3): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer
            
            # (4): Calculate everything:
            c_2_zero_plus_A_LP = prefactor * root_combination_of_y_and_epsilon * self.kinematics.x_Bjorken * t_over_Q_squared * (1. + self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(c_2_zero_plus_A_LP, list) or isinstance(c_2_zero_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_A_LP: {c_2_zero_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated c_2_zero_plus_A_LP: {c_2_zero_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated c_2_zero_plus_A_LP to be:\n{c_2_zero_plus_A_LP}")

            # (5): Return the coefficient:
            return c_2_zero_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating c_2_zero_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (3): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate self.epsilon^{2} y^{2} / 4
            self.epsilon_y_over_2_squared = (self.epsilon * self.lepton_energy_fraction / 2.) ** 2

            # (5): Calculate the first bracket term:
            first_bracket_term = 2. * root_one_plus_epsilon_squared - 1. + (t_over_Q_squared * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) / one_plus_root_epsilon_stuff)

            # (6): Calculate the second multiplicative factor:
            second_bracket_term = (3. * self.epsilon**2 / 2.) + (t_over_Q_squared * (1. - root_one_plus_epsilon_squared - self.epsilon**2 / 2. - self.kinematics.x_Bjorken * (3.  - root_one_plus_epsilon_squared)))

            # (7): Calculate the almost prefactor:
            almost_prefactor = 4. * self.target_polarization * self.kinematic_k / root_one_plus_epsilon_squared**6

            # (8): Calculate prefactor one:
            prefactor_one = almost_prefactor * (2. - 2. * self.lepton_energy_fraction + self.lepton_energy_fraction**2 + 2. * self.epsilon_y_over_2_squared) * one_plus_root_epsilon_stuff

            # (9): Calculate prefactor two:
            prefactor_two = 2. * almost_prefactor * (1. - self.lepton_energy_fraction - self.epsilon_y_over_2_squared)
        
            # (10): Calculate the coefficient:
            s_1_plus_plus_LP = prefactor_one * first_bracket_term + prefactor_two * second_bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_LP, list) or isinstance(s_1_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_LP: {s_1_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_LP: {s_1_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_LP to be:\n{s_1_plus_plus_LP}")

            # (11): Return the coefficient:
            return s_1_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate self.epsilon squared:
            ep_squared = self.epsilon**2

            # (2): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + ep_squared)

            # (3): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the quantity t'/Q^{2}
            t_prime_over_Q_squared = self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate self.epsilon^{2} y^{2} / 4
            self.epsilon_y_over_2_squared = ep_squared * self.lepton_energy_fraction**2 / 4.

            # (6): Calculate the first bracket term:
            first_bracket_term = 1. - (t_prime_over_Q_squared * ((1. - 2. * self.kinematics.x_Bjorken) * (1. - 2. * self.kinematics.x_Bjorken + root_one_plus_epsilon_squared)) / (2. * root_one_plus_epsilon_squared**2))

            # (7): Calculate the second multiplicative factor:
            second_term_parentheses_term = t_over_Q_squared * (1. - (self.kinematics.x_Bjorken * ((3. + root_one_plus_epsilon_squared) / 4.)) + (5. * ep_squared / 8.))

            # (8): Calculate the numerator of the second term in brackets
            second_bracket_term_numerator = 1. - root_one_plus_epsilon_squared + (ep_squared / 2.) - (2. * self.kinematics.x_Bjorken * (3. * (1. - self.kinematics.x_Bjorken) - root_one_plus_epsilon_squared))
            
            # (9): Calculate the denominator of the second term in brackets
            second_bracket_term_denominator = 4. - (self.kinematics.x_Bjorken * (root_one_plus_epsilon_squared + 3.)) + (5. * ep_squared / 2.)

            # (10): Calculate the second bracket term:
            second_bracket_term = 1. - (t_over_Q_squared * second_bracket_term_numerator / second_bracket_term_denominator)
            
            # (11): Calculate the almost_prefactor:
            almost_prefactor = 8. * self.target_polarization * self.kinematic_k / root_one_plus_epsilon_squared**4

            # (12): Calculate the first prefactor:
            prefactor_one = almost_prefactor * (2. - 2. * self.lepton_energy_fraction + self.lepton_energy_fraction**2 + 2. * self.epsilon_y_over_2_squared) * t_over_Q_squared

            # (13): Calculate the second prefactor:
            prefactor_two = 4. * almost_prefactor * (1. - self.lepton_energy_fraction - self.epsilon_y_over_2_squared) / root_one_plus_epsilon_squared**2

            # (14): Calculate the coefficient:
            s_1_plus_plus_V_LP = prefactor_one * first_bracket_term + prefactor_two * second_term_parentheses_term * second_bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_V_LP, list) or isinstance(s_1_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_V_LP: {s_1_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_V_LP: {s_1_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_V_LP to be:\n{s_1_plus_plus_V_LP}")

            # (15): Return the coefficient:
            return s_1_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the recurrent quantity t/Q^{2}
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate the quantity x_{B} t/Q^{2}
            xB_t_over_Q_squared = self.kinematics.x_Bjorken * t_over_Q_squared

            # (4): Calculate 3 + sqrt(1 + self.epsilon^2)
            three_plus_root_epsilon_stuff = 3 + root_one_plus_epsilon_squared

            # (5): Calculate self.epsilon^{2} y^{2} / 4
            self.epsilon_y_over_2_squared = (self.epsilon * self.lepton_energy_fraction / 2.) ** 2

            # (6): Calculate the almost prefactor
            almost_prefactor = 8. * self.target_polarization * self.kinematic_k / root_one_plus_epsilon_squared**6

            # (7): Calculate the first bracket term:
            first_bracket_term = root_one_plus_epsilon_squared - 1. + (t_over_Q_squared * (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken))

            # (8): Calculate the second bracket term:
            second_bracket_term = 1. - (t_over_Q_squared * (3.  - root_one_plus_epsilon_squared - 6. * self.kinematics.x_Bjorken) / three_plus_root_epsilon_stuff)

            # (9): Calculate the first prefactor:
            prefactor_one = -1. * almost_prefactor * (2. - 2. * self.lepton_energy_fraction + self.lepton_energy_fraction**2 + 2. * self.epsilon_y_over_2_squared) * xB_t_over_Q_squared

            # (10): Calculate the second prefactor:
            prefactor_two = almost_prefactor * (1. - self.lepton_energy_fraction - self.epsilon_y_over_2_squared) * three_plus_root_epsilon_stuff * xB_t_over_Q_squared

            # (11): Calculate the coefficient:
            s_1_plus_plus_A_LP = prefactor_one * first_bracket_term + prefactor_two * second_bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_plus_plus_A_LP, list) or isinstance(s_1_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_A_LP: {s_1_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_plus_plus_A_LP: {s_1_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_plus_plus_A_LP to be:\n{s_1_plus_plus_A_LP}")

            # (12): Return the coefficient:
            return s_1_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity 1 - y - y^{2} self.epsilon^{2} / 4
            combination_of_y_and_epsilon = 1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)

            # (2): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate first bracket term:
            first_bracket_term = self.k_tilde**2 * (2. - self.lepton_energy_fraction)**2 / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the second bracket term:
            second_bracket_term = (1. + t_over_Q_squared) * combination_of_y_and_epsilon * (2. * self.kinematics.x_Bjorken * t_over_Q_squared - (self.epsilon**2 * (1. - t_over_Q_squared)))
            
            # (5): Calculate the prefactor:
            prefactor = 8. * self.math.sqrt(2.) * self.target_polarization  * self.math.sqrt(combination_of_y_and_epsilon) / self.math.sqrt((1. + self.epsilon**2)**5)

            # (6): Calculate everything:
            s_1_zero_plus_LP = prefactor * (first_bracket_term + second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_LP, list) or isinstance(s_1_zero_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_LP: {s_1_zero_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_LP: {s_1_zero_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_LP to be:\n{s_1_zero_plus_LP}")

            # (7): Return the coefficient:
            return s_1_zero_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity 1 - y - y^{2} self.epsilon^{2} / 4
            combination_of_y_and_epsilon = 1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)

            # (2): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate first bracket term:
            first_bracket_term = self.k_tilde**2 * (2. - self.lepton_energy_fraction)**2 / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate a long contribution to the second bracket term:
            second_bracket_term_long = 4. - 2. * self.kinematics.x_Bjorken + 3. * self.epsilon**2 + t_over_Q_squared * (4. * self.kinematics.x_Bjorken * (1. - self.kinematics.x_Bjorken) + self.epsilon**2)

            # (5): Calculate the second bracket term:
            second_bracket_term = (1. + t_over_Q_squared) * combination_of_y_and_epsilon * second_bracket_term_long
            
            # (6): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2.) * self.target_polarization  * self.math.sqrt(combination_of_y_and_epsilon) * t_over_Q_squared / self.math.sqrt((1. + self.epsilon**2)**5)

            # (7): Calculate everything:
            s_1_zero_plus_V_LP = prefactor * (first_bracket_term + second_bracket_term)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_V_LP, list) or isinstance(s_1_zero_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_V_LP: {s_1_zero_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_V_LP: {s_1_zero_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_V_LP to be:\n{s_1_zero_plus_V_LP}")

            # (7): Return the coefficient:
            return s_1_zero_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_1_zero_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity (1 - y - y^{2} self.epsilon^{2} / 4)^{3/2}
            combination_of_y_and_epsilon_to_3_halves = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))**3

            # (2): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer
            
            # (3): Calculate the prefactor:
            prefactor = -16. * self.math.sqrt(2.) * self.target_polarization * self.kinematics.x_Bjorken * t_over_Q_squared * (1. + t_over_Q_squared) / self.math.sqrt((1. + self.epsilon**2)**5)

            # (4): Calculate everything:
            s_1_zero_plus_A_LP = prefactor * combination_of_y_and_epsilon_to_3_halves * (1. - (1. - 2. * self.kinematics.x_Bjorken) * t_over_Q_squared)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_1_zero_plus_A_LP, list) or isinstance(s_1_zero_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_A_LP: {s_1_zero_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_1_zero_plus_A_LP: {s_1_zero_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_1_zero_plus_A_LP to be:\n{s_1_zero_plus_A_LP}")

            # (5): Return the coefficient:
            return s_1_zero_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_1_zero_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate 1 + sqrt(1 + self.epsilon^2)
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (3): Calculate 4 * Kt^{2} * (1 + sqrt(1 + e^{2})) * (1 + sqrt(1 + e^{2}) + xb t / Q^{2})t'/Q^{2}
            bracket_term = 4. * self.k_tilde**2 * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) * (one_plus_root_epsilon_stuff + self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer) * self.t_prime / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer**2)

            # (4): Calculate the prefactor
            prefactor = -4. * self.target_polarization * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - (self.epsilon**2 * self.lepton_energy_fraction**2 / 4.)) / root_one_plus_epsilon_squared**5

            # (5): Calculate the coefficient
            s_2_plus_plus_LP = prefactor * bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_LP, list) or isinstance(s_2_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_LP: {s_2_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_LP: {s_2_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_LP to be:\n{s_2_plus_plus_LP}")

            # (6): Return the coefficient:
            return s_2_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the first contribution to the bracket term:
            bracket_term_second_term = (3.  - root_one_plus_epsilon_squared - (2. * self.kinematics.x_Bjorken) + (self.epsilon**2 / self.kinematics.x_Bjorken)) * self.kinematics.x_Bjorken * self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate second contribution to the bracket term:
            bracket_term_first_term = 4. * self.k_tilde**2 * (1. - 2. * self.kinematics.x_Bjorken) / (root_one_plus_epsilon_squared * self.kinematics.squared_Q_momentum_transfer)

            # (4): Calculate the bracket term:
            bracket_term = self.kinematics.squared_hadronic_momentum_transfer_t * (bracket_term_first_term - bracket_term_second_term) / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the prefactor:
            prefactor = 4. * self.target_polarization * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) / root_one_plus_epsilon_squared**5

            # (6): Calculate the coefficient
            s_2_plus_plus_V_LP = prefactor * bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_V_LP, list) or isinstance(s_2_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_V_LP: {s_2_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_V_LP: {s_2_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_V_LP to be:\n{s_2_plus_plus_V_LP}")

            # (7): Return the coefficient:
            return s_2_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the first contribution to the bracket term:
            bracket_term_first_term = (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) * (1. - ((1. - 2. * self.kinematics.x_Bjorken) * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer)) * self.t_prime / self.kinematics.squared_Q_momentum_transfer

            # (3): Calculate second contribution to the bracket term:
            bracket_term_second_term = 4. * self.k_tilde**2 / self.kinematics.squared_Q_momentum_transfer

            # (4): Calculate the bracket term:
            bracket_term = self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t * (bracket_term_second_term - bracket_term_first_term) / self.kinematics.squared_Q_momentum_transfer

            # (5): Calculate the prefactor:
            prefactor = 4. * self.target_polarization * (2. - self.lepton_energy_fraction) * (1. - self.lepton_energy_fraction - self.epsilon**2 * self.lepton_energy_fraction**2 / 4.) / root_one_plus_epsilon_squared**5

            # (6): Calculate the coefficient
            s_2_plus_plus_A_LP = prefactor * bracket_term

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_plus_plus_A_LP, list) or isinstance(s_2_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_A_LP: {s_2_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_plus_plus_A_LP: {s_2_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_plus_plus_A_LP to be:\n{s_2_plus_plus_A_LP}")

            # (7): Return the coefficient:
            return s_2_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 4)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))
            
            # (2): Calculate the prefactor:
            prefactor = 8. * self.math.sqrt(2.) * self.target_polarization * self.kinematic_k * (2. - self.lepton_energy_fraction )/ self.math.sqrt((1. + self.epsilon**2)**5)

            # (3): Calculate everything:
            s_2_zero_plus_LP = prefactor * root_combination_of_y_and_epsilon * (1. + (self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer))

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_zero_plus_LP, list) or isinstance(s_2_zero_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_LP: {s_2_zero_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_LP: {s_2_zero_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_zero_plus_LP to be:\n{s_2_zero_plus_LP}")

            # (4): Return the coefficient:
            return s_2_zero_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_zero_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 4)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))
            
            # (2): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2.) * self.target_polarization * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.kinematics.squared_hadronic_momentum_transfer_t / (self.math.sqrt((1. + self.epsilon**2)**5) * self.kinematics.squared_Q_momentum_transfer)

            # (3): Calculate everything:
            s_2_zero_plus_V_LP = prefactor * (1. - self.kinematics.x_Bjorken) * root_combination_of_y_and_epsilon

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_zero_plus_V_LP, list) or isinstance(s_2_zero_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_V_LP: {s_2_zero_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_V_LP: {s_2_zero_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_zero_plus_V_LP to be:\n{s_2_zero_plus_V_LP}")

            # (4): Return the coefficient:
            return s_2_zero_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_zero_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_2_zero_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the annoying quantity sqrt(1 - y - y^{2} self.epsilon^{2} / 4)
            root_combination_of_y_and_epsilon = self.math.sqrt(1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.))

            # (2): Calculate t/Q^{2}:
            t_over_Q_squared = self.kinematics.squared_hadronic_momentum_transfer_t / self.kinematics.squared_Q_momentum_transfer
            
            # (3): Calculate the prefactor:
            prefactor = -8. * self.math.sqrt(2.) * self.target_polarization  * self.kinematic_k * (2. - self.lepton_energy_fraction) * self.kinematics.x_Bjorken * t_over_Q_squared / self.math.sqrt((1. + self.epsilon**2)**5)

            # (4): Calculate everything:
            s_2_zero_plus_A_LP = prefactor * root_combination_of_y_and_epsilon * (1. + t_over_Q_squared)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_2_zero_plus_A_LP, list) or isinstance(s_2_zero_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_A_LP: {s_2_zero_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_2_zero_plus_A_LP: {s_2_zero_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_2_zero_plus_A_LP to be:\n{s_2_zero_plus_A_LP}")

            # (5): Return the coefficient:
            return s_2_zero_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_2_zero_plus_A_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_3_plus_plus_longitudinally_polarized(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate 1 + sqrt(1 + self.epsilon^2):
            one_plus_root_epsilon_stuff = 1. + root_one_plus_epsilon_squared

            # (3): Calculate the coefficient
            prefactor = -4. * self.target_polarization * self.kinematic_k * (1. - self.lepton_energy_fraction - self.lepton_energy_fraction**2 * self.epsilon**2 / 4.) / root_one_plus_epsilon_squared**6

            # (4): Calculate the coefficient:
            s_3_plus_plus_LP = prefactor * (one_plus_root_epsilon_stuff - 2. * self.kinematics.x_Bjorken) * self.epsilon**2 * self.t_prime / (self.kinematics.squared_Q_momentum_transfer * one_plus_root_epsilon_stuff)

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_3_plus_plus_LP, list) or isinstance(s_3_plus_plus_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_LP: {s_3_plus_plus_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_LP: {s_3_plus_plus_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_3_plus_plus_LP to be:\n{s_3_plus_plus_LP}")

            # (5): Return the coefficient:
            return s_3_plus_plus_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_3_plus_plus_LP for Interference Term:\n> {ERROR}")
            return 0.
        
    def calculate_s_3_plus_plus_longitudinally_polarized_v(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the main contribution:
            multiplicative_contribution = self.kinematics.squared_hadronic_momentum_transfer_t * self.t_prime * (4. * (1. - self.kinematics.x_Bjorken) * self.kinematics.x_Bjorken + self.epsilon**2) / self.kinematics.squared_Q_momentum_transfer**2

            # (3): Calculate the coefficient
            prefactor = 4. * self.target_polarization * self.kinematic_k * (1. - self.lepton_energy_fraction - self.lepton_energy_fraction**2 * self.epsilon**2 / 4.) / root_one_plus_epsilon_squared**6

            # (4): Calculate the coefficient:
            s_3_plus_plus_V_LP = prefactor * multiplicative_contribution

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_3_plus_plus_V_LP, list) or isinstance(s_3_plus_plus_V_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_V_LP: {s_3_plus_plus_V_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_V_LP: {s_3_plus_plus_V_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_3_plus_plus_V_LP to be:\n{s_3_plus_plus_V_LP}")

            # (5): Return the coefficient:
            return s_3_plus_plus_V_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_3_plus_plus_V_LP for Interference Term:\n> {ERROR}")
            return 0.
    
    def calculate_s_3_plus_plus_longitudinally_polarized_a(self) -> float:
        """
        Later!
        """
        try:

            # (1): Calculate the recurrent quantity sqrt(1 + self.epsilon^2):
            root_one_plus_epsilon_squared = self.math.sqrt(1. + self.epsilon**2)

            # (2): Calculate the main contribution:
            multiplicative_contribution = self.kinematics.x_Bjorken * self.kinematics.squared_hadronic_momentum_transfer_t * self.t_prime * (1. + root_one_plus_epsilon_squared - 2. * self.kinematics.x_Bjorken) / self.kinematics.squared_Q_momentum_transfer**2

            # (3): Calculate the coefficient
            prefactor = -8. * self.target_polarization * self.kinematic_k * (1. - self.lepton_energy_fraction - (self.lepton_energy_fraction**2 * self.epsilon**2 / 4.)) / root_one_plus_epsilon_squared**6

            # (4): Calculate the coefficient:
            s_3_plus_plus_A_LP = prefactor * multiplicative_contribution

            # (5): If verbose, log that the calculation finished!
            if self.verbose:
                if isinstance(s_3_plus_plus_A_LP, list) or isinstance(s_3_plus_plus_A_LP, np.ndarray):
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_A_LP: {s_3_plus_plus_A_LP[0]}")
                else:
                    print(f"> [VERBOSE]: Successfully calculated s_3_plus_plus_A_LP: {s_3_plus_plus_A_LP}")
            
            # (6): If debugging, log the entire output:
            if self.debugging:
                print(f"> [VERBOSE]: Calculated s_3_plus_plus_A_LP to be:\n{s_3_plus_plus_A_LP}")

            # (5): Return the coefficient:
            return s_3_plus_plus_A_LP

        except Exception as ERROR:
            print(f"> Error in calculating s_3_plus_plus_A_LP for Interference Term:\n> {ERROR}")
            
            return 0.