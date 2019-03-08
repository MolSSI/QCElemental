Install QCElemental
===================

You can install qcelemental with ``conda``, with ``pip``, or by installing from source.

Conda
-----

You can update qcelemental using `conda <https://www.anaconda.com/download/>`_:

.. code-block:: console

    >>> conda install qcelemental -c conda-forge

This installs QCElemental and its dependancies. The qcelemental package is maintained on the
`conda-forge channel <https://conda-forge.github.io/>`_.


Pip
---

To install QCElemental with ``pip`` there are a few options, depending on which
dependencies you would like to keep up to date:

.. code-block:: console

   >>> pip install qcelemental

Install from Source
-------------------

To install QCElemental from source, clone the repository from `github
<https://github.com/molssi/qcelemental>`_:

.. code-block:: console

    >>> git clone https://github.com/MolSSI/QCElemental.git
    >>> cd QCElemental
    >>> python setup.py install

or use ``pip`` for a local install:

.. code-block:: console

    >>> pip install -e .


Testing
-------
QCElemental can be tested using the ``pytest`` package which can be installed via Conda as well:

.. code-block:: console

    >>> conda install pytest -c conda-forge

Once ``pytest`` is installed QCElemental's testing suite can be run by:

.. code-block:: console

    >>> pytest --pyargs qcelemental


QCElemental can also be tested from source with:

.. code-block:: console

    >>> cd QCElemental
    >>> pytest
