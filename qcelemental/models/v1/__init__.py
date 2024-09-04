try:
    import pydantic
except ImportError:  # pragma: no cover
    raise ImportError(
        "Python module pydantic not found. Solve by installing it: "
        "`conda install pydantic -c conda-forge` or `pip install pydantic`"
    )

from . import types
from .align import AlignmentMill
from .basemodels import AutodocBaseSettings  # remove when QCFractal merges `next`
from .basemodels import ProtoModel
from .basis import BasisSet
from .common_models import ComputeError, DriverEnum, FailedOperation, Provenance
from .molecule import Molecule
from .procedures import Optimization  # scheduled for removal
from .procedures import OptimizationInput, OptimizationResult
from .results import Result  # scheduled for removal
from .results import ResultInput  # scheduled for removal
from .results import ResultProperties  # scheduled for removal
from .results import AtomicInput, AtomicResult, AtomicResultProperties


def qcschema_models():
    return [
        AtomicInput,
        AtomicResult,
        AtomicResultProperties,
        BasisSet,
        Molecule,
        Provenance,
    ]
