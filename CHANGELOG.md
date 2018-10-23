Changelog
=========

X.Y.0 / 2018-MM-DD
-------------------

#### New Features

#### Enhancements

#### Bug Fixes

0.3 / 2018-10-DD
-------------------

This is the first alpha release of QCElemental containing the primary three components.

#### New Features

- Periodic Table data from NIST SRD144 (c. pre-2015?) collected into `qcelemental.periodictable` instance,
  with accessors `to_Z`, `to_element`, `to_E`, `to_mass`, `to_A` (and redundant accessors `to_mass_number`,
  `to_atomic_number`, to_symbol`, `to_name`) in `float` and `Decimal` formats. Also includes functionality
  to write a corresponding "C" header.
- Physical Constants data from NIST SRD121 (CODATA 2014) collected into `qcelemental.constants` instance,
  with access through `qcelemental.constants.Faraday_constant` (exact capitalization; `float` result) or
  `get` (free capitalization; `float` or `Decimal` result). Also includes functionality to write a
  corresponding "C" header.
- `molparse` submodule where `from_string`, `from_array`, `from_schema` constructors parse and rearrange
  (if necessary) and validate molecule topology inputs from the QC and EFP domains into a QCSchema-like
  data structure. Current deficiencies from QCSchema are non-contiguous fragments and "provenance" fields.
  Accessors `to_string` and `to_schema` are highly customizable.
- A [pint](https://pint.readthedocs.io/en/latest/) context has been built around the NIST physical constants
  data so that `qcelemental.constants.conversion_factor(from_unit, to_unit)` uses the QCElemental values
  in its conversions. Resulting `float` is within uncertainty range of NIST constants but won't be exact
  for conversions involving multiple fundamental dimensions or ``wavelength -> energy != 1 / (energy -> wavelength)``.

