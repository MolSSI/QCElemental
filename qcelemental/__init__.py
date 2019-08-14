"""
Main init for QCElemental
"""

from .datum import Datum
from .exceptions import (NotAnElementError, ValidationError, MoleculeFormatError, ChoicesError, DataUnavailableError)
from .testing import (compare, compare_values, compare_recursive)
from . import molparse
from . import molutil
from . import models
from . import util

# Handle singletons, not their classes or modules
from .periodic_table import periodictable
from .physical_constants import constants, PhysicalConstantsContext
from .covalent_radii import covalentradii, CovalentRadii
del periodic_table
del physical_constants
del covalent_radii

# Handle versioneer
from .extras import get_information
__version__ = get_information('version')
__git_revision__ = get_information('git_revision')
del get_information
