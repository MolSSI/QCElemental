"""
Main init for QCElemental
"""

from . import models, molparse, molutil, util
from .covalent_radii import CovalentRadii, covalentradii
from .datum import Datum
from .exceptions import ChoicesError, DataUnavailableError, MoleculeFormatError, NotAnElementError, ValidationError
# Handle versioneer
from .extras import get_information
# Handle singletons, not their classes or modules
from .periodic_table import periodictable
from .physical_constants import PhysicalConstantsContext, constants
from .testing import compare, compare_recursive, compare_values

del periodic_table
del physical_constants
del covalent_radii

__version__ = get_information('version')
__git_revision__ = get_information('git_revision')
del get_information
