from enum import Enum
from typing import Any, Dict, Optional

import numpy as np
from pydantic import Schema

from .basemodels import ProtoModel

# Encoders, to be deprecated
ndarray_encoder = {np.ndarray: lambda v: v.flatten().tolist()}


class Provenance(ProtoModel):
    creator: str
    version: Optional[str] = None
    routine: Optional[str] = None

    class Config(ProtoModel.Config):
        extra = "allow"


class Model(ProtoModel):
    """
    The quantum chemistry model specification for a given operation to compute against
    """
    method: str = Schema(
        ...,
        description="The quantum chemistry method to evaluate (e.g., B3LYP, PBE, ...)."
    )
    basis: Optional[str] = Schema(
        None,
        description="The quantum chemistry basis set to evaluate (e.g., 6-31g, cc-pVDZ, ...). Can be ``None`` for "
                    "methods without basis sets."
    )

    # basis_spec: BasisSpec = None  # This should be exclusive with basis, but for now will be omitted

    class Config(ProtoModel.Config):
        extra = "allow"


class DriverEnum(str, Enum):
    energy = 'energy'
    gradient = 'gradient'
    hessian = 'hessian'
    properties = 'properties'

    def derivative_int(self):
        egh = ['energy', 'gradient', 'hessian', 'third', 'fourth', 'fifth']
        if self == 'properties':
            return 0
        else:
            return egh.index(self)


class ComputeError(ProtoModel):
    """The type of error message raised"""
    error_type: str = Schema(  # Error enumeration not yet strict
        ...,
        description="The type of error which was thrown. Restrict this field short classifiers e.g. 'input_error'."
    )
    error_message: str = Schema(
        ...,
        description="Text associated with the thrown error, often the backtrace, but can contain additional "
                    "information as well."
    )
    extras: Optional[Dict[str, Any]] = Schema(
        None,
        description="Additional data to ship with the ComputeError object."
    )

class FailedOperation(ProtoModel):
    """
    A record indicating that a given operation (compute, procedure, etc.) has failed and contains the reason and
    input data which generated the failure.
    
    """
    id: str = Schema(
        None,
        description="A unique identifier which links this FailedOperation, often of the same Id of the operation "
                     "should it have been successful. This will often be set programmatically by a database such as "
                      "Fractal."
    )
    input_data: Any = Schema(
        None,
        description="The input data which was passed in that generated this failure. This should be the complete "
                    "input which when attempted to be run, caused the operation to fail."
    )
    success: bool = Schema(
        False,
        description="A boolean indicator that the operation failed consistent with the model of successful operations. "
                    "Should always be False. Allows programmatic assessment of all operations a"
    )
    error: ComputeError = Schema(
        ...,
        description="A container which has details of the error that failed this operation. See the "
                    ":class:`ComputeError` for more details."
    )
    extras: Optional[Dict[str, Any]] = Schema(
        None,
        description="Additional information to bundle with this Failed Operation. Details which pertain specifically "
                    "to a thrown error should be contained in the `error` field. See :class:`ComputeError` for details."
    )


qcschema_input_default = "qcschema_input"
qcschema_output_default = "qcschema_output"
qcschema_optimization_input_default = "qcschema_optimization_input"
qcschema_optimization_output_default = "qcschema_optimization_output"
qcschema_molecule_default = "qcschema_molecule"
