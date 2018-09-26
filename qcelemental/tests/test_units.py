from decimal import Decimal

import pytest
import os

import qcelemental


@pytest.mark.parametrize("inp,expected,tol", [
    ("kcal/mol", 627.509474, 1.e-6),
    ("J/mol", 2625.499638*1000, 1.e-6),
    ("kJ/mol", 2625.499638, 1.e-6),
    ("eV", 27.21138602, 1e-6),
])
def test_hartree_conversion(inp, expected, tol):
    assert qcelemental.units.conversion_factor("hartree", inp) == pytest.approx(expected, tol)
    assert qcelemental.units.conversion_factor(inp, "hartree") == pytest.approx(1.0 / expected, tol)
