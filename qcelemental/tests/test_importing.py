import pytest

import os

import qcelemental as qcel


def test_which_import_t():
    ans = qcel.util.which_import('pint')
    assert ans.split(os.path.sep)[-1] == '__init__.py'


def test_which_import_t_bool():
    ans = qcel.util.which_import('pint', return_bool=True)
    assert ans is True


def test_which_import_f():
    ans = qcel.util.which_import('evilpint')
    assert ans is None


def test_which_import_f_bool():
    ans = qcel.util.which_import('evilpint', return_bool=True)
    assert ans is False


def test_which_import_f_raise():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import('evilpint', raise_error=True)

    assert str(e).endswith("Python module 'evilpint' not found in envvar PYTHONPATH.")


def test_which_import_f_raisemsg():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import('evilpint', raise_error=True, raise_msg='Install `evilpint`.')

    assert str(e).endswith("Python module 'evilpint' not found in envvar PYTHONPATH. Install `evilpint`.")


def test_which_t():
    ans = qcel.util.which('ls')
    assert ans.split(os.path.sep)[-1] == 'ls'


def test_which_t_bool():
    ans = qcel.util.which('ls', return_bool=True)
    assert ans is True


def test_which_f():
    ans = qcel.util.which('evills')
    assert ans is None


def test_which_f_bool():
    ans = qcel.util.which('evills', return_bool=True)
    assert ans is False


def test_which_f_raise():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which('evills', raise_error=True)

    assert str(e).endswith("Command 'evills' not found in envvar PATH.")


def test_which_f_raisemsg():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which('evills', raise_error=True, raise_msg='Install `evills`.')

    assert str(e).endswith("Command 'evills' not found in envvar PATH. Install `evills`.")


def test_which_f_raise():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which('evills', raise_error=True)

    assert str(e).endswith("Command 'evills' not found in envvar PATH.")


def test_which_f_raisemsg():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which('evills', raise_error=True, raise_msg='Install `evills`.')

    assert str(e).endswith("Command 'evills' not found in envvar PATH. Install `evills`.")


def test_safe_version():
    assert 'v' + qcel.util.safe_version(qcel.__version__) == qcel.__version__


def test_parse_version():
    import pydantic
    assert qcel.util.parse_version(str(pydantic.VERSION)) >= qcel.util.parse_version("v0.20")
