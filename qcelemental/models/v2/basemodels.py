import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

from pydantic import BaseModel, ConfigDict

from qcelemental.models import QCEL_V1V2_SHIM_CODE

from ...util import deserialize, serialize


def _repr(self) -> str:
    return f'{self.__repr_name__()}({self.__repr_str__(", ")})'


class ProtoModel(BaseModel):
    """QCSchema extension of pydantic.BaseModel."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

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
        warnings.warn("The `dict` method is deprecated; use `model_dump` instead.", DeprecationWarning, stacklevel=2)

        if "encoding" in kwargs:
            kwargs["mode"] = kwargs.pop("encoding")

        return self.model_dump(**kwargs)

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

    # UNCOMMENT IF NEEDED FOR UPGRADE REDO!!!
    def json(self, **kwargs):
        # Alias JSON here from BaseModel to reflect dict changes
        warnings.warn(
            "The `json` method is deprecated; use `model_dump_json` instead.", DeprecationWarning, stacklevel=2
        )
        return self.model_dump_json(**kwargs)

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
        from ...testing import compare_recursive

        return compare_recursive(self, other, **kwargs)

    @classmethod
    def _merge_config_with(cls, *args, **kwargs):
        """
        Helper function to merge protomodel's config with other args

        args: other ConfigDict instances or equivalent dicts
        kwargs: Keys to add into the dictionary raw
        """
        output_dict = {**cls.model_config}
        for arg in args:  # Handle other dicts first
            output_dict.update(arg)
        # Update any specific keywords
        output_dict.update(kwargs)
        # Finally, check against the Extended Config Dict
        return ConfigDict(**output_dict)


def check_convertible_version(ver: int, error: str):
    """Standardize the version/error handling for v2 QCSchema."""

    if ver == 1:
        return True
    elif ver == 2:
        return "self"
    elif ver == QCEL_V1V2_SHIM_CODE:
        # signal to create the emergency _v1v2 objects defined for some models
        return True
    else:
        raise ValueError(f"QCSchema {error} version={ver} does not exist for conversion.")


qcschema_draft = "http://json-schema.org/draft-04/schema#"
