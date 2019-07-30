import json
from typing import Any, Dict, Optional, Set, Union
from pathlib import Path

import numpy as np
from pydantic import BaseModel

from qcelemental.util import msgpack_dumps, msgpack_loads


class ProtoModel(BaseModel):
    class Config:
        allow_mutation = False
        extra = "forbid"
        json_encoders = {np.ndarray: lambda v: v.flatten().tolist()}
        serialize_default_excludes = set()
        serialize_skip_defaults = False

    @classmethod
    def parse_raw(cls, data: Union[bytes, str], *, content_type: str = None) -> 'Model':
        """
        Parses raw string or bytes into a Model object.

        Parameters
        ----------
        data : Union[bytes, str]
            A serialized data blob to be deserialized into a Model.
        content_type : str, optional
            The type of the serialized array, available types are: {'json', 'msgpack', 'pickle'}

        Returns
        -------
        Model
            The requested model from a serialized format.
        """

        if content_type is None:
            if isinstance(data, str):
                content_type = "json"
            elif isinstance(data, bytes):
                content_type = "msgpack"
            else:
                raise TypeError("Input is neither str nor bytes, please specify a content_type.")

        if content_type.endswith(('json', 'javascript', 'pickle')):
            return super().parse_raw(data, content_type=content_type)
        elif content_type == "msgpack":
            obj = cls._parse_msgpack(data)
        else:
            raise TypeError(f"Content type '{content_type}' not understood.")

        return cls.parse_obj(obj)

    @classmethod
    def parse_file(cls, path: Union[str, Path], *, content_type: str = None) -> 'Model':
        """Parses a file into a Model object.

        Parameters
        ----------
        path : Union[str, Path]
            The path to the file.
        content_type : str, optional
            The type of the files, available types are: {'json', 'msgpack', 'pickle'}. Attempts to
            automatically infer the file type from disk.

        Returns
        -------
        Model
            The requested model from a serialized format.

        """
        path = Path(path)
        if content_type is None:
            if path.suffix in [".json", ".js"]:
                content_type = "json"
            elif path.suffix in [".msgpack"]:
                content_type = "msgpack"
            elif path.suffix in [".pickle"]:
                content_type = "pickle"
            else:
                raise TypeError("Could not infer `content_type`, please provide a `content_type` for this file.")

        return cls.parse_raw(path.read_bytes(), content_type=content_type)

    def dict(self, *args, **kwargs):
        kwargs["exclude"] = (kwargs.get("exclude", None) or set()) | self.__config__.serialize_default_excludes
        kwargs.setdefault("skip_defaults", self.__config__.serialize_skip_defaults)
        return super().dict(*args, **kwargs)

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))

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

    def to_string(self):
        return f"{self.__class__.__name__}"