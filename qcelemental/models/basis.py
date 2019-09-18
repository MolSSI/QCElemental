from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
from pydantic import Schema, constr, validator

from .basemodels import ProtoModel


class HarmonicType(str, Enum):
    """
    The angular momentum representation of a shell.
    """
    spherical = 'spherical'
    cartesian = 'cartesian'


class ElectronShell(ProtoModel):
    """
    Information for a single electronic shell
    """

    angular_momentum: List[int] = Schema(..., description="Angular momentum for this shell.")
    harmonic_type: HarmonicType = Schema(..., description=str(HarmonicType.__doc__))
    exponents: List[float] = Schema(..., description="Exponents for this contracted shell.")
    coefficients: List[List[float]] = Schema(
        ...,
        description=
        "General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients."
    )

    @validator('coefficients', whole=True)
    def _check_coefficient_length(cls, v, values):
        len_exp = len(values["exponents"])
        for row in v:
            if len(row) != len_exp:
                raise ValueError("The length of coefficients does not match the length of exponents.")

        return v


class ECPType(str, Enum):
    """
    The type of the ECP potential.
    """
    scalar = 'scalar'
    spinorbit = 'spinorbit'


class ECPPotential(ProtoModel):
    """
    Information for a single ECP potential.
    """

    ecp_type: ECPType = Schema(..., description=str(ECPType.__doc__))
    angular_momentum: List[int] = Schema(..., description="Angular momentum for the ECPs.")
    r_exponents: List[int] = Schema(..., description="Exponents of the 'r' term.")
    gaussian_exponents: List[float] = Schema(..., description="Exponents of the 'gaussian' term.")
    coefficients: List[List[float]] = Schema(
        ...,
        description=
        "General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients."
    )

    @validator('gaussian_exponents', whole=True)
    def _check_gaussian_exponentst_length(cls, v, values):
        len_exp = len(values["r_exponents"])
        if len(v) != len_exp:
            raise ValueError("The length of gaussian_exponents does not match the length of `r` exponents.")

        return v

    @validator('coefficients', whole=True)
    def _check_coefficient_length(cls, v, values):
        len_exp = len(values["r_exponents"])
        for row in v:
            if len(row) != len_exp:
                raise ValueError("The length of coefficients does not match the length of `r` exponents.")

        return v


class BasisCenter(ProtoModel):
    """
    Data for a single atom/center in a basis set.
    """
    electron_shells: List[ElectronShell] = Schema(..., description="Electronic shells for this center.")
    ecp_electrons: int = Schema(0, description="Number of electrons replace by ECP potentials.")
    ecp_potentials: Optional[List[ECPPotential]] = Schema(None, description="ECPs for this center.")


class BasisSet(ProtoModel):
    """
    A quantum chemistry basis description.
    """
    schema_name: constr(strip_whitespace=True, regex="qcschema_basis") = "qcschema_basis"
    schema_version: int = 1

    basis_name: str = Schema(..., description="A standard basis name if available (e.g., 'cc-pVDZ'.")
    description: Optional[str] = Schema(None, description="A brief description of the basis set.")
    basis_data: Dict[str, BasisCenter] = Schema(..., description="A mapping of all types of centers available.")
    basis_atom_map: List[str] = Schema(
        ..., description="Mapping of all centers in the parent molecule to centers in `basis_data`.")

    @validator('basis_atom_map', whole=True)
    def _check_atom_map(cls, v, values):
        sv = set(v)
        missing = sv - values["basis_data"].keys()

        if missing:
            raise ValueError(f"'basis_atom_map' contains unknown keys to 'basis_data': {missing}.")

        return v
