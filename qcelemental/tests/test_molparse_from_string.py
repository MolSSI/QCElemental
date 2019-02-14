import copy
import sys

import numpy as np
import pytest
import qcelemental
from qcelemental.testing import compare, compare_molrecs, compare_recursive, tnm

_arrays_prov_stamp = {'creator': 'QCElemental', 'version': '1.0', 'routine': 'qcelemental.molparse.from_arrays'}
_string_prov_stamp = {'creator': 'QCElemental', 'version': '1.0', 'routine': 'qcelemental.molparse.from_string'}

subject1 = """O 0 0   0
no_com

H 1 ,, 0 \t  0 # stuff-n-nonsense"""

ans1 = {
    'geom': [0., 0., 0., 1., 0., 0.],
    'elbl': ['O', 'H'],
    'fix_com': True,
    'fragment_separators': [],
    'fragment_charges': [None],
    'fragment_multiplicities': [None],
    'fragment_files': [],
    'geom_hints': [],
    'hint_types': [],
}

fullans1a = {
    'geom': np.array([0., 0., 0., 1., 0., 0.]),
    'elea': np.array([16, 1]),
    'elez': np.array([8, 1]),
    'elem': np.array(['O', 'H']),
    'mass': np.array([15.99491462, 1.00782503]),
    'real': np.array([True, True]),
    'elbl': np.array(['', '']),
    'units': 'Angstrom',
    'fix_com': True,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [0.0],
    'fragment_multiplicities': [2],
    'molecular_charge': 0.0,
    'molecular_multiplicity': 2,
}
fullans1c = copy.deepcopy(fullans1a)
fullans1c.update({
    'fragment_charges': [1.],
    'fragment_multiplicities': [1],
    'molecular_charge': 1.,
    'molecular_multiplicity': 1
})


def test_psi4_qm_1a():
    subject = subject1
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans1, intermed, atol=1.e-4)
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_1ab():
    subject = subject1
    ans = copy.deepcopy(ans1)
    ans['fix_orientation'] = False
    ans['fix_com'] = False
    fullans = copy.deepcopy(fullans1a)
    fullans['fix_com'] = False
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(
        subject, return_processed=True, fix_orientation=False, fix_com=False)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_1b():
    subject = '\n' + '\t' + subject1 + '\n\n'
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans1, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_1c():
    subject = '1 1\n  -- \n' + subject1
    ans = copy.deepcopy(ans1)
    ans.update({'molecular_charge': 1., 'molecular_multiplicity': 1})
    fullans = copy.deepcopy(fullans1c)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_1d():
    subject = subject1 + '\n1 1'
    ans = copy.deepcopy(ans1)
    ans.update({'fragment_charges': [1.], 'fragment_multiplicities': [1]})
    fullans = copy.deepcopy(fullans1c)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_1e():
    """duplicate com"""
    subject = subject1 + '\n  nocom'

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_qm_1f():

    final = qcelemental.molparse.from_arrays(
        geom=np.array([0., 0., 0., 1., 0., 0.]),
        elez=np.array([8, 1]),
        units='Angstrom',
        fix_com=True,
        fix_orientation=False)


def test_psi4_qm_iutautoobig_error_1g():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=np.array([0., 0., 0., 1., 0., 0.]),
            elez=np.array([8, 1]),
            input_units_to_au=1.1 / 0.52917721067,
            units='Angstrom',
            fix_com=True,
            fix_orientation=False)

    assert 'No big perturbations to physical constants' in str(e)


def test_psi4_qm_iutau_1h():
    fullans = copy.deepcopy(fullans1a)
    iutau = 1.01 / 0.52917721067
    fullans['input_units_to_au'] = iutau
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        geom=np.array([0., 0., 0., 1., 0., 0.]),
        elez=np.array([8, 1]),
        input_units_to_au=iutau,
        units='Angstrom',
        fix_com=True,
        fix_orientation=False)

    assert compare_molrecs(fullans, final, tnm() + ': full')

    smol = qcelemental.molparse.to_string(final, dtype='xyz', units='Bohr')
    rsmol = """2 au
HO
O                     0.000000000000     0.000000000000     0.000000000000
H                     1.908623386712     0.000000000000     0.000000000000
"""
    assert compare(rsmol, smol, tnm() + ': str')


def test_psi4_qm_iutau_1i():
    fullans = copy.deepcopy(fullans1a)
    iutau = 1.01 / 0.52917721067
    fullans['input_units_to_au'] = iutau
    fullans['fix_symmetry'] = 'cs'
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        geom=np.array([0., 0., 0., 1., 0., 0.]),
        elez=np.array([8, 1]),
        input_units_to_au=iutau,
        units='Angstrom',
        fix_symmetry="CS",
        fix_com=True,
        fix_orientation=False)

    assert compare_molrecs(fullans, final, tnm() + ': full')

    kmol = qcelemental.molparse.to_schema(final, dtype=1, units='Bohr')
    schema14_1_iutau = {
        "schema_name": "qc_schema_input",
        "schema_version": 1,
        "molecule": {
            "geometry": [0.0, 0.0, 0.0, 1.908623386712, 0.0, 0.0],
            "symbols": ["O", "H"],
            "atomic_numbers": [8, 1],
            "mass_numbers": [16, 1],
            "atom_labels": ["", ""],
            'fragments': [[0, 1]],
            'fragment_charges': [0.0],
            'fragment_multiplicities': [2],
            'masses': [15.99491462, 1.00782503],
            'name': 'HO',
            'fix_com': True,
            'fix_orientation': False,
            'fix_symmetry': 'cs',
            'molecular_charge': 0.0,
            "molecular_multiplicity": 2,
            "real": [True, True],
            "provenance": _arrays_prov_stamp
        }
    }

    assert compare_molrecs(schema14_1_iutau["molecule"], kmol["molecule"], tnm() + ': sch', atol=1.e-8)


