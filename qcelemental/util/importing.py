import os
import shutil
import sys
from typing import List, Union


def which_import(
    module: str,
    *,
    return_bool: bool = False,
    raise_error: bool = False,
    raise_msg: str = None,
    package: str = None,
    namespace_ok: bool = False,
) -> Union[bool, None, str, List[str]]:
    r"""Tests to see if a Python module is available.

    Returns
    -------
    str or None
        By default, returns `__init__.py`-like path if `module` found or `None` if not.
        For namespace packages and if `namespace_ok=True`, returns the list of pieces locations if `module` found or `None` if not.
    bool
        When `return_bool=True`, returns whether or not found.
        Namespace packages only `True` if `namespace_ok=True`.

    Raises
    ------
    ModuleNotFoundError
        When `raise_error=True` and module not found. Raises generic message plus any `raise_msg`.

    """
    from importlib import util

    try:
        module_spec = util.find_spec(module, package=package)
    except ModuleNotFoundError:
        module_spec = None

    # module_spec.origin is 'namespace' for py36, None for >=py37
    namespace_package = module_spec is not None and module_spec.origin in [None, "namespace"]

    if (module_spec is None) or (namespace_package and not namespace_ok):
        if raise_error:
            raise ModuleNotFoundError(
                f"Python module '{module}' not found in envvar PYTHONPATH.{' ' + raise_msg if raise_msg else ''}"
            )
        elif return_bool:
            return False
        else:
            return None
    else:
        if return_bool:
            return True
        else:
            if namespace_package:
                return module_spec.submodule_search_locations
            else:
                return module_spec.origin


def which(
    command: str, *, return_bool: bool = False, raise_error: bool = False, raise_msg: str = None, env: str = None
) -> Union[bool, None, str]:
    r"""Test to see if a command is available.

    Returns
    -------
    str or None
        By default, returns command path if command found or `None` if not.
        Environment is $PATH or `os.pathsep`-separated `env`, less any None values.
    bool
        When `return_bool=True`, returns whether or not found.

    Raises
    ------
    ModuleNotFoundError
        When `raises_error=True` and command not found. Raises generic message plus any `raise_msg`.

    Notes
    -----

    +-------------+-------------+---------------------------------+---------------------------+
    | return_bool | raise_error | action if found                 | action if not found       |
    +=============+=============+=================================+===========================+
    | F (default) | F (default) | return <path to command> string | return None               |
    +-------------+-------------+---------------------------------+---------------------------+
    | T           | F (default) | return True                     | return False              |
    +-------------+-------------+---------------------------------+---------------------------+
    | F (default) | T           | return <path to command> string | raise ModuleNotFoundError |
    +-------------+-------------+---------------------------------+---------------------------+
    | T           | T           | return True                     | raise ModuleNotFoundError |
    +-------------+-------------+---------------------------------+---------------------------+

    """
    if env is None:
        lenv = {"PATH": os.pathsep + os.environ.get("PATH", "") + os.pathsep + os.path.dirname(sys.executable)}
    else:
        lenv = {"PATH": os.pathsep.join([os.path.abspath(x) for x in env.split(os.pathsep) if x != ""])}
    lenv = {k: v for k, v in lenv.items() if v is not None}

    ans = shutil.which(command, mode=os.F_OK | os.X_OK, path=lenv["PATH"])

    if sys.platform == "win32" and sys.version_info >= (3, 12, 0) and sys.version_info < (3, 12, 1):
        # https://github.com/python/cpython/issues/109590
        if command == "psi4":
            ans = shutil.which("psi4.exe", mode=os.F_OK | os.X_OK, path=lenv["PATH"])
            if ans is None:
                ans = shutil.which("psi4.bat", mode=os.F_OK | os.X_OK, path=lenv["PATH"])

    # secondary check, see https://github.com/MolSSI/QCEngine/issues/292
    local_raise_msg = ""
    if ans and (".pyenv/shims" in ans):
        local_raise_msg += (
            f"Pyenv shim detected; running {ans} and activating a suggested conda environment may provide '{command}'."
        )
        ans = None

    if raise_error and ans is None:
        raise ModuleNotFoundError(
            f"Command '{command}' not found in envvar PATH.{local_raise_msg}{' ' + raise_msg if raise_msg else ''}"
        )

    if return_bool:
        return bool(ans)
    else:
        return ans


def safe_version(*args, **kwargs) -> str:
    """
    Package resources is a very slow load
    """
    import pkg_resources

    version = pkg_resources.safe_version(*args, **kwargs)
    return version


def parse_version(*args, **kwargs):
    """
    Package resources is a very slow load
    """
    import pkg_resources

    return pkg_resources.parse_version(*args, **kwargs)
