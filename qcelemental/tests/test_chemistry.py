from decimal import Decimal

import pytest

import qcelemental


def test_id_resolution_1():
    assert qcelemental.periodictable._resolve_atom_to_key('He') == 'He'


def test_id_resolution_2():
    assert qcelemental.periodictable._resolve_atom_to_key('hE') == 'He'


def test_id_resolution_3():
    assert qcelemental.periodictable._resolve_atom_to_key('HE4') == 'He4'


def test_id_resolution_4():
    assert qcelemental.periodictable._resolve_atom_to_key('helium') == 'He'


def test_id_resolution_5():
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key('He100')


def test_id_resolution_6():
    assert qcelemental.periodictable._resolve_atom_to_key('2') == 'He'


def test_id_resolution_7():
    assert qcelemental.periodictable._resolve_atom_to_key(2) == 'He'


def test_id_resolution_8():
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key(-1)


def test_id_resolution_9():
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key('-1')


def test_id_resolution_10():
    assert qcelemental.periodictable._resolve_atom_to_key(2.0) == 'He'


def test_id_resolution_11():
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key('cat')


def test_id_resolution_12():
    with pytest.raises(qcelemental.exceptions.NotAnElementError):
        qcelemental.periodictable._resolve_atom_to_key(200)


# TODO test ghost


def test_to_mass_1():
    assert qcelemental.periodictable.to_mass('kr', return_decimal=True) == Decimal('83.9114977282')


def test_to_mass_2():
    assert qcelemental.periodictable.to_mass('KRYPTON') == 83.9114977282


def test_to_mass_3():
    assert qcelemental.periodictable.to_mass('kr84') == 83.9114977282


def test_to_mass_4():
    assert qcelemental.periodictable.to_mass('Kr86') == 85.9106106269


def test_to_mass_5():
    assert qcelemental.periodictable.to_mass(36) == 83.9114977282


def test_to_mass_6():
    assert qcelemental.periodictable.to_mass('D') == 2.01410177812


def test_to_mass_7():
    assert qcelemental.periodictable.to_mass('h2') == 2.01410177812


def test_to_mass_number_1():
    assert qcelemental.periodictable.to_A('kr') == 84


def test_to_mass_number_2():
    assert qcelemental.periodictable.to_A('KRYPTON') == 84


def test_to_mass_number_3():
    assert qcelemental.periodictable.to_A('kr84') == 84


def test_to_mass_number_4():
    assert qcelemental.periodictable.to_A('Kr86') == 86


def test_to_mass_number_5():
    assert qcelemental.periodictable.to_A(36) == 84


def test_to_mass_number_6():
    assert qcelemental.periodictable.to_A('D') == 2


def test_to_mass_number_7():
    assert qcelemental.periodictable.to_A('h2') == 2


def test_to_atomic_number_1():
    assert qcelemental.periodictable.to_Z('kr') == 36


def test_to_atomic_number_2():
    assert qcelemental.periodictable.to_Z('KRYPTON') == 36


def test_to_atomic_number_3():
    assert qcelemental.periodictable.to_Z('kr84') == 36


def test_to_atomic_number_4():
    assert qcelemental.periodictable.to_Z('Kr86') == 36


def test_to_atomic_number_5():
    assert qcelemental.periodictable.to_Z(36) == 36


def test_to_atomic_number_6():
    assert qcelemental.periodictable.to_Z('D') == 1


def test_to_atomic_number_7():
    assert qcelemental.periodictable.to_Z('h2') == 1


def test_to_symbol_1():
    assert qcelemental.periodictable.to_E('kr') == 'Kr'


def test_to_symbol_2():
    assert qcelemental.periodictable.to_E('KRYPTON') == 'Kr'


def test_to_symbol_3():
    assert qcelemental.periodictable.to_E('kr84') == 'Kr'


def test_to_symbol_4():
    assert qcelemental.periodictable.to_E('Kr86') == 'Kr'


def test_to_symbol_5():
    assert qcelemental.periodictable.to_E(36) == 'Kr'


def test_to_symbol_6():
    assert qcelemental.periodictable.to_E('D') == 'H'


def test_to_symbol_7():
    assert qcelemental.periodictable.to_E('h2') == 'H'


def test_to_element_1():
    assert qcelemental.periodictable.to_element('kr') == 'Krypton'


def test_to_element_2():
    assert qcelemental.periodictable.to_element('KRYPTON') == 'Krypton'


def test_to_element_3():
    assert qcelemental.periodictable.to_element('kr84') == 'Krypton'


def test_to_element_4():
    assert qcelemental.periodictable.to_element('Kr86') == 'Krypton'


def test_to_element_5():
    assert qcelemental.periodictable.to_element(36) == 'Krypton'


def test_to_element_6():
    assert qcelemental.periodictable.to_element('D') == 'Hydrogen'


def test_to_element_7():
    assert qcelemental.periodictable.to_element('h2') == 'Hydrogen'


def test_psi4_header():
    qcelemental.periodictable.write_psi4_header()


def test_psi4_header():
    qcelemental.periodictable.run_comparison()
