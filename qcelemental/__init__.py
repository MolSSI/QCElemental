"""
Main init for QCElemental
"""

from .datum import Datum
from .exceptions import (NotAnElementError, ValidationError, MoleculeFormatError, ChoicesError)
from . import units
from . import molparse

# Handle singletons, not their classes or modules
from .periodic_table import periodictable
from .physical_constants import constants, PhysicalConstantsContext
del periodic_table
del physical_constants

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
