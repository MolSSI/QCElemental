Changelog
=========

.. X.Y.0 / 2020-MM-DD
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


0.13.0 / 2020-01-DD
------------------

New Features
++++++++++++
- (:pr:`175`) QCElemental works with Python 3.8 at the expense of needing a new 0.10 pint (rather than generic install).

Enhancements
++++++++++++
- (:pr:`172`, :pr:`173`) Contribution workflow improvements, including GitHub Actions checking and ``make format`` guidance.

Bug Fixes
+++++++++
- (:pr:`174`) Fix ``compare_recursive`` for when expected is a list but computed is not.


0.12.0 / 2019-11-13
-------------------

New Features
++++++++++++

Enhancements
++++++++++++
- (:pr:`156`) ``Molecules`` can now be correctly compared with ``==``.
- (:pr:`157`) ``molparse.to_string`` Q-Chem dtype developed. Psi4 dtype now includes label and doesn't have extraneous info for single fragment systems.
- (:pr:`162`) New protocol ``stdout`` added to ``ResultProtocols`` controlling whether ``stdout`` field (which generally
  contains the primary logfile, whether a program writes it to file or stdout) is returned.
- (:pr:`165`) The code base is now Black formatted.

Deprecations
++++++++++++
- (:pr:`156`) ``Molecule.compare`` is deprecated and will be removed in v0.13.0.
- (:pr:`167`, :pr:`168`) ``ResultInput``, ``Result``, ``Optimization`` have been removed in favor of ``AtomicInput``, ``AtomicResult``, and ``OptimizationResult`` and will be removed in v0.13.0.

Bug Fixes
+++++++++
- (:pr:`170`) ``ProtoModel`` subclasses now correctly allow custom ``__repr__`` and ``__str__`` methods.
- (:pr:`164`, :pr:`166`) ``nglview-sdf`` molecule string format now correctly uses correct sdf format widths fixing some issues with very large molecules.


0.11.1 / 2019-10-28
-------------------

Bug Fixes
+++++++++
- (:pr:`152`) Patches ``Molecule.from_file`` and ``Molecule.from_data`` to read XYZ+ format and correctly handle keyword arguments.
   Patches ``Molecule.to_file`` to write XYZ+ format as the default for XYZ and XYZ+ files.

0.11.0 / 2019-10-24
-------------------

Enhancements
++++++++++++
- (:pr:`147`) Updates Pydantic to the 1.0 release and fixes a number of breaking changes.
- (:pr:`148`) Switches from Py3dMoljs to NGLView for molecular visualization due to Jupyter Widget integration.
- (:pr:`149`) Adds statC and Debye to the units registry.

Bug Fixes
+++++++++
- (:pr:`150`) Patches ``which_import`` to correctly handle submodules.

0.10.0 / 2019-10-16
-------------------

Enhancements
++++++++++++
- (:pr:`144`) Allows `which_import` to handle submodules.
- (:pr:`143`) Allow testing complex numbers.


0.9.0 / 2019-10-01
------------------

New Features
++++++++++++
- (:pr:`137`, :pr:`138`) Coordinates can now be output in ``Turbomole`` format in addition to all other formats.
- (:pr:`139`) A wavefunction property have been added to the ``Result`` Model. Adds the ability for Engine and other
  programs to store and fetch wavefunction data.
- (:pr:`140`) ``Protocols`` have been added to ``QCInputSpecification`` which allows data to pre-pruned by different
  specifications. Main intention is to reduce wavefunction data which may be re-computed cheaply rather than storing
  all of it. This does change the input model, so requires a minor version bump.

Enhancements
++++++++++++
- (:pr:`132`) ``BasisSet`` and ``Result``'s documentations have been brought up to the standards of other models.

0.8.0 / 2019-09-13
------------------

New Features
++++++++++++
- (:pr:`123`) QCElemental now passes MyPy!
- (:pr:`127`, :pr:`131`) Adds van der Waals radii data available through ``vdwradii.get(atom)`` function.

Enhancements
++++++++++++

Bug Fixes
+++++++++
- (:pr:`125`) Add back a consistency check that had been optimized out.

