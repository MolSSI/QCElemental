Covalent Radii
==============

Access Covalent Radii information within QCElemental.

.. code-block:: python

    >>> qcel.covalentradii.get(6)
    1.4361918553479494
    >>> qcel.covalentradii.get("C")
    1.4361918553479494
    >>> qcel.covalentradii.get("C12")
    1.4361918553479494
    >>> qcel.covalentradii.get("Carbon")
    1.4361918553479494

Contexts
--------

To prepare for future changes, covalent radii
are contained in contexts. The ``qcel.covalentradii`` context will be
updated over time to the latest data. To "pin" a context version, a
specific context can be created like so:

.. code-block:: python

    >>> context = qcel.CovalentRadii("ALVAREZ2008")
    >>> qcel.covalentradii.get(6)
    1.4361918553479494

Currently only ``ALVAREZ2008`` is available.


API
---

.. currentmodule:: qcelemental.covalentradii

Top level user functions:

.. autosummary::
    get
    string_representation

Function Definitions
--------------------

.. autofunction:: get
   :noindex:

.. autofunction:: string_representation
   :noindex:
