import os
from decimal import Decimal

import pytest

import qcelemental


@pytest.mark.parametrize("inp", ["He100", "-1", -1, -1.0, "cat", 200, "Cr_highspin"])
def test_id_resolution_error_bad_element(inp):
    with pytest.raises(qcelemental.NotAnElementError):
        qcelemental.covalentradii.get(inp)


@pytest.mark.parametrize("inp", ["X", "Bk", 100])
def test_id_resolution_error(inp):
    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.covalentradii.get(inp)

    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.covalentradii.get(inp, return_tuple=True)

    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.covalentradii.get(inp, return_tuple=True, missing=3.0)

    assert qcelemental.covalentradii.get(inp, missing=4.0) == pytest.approx(4.0, 1.0e-9)


a2b = 1.0 / qcelemental.constants.bohr2angstroms


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("KRYPTON", 1.16),
        ("kr", 1.16),
        ("kr84", 1.16),
        (36, 1.16),
        # aliases
        ("C", 0.76),
        ("C_sp", 0.69),
        ("MN", 1.61),
        ("Mn_lowspin", 1.39),
        # Deuterium
        ("D", 0.31),
        ("h2", 0.31),
    ],
)
def test_get(inp, expected):
    assert qcelemental.covalentradii.get(inp, units="angstrom") == pytest.approx(expected, 1.0e-9)
    assert qcelemental.covalentradii.get(inp) == pytest.approx(a2b * expected, 1.0e-9)


def test_get_tuple():
    ref = {"label": "Mn", "units": "angstrom", "data": Decimal("1.61")}
    dqca = qcelemental.covalentradii.get("manganese", return_tuple=True).dict()

    for itm in ref:
        assert ref[itm] == dqca[itm]


def test_c_header():
    qcelemental.covalentradii.write_c_header("header.h")
    os.remove("header.h")


def test_representation():
    qcelemental.covalentradii.string_representation()


def test_str():
    assert "CovalentRadii(" in str(qcelemental.covalentradii)


def test_covradmaker2018():
    with pytest.raises(KeyError) as e:
        qcelemental.CovalentRadii("COVRADMAKER2018")

    assert "only contexts {'ALVAREZ2008', } are currently supported" in str(e.value)
