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
