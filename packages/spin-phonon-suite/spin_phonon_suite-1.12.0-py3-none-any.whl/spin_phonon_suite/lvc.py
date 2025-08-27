from fractions import Fraction
from functools import lru_cache, partial
import warnings

import h5py

import numpy as np
from jax import jvp, jit
from jax.lax import stop_gradient
import jax.numpy as jnp
from jax.scipy.linalg import block_diag

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import xyz_py as xyzp

from hpc_suite.store import Store
from molcas_suite.generate_input import MolcasComm, MolcasInput, Alaska, \
    Mclr, Emil
from molcas_suite.extractor import make_extractor as make_molcas_extractor
import angmom_suite
from angmom_suite.model import ProjectModelHamiltonian, \
    MagneticSusceptibility
from angmom_suite.basis import sf2ws, sf2ws_amfi, unitary_transform, sfy, \
    from_blocks, dissect_array, extract_blocks, make_angmom_ops_from_mult, \
    rotate_cart

ANG2BOHR = 1.88973


def extract_molcas_rassi(f_rassi):

    geom = make_molcas_extractor(f_rassi, ("rassi", "center_coordinates"))[()]

    spin_mult = make_molcas_extractor(f_rassi, ("rassi", "spin_mult"))[()]
    sf_mult = dict(zip(*np.unique(spin_mult, return_counts=True)))

    ener = make_molcas_extractor(f_rassi, ("rassi", "SFS_energies"))[()]
    sf_ener = list(dissect_array(ener, spin_mult))

    amfi = make_molcas_extractor(f_rassi, ("rassi", "SFS_AMFIint"))[()]
    sf_amfi = list(map(list, dissect_array(amfi, spin_mult, spin_mult)))

    angm = make_molcas_extractor(f_rassi, ("rassi", "SFS_angmom"))[()]
    sf_angm = list(extract_blocks(angm, spin_mult, spin_mult))

    return geom, sf_mult, sf_ener, sf_amfi, sf_angm


def extract_molcas_couplings(f_grad_list):

    for grad_file in f_grad_list:

        grad = make_molcas_extractor(grad_file, ("gradients", None))

        for (mult, root), val in iter(grad):
            yield mult, (root - 1, root - 1), val

        nacs = make_molcas_extractor(grad_file, ("nacs", "CI"))

        for (mult, root1, root2), val in iter(nacs):
            yield mult, (root1 - 1, root2 - 1), val


def extract_molcas_frozen_density_couplings(f_grad_list, charges):

    for grad_file, charge in zip(f_grad_list, charges):

        grad = make_molcas_extractor(grad_file, ("rasscf", "efld"))

        for (mult, root), val in iter(grad):
            yield mult, (root - 1, root - 1), -val * charge[:, np.newaxis]


