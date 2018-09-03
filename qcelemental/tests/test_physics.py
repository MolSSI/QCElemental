from decimal import Decimal

import pytest

import qcelemental


def test_access_1a():
    assert qcelemental.constants.c == 299_792_458


def test_access_1b():
    assert qcelemental.constants.speed_of_light_in_vacuum == 299_792_458


def test_access_1c():
    assert qcelemental.constants.pc['speed of light in vacuum'].data == 299_792_458


def test_access_1d():
    assert qcelemental.constants.get('speed of light in vacuum') == 299_792_458


def test_access_1e():
    qca = qcelemental.constants.get('speed of light in vacuum', return_object=True)

    assert qca.units == 'm s^{-1}'
    assert qca.comment == 'uncertainty=(exact)'
    assert qca.doi == '10.18434/T4WW24'
    assert qca.data == 299_792_458


def test_access_1f():
    assert qcelemental.constants.get('speed of LIGHT in vacuum') == 299_792_458


def test_access_2a():
    assert qcelemental.constants.Hartree_energy_in_eV == 27.211_386_02


def test_access_2b():
    assert qcelemental.constants.hartree2ev == 27.211_386_02


def test_access_2c():
    assert qcelemental.constants.pc['hartree energy in ev'].data == Decimal('27.211_386_02')


def test_access_2d():
    assert qcelemental.constants.get('hartree energy in ev') == 27.211_386_02


def test_access_2e():
    qca = qcelemental.constants.get('Hartree energy in eV', return_object=True)

    assert qca.units == 'eV'
    assert qca.comment == 'uncertainty=0.000 000 17'
    assert qca.doi == '10.18434/T4WW24'
    assert qca.data == Decimal('27.211_386_02')


def test_access_2f():
    assert qcelemental.constants.get('hARTREE energy in eV') == 27.211_386_02


def test_access_2g():
    ref = {'lbl': 'Hartree energy in eV', 'units': 'eV', 'data': Decimal('27.211_386_02')}
    dqca = qcelemental.constants.get('Hartree energy in eV', return_object=True).to_dict()

    for itm in ref:
        assert ref[itm] == dqca[itm]


def test_psi4_header():
    qcelemental.constants.write_psi4_header()


def test_psi4_comparison():
    qcelemental.constants.run_comparison()


def test_print_out():
    qcelemental.constants.print_out()
