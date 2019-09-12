"""
Main init for QCElemental
"""

from . import models, molparse, molutil, util
from .datum import Datum
from .exceptions import ChoicesError, DataUnavailableError, MoleculeFormatError, NotAnElementError, ValidationError
# Handle versioneer
from .extras import get_information
# Handle singletons, not their classes or modules
from . import covalent_radii, vanderwaals_radii, periodic_table, physical_constants
# from .physical_constants import PhysicalConstantsContext, constants
from .testing import compare, compare_recursive, compare_values

# Expose singletons from the modules
periodictable = periodic_table.periodictable
PhysicalConstantsContext = physical_constants.PhysicalConstantsContext
constants = physical_constants.constants
CovalentRadii = covalent_radii.CovalentRadii
covalentradii = covalent_radii.covalentradii
VanderWaalsRadii = vanderwaals_radii.VanderWaalsRadii
vdwradii = vanderwaals_radii.vdwradii

# Remove singleton-providing modules from known imported objects
del periodic_table
del physical_constants
del covalent_radii
del vanderwaals_radii

__version__ = get_information('version')
__git_revision__ = get_information('git_revision')
del get_information