class LVC:

    def __init__(self, sf_ener, sf_linear, sf_mult, geom, sf_amfi=None,
                 sf_angm=None):

        # LVC data
        self.sf_ener = sf_ener
        self.sf_linear = sf_linear

        # Spin multiplicities
        self.sf_mult = sf_mult

        self.sf_amfi = sf_amfi
        self.sf_angm = sf_angm

        self.geom = geom

    @property
    def natoms(self):
        return self.geom.shape[0]

    @property
    def ground_ener(self):
        return min(map(min, self.sf_ener))

    @property
    def sos_angm(self):
        return unitary_transform(sf2ws(self.sf_angm, self.sf_mult),
                                 self.diabatic_soc_trafo)

    @property
    def sos_spin(self):
        spin_mult = \
            [mult for mult, num in self.sf_mult.items() for _ in range(num)]
        spin = np.array(make_angmom_ops_from_mult(spin_mult)[0:3])
        return unitary_transform(spin, self.diabatic_soc_trafo)

    @property
    def diabatic_soc_trafo(self):
        mch = sf2ws(map(jnp.diag, self.sf_ener), self.sf_mult)
        soc = sf2ws_amfi(self.sf_amfi, self.sf_mult)
        _, vec = jnp.linalg.eigh(mch + soc)
        return vec

    def print_grad_norm(self):

        num = len(self.sf_mult)
        fig, axes = plt.subplots(nrows=num, ncols=1, squeeze=False)
        fig.set_size_inches(4, num * 4)

        for idx, (mult, lin) in enumerate(zip(self.sf_mult, self.sf_linear)):
            grad_norm = np.linalg.norm(lin, axis=(2, 3))
            axes[idx][0].title.set_text(f"Spin Multiplicity = {mult}")
            mat = axes[idx][0].matshow(grad_norm, norm=LogNorm())
            fig.colorbar(mat)

        plt.savefig("coupling_norm.pdf", dpi=600)

    def print_trans_rot_invariance(self):
        """Evaluates translational and rotational invariance along and around
        all three coordinate axes
        """

        num = len(self.sf_mult)
        fig, axes = plt.subplots(nrows=num, ncols=1, squeeze=False)
        nrm = np.sqrt(self.natoms)

        fig, axes = plt.subplots(nrows=num, ncols=3, squeeze=False)
        fig.set_size_inches(12, num * 4)

        for idx, (mult, lin) in enumerate(zip(self.sf_mult, self.sf_linear)):
            for vdx, (vec, lab) in enumerate(zip(np.identity(3), 'xyz')):
                inv = np.abs(np.einsum('ijkl,l->ij', lin, vec / nrm))
                inv[inv != 0] /= np.linalg.norm(lin, axis=(2, 3))[inv != 0]
                axes[idx][vdx].title.set_text(
                    f"axis = {lab}, Spin Multiplicity = {mult}")
                mat = axes[idx][vdx].matshow(inv, norm=LogNorm())
            fig.colorbar(mat, ax=axes[idx].tolist())

        plt.savefig("translational_invariance.pdf", dpi=600)

        fig, axes = plt.subplots(nrows=num, ncols=3, squeeze=False)
        fig.set_size_inches(12, num * 4)

        for idx, (mult, lin) in enumerate(zip(self.sf_mult, self.sf_linear)):
            for vdx, (ax, lab) in enumerate(zip(np.identity(3), 'xyz')):
                vec = np.array([np.cross(c, ax) for c in self.geom])
                inv = np.abs(np.einsum('ijkl,kl->ij', lin,
                                       vec / np.linalg.norm(vec)))
                inv[inv != 0] /= np.linalg.norm(lin, axis=(2, 3))[inv != 0]
                axes[idx][vdx].title.set_text(
                    f"axis = {lab}, Spin Multiplicity = {mult}")
                mat = axes[idx][vdx].matshow(inv, norm=LogNorm())
            fig.colorbar(mat, ax=axes[idx].tolist())

        plt.savefig("rotational_invariance.pdf", dpi=600)

    def to_file(self, f_lvc, verbose=False):

        if verbose:
            self.print_trans_rot_invariance()
            self.print_grad_norm()

        with h5py.File(f_lvc, 'w') as h:

            # LVC data
            for mult, ener in zip(self.sf_mult, self.sf_ener):
                h.create_dataset(f'{mult}/sf_ener', data=ener)

            for mult, lin in zip(self.sf_mult, self.sf_linear):
                h.create_dataset(f'{mult}/sf_linear', data=lin)

            # coordinates
            h.create_dataset('geom', data=self.geom)

            # spin multiplicities
            h.create_dataset('sf_mult', data=list(self.sf_mult.keys()))
            h.create_dataset('sf_nroots', data=list(self.sf_mult.values()))

            if self.sf_amfi is not None:
                for mult1, row in zip(self.sf_mult, self.sf_amfi):
                    for mult2, amfi in zip(self.sf_mult, row):
                        if abs(mult1 - mult2) <= 2:
                            h.create_dataset(f'{mult1}/{mult2}/sf_amfi',
                                             data=amfi)

            if self.sf_angm is not None:
                for mult, angm in zip(self.sf_mult, self.sf_angm):
                    h.create_dataset(f'{mult}/sf_angm', data=angm)

    @classmethod
    def from_file(cls, f_lvc):

        with h5py.File(f_lvc, 'r') as h:

            # coordinates
            geom = h['geom'][...]

            # Spin multiplicities
            sf_mult = dict(zip(h['sf_mult'][...], h['sf_nroots'][...]))

            # LVC data
            sf_ener = [h[f'{mult}/sf_ener'][...] for mult in sf_mult]
            sf_linear = [h[f'{mult}/sf_linear'][...] for mult in sf_mult]

            try:
                sf_amfi = [[h[f'{mult1}/{mult2}/sf_amfi'][...]
                            if abs(mult1 - mult2) <= 2 else
                            jnp.zeros((3, nroots1, nroots2))
                            for mult2, nroots2 in sf_mult.items()]
                           for mult1, nroots1 in sf_mult.items()]

            except KeyError:
                sf_amfi = None

            try:
                sf_angm = [h[f'{mult}/sf_angm'][...] for mult in sf_mult]
            except KeyError:
                sf_angm = None

        return cls(sf_ener, sf_linear, sf_mult, geom, sf_amfi=sf_amfi,
                   sf_angm=sf_angm)

    @classmethod
    def from_molcas_frozen_density(cls, f_rassi, f_grad_list, charge_list,
                                   coord_list):

        sf_linear_iter = \
            extract_molcas_frozen_density_couplings(f_grad_list, charge_list)
        _, sf_mult, sf_ener, sf_amfi, sf_angm = extract_molcas_rassi(f_rassi)
        geom = np.concatenate(coord_list)

        return cls.from_iter(sf_ener, sf_linear_iter, sf_mult, geom,
                             sf_amfi=sf_amfi, sf_angm=sf_angm)

    @classmethod
    def from_molcas(cls, f_rassi, f_grad_list, verbose=False):

        sf_linear_iter = extract_molcas_couplings(f_grad_list)
        geom, sf_mult, sf_ener, sf_amfi, sf_angm = extract_molcas_rassi(f_rassi)

        return cls.from_iter(sf_ener, sf_linear_iter, sf_mult, geom,
                             sf_amfi=sf_amfi, sf_angm=sf_angm)

    @classmethod
    def from_iter(cls, sf_ener, sf_linear_iter, sf_mult, geom,
                  sf_amfi=None, sf_angm=None):

        couplings = {mult: np.zeros((nroots, nroots) + geom.shape)
                     for mult, nroots in sf_mult.items()}

        for mult, (root1, root2), val in sf_linear_iter:
            couplings[mult][root1, root2, :] = val
            if root1 != root2:
                couplings[mult][root2, root1, :] = val

        # check if any expected couplings have not been supplied
        for mult, nroots in sf_mult.items():
            for root1 in range(nroots):
                for root2 in range(root1, nroots):
                    if not couplings[mult][root1, root2].any():
                        warnings.warn("Missing couplings between roots "
                                      f"{root1+1} and {root2+1} of spin state with multiplicity {mult}!")

        return cls(sf_ener, list(couplings.values()), sf_mult, geom,
                   sf_amfi=sf_amfi, sf_angm=sf_angm)

    def join(self, other, ref_geom):

        if not (sfy(np.array_equal, sf=1)(self.sf_mult, other.sf_mult) and
                sfy(np.array_equal, sf=1)(self.sf_ener, other.sf_ener) and
                sfy(np.array_equal, sf=1)(self.sf_angm, other.sf_angm) and
                sfy(np.array_equal, sf=2)(self.sf_amfi, other.sf_amfi)):
            raise ValueError("LVC data not compatible!")

        sf_linear = map(lambda x, y: x + y, self.expand(ref_geom).sf_linear,
                        other.expand(ref_geom).sf_linear)

        return LVC(self.sf_ener, list(sf_linear), self.sf_mult, ref_geom,
                   sf_amfi=self.sf_amfi, sf_angm=self.sf_angm)

    def expand(self, ref_geom):

        def generate_mapping():
            for idx, coord in enumerate(self.geom):
                idc = np.flatnonzero(np.isclose(ref_geom, coord).all(axis=1))
                if len(idc) == 1:
                    yield (idx, idc[0])
                else:
                    raise ValueError(f"Multiple instances of atom {coord}!")

        atoms, mapping = zip(*generate_mapping())

        def expand(lin, num):
            zeros = jnp.zeros((num, num) + ref_geom.shape)
            return zeros.at[:, :, mapping].add(lin[:, :, atoms])

        sf_linear = map(expand, self.sf_linear, self.sf_mult.values())

        return LVC(self.sf_ener, list(sf_linear), self.sf_mult, ref_geom,
                   sf_amfi=self.sf_amfi, sf_angm=self.sf_angm)

    def subset_atoms(self, active_atom_idc=None, ref_coords=None):

        def generate_mapping():
            for idx, coord in enumerate(ref_coords):
                idc = np.flatnonzero(np.isclose(self.geom, coord).all(axis=1))
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

        geom = self.geom[idc]
        sf_linear = [lin[:, :, idc, :] for lin in self.sf_linear]

        return self.__class__(self.sf_ener, sf_linear, self.sf_mult, geom,
                              sf_amfi=self.sf_amfi, sf_angm=self.sf_angm)

    def align(self, ref_geom):
        # translate centroid
        # find optimal rotation
        # according to http://nghiaho.com/?page_id=671

        def centroid(coords):
            return jnp.mean(coords, axis=0)

        self_centroid = centroid(self.geom)
        ref_centroid = centroid(ref_geom)

        uvec, _, vhvec = jnp.linalg.svd(
            (self.geom - self_centroid).T @
            (ref_geom - ref_centroid))

        rot = vhvec.T @ uvec.T

        if jnp.isclose(jnp.linalg.det(rot), -1.0):
            vhvec = vhvec.at[2].multiply(-1.0)

        rot = vhvec.T @ uvec.T

        geom = (self.geom - self_centroid) @ rot.T + ref_centroid

        def rot_linear(y):
            return sfy(lambda x: jnp.einsum('ij,mnoj->mnoi', rot, x), sf=1)(y)

        sf_linear = rot_linear(self.sf_linear)
        sf_angm = sfy(lambda x: rotate_cart(x, rot), sf=1)(self.sf_angm)
        sf_amfi = sfy(lambda x: rotate_cart(x, rot), sf=2)(self.sf_amfi)

        return LVC(self.sf_ener, sf_linear, self.sf_mult, geom,
                   sf_amfi=sf_amfi, sf_angm=sf_angm)

    def diabatic_hamiltonian(self, geom, soc=False):

        distortion = geom - self.geom

        sf_mch = [jnp.diag(ener - self.sf_ener[0][0]) +
                  jnp.einsum('ijkl,kl->ij', lin, distortion)
                  for ener, lin in zip(self.sf_ener, self.sf_linear)]

        if soc:
            soc_potential = sf2ws_amfi(self.sf_amfi, self.sf_mult)
            soc_hamiltonian = sf2ws(sf_mch, self.sf_mult) + soc_potential
            return unitary_transform(soc_hamiltonian, self.diabatic_soc_trafo)
        else:
            return sf_mch

    def __call__(self, geom, soc=False):

        if soc:
            dia = self.diabatic_hamiltonian(geom, soc=True)
            soc_ener, soc_trafo = jnp.linalg.eigh(dia)

            def trafo(op):
                return unitary_transform(op, soc_trafo)

            return soc_ener, trafo

        else:
            dia = self.diabatic_hamiltonian(geom)
            sf_ener, sf_trafo = zip(*[jnp.linalg.eigh(v) for v in dia])

            def trafo(op, sf=0):
                Umat = sf_trafo if sf else from_blocks(*sf_trafo)
                return unitary_transform(op, Umat, sf=sf)

            return sf_ener, trafo


