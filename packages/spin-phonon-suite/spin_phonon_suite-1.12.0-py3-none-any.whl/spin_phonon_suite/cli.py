#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError, \
                     RawDescriptionHelpFormatter, BooleanOptionalAction
import sys
import re
from functools import reduce
import h5py
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants
from ase.data import chemical_symbols
from vasp_suite.structure import Structure

import xyz_py as xyzp
from molcas_suite.cli import ParseExtra
import hpc_suite as hpc
from hpc_suite.action import ParseKwargs, OrderedSelectionAction
from hpc_suite import make_parse_dict, SecondaryHelp, parse_index
import angmom_suite as angmom
from angmom_suite.crystal import calc_oef, calc_total_strength
from angmom_suite.basis import Level
from angmom_suite.multi_electron import Ion
from gaussian_suite.extractor import make_extractor as make_gaussian_extractor
import env_suite as env

from .derivative import print_tau_style, read_tau_style
from .lvc import LVC, generate_lvc_input, ANG2BOHR, \
    make_lvc_evaluator_eq, make_lvc_evaluator_xyz, \
    LVCModelHamiltonian, LVCAdiabaticEnergies, LVCDiabaticHamiltonian
from .vibrations import Harmonic, HARTREE2J, BOHR2M, E0_TO_C, construct_atomic_basis
from .polarisation_derivatives import parse_BEC, normalised_sphere_vectors
from .experiments import make_exp_evaluator

plt.rcParams['font.family'] = "Arial"

HARTREE2INVCM = 219474.63
EPSILON0 = scipy.constants.epsilon_0
BOHR_RADIUS = scipy.constants.physical_constants["Bohr radius"][0]

BOHR2_TO_COULOMBMETERPERVOLT = 1.0 / (4 * np.pi * EPSILON0 * BOHR_RADIUS**2)


# Action for secondary function help message
class FunctionHelp(SecondaryHelp):
    def __call__(self, parser, namespace, values, option_string=None):

        if namespace.function == 'proj':
            angmom.read_args(['proj', '--help'])
        else:
            raise ValueError("Supply valid option to function argument.")


def str_int(x):
    try:
        return int(x)
    except ValueError:
        return str(x)


def lvc_func(args):

    if args.add is not None:
        def join(a, b):
            return a.join(b, xyzp.load_xyz(args.reference_xyz)[1] * ANG2BOHR)
        lvc = reduce(join, (LVC.from_file(f_lvc) for f_lvc in args.add))

    elif args.efld is not None:
        charge_list = [np.loadtxt(f_chrg) for f_chrg in args.charge]
        xyz_list = [xyzp.load_xyz(f_xyz)[1] * ANG2BOHR for f_xyz in args.xyz]
        lvc = LVC.from_molcas_frozen_density(
            args.rassi, args.efld, charge_list, xyz_list)

    elif args.grad is not None:
        lvc = LVC.from_molcas(args.rassi, args.grad)

    else:
        raise ValueError("LVC gradient information supplied!")

    if args.active_atoms is not None:
        lvc = lvc.subset_atoms(active_atom_idc=args.active_atoms)

    elif args.ref_coordinates is not None:
        _, coords = xyzp.load_xyz(args.ref_coordinates)
        lvc = lvc.subset_atoms(ref_coords=coords * ANG2BOHR)

    lvc.to_file(args.lvc_data, verbose=args.verbose)

    return


def eval_func(args, unknown_args):

    try:
        selected = args._selection
    except AttributeError:
        sys.exit("No quantity selected for evaluation!")

    # Resolve coordinates
    if args.vibration_info is not None:
        ho = Harmonic.from_file(args.vibration_info)
        coords = ho.mass_freq_weighted_coordinates * ANG2BOHR
    else:
        coords = None

    if args.geom:
        store_args = hpc.read_args(['store'] + unknown_args + ['-i'] + args.geom)
    else:
        store_args = hpc.read_args(['store'] + unknown_args)

    hpc.store_func(
        store_args,
        make_lvc_evaluator_xyz if args.geom else make_lvc_evaluator_eq,
        selected,
        lvc=LVC.from_file(args.lvc_data),
        order=args.order,
        coords=coords,
        truncate=args.truncate,
        align=args.align
    )


