from pydantic import BaseModel, constr
from .common_models import (Model, DriverEnum, ComputeError, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default)
from .molecule import Molecule
from .results import Result
from typing import List


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


class Optimization(OptimizationInput):
    schema_name: constr(strip_whitespace=True,
                        regex=qcschema_optimization_output_default) = qcschema_optimization_output_default
    final_molecule: Molecule
    trajectory: List[Result] = None
    energies: List[float] = None
    success: bool
    error: ComputeError = None