def make_lvc_evaluator_xyz(xyz_file, select, **kwargs):
    geom = xyzp.load_xyz(xyz_file)[1] * ANG2BOHR
    return make_lvc_evaluator(geom, select, **kwargs)


def make_lvc_evaluator_eq(select, lvc=None, **kwargs):
    geom = lvc.geom
    return make_lvc_evaluator(geom, select, lvc, **kwargs)


def make_lvc_evaluator(geom, select, lvc, order=0, coords=None, truncate=None,
                       align=True):

    if align:
        lvc = lvc.align(geom)

    item, option_str = select

    resolve_options = {
        "adiabatic_energies": lambda opt: {'soc': opt == "soc", 'truncate': truncate},
        "diabatic_hamiltonian": lambda opt: {'soc': opt == "soc", 'truncate': truncate},
        "proj": lambda opt: angmom_suite.proj_parser.parse_args(opt.split()),
        "sus": lambda opt: angmom_suite.read_args(['sus'] + opt.split())
    }[item]

    options = resolve_options(option_str)

    evaluator = {
        "adiabatic_energies": LVCAdiabaticEnergies,
        "diabatic_hamiltonian": LVCDiabaticHamiltonian,
        "proj": LVCModelHamiltonian,
        "sus": LVCMagneticSusceptibility,
    }[item]

    return evaluator(lvc, order, geom=geom, coords=coords, **options)