def vib_func(args):

    if args.gaussian_log:

        if args.mass:
            raise ValueError("The --mass argument is not available with freq "
                             "data read from Gaussian text output use *.fchk!")

        ho = Harmonic.from_gaussian_log(args.gaussian_log)

    elif args.gaussian_fchk:
        ho = Harmonic.from_gaussian_fchk(
            args.gaussian_fchk,
            ext_masses=args.mass,
            rot=args.rot,
            trans=args.trans
        )

    elif args.orca_hess:
        ho = Harmonic.from_orca_hess(
            args.orca_hess,
            ext_masses=args.mass,
            rot=args.rot,
            trans=args.trans
        )

    elif args.vasp_outcar:
        ho = Harmonic.from_vasp_outcar(
                args.vasp_outcar,
                args.poscar,
                trans=args.trans
        )

    elif args.force_sets:

        ho = Harmonic.from_vasp_phonopy(
            args.poscar,
            args.force_sets,
            ext_masses=args.mass,
            trans=args.trans,
            cluster_expansion=args.cluster_expansion,
            cluster_cutoff=args.cluster_cutoff,
            central_idc=args.central_index,
            force_expansion=args.force_expansion,
            q_mesh=args.q_mesh
        )

    elif args.phonopy_hdf5:

        if args.mass:
            raise ValueError("The --mass argument is not available with phonon"
                             " data read from phonopy hdf5 database, use "
                             "FORCE_SETS instead!")

        ho = Harmonic.from_phonopy_hdf5(
            args.poscar,
            args.phonopy_hdf5,
            trans=args.trans,
            cluster_expansion=args.cluster_expansion,
            cluster_cutoff=args.cluster_cutoff,
            central_idc=args.central_index
        )

    if args.imaginary=='remove':
        ho = ho.remove_imaginary(verbose=True)
    elif args.imaginary=='absolute':
        ho = ho.abs_imaginary(verbose=True)

    if args.active_atoms is not None:
        ho = ho.subset_atoms(active_atom_idc=args.active_atoms)

    elif args.ref_coordinates is not None:
        _, coords = xyzp.load_xyz(args.ref_coordinates)
        ho = ho.subset_atoms(ref_coords=coords)

    ho.to_file(args.vibration_info, store_vecs=args.store_vecs)

    if args.save_pyvibms is not None:
        ho.to_pyvibms(args.save_pyvibms)

    return


