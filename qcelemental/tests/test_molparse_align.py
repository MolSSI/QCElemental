import math
import pprint

import numpy as np

import qcelemental as qcel
from qcelemental.testing import  compare_values
import pytest


oco10 = qcel.molparse.from_string("""
O  1.0 0.0 0.0
C  0.0 0.0 0.0
O -1.0 0.0 0.0
units ang
""")

oco12 = qcel.molparse.from_string("""
O  1.2 4.0 0.0
O -1.2 4.0 0.0
C  0.0 4.0 0.0
units ang
""")

ref_rmsd = math.sqrt(2. * 0.2 * 0.2 / 3.)  # RMSD always in Angstroms

def test_b787():
    oco10_geom_au = oco10['qm']['geom'].reshape((-1, 3)) / qcel.constants.bohr2angstroms
    oco12_geom_au = oco12['qm']['geom'].reshape((-1, 3)) / qcel.constants.bohr2angstroms

    rmsd, mill = qcel.molparse.B787(oco10_geom_au, oco12_geom_au, np.array(['O', 'C', 'O']), np.array(['O', 'O', 'C']), verbose=0, do_plot=False)

    assert compare_values(ref_rmsd, rmsd, 'known rmsd B787', atol=1.e-6)
