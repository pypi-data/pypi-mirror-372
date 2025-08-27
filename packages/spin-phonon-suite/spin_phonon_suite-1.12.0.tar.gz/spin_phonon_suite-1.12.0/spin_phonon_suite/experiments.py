import numpy as np
from ase.data import chemical_symbols
from hpc_suite.store import Store

from .vibrations import Harmonic


def make_exp_evaluator(vibration_info, select):

    ho = Harmonic.from_file(vibration_info)

    item, option_str = select

    options = {
        "nweights": {'approx': option_str}
    }[item]

    evaluator = {
        "nweights": NWeights
    }[item]

    return evaluator(ho, **options)


class ExpEvaluator:
    pass


class NWeights(Store):

    def __init__(self, ho, approx='incoherent'):
        self.ho = ho
        self.approx = approx

        description = ("Neutron scattering weights computed within the "
                       f"{self.approx} approximation")

        super().__init__("neutron_scattering_weights", description, label=())

    def evaluate(self):
        return compute_nweights(self.ho, approx=self.approx)

    def __iter__(self):
        yield (), self.evaluate()


# incoherent neutron scattering cross section in barn
# from Mitchell et al. (2005) Vibrational Spectroscopy with Neutrons, World Scientific
incoherent_cross_section = {
    "Ag": 0.58,
    "Al": 0.0082,
    "Ar": 0.225,
    "As": 0.06,
    "Au": 0.43,
    "B": 1.7,
    "Ba": 0.15,
    "Be": 0.0018,
    "Bi": 0.0084,
    "Br": 0.1,
    "C": 0.001,
    "Ca": 0.05,
    "Cd": 3.46,
    "Ce": 0.001,
    "Cl": 5.3,
    "Co": 4.8,
    "Cr": 1.83,
    "Cs": 0.21,
    "Cu": 0.55,
    "Dy": 54.4,
    "Er": 1.1,
    "Eu": 2.5,
    "F": 0.0008,
    "Fe": 0.4,
    "Fr": 0.0,
    "Ga": 0.16,
    "Gd": 151.0,
    "Ge": 0.18,
    "H": 80.26,
    "He": 0.0,
    "Hf": 2.6,
    "Hg": 6.6,
    "Ho": 0.36,
    "I": 0.31,
    "In": 0.54,
    "Ir": 0.0,
    "K": 0.27,
    "Kr": 0.01,
    "La": 1.13,
    "Li": 0.92,
    "Lu": 0.7,
    "Mg": 0.08,
    "Mn": 0.4,
    "Mo": 0.04,
    "N": 0.5,
    "Na": 1.62,
    "Nb": 0.0024,
    "Nd": 9.2,
    "Ne": 0.008,
    "Ni": 5.2,
    "O": 0.0008,
    "Os": 0.3,
    "P": 0.005,
    "Pa": 0.1,
    "Pb": 0.003,
    "Pd": 0.093,
    "Pm": 1.3,
    "Pr": 0.015,
    "Pt": 0.13,
    "Ra": 0.0,
    "Rb": 0.5,
    "Re": 0.9,
    "Rh": 0.3,
    "Rn": 0.0,
    "Ru": 0.4,
    "S": 0.007,
    "Sb": 0.007,
    "Sc": 4.5,
    "Se": 0.32,
    "Si": 0.004,
    "Sm": 39,
    "Sn": 0.022,
    "Sr": 0.06,
    "Ta": 0.01,
    "Tb": 0.004,
    "Tc": 0.5,
    "Te": 0.09,
    "Th": 0,
    "Ti": 2.87,
    "Tl": 0.21,
    "Tm": 0.1,
    "U": 0.005,
    "V": 5.08,
    "W": 1.63,
    "Xe": 0,
    "Y": 0.15,
    "Yb": 4,
    "Zn": 0.077,
    "Zr": 0.02
}

def compute_nweights(vib, approx='incoherent'):

    if approx == 'incoherent':
        cross_section_dict = incoherent_cross_section
    else:
        raise NotImplementedError(f"Approximation {approx} not implemented!")

    cross_secs = np.array([cross_section_dict[chemical_symbols[num]] for num in vib.atomic_nums])

    nweights = np.sum(cross_secs * np.sum(vib.displacements.real**2 + vib.displacements.imag**2, axis=2), axis=1)

    return nweights