0.7.0 / 2019-08-23
------------------

Enhancements
++++++++++++

- (:pr:`118`) Model string representations should be more user friendly and descriptive without overload the
  output.
- (:pr:`119`) The ``molparse.to_string`` keyword-arg ``return_data`` now returns molecule keywords for GAMESS and
  NWChem. The ``models.Molecule.to_string`` can use ``return_data`` now, too.
- (:pr:`120`) Auto documentation tech is now built into the ``ProtoModel`` and does not need
  an external function.

0.6.1 / 2019-08-19
------------------

Bug Fixes
+++++++++

- (:pr:`114`) The Numpy einsum calls reference the top level functions and not core C functions. This fixes an issue
  which can result in NumPy version dependencies.

0.6.0 / 2019-08-14
------------------

New Features
++++++++++++

- (:pr:`85`, :pr:`87`) Msgpack is a new serialization option for Models. Serialization defaults to msgpack when
  available (``conda install msgpack-python [-c conda-forge]``), falling back to JSON otherwise. This results in
  substantial speedups for both serialization and deserialization actions and should be a transparent replacement for
  users within Elemental itself.

Enhancements
++++++++++++

- (:pr:`78`) Molecular alignments can now be aligned on the derivatives of vector components.
- (:pr:`81`) Testing is now operated both on the minimal supported and the latest released versions of dependencies.
- (:pr:`82`) Molecule fragment grouping is now disabled by default to match expected behavior.
- (:pr:`84`) Testing without internet connection should now pass since PubChem testing is skipped with no connection.
- (:pr:`85`) Molecule switches from lists to numpy arrays for internal storage of per-atom fields.
- (:pr:`86`) Molecule performance and memory enhancements through reduced validation times and LRU caching of
  common validations.
- (:pr:`88`, :pr:`109`) The ``Molecule`` Model now has its attributes documented and in an on-the-fly manner derived
  from the Pydantic Schema of those attributes.
- (:pr:`99`, :pr:`100`, :pr:`101`, :pr:`102`, :pr:`103`, :pr:`104`, :pr:`105`, :pr:`106`, :pr:`107`) Various
  documentation, type hints, and small changes.

Bug Fixes
+++++++++

- (:pr:`87`) Molecule objects built from Schema are run through validators for consistency.


0.5.0 / 2019-07-16
------------------

Enhancements
++++++++++++

- (:pr:`76`) Adds a built-in ``Molecule.to_file`` function for easy serialization into ``.numpy``, ``.json``, ``.xyz``,
  ``.psimol``, and ``.psi4`` file formats.

Bug Fixes
+++++++++

- (:pr:`74`) Atom and fragment ordering are preserved when invoking ``get_fragment``.


0.4.2 / 2019-06-13
------------------

New Features
++++++++++++

- (:pr:`70`, :pr:`72`) ``molparse.to_string`` Molpro dtype developed.


0.4.1 / 2019-05-31
------------------

New Features
++++++++++++

Enhancements
++++++++++++

- (:pr:`68`) ``molparse.to_string`` learned parameter ``return_data`` that contains aspects of the
  ``models.Molecule`` not expressible in the string. Implemented for dtypes xyz, cfour, psi4.
- (:pr:`68`) ``Datum`` gained an attribute ``numeric`` that reflects whether arithmetic on ``data``
  is valid. ``Datum``\ s that aren't numeric can now be created by initializing with ``numeric=False``.

Bug Fixes
+++++++++

- (:pr:`66`) Fix tests when `networkx` not installed.
- (:pr:`67`) Fix "unsupported format string passed to numpy.ndarray.__format__" on Mac for ``testing.compare_values``.


0.4.0 / 2019-05-13
------------------

New Features
++++++++++++

- (:pr:`51`) Changes ``models.Molecule`` connectivity to default to `None` rather than an empty list. **WARNING** this
  change alters the hashes produced from the ``Molecule.get_hash`` functionality.
- (:pr:`52`, :pr:`53`) ``models.Molecule`` learned ``nuclear_repulsion_energy``, ``nelectrons``, and
  ``to_string`` functions.
