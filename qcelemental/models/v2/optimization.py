from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

try:
    from typing import Annotated
except ImportError:
    # remove when minimum py39
    from typing_extensions import Annotated

from pydantic import Discriminator, Field, Tag, field_validator

from ...util import provenance_stamp, which_import
from .atomic import AtomicProperties, AtomicResult, AtomicSpecification
from .basemodels import ProtoModel, check_convertible_version
from .common_models import Provenance
from .molecule import Molecule
from .types import Array, GenericData

if TYPE_CHECKING:
    from qcmanybody.models.v2 import ManyBodyProperties, ManyBodyResult, ManyBodySpecification

    import qcelemental

    from .common_models import ReprArgs


# ====  Protocols  ==============================================================


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

    schema_name: Literal["qcschema_optimization_protocols"] = "qcschema_optimization_protocols"
    trajectory_results: TrajectoryProtocolEnum = Field(
        TrajectoryProtocolEnum.none, description=str(TrajectoryProtocolEnum.__doc__)
    )

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationProtocols", "qcelemental.models.v2.OptimizationProtocols"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationProtocols") == "self":
            return self

        dself = self.model_dump()
        if target_version == 1:
            dself.pop("schema_name", None)

            # serialization is compact, so use model to assure value
            dself.pop("trajectory_results", None)
            dself["trajectory"] = self.trajectory_results.value

            self_vN = qcel.models.v1.OptimizationProtocols(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Inputs (Kw/Spec/In)  ====================================================


def _opt_subspec_tag(v: Any) -> str:
    # handle model w/o importing ManyBodySpecification to avoid circular imports
    sn = getattr(v, "schema_name", None)
    if sn == "qcschema_many_body_specification":
        return "manybody"
    if sn == "qcschema_atomic_specification":
        return "atomic"

    if isinstance(v, dict):
        # priority: schema_name, otherwise: judge specification vs. model, any doubt: error for atomic
        sn = v.get("schema_name")
        if sn == "qcschema_many_body_specification":
            return "manybody"
        if sn == "qcschema_atomic_specification":
            return "atomic"

        spec = v.get("specification", None)
        if isinstance(spec, dict) and "model" not in v:
            return "manybody"
    return "atomic"


# A simple v1-era Union also works. But the discriminator channels validation to one model for performance and clearer error messages
#   Also, this isn't managing qcmanybody as optional or deferring import to avoid circularity
# OptSubSpecs = Annotated[Union[AtomicSpecification, ManyBodySpecification], Field(union_mode="left_to_right")]

_merged_desc = {
    "opt_subspec": "A directive for how to compute a gradient for the optimization. Either an ordinary atomic/single-point or a many-body spec.",
    "opt_subprop": "An ordered list of abridged single-geometry property sets (energy and other properties) for each step in the optimization. Either an ordinary atomic/single-point or a many-body properties.",
    "opt_subres": "An ordered list of single-geometry result objects for each step in the optimization. Either an ordinary atomic/single-point or a many-body result.",
}

if which_import("qcmanybody", return_bool=True):
    OptSubSpecs = Annotated[
        Union[
            Annotated[AtomicSpecification, Tag("atomic")],
            Annotated["ManyBodySpecification", Tag("manybody")],
        ],
        Field(
            discriminator=Discriminator(_opt_subspec_tag),
            description=_merged_desc["opt_subspec"],
        ),
    ]
    OptSubProps = Annotated[
        Union[
            Annotated[List[AtomicProperties], Tag("atomic")],
            Annotated[List["ManyBodyProperties"], Tag("manybody")],
        ],
        Field(union_mode="left_to_right", description=_merged_desc["opt_subprop"]),
    ]
    OptSubRes = Annotated[
        Union[
            Annotated[List[AtomicResult], Tag("atomic")],
            Annotated[List["ManyBodyResult"], Tag("manybody")],
        ],
        Field(union_mode="left_to_right", description=_merged_desc["opt_subres"]),
    ]

else:
    OptSubSpecs = Annotated[AtomicSpecification, Field(description=_merged_desc["opt_subspec"])]
    OptSubProps = Annotated[List[AtomicProperties], Field(description=_merged_desc["opt_subprop"])]
    OptSubRes = Annotated[List[AtomicResult], Field(description=_merged_desc["opt_subres"])]


class OptimizationSpecification(ProtoModel):
    """Specification for how to run a geometry optimization."""

    schema_name: Literal["qcschema_optimization_specification"] = "qcschema_optimization_specification"

    # right default for program?
    program: str = Field(
        "", description="Optimizer CMS code / QCEngine procedure to run the geometry optimization with."
    )
    keywords: GenericData = Field({}, description="The optimization specific keywords to be used.")
    protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))
    extras: GenericData = Field(
        {},
        description="Additional information to bundle with the computation. Use for schema development and scratch space.",
    )
    specification: OptSubSpecs

    @field_validator("program")
    @classmethod
    def _check_procedure(cls, v):
        return v.lower()

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationSpecification", "qcelemental.models.v2.OptimizationSpecification"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationSpecification") == "self":
            return self

        loss_store = {}
        dself = self.model_dump()
        if target_version == 1:
            dself["procedure"] = dself.pop("program")
            dself["keywords"]["program"] = dself["specification"].pop("program")
            dself["protocols"] = self.protocols.convert_v(target_version)

            loss_store["extras"] = dself.pop("extras")
            loss_store["specification"] = dself.pop("specification")

            # if loss_store:
            #     dself["extras"]["_qcsk_conversion_loss"] = loss_store

            self_vN = qcel.models.v1.OptimizationSpecification(**dself)
        else:
            assert False, target_version

        return self_vN


