Molecule
========

A Python implementation of the `MolSSI QCSchema
<https://github.com/MolSSI/QCSchema>`_ ``Molecule`` object.
There are many definitions of ``Molecule`` depending on the domain; this particular
``Molecule`` is an immutable 3D Cartesian representation with support for
quantum chemistry constructs.


Creation
---------

A Molecule can be created using the normal kwargs fashion as shown below:

.. code-block:: python

    >>> mol = qcel.models.Molecule(**{"symbols": ["He"], "geometry": [0, 0, 0]})

In addition, there is the ``from_data`` attribute to create a molecule from standard strings:

.. code-block:: python

    >>> mol = qcel.models.Molecule.from_data("He 0 0 0")
    >>> mol
    <    Geometry (in Angstrom), charge = 0.0, multiplicity = 1:

           Center              X                  Y                   Z
        ------------   -----------------  -----------------  -----------------
        He                0.000000000000     0.000000000000     0.000000000000
    >

Identifiers
-----------

A number of unique identifiers are automatically created for each molecule.
Additional implementation such as InChI and SMILES are actively being looked
into.

Molecular Hash
++++++++++++++

A molecule hash is automatically created to allow each molecule to be uniquely
identified. The following keys are used to generate the hash:

- ``symbols``
- ``masses`` (1.e-6 tolerance)
- ``molecular_charge`` (1.e-4 tolerance)
- ``molecular_multiplicity``
- ``real``
- ``geometry`` (1.e-8 tolerance)
- ``fragments``
- ``fragment_charges`` (1.e-4 tolerance)
- ``fragment_multiplicities``
- ``connectivity``

Hashes can be acquired from any molecule object and a ``FractalServer``
automatically generates canonical hashes when a molecule is added to the
database.

.. code-block:: python

    >>> mol = qcel.models.Molecule(**{"symbols": ["He", "He"], "geometry": [0, 0, -3, 0, 0, 3]})
    >>> mol.get_hash()
    '84872f975d19aafa62b188b40fbadaf26a3b1f84'

Molecular Formula
+++++++++++++++++

The molecular formula is also available sorted in alphabetical order with
title case symbol names. Any symbol with a count of one does not have a number
associated with it.

.. code-block:: python

    >>> mol.get_molecular_formula()
        'He2'

Fragments
---------

A Molecule with fragments can be created either using the ``--`` separators in
the ``from_data`` function or by passing explicit fragments in the
``Molecule`` constructor:

.. code-block:: python

    >>> mol = qcel.models.Molecule.from_data(
    >>>       """
    >>>       Ne 0.000000 0.000000 0.000000
    >>>       --
    >>>       Ne 3.100000 0.000000 0.000000
    >>>       units au
    >>>       """)

    >>> mol = qcel.models.Molecule(
    >>>       geometry=[0, 0, 0, 3.1, 0, 0],
    >>>       symbols=["Ne", "Ne"],
    >>>       fragments=[[0], [1]]
    >>>       )

Fragments from a molecule containing fragment information can be acquired by:

.. code-block:: python

    >>> mol.get_fragment(0)
    <    Geometry (in Angstrom), charge = 0.0, multiplicity = 1:

           Center              X                  Y                   Z
        ------------   -----------------  -----------------  -----------------
        Ne                0.000000000000     0.000000000000     0.000000000000
    >

Obtaining fragments with ghost atoms is also supported:

.. code-block:: python

    >>> mol.get_fragment(0, 1)
    <    Geometry (in Angstrom), charge = 0.0, multiplicity = 1:

           Center              X                  Y                   Z
        ------------   -----------------  -----------------  -----------------
        Ne                0.000000000000     0.000000000000     0.000000000000
        Ne      (Gh)      3.100000000572     0.000000000000     0.000000000000
    >

API
---

.. autopydantic_model:: qcelemental.models.Molecule
   :noindex:

