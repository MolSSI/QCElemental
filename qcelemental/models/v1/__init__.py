"""
Safety shim for QCSchema v1 imports.

This module intentionally avoids importing v1 model internals eagerly. If the
Pydantic v1 compatibility layer (``pydantic.v1``) is available we will try to
re-export the real classes. Otherwise this module exposes placeholder classes
that emit a deprecation warning on import and raise a clear RuntimeError when
an attempt is made to instantiate any v1 model.

This keeps top-level imports (e.g. `import qcelemental`) clean while making
explicit `from qcelemental.models.v1 import Molecule` usable (it will return a
placeholder that raises on construction).
"""

from __future__ import annotations

import importlib
import sys
import warnings
from typing import List

_MSG = (
    "qcelemental.models.v1 is active but incompatible with Python 3.14+ "
    "(pydantic.v1 is not available). Imports will provide non-functional placeholders; "
    "instantiating any v1 model will raise a RuntimeError. Please run on Python < 3.14 "
    "or migrate to qcelemental.models.v2. See docs/MIGRATION.md"
)

# Warn on import so users see the incompatibility when they explicitly import v1
# Use FutureWarning (visible by default) so users notice the issue during import
warnings.warn(_MSG, FutureWarning, stacklevel=2)


def _make_placeholder(name: str):
    """Create a placeholder class for a v1 model.

    The class is importable (so `from ... import Name` works) but raises a
    RuntimeError on instantiation with an actionable message.
    """
    _MSG2 = (
        f"QCSchema v1 model '{name}' cannot be instantiated in this environment. "
        + "Reason: pydantic.v1 is unavailable on Python 3.14+. "
        + "Use qcelemental.models.v2 or run Python <3.14. See docs/MIGRATION.md"
    )

    def __init__(self, *args, **kwargs):
        raise RuntimeError(_MSG2)

    def __repr__(self):
        return f"<Unavailable QCSchema v1 model {name}>"

    def from_data(self, *args, **kwargs):
        raise RuntimeError(_MSG2)

    def from_file(self, *args, **kwargs):
        raise RuntimeError(_MSG2)

    if name == "Molecule":
        return type(
            name, (), {"__init__": __init__, "__repr__": __repr__, "from_data": from_data, "from_file": from_file}
        )
    else:
        return type(name, (), {"__init__": __init__, "__repr__": __repr__})


# Names this module should export (keeps parity with the previous file layout)
_EXPORT_NAMES = [
    "AlignmentMill",
    "AutodocBaseSettings",
    "ProtoModel",
    "BasisCenter",
    "BasisSet",
    "ECPPotential",
    "ElectronShell",
    "ECPType",
    "HarmonicType",
    "ComputeError",
    "DriverEnum",
    "FailedOperation",
    "Model",
    "Provenance",
    "Identifiers",
    "Molecule",
    "Optimization",
    "OptimizationInput",
    "OptimizationProtocols",
    "OptimizationResult",
    "OptimizationSpecification",
    "QCInputSpecification",
    "TDKeywords",
    "TrajectoryProtocolEnum",
    "TorsionDriveInput",
    "TorsionDriveResult",
    "Result",
    "ResultInput",
    "ResultProperties",
    "AtomicInput",
    "AtomicResult",
    "AtomicResultProperties",
    "AtomicResultProtocols",
    "WavefunctionProperties",
    "Array",
    "ErrorCorrectionProtocol",
    "WavefunctionProtocolEnum",
    "NativeFilesProtocolEnum",
]


def _use_real_if_possible():
    """Attempt to import and re-export real v1 symbols when pydantic.v1 is present.

    Falls back silently to placeholders on any error.
    """
    # Note: can't test on `import pydantic.v1` b/c it's not necessarily functional
    if sys.version_info >= (3, 14):
        return False

    # Map where names are defined in the original layout. Import cautiously.
    mapping = {
        "AlignmentMill": (".align", "AlignmentMill"),
        "AutodocBaseSettings": (".basemodels", "AutodocBaseSettings"),
        "ProtoModel": (".basemodels", "ProtoModel"),
        "BasisCenter": (".basis", "BasisCenter"),
        "BasisSet": (".basis", "BasisSet"),
        "ECPPotential": (".basis", "ECPPotential"),
        "ElectronShell": (".basis", "ElectronShell"),
        "ECPType": (".basis", "ECPType"),
        "HarmonicType": (".basis", "HarmonicType"),
        "ComputeError": (".common_models", "ComputeError"),
        "DriverEnum": (".common_models", "DriverEnum"),
        "FailedOperation": (".common_models", "FailedOperation"),
        "Model": (".common_models", "Model"),
        "Provenance": (".common_models", "Provenance"),
        "Identifiers": (".molecule", "Identifiers"),
        "Molecule": (".molecule", "Molecule"),
        "Optimization": (".procedures", "Optimization"),
        "OptimizationInput": (".procedures", "OptimizationInput"),
        "OptimizationProtocols": (".procedures", "OptimizationProtocols"),
        "OptimizationResult": (".procedures", "OptimizationResult"),
        "OptimizationSpecification": (".procedures", "OptimizationSpecification"),
        "QCInputSpecification": (".procedures", "QCInputSpecification"),
        "TDKeywords": (".procedures", "TDKeywords"),
        "TrajectoryProtocolEnum": (".procedures", "TrajectoryProtocolEnum"),
        "TorsionDriveInput": (".procedures", "TorsionDriveInput"),
        "TorsionDriveResult": (".procedures", "TorsionDriveResult"),
        "Result": (".results", "Result"),
        "ResultInput": (".results", "ResultInput"),
        "ResultProperties": (".results", "ResultProperties"),
        "AtomicInput": (".results", "AtomicInput"),
        "AtomicResult": (".results", "AtomicResult"),
        "AtomicResultProperties": (".results", "AtomicResultProperties"),
        "AtomicResultProtocols": (".results", "AtomicResultProtocols"),
        "WavefunctionProperties": (".results", "WavefunctionProperties"),
        "ErrorCorrectionProtocol": (".results", "ErrorCorrectionProtocol"),
        "WavefunctionProtocolEnum": (".results", "WavefunctionProtocolEnum"),
        "NativeFilesProtocolEnum": (".results", "NativeFilesProtocolEnum"),
        "Array": (".types", "Array"),
    }

    pkg = __name__.rsplit(".", 1)[0]

    for name, (submod, attr) in mapping.items():
        try:
            module = importlib.import_module(submod, package="qcelemental.models.v1")
            value = getattr(module, attr)
            globals()[name] = value
        except Exception:
            # Leave placeholder if anything goes wrong
            globals()[name] = _make_placeholder(name)

    return True


# First create placeholders for all names so imports always succeed
for _n in _EXPORT_NAMES:
    globals()[_n] = _make_placeholder(_n)


# Then attempt to shadow them with real implementations when available
_use_real_if_possible()


def qcschema_models() -> List[type]:
    """Return the list of QCSchema v1 model types exposed by this module.

    The returned classes may be real v1 models or placeholders that raise on
    instantiation depending on environment.
    """

    return [
        globals()[n]
        for n in ("AtomicInput", "AtomicResult", "AtomicResultProperties", "BasisSet", "Molecule", "Provenance")
    ]


# this is sensible but leads to:
#   AttributeError: module 'qcelemental.models' has no attribute 'basis'
# __all__ = _EXPORT_NAMES + ["qcschema_models"]
