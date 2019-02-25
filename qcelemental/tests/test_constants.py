import os
from decimal import Decimal

import pytest
import qcelemental


def test_access_1a():
    assert qcelemental.constants.c == 299792458


def test_access_1b():
    assert qcelemental.constants.speed_of_light_in_vacuum == 299792458


def test_access_1c():
    assert qcelemental.constants.pc['speed of light in vacuum'].data == 299792458


def test_access_1d():
    assert qcelemental.constants.get('speed of light in vacuum') == 299792458


def test_access_1e():
    qca = qcelemental.constants.get('speed of light in vacuum', return_tuple=True)

    assert qca.units == 'm s^{-1}'
    assert qca.comment == 'uncertainty=(exact)'
    assert qca.doi == '10.18434/T4WW24'
    assert qca.data == 299792458


def test_access_1f():
    assert qcelemental.constants.get('speed of LIGHT in vacuum') == 299792458


def test_access_2a():
    assert qcelemental.constants.Hartree_energy_in_eV == 27.21138602


def test_access_2b():
    assert qcelemental.constants.hartree2ev == 27.21138602


def test_access_2c():
    assert qcelemental.constants.pc['hartree energy in ev'].data == Decimal('27.21138602')


def test_access_2d():
    assert qcelemental.constants.get('hartree energy in ev') == 27.21138602


def test_access_2e():
    qca = qcelemental.constants.get('Hartree energy in eV', return_tuple=True)
    print(qca)

    assert qca.units == 'eV'
    assert qca.comment == 'uncertainty=0.000 000 17'
    assert qca.doi == '10.18434/T4WW24'
    assert qca.data == Decimal('27.21138602')


def test_access_2f():
    assert qcelemental.constants.get('hARTREE energy in eV') == 27.21138602


def test_access_2g():
    ref = {'label': 'Hartree energy in eV', 'units': 'eV', 'data': Decimal('27.21138602')}
    dqca = qcelemental.constants.get('Hartree energy in eV', return_tuple=True).dict()

    for itm in ref:
        assert ref[itm] == dqca[itm]


def test_c_header():
    qcelemental.constants.write_c_header("header.h")
    os.remove("header.h")


@pytest.mark.xfail(True, reason='comparison data not available for installed repository', run=True, strict=False)
def test_constants_comparison():
    qcelemental.constants.run_comparison()


def test_representation():
    qcelemental.constants.string_representation()


def test_str():
    assert "PhysicalConstantsContext(" in str(qcelemental.constants)


def test_codata2018():
    with pytest.raises(KeyError) as e:
        qcelemental.PhysicalConstantsContext("CODATA2018")

    assert "only contexts {'CODATA2014', } are currently supported" in str(e)