class OptimizationInput(ProtoModel):
    """QCSchema input directive for geometry optimization."""

    id: Optional[str] = None
    schema_name: Literal["qcschema_optimization_input"] = "qcschema_optimization_input"
    schema_version: Literal[2] = Field(
        2,
        description="The version number of ``schema_name`` to which this model conforms.",
    )

    specification: OptimizationSpecification = Field(..., description=str(OptimizationSpecification.__doc__))
    initial_molecule: Molecule = Field(..., description="The starting molecule for the geometry optimization.")

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

    def __repr_args__(self) -> "ReprArgs":
        try:
            try:
                model = self.specification.specification.model.model_dump()
            except AttributeError:
                try:
                    model = self.specification.specification.specification.model.model_dump()
                except AttributeError:
                    model = "-".join(
                        [str(v.model.model_dump()) for v in self.specification.specification.specification.values()]
                    )
        except Exception:
            # Best-effort: avoid raising from __repr__ if specification has an unexpected structure
            spec = getattr(self, "specification", None)
            model = getattr(spec, "schema_name", str(type(spec)))

        return [
            ("model", model),
            ("molecule_hash", self.initial_molecule.get_hash()[:7]),
        ]

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationInput", "qcelemental.models.v2.OptimizationInput"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationInput") == "self":
            return self

        dself = self.model_dump()
        if target_version == 1:
            dself.pop("schema_version")

            dself["initial_molecule"] = self.initial_molecule.convert_v(target_version)

            dself["extras"] = dself["specification"].pop("extras")
            dself["specification"].pop("protocols")
            dself["protocols"] = self.specification.protocols.convert_v(target_version)
            dself["keywords"] = dself["specification"].pop("keywords")

            dself["input_specification"] = self.specification.specification.convert_v(target_version)
            dself["keywords"]["program"] = dself["specification"]["specification"].pop("program")
            dself["specification"].pop("specification")
            dself["specification"].pop("schema_name")

            opt_program = dself["specification"].pop("program")
            assert not dself["specification"], dself["specification"]
            dself.pop("specification")  # now empty

            self_vN = qcel.models.v1.OptimizationInput(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Properties  =============================================================


class OptimizationProperties(ProtoModel):
    r"""
    Named properties of geometry optimization computations following the MolSSI QCSchema.
    """

    schema_name: Literal["qcschema_optimization_properties"] = Field(
        "qcschema_optimization_properties",
        description=f"The QCSchema specification to which this model conforms.",
    )

    # ========  Calcinfo  =======================================================
    # ========  Canonical  ======================================================

    nuclear_repulsion_energy: Optional[float] = Field(None, description="The nuclear repulsion energy.")

    return_energy: Optional[float] = Field(
        None,
        description=f"The energy of the final optimized molecule. Always available. Identical to the final :attr:`~qcelemental.models.OptimizationResult.trajectory_properties.return_energy`.",
        json_schema_extra={"units": "E_h"},
    )

    return_gradient: Optional[Array[float]] = Field(
        None,
        description=f"The gradient of the final optimized molecule. Always available. Identical to :attr:`~qcelemental.models.OptimizationResult.trajectory_properties.return_gradient`.",
        json_schema_extra={"units": "E_h/a0", "shape": ["nat", 3]},
    )

    optimization_iterations: Optional[int] = Field(
        None, description="The number of geometry iterations taken before convergence."
    )

    final_max_force: Optional[float] = Field(None)
    final_rms_force: Optional[float] = Field(
        None,
        description="The final RMS gradient of the molecule in Hartrees/Bohr.",
        json_schema_extra={"units": "E_h/a0"},
    )
    final_max_displacement: Optional[float] = Field(None)
    final_rms_displacement: Optional[float] = Field(None)

    model_config = ProtoModel._merge_config_with(force_skip_defaults=True)


# ====  Results  ================================================================


class OptimizationResult(ProtoModel):
    """QCSchema results model for geometry optimization."""

    schema_name: Literal["qcschema_optimization_result"] = "qcschema_optimization_result"
    schema_version: Literal[2] = Field(
        2,
        description="The version number of ``schema_name`` to which this model conforms.",
    )
    id: Optional[str] = Field(None, description="The optional ID for the computation.")
    input_data: OptimizationInput = Field(..., description=str(OptimizationInput.__doc__))

    final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
    trajectory_results: OptSubRes
    trajectory_properties: OptSubProps

    stdout: Optional[str] = Field(None, description="The standard output of the program.")
    stderr: Optional[str] = Field(None, description="The standard error of the program.")

    success: Literal[True] = Field(
        True, description="The success of a given programs execution. If False, other fields may be blank."
    )
    provenance: Provenance = Field(..., description=str(Provenance.__doc__))

    # native_files placeholder for when any opt programs supply extra files or need an input file. no protocol at present
    native_files: Dict[str, Any] = Field({}, description="DSL files.")

    properties: OptimizationProperties = Field(..., description=str(OptimizationProperties.__doc__))

    extras: GenericData = Field(
        {},
        description="Additional information to bundle with the computation. Use for schema development and scratch space.",
    )

    @field_validator("trajectory_results")
    @classmethod
    def _trajectory_protocol(cls, v, info):
        # Do not propogate validation errors
        if "input_data" not in info.data:
            raise ValueError("Input_data was not properly formed.")

        keep_enum = info.data["input_data"].specification.protocols.trajectory_results
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

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.OptimizationResult", "qcelemental.models.v2.OptimizationResult"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationResult") == "self":
            return self

        dself = self.model_dump()
        if target_version == 1:
            try:
                trajectory_class = self.trajectory_results[0].__class__
            except IndexError:
                trajectory_class = None

            # for input_data, work from model, not dict, to use convert_v
            dself.pop("input_data")
            input_data = self.input_data.convert_v(1).model_dump()  # exclude_unset=True, exclude_none=True

            dself.pop("properties")  # new in v2
            dself.pop("native_files")  # new in v2

            dself["final_molecule"] = self.final_molecule.convert_v(target_version)

            dself["trajectory"] = [
                trajectory_class(**atres).convert_v(target_version) for atres in dself["trajectory_results"]
            ]
            dself.pop("trajectory_results")
            dself["energies"] = [atprop.pop("return_energy", None) for atprop in dself["trajectory_properties"]]
            dself.pop("trajectory_properties")

            dself["extras"] = {**input_data.pop("extras", {}), **dself.pop("extras", {})}  # merge

            dself = {**input_data, **dself}
            dself.pop("schema_name")  # changed in v1
            dself.pop("schema_version")  # changed in v1

            self_vN = qcel.models.v1.OptimizationResult(**dself)
        else:
            assert False, target_version

        return self_vN
