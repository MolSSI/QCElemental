import copy
from typing import Dict

import numpy as np
import pytest

import qcelemental
from qcelemental.testing import compare_molrecs

_string_prov_stamp = {"creator": "QCElemental", "version": "1.0", "routine": "qcelemental.molparse.from_string"}
_schema_prov_stamp = {"creator": "QCElemental", "version": "1.0", "routine": "qcelemental.molparse.from_schema"}

subject14 = """0 3\n--\nHe 0 0 -5\n--\n@He 0 0 5\nunits au"""

schema14_1 = {
    "schema_name": "qc_schema_input",
    "schema_version": 1,
    "molecule": {
        "validated": True,
        "geometry": [0.0, 0.0, -5.0, 0.0, 0.0, 5.0],
        "symbols": ["He", "He"],
        "atomic_numbers": [2, 2],
        "mass_numbers": [4, 4],
        "atom_labels": ["", ""],
        "fragments": [[0], [1]],
        "fragment_charges": [0.0, 0.0],
        "fragment_multiplicities": [3, 1],
        "masses": [4.00260325413, 4.00260325413],
        "name": "He2",
        "fix_com": False,
        "fix_orientation": False,
        "molecular_charge": 0.0,
        "molecular_multiplicity": 3,
        "real": [True, False],
    },
}

schema14_2 = {"schema_name": "qcschema_molecule", "schema_version": 2}
schema14_2.update(schema14_1["molecule"])

schema14_psi4 = {
    "geom": [0.0, 0.0, -5.0, 0.0, 0.0, 5.0],
    "elem": ["He", "He"],
    "elea": [4, 4],
    "elez": [2, 2],
    "fragment_charges": [0.0, 0.0],
    "fragment_multiplicities": [3, 1],
    "mass": [4.00260325413, 4.00260325413],
    "name": "He2",
    "fix_com": False,
    "fix_orientation": False,
    "molecular_charge": 0.0,
    "molecular_multiplicity": 3,
    "units": "Bohr",
    "fragment_separators": [1],
    "elbl": ["", ""],
    "real": [True, False],
}


def test_1_14a():
    fullans = copy.deepcopy(schema14_1)
    fullans["molecule"]["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject14)
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype=1)
    assert compare_molrecs(fullans["molecule"], kmol["molecule"])

    fullans = copy.deepcopy(schema14_psi4)
    fullans["provenance"] = _schema_prov_stamp

    molrec = qcelemental.molparse.from_schema(kmol)
    molrec = qcelemental.util.unnp(molrec)
    assert compare_molrecs(fullans, molrec)


def test_2_14b():
    fullans = copy.deepcopy(schema14_2)
    fullans["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject14)
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype=2)
    assert compare_molrecs(fullans, kmol)

    fullans = copy.deepcopy(schema14_psi4)
    fullans["provenance"] = _schema_prov_stamp

    molrec = qcelemental.molparse.from_schema(kmol)
    molrec = qcelemental.util.unnp(molrec)
    assert compare_molrecs(fullans, molrec)


def test_psi4_14c():
    fullans = copy.deepcopy(schema14_psi4)
    fullans["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject14)
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype="psi4")
    assert compare_molrecs(fullans, kmol)


def test_dtype_error():

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final["qm"], dtype="xkcd927")

    assert "Schema dtype not understood" in str(e.value)


@pytest.mark.parametrize("dtype", [1, 2])
def test_qcschema_ang_error(dtype):

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final["qm"], dtype=dtype, units="Angstrom")

    assert f"QCSchema {dtype} allows only 'Bohr' coordinates" in str(e.value)


def test_psi4_nm_error():

    final = qcelemental.molparse.from_string(subject14)
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.to_schema(final["qm"], dtype="psi4", units="nm")

    assert "Psi4 Schema psi4 allows only 'Bohr'/'Angstrom' coordinates, not nm" in str(e.value)


twobohrinang = 2.0 * qcelemental.constants.conversion_factor("bohr", "angstrom")
subject15 = """symmetry cS\nH 0 0 {twobohrinang}\nO 0 0 0\n2H_deut {twobohrinang} 0 0\nno_com\nno_reorient""".format(
    twobohrinang=twobohrinang
)

schema15_1: Dict = {
    "schema_name": "qc_schema_input",
    "schema_version": 1,
    "molecule": {
        "validated": True,
        "geometry": [0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0],
        "symbols": ["H", "O", "H"],
        "atomic_numbers": [1, 8, 1],
        "mass_numbers": [1, 16, 2],
        "atom_labels": ["", "", "_deut"],
        "fragments": [[0, 1, 2]],
        "fragment_charges": [0.0],
        "fragment_multiplicities": [1],
        "masses": [1.00782503223, 15.99491461957, 2.01410177812],
        "name": "H2O",
        "comment": "I has a comment",
        "fix_com": True,
        "fix_orientation": True,
        "fix_symmetry": "cs",
        "molecular_charge": 0.0,
        "molecular_multiplicity": 1,
        "real": [True, True, True],
    },
}

schema15_2 = {"schema_name": "qcschema_molecule", "schema_version": 2}
schema15_2.update(schema15_1["molecule"])

