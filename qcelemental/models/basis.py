from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
from pydantic import Schema, constr, validator

from .basemodels import ProtoModel


class HarmonicType(str, enum):
    """
    The angular momentum representation of a shell.
    """
    spherical = 'spherical'
    cartesian = 'cartesian'


class ElectronShell(ProtoModel):
    """
    Information for a single electronic shell
    """

    angular_momentum: List[int] = Schema(..., description="Angular momentum (as an array of integers)")
    harmonic_type: HarmonicType = Schema(..., description=str(HarmonicType.__doc__))
    exponents: List[float] = Schema(..., description="Exponents for this contracted shell.")
    coefficients: List[List[float]] = Schema(
        ...,
        description=
        "General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients."
    )


class ECPType(str, enum):
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
    angular_momentum: List[int] = Schema(..., description="Angular momentum (as an array of integers)")
    r_exponents: List[int] = Schema(..., description="Exponents of the 'r' term.")
    gaussian_exponents: List[float] = Schema(..., description="Exponents of the 'gaussian' term.")
    coefficients: List[List[float]] = Schema(
        ...,
        description=
        "General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients."
    )


class CenterBasis(ProtoModel):
    """
    Data for a single atom/center in a basis set.
    """
    schema_name: constr(strip_whitespace=True, regex=qcschema_output_default) = qcschema_output_default
    electron_shells: List[ElectronShell] = Schema(..., description="Electronic shells for this center.")
    ecp_electrons: int = Schema(0, "Number of electrons replace by ECP potentials.")
    ecp_potentials: Optional[List[ECPPotential]] = Schema(None, "ECPs for this center.")
