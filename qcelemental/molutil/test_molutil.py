import math
import pprint

import numpy as np
import pydantic
import pytest

import qcelemental as qcel
from qcelemental.testing import compare, compare_molrecs, compare_recursive, compare_values

from ..tests.addons import using_networkx

pp = pprint.PrettyPrinter(width=120)

ss22_12 = """
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
"""


@using_networkx
def test_scramble_descrambles_plain():
    s22_12 = qcel.models.Molecule.from_data(ss22_12)

    for trial in range(5):
        s22_12.scramble(do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0, do_test=True)


def test_relative_geoms_align_free():
    s22_12 = qcel.models.Molecule.from_data(ss22_12)

    for trial in range(3):
        cmol, _ = s22_12.scramble(
            do_shift=True, do_rotate=True, do_resort=False, do_plot=False, verbose=2, do_test=True
        )

        rmolrec = qcel.molparse.from_schema(s22_12.dict())
        cmolrec = qcel.molparse.from_schema(cmol.dict())
        assert compare_molrecs(rmolrec, cmolrec, atol=1.0e-4, relative_geoms="align")


def test_relative_geoms_align_fixed():
    s22_12 = qcel.models.Molecule.from_data(ss22_12 + "nocom\nnoreorient\n")

    for trial in range(3):
        cmol, _ = s22_12.scramble(
            do_shift=False, do_rotate=False, do_resort=False, do_plot=False, verbose=2, do_test=True
        )

        rmolrec = qcel.molparse.from_schema(s22_12.dict())
        cmolrec = qcel.molparse.from_schema(cmol.dict())
        assert compare_molrecs(rmolrec, cmolrec, atol=1.0e-4, relative_geoms="align")


chiral = qcel.models.Molecule.from_data(
    """
 C     0.000000     0.000000     0.000000
Br     0.000000     0.000000     1.949834
 F     1.261262     0.000000    -0.451181
Cl    -0.845465     1.497406    -0.341118
 H    -0.524489    -0.897662    -0.376047
"""
)


@using_networkx
def test_scramble_descrambles_chiral():
    chiral.scramble(
        do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0, do_mirror=False, do_test=True
    )
    chiral.scramble(
        do_shift=True, do_rotate=True, do_resort=False, do_plot=False, verbose=1, do_mirror=False, do_test=True
    )
    for trial in range(5):
        chiral.scramble(
            do_shift=True, do_rotate=True, do_resort=True, do_plot=False, verbose=0, do_mirror=True, do_test=True
        )


soco10 = """
O  1.0 0.0 0.0
C  0.0 0.0 0.0
O -1.0 0.0 0.0
units ang
"""

sooc12 = """
O  1.2 4.0 0.0
O -1.2 4.0 0.0
C  0.0 4.0 0.0
units ang
"""

s18ooc12 = """
18O  1.2 4.0 0.0
O -1.2 4.0 0.0
C  0.0 4.0 0.0
units ang
"""

sooco12 = """
O  1.2 4.0 0.0
O -1.2 4.0 0.0
C  0.0 4.0 0.0
O  3.0 4.0 0.0
units ang
"""

soco12 = """
O  1.2 4.0 0.0
C  0.0 4.0 0.0
O -1.2 4.0 0.0
units ang
"""

ref_rmsd = math.sqrt(2.0 * 0.2 * 0.2 / 3.0)  # RMSD always in Angstroms


@using_networkx
def test_error_bins_b787():
    oco10 = qcel.models.Molecule.from_data(soco10)
    oco12 = qcel.models.Molecule.from_data(s18ooc12)

    with pytest.raises(qcel.ValidationError) as e:
        oco12.align(oco10, verbose=0)

    assert "atom subclasses unequal" in str(e.value)


@using_networkx
def test_error_nat_b787():
    oco10 = qcel.models.Molecule.from_data(soco10)
    oco12 = qcel.models.Molecule.from_data(sooco12)

    with pytest.raises(qcel.ValidationError) as e:
        oco12.align(oco10, verbose=0)

    assert "natom doesn't match" in str(e.value)


def test_mill_shift_error():
    with pytest.raises(pydantic.ValidationError) as e:
        qcel.models.AlignmentMill(shift=[0, 1])

    assert "Shift must be castable to shape" in str(e.value)


