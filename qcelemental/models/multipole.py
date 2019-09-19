from enum import Enum
from typing import Dict, List, Optional

from pydantic import Schema, constr, validator

from .basemodels import ProtoModel
from .types import Array


class Singlepole(ProtoModel):
    """Model for charges, dipoles, or quadrupoles, etc."""

    angular_momentum: int = Schema(..., description="Angular momentum for this singlepole.")
    exponents: List[float] = Schema(..., description="Exponents for this singlepole.")
    geometry: Array[float] = Schema(..., description="Location of the singlepoles.")
    coefficients: List[List[float]] = Schema(..., description="Coefficients for each AM component. Psi4 AM ordering convention: https://github.com/evaleev/libint/blob/5458ab2fb2fd51dcd19f1e8122a451f2a0808074/doc/progman/progman.tex#L1006-L1008")

    @validator('geometry')
    def _must_be_3n(cls, v, values, **kwargs):
        npts = len(values['exponents'])
        try:
            v = v.reshape(npts, 3)
        except (ValueError, AttributeError):
            raise ValueError("Geometry must be castable to shape (N,3)!")
        return v

    @validator('angular_momentum')
    def _must_be_am(cls, v, values, **kwargs):
        if v < 0:
            raise ValueError(f"Positive, please: {v}")

        return v

    @validator('coefficients', whole=True)
    def _must_be_nover3_by_am(cls, v, values, **kwargs):
        npts = len(values['exponents'])
        am = values['angular_momentum']
        ncoeff = (am + 1) * (am + 2) / 2
        if len(v) != npts:
            raise ValueError(f"The length of coefficients does not match number of points. {len(values['coefficients'])} != {npts}")
        for ipts in v:
            if len(ipts) != ncoeff:
                raise ValueError(f"The length of coefficients AM does not match the AM. {len(ipts)} != {coeff}")

        return v


class Multipoles(ProtoModel):

    poles: List[Singlepole] = []