subject2 = [
    """
6Li 0.0 0.0 0.0
  units  a.u.
H_specIAL@2.014101  100 0 0""", """@Ne 2 4 6""", """h .0,1,2
Gh(he3) 0 1 3
noreorient"""
]

ans2 = {
    'geom': [0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.],
    'elbl': ['6Li', 'H_specIAL@2.014101', '@Ne', 'h', 'Gh(he3)'],
    'units': 'Bohr',
    'fix_orientation': True,
    'fragment_separators': [2, 3],
    'fragment_charges': [None, None, None],
    'fragment_multiplicities': [None, None, None],
    'fragment_files': [],
    'geom_hints': [],
    'hint_types': [],
}

fullans2 = {
    'geom': np.array([0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.]),
    'elea': np.array([6, 2, 20, 1, 4]),
    'elez': np.array([3, 1, 10, 1, 2]),
    'elem': np.array(['Li', 'H', 'Ne', 'H', 'He']),
    'mass': np.array([6.015122794, 2.014101, 19.99244017542, 1.00782503, 4.00260325415]),
    'real': np.array([True, True, False, True, False]),
    'elbl': np.array(['', '_special', '', '', '3']),
    'units': 'Bohr',
    'fix_com': False,
    'fix_orientation': True,
    'fragment_separators': [2, 3],
}
fullans2_unnp = copy.deepcopy(fullans2)
fullans2_unnp.update({
    'geom': [0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.],
    'elea': [6, 2, 20, 1, 4],
    'elez': [3, 1, 10, 1, 2],
    'elem': ['Li', 'H', 'Ne', 'H', 'He'],
    'mass': [6.015122794, 2.014101, 19.99244017542, 1.00782503, 4.00260325415],
    'real': [True, True, False, True, False],
    'elbl': ['', '_special', '', '', '3'],
})


