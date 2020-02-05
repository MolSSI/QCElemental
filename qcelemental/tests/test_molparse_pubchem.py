import copy

import numpy as np
import pytest

import qcelemental
from qcelemental.testing import compare_molrecs, tnm

from .addons import using_web, xfail_on_pubchem_busy

_string_prov_stamp = {"creator": "QCElemental", "version": "1.0", "routine": "qcelemental.molparse.from_string"}

subject4 = """pubchem:benzene"""

ans4 = {
    # fmt: off
    'geom': [-1.213100, -0.688400, 0.000000, -1.202800, 0.706400, 0.000100,
             -0.010300, -1.394800, 0.000000, 0.010400, 1.394800, -0.000100, 1.202800,
             -0.706300, 0.000000, 1.213100, 0.688400, 0.000000, -2.157700, -1.224400,
             0.000000, -2.139300, 1.256400, 0.000100, -0.018400, -2.480900, -0.000100,
             0.018400, 2.480800, 0.000000, 2.139400, -1.256300, 0.000100, 2.157700,
             1.224500, 0.000000
            ],
    # fmt: on
    "elbl": ["C", "C", "C", "C", "C", "C", "H", "H", "H", "H", "H", "H"],
    "units": "Angstrom",
    "molecular_charge": 0.0,
    "fragment_separators": [],
    "fragment_charges": [None],
    "fragment_multiplicities": [None],
    "fragment_files": [],
    "geom_hints": [],
    "hint_types": [],
    "name": "IUPAC benzene",
}

fullans4 = {
    # fmt: off
    'geom': np.array(
        [ -1.213100, -0.688400, 0.000000, -1.202800, 0.706400, 0.000100,
          -0.010300, -1.394800, 0.000000, 0.010400, 1.394800, -0.000100, 1.202800,
          -0.706300, 0.000000, 1.213100, 0.688400, 0.000000, -2.157700, -1.224400,
          0.000000, -2.139300, 1.256400, 0.000100, -0.018400, -2.480900, -0.000100,
          0.018400, 2.480800, 0.000000, 2.139400, -1.256300, 0.000100, 2.157700,
          1.224500, 0.000000,
        ]
    ),
    # fmt: on
    "elea": np.array([12, 12, 12, 12, 12, 12, 1, 1, 1, 1, 1, 1]),
    "elez": np.array([6, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1]),
    "elem": np.array(["C", "C", "C", "C", "C", "C", "H", "H", "H", "H", "H", "H"]),
    "mass": np.array(
        [12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 1.00782503, 1.00782503, 1.00782503, 1.00782503, 1.00782503, 1.00782503]
    ),
    "real": np.array([True, True, True, True, True, True, True, True, True, True, True, True]),
    "elbl": np.array(["", "", "", "", "", "", "", "", "", "", "", ""]),
    "units": "Angstrom",
    "fix_com": False,
    "fix_orientation": False,
    "fragment_separators": [],
    "molecular_charge": 0.0,
    "molecular_multiplicity": 1,
    "fragment_charges": [0.0],
    "fragment_multiplicities": [1],
    "name": "IUPAC benzene",
}


@using_web
def test_pubchem_4a():
    subject = subject4
    fullans = copy.deepcopy(fullans4)
    fullans["provenance"] = _string_prov_stamp

    with xfail_on_pubchem_busy():
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_molrecs(ans4, intermed, tnm() + ": intermediate")
    assert compare_molrecs(fullans, final["qm"], tnm() + ": full")


@using_web
def test_pubchem_4b():
    """user units potentially contradicting pubchem units"""
    subject = subject4 + "\nunits au"

    with pytest.raises(qcelemental.MoleculeFormatError):
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject, return_processed=True)


@using_web
def test_pubchem_4c():
    subject = """
pubchem  : 241
"""
    ans = copy.deepcopy(ans4)
    ans["name"] = "benzene"
    fullans = copy.deepcopy(fullans4)
    fullans["name"] = "benzene"
    fullans["provenance"] = _string_prov_stamp

    with xfail_on_pubchem_busy():
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, name="benzene", verbose=2)
    assert compare_molrecs(ans, intermed, tnm() + ": intermediate")
    assert compare_molrecs(fullans, final["qm"], tnm() + ": full")


