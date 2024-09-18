import numpy as np
import pytest

import qcelemental
from qcelemental.testing import compare

# (system-shorthand, tot-chg, frag-chg, tot-mult, frag-mult), (expected_final_tot-chg, frag-chg, tot-mult, frag-mult)


working_chgmults = [
    (("He", 0, [0], 1, [1]), (0, [0], 1, [1]), "b3855c64"),  # 1
    (("He", None, [None], None, [None]), (0, [0], 1, [1]), "b3855c64"),  # 2
    (("He/He", None, [None, None], None, [None, None]), (0, [0, 0], 1, [1, 1]), "ad36285a"),  # 3
    (("He/He", 2, [None, None], None, [None, None]), (2, [2, 0], 1, [1, 1]), "bfdcbd63"),  # 4
    (("He/He", None, [2, None], None, [None, None]), (2, [2, 0], 1, [1, 1]), "bfdcbd63"),  # 5
    (("He/He", 0, [2, None], None, [None, None]), (0, [2, -2], 1, [1, 1]), "e7141038"),  # 6
    (("Ne/He/He", -2, [None, 2, None], None, [None, None, None]), (-2, [-4, 2, 0], 1, [1, 1, 1]), "35a61864"),  # 7
    (("Ne/He/He", 2, [None, -2, None], None, [None, None, None]), (2, [4, -2, 0], 1, [1, 1, 1]), "cd3a0ecd"),  # 8
    (("He/He/Ne", 2, [None, -2, None], None, [None, None, None]), (2, [0, -2, 4], 1, [1, 1, 1]), "e3ca63c8"),  # 9
    (("He/He/Ne", 2, [2, -2, None], None, [None, None, None]), (2, [2, -2, 2], 1, [1, 1, 1]), "8d70c7ec"),  # 11
    (("He/He", None, [-2, 2], None, [None, None]), (0, [-2, 2], 1, [1, 1]), "cf3e8c41"),  # 12
    (("He/He", None, [None, -2], None, [None, None]), (-2, [0, -2], 1, [1, 1]), "9cd54b37"),  # 13
    (("Ne/Ne", 0, [None, 4], None, [None, None]), (0, [-4, 4], 1, [1, 1]), "752ec2fe"),  # 14
    (("He/He/He", 4, [2, None, None], None, [None, None, None]), (4, [2, 2, 0], 1, [1, 1, 1]), "cc52833f"),  # 15
    (("He/He", 0, [-2, 2], None, [None, None]), (0, [-2, 2], 1, [1, 1]), "cf3e8c41"),  # 16
    (("He", None, [None], None, [1]), (0, [0], 1, [1]), "b3855c64"),  # 19
    (("He", None, [None], None, [3]), (0, [0], 3, [3]), "7caca87a"),  # 21
    (("He", None, [-1], None, [2]), (-1, [-1], 2, [2]), "e5f7b504"),  # 23
    (("He/He", None, [None, None], None, [1, 1]), (0, [0, 0], 1, [1, 1]), "ad36285a"),  # 25
    (("He/He", None, [None, None], None, [3, 1]), (0, [0, 0], 3, [3, 1]), "3fa264e9"),  # 26
    (("He/He", None, [None, None], None, [1, 3]), (0, [0, 0], 3, [1, 3]), "516f623a"),  # 27
    (("He/He", None, [None, None], None, [3, 3]), (0, [0, 0], 5, [3, 3]), "0f1a1ffc"),  # 28
    (("He/He", None, [None, None], 3, [3, 3]), (0, [0, 0], 3, [3, 3]), "9eb13213"),  # 29
    (("H", None, [None], None, [None]), (0, [0], 2, [2]), "512c204f"),  # 31
    (("H", 1, [None], None, [None]), (1, [1], 1, [1]), "74aba942"),  # 32
    (("H", None, [-1], None, [None]), (-1, [-1], 1, [1]), "809afce3"),  # 33
    (("funnyH", None, [None], None, [None]), (0, [0], 1, [1]), "f91e3c77"),  # 34
    (("H/H", None, [None, None], None, [None, None]), (0, [0, 0], 3, [2, 2]), "dc9720af"),  # 36
    (("H/He", None, [None, None], None, [None, None]), (0, [0, 0], 2, [2, 1]), "9445d8b9"),  # 37
    (("H/He", None, [1, 1], None, [None, None]), (2, [1, 1], 2, [1, 2]), "dfcb8940"),  # 38
    (("H/He", -2, [-1, None], None, [None, None]), (-2, [-1, -1], 2, [1, 2]), "e9b8fe09"),  # 39
    (
        ("H/He/Na/Ne", None, [1, None, 1, None], None, [None, None, None, None]),
        (2, [1, 0, 1, 0], 1, [1, 1, 1, 1]),
        "59c6613a",
    ),  # 40
    (
        ("H/He/Na/Ne", None, [-1, None, 1, None], None, [None, None, None, None]),
        (0, [-1, 0, 1, 0], 1, [1, 1, 1, 1]),
        "ccd5e698",
    ),  # 41
    (
        ("H/He/Na/Ne", 2, [None, None, 1, None], None, [None, None, None, None]),
        (2, [1, 0, 1, 0], 1, [1, 1, 1, 1]),
        "59c6613a",
    ),  # 42
    (
        ("H/He/Na/Ne", 3, [None, None, 1, None], None, [None, None, None, None]),
        (3, [0, 2, 1, 0], 2, [2, 1, 1, 1]),
        "ac9200ac",
    ),  # 43
    (
        ("H/He/Na/Ne", None, [None, 1, 0, 1], None, [None, None, None, None]),
        (2, [0, 1, 0, 1], 5, [2, 2, 2, 2]),
        "3a2ba1ea",
    ),  # 47
    (
        ("H/He/Na/Ne", None, [None, 1, 0, None], None, [None, None, None, None]),
        (1, [0, 1, 0, 0], 4, [2, 2, 2, 1]),
        "f4a99eac",
    ),  # 48
    (
        ("H/He/Na/Ne", None, [None, 1, 0, None], None, [None, None, 4, None]),
        (1, [0, 1, 0, 0], 6, [2, 2, 4, 1]),
        "cb147b67",
    ),  # 49
    (("He/He/He", 0, [None, None, 1], None, [1, None, 2]), (0, [0, -1, 1], 3, [1, 2, 2]), "7140d169"),  # 50
    (("N/N/N", None, [1, 1, 1], 3, [None, 3, None]), (3, [1, 1, 1], 3, [1, 3, 1]), "b381f350"),  # 51
    (("N/N/N", None, [1, 1, 1], 3, [None, None, None]), (3, [1, 1, 1], 3, [3, 1, 1]), "2d17a8fd"),  # 52
    (("N/N/N", 1, [None, -1, None], 3, [None, None, 2]), (1, [2, -1, 0], 3, [2, 1, 2]), "b3e87763"),  # 54
    (("N/Ne/N", 1, [None, None, None], 4, [None, 3, None]), (1, [1, 0, 0], 4, [1, 3, 2]), "38a20a23"),  # 55
    (("N/Ne/N", 1, [None, None, None], 4.0, [None, 3.0, None]), (1, [1, 0, 0], 4, [1, 3, 2]), "38a20a23"),  # 55b
    (("N/Ne/N", None, [None, None, 1], 4, [None, 3, None]), (1, [0, 0, 1], 4, [2, 3, 1]), "28064e3e"),  # 56
    (("He/He", None, [-1, 1], None, [None, None]), (0, [-1, 1], 3, [2, 2]), "83330b29"),  # 57
    (("He/Gh", None, [2, None], None, [None, None], {"verbose": 2}), (2, [2, 0], 1, [1, 1]), "dfc621eb"),  # 61
    (("Gh/He/Ne", 2, [None, -2, None], None, [None, None, None]), (2, [0, -2, 4], 1, [1, 1, 1]), "c828e6fd"),  # 63
    (("Gh/He/Gh", 1, [None, None, None], None, [None, None, None]), (1, [0, 1, 0], 2, [1, 2, 1]), "54238534"),  # 64
    (("Ne/Ne", 2, [-2, None], None, [None, None]), (2, [-2, 4], 1, [1, 1]), "ffe022cd"),  # 65a
    (("Gh/Ne", 2, [-2, None], None, [None, None], {"zero_ghost_fragments": True}), (0, [0, 0], 1, [1, 1]), ""),  # 65c
    (("Ne/Ne", None, [-2.1, 2.1], None, [None, None]), (0, [-2.1, 2.1], 1, [1, 1]), "684cec20"),  # 112
    (("N/N/N", 3.3, [1, None, 1], 3, [None, 3, None]), (3.3, [1, 3.3 - 2, 1], 3, [1, 3, 1]), "7a5fd2d3"),  # 151
    (
        ("N/N/N", -2.4, [None, None, None], None, [None, None, None], {"verbose": 2}),
        (-2.4, [-2.4, 0, 0], 3, [1, 2, 2]),
        "a83a3356",
    ),  # 166
    (("He", None, [None], 2.8, [None]), (0, [0], 2.8, [2.8]), "3e10e7b5"),  # 180
    (("He", None, [None], None, [2.8]), (0, [0], 2.8, [2.8]), "3e10e7b5"),  # 181
    (("N/N/N", None, [None, None, None], 2.2, [2, 2, 2.2]), (0, [0, 0, 0], 2.2, [2, 2, 2.2]), "798ee5d4"),  # 183
    (("N/N/N", None, [None, None, None], 4.2, [2, 2, 2.2]), (0, [0, 0, 0], 4.2, [2, 2, 2.2]), "ed6d1f35"),  # 185
    (("N/N/N", None, [None, None, None], None, [2, 2, 2.2]), (0, [0, 0, 0], 4.2, [2, 2, 2.2]), "ed6d1f35"),  # 186
    (("N/N/N", None, [2, -2, None], 2.2, [2, 2, 2.2]), (0, [2, -2, 0], 2.2, [2, 2, 2.2]), "66e655c0"),  # 187
]