class LVCData:

    def __init__(self, lvc, order, *args, geom=None, coords=None, **kwargs):
        self.lvc = lvc
        self.order = order
        self.geom = lvc.geom if geom is None else geom
        self.coords = np.identity(3 * lvc.natoms).reshape((-1, lvc.natoms, 3))\
            if coords is None else coords

        super().__init__(*args, **kwargs)

        self.meta['label'] = \
            tuple([f"coord_{i}" for i in range(order)]) + self.meta['label']

    def format_label(self, lab, axes):
        return axes + super().format_label(lab)

    def __iter__(self):

        def recursive_order(x, func, axes=(), order=0):

            if order == self.order:
                yield from map(lambda val, lab: (self.format_label(lab, axes), val), *func(x))

            elif order < self.order:
                first = axes[-1] if len(axes) else 0

                for axis, coord in enumerate(self.coords[first:], start=1):

                    def _func(x):
                        return jvp(func, (x,), (coord,), has_aux=True)[1:3]

                    yield from recursive_order(
                        x, _func, axes=axes + (axis,), order=order + 1)

        yield from recursive_order(self.geom, self.evaluate)


class LVCAdiabaticEnergies(LVCData, Store):
    def __init__(self, *args, soc=False, truncate=None, **kwargs):
        self.soc = soc
        self.truncate = truncate
        description = \
            ' '. join(["SOC" if self.soc else "MCH", "energies",
                       f"truncated to the lowest {self.truncate} states"
                       if self.truncate else ""])

        label = () if self.soc else ("multiplicity",)

        super().__init__(*args, "Energies", description, **kwargs, label=label,
                         units="cm^-1")

    def evaluate(self, x):

        if self.truncate is None or not self.soc:
            ener = self.lvc(x, soc=self.soc)[0]
        else:
            ener = self.lvc(x, soc=self.soc)[0][:self.truncate]

        if self.soc:
            return [ener], [()]
        else:
            return ener, map(lambda lab: (lab,), self.lvc.sf_mult)


