import numpy as np
import pytest
import qcelemental
from qcelemental.testing import compare

# (system-shorthand, tot-chg, frag-chg, tot-mult, frag-mult), (expected_final_tot-chg, frag-chg, tot-mult, frag-mult)


@pytest.mark.parametrize(
    "inp,expected",
    [
        (('He', 0, [0], 1, [1]), (0, [0], 1, [1])),  # 1
        (('He', None, [None], None, [None]), (0, [0], 1, [1])),  # 2
        (('He/He', None, [None, None], None, [None, None]), (0, [0, 0], 1, [1, 1])),  # 3
        (('He/He', 2, [None, None], None, [None, None]), (2, [2, 0], 1, [1, 1])),  # 4
        (('He/He', None, [2, None], None, [None, None]), (2, [2, 0], 1, [1, 1])),  # 5
        (('He/He', 0, [2, None], None, [None, None]), (0, [2, -2], 1, [1, 1])),  # 6
        (('Ne/He/He', -2, [None, 2, None], None, [None, None, None]), (-2, [-4, 2, 0], 1, [1, 1, 1])),  # 7
        (('Ne/He/He', 2, [None, -2, None], None, [None, None, None]), (2, [4, -2, 0], 1, [1, 1, 1])),  # 8
        (('He/He/Ne', 2, [None, -2, None], None, [None, None, None]), (2, [0, -2, 4], 1, [1, 1, 1])),  # 9
        (('He/He/Ne', 2, [2, -2, None], None, [None, None, None]), (2, [2, -2, 2], 1, [1, 1, 1])),  # 11
        (('He/He', None, [-2, 2], None, [None, None]), (0, [-2, 2], 1, [1, 1])),  # 12
        (('He/He', None, [None, -2], None, [None, None]), (-2, [0, -2], 1, [1, 1])),  # 13
        (('Ne/Ne', 0, [None, 4], None, [None, None]), (0, [-4, 4], 1, [1, 1])),  # 14
        (('He/He/He', 4, [2, None, None], None, [None, None, None]), (4, [2, 2, 0], 1, [1, 1, 1])),  # 15
        (('He/He', 0, [-2, 2], None, [None, None]), (0, [-2, 2], 1, [1, 1])),  # 16
        (('He', None, [None], None, [1]), (0, [0], 1, [1])),  # 19
        (('He', None, [None], None, [3]), (0, [0], 3, [3])),  # 21
        (('He', None, [-1], None, [2]), (-1, [-1], 2, [2])),  # 23
        (('He/He', None, [None, None], None, [1, 1]), (0, [0, 0], 1, [1, 1])),  # 25
        (('He/He', None, [None, None], None, [3, 1]), (0, [0, 0], 3, [3, 1])),  # 26
        (('He/He', None, [None, None], None, [1, 3]), (0, [0, 0], 3, [1, 3])),  # 27
        (('He/He', None, [None, None], None, [3, 3]), (0, [0, 0], 5, [3, 3])),  # 28
        (('He/He', None, [None, None], 3, [3, 3]), (0, [0, 0], 3, [3, 3])),  # 29
        (('H', None, [None], None, [None]), (0, [0], 2, [2])),  # 31
        (('H', 1, [None], None, [None]), (1, [1], 1, [1])),  # 32
        (('H', None, [-1], None, [None]), (-1, [-1], 1, [1])),  # 33
        (('funnyH', None, [None], None, [None]), (0, [0], 1, [1])),  # 34
        (('H/H', None, [None, None], None, [None, None]), (0, [0, 0], 3, [2, 2])),  # 36
        (('H/He', None, [None, None], None, [None, None]), (0, [0, 0], 2, [2, 1])),  # 37
        (('H/He', None, [1, 1], None, [None, None]), (2, [1, 1], 2, [1, 2])),  # 38
        (('H/He', -2, [-1, None], None, [None, None]), (-2, [-1, -1], 2, [1, 2])),  # 39
        (('H/He/Na/Ne', None, [1, None, 1, None], None, [None, None, None, None]),
         (2, [1, 0, 1, 0], 1, [1, 1, 1, 1])),  # 40
        (('H/He/Na/Ne', None, [-1, None, 1, None], None, [None, None, None, None]),
         (0, [-1, 0, 1, 0], 1, [1, 1, 1, 1])),  # 41
        (('H/He/Na/Ne', 2, [None, None, 1, None], None, [None, None, None, None]),
         (2, [1, 0, 1, 0], 1, [1, 1, 1, 1])),  # 42
        (('H/He/Na/Ne', 3, [None, None, 1, None], None, [None, None, None, None]),
         (3, [0, 2, 1, 0], 2, [2, 1, 1, 1])),  # 43
        (('H/He/Na/Ne', None, [None, 1, 0, 1], None, [None, None, None, None]),
         (2, [0, 1, 0, 1], 5, [2, 2, 2, 2])),  # 47
        (('H/He/Na/Ne', None, [None, 1, 0, None], None, [None, None, None, None]),
         (1, [0, 1, 0, 0], 4, [2, 2, 2, 1])),  # 48
        (('H/He/Na/Ne', None, [None, 1, 0, None], None, [None, None, 4, None]),
         (1, [0, 1, 0, 0], 6, [2, 2, 4, 1])),  # 49
        (('He/He/He', 0, [None, None, 1], None, [1, None, 2]), (0, [0, -1, 1], 3, [1, 2, 2])),  # 50
        (('N/N/N', None, [1, 1, 1], 3, [None, 3, None]), (3, [1, 1, 1], 3, [1, 3, 1])),  # 51
        (('N/N/N', None, [1, 1, 1], 3, [None, None, None]), (3, [1, 1, 1], 3, [3, 1, 1])),  # 52
        (('N/N/N', 1, [None, -1, None], 3, [None, None, 2]), (1, [2, -1, 0], 3, [2, 1, 2])),  # 54
        (('N/Ne/N', 1, [None, None, None], 4, [None, 3, None]), (1, [1, 0, 0], 4, [1, 3, 2])),  # 55
        (('N/Ne/N', None, [None, None, 1], 4, [None, 3, None]), (1, [0, 0, 1], 4, [2, 3, 1])),  # 56
        (('He/He', None, [-1, 1], None, [None, None]), (0, [-1, 1], 3, [2, 2])),  # 57
        (('He/Gh', None, [2, None], None, [None, None], {'verbose': 2}), (2, [2, 0], 1, [1, 1])),  # 61
        (('Gh/He/Ne', 2, [None, -2, None], None, [None, None, None]), (2, [0, -2, 4], 1, [1, 1, 1])),  # 63
        (('Gh/He/Gh', 1, [None, None, None], None, [None, None, None]), (1, [0, 1, 0], 2, [1, 2, 1])),  # 64
        (('Ne/Ne', 2, [-2, None], None, [None, None]), (2, [-2, 4], 1, [1, 1])),  # 65a
        (('Gh/Ne', 2, [-2, None], None, [None, None], {'zero_ghost_fragments': True}), (0, [0, 0], 1, [1, 1])),  # 65c
    ]) # yapf: disable
