import copy

import numpy as np
import pytest
import qcelemental as qcel
from qcelemental.testing import compare_molrecs

_schema_prov_stamp = {'creator': 'QCElemental', 'version': '1.0', 'routine': 'qcelemental.molparse.from_schema'}


@pytest.mark.parametrize("inp,expected", [
    ({
        'frag_pattern': [[0], [1]],
        'geom': [0., 0., 0., 1., 0., 0.],
        'elbl': ['O', 'H']
    }, {
        'fragment_separators': np.array([1]),
        'geom': np.array([0., 0., 0., 1., 0., 0.]),
        'elbl': np.array(['O', 'H'])
    }),
    ({
        'frag_pattern': [[2, 0], [1]],
        'geom': np.array([[0., 0., 1.], [0., 0., 2.], [0., 0., 0.]]),
        'elem': np.array(['Li', 'H', 'He'])
    }, {
        'fragment_separators': np.array([2]),
        'geom': np.array([0., 0., 0., 0., 0., 1., 0., 0., 2.]),
        'elem': np.array(['He', 'Li', 'H'])
    }),
    ({
        'frag_pattern': [[2, 0], [1]],
        'elez': [3, 1, 2]
    }, {
        'fragment_separators': np.array([2]),
        'elez': np.array([2, 3, 1])
    }),
])
def test_contiguize_from_fragment_pattern(inp, expected):
    ans = qcel.molparse.contiguize_from_fragment_pattern(**inp)

    # compare_molrecs instead of compare_dicts handles some fragment_separators types issues
    assert compare_molrecs(expected, ans, atol=1.e-6)


@pytest.mark.parametrize("inp,expected", [
    ({
        'frag_pattern': [[2, 0], [1, 3]],
        'geom': np.array([[0., 0., 1.], [0., 0., 2.], [0., 0., 0.]]),
        'elem': np.array(['Li', 'H', 'He'])
    }, 'dropped atoms'),
    ({
        'frag_pattern': [[2, 0], [1, 4]]
    }, 'Fragmentation pattern skips atoms'),
    ({
        'frag_pattern': [[2, 0], [1, 3]],
        'elem': np.array(['U', 'Li', 'H', 'He']),
        'elbl': np.array(['Li', 'H', 'He'])
    }, 'wrong number of atoms in array'),
    ({
        'frag_pattern': [[2, 0], [1]],
        'elez': [3, 1, 2],
        'throw_reorder': True
    }, 'reorder atoms to accommodate non-contiguous fragments'),
])
def test_contiguize_from_fragment_pattern_error(inp, expected):
    with pytest.raises(qcel.ValidationError) as e:
        qcel.molparse.contiguize_from_fragment_pattern(**inp)

    assert expected in str(e)


schema14_1 = {
    "geometry": [0.0, 0.0, -5.0, 0.0, 0.0, 5.0],
    "symbols": ["He", "He"],
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

schema14_psi4_np = {
    "geom": np.array([0.0, 0.0, -5.0, 0.0, 0.0, 5.0]),
    "elem": np.array(["He", "He"]),
    'elea': np.array([4, 4]),
    'elez': np.array([2, 2]),
    'fragment_charges': [0.0, 0.0],
    'fragment_multiplicities': [3, 1],
    'mass': np.array([4.00260325413, 4.00260325413]),
    'name': 'He2',
    'fix_com': False,
    'fix_orientation': False,
    'molecular_charge': 0.0,
    "molecular_multiplicity": 3,
    'units': 'Bohr',
    'fragment_separators': [1],
    'elbl': np.array(['', '']),
    "real": np.array([True, False]),
    "provenance": _schema_prov_stamp,
}


def test_from_schema_1_14e():
    schema = {"schema_name": "qc_schema", "schema_version": 1, "molecule": copy.deepcopy(schema14_1)}

    ans = qcel.molparse.from_schema(schema)
    assert compare_molrecs(schema14_psi4_np, ans, 4)


def test_from_schema_1p5_14e():
    # this is the oddball case where passing code has internally a dtype=2 molecule
    #   but it's still passing the outer data structure
    schema = {"schema_name": "qc_schema", "schema_version": 1, "molecule": copy.deepcopy(schema14_1)}
    schema['molecule'].update({"schema_name": "qcschema_molecule", "schema_version": 2})

    ans = qcel.molparse.from_schema(schema)
    assert compare_molrecs(schema14_psi4_np, ans, 4)


def test_from_schema_2_14e():
    schema = copy.deepcopy(schema14_1)
    schema.update({"schema_name": "qcschema_molecule", "schema_version": 2})

    ans = qcel.molparse.from_schema(schema)
    assert compare_molrecs(schema14_psi4_np, ans, 4)


def test_from_schema_error_f():
    schema = {"schema_name": "private_schema", "schema_version": 1, "molecule": copy.deepcopy(schema14_1)}

    with pytest.raises(qcel.ValidationError) as e:
        qcel.molparse.from_schema(schema)

    assert 'Schema not recognized' in str(e)


def test_from_schema_1_nfr_error_14g():
    schema = {"schema_name": "qc_schema", "schema_version": 1, "molecule": copy.deepcopy(schema14_1)}
    schema['molecule'].pop('fragments')

    with pytest.raises(qcel.ValidationError) as e:
        ans = qcel.molparse.from_schema(schema)

    assert 'Dimension mismatch among fragment quantities: sep + 1 (1), chg (2), and mult(2)' in str(e)