def test_psi4_qm_2a():
    subject = '\n--\n'.join(subject2)
    fullans = copy.deepcopy(fullans2)
    fullans_unnp = copy.deepcopy(fullans2_unnp)
    ud = {
        'molecular_charge': 0.,
        'molecular_multiplicity': 2,
        'fragment_charges': [0., 0., 0.],
        'fragment_multiplicities': [1, 1, 2]
    }
    fullans.update(ud)
    fullans_unnp.update(ud)
    fullans['provenance'] = _string_prov_stamp
    fullans_unnp['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans2, intermed, tnm() + ': intermediate')
    final_unnp = qcelemental.util.unnp(final['qm'])
    assert compare_molrecs(fullans_unnp, final_unnp, tnm() + ': full unnp')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_2b():
    subject = copy.deepcopy(subject2)
    subject.insert(0, '1 3')
    subject = '\n--\n'.join(subject)
    ans = copy.deepcopy(ans2)
    ans.update({'molecular_charge': 1., 'molecular_multiplicity': 3})
    fullans = copy.deepcopy(fullans2)
    fullans.update({
        'molecular_charge': 1.,
        'molecular_multiplicity': 3,
        'fragment_charges': [1., 0., 0.],
        'fragment_multiplicities': [2, 1, 2]
    })
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_psi4_qm_2c():
    """double overall chg/mult spec"""
    subject = copy.deepcopy(subject2)
    subject.insert(0, '1 3\n1 3')
    subject = '\n--\n'.join(subject)

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_qm_2d():
    """trailing comma"""
    subject = copy.deepcopy(subject2)
    subject.insert(0, 'H 10,10,10,')
    subject = '\n--\n'.join(subject)

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


#def test_psi4_qm_2e():
#    """empty fragment"""
#    subject = copy.deepcopy(subject2)
#    subject.insert(2, '\n')
#    subject = '\n--\n'.join(subject)
#
#    with pytest.raises(qcelemental.MoleculeFormatError):
#        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_qm_2f():
    """double frag chgmult"""
    subject = copy.deepcopy(subject2)
    subject[1] += '\n 1 2\n 5 6'
    subject = '\n--\n'.join(subject)

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_qm_2g():
    """illegal chars in nucleus"""
    subject = copy.deepcopy(subject2)
    subject[1] = """@Ne_{CN}_O 2 4 6"""
    subject = '\n--\n'.join(subject)

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_qm_3():
    """psi4/psi4#731"""
    subject = """0 1
Mg 0 0"""

    with pytest.raises(qcelemental.ValidationError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


subject5 = """
efp C6H6 -0.30448173 -2.24210052 -0.29383131 -0.642499 7.817407 -0.568147  # second to last equiv to 1.534222
--
efp C6H6 -0.60075437  1.36443336  0.78647823  3.137879 1.557344 -2.568550
"""

ans5 = {
    'fragment_files': ['C6H6', 'C6H6'],
    'hint_types': ['xyzabc', 'xyzabc'],
    'geom_hints': [[-0.30448173, -2.24210052, -0.29383131, -0.642499, 7.817407, -0.568147],
                   [-0.60075437, 1.36443336, 0.78647823, 3.137879, 1.557344, -2.568550]],
    'geom': [],
    'elbl': [],
    'fragment_charges': [None],
    'fragment_multiplicities': [None],
    'fragment_separators': [],
}

fullans5b = {'efp': {}}
fullans5b['efp']['hint_types'] = ans5['hint_types']
fullans5b['efp']['geom_hints'] = ans5['geom_hints']
fullans5b['efp']['units'] = 'Bohr'
fullans5b['efp']['fix_com'] = True
fullans5b['efp']['fix_orientation'] = True
fullans5b['efp']['fix_symmetry'] = 'c1'
fullans5b['efp']['fragment_files'] = ['c6h6', 'c6h6']


def test_psi4_efp_5a():
    subject = subject5

    hintsans = [[
        (val / qcelemental.constants.bohr2angstroms if i < 3 else val) for i, val in enumerate(ans5['geom_hints'][0])
    ], [(val / qcelemental.constants.bohr2angstroms if i < 3 else val) for i, val in enumerate(ans5['geom_hints'][1])]]
    hintsans[0][4] = 1.534222
    fullans = copy.deepcopy(fullans5b)
    fullans['efp']['units'] = 'Angstrom'
    fullans['efp']['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans5, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': final efp')

    hintsstd = qcelemental.util.standardize_efp_angles_units('Angstrom', final['efp']['geom_hints'])
    final['efp']['geom_hints'] = hintsstd
    fullans['efp']['geom_hints'] = hintsans
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': final efp standardized')


def test_psi4_efp_5b():
    subject = subject5 + '\nunits bohr'

    ans = copy.deepcopy(ans5)
    ans['units'] = 'Bohr'
    fullans = copy.deepcopy(fullans5b)
    fullans['efp']['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': final efp')


def test_psi4_efp_5c():
    """fix_orientation not mol kw"""
    subject = subject5 + '\nno_com\nfix_orientation\nsymmetry c1'

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_psi4_efp_5d():
    subject = subject5 + '\nno_com\nno_reorient\nsymmetry c1\nunits a.u.'

    ans = copy.deepcopy(ans5)
    ans['units'] = 'Bohr'
    ans['fix_com'] = True
    ans['fix_orientation'] = True
    ans['fix_symmetry'] = 'c1'
    fullans = copy.deepcopy(fullans5b)
    fullans['efp']['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': final')


def test_psi4_efp_5e():
    """symmetry w/efp"""
    subject = subject5 + 'symmetry cs\nunits a.u.'

    with pytest.raises(qcelemental.ValidationError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


subject6 = """
    0 1
    O1    0         0     0.118720
    h2   -0.753299, 0.0, -0.474880

    H3    0.753299, 0.0, -0.474880

    --
    efp h2O -2.12417561  1.22597097 -0.95332054 -2.902133 -4.5481863 -1.953647  # second to last equiv to 1.734999
 --
efp ammoniA
     0.98792    1.87681    2.85174
units au
     1.68798    1.18856    3.09517

     1.45873    2.55904    2.27226

"""

ans6 = {
    'units':
    'Bohr',
    'geom': [0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
    'elbl': ['O1', 'h2', 'H3'],
    'fragment_charges': [0.],
    'fragment_multiplicities': [1],
    'fragment_separators': [],
    'fragment_files': ['h2O', 'ammoniA'],
    'geom_hints': [[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                   [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
    'hint_types': ['xyzabc', 'points'],
}

fullans6 = {
    'qm': {
        'geom': np.array([0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880]),
        'elea': np.array([16, 1, 1]),
        'elez': np.array([8, 1, 1]),
        'elem': np.array(['O', 'H', 'H']),
        'mass': np.array([15.99491462, 1.00782503, 1.00782503]),
        'real': np.array([True, True, True]),
        'elbl': np.array(['1', '2', '3']),
        'units': 'Bohr',
        'fix_com': True,
        'fix_orientation': True,
        'fix_symmetry': 'c1',
        'fragment_charges': [0.],
        'fragment_multiplicities': [1],
        'fragment_separators': [],
        'molecular_charge': 0.,
        'molecular_multiplicity': 1
    },
    'efp': {
        'fragment_files': ['h2o', 'ammonia'],
        'geom_hints': [[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                       [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
        'hint_types': ['xyzabc', 'points'],
        'units':
        'Bohr',
        'fix_com':
        True,
        'fix_orientation':
        True,
        'fix_symmetry':
        'c1',
    }
}


def test_psi4_qmefp_6a():
    subject = subject6
    fullans = copy.deepcopy(fullans6)
    fullans['qm']['provenance'] = _string_prov_stamp
    fullans['efp']['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans6, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')

    hintsstd = qcelemental.util.standardize_efp_angles_units('Bohr', final['efp']['geom_hints'])
    final['efp']['geom_hints'] = hintsstd
    fullans['efp']['geom_hints'][0][4] = 1.734999
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': final efp standardized')


def test_psi4_qmefp_6b():
    subject = subject6.replace('au', 'ang')

    ans = copy.deepcopy(ans6)
    ans['units'] = 'Angstrom'

    fullans = copy.deepcopy(fullans6)
    fullans['qm']['units'] = 'Angstrom'
    fullans['efp']['units'] = 'Angstrom'
    fullans['qm']['provenance'] = _string_prov_stamp
    fullans['efp']['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')


def test_psi4_qmefpformat_error_6c():
    """try to give chgmult to an efp"""

    subject = subject6.replace('    efp h2O', '0 1\n    efp h2O')

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)


def test_qmefp_array_6d():

    fullans = copy.deepcopy(fullans6)
    fullans['qm']['provenance'] = _arrays_prov_stamp
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(
        units='Bohr',
        geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
        elbl=['O1', 'h2', 'H3'],
        fragment_files=['h2O', 'ammoniA'],
        geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                    [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
        hint_types=['xyzabc', 'points'])

    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')


def test_qmefp_badhint_error_6e():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'efp1'])

    assert "hint_types not among 'xyzabc', 'points', 'rotmat'" in str(e)


def test_qmefp_badefpgeom_error_6f():

    with pytest.raises(qcelemental.ValidationError) as e:
        final = qcelemental.molparse.from_input_arrays(
            units='Bohr',
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, None, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'points'])

    assert "Un float-able elements in geom_hints" in str(e)


def test_qmefp_badhintgeom_error_6g():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['points', 'xyzabc'])

    assert 'EFP hint type points not 9 elements' in str(e)


def test_qmefp_badfragfile_error_6h():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 5],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'points'])

    assert 'fragment_files not strings' in str(e)


def test_qmefp_hintlen_error_6i():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'points', 'points'])

    assert 'Missing or inconsistent length among efp quantities' in str(e)


def test_qmefp_fixcom_error_6j():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            fix_com=False,
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'points'])

    assert 'Invalid fix_com (False) with extern (True)' in str(e)


