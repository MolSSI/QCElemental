from pydantic import BaseModel, constr
from .common_models import Model, DriverEnum, \
    QCEngineError, \
    qcschema_input_default, qcschema_optimization_input_default, qcschema_optimization_output_default
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
    error: QCEngineError


class Optimization(FailedOptimization):
    schema_name: constr(strip_whitespace=True,
                        regex=qcschema_optimization_output_default) = qcschema_optimization_output_default
    final_molecule: Molecule
    trajectory: List[Result] = None
    energies: Union[List[float], float] = None
    success: bool
    error: QCEngineError = None



    __json_mapper = {
        "_id": "id",
        "_success": "success",
        "_hash_index": "hash_index",

        # Options
        "_program": "program",
        "_qc_options": "qc_meta",
        "_initial_molecule_id": "initial_molecule",
        "_final_molecule_id": "final_molecule",
        "_trajectory": "trajectory",
        "_energies": "energies",
    }

    """

    json_data = {
        "meta": {
            "procedure": "optimization",
            "option": "default",
            "program": "geometric",
            "qc_meta": {
                "driver": "energy",
                "method": "HF",
                "basis": "sto-3g",
                "options": "default",
                "program": "psi4"
            },
        },
        "data": ["mol_id_1", "mol_id_2", ...],
    }

    qc_schema_input = {
        "schema_name": "qc_schema_input",
        "schema_version": 1,
        "molecule": {
            "geometry": [
                0.0,  0.0, -0.6,
                0.0,  0.0,  0.6,
            ],
            "symbols": ["H", "H"],
            "connectivity": [[0, 1, 1]]
        },
        "driver": "gradient",
        "model": {
            "method": "HF",
            "basis": "sto-3g"
        },
        "keywords": {},
    }
    json_data = {
        "schema_name": "qc_schema_optimization_input",
        "schema_version": 1,
        "keywords": {
            "coordsys": "tric",
            "maxiter": 100,
            "program": "psi4"
        },
        "input_specification": qc_schema_input
    }

    """
