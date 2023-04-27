.. qcelemental documentation master file, created by
   sphinx-quickstart on Wed May 30 19:16:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===========
QCElemental
===========

*QCElemental is a resource module for quantum chemistry containing physical
constants and periodic table data from NIST and molecule handlers.*

Physical Constants
------------------

Physical constants can be acquired directly from the NIST CODATA:

.. code-block:: python

    >>> qcel.constants.get("hartree energy in ev")
    27.21138602

Alternatively, with the use of the Pint unit conversion package, arbitrary
conversion factors can be obtained:

.. code-block:: python

    >>> qcel.constants.conversion_factor("bohr", "miles")
    3.2881547429884475e-14

Periodic Table Data
-------------------

A variety of periodic table quantities are available using virtually any alias:

.. code-block:: python

    >>> qcel.periodictable.to_mass("Ne")
    19.9924401762

    >>> qcel.periodictable.to_mass(10)
    19.9924401762

Molecule Handlers
-----------------

Molecules can be translated to/from the `MolSSI QCSchema
<https://github.com/MolSSI/QCSchema>`_ format or quantum chemistry
program specific input specifications such as NWChem, Psi4, and CFour. In
addition, databases such as PubChem can be searched:

.. code-block:: python

    >>> qcel.molparse.from_string("pubchem:benzene")
        Searching PubChem database for benzene (single best match returned)
        Found 1 result(s)
        {"geometry": ...}

========

Index
-----

**Getting Started**

* :doc:`install`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Getting Started

   install

**Quantities**

* :doc:`physconst`
* :doc:`periodic_table`
* :doc:`covalent_radii`
* :doc:`vanderwaals_radii`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Quantities

   physconst
   periodic_table
   covalent_radii
   vanderwaals_radii

**QCSchema Models**

Implementation descriptions of QCSchema objects in Python.

* :doc:`models`
* :doc:`model_molecule`
* :doc:`model_result`
* :doc:`model_common`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: QCSchema Models

   models
   model_molecule
   model_result
   model_common

**Developer Documentation**

Contains in-depth developer documentation and API references.

* :doc:`api`
* :doc:`changelog`

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation
   :hidden:

   api
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