def test_qmefp_fixori_error_6k():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_input_arrays(
            units='Bohr',
            fix_orientation=False,
            geom=[0., 0., 0.118720, -0.753299, 0.0, -0.474880, 0.753299, 0.0, -0.474880],
            elbl=['O1', 'h2', 'H3'],
            fragment_files=['h2O', 'ammoniA'],
            geom_hints=[[-2.12417561, 1.22597097, -0.95332054, -2.902133, -4.5481863, -1.953647],
                        [0.98792, 1.87681, 2.85174, 1.68798, 1.18856, 3.09517, 1.45873, 2.55904, 2.27226]],
            hint_types=['xyzabc', 'points'])

    assert 'Invalid fix_orientation (False) with extern (True)' in str(e)


#QCEL@using_pylibefp
#QCELdef test_psi4_qmefp_6d():
#QCEL    subject = subject6
#QCEL
#QCEL    fullans = copy.deepcopy(fullans6)
#QCEL    fullans['efp']['geom'] = np.array([-2.22978429,  1.19270015, -0.99721732, -1.85344873,  1.5734809 ,
#QCEL        0.69660583, -0.71881655,  1.40649303, -1.90657336,  0.98792   ,
#QCEL        1.87681   ,  2.85174   ,  2.31084386,  0.57620385,  3.31175679,
#QCEL        1.87761143,  3.16604791,  1.75667803,  0.55253064,  2.78087794,
#QCEL        4.47837555])
#QCEL    fullans['efp']['elea'] = np.array([16, 1, 1, 14, 1, 1, 1])
#QCEL    fullans['efp']['elez'] = np.array([8, 1, 1, 7, 1, 1, 1])
#QCEL    fullans['efp']['elem'] = np.array(['O', 'H', 'H', 'N', 'H', 'H', 'H'])
#QCEL    fullans['efp']['mass'] = np.array([15.99491462, 1.00782503, 1.00782503, 14.00307400478, 1.00782503, 1.00782503, 1.00782503])
#QCEL    fullans['efp']['real'] = np.array([True, True, True, True, True, True, True])
#QCEL    fullans['efp']['elbl'] = np.array(['_a01o1', '_a02h2', '_a03h3', '_a01n1', '_a02h2', '_a03h3', '_a04h4'])
#QCEL    fullans['efp']['fragment_separators'] = [3]
#QCEL    fullans['efp']['fragment_charges'] = [0., 0.]
#QCEL    fullans['efp']['fragment_multiplicities'] = [1, 1]
#QCEL    fullans['efp']['molecular_charge'] = 0.
#QCEL    fullans['efp']['molecular_multiplicity'] = 1
#QCEL    fullans['efp']['hint_types'] = ['xyzabc', 'xyzabc']
#QCEL    fullans['efp']['geom_hints'][1] = [1.093116487139866, 1.9296501432128303, 2.9104336205167156, -1.1053108079381473, 2.0333070957565544, -1.488586877218809]
#QCEL
#QCEL    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True)
#QCEL
#QCEL    import pylibefp
#QCEL    efpobj = pylibefp.from_dict(final['efp'])
#QCEL    efpfinal = efpobj.to_dict()
#QCEL    efpfinal = qcelemental.molparse.from_arrays(speclabel=False, domain='efp', **efpfinal)
#QCEL
#QCEL    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
#QCEL    assert compare_molrecs(fullans['efp'], efpfinal, tnm() + ': full efp')

subject7 = """\
5
   stuffs
6Li 0.0 0.0 0.0
H_specIAL@2.014101  100 0 0
@Ne 2 4 6
h .0,1,2
Gh(he3) 0 1 3
"""

ans7 = {
    'geom': [0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.],
    'elbl': ['6Li', 'H_specIAL@2.014101', '@Ne', 'h', 'Gh(he3)'],
    'units': 'Angstrom',
    'geom_hints': [],  # shouldn't be needed
}

fullans7 = {
    'geom': np.array([0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.]),
    'elea': np.array([6, 2, 20, 1, 4]),
    'elez': np.array([3, 1, 10, 1, 2]),
    'elem': np.array(['Li', 'H', 'Ne', 'H', 'He']),
    'mass': np.array([6.015122794, 2.014101, 19.99244017542, 1.00782503, 4.00260325415]),
    'real': np.array([True, True, False, True, False]),
    'elbl': np.array(['', '_special', '', '', '3']),
    'units': 'Angstrom',
    'fix_com': False,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [0.],
    'fragment_multiplicities': [2],
    'molecular_charge': 0.,
    'molecular_multiplicity': 2,
}


def test_xyzp_qm_7a():
    """XYZ doesn't fit into psi4 string"""
    subject = subject7

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='psi4')


def test_xyzp_qm_7b():
    """XYZ doesn't fit into strict xyz string"""
    subject = subject7

    with pytest.raises(qcelemental.MoleculeFormatError):
        final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='xyz')


