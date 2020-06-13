import os
import sys
from pathlib import Path

import pytest

import qcelemental as qcel


def test_which_import_t():
    ans = qcel.util.which_import("pint")
    assert ans.split(os.path.sep)[-1] == "__init__.py"


def test_which_import_t_bool():
    ans = qcel.util.which_import("pint", return_bool=True)
    assert ans is True


def test_which_import_f():
    ans = qcel.util.which_import("evilpint")
    assert ans is None


def test_which_import_f_bool():
    ans = qcel.util.which_import("evilpint", return_bool=True)
    assert ans is False


def test_which_import_f_raise():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import("evilpint", raise_error=True)

    assert str(e.value).endswith("Python module 'evilpint' not found in envvar PYTHONPATH.")


def test_which_import_f_raisemsg():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import("evilpint", raise_error=True, raise_msg="Install `evilpint`.")

    assert str(e.value).endswith("Python module 'evilpint' not found in envvar PYTHONPATH. Install `evilpint`.")


def test_which_import_t_submodule():
    ans = qcel.util.which_import("pint.util")
    assert ans.split(os.path.sep)[-1] == "util.py"


def test_which_import_t_submodule_altsyntax():
    ans = qcel.util.which_import(".util", package="pint")
    assert ans.split(os.path.sep)[-1] == "util.py"


def test_which_import_t_bool_submodule():
    ans = qcel.util.which_import("pint.util", return_bool=True)
    assert ans is True


def test_which_import_f_submodule():
    ans = qcel.util.which_import("evilpint.util")
    assert ans is None


def test_which_import_f_submodule_altsyntax():
    ans = qcel.util.which_import(".util", package="evilpint")
    assert ans is None


def test_which_import_f_bool_submodule():
    ans = qcel.util.which_import("evilpint.util", return_bool=True)
    assert ans is False


def test_which_import_t_namespacemodule():
    testdir = Path(__file__).parent
    sys.path.append(str(testdir))  # brings to Py's notice a non-Py dir that qualifies as a namespace package
    ans = qcel.util.which_import("namespacemodule", namespace_ok=True)
    sys.path.pop()
    assert len(ans) == 1
    assert str(next(iter(ans))) == str(testdir / "namespacemodule")


def test_which_import_t_bool_namespacemodule():
    sys.path.append(str(Path(__file__).parent))
    ans = qcel.util.which_import("namespacemodule", return_bool=True, namespace_ok=True)
    sys.path.pop()
    assert ans is True


def test_which_import_f_namespacemodule():
    sys.path.append(str(Path(__file__).parent))
    ans = qcel.util.which_import("namespacemodule", namespace_ok=False)
    sys.path.pop()
    assert ans is None


def test_which_import_f_bool_namespacemodule():
    sys.path.append(str(Path(__file__).parent))
    ans = qcel.util.which_import("namespacemodule", return_bool=True, namespace_ok=False)
    sys.path.pop()
    assert ans is False


def test_which_import_f_raise_submodule():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import("evilpint.util", raise_error=True)

    assert str(e.value).endswith("Python module 'evilpint.util' not found in envvar PYTHONPATH.")


def test_which_import_f_raisemsg_submodule():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which_import("evilpint.util", raise_error=True, raise_msg="Install `evilpint`.")

    assert str(e.value).endswith("Python module 'evilpint.util' not found in envvar PYTHONPATH. Install `evilpint`.")


def test_which_t():
    ans = qcel.util.which("ls")
    assert ans.split(os.path.sep)[-1] == "ls"


def test_which_t_bool():
    ans = qcel.util.which("ls", return_bool=True)
    assert ans is True


def test_which_f():
    ans = qcel.util.which("evills")
    assert ans is None


def test_which_f_bool():
    ans = qcel.util.which("evills", return_bool=True)
    assert ans is False


def test_which_f_raise():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which("evills", raise_error=True)

    assert str(e.value).endswith("Command 'evills' not found in envvar PATH.")


def test_which_f_raisemsg():
    with pytest.raises(ModuleNotFoundError) as e:
        qcel.util.which("evills", raise_error=True, raise_msg="Install `evills`.")

    assert str(e.value).endswith("Command 'evills' not found in envvar PATH. Install `evills`.")


def test_safe_version():
    assert "v" + qcel.util.safe_version(qcel.__version__) == qcel.__version__


def test_parse_version():
    import pydantic

    assert qcel.util.parse_version(str(pydantic.VERSION)) >= qcel.util.parse_version("v0.20")