def prepare_func(args):

    # mode_energies.dat
    ho = Harmonic.from_file(args.vibration_info)

    np.savetxt('mode_energies.dat', ho.freqs, fmt='%16.8f',
               header="Frequency (cm-1)", comments='')

    name = args.program.split('_')[0]

    if args.program.split('_')[-1] == 'direct':
        lvc = LVC.from_file(args.lvc_data)

        ener = LVCAdiabaticEnergies(lvc, 0, soc=True,
                                    truncate=args.truncate)[()]

        nstates = args.truncate or ener.size

        couplings = LVCDiabaticHamiltonian(lvc, 1,
            coords=ho.mass_freq_weighted_coordinates * ANG2BOHR,
            soc=True, truncate=nstates)

        with h5py.File(f'{name}.hdf5', 'w') as h, open('coupling_strength.dat', 'w') as f:

            h.create_dataset('energies', data=(ener - ener[0]) * HARTREE2INVCM)
            h.create_dataset('mode_energies', data=ho.freqs)

            grp = h.create_group("couplings")

            for modes, lin in iter(couplings):

                cplg = lin * HARTREE2INVCM

                if args.trace_less:
                    cplg -= np.identity(nstates) * np.trace(cplg) / nstates

                grp.create_dataset('_'.join(map(str, modes)), data=cplg)
                strength = np.sum((cplg * cplg.conj()).real)
                f.write(f'{strength}\n')

            angm_grp = h.create_group('angmom')
            spin_grp = h.create_group('spin')

            for idx, comp in enumerate(["x", "y", "z"]):
                idc = np.ix_(range(nstates), range(nstates))
                angm_grp.create_dataset(comp, data=lvc.sos_angm[idx][idc])
                spin_grp.create_dataset(comp, data=lvc.sos_spin[idx][idc])

    if args.program in ('tau', 'firms'):
        # CFP args
        proj_kwargs = {
            'model_space': args.ground_level,
            'quax': args.quax,
            'terms': {"cf": [('J',)]},
            'k_max': args.k_max,
            'theta': True,
            'ion': args.ion
        }

        # EQ_CFPs.dat
        cfp_eq = LVCModelHamiltonian(LVC.from_file(args.lvc_data), 0,
                                     **proj_kwargs)[("cf", "J")]

        cfp_data = np.column_stack(
            (np.ones(27), list(cfp_eq.keys()), list(cfp_eq.values())))

        np.savetxt('EQ_CFPs.dat', cfp_data,
                   fmt=['%2d', '%2d', '% 2d', '%16.8f'])

        cfp_dq = LVCModelHamiltonian(
            LVC.from_file(args.lvc_data), 1,
            coords=ho.mass_freq_weighted_coordinates * ANG2BOHR,
            **proj_kwargs
        )

        print_tau_style(filter(lambda pars: pars[0][1] == 'cf', iter(cfp_dq)),
                        ho.freqs, 'CFP_polynomials.dat')

    elif name == 'firms':
        if args.vasp_born:
            bec_tensors = parse_BEC(args.poscar, args.vasp_born)
            derivatives = ho.calculate_dmudQ(bec_tensors) # [C amu^{-1/2}]
            red_masses = ho.mode_red_masses
            derivatives *= np.sqrt(red_masses).reshape((-1, 1)) # [C]
        elif args.gaussian_log:
            derivatives = make_gaussian_extractor(args.gaussian_log, ("freq", "dipole_derivatives"))[()]
            derivatives *= 1/np.sqrt(42.2561) * 3.33564e-30 * 1e10 * np.sqrt(ho.red_masses)
        elif args.gaussian_fchk:
            derivatives = make_gaussian_extractor(args.gaussian_fchk, ("fchk", "dipole_derivatives"))[()]
            derivatives = derivatives.reshape(-1, 3, 3) * E0_TO_C  # [C amu^{-1/2}]
            if args.active_atoms:
                derivatives = derivatives[args.active_atoms, :, :]
            derivatives = np.einsum('jab, kja -> kb', derivatives.reshape(-1, 3, 3), ho.displacements)
            red_masses = np.loadtxt(args.red_masses)
            derivatives *= np.sqrt(red_masses).reshape((-1,1)) # [C]

        with h5py.File('firms.hdf5', 'a') as h:
            h.create_dataset(name='dipole_derivatives', data=derivatives)
            h.create_dataset(name='red_masses', data=red_masses)

    return


def generate_lvc_input_func(args):

    # todo: replace dict by global definition
    roots_dict = {'dy': [18]}

    if args.num_roots:
        num_roots = map(int, args.num_roots)
    elif args.ion:
        num_roots = roots_dict[args.ion.lower()]
    else:
        sys.exit("Invalid specification of the number of roots.")

    for jobiph_idx, num_root in enumerate(num_roots):

        if num_root == 0:
            continue

        generate_lvc_input(
            args.old_path,
            args.old_project,
            num_root,
            jobiph_idx + 1,
            jobiph_path=args.jobiph_paths[jobiph_idx] if args.jobiph_paths is not None else None,
            mclr_extra=args.mclr_extra,
            alaska_extra=args.alaska_extra,
            two_step=args.two_step,
            dry=args.dry
        )

    return


def strength_func(args):
    """
    Wrapper for spin-phonon coupling strength CLI call
    """

    # Load CFP polynomials from file
    dQ, freqs = read_tau_style(args.cfp_file)

    # TODO delete
    args.n = 13
    args.J = 3.5
    args.L = 3
    args.S = 0.5

    if not args.nooef:
        # Get OEF values
        OEFs = calc_oef(args.n, args.J, args.L, args.S)
        print(np.shape(OEFs))

        # Add back in OEFs to polynomial values
        dQ *= OEFs

    # Calculate strength values of each mode
    S = np.array([calc_total_strength(mode) for mode in dQ])

    # Save strength to file
    np.savetxt("strengths.dat", S)
    print("Strengths saved to strengths.dat")

    # Read in symmetry labels if given
    if args.irreps:
        irreps = list(np.loadtxt(args.irreps, dtype=str))
    else:
        irreps = ['A']*len(freqs)

    unique_irreps, irrep_ints = np.unique(irreps, return_inverse=True)

    if args.plot:

        _, ax = plt.subplots(num='Spin-phonon coupling strength')

        for unique_int in np.unique(irrep_ints):
            ax.stem(
                freqs[np.nonzero(irrep_ints == unique_int)[0]],
                S[np.nonzero(irrep_ints == unique_int)[0]],
                basefmt=' ',
                linefmt='C{:d}-'.format(unique_int),
                markerfmt='C{:d}o'.format(unique_int)
            )
        if args.irreps:
            ax.legend(unique_irreps, frameon=False)

        ax.set_ylabel(r'$S$ (cm$^{-1}$)', fontname="Arial")
        ax.set_xlabel('Mode energy (cm$^{-1}$)', fontname="Arial")

        ax.set_ylim([0., np.max(S)*1.05])

        plt.savefig("strengths.svg")
        plt.savefig("strengths.png")
        print("Strength plots saved to strengths.svg and strengths.png")
        plt.show()

    return