def test_xyzp_qm_7c():
    subject = subject7
    fullans = copy.deepcopy(fullans7)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='xyz+')
    assert compare_recursive(ans7, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full qm')


def test_xyzp_qm_7d():
    subject = subject7.replace('5', '5 au ')
    subject = subject.replace('stuff', '-1 3 slkdjfl2 32#$^& ')

    ans = copy.deepcopy(ans7)
    ans['units'] = 'Bohr'
    ans['molecular_charge'] = -1.
    ans['molecular_multiplicity'] = 3

    fullans = copy.deepcopy(fullans7)
    fullans['units'] = 'Bohr'
    fullans['fragment_charges'] = [-1.]
    fullans['fragment_multiplicities'] = [3]
    fullans['molecular_charge'] = -1.
    fullans['molecular_multiplicity'] = 3
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='xyz+')
    assert compare_recursive(ans, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full qm')


def test_xyzp_qm_7e():
    subject = subject7.replace('5', '5 ang')
    fullans = copy.deepcopy(fullans7)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='xyz+')
    assert compare_recursive(ans7, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full qm')


subject8 = """\
3
   stuffs
Li 0.0 0.0 0.0
1  100 0 0
Ne 2 4 6
h .0,1,2
 2 0 1 3
"""

ans8 = {
    'geom': [0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.],
    'elbl': ['Li', '1', 'Ne', 'h', '2'],
    'units': 'Angstrom',
    'geom_hints': [],  # shouldn't be needed
}

fullans8 = {
    'geom': np.array([0., 0., 0., 100., 0., 0., 2., 4., 6., 0., 1., 2., 0., 1., 3.]),
    'elea': np.array([7, 1, 20, 1, 4]),
    'elez': np.array([3, 1, 10, 1, 2]),
    'elem': np.array(['Li', 'H', 'Ne', 'H', 'He']),
    'mass': np.array([7.016004548, 1.00782503, 19.99244017542, 1.00782503, 4.00260325415]),
    'real': np.array([True, True, True, True, True]),
    'elbl': np.array(['', '', '', '', '']),
    'units': 'Angstrom',
    'fix_com': False,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [0.],
    'fragment_multiplicities': [2],
    'molecular_charge': 0.,
    'molecular_multiplicity': 2,
}


def test_xyzp_qm_8a():
    subject = subject8
    fullans = copy.deepcopy(fullans8)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, dtype='xyz+')
    assert compare_recursive(ans8, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full qm', atol=1.e-4)


fullans10qm = {
    'geom': np.array([0., 0., 0.]),
    'elea': np.array([12]),
    'elez': np.array([6]),
    'elem': np.array(['C']),
    'mass': np.array([12.]),
    'real': np.array([True]),
    'elbl': np.array(['']),
    'units': 'Angstrom',
    'fix_com': False,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [0.],
    'fragment_multiplicities': [1],
    'molecular_charge': 0.,
    'molecular_multiplicity': 1
}
fullans10efp = {
    'fragment_files': ['cl2'],
    'hint_types': ['xyzabc'],
    'geom_hints': [[0., 0., 0., 0., 0., 0.]],
    'units': 'Angstrom',
    'fix_com': True,
    'fix_orientation': True,
    'fix_symmetry': 'c1'
}
blankqm = {
    'geom': np.array([]),
    'elea': np.array([]),
    'elez': np.array([]),
    'elem': np.array([]),
    'mass': np.array([]),
    'real': np.array([]),
    'elbl': np.array([]),
    'units': 'Angstrom',
    'fix_com': False,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [0.],
    'fragment_multiplicities': [1],
    'molecular_charge': 0.,
    'molecular_multiplicity': 1
}
blankefp = {
    'fragment_files': [],
    'hint_types': [],
    'geom_hints': [],
    'units': 'Angstrom',
    'fix_com': True,
    'fix_orientation': True,
    'fix_symmetry': 'c1'
}


def test_arrays_10a():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': True
    }

    fullans = {'qm': copy.deepcopy(fullans10qm), 'efp': copy.deepcopy(fullans10efp)}
    fullans['qm']['fix_com'] = True
    fullans['qm']['fix_orientation'] = True
    fullans['qm']['fix_symmetry'] = 'c1'
    fullans['qm']['provenance'] = _arrays_prov_stamp
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10b():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': False,
        'enable_efp': True
    }

    fullans = {'efp': fullans10efp}
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10c():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': False
    }

    fullans = {'qm': fullans10qm}
    fullans['qm']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10d():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_efp': 'none'
    }

    fullans = {'qm': fullans10qm}
    fullans['qm']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10e():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_efp': 'minimal'
    }

    fullans = {'qm': fullans10qm, 'efp': blankefp}
    fullans['qm']['provenance'] = _arrays_prov_stamp
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10f():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_efp': 'error'
    }

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.from_input_arrays(**subject)


def test_arrays_10g():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': False,
        'enable_efp': True,
        'missing_enabled_return_efp': 'none'
    }

    fullans = {}

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10h():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': False,
        'enable_efp': True,
        'missing_enabled_return_efp': 'minimal'
    }

    fullans = {'efp': blankefp}
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10i():
    subject = {
        'geom': [0, 0, 0],
        'elem': ['C'],
        'enable_qm': False,
        'enable_efp': True,
        'missing_enabled_return_efp': 'error'
    }

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.from_input_arrays(**subject)


def test_arrays_10j():
    subject = {'geom': [0, 0, 0], 'elem': ['C'], 'enable_qm': True, 'enable_efp': False}

    fullans = {'qm': fullans10qm}
    fullans['qm']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10k():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_qm': 'none'
    }

    fullans = {'efp': fullans10efp}
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10l():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_qm': 'minimal'
    }

    fullans = {'qm': copy.deepcopy(blankqm), 'efp': fullans10efp}
    fullans['qm']['fix_com'] = True
    fullans['qm']['fix_orientation'] = True
    fullans['qm']['fix_symmetry'] = 'c1'
    fullans['qm']['provenance'] = _arrays_prov_stamp
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10m():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': True,
        'missing_enabled_return_qm': 'error'
    }

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.from_input_arrays(**subject)