class LVCDiabaticHamiltonian(LVCData, Store):
    def __init__(self, *args, soc=False, truncate=None, **kwargs):
        self.soc = soc
        self.truncate = truncate
        description = \
            ' '.join(["Diabatic Hamiltonian matrix between the",
                      f"lowest {self.truncate}" if self.truncate else "",
                      "SOC states" if soc else "MCH states"])

        label = () if soc else ("multiplicity",)
        super().__init__(*args, "Diabatic Hamiltonian", description, **kwargs,
                         label=label, units="cm^-1")

    def evaluate(self, x):

        if self.truncate is None or not self.soc:
            hamiltonian = self.lvc.diabatic_hamiltonian(x, soc=self.soc)
        else:
            idc = jnp.ix_(jnp.arange(self.truncate), jnp.arange(self.truncate))
            hamiltonian = self.lvc.diabatic_hamiltonian(x, soc=self.soc)[idc]

        if self.soc:
            return [hamiltonian], [()]
        else:
            return hamiltonian, map(lambda lab: (lab,), self.lvc.sf_mult)


class LVCModelHamiltonian(LVCData, ProjectModelHamiltonian):
    def __init__(self, lvc, *args, **kwargs):
        super().__init__(lvc, *args, None, lvc.sf_mult, **kwargs)

    def evaluate(self, x):

        # parse operators in diabatic basis
        ops = {'sf_angm': self.lvc.sf_angm,
               'sf_mch': self.lvc.diabatic_hamiltonian(x, soc=False),
               'sf_amfi': self.lvc.sf_amfi}

        return super().evaluate(**ops)


class LVCMagneticSusceptibility(LVCData, MagneticSusceptibility):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, None, **kwargs)

    def evaluate(self, x):

        # parse operators in diabatic basis

        return super().evaluate(
            hamiltonian=self.lvc.diabatic_hamiltonian(x, soc=True),
            spin=self.lvc.sos_spin,
            angm=self.lvc.sos_angm
        )


