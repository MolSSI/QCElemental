Changelog
=========

.. X.Y.0 / 2019-MM-DD
.. ------------------
..
.. New Features
.. ++++++++++++
..
.. Enhancements
.. ++++++++++++
..
.. Bug Fixes
.. +++++++++

0.2.7 / 2019-02-DD
------------------

New Features
++++++++++++

- (:pr:`33`) `molparse.to_schema` recognizes `dtype=2` in keeping with
  GH:MolSSI/QCSchema#60 with internal `schema_name=qcschema_molecule` and
  `schema_version=2` fields. `molparse.from_schema` recognizes external
  fields (existing functionality), internal fields (dtype=2), and mixed.
- (:pr:`33`) Pydantic molecule model now contains schema_name and schema_version=2 information.

Enhancements
++++++++++++

- (:pr:`??`) Converts `qcel.Datum` to Pydantic model. Changes
  (a) comment, doi, glossary fields must be accessed by keyword,
  (b) `to_dict()` becomes `dict()` and instead of label, units, data only,
  now comment, doi, glossary present _if_ non-default,
  (c) complex values no longer list-ified by `to_dict()`.

Bug Fixes
+++++++++


0.2.6 / 2019-02-18
------------------

Bug Fixes
+++++++++

- (:pr:`32`) Updates compliance with Pydantic v0.20.


0.2.5 / 2019-02-13
------------------

Enhancements
++++++++++++

- (:pr:`31`) Lints the code base preparing for a release and minor test improvements.

Bug Fixes
+++++++++

- (:pr:`30`) Fixes ``dihedral`` measurement code for incorrect phase in certain quadrants.

0.2.4 / 2019-02-08
------------------

New Features
++++++++++++

- (:pr:`27`) Adds a new ``measure`` feature to Molecule for distances, angles, and dihedrals.
- (:pr:`25`) Adds a new ``testing`` module which contains testing routines for arrays, dictionaries, and molecules.

Enhancements
++++++++++++

- (:pr:`28`) Reduces loading time from ~1 second to 200 ms by delaying ``pint`` import and ensuring git tags are only computed once.


0.2.3 / 2019-01-29
------------------

Enhancements
++++++++++++

- (:pr:`24`) Update models to be compatible with QCFractal and MongoDB objects in the QCArchive Ecosystem.
  Also enhances the ``Molecule`` model's ``json`` function to accept ``as_dict`` keyword, permitting a return as a
  dictionary of Pydantic-serialized python (primitive) objects, instead of a string.

0.2.2 / 2019-01-28
------------------

Bug Fixes
+++++++++

- (:pr:`21`) Molparse's ``from_schema`` method now correctly parses the new ``qcschema_X`` strings for schema names.
- (:pr:`23`) Pydantic model serializations now correctly handle Numpy Array objects in nested ``BaseModels``. Model serialization testing added to catch these in the future.

0.2.1 / 2019-01-27
------------------

- (:pr:`20`) Moves several Molecule parsing functions to the molparse module.

0.2.0 / 2019-01-25
------------------

- now requires Python 3.6+
- now requires Pydantic

New Features
++++++++++++

- (:pr:`14`, :pr:`16`, :pr:`17`) Added new Pydantic models for Molecules, Results, and Optimizations to make common objects used in the QCArchive project all exist in one central, always imported module.

Enhancements
++++++++++++

- (:pr:`13`) Function `util.unnp` that recursively list-ifies ndarray in a dict now handles lists and flattens.

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

