import os
import shutil
import sys


def which_import(module, *, return_bool=False):
    """Tests to see if a Python module is available.

    Returns
    -------
    str or None
        By default, returns `__init__.py`-like path if module found or `None` if not.
    bool
        When `return_bool=True`, returns whether or not found.

    """
    import pkgutil
    plug_spec = pkgutil.find_loader(module)

    if plug_spec is None:
        if return_bool:
            return False
        else:
            return None
    else:
        if return_bool:
            return True
        else:
            return plug_spec.path


def which(command, *, return_bool=False):
    """Test to see if a command is available.

    Returns
    -------
    str or None
        By default, returns command path if command found or `None` if not.
        Environment is $PATH, less any None values.
    bool
        When `return_bool=True`, returns whether or not found.

    """
    lenv = {'PATH': ':' + os.environ.get('PATH') + ":" + os.path.dirname(sys.executable)}
    lenv = {k: v for k, v in lenv.items() if v is not None}

    ans = shutil.which(command, mode=os.F_OK | os.X_OK, path=lenv['PATH'])

    if return_bool:
        return bool(ans)
    else:
        return ans


def safe_version(*args, **kwargs):
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
