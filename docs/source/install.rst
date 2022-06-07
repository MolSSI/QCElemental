Install QCElemental
===================

You can install qcelemental with ``conda`` or with ``pip``.

Conda
-----

You can install qcelemental using `conda <https://www.anaconda.com/download/>`_:

.. code-block:: console

    >>> conda install qcelemental -c conda-forge

This installs QCElemental and its dependencies. The qcelemental package is maintained on the
`conda-forge channel <https://conda-forge.github.io/>`_.


Pip
---

You can also install QCElemental using ``pip``:

.. code-block:: console

   >>> pip install qcelemental


Test the Installation
---------------------

You can test to make sure that QCElemental is installed correctly by first installing ``pytest``.

From ``conda``:

.. code-block:: console

   >>> conda install pytest -c conda-forge

From ``pip``:

.. code-block:: console

   >>> pip install pytest

Then, run the following command:

.. code-block::

   >>> pytest --pyargs qcelemental


Developing from Source
----------------------

If you are a developer and want to make contributions to QCElemental, you can access the source code from
`github <https://github.com/molssi/qcelemental>`_.
