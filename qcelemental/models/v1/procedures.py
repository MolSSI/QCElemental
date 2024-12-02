from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic.v1 import Field, conlist, constr, validator

from ...util import provenance_stamp
from .basemodels import ProtoModel
from .common_models import (
    ComputeError,
    DriverEnum,
    Model,
    Provenance,
    check_convertible_version,
    qcschema_input_default,
    qcschema_optimization_input_default,
    qcschema_optimization_output_default,
    qcschema_torsion_drive_input_default,
    qcschema_torsion_drive_output_default,
)
from .molecule import Molecule
from .results import AtomicResult

if TYPE_CHECKING:
    from pydantic.v1.typing import ReprArgs


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
    schema_version: Literal[1] = 1

    driver: DriverEnum = Field(DriverEnum.gradient, description=str(DriverEnum.__doc__))
    model: Model = Field(..., description=str(Model.__doc__))
    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")

    extras: Dict[str, Any] = Field(
        {},
        description="Additional information to bundle with the computation. Use for schema development and scratch space.",
    )

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.QCInputSpecification", "qcelemental.models.v2.AtomicSpecification"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="QCInputSpecification") == "self":
            return self

        dself = self.dict()
        if target_version == 2:
            dself.pop("schema_name")
            dself.pop("schema_version")

            self_vN = qcel.models.v2.AtomicSpecification(**dself)
        else:
            assert False, target_version

        return self_vN


class OptimizationInput(ProtoModel):
    id: Optional[str] = None
    hash_index: Optional[str] = None
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_input_default
    ) = qcschema_optimization_input_default
    schema_version: Literal[1] = 1

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

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationInput", "qcelemental.models.v2.OptimizationInput"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationInput") == "self":
            return self

        dself = self.dict()
        if target_version == 2:
            dself["input_specification"].pop("schema_version", None)
            self_vN = qcel.models.v2.OptimizationInput(**dself)
        else:
            assert False, target_version

        return self_vN


class OptimizationResult(OptimizationInput):
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_output_default
    ) = qcschema_optimization_output_default
    schema_version: Literal[1] = 1

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

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationResult", "qcelemental.models.v2.OptimizationResult"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationResult") == "self":
            return self

        trajectory_class = self.trajectory[0].__class__
        dself = self.dict()
        if target_version == 2:
            # remove harmless empty error field that v2 won't accept. if populated, pydantic will catch it.
            if not dself.get("error", True):
                dself.pop("error")

            dself["trajectory"] = [trajectory_class(**atres).convert_v(target_version) for atres in dself["trajectory"]]
            dself["input_specification"].pop("schema_version", None)

            self_vN = qcel.models.v2.OptimizationResult(**dself)
        else:
            assert False, target_version

        return self_vN


class OptimizationSpecification(ProtoModel):
    """
    A specification for how a geometry optimization should be performed **inside** of
    another procedure.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: constr(strip_whitespace=True, regex="qcschema_optimization_specification") = "qcschema_optimization_specification"  # type: ignore
    schema_version: Literal[1] = 1

    procedure: str = Field(..., description="Optimization procedure to run the optimization with.")
    keywords: Dict[str, Any] = Field({}, description="The optimization specific keywords to be used.")
    protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    @validator("procedure")
    def _check_procedure(cls, v):
        return v.lower()


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


class TorsionDriveInput(ProtoModel):
    """Inputs for running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: constr(strip_whitespace=True, regex=qcschema_torsion_drive_input_default) = qcschema_torsion_drive_input_default  # type: ignore
    schema_version: Literal[1] = 1

    keywords: TDKeywords = Field(..., description="The torsion drive specific keywords to be used.")
    extras: Dict[str, Any] = Field({}, description="Extra fields that are not part of the schema.")

    input_specification: QCInputSpecification = Field(..., description=str(QCInputSpecification.__doc__))
    initial_molecule: conlist(item_type=Molecule, min_items=1) = Field(
        ..., description="The starting molecule(s) for the torsion drive."
    )

    optimization_spec: OptimizationSpecification = Field(
        ..., description="Settings to use for optimizations at each grid angle."
    )

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

    @validator("input_specification")
    def _check_input_specification(cls, value):
        assert value.driver == DriverEnum.gradient, "driver must be set to gradient"
        return value

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.TorsionDriveInput", "qcelemental.models.v2.TorsionDriveInput"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="TorsionDriveInput") == "self":
            return self

        dself = self.dict()
        # dself = self.model_dump(exclude_unset=True, exclude_none=True)
        if target_version == 2:
            dself["input_specification"].pop("schema_version", None)
            dself["optimization_spec"].pop("schema_version", None)

            self_vN = qcel.models.v2.TorsionDriveInput(**dself)
        else:
            assert False, target_version

        return self_vN


class TorsionDriveResult(TorsionDriveInput):
    """Results from running a torsion drive.

    Notes
    -----
    * This class is still provisional and may be subject to removal and re-design.
    """

    schema_name: constr(strip_whitespace=True, regex=qcschema_torsion_drive_output_default) = qcschema_torsion_drive_output_default  # type: ignore
    schema_version: Literal[1] = 1

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

    stdout: Optional[str] = Field(None, description="The standard output of the program.")
    stderr: Optional[str] = Field(None, description="The standard error of the program.")

    success: bool = Field(
        ..., description="The success of a given programs execution. If False, other fields may be blank."
    )
    error: Optional[ComputeError] = Field(None, description=str(ComputeError.__doc__))
    provenance: Provenance = Field(..., description=str(Provenance.__doc__))

    @validator("schema_version", pre=True)
    def _version_stamp(cls, v):
        return 1

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.TorsionDriveResult", "qcelemental.models.v2.TorsionDriveResult"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="TorsionDriveResult") == "self":
            return self

        opthist_class = next(iter(self.optimization_history.values()))[0].__class__
        dself = self.dict()
        if target_version == 2:
            # remove harmless empty error field that v2 won't accept. if populated, pydantic will catch it.
            if not dself.get("error", True):
                dself.pop("error")

            dself["input_specification"].pop("schema_version", None)
            dself["optimization_spec"].pop("schema_version", None)
            dself["optimization_history"] = {
                k: [opthist_class(**res).convert_v(target_version) for res in lst]
                for k, lst in dself["optimization_history"].items()
            }
            # if dself["optimization_spec"].pop("extras", None):
            #    pass

            self_vN = qcel.models.v2.TorsionDriveResult(**dself)
        else:
            assert False, target_version

        return self_vN


def Optimization(*args, **kwargs):
    """QC Optimization Results Schema.

    .. deprecated:: 0.12
       Use :py:func:`qcelemental.models.OptimizationResult` instead.

    """
    from warnings import warn

    warn(
        "Optimization has been renamed to OptimizationResult and will be removed as soon as v0.13.0", DeprecationWarning
    )
    return OptimizationResult(*args, **kwargs)
