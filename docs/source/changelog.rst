Changelog
=========

.. X.Y.0 / 2018-MM-DD
.. -------------------
..
.. New Features
.. ++++++++++++
..
.. Enhancements
.. ++++++++++++
..
.. Bug Fixes
.. +++++++++

0.1.3 / 2018-12-14
------------------

New Features
++++++++++++

- (:pr:`12`) Adds "connectivity" validation and storage consistent with QCSchema.

Enhancements
++++++++++++

- (:pr:`12`) Adds single dictionary provenance consistent with `QCSchema <https://github.com/MolSSI/QCSchema/blob/master/qcschema/dev/definitions.py#L23-L41>`_ rather than previous list o'dicts.

0.1.2 / 2018-11-3
-----------------

New Features
++++++++++++

- (:pr:`10`) Adds covalent radii data available through ``covalentradii.get(atom)`` function.
- (:pr:`10`) Adds ``to_units(unit)`` to ``Datum`` class to access the data in non-native units.
- (:pr:`10`) Adds ``periodictable.to_period(atom)`` and ``to_group(atom)`` functions to address periodic table.

0.1.1 / 2018-10-30
------------------

New Features
++++++++++++

- (:pr:`7`, :pr:`9`) Adds "comment" and "provenance" fields to internal repr to better match QCSchema.
- (:pr:`7`) Adds provenance stamp to ``from_string``, ``from_arrays``, ``from_schema`` functions.

Enhancements
++++++++++++

- (:pr:`7`) Adds outer schema_name/schema_version to ``to_schema(..., dtype=1)`` output so is inverse to ``from_schema``.

Bug Fixes
+++++++++

- (:pr:`8`) Tests pass for installed module now that comparison tests are xfail.

0.1.0a / 2018-10-24
-------------------

This is the first alpha release of QCElemental containing the primary three components.

New Features
++++++++++++

- (:pr:`6`) Updated molparse to write new Molecule QCSchema fields in keeping with GH:MolSSI/QCSchema#44
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
- A `pint <https://pint.readthedocs.io/en/latest/>`_ context has been built around the NIST physical constants
  data so that `qcelemental.constants.conversion_factor(from_unit, to_unit)` uses the QCElemental values
  in its conversions. Resulting `float` is within uncertainty range of NIST constants but won't be exact
  for conversions involving multiple fundamental dimensions or ``wavelength -> energy != 1 / (energy -> wavelength)``.

