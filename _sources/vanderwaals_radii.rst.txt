van der Waals Radii
===================

Access van der Waals Radii information within QCElemental.

.. code-block:: python

    >>> qcel.vdwradii.get(6)
    3.212534413278308
    >>> qcel.vdwradii.get("C")
    3.212534413278308
    >>> qcel.vdwradii.get("C12")
    3.212534413278308
    >>> qcel.vdwradii.get("Carbon")
    3.212534413278308


Contexts
--------

To prepare for future changes, van der waals radii
are contained in contexts. The ``qcel.vdwradii`` context will be
updated over time to the latest data. To "pin" a context version, a
specific context can be created like so:

.. code-block:: python

    >>> context = qcel.VanderWaalsRadii("MANTINA2009")
    >>> qcel.vdwradii.get(6)
    3.212534413278308

Currently only ``MANTINA2009`` is available.


API
---

.. currentmodule:: qcelemental.vdwradii

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
