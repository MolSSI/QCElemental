from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Tuple, Union

try:
    from typing import Literal
except ImportError:
    # remove when minimum py38
    from typing_extensions import Literal

import numpy as np
from pydantic import Field, field_validator

from .basemodels import ProtoModel, qcschema_draft
from .basis import BasisSet

if TYPE_CHECKING:
    ReprArgs = Sequence[Tuple[Optional[str], Any]]


def provenance_json_schema_extra(schema, model):
    schema["$schema"] = qcschema_draft


class Provenance(ProtoModel):
    """Provenance information."""

    creator: str = Field(..., description="The name of the program, library, or person who created the object.")
    version: str = Field(
        "",
        description="The version of the creator, blank otherwise. "
        "This should be sortable by the very broad `PEP 440 <https://www.python.org/dev/peps/pep-0440/>`_.",
    )
    routine: str = Field("", description="The name of the routine or function within the creator, blank otherwise.")

    model_config = ProtoModel._merge_config_with(
        canonical_repr=True, json_schema_extra=provenance_json_schema_extra, extra="allow"
    )


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
    model_config = ProtoModel._merge_config_with(canonical_repr=True, extra="allow")


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
        description="The type of error which was thrown. Restrict this field to short classifiers e.g. 'input_error'. "
        "Suggested classifiers: https://github.com/MolSSI/QCEngine/blob/master/qcengine/exceptions.py",
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

    model_config = ProtoModel._merge_config_with(repr_style=["error_type", "error_message"])

    def __repr_args__(self) -> "ReprArgs":
        return [("error_type", self.error_type), ("error_message", self.error_message)]


class FailedOperation(ProtoModel):
    """
    Record indicating that a given operation (program, procedure, etc.) has failed
    and containing the reason and input data which generated the failure.
    """

    schema_name: Literal["qcschema_failed_operation"] = Field(
        "qcschema_failed_operation",
        description=(
            f"The QCSchema specification this model conforms to. Explicitly fixed as qcschema_failed_operation."
        ),
    )
    schema_version: Literal[2] = Field(
        2,
        description="The version number of :attr:`~qcelemental.models.FailedOperation.schema_name` to which this model conforms.",
    )
    id: Optional[str] = Field(  # type: ignore
        None,
        description="A unique identifier which links this FailedOperation, often of the same Id of the operation "
        "should it have been successful. This will often be set programmatically by a database such as "
        "Fractal.",
    )
    input_data: Any = Field(  # type: ignore
        None,
        description="The input data which was passed in that generated this failure. This should be the complete "
        "input which when attempted to be run, caused the operation to fail.",
    )
    success: Literal[False] = Field(  # type: ignore
        False,
        description="A boolean indicator that the operation failed consistent with the model of successful operations. "
        "Should always be False. Allows programmatic assessment of all operations regardless of if they failed or "
        "succeeded",
    )
    error: ComputeError = Field(  # type: ignore
        ...,
        description="A container which has details of the error that failed this operation. See the "
        ":class:`ComputeError` for more details.",
    )
    extras: Optional[Dict[str, Any]] = Field(  # type: ignore
        {},
        description="Additional information to bundle with the failed operation. Details which pertain specifically "
        "to a thrown error should be contained in the `error` field. See :class:`ComputeError` for details.",
    )

    def __repr_args__(self) -> "ReprArgs":
        return [("error", self.error)]

    @field_validator("schema_version", mode="before")
    def _version_stamp(cls, v):
        return 2

    def convert_v(
        self, version: int
    ) -> Union["qcelemental.models.v1.FailedOperation", "qcelemental.models.v2.FailedOperation"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(version, error="FailedOperation") == "self":
            return self

        dself = self.model_dump()
        if version == 1:
            dself.pop("schema_name")
            dself.pop("schema_version")

            self_vN = qcel.models.v1.FailedOperation(**dself)

        return self_vN


def check_convertible_version(ver: int, error: str):
    if ver == 1:
        return True
    elif ver == 2:
        return "self"
    else:
        raise ValueError(f"QCSchema {error} version={version} does not exist for conversion.")


qcschema_input_default = "qcschema_input"
qcschema_output_default = "qcschema_output"
qcschema_optimization_input_default = "qcschema_optimization_input"
qcschema_optimization_output_default = "qcschema_optimization_output"
qcschema_torsion_drive_input_default = "qcschema_torsion_drive_input"
qcschema_torsion_drive_output_default = "qcschema_torsion_drive_output"
qcschema_molecule_default = "qcschema_molecule"
