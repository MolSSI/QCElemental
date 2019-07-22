from typing import Any, Dict, Optional, Set

import numpy as np
from pydantic import BaseModel

from qcelemental.util import msgpack_dumps, msgpack_loads


class ProtoModel(BaseModel):
    class Config:
        allow_mutation = False
        extras = "forbid"
        json_encoders = {np.ndarray: lambda v: v.flatten().tolist()}
        default_excludes = set()

    def dict(self, *args, **kwargs):
        kwargs["exclude"] = (kwargs.pop("exclude", None) or set()) | self.__config__.default_excludes
        return super().dict(*args, **kwargs)

    def msgpack(self,
                *,
                include: Optional[Set[str]] = None,
                exclude: Optional[Set[str]] = None,
                skip_defaults: bool = False) -> bytes:
        """Generates a msgpack serialized representation of the model

        Parameters
        ----------
        include : Optional[Set[str]], optional
            Fields to be included in the serialization.
        exclude : Optional[Set[str]], optional
            Fields to be excluded in the serialization.
        skip_defaults : bool, optional
            If True, skips fields that have default values provided.

        Returns
        -------
        bytes
            The msgpack serialization of the model.
        """
        data = self.dict(include=include, exclude=exclude, skip_defaults=skip_defaults)

        return msgpack_dumps(data)

    @classmethod
    def _parse_msgpack(cls, data: bytes) -> Dict[str, Any]:
        return msgpack_loads(data)
