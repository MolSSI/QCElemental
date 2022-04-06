from asyncio import protocols
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Tuple, Union

from pydantic import Field, constr, validator
from typing_extensions import Literal

from .abcmodels import ResultBase
from .basemodels import ProtoModel
from .common_models import (
    ComputeError,
    DriverEnum,
    qcschema_optimization_input_default,
    qcschema_optimization_output_default,
    qcschema_optimization_specification_default,
    qcschema_torsion_drive_input_default,
    qcschema_torsion_drive_output_default,
    qcschema_torsion_drive_specification_default,
)
from .molecule import Molecule
from .results import (
    AtomicInput,
    AtomicResult,
    InputComputationBase,
    InputSpecificationBase,
    QCInputSpecification,
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

    trajectory: TrajectoryProtocolEnum = Field(
        TrajectoryProtocolEnum.all, description=str(TrajectoryProtocolEnum.__doc__)
    )

    class Config:
        force_skip_defaults = True


class OptimizationSpecification(InputSpecificationBase):
    """
    A specification for how a geometry optimization should be performed **inside** of
    another procedure.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    * NOTE: I suggest this object be used analogous to QCInputSpecification but for optimizations
    """

    # schema_name: constr(strip_whitespace=True, regex=qcschema_optimization_specification) = qcschema_optimization_specification  # type: ignore
    schema_name: ClassVar[str] = qcschema_optimization_specification_default
    protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))
    # NOTE: Need a little help knowing how procedure field is used. What values might it contain?
    procedure: Optional[str] = Field(None, description="Optimization procedure to run the optimization with.")

    @validator("procedure")
    def _check_procedure(cls, v):
        return v.lower()


class OptimizationInput(InputComputationBase):
    """Input object for an optimization computation"""

    schema_name: ClassVar[str] = qcschema_optimization_input_default
    hash_index: Optional[str] = None  # NOTE: Need this field?
    input_spec: OptimizationSpecification = Field(
        OptimizationSpecification(), description=OptimizationSpecification.__doc__
    )
    gradient_spec: QCInputSpecification = Field(..., description=str(QCInputSpecification.__doc__))

    @validator("gradient_spec")
    def _check_gradient_spec(cls, value):
        assert value.driver == DriverEnum.gradient, "driver must be set to gradient"
        return value

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("model", self.gradient_spec.model.dict()),
            ("molecule_hash", self.molecule.get_hash()[:7]),
        ]


class OptimizationResult(SuccessfulResultBase):
    """The result of an optimization procedure"""

    schema_name: ClassVar[str] = qcschema_optimization_output_default
    # schema_name: constr(strip_whitespace=True, regex=qcschema_optimization_output_default) = qcschema_optimization_output_default  # type: ignore
    input_data: OptimizationInput = Field(..., description=str(OptimizationInput.__doc__))
    # NOTE: If Optional we want None instead of ...; is there a reason for ...? Should the attribute not be Optional?
    final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
    trajectory: List[AtomicResult] = Field(
        ..., description="A list of ordered Result objects for each step in the optimization."
    )
    energies: List[float] = Field(..., description="A list of ordered energies for each step in the optimization.")

    @validator("trajectory", each_item=False)
    def _trajectory_protocol(cls, v, values):
        # NOTE: Commenting out because with current setup field is gauranteed to always exist
        # Do not propagate validation errors
        # if "protocols" not in values["input_data"]:
        #     raise ValueError("Protocols was not properly formed.")

        keep_enum = values["input_data"].input_spec.protocols.trajectory
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


class TorsionDriveSpecification(InputSpecificationBase):
    """Specification for a Torsion Drive computation"""

    protocols: None = None
    schema_name: ClassVar[str] = qcschema_torsion_drive_specification_default
    # schema_name: constr(strip_whitespace=True, regex=qcschema_torsion_drive_input_default) = qcschema_torsion_drive_input_default  # type: ignore
    keywords: TDKeywords = Field(..., description="The torsion drive specific keywords to be used.")


class TorsionDriveInput(InputComputationBase):
    """Inputs for running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: ClassVar[str] = qcschema_torsion_drive_input_default
    input_spec: TorsionDriveSpecification = Field(..., description=(str(TorsionDriveSpecification.__doc__)))
    gradient_spec: QCInputSpecification = Field(..., description=str(QCInputSpecification.__doc__))
    optimization_spec: OptimizationSpecification = Field(
        OptimizationSpecification(), description="Settings to use for optimizations at each grid angle."
    )

    @validator("gradient_spec")
    def _check_gradient_spec(cls, value):
        assert value.driver == DriverEnum.gradient, "driver must be set to gradient"
        return value


class TorsionDriveResult(SuccessfulResultBase):
    """Results from running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: ClassVar[str] = qcschema_torsion_drive_output_default
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
    """Record indicating that a given operation (program, procedure, etc.) has failed and containing the reason and input data which generated the failure."""

    input_data: Union[AtomicInput, OptimizationInput, TorsionDriveInput] = Field(
        ..., description="The input data supplied to generate this computation"
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

    def __repr_args__(self) -> "ReprArgs":
        return [("error", self.error)]
