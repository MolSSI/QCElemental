from typing import Literal, Union

from pydantic import Field, field_validator

from ..v2.molecule import Molecule as Molecule_v2
from .basemodels import check_convertible_version


class Molecule(Molecule_v2):
    # remember, QCSchema:Molecule versions 1:2 and 2:3
    schema_version: Literal[2] = Field(2)

    # to exclude abc, try
    # https://github.com/pydantic/pydantic/discussions/6699#discussioncomment-14441081

    @field_validator("schema_version", mode="before")
    @classmethod
    def _validate_schver(cls, v):
        # validator assignment (w/before) needed b/c v2.Molecule constructor sets v=3
        v = 2
        return v

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.Molecule", "qcelemental.models.v2.Molecule", "qcelemental.models._v1v2.Molecule"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="Molecule") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            # below is assignment rather than popping so Mol() records as set and future Mol.model_dump() includes the field.
            #   needed for QCEngine Psi4.
            dself["schema_version"] = 3

            self_vN = qcel.models.v2.Molecule(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.Molecule(**dself)
        else:
            assert False, target_version

        return self_vN
