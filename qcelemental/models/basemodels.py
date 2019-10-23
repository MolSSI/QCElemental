import json
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import numpy as np
from pydantic import BaseModel, BaseSettings

from qcelemental.testing import compare_recursive
from qcelemental.util import deserialize, serialize
from qcelemental.util.autodocs import AutoPydanticDocGenerator


def _proto_repr_style(self, join_str: str) -> str:
    """
    This is required to be __repr_str__ as pydantic decided to rebuild a new base
    """
    if self.__config__.repr_style == "default":
        return super().__repr_str__(join_str)
    elif self.__config__.repr_style == 'dict':
        return join_str.join(f'{k}={v}' for k, v in self.dict().items())
    else:
        raise "Invalid repr_style detected, please edit this classes config."


class ProtoModel(BaseModel):
    class Config:
        allow_mutation: bool = False
        extra: str = "forbid"
        json_encoders: Dict[str, Any] = {np.ndarray: lambda v: v.flatten().tolist()}
        serialize_default_excludes: Set = set()
        serialize_skip_defaults: bool = False
        force_skip_defaults: bool = False
        repr_style: str = 'dict'

    def __init_subclass__(cls) -> None:
        cls.__doc__ = AutoPydanticDocGenerator(cls, always_apply=True)
        cls.__repr_str__ = _proto_repr_style

    @classmethod
    def parse_raw(cls, data: Union[bytes, str], *, encoding: str = None) -> 'ProtoModel':  # type: ignore
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
    def parse_file(cls, path: Union[str, Path], *, encoding: str = None) -> 'ProtoModel':  # type: ignore
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

    def dict(self, **kwargs) -> Dict[str, Any]:
        encoding = kwargs.pop("encoding", None)

        kwargs["exclude"] = (
            (kwargs.get("exclude", None) or set()) | self.__config__.serialize_default_excludes)  # type: ignore
        kwargs.setdefault("exclude_unset", self.__config__.serialize_skip_defaults)  # type: ignore
        if self.__config__.force_skip_defaults:  # type: ignore
            kwargs["exclude_unset"] = True

        data = super().dict(**kwargs)

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
                  exclude_unset: bool = False) -> Union[bytes, str]:
        """Generates a serialized representation of the model

        Parameters
        ----------
        encoding : str
            The serialization type, available types are: {'json', 'json-ext', 'msgpack-ext'}
        include : Optional[Set[str]], optional
            Fields to be included in the serialization.
        exclude : Optional[Set[str]], optional
            Fields to be excluded in the serialization.
        exclude_unset : bool, optional
            If True, skips fields that have default values provided.

        Returns
        -------
        Union[bytes, str]
            The serialized model.
        """
        data = self.dict(include=include, exclude=exclude, exclude_unset=exclude_unset)

        return serialize(data, encoding=encoding)

    def compare(self, other: Union['ProtoModel', BaseModel], **kwargs) -> bool:
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


class AutodocBaseSettings(BaseSettings):
    def __init_subclass__(cls) -> None:
        cls.__doc__ = AutoPydanticDocGenerator(cls, always_apply=True)
