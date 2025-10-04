from typing import Literal, Union

from pydantic import Field, field_validator

from ..v2.basis_set import BasisSet as BasisSet_v2
from .basemodels import check_convertible_version


class BasisSet(BasisSet_v2):
    schema_version: Literal[1] = Field(1)

    def convert_v(
        self, target_version: int, /
    ) -> Union["qcelemental.models.v1.BasisSet", "qcelemental.models.v2.BasisSet", "qcelemental.models._v1v2.BasisSet"]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="BasisSet") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            dself.pop("schema_name")  # changes in v2
            dself.pop("schema_version")  # changes in v2

            self_vN = qcel.models.v2.BasisSet(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.BasisSet(**dself)
        else:
            assert False, target_version

        return self_vN
