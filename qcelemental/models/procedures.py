from pydantic import BaseModel, constr, Extra
from .common_models import (Model, DriverEnum, ComputeError, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default, ndarray_encoder)
from .molecule import Molecule
from .results import Result
from typing import Any, Dict, List


class QCInputSpecification(BaseModel):
    driver: DriverEnum
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default
    schema_version: int = 1
    model: Model
    keywords: Dict[str, Any] = {}

    class Config:
        extra = Extra.allow
        allow_mutation = False


class OptimizationInput(BaseModel):
    schema_name: constr(
        strip_whitespace=True, regex=qcschema_optimization_input_default) = qcschema_optimization_input_default
    schema_version: int = 1
    keywords: Dict[str, Any] = {}
    input_specification: QCInputSpecification
    initial_molecule: Molecule

    class Config:
        extra = Extra.allow
        allow_mutation = False
        json_encoders = {**ndarray_encoder}

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))


class Optimization(OptimizationInput):
    id: str = None
    schema_name: constr(
        strip_whitespace=True, regex=qcschema_optimization_output_default) = qcschema_optimization_output_default
    final_molecule: Molecule
    trajectory: List[Result] = None
    energies: List[float] = None
    success: bool
    error: ComputeError = None

    class Config(OptimizationInput.Config):
        pass

    def dict(self, *args, **kwargs):
        if self.id is None:
            excl = kwargs.setdefault("exclude", [])
            if isinstance(excl, list):
                excl.append("id")
            elif isinstance(excl, set):
                excl |= {"id"}

        return super().dict(*args, **kwargs)