def test_arrays_10n():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': False,
        'enable_efp': True
    }

    fullans = {'efp': fullans10efp}
    fullans['efp']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_arrays_10o():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': False,
        'missing_enabled_return_qm': 'none'
    }

    fullans = {}

    final = qcelemental.molparse.from_input_arrays(**subject)
    with pytest.raises(KeyError):
        final['qm']
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10p():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': False,
        'missing_enabled_return_qm': 'minimal'
    }

    fullans = {'qm': blankqm}
    fullans['qm']['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_input_arrays(**subject)
    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    with pytest.raises(KeyError):
        final['efp']


def test_arrays_10q():
    subject = {
        'fragment_files': ['cl2'],
        'hint_types': ['xyzabc'],
        'geom_hints': [[0, 0, 0, 0, 0, 0]],
        'enable_qm': True,
        'enable_efp': False,
        'missing_enabled_return_qm': 'error'
    }

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.from_input_arrays(**subject)


def test_strings_10r():
    subject = ''

    final = qcelemental.molparse.from_string(
        subject, enable_qm=True, enable_efp=True, missing_enabled_return_qm='none', missing_enabled_return_efp='none')

    print('final', final)
    with pytest.raises(KeyError):
        final['qm']
    with pytest.raises(KeyError):
        final['efp']


def test_strings_10s():
    subject = ''

    final = qcelemental.molparse.from_string(
        subject,
        enable_qm=True,
        enable_efp=True,
        missing_enabled_return_qm='minimal',
        missing_enabled_return_efp='minimal')

    fullans = {'qm': blankqm, 'efp': blankefp}
    fullans['qm']['provenance'] = _string_prov_stamp
    fullans['efp']['provenance'] = _string_prov_stamp

    assert compare_molrecs(fullans['qm'], final['qm'], tnm() + ': full qm')
    assert compare_molrecs(fullans['efp'], final['efp'], tnm() + ': full efp')


def test_strings_10t():
    subject = ''

    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.from_string(
            subject,
            enable_qm=True,
            enable_efp=True,
            missing_enabled_return_qm='error',
            missing_enabled_return_efp='error')


def test_qmol_11c():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""nocom\n8 0 0 0\n1 1 0 0""", dtype='psi4')
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11d():
    fullans = copy.deepcopy(fullans1a)
    fullans.update({
        'variables': [],
        'geom_unsettled': [['0', '0', '0'], ['1', '0', '0']],
    })
    fullans.pop('geom')
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""nocom\n8 0 0 0\n1 1 0 0""", dtype='psi4+')
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11e():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""2\n\nO 0 0 0 \n1 1 0 0 """, dtype='xyz', fix_com=True)
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11g():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _arrays_prov_stamp

    asdf = qcelemental.molparse.from_arrays(geom=[0., 0., 0., 1., 0., 0.], elez=[8, 1], fix_com=True, verbose=2)
    assert compare_molrecs(fullans, asdf, 4)


def test_qmol_11h():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""nocom\n8 0 0 0\n1 1 0 0""")
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11i():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""nocom\n8 0 0 0\n1 1 0 0""")
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11j():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _string_prov_stamp

    asdf = qcelemental.molparse.from_string("""2\n\nO 0 0 0 \n1 1 0 0 """, fix_com=True)
    assert compare_molrecs(fullans, asdf['qm'], 4)


def test_qmol_11p():
    fullans = copy.deepcopy(fullans1a)
    fullans['provenance'] = _arrays_prov_stamp

    asdf = qcelemental.molparse.from_arrays(geom=[0., 0., 0., 1., 0., 0.], elez=[8, 1], fix_com=True, units='AngSTRom')
    assert compare_molrecs(fullans, asdf, 4)


def test_qmol_11q():
    with pytest.raises(KeyError):
        qcelemental.molparse.from_string("""2\n\nO 0 0 0 \n1 1 0 0 """, fix_com=True, dtype='psi3')


#QCELdef test_qmol_12():
#QCEL    asdf = qcdb.Molecule(geom=[ 0.,  0.,  0.,  1.,  0.,  0.], elez=[8, 1], fix_com=True)
#QCEL    assess_mol_11(asdf, 'qcdb.Molecule(geom, elez)')
#QCEL
#QCEL    import json
#QCEL    smol = json.dumps(asdf.to_dict(np_out=False))
#QCEL    dmol = json.loads(smol)
#QCEL
#QCEL    asdf2 = qcdb.Molecule(dmol)
#QCEL    assess_mol_11(asdf, 'qcdb.Molecule(jsondict)')

subject12 = """
 0 1
 1
 8 1 0.95
 O 2 1.40 1 A
 H 3 0.95 2 A 1 120.0

A = 105.0
"""

fullans12 = {
    'elbl': np.array(['', '', '', '']),
    'elea': np.array([1, 16, 16, 1]),
    'elem': np.array(['H', 'O', 'O', 'H']),
    'elez': np.array([1, 8, 8, 1]),
    'fix_com': False,
    'fix_orientation': False,
    'fragment_charges': [0.0],
    'fragment_multiplicities': [1],
    'fragment_separators': [],
    'geom_unsettled': [[], ['1', '0.95'], ['2', '1.40', '1', 'A'], ['3', '0.95', '2', 'A', '1', '120.0']],
    'mass': np.array([1.00782503, 15.99491462, 15.99491462, 1.00782503]),
    'molecular_charge': 0.0,
    'molecular_multiplicity': 1,
    'real': np.array([True, True, True, True]),
    'units': 'Angstrom',
    'variables': [['A', 105.0]],
    'fix_symmetry': 'c1'
}
ans12 = {
    'elbl': ['1', '8', 'O', 'H'],
    'fragment_charges': [0.0],
    'fragment_files': [],
    'fragment_multiplicities': [1],
    'fragment_separators': [],
    'geom_hints': [],
    'geom_unsettled': [[], ['1', '0.95'], ['2', '1.40', '1', 'A'], ['3', '0.95', '2', 'A', '1', '120.0']],
    'hint_types': [],
    'variables': [('A', '105.0')],
    'fix_symmetry': 'c1'
}


def test_psi4_qm_12a():
    subject = subject12
    fullans = copy.deepcopy(fullans12)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, fix_symmetry='c1')
    assert compare_recursive(ans12, intermed, tnm() + ': intermediate')
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_tooclose_error():
    subject = """2 -1 -1 -1\n2 -1 -1 -1.05"""

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_string(subject)

    assert 'too close' in str(e)


def test_cartbeforezmat_error():
    subject = """He 0 0 0\nHe 1 2"""

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_string(subject)

    assert 'Mixing Cartesian and Zmat' in str(e)


def test_jumbledzmat_error():
    subject = """He\nHe 1 2. 2 100. 3 35.\nHe 1 2."""

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_string(subject)

    assert 'aim for lower triangular' in str(e)


def test_steepzmat_error():
    subject = """He\nHe 1 2.\nHe 1 2. 2 100. 3 35."""

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_string(subject)

    assert 'aim for lower triangular' in str(e)


def test_zmatvar_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            elem=['Rn', 'Rn'],
            variables=[['bond', 2.0, 'badextra']],
            geom_unsettled=[[], ['1', 'bond']])

    assert 'Variables should come in pairs' in str(e)


def test_toomanyfrag_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['ar1', '42AR2'],
            fragment_multiplicities=[3, 3],
            fragment_separators=[1, 2],
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'zero-length fragment' in str(e)


def test_fragsep_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['ar1', '42AR2'],
            fragment_multiplicities=[3, 3],
            fragment_separators=np.array(['1']),
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'unable to perform trial np.split on geometry' in str(e)


def test_cartzmatcart():
    subject = """1 1
