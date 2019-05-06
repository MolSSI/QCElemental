import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, constr

from ..util import provenance_stamp
from .common_models import (ComputeError, DriverEnum, Model, ndarray_encoder, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default, Provenance)
from .molecule import Molecule
from .results import Result


class QCInputSpecification(BaseModel):
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default
    schema_version: int = 1

    driver: DriverEnum
    model: Model
    keywords: Dict[str, Any] = {}

    extras: Dict[str, Any] = {}

    class Config:
        extra = "forbid"
        allow_mutation = False


class OptimizationInput(BaseModel):
    id: Optional[str] = None
    hash_index: Optional[str] = None
    schema_name: constr(
        strip_whitespace=True, regex=qcschema_optimization_input_default) = qcschema_optimization_input_default
    schema_version: int = 1

    keywords: Dict[str, Any] = {}
    extras: Dict[str, Any] = {}

    input_specification: QCInputSpecification
    initial_molecule: Molecule

    provenance: Provenance = provenance_stamp(__name__)

    class Config:
        extra = "forbid"
        allow_mutation = False
        json_encoders = {**ndarray_encoder}

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))


class Optimization(OptimizationInput):
    schema_name: constr(
        strip_whitespace=True, regex=qcschema_optimization_output_default) = qcschema_optimization_output_default

    final_molecule: Optional[Molecule]
    trajectory: List[Result]
    energies: List[float]

    stdout: Optional[str] = None
    stderr: Optional[str] = None

    success: bool
    error: Optional[ComputeError] = None
    provenance: Provenance

    class Config(OptimizationInput.Config):
        pass
