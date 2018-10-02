<p align="center">
<br>
<!-- Commit -->
<a href="https://travis-ci.org/MolSSI/QCElemental"><img src="https://travis-ci.org/MolSSI/QCElemental.svg?branch=master"></a>
<a href="https://codecov.io/gh/MolSSI/QCElemental"> <img src="https://codecov.io/gh/MolSSI/QCElemental/branch/master/graph/badge.svg" /></a>
<br>
<!-- Release & PR Activity -->
<a href="https://github.com/MolSSI/QCElemental/releases"> <img src="https://img.shields.io/github/release/MolSSI/QCElemental.svg" /></a>
<a href="https://github.com/MolSSI/QCElemental/releases"> <img src="https://img.shields.io/github/release-date/MolSSI/QCElemental.svg" /></a>
<a href="https://github.com/MolSSI/QCElemental/releases"> <img src="https://img.shields.io/github/commits-since/MolSSI/QCElemental/latest.svg" /></a>
<a href="https://github.com/MolSSI/QCElemental/graphs/contributors"> <img src="https://img.shields.io/github/commit-activity/y/MolSSI/QCElemental.svg" /></a>
<br>
<!-- Supported -->
<a href="https://opensource.org/licenses/BSD-3-Clause"> <img src="https://img.shields.io/github/license/MolSSI/QCElemental.svg" /></a>
<!--<a href="#"> <img src="https://img.shields.io/badge/Platforms-Linux%2C%20MacOS%2C%20Windows%20WSL-orange.svg" /></a>-->
<a href="#"> <img src="https://img.shields.io/badge/python-3.5%2C%203.6%2C%203.7-blue.svg" /></a>
<br>
<!-- Project/Communication -->
<!--<a href="http://psicode.org/pylibefpmanual/master/index.html"> <img src="https://img.shields.io/badge/docs-latest-5077AB.svg" /></a>-->
<a href="https://join.slack.com/t/qcarchive/shared_invite/enQtNDIzNTQ2OTExODk0LWM3OTgxN2ExYTlkMTlkZjA0OTExZDlmNGRlY2M4NWJlNDlkZGQyYWUxOTJmMzc3M2VlYzZjMjgxMDRkYzFmOTE"> <img src="https://img.shields.io/badge/chat-on_slack-808493.svg" /></a>
<br>
<!-- Obtain -->
<!--<a href="https://anaconda.org/psi4/pylibefp"> <img src="https://anaconda.org/psi4/pylibefp/badges/installer/conda.svg" /></a>
<a href="https://anaconda.org/psi4/pylibefp"> <img src="https://anaconda.org/psi4/pylibefp/badges/platforms.svg" /> </a>
<a href="https://anaconda.org/psi4/pylibefp"> <img src="https://anaconda.org/psi4/pylibefp/badges/version.svg" /> </a>
<a href="https://anaconda.org/psi4/pylibefp"> <img src="https://anaconda.org/psi4/pylibefp/badges/latest_release_relative_date.svg" /> </a>-->
<br><br>
</p>

# QCElemental

A Python interface to Periodic Table and Physical Constants data from
a reliable source (NIST srd144 and srd121, respectively;
[details](nist_data/README.md)) in a renewable
manner (class around NIST-published JSON file).

## Demo

### periodic table
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

### physical constants ([available](https://physics.nist.gov/cuu/Constants/Table/allascii.txt))
```python
>>> import qcelemental as qcel
>>> qcel.constants.Hartree_energy_in_eV
27.21138602
>>> qcel.constants.get('hartree ENERGY in ev')
27.21138602
>>> pc = qcel.constants.get('hartree ENERGY in ev', return_tuple=True)
>>> pc.lbl
'Hartree energy in eV'
>>> pc.data
Decimal('27.21138602')
>>> pc.units
'eV'
>>> pc.comment
'uncertainty=0.000 000 17'
```

