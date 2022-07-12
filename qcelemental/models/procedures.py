from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple, Union

from pydantic import Field, validator
from typing_extensions import Literal

from .inputresult_abc import ResultBase
from .basemodels import ProtoModel
from .common_models import (
    ComputeError,
    DriverEnum,
)
from .molecule import Molecule
from .results import (
    AtomicInput,
    AtomicResult,
    InputBase,
    SpecificationBase,
    AtomicSpecification,
    SuccessfulResultBase,
)

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

    trajectory: TrajectoryProtocolEnum = Field(TrajectoryProtocolEnum.all, description=TrajectoryProtocolEnum.__doc__)

    class Config:
        force_skip_defaults = True


class OptimizationSpecification(SpecificationBase):
    """
    A specification for how a geometry optimization should be performed **inside** of
    another procedure.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    * NOTE: I suggest this object be used analogous to QCInputSpecification but for optimizations
    """

    schema_name: Literal["qcschema_optimizationspecification"] = "qcschema_optimizationspecification"
    protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=OptimizationProtocols.__doc__)
    gradient_specification: AtomicSpecification = Field(..., description=AtomicSpecification.__doc__)

    @validator("gradient_specification")
    def _check_gradient_spec(cls, value):
        assert value.driver == DriverEnum.gradient, "driver must be set to gradient"
        return value


class OptimizationInput(InputBase):
    """Input object for an optimization computation"""

    schema_name: Literal["qcschema_optimizationinput"] = "qcschema_optimizationinput"
    specification: OptimizationSpecification = Field(..., description=OptimizationSpecification.__doc__)

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("model", self.specification.gradient_specification.model.dict()),
            ("molecule_hash", self.molecule.get_hash()[:7]),
        ]


class OptimizationResult(SuccessfulResultBase):
    """The result of an optimization procedure"""

    schema_name: Literal["qcschema_optimizationresult"] = "qcschema_optimizationresult"
    input_data: OptimizationInput = Field(..., description=OptimizationInput.__doc__)
    # NOTE: If Optional we want None instead of ...; is there a reason for ...? Should the attribute not be Optional?
    final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
    trajectory: List[AtomicResult] = Field(
        ..., description="A list of ordered Result objects for each step in the optimization."
    )
    energies: List[float] = Field(..., description="A list of ordered energies for each step in the optimization.")

    @validator("trajectory", each_item=False)
    def _trajectory_protocol(cls, v, values):
        # NOTE: Commenting out because with current setup field is guaranteed to always exist
        # Do not propagate validation errors
        # if "protocols" not in values["input_data"]:
        #     raise ValueError("Protocols was not properly formed.")
        if not values.get("input_data"):
            raise ValueError("input_data not correctly formatted!")

        keep_enum = values["input_data"].specification.protocols.trajectory
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


class TDKeywords(ProtoModel):
    # NOTE: May want to consider using typing_extensions.TypedDict instead of ProtoModel
    # Will maintain .keywords: dict interface while allowing more specific type checking
    # https://docs.python.org/3.8/library/typing.html#typing.TypedDict
    """
    TorsionDriveRecord options

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    dihedrals: List[Tuple[int, int, int, int]] = Field(
        ...,
        description="The list of dihedrals to select for the TorsionDrive operation. Each entry is a tuple of integers "
        "of for particle indices.",
    )
    grid_spacing: List[int] = Field(
        ...,
        description="List of grid spacing for dihedral scan in degrees. Multiple values will be mapped to each "
        "dihedral angle.",
    )
    dihedral_ranges: Optional[List[Tuple[int, int]]] = Field(
        None,
        description="A list of dihedral range limits as a pair (lower, upper). "
        "Each range corresponds to the dihedrals in input.",
    )
    energy_decrease_thresh: Optional[float] = Field(
        None,
        description="The threshold of the smallest energy decrease amount to trigger activating optimizations from "
        "grid point.",
    )
    energy_upper_limit: Optional[float] = Field(
        None,
        description="The threshold if the energy of a grid point that is higher than the current global minimum, to "
        "start new optimizations, in unit of a.u. I.e. if energy_upper_limit = 0.05, current global "
        "minimum energy is -9.9 , then a new task starting with energy -9.8 will be skipped.",
    )


class TorsionDriveSpecification(SpecificationBase):
    """Specification for a Torsion Drive computation"""

    schema_name: Literal["qcschema_torsiondrivespecification"] = "qcschema_torsiondrivespecification"
    keywords: TDKeywords = Field(..., description="The torsion drive specific keywords to be used.")
    optimization_specification: OptimizationSpecification = Field(..., description=OptimizationSpecification.__doc__)


class TorsionDriveInput(InputBase):
    """Inputs for running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: Literal["qcschema_torsiondriveinput"] = "qcschema_torsiondriveinput"
    specification: TorsionDriveSpecification = Field(..., description=(TorsionDriveSpecification.__doc__))


class TorsionDriveResult(SuccessfulResultBase):
    """Results from running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: Literal["qcschema_torsiondriveresult"] = "qcschema_torsiondriveresult"
    input_data: TorsionDriveInput = Field(..., description="TorsionDriveInput used to generate the computation")
    final_energies: Dict[str, float] = Field(
        ..., description="The final energy at each angle of the TorsionDrive scan."
    )
    final_molecules: Dict[str, Molecule] = Field(
        ..., description="The final molecule at each angle of the TorsionDrive scan."
    )
    optimization_history: Dict[str, List[OptimizationResult]] = Field(
        ...,
        description="The map of each angle of the TorsionDrive scan to each optimization computations.",
    )


class FailedOperation(ResultBase):
    """Record indicating that a given operation (program, procedure, etc.) has failed and containing the reason and input_data which generated the failure."""

    schema_name: Literal["qcschema_failedoperation"] = "qcschema_failedoperation"
    input_data: Union[AtomicInput, OptimizationInput, TorsionDriveInput] = Field(
        ...,
        discriminator="schema_name",
        description="The input data supplied to generate this computation",
    )
    success: Literal[False] = Field(False, description="FailedOperation objects always have `False`.")
    error: ComputeError = Field(
        ...,
        description="A container which has details of the error that failed this operation. See the "
        ":class:`ComputeError` for more details.",
    )

    def __repr_args__(self) -> "ReprArgs":
        return [("error", self.error)]
