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
    # Hack to get test_safe_version test passed
    # TODO: Versioning is a mess in repo. Fix with simple best practice at some point.
    info = __info[key]
    if key == "version" and not info.startswith("v"):
        info = f"v{info}"
    return info
