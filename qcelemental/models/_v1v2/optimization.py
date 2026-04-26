from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import Field, field_validator

from ...util import provenance_stamp
from ..v2.basemodels import ProtoModel
from ..v2.common_models import DriverEnum, Model, Provenance
from ..v2.types import GenericData
from .atomic import AtomicResult
from .basemodels import check_convertible_version
from .basis_set import BasisSet
from .failed_operation import ComputeError
from .molecule import Molecule

if TYPE_CHECKING:
    from ..v2.common_models import ReprArgs


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

    trajectory: TrajectoryProtocolEnum = Field(TrajectoryProtocolEnum.all)

    def convert_v(self, target_version: int, /) -> Union[
        "qcelemental.models.v1.OptimizationProtocols",
        "qcelemental.models.v2.OptimizationProtocols",
        "qcelemental.models._v1v2.OptimizationProtocols",
    ]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationProtocols") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            dself.pop("trajectory", None)
            dself["trajectory_results"] = self.trajectory.value

            self_vN = qcel.models.v2.OptimizationProtocols(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.OptimizationProtocols(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Inputs (Kw/Spec/In)  ====================================================


class QCInputSpecification(ProtoModel):
    """
    A compute description for energy, gradient, and Hessian computations used in a geometry optimization.
    """

    schema_name: Literal["qcschema_input"] = Field("qcschema_input")
    schema_version: Literal[1] = Field(1)

    driver: DriverEnum = Field(DriverEnum.gradient)
    model: Model = Field(...)
    keywords: GenericData = Field({})

    extras: GenericData = Field({})

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.QCInputSpecification", "qcelemental.models.v2.AtomicSpecification"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="QCInputSpecification") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            dself.pop("schema_name")
            dself.pop("schema_version")

            model = dself.pop("model")
            if isinstance(self.model.basis, BasisSet):
                model["basis"] = self.model.basis.convert_v(target_version)
            dself["model"] = model

            self_vN = qcel.models.v2.AtomicSpecification(**dself)
        else:
            assert False, target_version

        return self_vN


class OptimizationInput(ProtoModel):
    """QCSchema input directive for geometry optimization."""

    id: Optional[str] = None
    hash_index: Optional[str] = None
    schema_name: Literal["qcschema_optimization_input"] = "qcschema_optimization_input"
    schema_version: Literal[1] = 1

    keywords: GenericData = Field({})
    extras: GenericData = Field({})
    protocols: OptimizationProtocols = Field(OptimizationProtocols())

    input_specification: QCInputSpecification = Field(...)
    initial_molecule: Molecule = Field(...)

    provenance: Provenance = Field(default_factory=partial(provenance_stamp, __name__), validate_default=True)

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("model", self.input_specification.model.model_dump()),
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
        if target_version == 2:
            dself.pop("schema_version")  # changed in v2
            dself.pop("hash_index", None)  # no longer used, so dropped in v2

            dself["initial_molecule"] = self.initial_molecule.convert_v(target_version)

            spec = {}
            spec["extras"] = dself.pop("extras")
            dself.pop("protocols")
            spec["protocols"] = self.protocols.convert_v(target_version).model_dump()
            spec["specification"] = self.input_specification.convert_v(target_version).model_dump()
            dself.pop("input_specification")
            spec["specification"]["program"] = dself["keywords"].pop(
                "program", ""
            )  # "" is when there's an implicit program, like nwchemopt
            spec["keywords"] = dself.pop("keywords")
            dself["specification"] = spec

            self_vN = qcel.models.v2.OptimizationInput(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Results  ================================================================


class OptimizationResult(OptimizationInput):
    """QCSchema results model for geometry optimization."""

    schema_name: Literal["qcschema_optimization_output"] = "qcschema_optimization_output"

    final_molecule: Optional[Molecule] = Field(...)
    trajectory: List[AtomicResult] = Field(...)
    energies: List[float] = Field(...)

    stdout: Optional[str] = Field(None)
    stderr: Optional[str] = Field(None)

    success: bool = Field(...)
    error: Optional[ComputeError] = Field(None)
    provenance: Provenance = Field(...)

    @field_validator("trajectory")
    @classmethod
    def _trajectory_protocol(cls, v, info):
        # Do not propogate validation errors
        if "protocols" not in info.data:
            raise ValueError("Protocols was not properly formed.")

        keep_enum = info.data["protocols"].trajectory
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
        self,
        target_version: int,
        /,
        *,
        external_input_data: Optional[Union[Dict[str, Any], "OptimizationInput"]] = None,
    ) -> Union["qcelemental.models.v1.OptimizationResult", "qcelemental.models.v2.OptimizationResult"]:
        """Convert to instance of particular QCSchema version.

        Parameters
        ----------
        target_version
            The version to convert to.
        external_input_data
            Since self contains data merged from input, this allows passing in the original input, particularly for
            `extras` fields. Can be model or dictionary and should be *already* converted to target_version.
            Replaces ``input_data`` field entirely (not merges with extracts from self) and w/o consistency checking.
        """
        import qcelemental as qcel

        if check_convertible_version(target_version, error="OptimizationResult") == "self":
            return self

        try:
            trajectory_class = self.trajectory[0].__class__
        except IndexError:
            trajectory_class = None

        dself = self.model_dump()
        if target_version == 2:
            # remove harmless empty error field that v2 won't accept. if populated, pydantic will catch it.
            if not dself.get("error", True):
                dself.pop("error")

            dself.pop("hash_index", None)  # no longer used, so dropped in v2
            dself.pop("schema_name")  # changed in v2
            dself.pop("schema_version")  # changed in v2

            v1_input_data = {
                k: dself.pop(k)
                for k in list(dself.keys())
                if k in ["initial_molecule", "protocols", "keywords", "input_specification"]
            }
            # sep any merged extras known to belong to input
            v1_input_data["extras"] = {k: dself["extras"].pop(k) for k in list(dself["extras"].keys()) if k in []}
            v2_input_data = qcel.models._v1v2.OptimizationInput(**v1_input_data).convert_v(target_version)

            # any input provenance has been overwritten
            # if dself["id"]:
            #     input_data["id"] = dself["id"]  # in/out should likely match

            if external_input_data:
                # Note: overwriting with external, not updating. reconsider?
                if isinstance(external_input_data, dict):
                    if isinstance(external_input_data["specification"], dict):
                        in_extras = external_input_data["specification"].get("extras", {})
                    else:
                        in_extras = external_input_data["specification"].extras
                else:
                    in_extras = external_input_data.specification.extras
                    optsubptcl = external_input_data.specification.specification.protocols
                dself["extras"] = {k: v for k, v in dself["extras"].items() if (k, v) not in in_extras.items()}
                dself["input_data"] = external_input_data
            else:
                dself["input_data"] = v2_input_data
                optsubptcl = None

            dself["final_molecule"] = self.final_molecule.convert_v(target_version)
            dself["properties"] = {
                "nuclear_repulsion_energy": self.final_molecule.nuclear_repulsion_energy(),
                "return_energy": dself["energies"][-1],
                "optimization_iterations": len(dself["energies"]),
            }
            if dself.get("trajectory", []):
                if (
                    last_grad := dself["trajectory"][-1].get("properties", {}).get("return_gradient", None)
                ) is not None:
                    dself["properties"]["return_gradient"] = last_grad
            if len(dself.get("trajectory", [])) == len(dself["energies"]):
                dself["trajectory_properties"] = [
                    res["properties"] for res in dself["trajectory"]
                ]  # TODO filter to key keys
            dself["trajectory_properties"] = [{"return_energy": ene} for ene in dself["energies"]]
            dself.pop("energies")

            dself["trajectory_results"] = [
                trajectory_class(**atres).convert_v(target_version, external_protocols=optsubptcl)
                for atres in dself["trajectory"]
            ]
            dself.pop("trajectory")

            self_vN = qcel.models.v2.OptimizationResult(**dself)
        else:
            assert False, target_version

        return self_vN
