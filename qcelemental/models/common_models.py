from enum import Enum
from typing import Any

import numpy as np
from pydantic import BaseModel, Extra

ndarray_encoder = {np.ndarray: lambda v: v.flatten().tolist()}


class ObjectId(str):
    _valid_hex = set("0123456789abcdef")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if (not isinstance(v, str)) or (len(v) != 24) or (not set(v) <= cls._valid_hex):
            raise TypeError("The string {} is not a valid 24-character hexadecimal ObjectId!".format(v))
        return v


class Provenance(BaseModel):
    creator: str
    version: str = None
    routine: str = None

    class Config:
        extra = Extra.allow


class Model(BaseModel):
    method: str
    basis: str = None

    # basis_spec: BasisSpec = None  # This should be exclusive with basis, but for now will be omitted

    class Config:
        allow_mutation = False
        extra = Extra.allow


class DriverEnum(str, Enum):
    energy = 'energy'
    gradient = 'gradient'
    hessian = 'hessian'


class ComputeError(BaseModel):
    """The type of error message raised"""
    error_type: str  # Error enumeration not yet strict
    error_message: str

    class Config:
        extra = Extra.forbid


class FailedOperation(BaseModel):
    id: str = None
    input_data: Any = None
    success: bool = False
    error: ComputeError

    class Config:
        extra = Extra.allow
        allow_mutation = False
        json_encoders = {**ndarray_encoder}


qcschema_input_default = "qcschema_input"
qcschema_output_default = "qcschema_output"
qcschema_optimization_input_default = "qcschema_optimization_input"
qcschema_optimization_output_default = "qcschema_optimization_output"
qcschema_molecule_default = "qcschema_molecule"
