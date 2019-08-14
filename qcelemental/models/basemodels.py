import json
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import numpy as np
from pydantic import BaseModel

from qcelemental.testing import compare_recursive
from qcelemental.util import deserialize, serialize


class ProtoModel(BaseModel):
    class Config:
        allow_mutation = False
        extra = "forbid"
        json_encoders = {np.ndarray: lambda v: v.flatten().tolist()}
        serialize_default_excludes = set()
        serialize_skip_defaults = False

    @classmethod
    def parse_raw(cls, data: Union[bytes, str], *, encoding: str = None) -> 'Model':
        """
        Parses raw string or bytes into a Model object.

        Parameters
        ----------
        data : Union[bytes, str]
            A serialized data blob to be deserialized into a Model.
        encoding : str, optional
            The type of the serialized array, available types are: {'json', 'json-ext', 'msgpack-ext', 'pickle'}

        Returns
        -------
        Model
            The requested model from a serialized format.
        """

        if encoding is None:
            if isinstance(data, str):
                encoding = "json"
            elif isinstance(data, bytes):
                encoding = "msgpack-ext"
            else:
                raise TypeError("Input is neither str nor bytes, please specify an encoding.")

        if encoding.endswith(('json', 'javascript', 'pickle')):
            return super().parse_raw(data, content_type=encoding)
        elif encoding in ["msgpack-ext", "json-ext"]:
            obj = deserialize(data, encoding)
        else:
            raise TypeError(f"Content type '{encoding}' not understood.")

        return cls.parse_obj(obj)

    @classmethod
    def parse_file(cls, path: Union[str, Path], *, encoding: str = None) -> 'Model':
        """Parses a file into a Model object.

        Parameters
        ----------
        path : Union[str, Path]
            The path to the file.
        encoding : str, optional
            The type of the files, available types are: {'json', 'msgpack', 'pickle'}. Attempts to
            automatically infer the file type from the file extension if None.

        Returns
        -------
        Model
            The requested model from a serialized format.

        """
        path = Path(path)
        if encoding is None:
            if path.suffix in [".json", ".js"]:
                encoding = "json"
            elif path.suffix in [".msgpack"]:
                encoding = "msgpack-ext"
            elif path.suffix in [".pickle"]:
                encoding = "pickle"
            else:
                raise TypeError("Could not infer `encoding`, please provide a `encoding` for this file.")

        return cls.parse_raw(path.read_bytes(), encoding=encoding)

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        encoding = kwargs.pop("encoding", None)

        kwargs["exclude"] = (kwargs.get("exclude", None) or set()) | self.__config__.serialize_default_excludes
        kwargs.setdefault("skip_defaults", self.__config__.serialize_skip_defaults)
        data = super().dict(*args, **kwargs)

        if encoding is None:
            return data
        elif encoding == "json":
            return json.loads(serialize(data, encoding="json"))
        else:
            raise KeyError(f"Unknown encoding type '{encoding}', valid encoding types: 'json'.")

    def serialize(self,
                  encoding: str,
                  *,
                  include: Optional[Set[str]] = None,
                  exclude: Optional[Set[str]] = None,
                  skip_defaults: bool = False) -> Union[bytes, str]:
        """Generates a serialized representation of the model

        Parameters
        ----------
        encoding : str
            The serialization type, available types are: {'json', 'json-ext', 'msgpack-ext'}
        include : Optional[Set[str]], optional
            Fields to be included in the serialization.
        exclude : Optional[Set[str]], optional
            Fields to be excluded in the serialization.
        skip_defaults : bool, optional
            If True, skips fields that have default values provided.

        Returns
        -------
        Union[bytes, str]
            The serialized model.
        """
        data = self.dict(include=include, exclude=exclude, skip_defaults=skip_defaults)

        return serialize(data, encoding=encoding)

    def compare(self, other: 'Model', **kwargs) -> bool:
        """Compares the current object to the provided object recursively.

        Parameters
        ----------
        other : Model
            The model to compare to.
        **kwargs
            Additional kwargs to pass to ``qcelemental.compare_recursive``.

        Returns
        -------
        bool
            True if the objects match.
        """
        return compare_recursive(self, other, **kwargs)

    def to_string(self):  # lgtm [py/inheritance/incorrect-overridden-signature]
        return f"{self.__class__.__name__}"