def exp_func(args, unknown_args):
    """
    Wrapper for experimental data simulation CLI call
    """

    try:
        selected = args._selection
    except AttributeError:
        sys.exit("No experiment selected!")

    store_args = hpc.read_args(['store'] + unknown_args + ['-i'] + args.vibration_info)

    hpc.store_func(
        store_args,
        make_exp_evaluator,
        selected
    )

    return


def electric_field_func(args):
    """
    Model distortions due to an applied electric field from a single point
    frequency calculation in Gaussian16 or VASP

    Equation (Gas phase):
        -2 U^T H U U^T r = U^T ( 1/1! nabla_r mu * E + 1/2! nabla_r alpha * E^2 + ... )

    Equation (Solid state):
        -2 U^T H U U^T r = U^T (nabla_r mu * E)
    """

    if args.gaussian_fchk is not None:
        hess = make_gaussian_extractor(args.gaussian_fchk, ('fchk', 'hessian'))[()]
        coords = make_gaussian_extractor(args.gaussian_fchk, ('fchk', 'coordinates'))[()]
        grad_mu = make_gaussian_extractor(args.gaussian_fchk, ('fchk', 'dipole_derivatives'))[()]
        numbers = make_gaussian_extractor(args.gaussian_fchk, ('fchk', 'atomic_number'))[()]
        symbols = list(map(lambda x: chemical_symbols[x], numbers))

        # unit conversion
        hess *= HARTREE2J / BOHR2M**2  # J/m^2 = N/m
        grad_mu *= E0_TO_C  # C
        coords *= BOHR2M * 1e10  # Angstrom

        U = construct_atomic_basis(int(grad_mu.shape[0]/3), gaussian_fchk=True,
                                   coords=coords)  # units in angstrom
        hess = U.T @ hess @ U

        if args.field_vector is not None:
            E = np.array(args.field_vector)
            grad_mu_E = grad_mu @ E
            r = np.linalg.solve(-1 * hess, U.T @ grad_mu_E)
            r = (U @ r) * 1e10

            new_coords = coords + r.reshape(-1, 3)
            xyzp.save_xyz(args.output, symbols, new_coords)

        elif args.range is not None:
            args.range = args.range[0].split(' ')
            args.range = list(map(float, args.range))
            start, stop, step, dir = args.range
            field_range = np.linspace(start, stop, int(step))
            field_vector = np.eye(3)[int(dir)]
            for idx, field_strength in enumerate(field_range):
                E = field_strength * field_vector
                grad_mu_E = grad_mu @ E
                r = np.linalg.solve(-1 * hess, U.T @ grad_mu_E)
                r = (U @ r) * 1e10

                output = args.output.split('.')
                output = output[0] + '_{}'.format(idx) + '.' + output[1]
                xyzp.save_xyz(output, symbols, coords + r.reshape(-1, 3))

        elif args.field_sampling is not None:
            num_points = int(args.field_sampling[0])
            field_strength = args.field_sampling[1]
            field_vectors = field_strength * np.unique(normalised_sphere_vectors(num_points), axis=0)
            print("Number of sampled electric field {} of strength {} V/m".format(num_points, field_strength))
            with open('sample_fields.dat', 'w') as f:
                for idx, E in enumerate(field_vectors):
                    grad_mu_E = grad_mu @ E
                    r = np.linalg.solve(-2 * hess, U.T @ grad_mu_E)
                    r = (U @ r) * 1e10

                    output = args.output.split('.')
                    output = output[0] + '_{}'.format(idx) + '.' + output[1]
                    xyzp.save_xyz(output, symbols, coords + r.reshape(-1, 3))
                    f.write('{} {} {}\n'.format(*E))
            print('Sampled fields saved to sample_fields.dat')

    elif args.vasp_born is not None:
        struct = Structure.from_poscar(args.poscar)
        coords = struct.cart_coords
        symbols = struct.atom_list
        grad_mu = parse_BEC(args.poscar, args.vasp_born)

        # reshape of Z^*_{i,ab} -> dmu_{a}/dr_{i,b}
        # [i, a, b] -> [i, b, a] -> [ib, a] == [3N x 3]
        grad_mu = np.array(list(map(lambda x: x.T, grad_mu)))
        grad_mu = grad_mu.reshape(-1, 3)

        vibration = Harmonic.from_file(args.vibrational_info)
        hess = vibration.vasp_hessian
        U = construct_atomic_basis(int(hess.shape[0]/3), vasp_born=True)
        hess = U.T @ hess @ U
        # unit conversion
        grad_mu *= E0_TO_C  # C
        if not args.range:
            grad_mu_E = grad_mu @ np.array(args.field_vector)
            r = np.linalg.solve(hess, -2 * U.T @ grad_mu_E)
            r = U @ r
            r *= 1e10  # Å
            new_coords = coords + r.reshape(-1, 3)
            frac_coords = new_coords @ np.linalg.inv(struct.lattice_vectors)
            frac_coords %= 1
            struct.coords = frac_coords
            struct.write_poscar(args.output)
        else:
            start, stop, step, dir = args.range
            field_range = np.linspace(start, stop, int(step))
            field_vector = np.eye(3)[int(dir)]
            for field_strength in field_range:
                efield = field_strength * field_vector
                grad_mu_E = grad_mu @ efield

                r = np.linalg.solve(-2 * hess, U.T @ grad_mu_E)
                r = U @ r
                r *= 1e10  # Å
                output = args.output.split('.')
                output = output[0] + '_{:1.3e}'.format(field_strength) + '.' + output[1]
                frac_coords = (coords + r.reshape(-1, 3)) @ np.linalg.inv(struct.lattice_vectors)
                frac_coords %= 1
                struct.coords = frac_coords
                struct.write_poscar(output)

    else:
        raise NotImplementedError


