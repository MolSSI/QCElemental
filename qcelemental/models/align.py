import json

import numpy as np
from pydantic import BaseModel, validator

from ..util import blockwise_expand, blockwise_contract
from .common_models import (NDArray, NDArrayInt, ndarray_encoder)


class AlignmentMill(BaseModel):
    """Facilitates the application of the simple transformation operations
    defined by namedtuple of arrays as recipe to the data structures
    describing Cartesian molecular coordinates. Attaches functions to
    transform the geometry, element list, gradient, etc. to the
    AlignmentRecipe. When `mirror` attribute (defaults to False) active,
    then molecular system can be substantively changed by procedure.

    """
    shift: NDArray
    rotation: NDArray
    atommap: NDArrayInt
    mirror: bool = False

    class Config:
        json_encoders = {**ndarray_encoder}
        allow_mutation = False
        extra = "forbid"

    @validator('shift', whole=True)
    def must_be_3(cls, v, values, **kwargs):
        try:
            v = v.reshape(3)
        except (ValueError, AttributeError):
            raise ValueError("Shift must be castable to shape (3,)!")
        return v

    @validator('rotation', whole=True)
    def must_be_33(cls, v, values, **kwargs):
        try:
            v = v.reshape(3, 3)
        except (ValueError, AttributeError):
            raise ValueError("Rotation must be castable to shape (3, 3)!")
        return v

    def dict(self, *args, **kwargs):
        return super().dict(*args, **{**kwargs, **{"skip_defaults": False}})

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))


### Non-Pydantic API functions

    def __str__(self, label: str = '') -> str:
        width = 40
        text = []
        text.append('-' * width)
        text.append('{:^{width}}'.format('AlignmentMill', width=width))
        if label:
            text.append('{:^{width}}'.format(label, width=width))
        text.append('-' * width)
        text.append('Mirror:   {}'.format(self.mirror))
        text.append('Atom Map: {}'.format(self.atommap))
        text.append('Shift:    {}'.format(self.shift))
        text.append('Rotation:')
        text.append('{}'.format(self.rotation))
        text.append('-' * width)
        return ('\n'.join(text))

    def align_coordinates(self, geom, *, reverse=False) -> NDArray:
        """suitable for geometry or displaced geometry"""

        algeom = np.copy(geom)
        if reverse:
            algeom = algeom.dot(self.rotation)
            algeom = algeom + self.shift
            if self.mirror:
                algeom[:, 1] *= -1.
        else:
            if self.mirror:
                algeom[:, 1] *= -1.
            algeom = algeom - self.shift
            algeom = algeom.dot(self.rotation)
        algeom = algeom[self.atommap, :]
        # mirror-wise, rsm/msr == rms/msr

        return algeom

    def align_atoms(self, ats):
        """suitable for masses, symbols, Zs, etc."""

        return ats[self.atommap]

    def align_vector(self, vec):
        """suitable for vector attached to molecule"""

        # sensible? TODO
        #alvec = np.copy(vec)
        #if self.mirror:
        #    alvec[:, 1] *= -1
        return vec.dot(self.rotation)

    def align_gradient(self, grad) -> NDArray:
        """suitable for vector system attached to atoms"""

        # sensible? TODO
        #algrad = np.copy(grad)
        #if self.mirror:
        #    algrad[:, 1] *= -1
        algrad = grad.dot(self.rotation)
        algrad = algrad[self.atommap]

        return algrad

    def align_hessian(self, hess) -> NDArray:
        blocked_hess = blockwise_expand(hess, (3, 3), False)
        alhess = np.zeros_like(blocked_hess)

        nat = blocked_hess.shape[0]
        for iat in range(nat):
            for jat in range(nat):
                alhess[iat, jat] = (self.rotation.T).dot(blocked_hess[iat, jat].dot(self.rotation))

        alhess = alhess[np.ix_(self.atommap, self.atommap)]

        alhess = blockwise_contract(alhess)
        return alhess

    def align_system(self, geom, mass, elem, elez, uniq, *, reverse: bool = False):
        """For AlignmentRecipe `ar`, apply its translation, rotation, and atom map."""

        nugeom = self.align_coordinates(geom, reverse=reverse)
        numass = self.align_atoms(mass)
        nuelem = self.align_atoms(elem)
        nuelez = self.align_atoms(elez)
        nuuniq = self.align_atoms(uniq)

        return nugeom, numass, nuelem, nuelez, nuuniq

    def align_mini_system(self, geom, uniq, *, reverse: bool = False):
        """For AlignmentRecipe `ar`, apply its translation, rotation, and atom map."""

        nugeom = self.align_coordinates(geom, reverse=reverse)
        nuuniq = self.align_atoms(uniq)

        return nugeom, nuuniq
