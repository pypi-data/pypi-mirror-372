The BKM10 formalism as a Python library.

## Description:
A Python library to help nuclear physicists use the BKM formalism in predicting cross-section, asymmetries, and comparing GPD models.

## Installation:

Available on PyPI. To install, one can run

```bash
pip install bkm10
```

You will need Python 3 and pip.

## Technicalities:
There are three different classes at play in this library: the main one, `DifferentialCrossSection`; the dataclass, `BKM10Inputs`; and another dataclass called `CFFInputs`. `DifferentialCrossSection` requires a million different inputs.

### The Four-Fold Cross Section:

What we are numerically calculating is a four-fold (meaning, we need to do four integrals) cross section. We need to integrate over four variables: $Q^{2}$ , $x_{B}$ , $t$, $\phi$ . By the way, the first three quantities are called the *kinematics*, and $\phi$ is an azimuthal angle that is measured in a chosen reference frame. However, the function actually requires a bit more detail. It is a function of several different things -- schematically, we express this as:

$$d^{4}\sigma \left(\lambda, \Lambda; k, Q^{2} , x_{B} , t , \phi; \mathcal{H}, \mathcal{E}, \tilde{\mathcal{H}}, \tilde{\mathcal{E}} \right).$$

### Polarization Settings:

The BKM10 formalism uses $\lambda$ to refer to the lepton beam helicity. (Note: $\lambda \in \{ -1, +1 \}$ in this formalism!) $\Lambda$ refers to the target polarization. (In the formalism, $\Lambda \in \{ -1/2, +1/2 \}$.)

### Kinematics:

In order to evaluate the cross-section, you need to specify four numbers that correspond to the kinematic settings (experimental kinematics). These numbers are: $k$, the beam energy; $Q^{2}$, the virtuality of the photon probing the nucleon's partons; $x_{B}$, Bjorken $x$; and $t$, the (squared) momentum transfer to the hadron. Use the dataclass `BKM10Inputs` to specify these kinematic settings.

Note: the library *currently does not* handle exceptions where the provided kinematic inputs correspond to illegal mathematical operations, like division by $0$ and such. These exceptions usually correspond to unphysical kinematic settings.

### Compton Form Factors:

There are four CFFs involved in the computation: $\mathcal{H}, \mathcal{E}, \tilde{\mathcal{H}}, \tilde{\mathcal{E}}$. Each of them is a complex function, so there are technically eight real numbers here. (Remember: any $z \in \mathbb{C}$ is $z = x + i y$, where $x, y \in \mathbb{R}$.) Use the dataclass `CFFInputs` to specify the values of these CFFs. (Note: they are of `complex` type!)

## Goals/Future Work:

- Provide the opportunity to compute the differential cross-section using the BKM02 formalism.
- Integrate the functionality to actually *do* the integral over a *given* GPD model to obtain the CFFs, and *then* compute the differential cross-section.

## Physics Terminology:

BKM: names of three authors: A.V. **B**elitsky, D. **B**uller, A. **K**irchner,

QCD: "Quantum Chromodynamics"

CFF: "Compton Form Factor"

TMD: "Transverse Momentum Distribution"

GPD: "Generalized Parton Distribution (function)"