def reserve_space(string):
    return r"{:0" + str(len(str(string))) + r"}"


def generate_lvc_input(old_path, old_proj, num_root, jobiph_idx, jobiph_path=None,
                       mclr_extra=((), {}), alaska_extra=((), {}), two_step=True, dry=False):

    if jobiph_path is None and (old_proj is not None and old_path is not None):
        jobiph_path = f"{old_path}/{jobiph_idx}_IPH"

    elif jobiph_path is None and (old_proj is None and old_path is None):
        raise ValueError("Provide at least one of jobiph_path, or old_path and old_proj!")

    files = [
        Emil('copy', src, dest) for src, dest in [
            (f"{old_path}/{old_proj}.RunFile", "$Project.RunFile"),
            (f"{old_path}/{old_proj}.OneInt", "$Project.OneInt"),
            (jobiph_path, "$Project.JobIph"),
            (f"{old_path}/{old_proj}.ChDiag", "$Project.ChDiag"),
            (f"{old_path}/{old_proj}.ChMap", "$Project.ChMap"),
            (f"{old_path}/{old_proj}.ChRed", "$Project.ChRed"),
            (f"{old_path}/{old_proj}.ChRst", "$Project.ChRst"),
            (f"{old_path}/{old_proj}.ChVec1", "$Project.ChVec1"),
            (f"{old_path}/{old_proj}.QVec00", "$Project.QVec00")
        ]
    ]

    root_pattern = reserve_space(num_root)
    input_name = f"lvc{jobiph_idx}_root{root_pattern}-{root_pattern}.input"

    if two_step:

        mclr_input = MolcasInput(
            *files, MolcasComm('MCLR first step'),
            Mclr(*mclr_extra[0], **mclr_extra[1], SALA=1, TWOStep="first"),
            title="LVC parametrisation generated by spin-phonon_suite"
        )

        if dry:
            print(f"lvc{jobiph_idx}_mclr.input")
        else:
            mclr_input.write(f"lvc{jobiph_idx}_mclr.input")

        mclr_files = [
            Emil('copy', src, dest) for src, dest in [
                (f"{old_path}/lvc{jobiph_idx}_mclr.tramo", "$Project.tramo"),
                (f"{old_path}/lvc{jobiph_idx}_mclr.Qdat", "$Project.Qdat")
            ]
        ]

        # set TWOStep flag for subsequent mclr runs and append extra file names
        files.extend(mclr_files)

    for iroot in range(1, num_root + 1):

        if two_step:
            mclr_grad = (Mclr(*mclr_extra[0], SALA=f"{iroot}", **mclr_extra[1], TWOStep="second"),)
        elif mclr_extra[0] or mclr_extra[1]:
            mclr_grad = (Mclr(*mclr_extra[0], SALA=f"{iroot}", **mclr_extra[1]),)
        else:
            mclr_grad = ()

        grad_input = MolcasInput(
            *files, MolcasComm('Gradient'), *mclr_grad,
            Alaska(*alaska_extra[0], ROOT=f"{iroot}", **alaska_extra[1]),
            title="LVC parametrisation generated by spin-phonon_suite"
        )

        grad_file = input_name.format(iroot, iroot)

        if dry:
            print(grad_file)
        else:
            grad_input.write(grad_file)

        for jroot in range(iroot + 1, num_root + 1):

            if two_step:
                mclr_nac = (Mclr(*mclr_extra[0], NAC=f"{iroot} {jroot}", **mclr_extra[1], TWOStep="second"),)
            elif mclr_extra[0] or mclr_extra[1]:
                mclr_nac = (Mclr(*mclr_extra[0], NAC=f"{iroot} {jroot}", **mclr_extra[1]),)
            else:
                mclr_nac = ()

            nac_input = MolcasInput(
                *files, MolcasComm('Nonadiabatic coupling'), *mclr_nac,
                Alaska(*alaska_extra[0], NAC="{} {}".format(iroot, jroot),
                       **alaska_extra[1]),
                title="LVC parametrisation generated by spin-phonon_suite"
            )

            nac_file = input_name.format(iroot, jroot)

            if dry:
                print(nac_file)
            else:
                nac_input.write(nac_file)
