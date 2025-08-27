#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "1.12.0"

setuptools.setup(
    name='spin_phonon_suite',
    version=__version__,
    author='Chilton Group',
    author_email='nicholas.chilton@manchester.ac.uk',
    description='A package for performing spin-phonon coupling calculations with openMOLCAS, VASP, and Gaussian', # noqa
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/chilton-group/spin_phonon_suite",
    project_urls={
        "Bug Tracker": "https://gitlab.com/chilton-group/spin_phonon_suite/-/issues", # noqa
        "Documentation": "https://chilton-group.gitlab.io/spin_phonon_suite"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
        ],
    python_requires='>=3.9',
    install_requires=[
        'numpy < 2.0.0',
        'scipy',
        'h5py',
        'xyz_py>=5.1.0',
        'angmom_suite>=1.22.0',
        'hpc_suite>=1.8.0',
        'matplotlib',
        'gaussian_suite>=1.11.0',
        'phonopy',
        'molvis>=0.3.0',
        'molcas_suite>=1.21.0',
        'ase',
        'env_suite',
        'vasp_suite>=1.9.0',
        'spglib==2.0.2',
        ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'spin_phonon_suite = spin_phonon_suite.cli:main'
            ]
        }
    )
