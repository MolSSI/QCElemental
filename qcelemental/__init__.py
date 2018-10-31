"""
Main init for QCElemental
"""

from .datum import Datum
from .exceptions import (NotAnElementError, ValidationError, MoleculeFormatError, ChoicesError, DataUnavailableError)
from . import molparse

# Handle singletons, not their classes or modules
from .periodic_table import periodictable
from .physical_constants import constants, PhysicalConstantsContext
from .covalent_radii import covalentradii, CovalentRadii
del periodic_table
del physical_constants
del covalent_radii

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
