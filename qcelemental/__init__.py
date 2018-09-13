"""
Main init for QCElemental
"""

from .chemistry import periodictable
from .datum import Datum
from .exceptions import *
from .physics import constants

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
