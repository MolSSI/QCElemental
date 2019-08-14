from typing import Any, Dict, List, Optional, Union

import numpy as np
from pydantic import constr, validator

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .common_models import ComputeError, DriverEnum, Model, Provenance, qcschema_input_default, qcschema_output_default
from .molecule import Molecule
from .types import Array


class ResultProperties(ProtoModel):

    # Calcinfo
    calcinfo_nbasis: Optional[int] = None
    calcinfo_nmo: Optional[int] = None
    calcinfo_nalpha: Optional[int] = None
    calcinfo_nbeta: Optional[int] = None
    calcinfo_natom: Optional[int] = None

    # Canonical
    nuclear_repulsion_energy: Optional[float] = None
    return_energy: Optional[float] = None

    # SCF Keywords
    scf_one_electron_energy: Optional[float] = None
    scf_two_electron_energy: Optional[float] = None
    scf_vv10_energy: Optional[float] = None
    scf_xc_energy: Optional[float] = None
    scf_dispersion_correction_energy: Optional[float] = None
    scf_dipole_moment: Optional[List[float]] = None
    scf_total_energy: Optional[float] = None
    scf_iterations: Optional[int] = None

    # MP2 Keywords
    mp2_same_spin_correlation_energy: Optional[float] = None
    mp2_opposite_spin_correlation_energy: Optional[float] = None
    mp2_singles_energy: Optional[float] = None
    mp2_doubles_energy: Optional[float] = None
    mp2_total_correlation_energy: Optional[float] = None  # Old name, to be deprecated
    mp2_correlation_energy: Optional[float] = None
    mp2_total_energy: Optional[float] = None
    mp2_dipole_moment: Optional[List[float]] = None

    # CCSD Keywords
    ccsd_same_spin_correlation_energy: Optional[float] = None
    ccsd_opposite_spin_correlation_energy: Optional[float] = None
    ccsd_singles_energy: Optional[float] = None
    ccsd_doubles_energy: Optional[float] = None
    ccsd_correlation_energy: Optional[float] = None
    ccsd_total_energy: Optional[float] = None
    ccsd_dipole_moment: Optional[List[float]] = None
    ccsd_iterations: Optional[int] = None

    # CCSD(T) keywords
    ccsd_prt_pr_correlation_energy: Optional[float] = None
    ccsd_prt_pr_total_energy: Optional[float] = None
    ccsd_prt_pr_dipole_moment: Optional[List[float]] = None

    class Config(ProtoModel.Config):
        serialize_skip_defaults = True


### Primary models


class ResultInput(ProtoModel):
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


class Result(ResultInput):
    schema_name: constr(strip_whitespace=True, regex=qcschema_output_default) = qcschema_output_default

    properties: ResultProperties
    return_result: Union[float, Array[float], Dict[str, Any]]

    stdout: Optional[str] = None
    stderr: Optional[str] = None

    success: bool
    error: Optional[ComputeError] = None
    provenance: Provenance

    @validator("schema_name", pre=True)
    def _input_to_output(cls, v):
        """If qcschema_input is passed in, cast it to output, otherwise no"""
        if v.lower().strip() in [qcschema_input_default, qcschema_output_default]:
            return qcschema_output_default
        raise ValueError("Only {0} or {1} is allowed for schema_name, "
                         "which will be converted to {0}".format(qcschema_output_default, qcschema_input_default))

    @validator("return_result", whole=True)
    def _validate_return_result(cls, v, values):
        if values["driver"] == "gradient":
            v = np.asarray(v).reshape(-1, 3)
        elif values["driver"] == "hessian":
            v = np.asarray(v)
            nsq = int(v.size**0.5)
            v.shape = (nsq, nsq)

        return v
