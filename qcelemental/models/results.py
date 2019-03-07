import json
from typing import Any, Dict, List, Union, Optional

from pydantic import BaseModel, constr, validator

from ..util import provenance_stamp
from .common_models import (ComputeError, DriverEnum, Model, Provenance, ndarray_encoder, qcschema_input_default,
                            qcschema_output_default)
from .molecule import Molecule


class ResultProperties(BaseModel):

    # Calcinfo
    calcinfo_nbasis: int = None
    calcinfo_nmo: int = None
    calcinfo_nalpha: int = None
    calcinfo_nbeta: int = None
    calcinfo_natom: int = None

    # Canonical
    nuclear_repulsion_energy: float = None
    return_energy: float = None

    # SCF Keywords
    scf_one_electron_energy: float = None
    scf_two_electron_energy: float = None
    scf_vv10_energy: float = None
    scf_xc_energy: float = None
    scf_dispersion_correction_energy: float = None
    scf_dipole_moment: List[float] = None
    scf_total_energy: float = None
    scf_iterations: int = None

    # MP2 Keywords
    mp2_same_spin_correlation_energy: float = None
    mp2_opposite_spin_correlation_energy: float = None
    mp2_singles_energy: float = None
    mp2_doubles_energy: float = None
    mp2_total_correlation_energy: float = None
    mp2_total_energy: float = None

    class Config:
        allow_mutation = False
        extra = "forbid"

    def dict(self, *args, **kwargs):
        return super().dict(*args, **{**kwargs, **{"skip_defaults": True}})


### Primary models


class ResultInput(BaseModel):
    """The MolSSI Quantum Chemistry Schema"""
    id: Optional[str] = None
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default
    schema_version: int = 1

    molecule: Molecule
    driver: DriverEnum
    model: Model
    keywords: Dict[str, Any] = {}

    extras: Dict[str, Any] = {}

    provenance: Provenance = provenance_stamp(__name__)

    class Config:
        allow_mutation = False
        extra = "forbid"

        json_encoders = {**ndarray_encoder}

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))


class Result(ResultInput):
    schema_name: constr(strip_whitespace=True, regex=qcschema_output_default) = qcschema_output_default

    properties: ResultProperties
    return_result: Union[float, List[float], Dict[str, Any]]

    stdout: Optional[str] = None
    stderr: Optional[str] = None

    success: bool
    error: ComputeError = None
    provenance: Provenance

    class Config(ResultInput.Config):
        # Will carry other properties
        pass

    @validator("schema_name", pre=True)
    def input_to_output(cls, v):
        """If qcschema_input is passed in, cast it to output, otherwise no"""
        if v.lower().strip() in [qcschema_input_default, qcschema_output_default]:
            return qcschema_output_default
        raise ValueError("Only {0} or {1} is allowed for schema_name, "
                         "which will be converted to {0}".format(qcschema_output_default, qcschema_input_default))
