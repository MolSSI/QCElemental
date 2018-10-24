Install QCElemental
===================

You can install qcelemental with ``conda``, with ``pip``, or by installing from source.

Conda
-----

.. note:: 
    Work in progress.

You can update qcelemental using `conda <https://www.anaconda.com/download/>`_::

    conda install qcelemental -c conda-forge

This installs QCElemental and its dependancies.

The qcelemental package is maintained on the
`conda-forge channel <https://conda-forge.github.io/>`_.


Pip
---

To install QCElemental with ``pip`` there are a few options, depending on which
dependencies you would like to keep up to date:

*   ``pip install qcelemental``

Install from Source
-------------------

To install QCElemental from source, clone the repository from `github
<https://github.com/molssi/qcelemental>`_::

    git clone https://github.com/MolSSI/QCElemental.git
    cd QCElemental
    python setup.py install

or use ``pip`` for a local install::

    pip install -e .


Test
----

Test QCElemental with ``py.test``::

    cd QCElemental
    py.test
