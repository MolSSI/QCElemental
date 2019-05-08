import os
import shutil
import sys
from typing import Union


def which_import(module: str, *, return_bool: bool = False, raise_error: bool = False,
                 raise_msg: str = None) -> Union[bool, None, str]:
    """Tests to see if a Python module is available.

    Returns
    -------
    str or None
        By default, returns `__init__.py`-like path if module found or `None` if not.
    bool
        When `return_bool=True`, returns whether or not found.

    Raises
    ------
    ModuleNotFoundError
        When `raises_error=True` and module not found. Raises generic message plus any `raise_msg`.

    """
    import importlib
    module_spec = importlib.util.find_spec(module)

    if module_spec is None:
        if raise_error:
            raise ModuleNotFoundError(
                f"Python module '{module}' not found in envvar PYTHONPATH.{' ' + raise_msg if raise_msg else ''}")
        elif return_bool:
            return False
        else:
            return None
    else:
        if return_bool:
            return True
        else:
            return module_spec.origin


def which(command: str, *, return_bool: bool = False, raise_error: bool = False,
          raise_msg: str = None, env: str = None) -> Union[bool, None, str]:
    """Test to see if a command is available.

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

    """
    if env is None:
        lenv = {'PATH': os.pathsep + os.environ.get('PATH', '') + os.path.dirname(sys.executable)}
    else:
        lenv = {'PATH': os.pathsep.join([os.path.abspath(x) for x in env.split(os.pathsep) if x != ''])}
    lenv = {k: v for k, v in lenv.items() if v is not None}

    ans = shutil.which(command, mode=os.F_OK | os.X_OK, path=lenv['PATH'])

    if raise_error and ans is None:
        raise ModuleNotFoundError(
            f"Command '{command}' not found in envvar PATH.{' ' + raise_msg if raise_msg else ''}")

    if return_bool:
        return bool(ans)
    else:
        return ans


def safe_version(*args, **kwargs) -> str:
    """
    Package resources is a very slow load
    """
    import pkg_resources
    return pkg_resources.safe_version(*args, **kwargs)


def parse_version(*args, **kwargs):
    """
    Package resources is a very slow load
    """
    import pkg_resources
    return pkg_resources.parse_version(*args, **kwargs)
