import os
from decimal import Decimal

import pytest
import qcelemental


@pytest.mark.parametrize("inp,expected", [
    ("He", "He"),
    ("He", "He"),
    ("He4", "He"),
    ("he", "He"),
    ("2", "He"),
    (2, "He"),
    (2.0, "He"),
])
def test_id_resolution(inp, expected):
    assert qcelemental.periodictable._resolve_atom_to_key('He') == 'He'


@pytest.mark.parametrize("inp", ["He100", '-1', -1, -1.0, 'cat', 200])
def test_id_resolution_error(inp):
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key(inp)


# TODO test ghost


def test_to_mass_krypton_decimal():
    assert qcelemental.periodictable.to_mass('kr', return_decimal=True) == Decimal('83.9114977282')


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("KRYPTON", 83.9114977282),
        ("kr", 83.9114977282),
        ("kr84", 83.9114977282),
        (36, 83.9114977282),

        # Kr 86
        ("kr86", 85.9106106269),

        # Helium
        ("D", 2.01410177812),
        ("h2", 2.01410177812),
    ])
def test_to_mass(inp, expected):
    assert qcelemental.periodictable.to_mass(inp) == pytest.approx(expected, 1.e-9)


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("kr", 84),
        ("KRYPTON", 84),
        ("kr84", 84),
        (36, 84),

        # Kr 86
        ("kr86", 86),

        # Helium
        ("D", 2),
        ("h2", 2),
    ])
def test_to_mass_number(inp, expected):
    assert qcelemental.periodictable.to_A(inp) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("kr", 36),
        ("KRYPTON", 36),
        ("kr84", 36),
        (36, 36),

        # Kr 86
        ("kr86", 36),

        # Deuterium
        ("D", 1),
        ("h2", 1),
    ])
def test_to_atomic_number(inp, expected):
    assert qcelemental.periodictable.to_Z(inp) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("kr", "Kr"),
        ("KRYPTON", "Kr"),
        ("kr84", "Kr"),
        (36, "Kr"),

        # Kr 86
        ("kr86", "Kr"),

        # Deuterium
        ("D", "H"),
        ("h2", "H"),
    ])
def test_to_symbol(inp, expected):
    assert qcelemental.periodictable.to_E(inp) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("kr", "Krypton"),
        ("KRYPTON", "Krypton"),
        ("kr84", "Krypton"),
        (36, "Krypton"),

        # Kr 86
        ("kr86", "Krypton"),

        # Deuterium
        ("D", "Hydrogen"),
        ("h2", "Hydrogen"),
    ])
def test_to_element(inp, expected):
    assert qcelemental.periodictable.to_element(inp) == expected


@pytest.mark.parametrize("inp,expected", [('HE', 1), ('carbon', 2), ('cl35', 3), (36, 4), (37.0, 5), ('mercury', 6),
                                          ('Ts', 7)])
def test_to_period(inp, expected):
    assert qcelemental.periodictable.to_period(inp) == expected


@pytest.mark.parametrize("inp,expected", [
    ('D', 1),
    ('Ba', 2),
    ('yttrium', 3),
    ('hf179', 4),
    (23, 5),
    ('w', 6),
    (43.0, 7),
    (26.0, 8),
    ('meitnerium', 9),
    ('pt', 10),
    ('gold', 11),
    ('cd', 12),
    (5.0, 13),
    (14, 14),
    ('phosphorus', 15),
    ('SE', 16),
    ('i', 17),
    (54, 18),
    ('La', None),
    (89.0, None),
    ('lutetium', None),
    (103.0, None),
    ('u238', None),
])
def test_to_group(inp, expected):
    assert qcelemental.periodictable.to_group(inp) == expected


def test_c_header():
    qcelemental.periodictable.write_c_header("header.h")
    os.remove("header.h")


@pytest.mark.xfail(True, reason='comparison data not available for installed repository', run=True, strict=False)
def test_periodic_table_comparison():
    qcelemental.periodictable.run_comparison()
