import pytest

from qcelemental.util import which_import


using_networkx = pytest.mark.skipif(
    which_import('networkx', return_bool=True) is False,
    reason='Not detecting module networkx. Install package if necessary and add to envvar PYTHONPATH')

using_scipy = pytest.mark.skipif(
    which_import('scipy', return_bool=True) is False,
    reason='Not detecting module scipy. Install package if necessary and add to envvar PYTHONPATH')

using_py3dmol = pytest.mark.skipif(
    which_import('py3Dmol', return_bool=True) is False,
    reason='Not detecting module py3Dmol. Install package if necessary and add to envvar PYTHONPATH')