def test_mill_rot_error():
    with pytest.raises(pydantic.ValidationError) as e:
        qcel.models.AlignmentMill(rotation=[0, 1, 3])

    assert "Rotation must be castable to shape" in str(e.value)


@using_networkx
def test_b787():
    oco10 = qcel.molparse.from_string(soco10)
    oco12 = qcel.molparse.from_string(sooc12)

    oco10_geom_au = oco10["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms
    oco12_geom_au = oco12["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms

    rmsd, mill = qcel.molutil.B787(
        oco10_geom_au,
        oco12_geom_au,
        np.array(["O", "C", "O"]),
        np.array(["O", "O", "C"]),
        algorithm="permutative",
        verbose=4,
        do_plot=False,
    )

    assert compare_values(ref_rmsd, rmsd, "known rmsd B787", atol=1.0e-6)


@using_networkx
def test_b787_atomsmap():
    oco10 = qcel.molparse.from_string(soco10)
    oco12 = qcel.molparse.from_string(soco12)

    oco10_geom_au = oco10["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms
    oco12_geom_au = oco12["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms

    rmsd, mill = qcel.molutil.B787(oco10_geom_au, oco12_geom_au, None, None, atoms_map=True)

    assert compare_values(ref_rmsd, rmsd, "known rmsd B787", atol=1.0e-6)


@using_networkx
def test_model_b787():
    oco10 = qcel.models.Molecule.from_data(soco10)
    oco12 = qcel.models.Molecule.from_data(sooc12)

    mol, data = oco12.align(oco10, verbose=4)

    assert compare_values(ref_rmsd, data["rmsd"], "known rmsd qcel.models.Molecule.align", atol=1.0e-6)


def test_error_kabsch():
    with pytest.raises(qcel.ValidationError) as e:
        qcel.molutil.kabsch_align([1, 2, 3], [4, 5, 6], weight=7)

    assert "for kwarg 'weight'" in str(e.value)


@using_networkx
def test_kabsch_identity():
    oco10 = qcel.molparse.from_string(soco10)
    oco12 = qcel.molparse.from_string(soco10)

    oco10_geom_au = oco10["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms
    oco12_geom_au = oco12["qm"]["geom"].reshape((-1, 3)) / qcel.constants.bohr2angstroms

    rmsd, rot, shift = qcel.molutil.kabsch_align(oco10_geom_au, oco12_geom_au)

    assert compare_values(0.0, rmsd, "identical")
    assert compare_values(np.identity(3), rot, "identity rotation matrix")
    assert compare_values(np.zeros(3), shift, "identical COM")


trop_cs = qcel.models.Molecule.from_data(
    """
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
"""
)

trop_gs_c2v = qcel.models.Molecule.from_data(
    """
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
"""
)


@using_networkx
def test_tropolone_b787():
    mol, data = trop_cs.align(trop_gs_c2v, do_plot=False, verbose=0, uno_cutoff=0.5)
    assert compare_values(0.1413, data["rmsd"], "cs<-->c2v tropolones align", atol=1.0e-2)


def test_scramble_identity():
    mill = qcel.molutil.compute_scramble(
        4, do_resort=False, do_shift=False, do_rotate=False, deflection=1.0, do_mirror=False
    )

    mill_str = """----------------------------------------
             AlignmentMill
                  eye
----------------------------------------
Mirror:   False
Atom Map: [0 1 2 3]
Shift:    [0. 0. 0.]
Rotation:
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]
----------------------------------------"""

    assert compare(mill_str, mill.pretty_print(label="eye"))

    mill_dict = {
        "shift": [0.0, 0.0, 0.0],
        "rotation": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "atommap": [0, 1, 2, 3],
        "mirror": False,
    }

    assert compare_recursive(mill_dict, mill.dict())
    mill_dict["rotation"] = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    assert compare_recursive(mill_dict, mill.dict(encoding="json"))


def test_scramble_specific():
    mill = qcel.molutil.compute_scramble(
        4,
        do_resort=[1, 2, 0, 3],
        do_shift=[-1.82564537, 2.25391838, -2.56591963],
        do_rotate=[
            [0.39078817, -0.9101616, -0.13744259],
            [0.36750838, 0.29117465, -0.88326379],
            [0.84393258, 0.29465774, 0.44827962],
        ],
    )

    mill_str = """----------------------------------------
             AlignmentMill
----------------------------------------
Mirror:   False
Atom Map: [1 2 0 3]
Shift:    [-1.82564537  2.25391838 -2.56591963]
Rotation:
[[ 0.39078817 -0.9101616  -0.13744259]
 [ 0.36750838  0.29117465 -0.88326379]
 [ 0.84393258  0.29465774  0.44827962]]
----------------------------------------"""

    assert compare(mill_str, mill.pretty_print())


def test_hessian_align():
    # from Psi4 test test_hessian_vs_cfour[HOOH_TS-H_analytic]

    # fmt: off
    rmill = """
----------------------------------------
             AlignmentMill
----------------------------------------
Mirror:   False
Atom Map: [0 1 2 3]
Shift:    [0.00000000e+00 0.00000000e+00 1.32217718e-10]
Rotation:
[[ 9.99999870e-01 -5.08999836e-04 -0.00000000e+00]
 [ 5.08999836e-04  9.99999870e-01  0.00000000e+00]
 [ 0.00000000e+00 -0.00000000e+00  1.00000000e+00]]
----------------------------------------
"""

    p4_hooh_xyz = """
    units au
    H  1.8327917647 -1.5752960165 -0.0000055594
    O  1.3171390326  0.1388012713  0.0000003503
    O -1.3171390326 -0.1388012713  0.0000003503
    H -1.8327917647  1.5752960165 -0.0000055594
    """

    c4_hooh_xyz = """
         H                  1.83199008    -1.57622903    -0.00000556
         O                  1.31720978     0.13813086     0.00000035
         O                 -1.31720978    -0.13813086     0.00000035
         H                 -1.83199008     1.57622903    -0.00000556
         units au"""

    c4_hooh_hess = np.array(
    [[ 1.26389745e-01, -1.48044116e-01, -5.10600000e-07, -8.25705803e-02,
       8.94682153e-02,  3.59200000e-07, -2.97329883e-02,  6.20787276e-02,
       1.15100000e-07, -1.40861766e-02, -3.50282710e-03,  3.62000000e-08],
     [-1.48044116e-01,  5.70582596e-01,  1.97410000e-06,  1.70543201e-01,
      -5.85505592e-01, -2.01940000e-06, -1.89962579e-02,  1.41465336e-02,
       4.31000000e-08, -3.50282710e-03,  7.76462400e-04,  2.30000000e-09],
     [-5.10600000e-07,  1.97410000e-06, -1.39249540e-03,  5.48500000e-07,
      -2.04760000e-06,  1.39251280e-03, -1.70000000e-09,  7.57000000e-08,
       1.39261030e-03, -3.62000000e-08, -2.30000000e-09, -1.39262780e-03],
     [-8.25705803e-02,  1.70543201e-01,  5.48500000e-07,  4.71087328e-01,
      -1.32453772e-01, -3.97100000e-07, -3.58783760e-01, -1.90931709e-02,
      -1.53000000e-07, -2.97329883e-02, -1.89962579e-02,  1.70000000e-09],
     [ 8.94682153e-02, -5.85505592e-01, -2.04760000e-06, -1.32453772e-01,
       6.80349634e-01,  2.09300000e-06, -1.90931709e-02, -1.08990576e-01,
       3.04000000e-08,  6.20787276e-02,  1.41465336e-02, -7.57000000e-08],
     [ 3.59200000e-07, -2.01940000e-06,  1.39251280e-03, -3.97100000e-07,
       2.09300000e-06, -1.39226390e-03,  1.53000000e-07, -3.04000000e-08,
      -1.39285910e-03, -1.15100000e-07, -4.31000000e-08,  1.39261030e-03],
     [-2.97329883e-02, -1.89962579e-02, -1.70000000e-09, -3.58783760e-01,
      -1.90931709e-02,  1.53000000e-07,  4.71087328e-01, -1.32453772e-01,
       3.97100000e-07, -8.25705803e-02,  1.70543201e-01, -5.48500000e-07],
     [ 6.20787276e-02,  1.41465336e-02,  7.57000000e-08, -1.90931709e-02,
      -1.08990576e-01, -3.04000000e-08, -1.32453772e-01,  6.80349634e-01,
      -2.09300000e-06,  8.94682153e-02, -5.85505592e-01,  2.04760000e-06],
     [ 1.15100000e-07,  4.31000000e-08,  1.39261030e-03, -1.53000000e-07,
       3.04000000e-08, -1.39285910e-03,  3.97100000e-07, -2.09300000e-06,
      -1.39226390e-03, -3.59200000e-07,  2.01940000e-06,  1.39251280e-03],
     [-1.40861766e-02, -3.50282710e-03, -3.62000000e-08, -2.97329883e-02,
       6.20787276e-02, -1.15100000e-07, -8.25705803e-02,  8.94682153e-02,
      -3.59200000e-07,  1.26389745e-01, -1.48044116e-01,  5.10600000e-07],
     [-3.50282710e-03,  7.76462400e-04, -2.30000000e-09, -1.89962579e-02,
       1.41465336e-02, -4.31000000e-08,  1.70543201e-01, -5.85505592e-01,
       2.01940000e-06, -1.48044116e-01,  5.70582596e-01, -1.97410000e-06],
     [ 3.62000000e-08,  2.30000000e-09, -1.39262780e-03,  1.70000000e-09,
      -7.57000000e-08,  1.39261030e-03, -5.48500000e-07,  2.04760000e-06,
       1.39251280e-03,  5.10600000e-07, -1.97410000e-06, -1.39249540e-03]])

    # generated from native psi4 geometry before alignment to cfour geometry
    p4_hooh_hess_native = np.array(
    [[ 1.26540599e-01, -1.48270387e-01, -5.11580572e-07, -8.27030303e-02,
       8.97243491e-02,  3.60275814e-07, -2.97549532e-02,  6.20564277e-02,
       1.15085371e-07, -1.40826158e-02, -3.51038930e-03,  3.62193872e-08],
     [-1.48270387e-01,  5.70432494e-01,  1.97383511e-06,  1.70799401e-01,
      -5.85373844e-01, -2.01926658e-06, -1.90186246e-02,  1.41684555e-02,
       4.31889743e-08, -3.51038930e-03,  7.72894141e-04,  2.24249453e-09],
     [-5.11580572e-07,  1.97383511e-06, -1.39261744e-03,  5.49492724e-07,
      -2.04733779e-06,  1.39262576e-03, -1.69276446e-09,  7.57451701e-08,
       1.39262075e-03, -3.62193872e-08, -2.24249453e-09, -1.39262906e-03],
     [-8.27030303e-02,  1.70799401e-01,  5.49492724e-07,  4.71222858e-01,
      -1.32560453e-01, -3.98187966e-07, -3.58764874e-01, -1.92203240e-02,
      -1.52997522e-07, -2.97549532e-02, -1.90186246e-02,  1.69276446e-09],
     [ 8.97243491e-02, -5.85373844e-01, -2.04733779e-06, -1.32560453e-01,
       6.80215453e-01,  2.09276925e-06, -1.92203240e-02, -1.09010064e-01,
       3.03137013e-08,  6.20564277e-02,  1.41684555e-02, -7.57451701e-08],
     [ 3.60275814e-07, -2.01926658e-06,  1.39262576e-03, -3.98187966e-07,
       2.09276925e-06, -1.39245013e-03,  1.52997522e-07, -3.03137013e-08,
      -1.39279639e-03, -1.15085371e-07, -4.31889743e-08,  1.39262075e-03],
     [-2.97549532e-02, -1.90186246e-02, -1.69276446e-09, -3.58764874e-01,
      -1.92203240e-02,  1.52997522e-07,  4.71222858e-01, -1.32560453e-01,
       3.98187966e-07, -8.27030303e-02,  1.70799401e-01, -5.49492724e-07],
     [ 6.20564277e-02,  1.41684555e-02,  7.57451701e-08, -1.92203240e-02,
      -1.09010064e-01, -3.03137013e-08, -1.32560453e-01,  6.80215453e-01,
      -2.09276925e-06,  8.97243491e-02, -5.85373844e-01,  2.04733779e-06],
     [ 1.15085371e-07,  4.31889743e-08,  1.39262075e-03, -1.52997522e-07,
       3.03137013e-08, -1.39279639e-03,  3.98187966e-07, -2.09276925e-06,
      -1.39245013e-03, -3.60275814e-07,  2.01926658e-06,  1.39262576e-03],
     [-1.40826158e-02, -3.51038930e-03, -3.62193872e-08, -2.97549532e-02,
       6.20564277e-02, -1.15085371e-07, -8.27030303e-02,  8.97243491e-02,
      -3.60275814e-07,  1.26540599e-01, -1.48270387e-01,  5.11580572e-07],
     [-3.51038930e-03,  7.72894141e-04, -2.24249453e-09, -1.90186246e-02,
       1.41684555e-02, -4.31889743e-08,  1.70799401e-01, -5.85373844e-01,
       2.01926658e-06, -1.48270387e-01,  5.70432494e-01, -1.97383511e-06],
     [ 3.62193872e-08,  2.24249453e-09, -1.39262906e-03,  1.69276446e-09,
      -7.57451701e-08,  1.39262075e-03, -5.49492724e-07,  2.04733779e-06,
       1.39262576e-03,  5.11580572e-07, -1.97383511e-06, -1.39261744e-03]])

    # fmt: on

    p4mol = qcel.models.Molecule.from_data(p4_hooh_xyz)
    c4mol = qcel.models.Molecule.from_data(c4_hooh_xyz)
    aqmol, data = p4mol.align(c4mol, atoms_map=True, mols_align=True, verbose=4)
    mill = data["mill"]

    assert compare([0, 1, 2, 3], mill.atommap)
    assert compare_values(
        [
            [9.99999870e-01, -5.08999836e-04, -0.00000000e00],
            [5.08999836e-04, 9.99999870e-01, 0.00000000e00],
            [0.00000000e00, -0.00000000e00, 1.00000000e00],
        ],
        mill.rotation,
        atol=1.0e-6,
    )

    p2cgeom = mill.align_coordinates(p4mol.geometry)
    assert compare_values(c4mol.geometry, p2cgeom, atol=1.0e-6)

    p2chess = mill.align_hessian(p4_hooh_hess_native)
    assert compare_values(c4_hooh_hess, p2chess, atol=1.0e-4)


@using_networkx
def test_vector_gradient_align():
    # fmt: off

    # HOOH TS (optimized to be very nearly planar)
    p4_hooh_xyz = """
    units au
    H  1.8327917647 -1.5752960165 -0.0000055594
    O  1.3171390326  0.1388012713  0.0000003503
    O -1.3171390326 -0.1388012713  0.0000003503
    H -1.8327917647  1.5752960165 -0.0000055594
    """

    # from C4 GRD file, produced by p4_hooh_xyz in ZMAT
    c4_hooh_xyz = """
    units au
    H  1.8319897007 -1.5762287045  -0.0000055594
    H -1.8319897007  1.5762287045  -0.0000055594
    O  1.3172095119  0.1381308288   0.0000003503
    O -1.3172095119 -0.1381308288   0.0000003503
    """

    # From C4 DIPDER file, analytic
    c4_hooh_dipder_x = np.array([
        0.2780463810,      -0.0627423838,      -0.0000001663,
        0.2780463810,      -0.0627423838,       0.0000001663,
       -0.2780463810,       0.0627423838,       0.0000007872,
       -0.2780463810,       0.0627423838,      -0.0000007872])
    c4_hooh_dipder_y = np.array([
       -0.0452364698,       0.2701572972,      -0.0000004246,
       -0.0452364698,       0.2701572972,       0.0000004246,
        0.0452364698,      -0.2701572972,       0.0000007936,
        0.0452364698,      -0.2701572972,      -0.0000007936])
    c4_hooh_dipder_z = np.array([
       -0.0000001575,      -0.0000004725,       0.4019549601,
        0.0000001575,       0.0000004725,       0.4019549601,
       -0.0000000523,       0.0000008401,      -0.4019549601,
        0.0000000523,      -0.0000008401,      -0.4019549601])

    # Generated from fixing orientation/com in psi4.  Then using
    # a 5-point finite differences of nuclear gradients computed
    # with an applied electric field to produce a file17.dat.
    p4_hooh_dipder_x  = np.array([
        0.2781013514,      -0.0627383175,      -0.0000001660,
       -0.2781013514,       0.0627383175,       0.0000007867,
       -0.2781013514,       0.0627383175,      -0.0000007867,
        0.2781013514,      -0.0627383175,       0.0000001660])
    p4_hooh_dipder_y  = np.array([
       -0.0452324587,       0.2701024305,      -0.0000004247,
        0.0452324587,      -0.2701024305,       0.0000007939,
        0.0452324587,      -0.2701024305,      -0.0000007939,
       -0.0452324587,       0.2701024305,       0.0000004247])
    p4_hooh_dipder_z  = np.array([
       -0.0000001572,      -0.0000004726,       0.4019549470,
       -0.0000000527,       0.0000008401,      -0.4019549470,
        0.0000000527,      -0.0000008401,      -0.4019549470,
        0.0000001572,       0.0000004726,       0.4019549470])
    p4_hooh_dipder = np.concatenate((p4_hooh_dipder_x, p4_hooh_dipder_y, p4_hooh_dipder_z)).reshape(3, -1)

    # fmt: on

    p4mol = qcel.models.Molecule.from_data(p4_hooh_xyz)
    c4mol = qcel.models.Molecule.from_data(c4_hooh_xyz)
    aqmol, data = p4mol.align(c4mol, atoms_map=False, mols_align=True, verbose=4)
    mill = data["mill"]

    assert compare([0, 3, 1, 2], mill.atommap)

    p2cgeom = mill.align_coordinates(p4mol.geometry)
    assert compare_values(c4mol.geometry, p2cgeom, atol=1.0e-6)

    p2c_dipder_x, p2c_dipder_y, p2c_dipder_z = mill.align_vector_gradient(p4_hooh_dipder)

    assert compare_values(c4_hooh_dipder_x, p2c_dipder_x, atol=1.0e-5)
    assert compare_values(c4_hooh_dipder_y, p2c_dipder_y, atol=1.0e-5)
    assert compare_values(c4_hooh_dipder_z, p2c_dipder_z, atol=1.0e-5)


@pytest.mark.parametrize(
    "args, kwargs, ans",
    [
        ((["C", "C"], [0, 0, 0, 0, 0, 3]), {}, [(0, 1)]),
        ((["C", "C"], [0, 0, 0, 0, 0, 3]), {"threshold": 4}, [(0, 1)]),
        ((["C", "C"], [0, 0, 0, 0, 0, 10]), {}, []),
        ((["C", "C"], [0, 0, 0, 0, 0, 2]), {"default_connectivity": 3}, [(0, 1, 3)]),
        ((["C", "C", "C"], [0, 0, 0, 0, 0, 3, 0, 0, -3]), {}, [(0, 1), (0, 2)]),
        ((["C", "Unknown"], [0, 0, 0, 0, 0, 3]), {}, [(0, 1)]),
    ],
)
def test_guess_connectivity(args, kwargs, ans):

    computed = qcel.molutil.guess_connectivity(*args, **kwargs)
    assert compare(computed, ans)


@pytest.mark.parametrize(
    "input,order,expected",
    [
        ("NH3", "alphabetical", "H3N"),
        ("NH3", "hill", "H3N"),
        ("CH4", "alphabetical", "CH4"),
        ("CH4", "hill", "CH4"),
        ("IBr", "alphabetical", "BrI"),
        ("IBr", "hill", "BrI"),
        ("CCl4", "alphabetical", "CCl4"),
        ("CCl4", "hill", "CCl4"),
        ("CBr4", "alphabetical", "Br4C"),
        ("CBr4", "hill", "CBr4"),
        ("CBrH3", "alphabetical", "BrCH3"),
        ("CBrH3", "hill", "CH3Br"),
    ],
)
def test_order_molecular_formula(input, order, expected):
    assert qcel.molutil.order_molecular_formula(input, order=order) == expected


def test_bad_formula_order():
    with pytest.raises(ValueError):
        qcel.molutil.order_molecular_formula("CH4", order="disorder")
    with pytest.raises(ValueError):
        qcel.molutil.order_molecular_formula("ch4")