@pytest.mark.parametrize("inp,expected,exp_hash", working_chgmults)
def test_validate_and_fill_chgmult(systemtranslator, inp, expected, exp_hash):
    system = systemtranslator[inp[0]]
    kwargs = inp[5] if len(inp) > 5 else {}
    _keys = ["molecular_charge", "fragment_charges", "molecular_multiplicity", "fragment_multiplicities"]

    ans = qcelemental.molparse.validate_and_fill_chgmult(system[0], system[1], inp[1], inp[2], inp[3], inp[4], **kwargs)
    assert compare(1, ans == dict(zip(_keys, expected)), """{}: {}, {}, {}, {} --> {}""".format(*inp, expected))


@pytest.mark.parametrize("inp,expected,exp_hash", working_chgmults)
def test_validate_and_fill_chgmult_mol_model(systemtranslator, inp, expected, exp_hash):
    symbols, sep = systemtranslator[inp[0]]
    kwargs = inp[5] if len(inp) > 5 else {}
    if "zero_ghost_fragments" in kwargs:
        pytest.skip()

    def none_y(inp):
        return (inp is None) or (isinstance(inp, list) and (all(x is None for x in inp)))

    _keys = ["molecular_charge", "fragment_charges", "molecular_multiplicity", "fragment_multiplicities"]
    input_chgmults = {k: v for k, v in zip(_keys, inp[1:]) if not none_y(v)}
    nat = len(symbols)
    geometry = [[iat * 2.0, 0.0, 0.0] for iat in range(nat)]
    fidx = np.split(np.arange(nat), sep)
    fragments = [fr.tolist() for fr in fidx]

    mol = qcelemental.models.Molecule(symbols=symbols, geometry=geometry, fragments=fragments, **input_chgmults)

    assert mol.molecular_charge == expected[0]
    assert mol.fragment_charges == expected[1]
    assert mol.molecular_multiplicity == expected[2]
    assert mol.fragment_multiplicities == expected[3]
    assert mol.get_hash()[:8] == exp_hash