schema15_psi4 = {
    "geom": [0.0, 0.0, twobohrinang, 0.0, 0.0, 0.0, twobohrinang, 0.0, 0.0],
    "elem": ["H", "O", "H"],
    "elez": [1, 8, 1],
    "elea": [1, 16, 2],
    "elbl": ["", "", "_deut"],
    "fragment_charges": [0.0],
    "fragment_multiplicities": [1],
    "mass": [1.00782503223, 15.99491461957, 2.01410177812],
    "name": "H2O",
    "comment": "I has a comment",
    "fix_com": True,
    "fix_orientation": True,
    "fix_symmetry": "cs",
    "molecular_charge": 0.0,
    "molecular_multiplicity": 1,
    "units": "Angstrom",
    "fragment_separators": [],
    "real": [True, True, True],
}


def test_1_15a():
    fullans = copy.deepcopy(schema15_1)
    fullans["molecule"]["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject15)
    final["qm"]["comment"] = "I has a comment"
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype=1)
    assert compare_molrecs(fullans["molecule"], kmol["molecule"])

    fullans = copy.deepcopy(schema15_psi4)
    fullans["units"] = "Bohr"
    fullans["geom"] = [0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0]
    fullans["provenance"] = _schema_prov_stamp

    molrec = qcelemental.molparse.from_schema(kmol)
    molrec = qcelemental.util.unnp(molrec)
    assert compare_molrecs(fullans, molrec)


def test_2_15b():
    fullans = copy.deepcopy(schema15_2)
    fullans["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject15)
    final["qm"]["comment"] = "I has a comment"
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype=2)
    assert compare_molrecs(fullans, kmol)

    fullans = copy.deepcopy(schema15_psi4)
    fullans["units"] = "Bohr"
    fullans["geom"] = [0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0]
    fullans["provenance"] = _schema_prov_stamp

    molrec = qcelemental.molparse.from_schema(kmol)
    molrec = qcelemental.util.unnp(molrec)
    assert compare_molrecs(fullans, molrec)


def test_psi4_15c():
    fullans = copy.deepcopy(schema15_psi4)
    fullans["provenance"] = _string_prov_stamp

    final = qcelemental.molparse.from_string(subject15)
    final["qm"]["comment"] = "I has a comment"
    kmol = qcelemental.molparse.to_schema(final["qm"], dtype="psi4", units="Angstrom")
    assert compare_molrecs(fullans, kmol)


schema16_1 = {
    "schema_name": "qc_schema_input",
    "schema_version": 1,
    "molecule": {
        "validated": True,
        "geometry": [2.0, 2.0, 3.0],
        "symbols": ["C"],
        "masses": [12.0],
        "atom_labels": [""],
        "atomic_numbers": [6],
        "mass_numbers": [12],
        "real": [True],
        "name": "C",
        "molecular_charge": 0.0,
        "molecular_multiplicity": 1,
        "fragments": [[0]],
        "fragment_charges": [0.0],
        "fragment_multiplicities": [1],
        "fix_com": False,
        "fix_orientation": False,
        "provenance": {"creator": "Mystery Program", "version": "2018.3", "routine": "molecule builder"},
        "connectivity": [(0, 0, 0.0)],
    },
}

schema16_2 = {"schema_name": "qcschema_molecule", "schema_version": 2}
schema16_2.update(schema16_1["molecule"])

schema16_psi4 = {
    "units": "Bohr",
    "geom": np.array([2.0, 2.0, 3.0]),
    "elem": np.array(["C"]),
    "mass": np.array([12.0]),
    "elbl": np.array([""]),
    "elez": np.array([6]),
    "elea": np.array([12]),
    "real": np.array([True]),
    "name": "C",
    "molecular_charge": 0.0,
    "molecular_multiplicity": 1,
    "fragment_separators": [],
    "fragment_charges": [0.0],
    "fragment_multiplicities": [1],
    "fix_com": False,
    "fix_orientation": False,
    "provenance": {"creator": "Mystery Program", "version": "2018.3", "routine": "molecule builder"},
    "connectivity": [(0, 0, 0.0)],
}


def test_froto_1_16a():
    basic = {
        "schema_name": "qc_schema_output",
        "schema_version": 1,
        "molecule": {
            "geometry": [2, 2, 3],
            "symbols": ["C"],
            "connectivity": [(0.0, -0.0, 0)],
            "provenance": {"creator": "Mystery Program", "version": "2018.3", "routine": "molecule builder"},
        },
    }

    fullans = copy.deepcopy(schema16_1)
    fullans["molecule"]["provenance"] = _schema_prov_stamp

    roundtrip = qcelemental.molparse.to_schema(qcelemental.molparse.from_schema(basic), dtype=1)
    assert compare_molrecs(fullans["molecule"], roundtrip["molecule"])


def test_froto_2_16a():
    basic = {
        "schema_name": "qcschema_molecule",
        "schema_version": 2,
        "geometry": [2, 2, 3],
        "symbols": ["C"],
        "connectivity": [(0.0, -0.0, 0)],
        "provenance": {"creator": "Mystery Program", "version": "2018.3", "routine": "molecule builder"},
    }

    fullans = copy.deepcopy(schema16_2)
    fullans["provenance"] = _schema_prov_stamp

    roundtrip = qcelemental.molparse.to_schema(qcelemental.molparse.from_schema(basic), dtype=2)
    assert compare_molrecs(fullans, roundtrip)


@pytest.mark.parametrize("dtype", [1, 2])
def test_tofro_16b(dtype):

    fullans = copy.deepcopy(schema16_psi4)
    fullans["provenance"] = _schema_prov_stamp

    roundtrip = qcelemental.molparse.from_schema(qcelemental.molparse.to_schema(schema16_psi4, dtype=dtype))
    assert compare_molrecs(fullans, roundtrip)
