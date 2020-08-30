try:
    import pydantic
except ImportError:  # pragma: no cover
    raise ImportError(
        "Python module pydantic not found. Solve by installing it: "
        "`conda install pydantic -c conda-forge` or `pip install pydantic`"
    )

from . import types
from .align import AlignmentMill
from .basemodels import AutodocBaseSettings, ProtoModel
from .basis import BasisSet
from .common_models import ComputeError, DriverEnum, FailedOperation, Provenance
from .molecule import Molecule
from .procedures import OptimizationInput, OptimizationResult
from .procedures import Optimization  # scheduled for removal
from .results import AtomicInput, AtomicResult, AtomicResultProperties
from .results import Result, ResultInput, ResultProperties  # scheduled for removal


def qcschema_models():
    return [
        AtomicInput,
        AtomicResult,
        AtomicResultProperties,
        BasisSet,
        Molecule,
        Provenance,
    ]
