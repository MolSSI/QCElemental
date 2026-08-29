import os

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


@pytest.fixture
def namespace_module(tmp_path, monkeypatch):
    namespace_module = tmp_path / "namespacemodule"
    namespace_module.mkdir()
    monkeypatch.syspath_prepend(str(tmp_path))
    return namespace_module


def test_which_import_t_namespacemodule(namespace_module):
    ans = qcel.util.which_import("namespacemodule", namespace_ok=True)
    assert len(ans) == 1
    assert str(next(iter(ans))) == str(namespace_module)


def test_which_import_t_bool_namespacemodule(namespace_module):
    ans = qcel.util.which_import("namespacemodule", return_bool=True, namespace_ok=True)
    assert ans is True


def test_which_import_f_namespacemodule(namespace_module):
    ans = qcel.util.which_import("namespacemodule", namespace_ok=False)
    assert ans is None


def test_which_import_f_bool_namespacemodule(namespace_module):
    ans = qcel.util.which_import("namespacemodule", return_bool=True, namespace_ok=False)
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
    assert ans.split(os.path.sep)[-1] in ["ls", "ls.EXE"]


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


def test_parse_version():
    v = qcel.util.parse_version("5.3.1")
    assert str(v) == "5.3.1"


@pytest.mark.parametrize(
    "inp,out",
    [
        ("5.3.1", "5.3.1"),
        ("30 SEP 2023 (R2)", "30.SEP.2023.-R2-"),
        ("7.0.0+N/A", "7.0.0-N-A"),
    ],
)
def test_safe_version(inp, out):
    v = qcel.util.safe_version(inp)
    assert v == out