# This part is just a normal Cartesian geometry specification for benzene
C          0.710500000000    -0.794637665924    -1.230622098778
C          1.421000000000    -0.794637665924     0.000000000000
C          0.710500000000    -0.794637665924     1.230622098778
C         -0.710500000000    -0.794637665924     1.230622098778
H          1.254500000000    -0.794637665924    -2.172857738095
H         -1.254500000000    -0.794637665924     2.172857738095
C         -0.710500000000    -0.794637665924    -1.230622098778
C         -1.421000000000    -0.794637665924     0.000000000000
H          2.509000000000    -0.794637665924     0.000000000000
H          1.254500000000    -0.794637665924     2.172857738095
H         -1.254500000000    -0.794637665924    -2.172857738095
H         -2.509000000000    -0.794637665924     0.000000000000
# And the hydronium part is specified using a zmatrix, referencing the benzene coordinates
X  1  CC  3  30   2  A2
O  13 R   1  90   2  90
H  14 OH  13 TDA  1  0
H  14 OH  15 TDA  13 A1
H  14 OH  15 TDA  13 -A1
He         3.710500000000    -0.794637665924    -1.230622098778

CC    = 1.421
CH    = 1.088
A1    = 120.0
A2    = 180.0
OH    = 1.05
R     = 4.0
"""

    qcelemental.molparse.from_string(subject)


def test_fixcom_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(elez=[3], molecular_charge=1, geom=[0, 0, 0], fix_com='thanks!')

    assert 'Invalid fix_com' in str(e)


def test_fixori_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(elez=[3], molecular_charge=1, geom=[0, 0, 0], fix_orientation=-1)

    assert 'Invalid fix_orientation' in str(e)


def test_units_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(elez=[3], molecular_charge=1, geom=[0, 0, 0], units='furlong')

    assert 'Invalid molecule geometry units' in str(e)


def test_domain_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(domain='kitten')

    assert 'Topology domain kitten not available' in str(e)


def test_natom_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(elem=['C'], elea=[12, 13], geom=[0, 0, 0])

    assert 'Dimension mismatch natom' in str(e)


def test_incompletefrag_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['ar1', '42AR2'],
            fragment_multiplicities=[3, 3],
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'Fragment quantities given without separation info' in str(e)


def test_badmult_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['ar1', '42AR2'],
            fragment_multiplicities=[-3, 3],
            fragment_separators=np.array([1]),
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'fragment_multiplicities not among None or positive integer' in str(e)


def test_badchg_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['ar1', '42AR2'],
            fragment_charges=[[], {}],
            fragment_separators=np.array([1]),
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'fragment_charges not among None or float' in str(e)


def test_fraglen_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            domain='qmvz',
            speclabel=True,
            elbl=['na', 'cl'],
            fragment_charges=[1, -1, 0],
            fragment_separators=np.array([1]),
            geom_unsettled=[[], ['1', 'bond']],
            hint_types=[],
            units='Bohr',
            variables=[('bond', '3')])

    assert 'mismatch among fragment quantities' in str(e)


def test_zmatfragarr_14a():
    fullans = copy.deepcopy(fullans14)
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        domain='qmvz',
        speclabel=True,
        elbl=['ar1', '42AR2'],
        fragment_multiplicities=[3, 3],
        fragment_separators=[1],
        geom_unsettled=[[], ['1', 'bond']],
        hint_types=[],
        units='Bohr',
        variables=[('bond', '3')])

    assert compare_molrecs(fullans, final, tnm() + ': full')


def test_zmatfragarr_14b():
    fullans = copy.deepcopy(fullans14)
    fullans['elbl'] = ['', '']
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        domain='qmvz',
        speclabel=False,
        elez=[18, 18],
        elea=np.array([40, 42]),
        real=[True, True],
        fragment_multiplicities=[3, 3],
        fragment_separators=[1],
        geom_unsettled=[[], ['1', 'bond']],
        hint_types=[],
        units='Bohr',
        variables=[('bond', '3')])

    assert compare_molrecs(fullans, final, tnm() + ': full')


def test_zmatfragarr_14c():
    fullans = copy.deepcopy(fullans14)
    fullans['elbl'] = ['', '']
    fullans['fix_com'] = True
    fullans['fix_orientation'] = True
    fullans['mass'] = fullans['mass'].tolist()  # other np vs. list diffs are hidden by compare_molrecs
    fullans['real'] = fullans['real'].tolist()
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        np_out=False,
        domain='qmvz',
        speclabel=False,
        elez=[18, 18],
        elea=[40, None],
        mass=[None, 41.96304574],
        real=[True, True],
        fragment_multiplicities=[3, 3],
        fragment_separators=[1],
        geom_unsettled=[[], ['1', 'bond']],
        hint_types=[],
        units='Bohr',
        fix_com=True,
        fix_orientation=True,
        variables=[('bond', '3')])

    assert compare_molrecs(fullans, final, tnm() + ': full')


subject14 = """
        0 3
        ar1
        --
        0 3
        42AR2 1 bond
    units a.u.
        bond =3.0
        """

fullans14 = {
    'elbl': np.array(['1', '2']),
    'elea': np.array([40, 42]),
    'elem': np.array(['Ar', 'Ar']),
    'elez': np.array([18, 18]),
    'fix_com': False,
    'fix_orientation': False,
    'fragment_charges': [0.0, 0.0],
    'fragment_multiplicities': [3, 3],
    'fragment_separators': [1],
    'geom_unsettled': [[], ['1', 'bond']],
    'mass': np.array([39.96238312, 41.96304574]),
    'molecular_charge': 0.0,
    'molecular_multiplicity': 5,
    'real': np.array([True, True]),
    'units': 'Bohr',
    'variables': [['bond', 3.0]]
}


def test_zmatfragstr_14d():
    subject = subject14
    fullans = copy.deepcopy(fullans14)
    fullans['provenance'] = _string_prov_stamp

    final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, verbose=2)
    assert compare_molrecs(fullans, final['qm'], tnm() + ': full')


def test_badprov0_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(geom=[1, 2, 3], elez=[4], provenance='mine')

    assert 'Provenance entry is not dictionary' in str(e)


def test_badprov1_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=[1, 2, 3], elez=[4], provenance={
                'creator': ('psi', 'tuple'),
                'routine': 'buggy',
                'version': '0.1b'
            })

    assert """Provenance key 'creator' should be string of creating program's name:""" in str(e)


