from typing import Optional

import numpy as np
from pydantic import Field, validator

from ..util import blockwise_contract, blockwise_expand
from .basemodels import ProtoModel
from .types import Array

__all__ = ["AlignmentMill"]


class AlignmentMill(ProtoModel):
    """Facilitates the application of the simple transformation operations
    defined by ``shift``, ``rotation``, ``atommap`` arrays and ``mirror``
    boolean as recipe to the data structures
    describing Cartesian molecular coordinates. Attaches functions to
    transform the geometry, element list, gradient, etc. to the
    AlignmentRecipe. When `mirror` attribute (defaults to False) active,
    then molecular system can be substantively changed by procedure.

    """

    shift: Optional[Array[float]] = Field(  # type: ignore
        None, description="Translation array (3,) for coordinates."
    )
    rotation: Optional[Array[float]] = Field(  # type: ignore
        None, description="Rotation array (3, 3) for coordinates."
    )
    atommap: Optional[Array[int]] = Field(  # type: ignore
        None, description="Atom exchange map (nat,) for coordinates."
    )
    mirror: bool = Field(False, description="Do mirror invert coordinates?")

    class Config:
        force_skip_defaults = True

    @validator("shift")
    def _must_be_3(cls, v, values, **kwargs):
        try:
            v = v.reshape(3)
        except (ValueError, AttributeError):
            raise ValueError("Shift must be castable to shape (3,)!")
        return v

    @validator("rotation")
    def _must_be_33(cls, v, values, **kwargs):
        try:
            v = v.reshape(3, 3)
        except (ValueError, AttributeError):
            raise ValueError("Rotation must be castable to shape (3, 3)!")
        return v

    ### Non-Pydantic API functions

    def pretty_print(self, label: str = "") -> str:
        width = 40
        text = []
        text.append("-" * width)
        text.append("{:^{width}}".format("AlignmentMill", width=width))
        if label:
            text.append("{:^{width}}".format(label, width=width))
        text.append("-" * width)
        text.append("Mirror:   {}".format(self.mirror))
        text.append("Atom Map: {}".format(self.atommap))
        text.append("Shift:    {}".format(self.shift))
        text.append("Rotation:")
        text.append("{}".format(self.rotation))
        text.append("-" * width)
        return "\n".join(x.rstrip() for x in text)

    def align_coordinates(self, geom, *, reverse=False) -> Array:
        """suitable for geometry or displaced geometry"""

        algeom = np.copy(geom)
        if reverse:
            algeom = algeom.dot(self.rotation)
            algeom = algeom + self.shift
            if self.mirror:
                algeom[:, 1] *= -1.0
        else:
            if self.mirror:
                algeom[:, 1] *= -1.0
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
        # alvec = np.copy(vec)
        # if self.mirror:
        #    alvec[:, 1] *= -1
        return vec.dot(self.rotation)

    def align_gradient(self, grad) -> Array:
        """suitable for vector system attached to atoms"""

        # sensible? TODO
        # algrad = np.copy(grad)
        # if self.mirror:
        #    algrad[:, 1] *= -1
        algrad = grad.dot(self.rotation)
        algrad = algrad[self.atommap]

        return algrad

    def align_hessian(self, hess) -> Array:
        blocked_hess = blockwise_expand(hess, (3, 3), False)
        alhess = np.zeros_like(blocked_hess)

        nat = blocked_hess.shape[0]
        for iat in range(nat):
            for jat in range(nat):
                alhess[iat, jat] = (self.rotation.T).dot(blocked_hess[iat, jat].dot(self.rotation))

        alhess = alhess[np.ix_(self.atommap, self.atommap)]

        alhess = blockwise_contract(alhess)
        return alhess

    def align_vector_gradient(self, mu_derivatives):
        """Align the nuclear gradients of vector components (e.g. dipole derivatives)."""
        # Input data is assumed to be organized into outermost x, y, z vector components.
        # Organize derivatives for each atom into 3x3 and transform it.
        mu_x, mu_y, mu_z = mu_derivatives
        nat = mu_x.shape[0] // 3
        al_mu = np.zeros((3, 3 * nat))

        Datom = np.zeros((3, 3))  # atom whose nuclear derivatives are taken
        for at in range(nat):
            Datom.fill(0)
            Datom[0, :] = mu_x[3 * self.atommap[at] : 3 * self.atommap[at] + 3]
            Datom[1, :] = mu_y[3 * self.atommap[at] : 3 * self.atommap[at] + 3]
            Datom[2, :] = mu_z[3 * self.atommap[at] : 3 * self.atommap[at] + 3]
            Datom[:] = np.dot(self.rotation.T, np.dot(Datom, self.rotation))
            al_mu[0, 3 * at : 3 * at + 3] = Datom[0, :]
            al_mu[1, 3 * at : 3 * at + 3] = Datom[1, :]
            al_mu[2, 3 * at : 3 * at + 3] = Datom[2, :]
        return al_mu

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
