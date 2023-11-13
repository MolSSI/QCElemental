# QCElemental

[![Build Status](https://github.com/MolSSI/QCElemental/workflows/CI/badge.svg?branch=master)](https://github.com/MolSSI/QCElemental/actions?query=workflow%3ACI)
[![codecov](https://img.shields.io/codecov/c/github/MolSSI/QCElemental.svg?logo=Codecov&logoColor=white)](https://codecov.io/gh/MolSSI/QCElemental)
[![Documentation Status](https://img.shields.io/github/actions/workflow/status/MolSSI/QCElemental/CI.yaml?label=docs&logo=readthedocs&logoColor=white)](https://molssi.github.io/QCElemental/)
[![Chat on Slack](https://img.shields.io/badge/chat-on_slack-green.svg?longCache=true&style=flat&logo=slack)](https://join.slack.com/t/qcarchive/shared_invite/enQtNDIzNTQ2OTExODk0LTE3MWI0YzBjNzVhNzczNDM0ZTA5MmQ1ODcxYTc0YTA1ZDQ2MTk1NDhlMjhjMmQ0YWYwOGMzYzJkZTM2NDlmOGM)
![python](https://img.shields.io/badge/python-3.7+-blue.svg)

**Documentation:** [GitHub Pages](https://molssi.github.io/QCElemental/)

Core data structures for Quantum Chemistry. QCElemental also contains physical constants and periodic table data from NIST and molecule handlers.

Periodic Table and Physical Constants data are pulled from NIST srd144 and srd121, respectively ([details](raw_data/README.md)) in a renewable manner (class around NIST-published JSON file).

This project also contains a generator, validator, and translator for [Molecule QCSchema](https://molssi-qc-schema.readthedocs.io/en/latest/auto_topology.html).

## ✨ Getting Started

- Installation. QCElemental supports Python 3.7+.

  ```sh
  python -m pip install qcelemental
  ```

- To install QCElemental with molecule visualization capabilities (useful in iPython or Jupyter notebook environments):

  ```sh
  python -m pip install 'qcelemental[viz]`
  ```

- To install QCElemental with various alignment capabilities using `networkx`

  ```sh
  python -m pip install 'qcelemental[align]`
  ```

- Or install both:

  ```sh
  python -m pip install 'qcelemental[viz,align]`
  ```

- See [documentation](https://molssi.github.io/QCElemental/)

### Periodic Table

A variety of periodic table quantities are available using virtually any alias:

```python
>>> import qcelemental as qcel
>>> qcel.periodictable.to_E('KRYPTON')
'Kr'
>>> qcel.periodictable.to_element(36)
'Krypton'
>>> qcel.periodictable.to_Z('kr84')
36
>>> qcel.periodictable.to_A('Kr')
84
>>> qcel.periodictable.to_A('D')
2
>>> qcel.periodictable.to_mass('kr', return_decimal=True)
Decimal('83.9114977282')
>>> qcel.periodictable.to_mass('kr84')
83.9114977282
>>> qcel.periodictable.to_mass('Kr86')
85.9106106269
```

### Physical Constants

Physical constants can be acquired directly from the [NIST CODATA](https://physics.nist.gov/cuu/Constants/Table/allascii.txt):

```python
>>> import qcelemental as qcel
>>> qcel.constants.Hartree_energy_in_eV
27.21138602
>>> qcel.constants.get('hartree ENERGY in ev')
27.21138602
>>> pc = qcel.constants.get('hartree ENERGY in ev', return_tuple=True)
>>> pc.label
'Hartree energy in eV'
>>> pc.data
Decimal('27.21138602')
>>> pc.units
'eV'
>>> pc.comment
'uncertainty=0.000 000 17'
```

Alternatively, with the use of the [Pint unit conversion package](https://pint.readthedocs.io/en/latest/), arbitrary
conversion factors can be obtained:

```python
>>> qcel.constants.conversion_factor("bohr", "miles")
3.2881547429884475e-14
```

### Covalent Radii

Covalent radii are accessible for most of the periodic table from [Alvarez, Dalton Transactions (2008) doi:10.1039/b801115j](https://doi.org/10.1039/b801115j) ([details](qcelemental/data/alvarez_2008_covalent_radii.py.py)).

```python
>>> import qcelemental as qcel
>>> qcel.covalentradii.get('I')
2.626719314386381
>>> qcel.covalentradii.get('I', units='angstrom')
1.39
>>> qcel.covalentradii.get(116)
Traceback (most recent call last):
...
qcelemental.exceptions.DataUnavailableError: ('covalent radius', 'Lv')
>>> qcel.covalentradii.get(116, missing=4.0)
4.0
>>> qcel.covalentradii.get('iodine', return_tuple=True).dict()
{'numeric': True, 'label': 'I', 'units': 'angstrom', 'data': Decimal('1.39'), 'comment': 'e.s.d.=3 n=451', 'doi': 'DOI: 10.1039/b801115j'}
```

### van der Waals Radii

Van der Waals radii are accessible for most of the periodic table from [Mantina, J. Phys. Chem. A (2009) doi: 10.1021/jp8111556](https://pubs.acs.org/doi/10.1021/jp8111556) ([details](qcelemental/data/mantina_2009_vanderwaals_radii.py)).

```python
>>> import qcelemental as qcel
>>> qcel.vdwradii.get('I')
3.7416577284064996
>>> qcel.vdwradii.get('I', units='angstrom')
1.98
>>> qcel.vdwradii.get(116)
Traceback (most recent call last):
...
qcelemental.exceptions.DataUnavailableError: ('vanderwaals radius', 'Lv')
>>> qcel.vdwradii.get('iodine', return_tuple=True).dict()
{'numeric': True, 'label': 'I', 'units': 'angstrom', 'data': Decimal('1.98'), 'doi': 'DOI: 10.1021/jp8111556'}
```
