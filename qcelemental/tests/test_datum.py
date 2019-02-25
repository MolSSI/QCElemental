from decimal import Decimal

import numpy as np
import pytest
import pydantic

import qcelemental as qcel
from qcelemental.testing import compare_recursive


@pytest.fixture
def dataset():
    datums = {
        'decimal': qcel.Datum('a label', 'mdyn/angstrom', Decimal('4.4'), comment='force constant', doi='10.1000/182'),
        'ndarray': qcel.Datum('an array', 'cm^-1',
                              np.arange(4, dtype=np.float) * 4 / 3, comment='freqs'),
        'float': qcel.Datum('a float', 'kg', 4.4, doi='10.1000/182'),
    }

    return datums


def test_creation(dataset):
    datum1 = dataset['decimal']

    assert datum1.label == 'a label'
    assert datum1.units == 'mdyn/angstrom'
    assert datum1.data == Decimal('4.4')


def test_creation_error():
    with pytest.raises(pydantic.ValidationError):
        qcel.Datum('ze lbl', 'ze unit', 'ze data')

    # assert 'Datum data should be float' in str(e)


@pytest.mark.parametrize("inp,expected", [
    (('decimal', None), 4.4),
    (('decimal', 'N/m'), 440),
    (('decimal', 'hartree/bohr/bohr'), 0.282614141011),
    (('ndarray', '1/m'), np.arange(4, dtype=np.float) * 400 / 3),
])
def test_units(dataset, inp, expected):
    assert dataset[inp[0]].to_units(inp[1]) == pytest.approx(expected, 1.e-9)


def test_printing(dataset):
    datum1 = dataset['decimal']
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
    str2 = datum1.__str__(label='Pytest')
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
  "ndarray" =>                        [cm^-1]
        [0.         1.33333333 2.66666667 4.        ]
"""

    assert str1 == qcel.datum.print_variables(dataset)


def test_to_dict(dataset):
    listans = [i * 4 / 3 for i in range(4)]
    ans = {'label': 'an array', 'units': 'cm^-1', 'data': listans, 'comment': 'freqs'}

    dicary = dataset['ndarray'].dict()
    assert compare_recursive(ans, dicary, 9)


def test_complex_scalar():
    datum1 = qcel.Datum('complex scalar', '', complex(1, 2))
    ans = {'label': 'complex scalar', 'units': '', 'data': complex(1, 2)}

    assert datum1.label == 'complex scalar'
    assert datum1.units == ''
    assert datum1.data.real == 1
    assert datum1.data.imag == 2

    dicary = datum1.dict()
    assert compare_recursive(ans, dicary, 9)


def test_complex_array():
    datum1 = qcel.Datum('complex array', '', np.arange(3, dtype=np.complex_) + 1j)
    ans = {'label': 'complex array', 'units': '', 'data': [complex(0, 1), complex(1, 1), complex(2, 1)]}

    dicary = datum1.dict()
    assert compare_recursive(ans, dicary, 9)