- (:pr:`54`) ``models.ResultProperties`` supports CCSD and CCSD(T) properties.
- (:pr:`56`) Algorithms Kabsch ``molutil.kabsch_align``, Hungarian ``util.linear_sum_assignment``, and Uno ``util.uno``
  added. Utilities to generate random 3D rotations ``util.random_rotation_matrix`` and reindex a NumPy array into
  smaller blocks ``util.blockwise_expand`` added.
- (:pr:`56`) Molecular alignment taking into account displacement, rotation, atom exchange, and mirror symmetry for
  superimposable and differing geometries was added in ``molutil.B787`` (basis NumPy function) and
  ``models.Molecule.align`` (far more convenient). Suitable for QM-sized molecules. Requires addition package
  ``networkx``.
- (:pr:`58`) ``utils`` learned ``which_import`` and ``which`` that provide a path or boolean result
  for locating modules or commands, respectively. These were migrated from QCEngine along with
  ``safe_version`` and ``parse_version`` to colocate the import utilities.
- (:pr:`61`) Add molecular visualization to the ``models.Molecule`` object through the optional 3dMol.js framework.
- (:pr:`65`) ``testing.compare_molrecs`` learned parameter ``relative_geoms='align'`` that lets Molecules pass if
  geometries within a translation and rotation of each other.
- (:pr:`65`) ``testing.compare_recursive`` learned parameter ``forgive`` that is a list of paths that may differ without
  failing the comparison.

Enhancements
++++++++++++

- (:pr:`52`, :pr:`53`) ``molparse.to_string`` NWChem and GAMESS dtypes developed.
- (:pr:`57`) ``molparse.to_string`` learned ``dtype='terachem'`` for writing the separate XYZ file
  required by TeraChem. Angstroms or Bohr allowed, though the latter requires extra in input file.
- (:pr:`60`) ``util.which`` added the Python interpreter path to the default search ``$PATH``.
- (:pr:`62`) Added ``*`` to parameter list of many functions requiring subsequent to be keyword only. Code relying
  heavily on positional arguments may get broken.
- (:pr:`63`) ``util.which`` learned parameter ``env`` to use an alternate search ``$PATH``.
- (:pr:`63`) ``util.which`` and ``util.which_import`` learned parameters ``raise_error`` and ``raise_msg`` which raises
  ``ModuleNotFoundError`` (for both functions) when not located. It error will have a generic error message which can
  be extended by ``raise_msg``. It is strongly encouraged to add specific remedies (like how to install) through this
  parameter. This is the third exit pattern possible from the "which" functions, of which path/None is the default,
  True/error happens when ``raise_error=True``, and True/False happens otherwise when ``return_bool=True``.
- (:pr:`65`) Testing functions ``compare``, ``compare_values``, ``compare_recursive`` learned parameter
  ``return_handler`` that lets other printing, logging, and pass/fail behavior to be interjected.

Bug Fixes
+++++++++

- (:pr:`63`) ``util.which`` uses ``os.pathsep`` rather than Linux-focused ``:``.
- (:pr:`65`) Fixed some minor printing and tolerance errors in molecule alignment.
- (:pr:`65`) ``testing.compare_recursive`` stopped doing ``atol=10**-atol`` for ``atol>=1``, bringing it in line with
  other compare functions.


0.3.3 / 2019-03-12
------------------

Enhancements
++++++++++++

- (:pr:`49`) Precompute some mass number and mass lookups and store on ``qcel.periodic_table``. Also move
  static ``re.compile`` expressions out of fns on to module. Mol validation .127s --> .005s.


0.3.2 / 2019-03-11
------------------

New Features
++++++++++++

- (:pr:`47`) ``models.DriverEnum`` now has a ``derivative_int`` function to return 1 for ``gradient``, etc.,
  for easy math. ``properties`` returns 0.
- (:pr:`47`) Optional ``fix_symmetry`` field in qcschema_molecule was missing from ``models.Molecule`` so
  Pydantic got mad at Psi4. Now calmed.

Enhancements
++++++++++++

