from pydantic import BaseModel, constr
from .common_models import (Model, DriverEnum, ComputeError, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default)
from .molecule import Molecule
from .results import Result, FailedResult
from typing import List, Union, Any


class InputSpecification(BaseModel):
    id: str = None
    driver: DriverEnum
    schema_name: constr(strip_whitespace=True,
                        regex=qcschema_input_default) = qcschema_input_default
    schema_version: int = 1
    model: Model = None
    keywords: dict = {}

    class Config:
        allow_extra = True
        allow_mutation = False


class OptimizationInput(BaseModel):
    id: str = None
    schema_name: constr(strip_whitespace=True,
                        regex=qcschema_optimization_input_default) = qcschema_optimization_input_default
    schema_version: int = 1
    keywords: dict = {}
    input_specification: InputSpecification
    initial_molecule: Molecule

    class Config:
        allow_extra = True
        allow_mutation = False


class FailedOptimization(OptimizationInput):
    schema_name: Any = None
    final_molecule: Any = None
    trajectory: Union[List[FailedResult], Any] = None
    energies: Any = None
    success: bool = False
    error: ComputeError


class Optimization(FailedOptimization):
    schema_name: constr(strip_whitespace=True,
                        regex=qcschema_optimization_output_default) = qcschema_optimization_output_default
    final_molecule: Molecule
    trajectory: List[Result] = None
    energies: List[float] = None
    success: bool
    error: ComputeError = None