def test_pubchem_error_d():
    subject = """
    pubchem:-55
"""

    with pytest.raises(qcelemental.ValidationError):
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject, return_processed=True)


def test_pubchem_error_e():
    # no 3D structure available
    subject = """
pubchem : sodium benzenesulfonate

"""

    with pytest.raises(qcelemental.ValidationError):
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject)


def test_pubchem_error_f():
    subject = """
    pubchem: 100000000000000
"""

    with pytest.raises(qcelemental.ValidationError):
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject, return_processed=True)


@using_web
def test_pubchem_multiout_g():
    subject = """
    #pubchem: gobbledegook
    #pubchem: c6h12o
    #pubchem: formaldehyde*
    pubchem: tropolone*
"""

    with pytest.raises(qcelemental.ChoicesError) as e:
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject, return_processed=True)

    try:
        with xfail_on_pubchem_busy():
            qcelemental.molparse.from_string(subject, return_processed=True)
    except qcelemental.ChoicesError as e:
        assert e.choices[10789] == "2-hydroxycyclohepta-2,4,6-trien-1-one"
        assert e.choices[193687] == "2-hydroxy-3-iodo-6-propan-2-ylcyclohepta-2,4,6-trien-1-one"


subject13 = """pubchem :ammonium\n"""

ans13 = {
    "name": "IUPAC azanium",
    "molecular_charge": 1.0,
    "units": "Angstrom",
    "fragment_files": [],
    "hint_types": [],
    "geom_hints": [],
    "elbl": ["N", "H", "H", "H", "H"],
    "fragment_separators": [],
    "fragment_charges": [None],
    "fragment_multiplicities": [None],
    # fmt: off
    'geom': [
        0.0, 0.0, 0.0, 0.9645, 0.2796, 0.2138, 0.0075, -0.886, -0.5188,
        -0.5235, -0.1202, 0.8751, -0.4486, 0.7266, -0.5701,
    ],
    # fmt: on
}

fullans13 = {
    "name": "IUPAC azanium",
    "units": "Angstrom",
    # fmt: off
    'geom': np.array([
        0.0, 0.0, 0.0, 0.9645, 0.2796, 0.2138, 0.0075, -0.886, -0.5188,
        -0.5235, -0.1202, 0.8751, -0.4486, 0.7266, -0.5701,
        ]),
    # fmt: on
    "elea": np.array([14, 1, 1, 1, 1]),
    "elez": np.array([7, 1, 1, 1, 1]),
    "elem": np.array(["N", "H", "H", "H", "H"]),
    "mass": np.array([14.003074, 1.00782503, 1.00782503, 1.00782503, 1.00782503]),
    "real": np.array([True, True, True, True, True]),
    "elbl": np.array(["", "", "", "", ""]),
    "fragment_separators": [],
    "molecular_charge": 1.0,
    "fragment_charges": [1.0],
    "molecular_multiplicity": 1,
    "fragment_multiplicities": [1],
    "fix_com": False,
    "fix_orientation": False,
}


@using_web
def test_pubchem_13h():
    subject = subject13
    fullans = copy.deepcopy(fullans13)
    fullans["provenance"] = _string_prov_stamp

    with xfail_on_pubchem_busy():
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_molrecs(ans13, intermed, tnm() + ": intermediate")
    assert compare_molrecs(fullans, final["qm"], tnm() + ": full")


@using_web
def test_pubchem_13i():
    subject = "PubChem:223"
    fullans = copy.deepcopy(fullans13)
    fullans["provenance"] = _string_prov_stamp

    with xfail_on_pubchem_busy():
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_molrecs(ans13, intermed, tnm() + ": intermediate")
    assert compare_molrecs(fullans, final["qm"], tnm() + ": full")