- (:pr:`48`) If Molecule object has passed through molparse validation because it was created with a molparse
  constructor (e.g., ``from_string``), save some time by not passing it through again at ``model.Molecule``
  creation time.

Bug Fixes
+++++++++

- (:pr:`48`) Fixed a ``Molecule.get_fragment`` bug where ghosted fragments still asserted charge/multiplicity
  to the validator, which was rightly confused.


0.3.1 / 2019-03-07
------------------

Enhancements
++++++++++++

- (:pr:`37`) Documentation now pulls from the custom QC Archive Sphinx Theme, but can fall back to the standard
  RTD theme. This allows all docs across QCA to appear consistent with each other.
- (:pr:`41`) Conda-build recipe removed to avoid possible confusion for everyone who isn't a Conda-Forge
  recipe maintainer. Tests now rely on the ``conda env`` setups.
- (:pr:`44`) Molecule objects are now always validated against a more rigorous model and fragment multiplicities are
  fixed at the correct times, even when no multiplicities are provided. Molecule defaults to ``dtype=2``.


Bug Fixes
+++++++++

- (:pr:`39`) Fixed ``setup.py`` to call ``pytest`` instead of ``unittest`` when running tests on install
- (:pr:`41`) Pinned a minimum Pytest version to make sure errors are not because of too old of a pytest version


0.3.0 / 2019-02-27
------------------

New Features
++++++++++++

- (:pr:`33`) ``molparse.to_schema`` recognizes ``dtype=2`` in keeping with
  GH:MolSSI/QCSchema#60 with internal ``schema_name=qcschema_molecule`` and
  ``schema_version=2`` fields. ``molparse.from_schema`` recognizes external
  fields (existing functionality), internal fields (dtype=2), and mixed.
- (:pr:`33`) Pydantic molecule model now contains schema_name and schema_version=2 information.
- (:pr:`35`) Models now have an ``extra`` field for extra attributes, no additional base keys are allowed.


Enhancements
++++++++++++

- (:pr:`34`) Converts ``qcel.Datum`` to Pydantic model. Changes:
  (a) comment, doi, glossary fields must be accessed by keyword,
  (b) ``to_dict()`` becomes ``dict()`` and instead of only label, units,
  data fields in dict, now comment, doi, glossary present _if_ non-default,
  (c) complex values no longer list-ified by ``to_dict()``.
- (:pr:`36`) Changelog and Models documentation.

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

- (:pr:`13`) Function ``util.unnp`` that recursively list-ifies ndarray in a dict now handles lists and flattens.


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
- Periodic Table data from NIST SRD144 (c. pre-2015?) collected into ``qcelemental.periodictable`` instance,
  with accessors ``to_Z``, ``to_element``, ``to_E``, ``to_mass``, ``to_A`` (and redundant accessors ``to_mass_number``,
  ``to_atomic_number``, ``to_symbol``, ``to_name``) in ``float`` and ``Decimal`` formats. Also includes functionality
  to write a corresponding "C" header.
- Physical Constants data from NIST SRD121 (CODATA 2014) collected into ``qcelemental.constants`` instance,
  with access through ``qcelemental.constants.Faraday_constant`` (exact capitalization; ``float`` result) or
  ``get`` (free capitalization; ``float`` or ``Decimal`` result). Also includes functionality to write a
  corresponding "C" header.
- ``molparse`` submodule where ``from_string``, ``from_array``, ``from_schema`` constructors parse and rearrange
  (if necessary) and validate molecule topology inputs from the QC and EFP domains into a QCSchema-like
  data structure. Current deficiencies from QCSchema are non-contiguous fragments and "provenance" fields.
  Accessors ``to_string`` and ``to_schema`` are highly customizable.
- A `pint <https://pint.readthedocs.io/en/latest/>`_ context has been built around the NIST physical constants
  data so that ``qcelemental.constants.conversion_factor(from_unit, to_unit)`` uses the QCElemental values
  in its conversions. Resulting ``float`` is within uncertainty range of NIST constants but won't be exact
  for conversions involving multiple fundamental dimensions or ``wavelength -> energy != 1 / (energy -> wavelength)``.
