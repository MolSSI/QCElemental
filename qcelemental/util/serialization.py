import json
from typing import Any, Union, Dict, Optional

import numpy as np
from pydantic.json import pydantic_encoder

from .importing import which_import

try:
    import msgpack
except ModuleNotFoundError:
    pass

try:
    import yaml
except ModuleNotFoundError:
    pass

_msgpack_which_msg = "Please install via `conda install msgpack-python`."
_pyyaml_which_msg = "Please install via `pip install pyyaml` or `conda install pyyaml`."

## MSGPackExt


def msgpackext_encode(obj: Any) -> Any:
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
            if len(obj.shape) > 1:
                data[b"shape"] = obj.shape
            return data

        else:
            # Converts np.array(5) -> 5
            return obj.tolist()

    return obj


def msgpackext_decode(obj: Any) -> Any:
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
        arr = np.frombuffer(obj[b"data"], dtype=obj[b"dtype"])
        if b"shape" in obj:
            arr.shape = obj[b"shape"]

        return arr

    return obj


def msgpackext_dumps(data: Any, **kwargs: Optional[Dict[str, Any]]) -> bytes:
    """Safe serialization of a Python object to msgpack binary representation using all known encoders.
    For NumPy, encodes a specialized object format to encode all shape and type data.

    Parameters
    ----------
    data : Any
        A encodable python object.
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructor.

    Returns
    -------
    bytes
        A msgpack representation of the data in bytes.
    """
    which_import("msgpack", raise_error=True, raise_msg=_msgpack_which_msg)
    print("WTF!!!")

    use_bin_type = kwargs.pop("use_bin_type", True)

    return msgpack.dumps(data, default=msgpackext_encode, use_bin_type=use_bin_type, **kwargs)


def msgpackext_loads(data: bytes, **kwargs: Dict[str, Any]) -> Any:
    """Deserializes a msgpack byte representation of known objects into those objects.

    Parameters
    ----------
    data : bytes
        The serialized msgpack byte array.
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructor.

    Returns
    -------
    Any
        The deserialized Python objects.
    """
    which_import("msgpack", raise_error=True, raise_msg=_msgpack_which_msg)

    raw = kwargs.pop("raw", False)

    return msgpack.loads(data, object_hook=msgpackext_decode, raw=raw, **kwargs)


## JSON Ext


class JSONExtArrayEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        try:
            return pydantic_encoder(obj)
        except TypeError:
            pass

        if isinstance(obj, np.ndarray):
            if obj.shape:
                data = {"_nd_": True, "dtype": obj.dtype.str, "data": np.ascontiguousarray(obj).tobytes().hex()}
                if len(obj.shape) > 1:
                    data["shape"] = obj.shape
                return data

            else:
                # Converts np.array(5) -> 5
                return obj.tolist()

        return json.JSONEncoder.default(self, obj)


def jsonext_decode(obj: Any) -> Any:

    if "_nd_" in obj:
        arr = np.frombuffer(bytes.fromhex(obj["data"]), dtype=obj["dtype"])
        if "shape" in obj:
            arr.shape = obj["shape"]

        return arr

    return obj


def jsonext_dumps(data: Any, **kwargs: Optional[Dict[str, Any]]) -> str:
    """Safe serialization of Python objects to JSON string representation using all known encoders.
    The JSON serializer uses a custom array syntax rather than flat JSON lists.

    Parameters
    ----------
    data : Any
        A encodable python object.
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructor

    Returns
    -------
    str
        A JSON representation of the data.
    """

    return json.dumps(data, cls=JSONExtArrayEncoder, **kwargs)


def jsonext_loads(data: Union[str, bytes]) -> Any:
    """Deserializes a json representation of known objects into those objects.

    Parameters
    ----------
    data : str or bytes
        The byte-serialized JSON blob.

    Returns
    -------
    Any
        The deserialized Python objects.
    """

    return json.loads(data, object_hook=jsonext_decode)


## JSON


class JSONArrayEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        try:
            return pydantic_encoder(obj)
        except TypeError:
            pass

        if isinstance(obj, np.ndarray):
            if obj.shape:
                return obj.ravel().tolist()
            else:
                return obj.tolist()

        return json.JSONEncoder.default(self, obj)


def json_dumps(data: Any, **kwargs: Optional[Dict[str, Any]]) -> str:
    """Safe serialization of a Python dictionary to JSON string representation using all known encoders.

    Parameters
    ----------
    data : Any
        A encodable python object.
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructor

    Returns
    -------
    str
        A JSON representation of the data.
    """

    return json.dumps(data, cls=JSONArrayEncoder, **kwargs)