@pytest.mark.parametrize(
    "inp",
    [
        ("He/He/Ne", 2, [None, -2, 0], None, [None, None, None]),  # 10
        ("He/He", 0, [-2, -2], None, [None, None]),  # 17
        ("He", None, [None], 0, [None]),  # 18
        ("He", None, [None], None, [2]),  # 20
        ("He", None, [None], None, [5]),  # 22
        ("He", None, [-2], None, [2]),  # 24
        ("He/He", None, [None, None], 2, [3, 3]),  # 30
        ("funnierH", None, [None], None, [None]),  # 35
        ("H/He", None, [1, None], None, [2, None]),  # 44
        ("H/He", None, [None, 0], None, [None, 2]),  # 45
        ("H/He", None, [None, -1], None, [None, 3]),  # 46
        ("N/N/N", None, [None, None, None], 3, [None, None, 2]),  # 53
        ("Gh", 1, [None], None, [None]),  # 58
        ("Gh", -1, [None], None, [None]),  # 59
        ("Gh", None, [None], 3, [None]),  # 60
        ("Gh/He", None, [2, None], None, [None, None]),  # 62
        ("Gh/Ne", 2, [-2, None], None, [None, None]),  # 65b
        ("He", None, [None], 3.2, [None]),  # 182
        ("N/N/N", None, [None, None, None], 2.2, [None, None, 2.2]),  # 184
    ],
)
def test_validate_and_fill_chgmult_irreconcilable(systemtranslator, inp):
    system = systemtranslator[inp[0]]

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.validate_and_fill_chgmult(system[0], system[1], inp[1], inp[2], inp[3], inp[4], verbose=0)


