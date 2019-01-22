from enum import Enum
from pydantic import BaseModel, constr
from typing import List, Union, Dict
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
    scf_one_electron_energy: float = None
    scf_two_electron_energy: float = None
    nuclear_repulsion_energy: float = None
    scf_vv10_energy: float = None
    scf_xc_energy: float = None
    scf_dispersion_correction_energy: float = None
    scf_dipole_moment: List[float] = None
    scf_total_energy: float = None
    scf_iterations: int = None
    mp2_same_spin_correlation_energy: float = None
    mp2_opposite_spin_correlation_energy: float = None
    mp2_singles_energy: float = None
    mp2_doubles_energy: float = None
    mp2_total_correlation_energy: float = None
    mp2_total_energy: float = None
    calcinfo_nbasis: int = None
    calcinfo_nmo: int = None
    calcinfo_nalpha: int = None
    calcinfo_nbeta: int = None
    calcinfo_natom: int = None
    return_energy: float = None

    class Config:
        allow_extra = True  # Not yet fully validated, but will accept extra for now


class ErrorEnum(str, Enum):
    convergence_error = "convergence_error"
    file_error = "file_error"
    memory_error = "memory_error"


class Error(BaseModel):
    """The type of error message raised"""
    error_type: Dict[str, str]  # Error enumeration not yet strict
    error_message: str

    class Config:
        allow_extra = False


### Primary models

class ResultInput(BaseModel):
    """The MolSSI Quantum Chemistry Schema"""
    id: str = None
    molecule: Molecule
    driver: DriverEnum
    model: Model
    schema_name: constr(strip_whitespace=True, regex='qc_schema_input') = "qc_schema_input"  # IDEs complain, its fine
    schema_version: int = 1
    keywords: dict = {}
    provenance: Provenance = provenance_stamp(__name__)

    class Config:
        allow_mutation = False


class Result(ResultInput):
    properties: Properties
    success: bool
    error: Error = None
    return_result: Union[float, List[float]]

    class Config(ResultInput.Config):
        # Will carry the allow_mutation flag
        allow_extra = True  # Permits arbitrary fields