def json_loads(data: str) -> Any:
    """Deserializes a json representation of known objects into those objects.

    Parameters
    ----------
    data : str
        The serialized JSON blob.

    Returns
    -------
    Any
        The deserialized Python objects.
    """

    # Doesn't hurt anything to try to load JSONext as well
    return json.loads(data, object_hook=jsonext_decode)


## YAML


def yaml_encode(dumper: "yaml.dumper.SafeDumper", obj: np.ndarray) -> "yaml.nodes.Node":
    """
    Encodes a NumPy ndarray for YAML.

    Parameters
    ----------
    dumper: yaml.dumper.SafeDumper
        A PyYAML SafeDumper object
    obj : np.ndarray
        A NumPy ndarray object

    Returns
    -------
    yaml.nodes.Node
        A YAML node representing the object.
    """

    if obj.shape:
        return dumper.represent_list(obj.ravel().tolist())
    else:
        # Converts np.array(5) -> 5
        return dumper.represent_data(obj.tolist())


def safe_dump(data, stream=None, sort_keys=False, **kwargs):
    """Mimics yaml.safe_dump with support for numpy.ndarray encoding. If stream is None, return
    the produced string instead. Order is preserved by default."""
    which_import("yaml", raise_error=True, raise_msg=_pyyaml_which_msg)

    class SafeDumper(yaml.SafeDumper):
        ...

    SafeDumper.add_representer(np.ndarray, yaml_encode)
    return yaml.dump(data, stream=stream, Dumper=SafeDumper, sort_keys=sort_keys, **kwargs)


def yaml_dump(data: Any, **kwargs: Optional[Dict[str, Any]]) -> str:
    """Safe serialization of a Python dictionary to YAML string representation.

    Parameters
    ----------
    data : Any
        An encodable python object.
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructor

    Returns
    -------
    str
        A YAML representation of the data.
    """
    return safe_dump(data, **kwargs)


def yaml_load(data: str) -> Any:
    """Deserializes a yaml representation of known objects into those objects.

    Parameters
    ----------
    data : str
        The serialized YAML blob.

    Returns
    -------
    Any
        The deserialized Python objects.
    """
    which_import("yaml", raise_error=True, raise_msg=_pyyaml_which_msg)

    return yaml.safe_load(data)


## Helper functions


def serialize(data: Any, encoding: str, **kwargs: Optional[Dict[str, Any]]) -> Union[str, bytes]:
    """Encoding Python objects using the provided encoder.

    Parameters
    ----------
    data : Any
        A encodable python object.
    encoding : str
        The type of encoding to perform: {'json', 'json-ext', 'yaml', 'msgpack-ext'}
    **kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to pass to the constructors.

    Returns
    -------
    Union[str, bytes]
        A serialized representation of the data.

    """
    if encoding.lower() == "json":
        return json_dumps(data, **kwargs)
    elif encoding.lower() == "json-ext":
        return jsonext_dumps(data, **kwargs)
    elif encoding.lower() == "yaml":
        return yaml_dump(data, **kwargs)
    elif encoding.lower() == "msgpack-ext":
        return msgpackext_dumps(data, **kwargs)
    else:
        raise KeyError(
            f"Encoding '{encoding}' not understood, valid options: 'json', 'json-ext', 'yaml', 'msgpack-ext'"
        )


def deserialize(blob: Union[str, bytes], encoding: str) -> Any:
    """Encoding Python objects using .

    Parameters
    ----------
    blob : Union[str, bytes]
        The serialized data.
    encoding : str
        The type of encoding of the blob: {'json', 'json-ext', 'msgpack'}

    Returns
    -------
    Any
        The deserialized Python objects.
    """
    if encoding.lower() == "json":
        assert isinstance(blob, str)
        return json_loads(blob)
    elif encoding.lower() == "json-ext":
        assert isinstance(blob, (str, bytes))
        return jsonext_loads(blob)
    elif encoding.lower() == "yaml":
        assert isinstance(blob, str)
        return yaml_load(blob)
    elif encoding.lower() in ["msgpack", "msgpack-ext"]:
        assert isinstance(blob, bytes)
        return msgpackext_loads(blob)
    else:
        raise KeyError(f"Encoding '{encoding}' not understood, valid options: 'json', 'json-ext', 'msgpack-ext'")
