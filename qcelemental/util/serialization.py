from typing import Any, Dict

import numpy as np
from pydantic.json import pydantic_encoder

from .importing import which_import

try:
    import msgpack

    _has_msgpack = True
except ModuleNotFoundError:
    msgpack = None

    _has_msgpack = True

_msgpack_which_msg = "Please install via `conda install msgpack-python`."


def msgpack_encode(obj: Any) -> Any:
    """
    Encodes an object using pydantic and NumPy array serialization techniques suitable for msgpack.

    Parameters
    ----------
    obj : Any
        Any object that can be serialized with pydantic and NumPy encoding techniques.

    Returns
    -------
    Any
        A msgpack compatible form of the object.
    """

    # First try pydantic base objects
    try:
        return pydantic_encoder(obj)
    except TypeError:
        pass

    if isinstance(obj, np.ndarray):
        if obj.shape:
            data = {b"_nd_": True, b"dtype": obj.dtype.str, b"data": np.ascontiguousarray(obj).tobytes()}
            return data

        else:
            # Converts np.array(5) -> 5
            return obj.tolist()

    return obj


def msgpack_decode(obj: Any) -> Any:
    """
    Decodes a msgpack objects from a dictionary representation.

    Parameters
    ----------
    obj : Any
        An encoded object, likely a dictionary.

    Returns
    -------
    Any
        The decoded form of the object.
    """

    if b"_nd_" in obj:
        return np.frombuffer(obj[b"data"], dtype=obj[b"dtype"])

    return obj


def msgpack_dumps(data: Dict[str, Any]) -> bytes:
    """Safe serialization of a Python dictionary to msgpack binary representation using all known encoders.

    Parameters
    ----------
    data : Dict[str, Any]
        A encodable dictionary.

    Returns
    -------
    bytes
        A msgpack representation of the data in bytes.
    """
    which_import("msgpack", raise_error=True, raise_msg=_msgpack_which_msg)

    return msgpack.dumps(data, default=msgpack_encode, use_bin_type=True)


def msgpack_loads(data: bytes) -> Dict[str, Any]:
    """Deserializes a msgpack byte representation of known objects into those objects.

    Parameters
    ----------
    data : bytes
        The serialized msgpack byte array.

    Returns
    -------
    Dict[str, Any]
        A dictionary of objects.
    """
    which_import("msgpack", raise_error=True, raise_msg=_msgpack_which_msg)

    return msgpack.loads(data, object_hook=msgpack_decode, raw=False)
