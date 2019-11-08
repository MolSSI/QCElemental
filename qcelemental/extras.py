"""
Misc information and runtime information.
"""

from . import _version

__all__ = ["get_information"]

versions = _version.get_versions()

__info = {"version": versions["version"], "git_revision": versions["full-revisionid"]}


def get_information(key: str):
    """
    Obtains a variety of runtime information about QCElemental.
    """
    key = key.lower()
    if key not in __info:
        raise KeyError(f"Information key '{key}' not understood.")

    return __info[key]
