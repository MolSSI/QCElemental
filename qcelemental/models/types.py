from typing import Any, Dict
from typing_extensions import Annotated, get_args

import numpy as np
from numpy.typing import NDArray
from pydantic_core import core_schema


def generate_caster(dtype):
    def cast_to_np(v):
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
        serializer = core_schema.plain_serializer_function_ser_schema(lambda v: v.flatten().tolist())
        # Affix dtype metadata to the schema we'll use in serialization
        schema = core_schema.no_info_plain_validator_function(
            validator,
            serialization=serializer,
            metadata={"dtype": dtype})
        return schema

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> Dict[str, Any]:
        # Old __modify_schema__ method from v1 setup in v2 and customized for our purposes
        # Get the dtype metadata from our original schema
        dt = _core_schema["metadata"]["dtype"]
        output_schema = {}
        if dt is int or np.issubdtype(dt, np.integer):
            items = {"type": "number", "multipleOf": 1.0}
        elif dt is float or np.issubdtype(dt, np.floating):
            items = {"type": "number"}
        elif dt is str or np.issubdtype(dt, np.string_):
            items = {"type": "string"}
        elif dt is bool or np.issubdtype(dt, np.bool_):
            items = {"type": "boolean"}
        output_schema.update(type="array", items=items)
        return output_schema


Array = Annotated[NDArray, ValidatableArrayAnnotation]
