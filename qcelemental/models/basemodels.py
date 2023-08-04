import json
import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union, List, Callable

import numpy as np

from pydantic_settings import BaseSettings  # remove when QCFractal merges `next`
from pydantic import BaseModel, ConfigDict

from qcelemental.util import deserialize, serialize
from qcelemental.util.autodocs import AutoPydanticDocGenerator  # remove when QCFractal merges `next`


def _repr(self) -> str:
    return f'{self.__repr_name__()}({self.__repr_str__(", ")})'


class ExtendedConfigDict(ConfigDict, total=False):
    serialize_default_excludes: Set
    """Add items to exclude from serialization"""

    serialize_skip_defaults: bool
    """When serializing, ignore default values (i.e. those not set by user)"""

    force_skip_defaults: bool
    """Manually force defaults to not be included in output dictionary"""

    canonical_repr: bool
    """Use canonical representation of the molecules"""

    repr_style: Union[List[str], Callable]
    """Representation styles"""


class ProtoModel(BaseModel):
    model_config = ExtendedConfigDict(
        frozen=True,
        extra="forbid",
        serialize_default_excludes=set(),
        serialize_skip_defaults=False,
        force_skip_defaults=False
    )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.__base_doc__ = ""  # remove when QCFractal merges `next`

        if "pydantic" in cls.__repr__.__module__:
            cls.__repr__ = _repr

        if "pydantic" in cls.__str__.__module__:
            cls.__str__ = _repr

    @classmethod
    def parse_raw(cls, data: Union[bytes, str], *, encoding: Optional[str] = None) -> "ProtoModel":  # type: ignore
        r"""
        Parses raw string or bytes into a Model object.

        This overwrites the deprecated parse_file of v2 Pydantic to eventually call parse_model or parse_model_json,
        but is kept to preserve our own API

        May also be deprecated from QCElemental in time

        Parameters
        ----------
        data
            A serialized data blob to be deserialized into a Model.
        encoding
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

        if encoding.endswith(("json", "javascript", "pickle")):
            # return super().parse_raw(data, content_type=encoding)
            return cls.model_validate_json(data)
        elif encoding in ["msgpack-ext", "json-ext", "msgpack"]:
            obj = deserialize(data, encoding)
        else:
            raise TypeError(f"Content type '{encoding}' not understood.")

        return cls.model_validate(obj)

    @classmethod
    def parse_file(cls, path: Union[str, Path], *, encoding: Optional[str] = None) -> "ProtoModel":  # type: ignore
        r"""Parses a file into a Model object.

        This overwrites the deprecated parse_file of v2 Pydantic to eventually call parse_model or parse_model_json,
        but is kept to preserve our own API

        May also be deprecated from QCElemental in time

        Parameters
        ----------
        path
            The path to the file.
        encoding
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
        warnings.warn('The `dict` method is deprecated; use `model_dump` instead.', DeprecationWarning)
        return self.model_dump(**kwargs)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        encoding = kwargs.pop("encoding", None)

        kwargs["exclude"] = (
            kwargs.get("exclude", None) or set()
        ) | self.model_config["serialize_default_excludes"]  # type: ignore
        kwargs.setdefault("exclude_unset", self.model_config["serialize_skip_defaults"])  # type: ignore
        if self.model_config["force_skip_defaults"]:  # type: ignore
            kwargs["exclude_unset"] = True

        data = super().model_dump(**kwargs)

        if encoding is None:
            return data
        elif encoding == "json":
            return json.loads(serialize(data, encoding="json"))
        else:
            raise KeyError(f"Unknown encoding type '{encoding}', valid encoding types: 'json'.")

    def serialize(
        self,
        encoding: str,
        *,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
    ) -> Union[bytes, str]:
        r"""Generates a serialized representation of the model

        Parameters
        ----------
        encoding
            The serialization type, available types are: {'json', 'json-ext', 'msgpack-ext'}
        include
            Fields to be included in the serialization.
        exclude
            Fields to be excluded in the serialization.
        exclude_unset
            If True, skips fields that have default values provided.
        exclude_defaults
            If True, skips fields that have set or defaulted values equal to the default.
        exclude_none
            If True, skips fields that have value ``None``.

        Returns
        -------
        ~typing.Union[bytes, str]
            The serialized model.
        """

        kwargs = {}
        if include:
            kwargs["include"] = include
        if exclude:
            kwargs["exclude"] = exclude
        if exclude_unset:
            kwargs["exclude_unset"] = exclude_unset
        if exclude_defaults:
            kwargs["exclude_defaults"] = exclude_defaults
        if exclude_none:
            kwargs["exclude_none"] = exclude_none

        data = self.model_dump(**kwargs)

        return serialize(data, encoding=encoding)

    def json(self, **kwargs):
        # Alias JSON here from BaseModel to reflect dict changes
        warnings.warn('The `json` method is deprecated; use `model_dump_json` instead.', DeprecationWarning)
        return self.model_dump_json(**kwargs)

    def model_dump_json(self, **kwargs):
        return self.serialize("json", **kwargs)

    def compare(self, other: Union["ProtoModel", BaseModel], **kwargs) -> bool:
        r"""Compares the current object to the provided object recursively.

        Parameters
        ----------
        other
            The model to compare to.
        **kwargs
            Additional kwargs to pass to :func:`~qcelemental.compare_recursive`.

        Returns
        -------
        bool
            True if the objects match.
        """
        from ..testing import compare_recursive

        return compare_recursive(self, other, **kwargs)


# remove when QCFractal merges `next`
class AutodocBaseSettings(BaseSettings):
    def __init_subclass__(cls) -> None:
        cls.__doc__ = AutoPydanticDocGenerator(cls, always_apply=True)


qcschema_draft = "http://json-schema.org/draft-04/schema#"
