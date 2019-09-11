van der Waals Radii
===================

Access van der Waals Radii information within QCElemental.

.. code-block:: python

    >>> qcel.vanderwaalsradii.get(6)
    3.212534413278308
    >>> qcel.vanderwaalsradii.get("C")
    3.212534413278308
    >>> qcel.vanderwaalsradii.get("C12")
    3.212534413278308
    >>> qcel.vanderwaalsradii.get("Carbon")
    3.212534413278308


Contexts
--------

To prepare for future changes, van der waals radii
are contained in contexts. The ``qcel.vanderwaalsradii`` context will be
updated over time to the latest data. To "pin" a context version, a
specific context can be created like so:

.. code-block:: python

    >>> context = qcel.VanderwaalsRadii("MANTINA2009")
    >>> qcel.vanderwaalsradii.get(6)
    3.212534413278308

Currently only ``MANTINA2009`` is available.


API
---

.. currentmodule:: qcelemental.vanderwaalsradii

Top level user functions:

.. autosummary::
    get
    string_representation

Function Definitions
--------------------

.. autofunction:: get

.. autofunction:: string_representation