def read_args(arg_list=None):
    description = '''
    A package for performing Spin-Phonon coupling calculations.
    '''

    parser = ArgumentParser(
            description=description,
            formatter_class=RawDescriptionHelpFormatter
            )

    subparsers = parser.add_subparsers(dest='prog')

    evaluate = subparsers.add_parser('eval')
    evaluate.set_defaults(func=eval_func)

    evaluate.add_argument(
        '-H',
        '--Help',
        action=FunctionHelp,
        help='show help message for additional arguments and exit'
    )

    evaluate.add_argument(
        '-L',
        '--lvc_data',
        type=str,
        help='HDF5 database containing the LVC parameters.'
    )

    evaluate.add_argument(
        '-V',
        '--vibration_info',
        type=str,
        help=('HDF5 database containing information about the vibrations.'
              'Derivatives are evaluated in the basis of dimension-less'
              'mass-frequency weighted normal mode coordinates.')
    )

    evaluate.add_argument(
        '--geom',
        nargs='+',
        help='*.xyz coordinates at which properties will be evaluated.'
    )

    evaluate.add_argument(
        '--order',
        type=int,
        default=0,
        help='Order of derivative.'
    )

    evaluate.add_argument(
        '--truncate',
        type=int,
        metavar="max_state",
        help='Truncate matrix elements at max_state'
    )

    evaluate.add_argument(
        '--align',
        action=BooleanOptionalAction,
        default=True,
        help='Align LVC model reference to input geometry by minimising RMSD.'
    )

    evaluate.add_argument(
        '--adiabatic_energies',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['mch', 'soc'],
        help='Energies of the MCH or SOC eigenstates.'
    )

    evaluate.add_argument(
        '--diabatic_hamiltonian',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['mch', 'soc'],
        help='Diabatic potential energy matrix between MCH or SOC states.'
    )

    evaluate.add_argument(
        '--proj',
        nargs='+',
        action=OrderedSelectionAction,
        help='Model Hamiltonian projection'
    )

    evaluate.add_argument(
        '--sus',
        nargs='+',
        action=OrderedSelectionAction,
        help='Magnetic susceptibility'
    )

    inp = subparsers.add_parser('generate_input')
    inp.set_defaults(func=generate_lvc_input_func)

    inp.add_argument(
        'old_project',
        type=str,
        help='Project name of preceding Molcas calculation.'
    )

    inp.add_argument(
        '--old_path',
        type=str,
        default='../',
        help='Path to WorkDir of preceding Molcas calculation.'
    )

    roots = inp.add_mutually_exclusive_group(required=True)

    roots.add_argument(
        '--num_roots',
        nargs='+',
        help='Number of states per JOBIPH.'
    )

    roots.add_argument(
        '--ion',
        type=str,
        help='Label of the metal center, e.g. Dy.'
    )

    inp.add_argument(
        '--jobiph',
        nargs='+',
        help='Indices of Molcas JOBIPH wavefunction files *_IPH.'
    )

    inp.add_argument(
        '--jobiph_paths',
        nargs='+',
        help='Paths of Molcas JOBIPH wavefunction files *_IPH.'
    )

    inp.add_argument(
        '--mclr_extra',
        nargs='+',
        default=((), {}),
        type=make_parse_dict(str, str, key_only=True),
        action=ParseExtra,
        help='Manually run mclr with custom options, e.g. thre=1e-8',
        metavar='name=value')

    inp.add_argument(
        '--alaska_extra',
        nargs='+',
        default=((), {}),
        type=make_parse_dict(str, str, key_only=True),
        action=ParseExtra,
        help='Run alaska with custom options, e.g. cuto=1e-8',
        metavar='name=value')

    inp.add_argument(
        '--two_step',
        action=BooleanOptionalAction,
        default=True,
        help='Utilize two-step procedure for MCLR runs'
    )

    inp.add_argument(
        '--dry',
        default=False,
        action='store_true',
        help='Dry-run which prints files to be created'
    )

    lvc = subparsers.add_parser('lvc')
    lvc.set_defaults(func=lvc_func)

    lvc.add_argument(
        '-L', '--lvc_data',
        type=str,
        help='HDF5 database output containing the LVC data.'
    )

    grad = lvc.add_mutually_exclusive_group()

    grad.add_argument(
        '--grad',
        type=str,
        nargs='+',
        help='Molcas output file(s) containing gradients and NACs.'
    )

    grad.add_argument(
        '--efld',
        type=str,
        nargs='+',
        help='Molcas output file(s) containing electric field values.'
    )

    grad.add_argument(
        '--add',
        type=str,
        nargs='+',
        help='LVC HDF5 data bases to be added.'
    )

    frozen = lvc.add_argument_group('Frozen density gradient arguments')

    frozen.add_argument(
        '--charge',
        type=str,
        nargs='+',
        help='Text file(s) containing point charge values.'
    )

    frozen.add_argument(
        '--xyz',
        type=str,
        nargs='+',
        help='xyz file(s) containing point charge coordinates.'
    )

    add = lvc.add_argument_group('LVC addition arguments')

    add.add_argument(
        '--reference_xyz',
        type=str,
        help='xyz file containing the reference coordinates.'
    )

    lvc.add_argument(
        '--rassi',
        type=str,
        help=('Molcas *.rassi.h5 output file containing AMFI integrals, '
              'SF_ANGMOM operators and the spin multiplicities.')
    )

    subset = lvc.add_mutually_exclusive_group()

    subset.add_argument(
        '--active_atoms',
        nargs='+',
        type=parse_index,
        help=(
            'atomic indices active during spin-phonon coupling. effectively '
            'effectively setting the coupling of all other atoms to zero. '
            'useful to suppress coupling of specific atoms.'
        )
    )

    subset.add_argument(
        '--ref_coordinates',
        help='xyz coordinates containing the atomic positions of active atoms.'
    )

    lvc.add_argument(
        '--verbose',
        action='store_true',
        help='Plot gradient norm and invariance measures.'
    )

    vibrate = subparsers.add_parser('vib', parents=[env.cluster])
    vibrate.set_defaults(func=vib_func)

    vibrate.add_argument(
        '-V', '--vibration_info',
        type=str,
        help='HDF5 database containing information about the vibrations.'
    )

    vib_calc_excl = vibrate.add_mutually_exclusive_group(required=True)

    vib_calc_excl.add_argument(
        '--gaussian_log',
        type=str,
        help='Text output of a gaussian freq calculation.'
    )

    vib_calc_excl.add_argument(
        '--gaussian_fchk',
        type=str,
        help='Formatted checkpoint file of a gaussian freq calculation.'
    )

    vib_calc_excl.add_argument(
        '--orca_hess',
        type=str,
        help='Orca *.hess file',
    )

    vib_calc_excl.add_argument(
        '--force_sets',
        type=str,
        help='FORCE_SETS file from VASP-phonopy pre-process.'
    )

    vib_calc_excl.add_argument(
        '--phonopy_hdf5',
        type=str,
        help='Phonon database from phono3py calculation.'
    )

    vib_calc_excl.add_argument(
        '--vasp_outcar',
        type=str,
        help='OUTCAR file from IBRION=5 calculation.'
    )

    vibrate.add_argument(
        '--poscar',
        type=str,
        help='Unit cell POSCAR from VASP-phonopy pre-process.'
    )

    vibrate.add_argument(
        '--force_expansion',
        nargs=3,
        metavar=('N_x', 'N_y', 'N_z'),
        default=(1, 1, 1),
        type=int,
        help='Supercell expansion used in phonon calculation'
    )

    qpoints = vibrate.add_mutually_exclusive_group()

    qpoints.add_argument(
        '--q_mesh',
        nargs=3,
        metavar=('N_x', 'N_y', 'N_z'),
        type=int,
        help='Mesh in q-space for phonon evaluation.'
    )

    vibrate.add_argument(
        '--mass',
        type=make_parse_dict(str_int, float),
        default={},
        nargs='+',
        action=ParseKwargs,
        help='Modify atomic masses for isotopic substitution.',
        metavar='atom_index=mass or element_symbol=mass'
    )

    vibrate.add_argument(
        '--trans',
        action=BooleanOptionalAction,
        default=True,
        help='Project out three rigid body translations.'
    )

    vibrate.add_argument(
        '--rot',
        action=BooleanOptionalAction,
        default=True,
        help='Project out three rigid body rotations.'
    )

    vibrate.add_argument(
        '--imaginary',
        default='remove',
        choices=['remove', 'keep', 'absolute'],
        help=('Remove modes with imaginary frequencies (default), '
             'keep without altering, or set to their absolute value.')
    )


    subset = vibrate.add_mutually_exclusive_group()

    subset.add_argument(
        '--active_atoms',
        nargs='+',
        type=parse_index,
        help=(
            'Atomic indices active during spin-phonon coupling. Effectively'
            ' subsets the displacement vectors. Useful if coupling is '
            'evaluated with a subset of the atoms present in the vibrational'
            ' calculation.'
        )
    )

    subset.add_argument(
        '--ref_coordinates',
        help='xyz coordinates containing the atomic positions of active atoms.'
    )

    vibrate.add_argument(
        '--save_pyvibms',
        type=str,
        help='optional pyvibms output for visualisation in PyMol.'
    )

    vibrate.add_argument(
        '--store_vecs',
        action=BooleanOptionalAction,
        default=True,
        help='Flag to disable expensive storage of normal mode displacements.'
    )

    prepare = subparsers.add_parser('prep')
    prepare.set_defaults(func=prepare_func)

    prepare.add_argument(
        'program',
        choices=['tau', 'tau_direct', 'firms', 'firms_direct'],
        help='Program for which to prepare inputs.'
    )

    dip = prepare.add_mutually_exclusive_group()

    dip.add_argument(
            '--gaussian_log',
            type=str,
            help='Gaussian log file',
    )

    dip.add_argument(
            '--gaussian_fchk',
            type=str,
            help='Gaussian log file',
    )

    dip.add_argument(
            '--vasp_born',
            type=str,
            help='VASP BORN file',
    )

    prepare.add_argument(
            '--poscar',
            type=str,
            help='VASP POSCAR file, required for VASP BORN file',
    )

    data = prepare.add_argument_group('database files')

    data.add_argument(
        '-L', '--lvc_data',
        help='HDF5 database containing the LVC parameters.')

    data.add_argument(
        '-V', '--vibration_info',
        help='HDF5 database containing information about the vibrations.')

    prepare.add_argument(
        '--ground_level',
        type=Level.parse,
        help='Symbol of the model space.'
    )

    prepare.add_argument(
        '--ion',
        type=Ion.parse,
        help='Central ion.'
    )

    prepare.add_argument(
        '--k_max',
        type=int,
        default=6,
        help='Maximum Stevens operator rank.'
    )

    prepare.add_argument(
        '--quax',
        action=angmom.QuaxAction,
        help='Quantisation axes.'
    )

    prepare.add_argument(
        '--truncate',
        type=int,
        metavar="max_state",
        help='Truncate matrix elements at max_state'
    )

    prepare.add_argument(
        '--trace_less',
        action=BooleanOptionalAction,
        default=True,
        help='Substract out trace from bare coupling elements.'
    )

    prepare.add_argument(
        '--active_atoms',
        nargs='+',
        type=parse_index,
        help=(
            'Atomic indices active during spin-phonon coupling. Effectively'
            ' subsets the displacement vectors. Useful if coupling is '
            'evaluated with a subset of the atoms present in the vibrational'
            ' calculation.'
        )
    )

    prepare.add_argument(
            '--red_masses',
            type=str,
            help='The reduced masses obtained from the gaussian log file using gaussian_suite extractor',
            )


    strength = subparsers.add_parser('strength')
    strength.set_defaults(func=strength_func)

    strength.add_argument(
        "cfp_file",
        type=str,
        help=(
            "File (hdf5 or CFP_polynomials) containing coupling crystal "
            "field parameters"
        )
    )

    strength.add_argument(
        "n",
        type=float,
        help=(
            "Number of unpaired electrons in 4f subshell"
        )
    )

    strength.add_argument(
        "J",
        type=float,
        help=(
            "Total angular momentum quantum number"
        )
    )

    strength.add_argument(
        "L",
        type=float,
        help=(
            "Orbital angular momentum quantum number"
        )
    )

    strength.add_argument(
        "S",
        type=float,
        help=(
            "Spin angular momentum quantum number"
        )
    )

    strength.add_argument(
        "--plot",
        action="store_true",
        help="Produce plot of strength as a function of mode energy"
    )

    strength.add_argument(
        '--irreps',
        type=str,
        metavar='<file_name>',
        help=(
            'Color code strength plot based on mode symmetries listed in file. '
            'File must contain column of IRREPs, one per mode'
        )
    )

    strength.add_argument(
        "--nooef",
        action="store_true",
        help="Produce plot of strength as a function of mode energy"
    )

    exp = subparsers.add_parser('exp')
    exp.set_defaults(func=exp_func)

    data = exp.add_argument_group('database files')

    data.add_argument(
        '-V', '--vibration_info',
        nargs='+',
        help='HDF5 database containing information about the vibrations.')

    exp.add_argument(
        '--nweights',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['coherent', 'incoherent'],
        help='Neutron scattering weights'
    )

    efield = subparsers.add_parser('efield_distort')
    efield.set_defaults(func=electric_field_func)

    state_input = efield.add_mutually_exclusive_group(required=True)

    state_input.add_argument(
        '--gaussian_fchk',
        type=str,
        help='Gaussian fchk file',
    )

    state_input.add_argument(
        '--vasp_born',
        type=str,
        help='VASP BORN file',
    )

    efield.add_argument(
        '--poscar',
        type=str,
        help='VASP POSCAR file, required for VASP BORN file',
    )

    efield.add_argument(
        '--vibrational_info',
        type=str,
        help='HDF5 database containing information about the vibrations.'
    )

    efield.add_argument(
        '--output', '-o',
        type=str,
        help='Output file name',
        required=True
    )

    field_type = efield.add_mutually_exclusive_group(required=True)

    field_type.add_argument(
        '--range',
        type=str,
        nargs=1,
        metavar=('min, max, steps, direction'),
        help='Range of field strengths, e.g. --range="start stop steps direction"'
    )

    field_type.add_argument(
        '--field_vector',
        type=float,
        nargs=3,
        metavar=('x', 'y', 'z'),
        help='Electric field vector',
    )

    field_type.add_argument(
        "--field_sampling",
        type=float,
        nargs=2,
        metavar=('Number of points', 'Field Strength'),
        help="Number of points and field strength for sampling"
    )

    # If arg_list==None, i.e. normal cli usage, parse_args() reads from
    # "sys.argv". The arg_list can be used to call the argparser from the
    # back end.

    # read sub-parser
    parser.set_defaults(func=lambda args: parser.print_help())
    _args, _ = parser.parse_known_args(arg_list)

    # select parsing option based on sub-parser
    if _args.prog in ['derivatives', 'eval', 'exp']:
        args, hpc_args = parser.parse_known_args(arg_list)
        args.func(args, hpc_args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)


def main():
    read_args()
