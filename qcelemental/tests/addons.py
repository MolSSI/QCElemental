import pytest


def which_import(plug, return_bool=False):
    """Tests to see if a Python module is available.

    Returns
    -------
    str or None
        By default, returns `__init__.py`-like path if module found or `None` if not.
    bool
        When `return_bool=True`, returns whether or not found.

    """
    import pkgutil
    plug_spec = pkgutil.find_loader(plug)

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


using_networkx = pytest.mark.skipif(
    which_import('networkx', return_bool=True) is False,
    reason='Not detecting module networkx. Install package if necessary and add to envvar PYTHONPATH')
