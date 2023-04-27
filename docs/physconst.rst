Physical Constants
==================


NIST Physical constants are available from QCElemental with arbitrary
conversion factors using the `pint <https://pint.readthedocs.io/en/latest/>`_
package. The current default physical constants come from the `NIST CODATA
2014 <https://physics.nist.gov/cuu/Constants/>`_.

Conversion Factors
------------------

Conversion factors are available for any valid conversion:

.. code-block:: python

    >>> qcel.constants.conversion_factor("nanometer", "angstrom")
    10.0

    >>> qcel.constants.conversion_factor("eV / nanometer ** 2", "hartree / angstrom ** 2")
    0.00036749322481535707


.. warning::

    QCElemental is explicit: ``kcal`` is quite different from ``kcal / mol``. Be careful of common
    shorthands.

    .. code-block:: python

        >>> qcel.constants.conversion_factor("kcal", "eV")
        2.611447418269555e+22

        >>> qcel.constants.conversion_factor("kcal / mol", "eV")
        0.043364103900593226


Quantities
-----------

QCElemental supports the ``pint`` "values with units" Quantity objects:

.. code-block:: python

    >>> q = qcel.constants.Quantity("5 kcal / mol")
    >>> q
    <Quantity(5, 'kilocalorie')>

    >>> q.magnitude
    5.0

    >>> q.dimensionality
    <UnitsContainer({'[length]': 2.0, '[mass]': 1.0, '[substance]': -1.0, '[time]': -2.0})>

These objects are often used for code that has many different units to make
the requisite bookkeeping nearly effortless. In addition, these objects have
NumPy and Pandas support built-in:

.. code-block:: python

    >>> import numpy as np
    >>> a = qcel.constants.Quantity("kcal") * np.arange(4)
    >>> a
    <Quantity([0 1 2 3], 'kilocalorie')>

An example of array manipulation using a NumPy array with a ``pint`` quantity:

    >>> a * qcel.constants.Quantity("eV")
    <Quantity([0 1 2 3], 'electron_volt * kilocalorie')>

    >>> a.to("eV")
    <Quantity([0.00000000e+00 2.61144742e+22 5.22289484e+22 7.83434225e+22], 'electron_volt')>


NIST CODATA
-----------

The exact values from the NIST CODATA can be queried explicitly:

.. code-block:: python

    >>> qcel.constants.get("hartree energy in ev")
    27.21138602

The complete NIST CODATA record is held and can be obtained via the Python-
API. The following example shows how to obtain a  comprehensive overview of
the individual CODATA record:

.. code-block:: python

    >>> datum = qcel.constants.get("hartree energy in ev", return_tuple=True)
    >>> datum
    <----------------------------------------
           Datum Hartree energy in eV
    ----------------------------------------
    Data:     27.21138602
    Units:    [eV]
    doi:      10.18434/T4WW24
    Comment:  uncertainty=0.000 000 17
    Glossary:
    ---------------------------------------->

Each of these quantities is API accessible:

.. code-block:: python

    >>> datum.doi
    '10.18434/T4WW24'
    >>> datum.comment
    'uncertainty=0.000 000 17'


Contexts
--------

Physical constants are continuously refined over time as experimental precision
increases or redefinition occurs. To prepare for future changes, physical
constants are contained in contexts. The ``qcel.constants`` context will be
updated over time to the latest NIST data. To "pin" a context version, a
specific context can be created like so:


.. code-block:: python

    >>> context = qcel.PhysicalConstantsContext("CODATA2014")
    >>> context.conversion_factor("hartree", "eV")
    27.21138601949571

Currently only ``CODATA2014`` is available.

API
---

.. currentmodule:: qcelemental.constants

Top level user functions:

.. autosummary::
    conversion_factor
    get
    Quantity
    string_representation

Function Definitions
--------------------

.. note:: ``conversion_factor`` is a function, not a class, but cannot be documented in Sphinx as such
           due to the way the LRU Cache wraps it. Please disregard the marking of it being a "class."

.. autoclass:: conversion_factor
   :noindex:

.. autofunction:: get
   :noindex:

.. autofunction:: Quantity
   :noindex:

.. autofunction:: string_representation
   :noindex:
