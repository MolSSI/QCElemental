import pytest
from .addons import using_networkx

import math
import pprint

import numpy as np

import qcelemental as qcel
from qcelemental.testing import compare_values



s22_12 = qcel.models.Molecule.from_data("""
C    -1.2471894   -1.1718212   -0.6961388
C    -1.2471894   -1.1718212    0.6961388
N    -0.2589510   -1.7235771    1.4144796
C     0.7315327   -2.2652221    0.6967288
C     0.7315327   -2.2652221   -0.6967288
N    -0.2589510   -1.7235771   -1.4144796
H    -2.0634363   -0.7223199   -1.2472797
H    -2.0634363   -0.7223199    1.2472797
H     1.5488004   -2.7128282    1.2475604
H     1.5488004   -2.7128282   -1.2475604
C    -0.3380031    2.0800608    1.1300452
C     0.8540254    1.3593471    1.1306308
N     1.4701787    0.9907598    0.0000000
C     0.8540254    1.3593471   -1.1306308
C    -0.3380031    2.0800608   -1.1300452
N    -0.9523059    2.4528836    0.0000000
H    -0.8103758    2.3643033    2.0618643
H     1.3208583    1.0670610    2.0623986
H     1.3208583    1.0670610   -2.0623986
H    -0.8103758    2.3643033   -2.0618643
""")

for trial in range(5):
    s22_12.scramble(do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0)

chiral = qcel.models.Molecule.from_data("""
 C     0.000000     0.000000     0.000000
Br     0.000000     0.000000     1.949834
 F     1.261262     0.000000    -0.451181
Cl    -0.845465     1.497406    -0.341118
 H    -0.524489    -0.897662    -0.376047
""")

chiral.scramble(do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0, do_mirror=False)
for trial in range(5):
    chiral.scramble(do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0, do_mirror=True)


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
