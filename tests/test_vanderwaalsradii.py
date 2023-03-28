import os
from decimal import Decimal

import pytest

import qcelemental


@pytest.mark.parametrize("inp", ["He100", "-1", -1, -1.0, "cat", 200, "Cro"])
def test_id_resolution_error_bad_element(inp):
    with pytest.raises(qcelemental.NotAnElementError):
        qcelemental.vdwradii.get(inp)


@pytest.mark.parametrize("inp", ["X", "Fe", 100, "Ru"])
def test_id_resolution_error(inp):
    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.vdwradii.get(inp)

    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.vdwradii.get(inp, return_tuple=True)

    with pytest.raises(qcelemental.DataUnavailableError):
        qcelemental.vdwradii.get(inp, return_tuple=True, missing=3.0)

    assert qcelemental.vdwradii.get(inp, missing=4.0) == pytest.approx(4.0, 1.0e-9)


a2b = 1.0 / qcelemental.constants.bohr2angstroms


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Kr 84
        ("KRYPTON", 2.02),
        ("kr", 2.02),
        ("kr84", 2.02),
        (36, 2.02),
        # Deuterium
        ("D", 1.10),
        ("h2", 1.10),
        # Germanium
        ("germanium", 2.11),
        ("Ge", 2.11),
    ],
)
def test_get(inp, expected):
    assert qcelemental.vdwradii.get(inp, units="angstrom") == pytest.approx(expected, 1.0e-9)
    assert qcelemental.vdwradii.get(inp) == pytest.approx(a2b * expected, 1.0e-9)


def test_get_tuple():
    ref = {"label": "Mg", "units": "angstrom", "data": Decimal("1.73")}
    dqca = qcelemental.vdwradii.get("magnesium", return_tuple=True).dict()

    for itm in ref:
        assert ref[itm] == dqca[itm]


def test_c_header():
    qcelemental.vdwradii.write_c_header("header.h")
    os.remove("header.h")


def test_representation():
    qcelemental.vdwradii.string_representation()


def test_str():
    print(str(qcelemental.vdwradii))
    assert "VanderWaalsRadii(" in str(qcelemental.vdwradii)


def test_vdwradmaker2018():
    with pytest.raises(KeyError) as e:
        qcelemental.VanderWaalsRadii("VDWRADMAKER2019")

    assert "only contexts {'MANTINA2009', } are currently supported" in str(e.value)