def test_badprov2_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=[1, 2, 3],
            elez=[4],
            provenance={
                'creator': '',
                'routine': 'buggy',
                'version': 'my.vanity.version.13'
            })

    assert """Provenance key 'version' should be a valid PEP 440 string:""" in str(e)


def test_badprov3_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=[1, 2, 3], elez=[4], provenance={
                'creator': '',
                'routine': 5,
                'version': '0.1b'
            })

    assert """Provenance key 'routine' should be string of creating function's name:""" in str(e)


def test_badprov4_error():
    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=[1, 2, 3], elez=[4], provenance={
                'creators': '',
                'routine': 'buggy',
                'version': '0.1b'
            })

    assert """Provenance keys (['creator', 'routine', 'version']) incorrect:""" in str(e)


fullans17 = {
    'geom': np.array([0., 1., 2., 3., 4., 5., 6., 7., 8.]),
    'elea': np.array([1, 32, 1]),
    'elez': np.array([1, 16, 1]),
    'elem': np.array(['H', 'S', 'H']),
    'mass': np.array([1.00782503, 31.9720711744, 1.00782503]),
    'real': np.array([False, True, True]),
    'elbl': np.array(['', '', '']),
    'units': 'Bohr',
    'fix_com': False,
    'fix_orientation': False,
    'fragment_separators': [],
    'fragment_charges': [-1.0],
    'fragment_multiplicities': [1],
    'molecular_charge': -1.0,
    'molecular_multiplicity': 1,
    'connectivity': [
        (0, 1, 1.0),
        (1, 2, 1.0),
    ],
}


def test_connectivity_17a():
    fullans = copy.deepcopy(fullans17)
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        geom=np.arange(9),
        units='Bohr',
        elez=[1, 16, 1],
        molecular_charge=-1,
        real=[False, True, True],
        connectivity=[(0, 1, 1), (1, 2, 1)],
    )

    assert compare_molrecs(fullans, final, tnm() + ': full')


def test_connectivity_17b():
    fullans = copy.deepcopy(fullans17)
    fullans['provenance'] = _arrays_prov_stamp

    final = qcelemental.molparse.from_arrays(
        geom=np.arange(9),
        units='Bohr',
        elez=[1, 16, 1],
        molecular_charge=-1,
        real=[False, True, True],
        connectivity=[(2.0, 1, 1), (1, 0, 1)],
    )

    assert compare_molrecs(fullans, final, tnm() + ': full')


def test_connectivity_atindex_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=np.arange(9),
            units='Bohr',
            elez=[1, 16, 1],
            molecular_charge=-1,
            real=[False, True, True],
            connectivity=[(2.1, 1, 1), (1, 0, 1)],
        )

    assert "Connectivity first atom should be int" in str(e)


def test_connectivity_atrange_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=np.arange(9),
            units='Bohr',
            elez=[1, 16, 1],
            molecular_charge=-1,
            real=[False, True, True],
            connectivity=[(2, 1, 1), (1, -1, 1)],
        )

    assert "Connectivity second atom should be int" in str(e)


def test_connectivity_bondorder_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=np.arange(9),
            units='Bohr',
            elez=[1, 16, 1],
            molecular_charge=-1,
            real=[False, True, True],
            connectivity=[(2, 1, 1), (1, 0, 6)],
        )

    assert "Connectivity bond order should be float" in str(e)


def test_connectivity_type_error():

    with pytest.raises(qcelemental.ValidationError) as e:
        qcelemental.molparse.from_arrays(
            geom=np.arange(9),
            units='Bohr',
            elez=[1, 16, 1],
            molecular_charge=-1,
            real=[False, True, True],
            connectivity='wire',
        )

    assert "Connectivity entry is not of form" in str(e)


#'geom_unsettled': [[], ['1', '2.'], ['1', '2.', '2', '100.', '3', '35.']],

#final, intermed = qcelemental.molparse.from_string(subject, return_processed=True, verbose=2)
#import pprint
#pprint.pprint(final)
#pprint.pprint(intermed)

#assert False
