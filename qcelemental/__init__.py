"""
Main init for QCElemental
"""

from .datum import Datum
from .exceptions import *

# Handle singletons
from .periodic_table import PeriodicTable
from .physical_constants import PhysicalConstants

periodictable = PeriodicTable()
constants = PhysicalConstants()

del PeriodicTable
del PhysicalConstants


# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
