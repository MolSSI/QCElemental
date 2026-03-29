import os
import warnings
from typing import Any, Dict, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing_extensions import Annotated, get_args


def generate_caster(dtype):
    def cast_to_np(v):
        if isinstance(v, (float, dict)):
            return v
        elif isinstance(v, int):
            return float(v)

        try:
            v = np.asarray(v, dtype=dtype)
        except ValueError:
            raise ValueError(f"Could not cast {v} to NumPy Array!")
        return v

    return cast_to_np


class ValidatableArrayAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, source, _):
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * Data will be cast to ndarrays with the correct dtype
        * `ndarrays` instances will be parsed as `ndarrays` and cast to the correct dtype
        """
        shape, dtype_alias = get_args(source)
        dtype = get_args(dtype_alias)[0]
        validator = generate_caster(dtype)
        # When serializing to JSON, flatten and to list it
        serializer = core_schema.plain_serializer_function_ser_schema(lambda v: v.flatten().tolist(), when_used="json")
        # Affix dtype metadata to the schema we'll use in serialization
        schema = core_schema.no_info_plain_validator_function(
            validator, serialization=serializer, metadata={"dtype": dtype}
        )
        return schema

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> Dict[str, Any]:
        # Get the dtype metadata from our original schema
        if os.environ.get("SPHINX_BUILD") == "1":
            dt = float
        else:
            dt = _core_schema["metadata"]["dtype"]
        output_schema = {}
        if dt is int or np.issubdtype(dt, np.integer):
            items = {"type": "number", "multipleOf": 1.0}
        elif dt is float or np.issubdtype(dt, np.floating):
            items = {"type": "number"}
        elif dt is str or np.issubdtype(dt, np.bytes_):
            items = {"type": "string"}
        elif dt is bool or np.issubdtype(dt, np.bool_):
            items = {"type": "boolean"}
        else:
            items = {"type": "Unknown"}
            warnings.warn(f"Unknown dtype to handle type [{dt}] for array. May result in weird serialization or typing")
        output_schema.update(type="array", items=items)
        return output_schema


class NestedDataAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        An annotation for generic, nested data

        This will handle nested dictionaries and lists on both validation and serialization

        On validation:
          * Data in lists or other sequences will be cast to ndarrays
          * `ndarrays` instances will be left as `ndarrays`

        On serialization:
          * Numpy arrays will be flattened
        """

        def _recursive_flatten(a):
            """Recursively flattens numpy arrays that are part of lists, dicts, and other sequences/mappings"""

            if isinstance(a, str):
                return a
            if isinstance(a, np.ndarray):
                return a.flatten().tolist()
            if isinstance(a, Mapping):
                return {k: _recursive_flatten(v) for k, v in a.items()}
            if isinstance(a, Sequence):
                return [_recursive_flatten(x) for x in a]

            return a

        def _from_input(v, convert_list=True):
            if isinstance(v, (float, str, np.ndarray)):
                return v
            if isinstance(v, int):
                return float(v)
            elif isinstance(v, Sequence) and convert_list:
                return np.asarray(v)
            elif isinstance(v, Mapping):
                return {k: _from_input(v, False) for k, v in v.items()}
            else:
                return v

        return core_schema.no_info_plain_validator_function(
            _from_input,
            serialization=core_schema.plain_serializer_function_ser_schema(_recursive_flatten, when_used="json"),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> Dict[str, Any]:
        return {}


Array = Annotated[NDArray, ValidatableArrayAnnotation]
NestedData = Annotated[Any, NestedDataAnnotation]
