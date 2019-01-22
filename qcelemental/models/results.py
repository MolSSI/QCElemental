from enum import Enum
from pydantic import BaseModel, constr
from typing import List, Union
from .molecule import Molecule
from .common_models import Provenance
from ..util import provenance_stamp


class DriverEnum(str, Enum):
    energy = 'energy'
    gradient = 'gradient'
    hessian = 'hessian'


class Model(BaseModel):
    method: str
    basis: str = None
    # basis_spec: BasisSpec = None  # This should be exclusive with basis, but for now will be omitted


class Properties(BaseModel):
    scf_one_electron_energy: float
    scf_two_electron_energy: float
    nuclear_repulsion_energy: float
    scf_vv10_energy: float
    scf_xc_energy: float
    scf_dispersion_correction_energy: float
    scf_dipole_moment: List[float]
    scf_total_energy: float
    scf_iterations: int
    mp2_same_spin_correlation_energy: float
    mp2_opposite_spin_correlation_energy: float
    mp2_singles_energy: float
    mp2_doubles_energy: float
    mp2_total_correlation_energy: float
    mp2_total_energy: float
    calcinfo_nbasis: int
    calcinfo_nmo: int
    calcinfo_nalpha: int
    calcinfo_nbeta: int
    calcinfo_natom: int
    return_energy: float

    class Config:
        allow_extra = False


class ErrorType(str, Enum):
    convergence_error = "convergence_error"
    file_error = "file_error"
    memory_error = "memory_error"


class Error(BaseModel):
    """The type of error message raised"""
    error_type: ErrorType
    error_message: str

    class Config:
        allow_extra = False


### Primary models

class ResultsInput(BaseModel):
    """The MolSSI Quantum Chemistry Schema"""
    id: str = None
    molecule: Molecule
    driver: DriverEnum
    model: Model
    schema_name: constr(strip_whitespace=True, regex='qc_schema_input') = "qc_schema_input"  # IDEs complain, its fine
    schema_version: int = 1
    keywords: dict = {}
    provenance: Provenance = provenance_stamp(__name__)


class Results(ResultsInput):
    properties: Properties
    success: bool
    error: Error = None
    return_result: Union[float, List[float]]
