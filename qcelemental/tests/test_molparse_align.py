import pytest
from .addons import using_networkx

import math
import pprint

import numpy as np

import qcelemental as qcel
from qcelemental.testing import compare_values

soco10 = """
O  1.0 0.0 0.0
C  0.0 0.0 0.0
O -1.0 0.0 0.0
units ang
"""

soco12 = """
O  1.2 4.0 0.0
O -1.2 4.0 0.0
C  0.0 4.0 0.0
units ang
"""

ref_rmsd = math.sqrt(2. * 0.2 * 0.2 / 3.)  # RMSD always in Angstroms


@using_networkx
def test_b787():
    oco10 = qcel.molparse.from_string(soco10)
    oco12 = qcel.molparse.from_string(soco12)

    oco10_geom_au = oco10['qm']['geom'].reshape((-1, 3)) / qcel.constants.bohr2angstroms
    oco12_geom_au = oco12['qm']['geom'].reshape((-1, 3)) / qcel.constants.bohr2angstroms

    rmsd, mill = qcel.molparse.B787(
        oco10_geom_au, oco12_geom_au, np.array(['O', 'C', 'O']), np.array(['O', 'O', 'C']), verbose=0, do_plot=False)

    assert compare_values(ref_rmsd, rmsd, 'known rmsd B787', atol=1.e-6)


@using_networkx
def test_model_b787():
    oco10 = qcel.models.Molecule.from_data(soco10)
    oco12 = qcel.models.Molecule.from_data(soco12)

    rmsd, mill, mol = oco12.B787(oco10, verbose=0)

    assert compare_values(ref_rmsd, rmsd, 'known rmsd qcel.models.Molecule.B787', atol=1.e-6)


trop_cs = qcel.models.Molecule.from_data("""
     C        -3.19247825     2.43488661     0.00000000
     C        -4.39993972     0.13119097     0.00000000
     C        -3.25125097    -2.33609553     0.00000000
     C        -0.53296611     2.98441107     0.00000000
     C        -0.74683325    -3.02798473     0.00000000
     C         1.48688415     1.34759833     0.00000000
     H        -4.41324589     4.10714388     0.00000000
     H        -6.46804026     0.15889833     0.00000000
     H        -4.59260816    -3.91576186     0.00000000
     H        -0.00999373     4.98699344     0.00000000
     H        -0.30873683    -5.05056347     0.00000000
     C         1.53303555    -1.47231513     0.00000000
     O         3.67104984    -2.45774212     0.00000000
     O         3.84147141     2.33923482     0.00000000
     H         4.95785438     0.85953513     0.00000000
     units au
""")

trop_gs_c2v = qcel.models.Molecule.from_data("""
     C         2.38842439     0.00000000    -3.20779039
     C         0.00000000     0.00000000    -4.37431891
     C        -2.38842439     0.00000000    -3.20779039
     C         3.04548001     0.00000000    -0.63779964
     C        -3.04548001     0.00000000    -0.63779964
     C         1.40969252     0.00000000     1.46237865
     C        -1.40969252     0.00000000     1.46237865
     O         2.17618825     0.00000000     3.78161558
     O        -2.17618825     0.00000000     3.78161558
     H         0.00000000     0.00000000     4.59454571
     H         0.00000000     0.00000000    -6.44213321
     H         4.00103632     0.00000000    -4.50882987
     H        -4.00103632     0.00000000    -4.50882987
     H         5.05910161     0.00000000    -0.16572021
     H        -5.05910161     0.00000000    -0.16572021
     units au
""")

@using_networkx
def test_tropolone_b787():
    rmsd, mill, mol = trop_cs.B787(trop_gs_c2v, do_plot=False, verbose=0, uno_cutoff=0.5)
    assert compare_values(0.1413, rmsd, 'cs<-->c2v tropolones align', atol=1.e-2)
