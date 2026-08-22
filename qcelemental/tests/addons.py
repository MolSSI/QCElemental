import json
import os
import re
import socket
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

import qcelemental
from qcelemental.util import which_import


def internet_connection():
    try:
        scc = socket.create_connection(("www.google.com", 80))
    except OSError:
        scc.close()
        return False
    else:
        scc.close()
        return True


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

using_qcmb = pytest.mark.skipif(
    which_import("qcmanybody", return_bool=True) is False,
    reason="Not detecting module QCManyBody. Install package if necessary and add to envvar PYTHONPATH",
)

using_schrodinger = pytest.mark.skipif(
    which_import("schrodinger.structure", return_bool=True) is False,
    reason="Not detecting the Schrodinger Python API. Run tests from a Schrodinger Python environment.",
)

py37_skip = pytest.mark.skipif(sys.version_info.minor < 8, reason="Needs Python 3.8 features")

using_pydv1 = pytest.mark.skipif(sys.version_info.minor > 13, reason="QCSchema v1 models (Pyd v1 API) need Py <=3.14")

serialize_extensions = [
    "json",
    "json-ext",
    pytest.param("msgpack", marks=using_msgpack),
    pytest.param("msgpack-ext", marks=using_msgpack),
]


@contextmanager
def xfail_on_pubchem_busy():
    import qcelemental

    try:
        yield
    except qcelemental.ValidationError as e:
        if "HTTP Error 503: PUGREST.ServerBusy" in e.message:
            pytest.xfail("Pubchem server busy")
        else:
            raise e


_data_path = Path(__file__).parent.resolve() / "qcschema_instances"


def _qcschema_example_name(test_name: str) -> str:
    """Remove the model-family parameter from a pytest node name."""

    name = re.sub(r"\[(?:None|v1|v2)(?:-|(?=\]))", "[", test_name, count=1)
    name = name.replace("[]", "")
    return f"qcelemental-{name.replace('/', '_')}"


def drop_qcsk(instance, tnm: str, schema_name: str = None, *, qcschema_version: int = None):
    """Write a QCSchema example when ``--qcschema-examples`` is active.

    The model family is inferred for Pydantic models. Raw dictionaries must
    supply ``qcschema_version`` explicitly because their Python type carries
    no model-family information.
    """

    if os.environ.get("QCELEMENTAL_GENERATE_QCSCHEMA_EXAMPLES") != "1":
        return

    import qcelemental

    if isinstance(instance, qcelemental.models.v2.ProtoModel):
        inferred_version = 2
        is_model = True
    elif sys.version_info < (3, 14) and isinstance(instance, qcelemental.models.v1.ProtoModel):
        inferred_version = 1
        is_model = True
    elif isinstance(instance, dict):
        if qcschema_version not in (1, 2):
            raise ValueError("Raw dictionary QCSchema examples require qcschema_version=1 or 2")
        inferred_version = qcschema_version
        is_model = False
    else:
        raise TypeError(f"QCSchema example must be a model or dictionary, not {type(instance)!r}")

    if qcschema_version is not None and qcschema_version != inferred_version:
        raise ValueError(
            f"Explicit QCSchema version {qcschema_version} does not match inferred version {inferred_version}"
        )
    if is_model and schema_name is None:
        schema_name = type(instance).__name__
    if schema_name is None:
        raise ValueError("Raw dictionary QCSchema examples require schema_name")

    drop = (_data_path / f"v{inferred_version}" / schema_name / _qcschema_example_name(tnm)).with_suffix(".json")
    drop.parent.mkdir(parents=True, exist_ok=True)

    with open(drop, "w") as fp:
        if is_model:
            instance = json.loads(instance.model_dump_json(exclude_unset=True, exclude_none=True))
        json.dump(instance, fp, sort_keys=True, indent=2)
        fp.write("\n")


@pytest.fixture(scope="function", params=[None, "v1", "v2"])
def Molecule(request):
    # for Molecule, qcsk v1 & v2 are schema_version v2 & v3
    if request.param == "v1":
        if sys.version_info >= (3, 14):
            pytest.skip("no QCSchema v1 with py314+")
        else:
            return qcelemental.models.v1.Molecule
    elif request.param == "v2":
        return qcelemental.models.v2.Molecule
    else:
        if sys.version_info >= (3, 14):
            pytest.skip("no QCSchema v1 with py314+")
        else:
            return qcelemental.models.Molecule


@pytest.fixture(scope="function", params=[None, "v1", "v2"])
def schema_versions(request):
    if request.param == "v1":
        if sys.version_info >= (3, 14):
            pytest.skip("no QCSchema v1 with py314+")
        else:
            return qcelemental.models.v1
    elif request.param == "v2":
        return qcelemental.models.v2
    else:
        if sys.version_info >= (3, 14):
            pytest.skip("no QCSchema v1 with py314+")
        else:
            return qcelemental.models
