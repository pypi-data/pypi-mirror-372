"""
A module to calculate the derivative of the
polarisation with respect to phonon mode displacements.
"""
import numpy as np

from phonopy.file_IO import parse_BORN
from phonopy.structure.atoms import Atoms
from vasp_suite.structure import Structure

import jax.numpy as jnp
from jax import grad, jit

#
#           Notes:
#           ------
#           Dependency on spglib version 2.0.2,
#           Newer versions of spglib are not compatible with phonopy
#
#           dmu_dQ is in units of [C].
#           This makes line 2303 of firm_sim.f90 redundant
#           Conditional if statement required to not convert units
#
#


def parse_BEC(poscar_file, born_file):
    """
    Parse the Born effective charge tensors from the 'BORN' file
    produced by Phonopy.

    Parameters
    ----------
    poscar_file : str
        The path to the POSCAR file.

    Returns
    -------
    BEC : ndarray of shape (N, 3, 3)
    """
    poscar = Structure.from_poscar(poscar_file)
    cell = Atoms(symbols=poscar.atom_list, cell=poscar.lattice_vectors,
                 scaled_positions=poscar.coords)
    born = parse_BORN(cell, filename=born_file)
    return np.array([tensor for tensor in born['born']])


def normalised_sphere_vectors(num_points):
    polar_vectors = sample_sphere(num_points)
    cartesian_vectors = np.array(list(map(polar_to_cartesian, polar_vectors)))
    return cartesian_vectors


def polar_to_cartesian(polar_vector):
    theta, phi = polar_vector
    x = 1 * np.sin(theta) * np.cos(phi)
    y = 1 * np.sin(theta) * np.sin(phi)
    z = 1 * np.cos(theta)
    return np.array([x, y, z])


def sample_sphere(num_points):
    angles = np.linspace(0, 2 * np.pi, num_points)
    polar_vectors = list(map(lambda x: list(map(lambda y: [x,  y], angles)), angles))
    return np.array(polar_vectors).reshape(-1, 2)
