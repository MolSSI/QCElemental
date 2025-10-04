# These are QCSchema v1 data layouts formed from Pydantic API v2 syntax.
# They are here as internal stopgaps for identifying QCSchema v1 models
#   and so that v1 dictionaries can be returned.
#   Use them internally if you absolutely must, but
#   DO NOT RETURN THESE OBJECT IN THE WILD!

from .atomic import (
    AtomicInput,
    AtomicResult,
    AtomicResultProtocols,
    WavefunctionProperties,
)
from .basis_set import BasisSet
from .failed_operation import FailedOperation
from .molecule import Molecule
