from operator import add, mul
from functools import reduce, partial
from itertools import product
from fractions import Fraction
import numpy as np
import scipy as sp
import h5py
from ase.data import atomic_numbers
from pymatgen.core.structure import Structure
import phonopy
from phonopy.harmonic.dynmat_to_fc import get_commensurate_points
from scipy.constants import physical_constants

from vasp_suite.parser import ParseOUTCAR
import vasp_suite.hessian as outcar_hess

from gaussian_suite.extractor import make_extractor as make_gaussian_extractor

from env_suite.cells import build_cluster

import matplotlib.pyplot as plt

C0 = 299.792458e6
BOHR2M = 5.29177210903e-11
AMU = 1.66053906660e-27
HARTREE2J = 4.3597447222071e-18
EV2J = 1.602176634e-19
H_PCK = 6.62607015E-34
E0_TO_C = physical_constants['atomic unit of charge'][0]
HZ2HARTREE = 1.51983e-16


class Harmonic:
    """Set of indenpendent quantum harmonic oscillators defined by their
    frequencies, displacements and reduced masses. The coordinate system
    follows the same conventions as the Gaussian software, i.e. the cartesian
    displacements are normalised and the normalisation constant is absorbed
    into the reduced mass.

    Parameters
    ----------
    freqs : np.array
        Array of harmonic frequencies in cm^-1.
    displacements : np.array
        K x N x 3 array containing the mass-weighted displacement vectors.

    Attributes
    ----------
    freqs : np.array
        Array of harmonic frequencies in units of cm^-1.
    displacements : np.array
        K x N x 3 array containing the mass-weighted displacement vectors.
    natoms : int
        Number of atoms.
    nmodes : int
        Number of modes.
    force_const : np.array
        Array of force constants in units of mdyne/ang or N/cm.
    zpd : np.array
        Array of zero point displacements in ang.
    """

    def __init__(self, freqs, displacements, coords=None, atomic_nums=None,
                 weights=None, band_indices=None, q_points=None):

        self.nmodes = displacements.shape[0]
        self.natoms = displacements.shape[1]

        if freqs.shape[0] != self.nmodes:
            raise ValueError("Dimensions of HO parameters do not match.")

        self.freqs = freqs
        self.displacements = displacements

        self.coords = coords
        self.atomic_nums = atomic_nums

        self.weights = weights
        self.band_indices = band_indices
        self.q_points = q_points

    @property
    def mass_freq_weighted_coordinates(self):
        """Mass-frequency weighted normal mode displacements. Equivalent to the
        conversion to zero-point displacement weighted coordinates divided by
        sqrt(2)."""
        conversion = 1.0e10 / np.sqrt(AMU) * np.sqrt(H_PCK / (4 * np.pi) / self.omega)
        return self.displacements * conversion[:, np.newaxis, np.newaxis]

    @property
    def omega(self):
        """angular frequency in s^-1"""
        return 2 * np.pi * (self.freqs * 100 * C0)

    @property
    def red_masses(self):
        """Reduced masses in amu"""
        return np.sum(self.displacements**2, axis=0)

    @property
    def mode_red_masses(self):
        """Reduced masses of each mode in amu"""
        return np.sum(self.displacements**2, axis=(1,2))

    def calculate_dmudQ(self, bec_tensors):
        """
        Calculate the derivative of the polarisation with respect to
        phonon mode displacements.

        dmu/dQ = sum^n_j sum^3_b Z^*_{j,ab} X_{s,jb}

        Parameters
        ----------
        bec_tensors : ndarray of shape (N, 3, 3)
            The Born effective charge tensors.
        eigenvectors : ndarray of shape (3N, N, 3)
            The phonon eigenvectors.
        atomic_masses : ndarray of shape (N,)
            The atomic masses.

        Returns
        -------
        dmudQ : ndarray of shape (3N, 3)
            The derivative of the polarisation with respect to
            phonon mode displacements.
        """
        # tile the tensors to match the eigenvectors
        mult = int(self.displacements.shape[1] // bec_tensors.shape[0])
        if mult != 1:
            bec_tensors = np.tile(bec_tensors, (mult, 1, 1))
        assert bec_tensors.shape[0] == self.displacements.shape[1]

        # units e0 amu^{-1/2}
        dmu_dQ = np.einsum('jba, sjb -> sa', bec_tensors, self.displacements)
        # convert to C amu^{-1/2}
        dmu_dQ *= E0_TO_C
        # Normalise over the periodic images
        dmu_dQ /= mult

        return dmu_dQ

    def to_file(self, h_file, store_vecs=True):

        with h5py.File(h_file, 'w') as h:
            h['/'].attrs.create('num_modes', self.nmodes)
            h['/'].attrs.create('num_atoms', self.natoms)
            h.create_dataset('frequencies', data=self.freqs)

            if store_vecs:
                h.create_dataset('displacements', data=self.displacements)

            if self.coords is not None:
                h.create_dataset('coords', data=self.coords)

            if self.atomic_nums is not None:
                h.create_dataset('atomic_nums', data=self.atomic_nums)

            if self.weights is not None:
                h.create_dataset('weights', data=self.weights)

            if self.band_indices is not None:
                h.create_dataset('band_indices', data=self.band_indices)

            if self.q_points is not None:
                h.create_dataset('q_points', data=self.q_points)

    def to_pyvibms(self, file):
        with open(file, 'w') as f:
            f.write(f"{self.natoms} {self.nmodes}\n")
            for idx, (freq, displacement) in enumerate(zip(self.freqs, self.displacements), start=1):
                normalised = displacement.real / np.linalg.norm(displacement)
                f.write(f"\nN {freq:9.4f} A {idx}\n")
                f.write('\n'.join(f"{displ:9.4f}" for vec in normalised for displ in vec))
                f.write('\n')
            f.write("END\n")

    def subset_atoms(self, active_atom_idc=None, ref_coords=None):

        def generate_mapping():
            for idx, coord in enumerate(ref_coords):
                idc = np.flatnonzero(np.isclose(self.coords, coord).all(axis=1))
                if len(idc) == 0:
                    continue
                elif len(idc) == 1:
                    yield idc[0]
                else:
                    raise ValueError(f"Multiple instances of atom {coord}!")

        if active_atom_idc is not None and ref_coords is not None:
            raise ValueError("Supply one of active_atom_idc or ref_coords!")
        elif active_atom_idc is not None:
            idc = active_atom_idc
        elif ref_coords is not None:
            idc = list(generate_mapping())
        else:
            return self

        coords = None if self.coords is None else self.coords[idc]
        atomic_nums = None if self.atomic_nums is None else self.atomic_nums[idc]

        return self.__class__(self.freqs, self.displacements[:, idc],
                              coords=coords, atomic_nums=atomic_nums,
                              weights=self.weights, band_indices=self.band_indices, q_points=self.q_points)

    @classmethod
    def from_file(cls, h_file):

        with h5py.File(h_file, 'r') as h:
            displacements = h['displacements'][...]
            freqs = h['frequencies'][...]

            try:
                coords = h['coords'][...]
            except KeyError:
                coords = None

            try:
                atomic_nums = h['atomic_nums'][...]
            except KeyError:
                atomic_nums = None

            try:
                weights = h['weights'][...]
            except KeyError:
                weights = None

            try:
                band_indices = h['band_indices'][...]
            except KeyError:
                band_indices = None

            try:
                q_points = h['q_points'][...]
            except KeyError:
                q_points = None

        return cls(freqs, displacements,
                   coords=coords, atomic_nums=atomic_nums,
                   weights=weights, band_indices=band_indices, q_points=q_points)

    @classmethod
    def from_gaussian_log(cls, f):
        freqs = make_gaussian_extractor(f, ("freq", "frequency"))[1]
        modes = make_gaussian_extractor(f, ("freq", "displacement"))[1]
        red_masses = make_gaussian_extractor(f, ("freq", "reduced_mass"))[1]
        return cls(freqs, modes / np.sqrt(red_masses)[:, np.newaxis, np.newaxis])

    @classmethod
    def from_gaussian_fchk(cls, f, ext_masses=None, **kwargs):
        hess = make_gaussian_extractor(f, ('fchk', 'hessian'))[()]
        masses = make_gaussian_extractor(f, ('fchk', 'atomic_mass'))[()]
        numbers = make_gaussian_extractor(f, ('fchk', 'atomic_number'))[()]
        coords = make_gaussian_extractor(f, ('fchk', 'coordinates'))[()]

        for key, mass in ext_masses.items():
            if isinstance(key, int):
                masses[key - 1] = mass
            elif isinstance(key, str):
                num = atomic_numbers[key]
                for idx in [i for i, n in enumerate(numbers) if n == num]:
                    masses[idx] = mass
            else:
                raise KeyError("Specify isotopic substitutions with either "
                               "element symbol (str) or atomic indices (int)!")

        return cls.analysis(hess, masses, coords=coords * BOHR2M * 1e10,
                            atomic_nums=numbers, **kwargs)

    @classmethod
    def from_orca_hess(cls, f, ext_masses=None, **kwargs):
        from orca_suite.extractor import make_extractor as make_orca_extractor
        hess = make_orca_extractor(f, ('hess', 'hessian'))[()]
        masses = make_orca_extractor(f, ('hess', 'atomic_mass'))[()]
        symbols = make_orca_extractor(f, ('hess', 'atomic_symbol'))[()]
        numbers = [atomic_numbers[sym.decode()] for sym in symbols]
        coords = make_orca_extractor(f, ('hess', 'coordinates'))[()]

        for key, mass in ext_masses.items():
            if isinstance(key, int):
                masses[key - 1] = mass
            elif isinstance(key, str):
                num = atomic_numbers[key]
                for idx in [i for i, n in enumerate(numbers) if n == num]:
                    masses[idx] = mass
            else:
                raise KeyError("Specify isotopic substitutions with either "
                               "element symbol (str) or atomic indices (int)!")

        return cls.analysis(hess, masses, coords=coords * BOHR2M * 1e10,
                            atomic_nums=numbers, **kwargs)

    @classmethod
    def from_vasp_outcar(cls, outcar_file, poscar_file, trans=True, **kwargs):
        outcar = ParseOUTCAR(outcar_file, poscar_file=poscar_file)
        freqs = outcar_hess.parse_frequencies(outcar)
        displacements = outcar_hess.parse_displacements(outcar)
        freqs, displacements = zip(*sorted(zip(freqs, displacements), key=lambda x: x[0]))
        freqs = np.array(freqs)
        displacements = np.array(displacements)

        if trans:
            freqs = freqs[3:]
            displacements = displacements[3:]

        masses = outcar.masses
        coords = outcar.cart_coords
        return cls(freqs, displacements / np.sqrt(masses)[np.newaxis, :, np.newaxis], coords=coords, **kwargs)

    @classmethod
    def generate_from_qpoints(cls, q_mesh, q_points, freqs_list, vecs_list,
                              poscar, masses, trans=True, **cluster_kwargs):

        cluster = build_cluster(poscar, **cluster_kwargs)

        n_cell = cluster.n_cell

        cart = cluster.cart_coords
        frac = cluster.frac_coords

        # norm is sqrt(#qpoint)
        norm = np.sqrt(reduce(mul, q_mesh))

        for q_point, freqs, vecs in zip(q_points, freqs_list, vecs_list):

            nmodes, natoms = vecs.shape[1], vecs.shape[0] // 3

            # reshape to K x N x 3 (K: #modes, N: #atoms)
            unitcell_displacements = vecs.T.reshape(nmodes, natoms, 3) / \
                np.sqrt(masses)[np.newaxis, :, np.newaxis] / norm

            if trans and q_point.is_gamma():
                freqs = freqs[3:]
                unitcell_displacements = unitcell_displacements[3:]

            print(f"Evaluating q-point {q_point}")
            
            # With boundary atoms, need to map cluster atoms to their POSCAR index
            # using "ENV" labels
            try:
                poscar_index = np.array([int(label.split('.')[-1]) - 1 for label in cluster.labels])
            except (ValueError, IndexError) as e: 
                raise ValueError(f"Could not parse original POSCAR index from cluster labels. Error: {e}")

            # Map unit cell displacements, atomic numbers to the cluster:
            displacements = unitcell_displacements[:, poscar_index, :]
            atomic_nums = np.array(cluster.atom_numbers)[poscar_index]

            # apply relative phases at off-gamma q-points
            if not q_point.is_gamma():
                phase = np.exp(2.j * np.pi * frac @ q_point.coords)
                displacements *= phase[np.newaxis, :, np.newaxis]

            nmodes = freqs.size

            if q_point.is_boundary() or q_point.is_gamma():

                abs_phase = np.array(list(map(phase_by_min_imag, displacements)))
                displacements *= abs_phase[:, np.newaxis, np.newaxis]

                imag_norm = np.linalg.norm(displacements.imag)
                real_norm = np.linalg.norm(displacements.real)
                print(f"{q_point}-point displacements have non-zero "
                      f"imaginary component: {imag_norm}, "
                      f"real component: {real_norm}!")

                yield cls(freqs, displacements.real,
                          coords=cart, atomic_nums=atomic_nums,
                          band_indices=np.arange(1, nmodes + 1),
                          q_points=np.tile(q_point.coords, (nmodes, 1)))
            else:

                yield cls(freqs, np.sqrt(2) * displacements.real,
                          coords=cart, atomic_nums=atomic_nums,
                          band_indices=np.arange(1, nmodes + 1),
                          q_points=np.tile(q_point.coords, (nmodes, 1)))

                yield cls(freqs, np.sqrt(2) * displacements.imag,
                          coords=cart, atomic_nums=atomic_nums,
                          band_indices=np.arange(1, nmodes + 1),
                          q_points=-np.tile((-q_point).coords, (nmodes, 1)))

    @classmethod
    def from_vasp_phonopy(cls, poscar, force_sets, ext_masses=None, trans=True,
                          force_expansion=(1, 1, 1), q_mesh=(1, 1, 1),
                          **cluster_kwargs):
        """Evaluate harmonic oscillators from VASP-phonopy calculation based
        on 
        """

        q_points = list(reduce_half_bz(map(partial(Qpoint, q_mesh), product(*map(range, q_mesh)))))

        cell = phonopy.load(
            unitcell_filename=poscar,
            force_sets_filename=force_sets,
            supercell_matrix=force_expansion,
            primitive_matrix=np.identity(3)
        )

        masses = cell._dynamical_matrix._pcell.masses
        symbols = cell.unitcell.symbols

        for key, mass in ext_masses.items():
            if isinstance(key, int):
                masses[key - 1] = mass
            elif isinstance(key, str):
                for idx in [i for i, sym in enumerate(symbols) if sym == key]:
                    masses[idx] = mass
            else:
                raise KeyError("Specify isotopic substitutions with either "
                               "element symbol (str) or atomic indices (int)!")

        if ext_masses:
            cell._dynamical_matrix._pcell.masses = masses
            cell._set_dynamical_matrix()

        cell.run_qpoints([q.coords for q in q_points], with_eigenvectors=True)

        qpoint_dict = cell.get_qpoints_dict()

        modes = Harmonic.generate_from_qpoints(
            q_mesh,
            q_points,
            qpoint_dict['frequencies'] * 1e12 / (C0 * 1e2),
            qpoint_dict['eigenvectors'],
            poscar,
            masses,
            trans=trans,
            **cluster_kwargs)

        return reduce(add, modes)

    @classmethod
    def from_phonopy_hdf5(cls, poscar, h_file, trans=True, **cluster_kwargs):

        with h5py.File(h_file, 'r') as h:

            q_mesh = tuple(h['mesh'][...])
            q_point_list_full = list(map(partial(Qpoint, q_mesh),
                                         map(tuple, h['grid_address'][...])))
            freqs_list_full = h['frequency'][...] * 1e12 / (C0 * 1e2)
            vecs_list_full = h['eigenvector'][...]

        unique_half_bz = list(map(lambda q: q.address, reduce_half_bz(q_point_list_full)))

        q_point_list, freqs_list, vecs_list = zip(*filter(
            lambda args: args[0].address in unique_half_bz,
            zip(q_point_list_full, freqs_list_full, vecs_list_full)))

        structure = Structure.from_file(poscar)
        masses = np.array([site.specie.atomic_mass for site in structure.sites])

        modes = Harmonic.generate_from_qpoints(
            q_mesh,
            q_point_list,
            freqs_list,
            vecs_list,
            poscar,
            masses,
            trans=trans,
            **cluster_kwargs
        )

        return reduce(add, modes)

    @property
    def hessian(self):
        """
        Reform the Hessian matrix

        self.omega = Omega^2
        Omega^2 = L^T D^T sqrt{M^-1} H sqrt{M^-1} D L

        H = sqrt{M} D L Omega^2 L^T D^T sqrt{M}

        where displacements = sqrt{M^{-1}} D L

        parameters
        ----------
        self : Harmonic

        returns
        -------
        H : np.ndarray
        """
        disp_shape = self.displacements.shape
        displacements = self.displacements.reshape(disp_shape[0], -1)
        # displacements units: sqrt(amu)
        omega = self.omega  # rad s^-1
        omega2 = omega ** 2  # rad^2 s^-2

        hessian = displacements.T @ np.diag(omega2) @ displacements
        # units = sqrt(amu) * rad^2 s^-2 * sqrt(amu)
        # units = amu s^-2
        hessian *= AMU  # Kg s^-2 == J m^-2
        # hessian *= (1/HARTREE2J) * (1/BOHR2M) ** 2  # Ha Bohr^-2
        return hessian

    def remove_imaginary(self, verbose=False):

        def is_real(idx_freq):
            idx, freq = idx_freq
            if verbose and freq < 0:
                print(f"Removing imaginary mode: {idx+1} ({freq: .2f} cm^-1)")
                return False
            else:
                return True

        idc = list(tuple(zip(*filter(is_real, enumerate(self.freqs))))[0])

        return Harmonic(self.freqs[idc], self.displacements[idc],
                        coords=self.coords, atomic_nums=self.atomic_nums,
                        weights=None if self.weights is None else self.weights[idc],
                        band_indices=None if self.band_indices is None else self.band_indices[idc],
                        q_points=None if self.q_points is None else self.q_points[idc])

    def abs_imaginary(self, verbose=False):
        
        if verbose: 
            for idx, freq in enumerate(self.freqs):
                if freq < 0: print(f"Setting imaginary mode: {idx+1} {freq: .2f} cm^-1 to {abs(freq): .2f} cm^-1")

        self.freqs=abs(self.freqs)
        idc=np.argsort(self.freqs)

        return Harmonic(self.freqs[idc], self.displacements[idc],
                        coords=self.coords, atomic_nums=self.atomic_nums,
                        weights=None if self.weights is None else self.weights[idc],
                        band_indices=None if self.band_indices is None else self.band_indices[idc],
                        q_points=None if self.q_points is None else self.q_points[idc])

    def __add__(self, other):

        if not np.allclose(self.coords, other.coords):
            raise ValueError("Coordinates are incompatible!")

        if not all(self.atomic_nums == other.atomic_nums):
            raise ValueError("Atomic numbers are incompatible!")

        order = np.argsort(np.concatenate((self.freqs, other.freqs)))

        def concat_order(attr):

            self_attr = getattr(self, attr)
            other_attr = getattr(other, attr)

            if self_attr is None or other_attr is None:
                return None
            else:
                return np.concatenate((self_attr, other_attr))[order]

        freqs = concat_order("freqs")
        displacements = concat_order("displacements")

        coords = self.coords
        atomic_nums = self.atomic_nums

        weights = concat_order("weights")
        band_indices = concat_order("band_indices")
        q_points = concat_order("q_points")

        return self.__class__(freqs, displacements, coords=coords, atomic_nums=atomic_nums,
                              weights=weights, band_indices=band_indices,
                              q_points=q_points)

    @classmethod
    def analysis(cls, hessian, masses, trans=True, rot=True,
                 coords=None, atomic_nums=None):

        natom = len(masses)

        mwhess = hessian / np.sqrt(np.repeat(masses, 3)[np.newaxis, :] *
                                   np.repeat(masses, 3)[:, np.newaxis])

        eig, vec = np.linalg.eigh(mwhess)

        if trans:
            tra_frame = [np.array([d * np.sqrt(m) for m in masses for d in v])
                         for v in np.identity(3)]
            ntra = 3
        else:
            tra_frame = []
            ntra = 0

        if rot:
            # compute principle axis frame
            nrot, _, vec_inertia = principle_axis_inertia(masses, coords)

            # convert coordinates to principle axis frame
            # _coords = shift_to_com(masses, coords) @ vec_inertia.T
            _coords = shift_to_com(masses, coords)

            rot_frame = \
                [np.array([d * np.sqrt(m) for m, c in zip(masses, _coords)
                           for d in np.cross(c, v)])
                 for v in vec_inertia[:, (3 - nrot):].T]
        else:
            rot_frame = []
            nrot = 0

        nrotra = ntra + nrot
        nmodes = 3 * natom - nrotra

        rotra_frame = \
            np.array([d / np.linalg.norm(d) for d in tra_frame + rot_frame])

        if len(rotra_frame) != 0:
            # detect rigid body motions
            int_mask = np.logical_not(np.isclose(
                np.sum((rotra_frame @ vec)**2, axis=0), 1.0, rtol=1e-1))
            # Schmidt orthogonalisation
            new_frame, _ = np.linalg.qr(
                np.column_stack((rotra_frame.T, vec[:, int_mask])))
            # set coordinate frame to internal coordiantes
            frame = new_frame[:, nrotra:]

            # transfrom Hessian to internal coordinate frame and project out
            # rigid body motions
            eig, vec = np.linalg.eigh(frame.T @ mwhess @ frame)
            cart = frame @ vec / np.sqrt(np.repeat(masses, 3)[:, np.newaxis])

        else:
            cart = vec / np.sqrt(np.repeat(masses, 3)[:, np.newaxis])

        freqs = np.sqrt(eig * (HARTREE2J / BOHR2M**2 / AMU) /
                        (4*np.pi**2 * C0**2) + 0.j) / 100
        _freqs = np.vectorize(lambda x: -x.imag if x.imag else x.real)(freqs)

        displacements = np.reshape(cart.T, (nmodes, natom, 3))

        return cls(_freqs, displacements,
                   coords=coords, atomic_nums=atomic_nums)


class Qpoint:

    def __init__(self, mesh, address):
        self.mesh = mesh
        self.address = address

    @property
    def coords(self):
        return np.array(list(map(lambda n, x: x / n, self.mesh, self.address)))

    def __eq__(self, other):

        if self.mesh != other.mesh:
            ValueError(f"Comparing unequal q-meshes: {self.mesh} {other.mesh}")

        def predicate(n, x, y):  # same or translationally equivalent
            return (x - y) % n == 0

        return all(map(predicate, self.mesh, self.address, other.address))

    def is_gamma(self):

        def predicate(n, x):
            return x % n == 0
        
        return all(map(predicate, self.mesh, self.address))

    def is_boundary(self):
        
        def predicate(n, x):
            return x % n == 0 or (n % 2 == 0 and x % n == n // 2)
        
        return all(map(predicate, self.mesh, self.address)) and not self.is_gamma()

    def __ne__(self, other):
        return not self == other

    def __neg__(self):
        return Qpoint(self.mesh, tuple(map(lambda x: -x, self.address)))

    def __hash__(self):
        return hash(tuple(x % n for n, x in zip(self.mesh, self.address)))

    def __str__(self):
        return str(self.coords)

    def __repr__(self):
        return f"Qpoint({self.mesh},{self.address})"


def reduce_half_bz(q_points):

    unique_q_points = set()

    for q_point in q_points:

        if q_point in unique_q_points or -q_point in unique_q_points:
            continue
        else:
            unique_q_points.add(q_point)
            yield q_point


def phase_by_min_imag(x):

    ang = np.angle(x)
    mag = np.abs(x)**2

    phase = -np.arctan(np.sum(mag * np.sin(2 * ang)) / np.sum(mag * np.cos(2 * ang))) / 2

    if 2 * np.sum(mag * np.cos(2 * (ang + phase))) > 0:
        return np.exp(1.j * phase)
    else:
        return np.exp(1.j * (phase + np.pi / 2))


def shift_to_com(masses, coords):
    com = np.sum(masses[:, np.newaxis] * coords, axis=0) / np.sum(masses)
    return coords - com


def principle_axis_inertia(masses, coords):

    _coords = shift_to_com(masses, coords)

    inertia = np.zeros((3, 3))
    inertia[0, 0] = np.sum(masses * (_coords[:, 1]**2 + _coords[:, 2]**2))
    inertia[1, 1] = np.sum(masses * (_coords[:, 2]**2 + _coords[:, 0]**2))
    inertia[2, 2] = np.sum(masses * (_coords[:, 0]**2 + _coords[:, 1]**2))
    inertia[1, 0] = -np.sum(masses * (_coords[:, 0] * _coords[:, 1]))
    inertia[2, 0] = -np.sum(masses * (_coords[:, 0] * _coords[:, 2]))
    inertia[2, 1] = -np.sum(masses * (_coords[:, 1] * _coords[:, 2]))
    inertia[0, 1] = inertia[1, 0]
    inertia[0, 2] = inertia[2, 0]
    inertia[1, 2] = inertia[2, 1]

    eig_inertia, vec_inertia = np.linalg.eig(inertia)
    rank = np.linalg.matrix_rank(inertia)

    if rank > 1:
        return rank, eig_inertia, vec_inertia
    else:
        raise ValueError("Rank of moment of inertia tensor smaller than one.")


def construct_atomic_basis(dim, gaussian_fchk=False, vasp_born=False, coords=None):
    def make_rigid_translations():
        x = np.array([np.eye(3)[0]] * dim).reshape(-1, 1)
        y = np.array([np.eye(3)[1]] * dim).reshape(-1, 1)
        z = np.array([np.eye(3)[2]] * dim).reshape(-1, 1)
        return np.hstack((x, y, z))

    def make_rigid_rotations(coords):
        x = np.array(list(map(lambda x: np.cross([1, 0, 0], x), coords))).reshape(-1, 1)
        y = np.array(list(map(lambda x: np.cross([0, 1, 0], x), coords))).reshape(-1, 1)
        z = np.array(list(map(lambda x: np.cross([0, 0, 1], x), coords))).reshape(-1, 1)
        return np.hstack((x, y, z))

    rigid_translations = make_rigid_translations()
    if gaussian_fchk:
        if coords is None:
            raise ValueError('Supply coordinates for rigid body rotations')
        rigid_rotations = make_rigid_rotations(coords)
        energy_invariant = np.hstack((rigid_translations, rigid_rotations))
    else:
        energy_invariant = rigid_translations

    q, _, _ = sp.linalg.qr(energy_invariant, mode='full', pivoting=True)
    if gaussian_fchk:
        return q[6:].T
    else:
        return q[3:].T