def test_validate_and_fill_chgmult(inp, expected):
    system = _systemtranslator[inp[0]]
    kwargs = inp[5] if len(inp) > 5 else {}

    ans = qcelemental.molparse.validate_and_fill_chgmult(system[0], system[1], inp[1], inp[2], inp[3], inp[4],
                                                         **kwargs)
    assert compare(1, ans == dict(zip(_keys, expected)), """{}: {}, {}, {}, {} --> {}""".format(*inp, expected))


@pytest.mark.parametrize(
    "inp",
    [
        ('He/He/Ne', 2, [None, -2, 0], None, [None, None, None]),  # 10
        ('He/He', 0, [-2, -2], None, [None, None]),  # 17
        ('He', None, [None], 0, [None]),  # 18
        ('He', None, [None], None, [2]),  # 20
        ('He', None, [None], None, [5]),  # 22
        ('He', None, [-2], None, [2]),  # 24
        ('He/He', None, [None, None], 2, [3, 3]),  # 30
        ('funnierH', None, [None], None, [None]),  # 35
        ('H/He', None, [1, None], None, [2, None]),  # 44
        ('H/He', None, [None, 0], None, [None, 2]),  # 45
        ('H/He', None, [None, -1], None, [None, 3]),  # 46
        ('N/N/N', None, [None, None, None], 3, [None, None, 2]),  # 53
        ('Gh', 1, [None], None, [None]),  # 58
        ('Gh', -1, [None], None, [None]),  # 59
        ('Gh', None, [None], 3, [None]),  # 60
        ('Gh/He', None, [2, None], None, [None, None]),  # 62
        ('Gh/Ne', 2, [-2, None], None, [None, None]),  # 65b
    ]) # yapf: disable
def test_validate_and_fill_chgmult_irreconcilable(inp):
    system = _systemtranslator[inp[0]]

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

_keys = ['molecular_charge', 'fragment_charges', 'molecular_multiplicity', 'fragment_multiplicities']
_systemtranslator = {
    'He': (np.array([2]), np.array([])),
    'He/He': (np.array([2, 2]), np.array([1])),
    'Ne/He/He': (np.array([10, 2, 2]), np.array([1, 2])),
    'He/He/Ne': (np.array([2, 2, 10]), np.array([1, 2])),
    'Ne/Ne': (np.array([10, 10]), np.array([1])),
    'He/He/He': (np.array([2, 2, 2]), np.array([1, 2])),
    'H': (np.array([1]), np.array([])),
    'funnyH': (np.array([0]), np.array([])),  # has no electrons
    'funnierH': (np.array([-1]), np.array([])),  # has positron
    'H/H': (np.array([1, 1]), np.array([1])),
    'H/He': (np.array([1, 2]), np.array([1])),
    'H/He/Na/Ne': (np.array([1, 2, 11, 10]), np.array([1, 2, 3])),
    'N/N/N': (np.array([7, 7, 7]), np.array([1, 2])),
    'N/Ne/N': (np.array([7, 10, 7]), np.array([1, 2])),
    'He/Gh': (np.array([2, 0]), np.array([1])),
    'Gh/He': (np.array([0, 2]), np.array([1])),
    'Gh': (np.array([0, 0]), np.array([])),
    'Gh/He/Ne': (np.array([0, 0, 2, 10]), np.array([2, 3])),
    'Gh/He/Gh': (np.array([0, 2, 0]), np.array([1, 2])),
    'Gh/Ne': (np.array([0, 10]), np.array([1])),
}
