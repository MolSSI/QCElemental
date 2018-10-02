from decimal import Decimal

import pytest
import os

import qcelemental


# 2014 CODATA values
@pytest.mark.parametrize("from_unit, to_unit, expected", [

    # First satisfy the 7 canonical conversions
    ("hartree", "Hz", "6.579683920711e15"),
    ("hartree", "amu", "2.9212623197e-8"),
    ("hartree", "kilogram", "4.850870129e-35"),
    ("hartree", "J/mol", "2625499.638"),
    ("hartree", "eV", "27.21138602"),
    ("hartree", "wavenumber", "2.194746313702e5"),
    ("hartree", "kelvin", "3.1577513e5"),

    ("hartree", "kcal/mol", "627.509474"),
    ("hartree", "kJ/mol", "2625.499638"),
    ("bohr", "angstrom", "0.52917721067"),
    ("bohr", "nanometer", "5.2917721067e-2"),
    ("bohr", "cm", "5.2917721067e-9"),
    ("amu", "kg", "1.660539040e-27"),
    ("amu", "g", "1.660539040e-24"),
])
def test_unit_conversion(from_unit, to_unit, expected):

    # Build values and quantize to the tolerance
    expected = Decimal(expected)
    from_to_value = Decimal(qcelemental.units.conversion_factor(from_unit, to_unit)).quantize(expected)
    assert from_to_value == expected

    # Build inverse
    inv_expected = 1 / Decimal(expected)
    to_from_value = Decimal(qcelemental.units.conversion_factor(to_unit, from_unit))

    # Expected to a relative tolerance as the number of digits plus two for rounding
    # Using float comparisons as we are taking an (1 / float) inverse in the conversion code
    rel_tol = float("10e-{}".format(len(expected.as_tuple().digits) + 2))
    assert pytest.approx(float(inv_expected), rel_tol) == float(to_from_value)


