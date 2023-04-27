# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

# Handle singletons, not their classes or modules
from . import covalent_radii, models, molparse, molutil, periodic_table, physical_constants, util, vanderwaals_radii
from .datum import Datum
from .exceptions import ChoicesError, DataUnavailableError, MoleculeFormatError, NotAnElementError, ValidationError
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
