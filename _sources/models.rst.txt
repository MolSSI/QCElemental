Overview
========

Python implementations of the `MolSSI QCSchema <https://github.com/MolSSI/QCSchema>`_
are available within QCElemental. These models use `Pydantic <https://pydantic-docs.helpmanual.io>`_
as their base to provide serialization, validation, and manipluation.


Basics
--------

Model creation occurs with a ``kwargs`` constructor as shown by equivalent operations below:

.. code-block:: python

    >>> mol = qcel.models.Molecule(symbols=["He"], geometry=[0, 0, 0])
    >>> mol = qcel.models.Molecule(**{"symbols":["He"], "geometry": [0, 0, 0]})

A list of all available fields can be found by querying the ``fields`` attribute:

.. code-block:: python

    >>> mol.fields.keys()
    dict_keys(['symbols', 'geometry', ..., 'id', 'extras'])

These attributes can be accessed as shown:

.. code-block:: python

    >>> mol.symbols
    ['He']

Note that these models are typically immutable:

.. code-block:: python

    >>> mol.symbols = ["Ne"]
    TypeError: "Molecule" is immutable and does not support item assignment

To update or alter a model the ``copy`` command can be used with the ``update`` kwargs:

.. code-block:: python

    >>> mol.copy(update={"symbols": ["Ne"]})
    <    Geometry (in Angstrom), charge = 0.0, multiplicity = 1:

           Center              X                  Y                   Z
        ------------   -----------------  -----------------  -----------------
        Ne                0.000000000000     0.000000000000     0.000000000000

    >

Serialization
-------------

All models can be serialized back to their dictionary counterparts through the ``dict`` function:

.. code-block:: python

    >>> mol.dict()
    {'symbols': ['He'], 'geometry': array([[0., 0., 0.]])}


JSON representations are supported out of the box for all models:

.. code-block:: python

    >>> mol.json()
    '{"symbols": ["He"], "geometry": [0.0, 0.0, 0.0]}'

Raw JSON can also be parsed back into a model:

.. code-block:: python

    >>> mol.parse_raw(mol.json())
    <    Geometry (in Angstrom), charge = 0.0, multiplicity = 1:

           Center              X                  Y                   Z
        ------------   -----------------  -----------------  -----------------
        He                0.000000000000     0.000000000000     0.000000000000

    >

The standard ``dict`` operation returns all internal representations which may be classes or other complex structures.
To return a JSON-like dictionary the ``dict`` function can be used:

.. code-block:: python

    >>> mol.dict(encoding='json')
    {'symbols': ['He'], 'geometry': [0.0, 0.0, 0.0]}

