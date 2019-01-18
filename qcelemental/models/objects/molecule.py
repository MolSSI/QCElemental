"""
Molecule Object Model
"""

import numpy as np
from pydantic import BaseModel, validator
from typing import List, Tuple


class NPArray(np.ndarray):
    @classmethod
    def get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            v = np.array(v)
        except:
            raise RuntimeError("Could not cast {} to NumPy Array!".format(v))
        return v

class Identifiers(BaseModel):
    """Canonical chemical identifiers"""
    molecule_hash: str = None
    molecular_formula: str = None
    smiles: str = None
    inchi: str = None
    inchikey: str = None
    canonical_explicit_hydrogen_smiles: str = None
    canonical_isomeric_explicit_hydrogen_mapped_smiles: str = None
    canonical_isomeric_explicit_hydrogen_smiles: str = None
    canonical_isomeric_smiles: str = None
    canonical_smiles: str = None

    class Config:
        allow_extra = True


# Outstanding issues:
# required_definitions
# hash_fields
# Numpy arrays or lists?
class Molecule(BaseModel):
    id: str = None
    symbols: List[str]
    geometry: NPArray = ...
    masses: List[float] = None
    name: str = None
    identifiers: Identifiers = None
    comment: str = None
    charge: float = 0.0
    multiplicity: int = 1
    real: List[bool] = None
    connectivity: List[Tuple[int, int, int]] = []
    fragments: List[List[int]] = None
    fragment_charges: List[float] = None
    fragment_multiplicities: List[int] = None
    fix_com: bool = False
    fix_orientation: bool = False
    provenance: dict = {}

    @validator('geometry')
    def must_be_3n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        try:
            v = v.reshape(n, 3)
            if v.shape != (n, 3):
                raise ValueError()
        except (ValueError, AttributeError):
            raise ValueError("Geometry must be castable to shape (N,3)!")
        return v

    @validator('masses', 'real')
    def must_be_n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        if len(v) != n:
            raise ValueError("Masses and Real must be same number of entries as Symbols")
        return v

    @validator('fragment_charges', 'fragment_multiplicities')
    def must_be_n_frag(cls, v, values, **kwargs):
        if 'fragments' in values:
            n = values['fragments']
            if len(v) != n:
                raise ValueError("Fragment Charges and Fragment Multiplicities"
                                 " must be same number of entries as Fragments")
        else:
            raise ValueError("Cannot have Fragment Charges or Fragment Multiplicities "
                             "without Fragments")
        return v

    @validator('connectivity')
    def min_zero(cls, v):
        if v < 0:
            raise ValueError("Connectivity entries must be greater than 0")
        return v

    @property
    def hash_fields(self):
        return ["symbols", "masses", "charge", "multiplicity", "real", "geometry", "fragments", "fragment_charges",
                "fragment_multiplicities", "connectivity"]

    class Config:
        json_encoders = {
            np.ndarray: lambda v: v.flatten().tolist(),
        }
