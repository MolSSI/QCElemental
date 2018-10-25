import copy

import numpy as np
import pytest

from utils import *

import qcelemental

_string_prov_stamp = {'creator': 'QCElemental', 'version': '1.0', 'routine': 'qcelemental.molparse.from_string'}

subject14 = """0 3\n--\nHe 0 0 -5\n--\n@He 0 0 5\nunits au"""

schema14_1 = {
    "geometry": [0.0, 0.0, -5.0, 0.0, 0.0, 5.0],
    "symbols": ["He", "He"],
    "atomic_numbers": [2, 2],
    "mass_numbers": [4, 4],
    "atom_labels": ['', ''],
    'fragments': [[0], [1]],
    'fragment_charges': [0.0, 0.0],
    'fragment_multiplicities': [3, 1],
    'masses': [4.00260325413, 4.00260325413],
    'name': 'He2',
    'fix_com': False,
    'fix_orientation': False,
    'molecular_charge': 0.0,
    "molecular_multiplicity": 3,
    "real": [True, False]
}

schema14_psi4 = {
    "geom": [0.0, 0.0, -5.0, 0.0, 0.0, 5.0],
    "elem": ["He", "He"],
    'elea': [4, 4],
    'elez': [2, 2],
    'fragment_charges': [0.0, 0.0],
    'fragment_multiplicities': [3, 1],
    'mass': [4.00260325413, 4.00260325413],
    'name': 'He2',
    'fix_com': False,
    'fix_orientation': False,
    'molecular_charge': 0.0,
    "molecular_multiplicity": 3,
    'units': 'Bohr',
    'fragment_separators': [1],
    'elbl': ['', ''],
    "real": [True, False]
}


def test_1_14a():
    fullans = copy.deepcopy(schema14_1)
    fullans['provenance'] = [_string_prov_stamp]

    final = qcelemental.molparse.from_string(subject14)
    kmol = qcelemental.molparse.to_schema(final['qm'], dtype=1)
    assert compare_molrecs(fullans, kmol, 4, tnm())


def test_1_ang_14b():

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final['qm'], dtype=1, units='Angstrom')

    assert "QC_JSON_Schema 1 allows only 'Bohr' coordinates" in str(e)


def test_psi4_14c():
    fullans = copy.deepcopy(schema14_psi4)
    fullans['provenance'] = [_string_prov_stamp]

    final = qcelemental.molparse.from_string(subject14)
    kmol = qcelemental.molparse.to_schema(final['qm'], dtype='psi4')
    assert compare_molrecs(fullans, kmol, 4, tnm())


def test_dtype_d():

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final['qm'], dtype='xkcd927')

    assert "Schema dtype not understood" in str(e)


def test_psi4_nm_14e():

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final['qm'], dtype='psi4', units='nm')

    assert "Psi4 Schema psi4 allows only 'Bohr'/'Angstrom' coordinates, not nm" in str(e)
