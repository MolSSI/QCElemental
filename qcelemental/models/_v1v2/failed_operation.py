from typing import Any, Dict, Optional, Union

from pydantic import Field, field_validator

from ..v2.basemodels import ProtoModel
from ..v2.failed_operation import ComputeError
from .basemodels import check_convertible_version


class FailedOperation(ProtoModel):
    id: Optional[str] = Field(None)
    input_data: Any = Field(None)
    success: bool = Field(False)
    error: ComputeError = Field(...)
    extras: Optional[Dict[str, Any]] = Field({})

    def __repr_args__(self) -> "ReprArgs":
        return [("error", self.error)]

    def convert_v(self, target_version: int, /) -> Union[
        "qcelemental.models.v1.FailedOperation",
        "qcelemental.models.v2.FailedOperation",
        "qcelemental.models._v1v2.FailedOperation",
    ]:
        """Convert to instance of particular QCSchema version."""
        import qcelemental as qcel

        if check_convertible_version(target_version, error="FailedOperation") == "self":
            return self

        dself = self.model_dump()
        if target_version == 2:
            self_vN = qcel.models.v2.FailedOperation(**dself)
        elif target_version == 1:
            self_vN = qcel.models.v1.FailedOperation(**dself)
        else:
            assert False, target_version

        return self_vN
