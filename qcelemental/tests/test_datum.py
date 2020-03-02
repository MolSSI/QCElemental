from decimal import Decimal

import numpy as np
import pydantic
import pytest

import qcelemental as qcel
from qcelemental.testing import compare_recursive, compare_values


@pytest.fixture
def dataset():
    datums = {
        "decimal": qcel.Datum(
            "a label", "mdyn/angstrom", Decimal("4.4"), comment="force constant", doi="10.1000/182", numeric=False
        ),
        "ndarray": qcel.Datum("an array", "cm^-1", np.arange(4, dtype=np.float) * 4 / 3, comment="freqs"),
        "float": qcel.Datum("a float", "kg", 4.4, doi="10.1000/182"),
        "string": qcel.Datum("ze lbl", "ze unit", "ze data", numeric=False),
        "lststr": qcel.Datum("ze lbl", "ze unit", ["V", "R", None], numeric=False),
    }

    return datums


def test_creation(dataset):
    datum1 = dataset["decimal"]

    assert datum1.label == "a label"
    assert datum1.units == "mdyn/angstrom"
    assert datum1.data == Decimal("4.4")
    assert datum1.numeric is True  # checking that numeric got properly reset from input


def test_creation_nonnum(dataset):
    datum1 = dataset["string"]

    assert datum1.label == "ze lbl"
    assert datum1.units == "ze unit"
    assert datum1.data == "ze data"
    assert datum1.numeric is False


def test_creation_error():
    with pytest.raises(pydantic.ValidationError):
        qcel.Datum("ze lbl", "ze unit", "ze data")

    # assert 'Datum data should be float' in str(e)


@pytest.mark.parametrize(
    "inp,expected",
    [
        (("decimal", None), 4.4),
        (("decimal", "N/m"), 440),
        (("decimal", "hartree/bohr/bohr"), 0.282614141011 if qcel.constants.name == "CODATA2014" else 0.28261413658),
        (("ndarray", "1/m"), np.arange(4, dtype=np.float) * 400 / 3),
    ],
)
def test_units(dataset, inp, expected):
    assert compare_values(expected, dataset[inp[0]].to_units(inp[1]), atol=1.0e-9)


def test_printing(dataset):
    datum1 = dataset["decimal"]
    str1 = """----------------------------------------
             Datum a label
                 Pytest
----------------------------------------
Data:     4.4
Units:    [mdyn/angstrom]
doi:      10.1000/182
Comment:  force constant
Glossary:
----------------------------------------"""

    # Handle some odd spaces in the assert
    str2 = datum1.__str__(label="Pytest")
    assert all(x == y for x, y in zip(str1.split(), str2.split()))


def test_mass_printing_blank():
    pvnone = """
  Variable Map:
  ----------------------------------------------------------------------------
  (none)"""

    assert pvnone == qcel.datum.print_variables({})


def test_mass_printing(dataset):
    str1 = """
  Variable Map:
  ----------------------------------------------------------------------------
  "decimal" =>                    4.4 [mdyn/angstrom]
  "float"   =>         4.400000000000 [kg]
  "lststr"  =>       ['V', 'R', None] [ze unit]
  "ndarray" =>                        [cm^-1]
        [0.         1.33333333 2.66666667 4.        ]
  "string"  =>                ze data [ze unit]
"""

    assert str1 == qcel.datum.print_variables(dataset)


def test_to_dict(dataset):
    listans = [i * 4 / 3 for i in range(4)]
    ans = {"label": "an array", "units": "cm^-1", "data": listans, "comment": "freqs", "numeric": True}

    dicary = dataset["ndarray"].dict()
    assert compare_recursive(ans, dicary, 9)


def test_complex_scalar():
    datum1 = qcel.Datum("complex scalar", "", complex(1, 2))
    ans = {"label": "complex scalar", "units": "", "data": complex(1, 2), "numeric": True}

    assert datum1.label == "complex scalar"
    assert datum1.units == ""
    assert datum1.data.real == 1
    assert datum1.data.imag == 2

    dicary = datum1.dict()
    assert compare_recursive(ans, dicary, 9)


def test_complex_array():
    datum1 = qcel.Datum("complex array", "", np.arange(3, dtype=np.complex_) + 1j)
    ans = {
        "label": "complex array",
        "units": "",
        "data": [complex(0, 1), complex(1, 1), complex(2, 1)],
        "numeric": True,
    }

    dicary = datum1.dict()
    assert compare_recursive(ans, dicary, 9)
