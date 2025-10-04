from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Set, Union

from pydantic import Field, field_validator

from ...util import provenance_stamp

# Note that if any of these models presently borrowed from v2 diverge
#   from v1, they'll need redefining here
from ..v2.atomic import AtomicProperties as AtomicProperties_v2
from ..v2.atomic import WavefunctionProperties as WavefunctionProperties_v2
from ..v2.basemodels import ExtendedConfigDict, ProtoModel
from ..v2.common_models import DriverEnum, Model, Provenance
from ..v2.failed_operation import ComputeError
from ..v2.types import Array
from .basemodels import check_convertible_version, qcschema_draft
from .basis_set import BasisSet
from .molecule import Molecule

# ====  Properties  =============================================================


class AtomicResultProperties(AtomicProperties_v2):
    pass


class WavefunctionProperties(WavefunctionProperties_v2):
    basis: BasisSet = Field(...)

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.WavefunctionProperties", "qcelemental.models.v2.WavefunctionProperties"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="WavefunctionProperties") == "self":
            return self

        dself = self.dict()
        if target_version == 2:
            dself["basis"] = self.basis.convert_v(target_version).model_dump()

            self_vN = qcel.models.v2.WavefunctionProperties(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.WavefunctionProperties(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Protocols  ==============================================================


class WavefunctionProtocolEnum(str, Enum):
    all = "all"
    orbitals_and_eigenvalues = "orbitals_and_eigenvalues"
    occupations_and_eigenvalues = "occupations_and_eigenvalues"
    return_results = "return_results"
    none = "none"


class ErrorCorrectionProtocol(ProtoModel):
    default_policy: bool = Field(True)
    policies: Optional[Dict[str, bool]] = Field(None)

    def allows(self, policy: str):
        if self.policies is None:
            return self.default_policy
        return self.policies.get(policy, self.default_policy)


class NativeFilesProtocolEnum(str, Enum):
    all = "all"
    input = "input"
    none = "none"


class AtomicResultProtocols(ProtoModel):
    wavefunction: WavefunctionProtocolEnum = Field(WavefunctionProtocolEnum.none)
    stdout: bool = Field(True)
    error_correction: ErrorCorrectionProtocol = Field(default_factory=ErrorCorrectionProtocol)
    native_files: NativeFilesProtocolEnum = Field(NativeFilesProtocolEnum.none)

    model_config = ExtendedConfigDict(force_skip_defaults=True)


# ====  Inputs (Kw/Spec/In)  ====================================================


def atomic_input_json_schema_extra(schema, model):
    schema["$schema"] = qcschema_draft


class AtomicInput(ProtoModel):

    id: Optional[str] = Field(None)
    schema_name: Literal["qcschema_input"] = Field("qcschema_input")
    schema_version: Literal[1] = Field(1)
    molecule: Molecule = Field(...)
    driver: DriverEnum = Field(...)
    model: Model = Field(...)
    keywords: Dict[str, Any] = Field({})
    protocols: AtomicResultProtocols = Field(AtomicResultProtocols())
    extras: Dict[str, Any] = Field({})
    provenance: Provenance = Field(default_factory=partial(provenance_stamp, __name__), validate_default=True)

    model_config = ProtoModel._merge_config_with(json_schema_extra=atomic_input_json_schema_extra)

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("driver", self.driver.value),
            ("model", self.model.model_dump()),
            ("molecule_hash", self.molecule.get_hash()[:7]),
        ]

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.AtomicInput", "qcelemental.models.v2.AtomicInput"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="AtomicInput") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            dself.pop("schema_name")  # changes in v2
            dself.pop("schema_version")  # changes in v2

            model = dself.pop("model")
            if isinstance(self.model.basis, BasisSet):
                model["basis"] = self.model.basis.convert_v(target_version)
            dself["molecule"] = self.molecule.convert_v(target_version)

            spec = {}
            spec["driver"] = dself.pop("driver")
            spec["model"] = model
            spec["keywords"] = dself.pop("keywords", None)
            spec["protocols"] = dself.pop("protocols", None)
            spec["extras"] = dself.pop("extras", None)
            dself["specification"] = spec
            self_vN = qcel.models.v2.AtomicInput(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.AtomicInput(**dself)
        else:
            assert False, target_version

        return self_vN


# ====  Results  ================================================================


class AtomicResult(AtomicInput):
    schema_name: Literal["qcschema_output"] = Field("qcschema_output")
    schema_version: Literal[1] = Field(1)
    properties: AtomicResultProperties = Field(...)
    wavefunction: Optional[WavefunctionProperties] = Field(None)
    return_result: Union[float, Array[float], Dict[str, Any]] = Field(...)
    stdout: Optional[str] = Field(None)
    stderr: Optional[str] = Field(None)
    native_files: Dict[str, Any] = Field({})
    success: bool = Field(...)
    error: Optional[ComputeError] = Field(None)
    provenance: Provenance = Field(...)

    def convert_v(
        self,
        target_version: int,
        /,
        *,
        external_input_data: Optional[Any] = None,
        external_protocols: Optional[AtomicResultProtocols] = None,
    ) -> Union["qcelemental.models.v1.AtomicResult", "qcelemental.models.v2.AtomicResult"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="AtomicResult") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            dself.pop("schema_name")  # changes in v2
            dself.pop("schema_version")  # changes in v2

            molecule = self.molecule.convert_v(target_version)

            # remove harmless empty error field that v2 won't accept. if populated, pydantic will catch it.
            if not dself.get("error", True):
                dself.pop("error")

            input_data = {
                "specification": {
                    k: dself.pop(k) for k in list(dself.keys()) if k in ["driver", "keywords", "model", "protocols"]
                },
                "molecule": molecule,  # duplicate since input mol has been overwritten
            }
            in_extras = {
                k: dself["extras"].pop(k) for k in list(dself["extras"].keys()) if k in []
            }  # sep any merged extras known to belong to input
            input_data["specification"]["extras"] = in_extras
            if isinstance(self.model.basis, BasisSet):
                input_data["specification"]["model"]["basis"] = self.model.basis.convert_v(target_version)

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
                dself["extras"] = {k: v for k, v in dself["extras"].items() if (k, v) not in in_extras.items()}
                dself["input_data"] = external_input_data
            else:
                dself["input_data"] = input_data
                if external_protocols:
                    dself["input_data"]["specification"]["protocols"] = external_protocols

            dself["molecule"] = molecule
            if self.wavefunction is not None:
                dself["wavefunction"] = self.wavefunction.convert_v(target_version).model_dump()

            self_vN = qcel.models.v2.AtomicResult(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.AtomicResult(**dself)
        else:
            assert False, target_version

        return self_vN
