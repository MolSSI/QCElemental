from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Field, constr, validator

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .common_models import (
    ComputeError,
    DriverEnum,
    Model,
    Provenance,
    qcschema_input_default,
    qcschema_optimization_input_default,
    qcschema_optimization_output_default,
)
from .molecule import Molecule
from .results import AtomicResult

if TYPE_CHECKING:
    from pydantic.typing import ReprArgs


class TrajectoryProtocolEnum(str, Enum):
    """
    Which gradient evaluations to keep in an optimization trajectory.
    """

    all = "all"
    initial_and_final = "initial_and_final"
    final = "final"
    none = "none"


class OptimizationProtocols(ProtoModel):
    """
    Protocols regarding the manipulation of a Optimization output data.
    """

    trajectory: TrajectoryProtocolEnum = Field(
        TrajectoryProtocolEnum.all, description=str(TrajectoryProtocolEnum.__doc__)
    )

    class Config:
        force_skip_defaults = True


class QCInputSpecification(ProtoModel):
    """
    A compute description for energy, gradient, and Hessian computations used in a geometry optimization.
    """

    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default  # type: ignore
    schema_version: int = 1

    driver: DriverEnum = Field(DriverEnum.gradient, description=str(DriverEnum.__doc__))
    model: Model = Field(..., description=str(Model.__doc__))
    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")

    extras: Dict[str, Any] = Field({}, description="Extra fields that are not part of the schema.")


class OptimizationInput(ProtoModel):
    id: Optional[str] = None
    hash_index: Optional[str] = None
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_input_default
    ) = qcschema_optimization_input_default
    schema_version: int = 1

    keywords: Dict[str, Any] = Field({}, description="The optimization specific keywords to be used.")
    extras: Dict[str, Any] = Field({}, description="Extra fields that are not part of the schema.")
    protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))

    input_specification: QCInputSpecification = Field(..., description=str(QCInputSpecification.__doc__))
    initial_molecule: Molecule = Field(..., description="The starting molecule for the geometry optimization.")

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("model", self.input_specification.model.dict()),
            ("molecule_hash", self.initial_molecule.get_hash()[:7]),
        ]


class OptimizationResult(OptimizationInput):
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_output_default
    ) = qcschema_optimization_output_default

    final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
    trajectory: List[AtomicResult] = Field(
        ..., description="A list of ordered Result objects for each step in the optimization."
    )
    energies: List[float] = Field(..., description="A list of ordered energies for each step in the optimization.")

    stdout: Optional[str] = Field(None, description="The standard output of the program.")
    stderr: Optional[str] = Field(None, description="The standard error of the program.")

    success: bool = Field(
        ..., description="The success of a given programs execution. If False, other fields may be blank."
    )
    error: Optional[ComputeError] = Field(None, description=str(ComputeError.__doc__))
    provenance: Provenance = Field(..., description=str(Provenance.__doc__))

    @validator("trajectory", each_item=False)
    def _trajectory_protocol(cls, v, values):

        # Do not propogate validation errors
        if "protocols" not in values:
            raise ValueError("Protocols was not properly formed.")

        keep_enum = values["protocols"].trajectory
        if keep_enum == "all":
            pass
        elif keep_enum == "initial_and_final":
            if len(v) != 2:
                v = [v[0], v[-1]]
        elif keep_enum == "final":
            if len(v) != 1:
                v = [v[-1]]
        elif keep_enum == "none":
            v = []
        else:
            raise ValueError(f"Protocol `trajectory:{keep_enum}` is not understood.")

        return v


def Optimization(*args, **kwargs):
    from warnings import warn

    warn("Optimization has been renamed to OptimizationResult and will be removed in v0.13.0", DeprecationWarning)
    return OptimizationResult(*args, **kwargs)
