try:
    import pydantic
except ImportError:  # pragma: no cover
    raise ImportError(
        "Python module pydantic not found. Solve by installing it: "
        "`conda install pydantic -c conda-forge` or `pip install pydantic`"
    )

from . import types
from .align import AlignmentMill
from .basemodels import (
    AutodocBaseSettings,
    ProtoModel,
    Provenance,
)  # remove AutodocBaseSettings when QCFractal merges `next`
from .basis import BasisSet
from .common_models import ComputeError, DriverEnum
from .molecule import Molecule
from .procedures import OptimizationInput, OptimizationResult, FailedOperation, TorsionDriveInput, TorsionDriveResult
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
