import json
import socket
from contextlib import contextmanager
from pathlib import Path

import pytest

import qcelemental
from qcelemental.util import which_import


def internet_connection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


using_web = pytest.mark.skipif(internet_connection() is False, reason="Could not connect to the internet")

using_msgpack = pytest.mark.skipif(
    which_import("msgpack", return_bool=True) is False,
    reason="Not detecting module msgpack. Install package if necessary and add to envvar PYTHONPATH",
)

using_networkx = pytest.mark.skipif(
    which_import("networkx", return_bool=True) is False,
    reason="Not detecting module networkx. Install package if necessary and add to envvar PYTHONPATH",
)

using_scipy = pytest.mark.skipif(
    which_import("scipy", return_bool=True) is False,
    reason="Not detecting module scipy. Install package if necessary and add to envvar PYTHONPATH",
)

using_nglview = pytest.mark.skipif(
    which_import("nglview", return_bool=True) is False,
    reason="Not detecting module py3Dmol. Install package if necessary and add to envvar PYTHONPATH",
)

serialize_extensions = [
    "json",
    "json-ext",
    pytest.param("msgpack", marks=using_msgpack),
    pytest.param("msgpack-ext", marks=using_msgpack),
]


@contextmanager
def xfail_on_pubchem_busy():
    try:
        yield
    except qcelemental.ValidationError as e:
        if "HTTP Error 503: PUGREST.ServerBusy" in e.message:
            pytest.xfail("Pubchem server busy")
        else:
            raise e


_data_path = Path(__file__).parent.resolve() / "qcschema_instances"


def drop_qcsk(instance, tnm: str, schema_name: str = None):
    if isinstance(instance, qcelemental.models.ProtoModel) and schema_name is None:
        schema_name = type(instance).__name__
    drop = (_data_path / schema_name / tnm).with_suffix(".json")

    with open(drop, "w") as fp:
        if isinstance(instance, qcelemental.models.ProtoModel):
            # fp.write(instance.json(exclude_unset=True, exclude_none=True))  # works but file is one-line
            instance = json.loads(instance.json(exclude_unset=True, exclude_none=True))
        elif isinstance(instance, dict):
            pass
        else:
            raise TypeError
        json.dump(instance, fp, sort_keys=True, indent=2)