# Notes
#  9 - residual +4 distributes to first fragment able to wholly accept it (He+4 is no-go)
# 10 - residual +4 unsuited for only open fragment, He, so irreconcilable
# 11 - non-positive multiplicity
# 20 - doublet non consistent with closed-shell, neutral default charge
# 22 - insufficient electrons for pentuplet
# 24 - doublet not consistent with even charge
# 30 - bad parity btwn mult and total # electrons
# 35 - insufficient electrons
# 55 - both (1, (1, 0.0, 0.0), 4, (1, 3, 2)) and (1, (0.0, 0.0, 1), 4, (2, 3, 1)) plausible
# 65 - non-0/1 on Gh fragment errors normally but reset by zero_ghost_fragments
# 182 - insufficient electrons on He
# 184 - decline to guess fragment multiplicities when floats involved


@pytest.fixture
def systemtranslator():
    return {
        "He": (np.array([2]), np.array([])),
        "He/He": (np.array([2, 2]), np.array([1])),
        "Ne/He/He": (np.array([10, 2, 2]), np.array([1, 2])),
        "He/He/Ne": (np.array([2, 2, 10]), np.array([1, 2])),
        "Ne/Ne": (np.array([10, 10]), np.array([1])),
        "He/He/He": (np.array([2, 2, 2]), np.array([1, 2])),
        "H": (np.array([1]), np.array([])),
        "funnyH": (np.array([0]), np.array([])),  # has no electrons
        "funnierH": (np.array([-1]), np.array([])),  # has positron
        "H/H": (np.array([1, 1]), np.array([1])),
        "H/He": (np.array([1, 2]), np.array([1])),
        "H/He/Na/Ne": (np.array([1, 2, 11, 10]), np.array([1, 2, 3])),
        "N/N/N": (np.array([7, 7, 7]), np.array([1, 2])),
        "N/Ne/N": (np.array([7, 10, 7]), np.array([1, 2])),
        "He/Gh": (np.array([2, 0]), np.array([1])),
        "Gh/He": (np.array([0, 2]), np.array([1])),
        "Gh": (np.array([0, 0]), np.array([])),
        "Gh/He/Ne": (np.array([0, 0, 2, 10]), np.array([2, 3])),
        "Gh/He/Gh": (np.array([0, 2, 0]), np.array([1, 2])),
        "Gh/Ne": (np.array([0, 10]), np.array([1])),
    }
