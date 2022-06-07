Periodic Table
==============

Full access to the periodic table is also available within QCElemental. This
includes mass, atomic number, symbol, and name information. Data is indexed
many ways so that many possible aliases can lead to a single quantity. For
example, to obtain the mass (in a.m.u) of of Carbon atomic number, symbol,
isotope symbol, and name can all be passed:

.. code-block:: python

    >>> qcel.periodictable.to_mass(6)
    12.0
    >>> qcel.periodictable.to_mass("C")
    12.0
    >>> qcel.periodictable.to_mass("C12")
    12.0
    >>> qcel.periodictable.to_mass("Carbon")
    12.0

A variety of infomation can be accessed in this manner. Taking 'Carbon' as an example for mass information:

.. code-block:: python

    >>> qcel.periodictable.to_mass("Carbon")
    12.0
    >>> qcel.periodictable.to_mass_number("Carbon")
    12
    >>> qcel.periodictable.to_atomic_number("Carbon")
    6

Symbol information:

.. code-block:: python

    >>> qcel.periodictable.to_symbol("Carbon")
    'C'
    >>> qcel.periodictable.to_name("Carbon")
    'Carbon'

Table position information:

    >>> qcel.periodictable.to_period("Carbon")
    2
    >>> qcel.periodictable.to_group("Carbon")
    14

API
---

.. currentmodule:: qcelemental.periodictable

Top level user functions:

.. autosummary::
    to_mass
    to_mass_number
    to_atomic_number
    to_symbol
    to_name
    to_period
    to_group

Function Definitions
--------------------

.. autofunction:: to_mass
   :noindex:

.. autofunction:: to_mass_number
   :noindex:

.. autofunction:: to_atomic_number
   :noindex:

.. autofunction:: to_symbol
   :noindex:

.. autofunction:: to_name
   :noindex:

.. autofunction:: to_period
   :noindex:

.. autofunction:: to_group
   :noindex:
