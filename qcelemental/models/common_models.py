from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import numpy as np
from pydantic import Field

from .basemodels import ProtoModel
from .basis import BasisSet

if TYPE_CHECKING:
    from pydantic.typing import ReprArgs


# Encoders, to be deprecated
ndarray_encoder = {np.ndarray: lambda v: v.flatten().tolist()}


class Model(ProtoModel):
    """The computational molecular sciences model to run."""

    method: str = Field(  # type: ignore
        ...,
        description="The quantum chemistry method to evaluate (e.g., B3LYP, PBE, ...). "
        "For MM, name of the force field.",
    )
    basis: Optional[Union[str, BasisSet]] = Field(  # type: ignore
        None,
        description="The quantum chemistry basis set to evaluate (e.g., 6-31g, cc-pVDZ, ...). Can be ``None`` for "
        "methods without basis sets. For molecular mechanics, name of the atom-typer.",
    )

    # basis_spec: BasisSpec = None  # This should be exclusive with basis, but for now will be omitted

    class Config(ProtoModel.Config):
        canonical_repr = True
        extra: str = "allow"


class DriverEnum(str, Enum):
    """Allowed computation driver values."""

    energy = "energy"
    gradient = "gradient"
    hessian = "hessian"
    properties = "properties"

    def derivative_int(self):
        egh = ["energy", "gradient", "hessian", "third", "fourth", "fifth"]
        if self == "properties":
            return 0
        else:
            return egh.index(self)


class ComputeError(ProtoModel):
    """Complete description of the error from an unsuccessful program execution."""

    error_type: str = Field(  # type: ignore
        ...,  # Error enumeration not yet strict
        description="The type of error which was thrown. Restrict this field to short classifiers e.g. 'input_error'. Suggested classifiers: https://github.com/MolSSI/QCEngine/blob/master/qcengine/exceptions.py",
    )
    error_message: str = Field(  # type: ignore
        ...,
        description="Text associated with the thrown error. This is often the backtrace, but it can contain additional "
        "information as well.",
    )
    extras: Optional[Dict[str, Any]] = Field(  # type: ignore
        None,
        description="Additional information to bundle with the error.",
    )

    class Config:
        repr_style = ["error_type", "error_message"]

    def __repr_args__(self) -> "ReprArgs":
        return [("error_type", self.error_type), ("error_message", self.error_message)]
