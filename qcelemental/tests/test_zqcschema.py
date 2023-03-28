import json

import pytest

import qcelemental as qcel

from .addons import _data_path


@pytest.fixture(scope="module")
def qcschema_models():
    return {md.__name__: json.loads(md.schema_json()) for md in qcel.models.qcschema_models()}


files = sorted(_data_path.rglob("*.json"))
ids = [fl.parent.stem + "_" + fl.stem[5:] for fl in files]


@pytest.mark.parametrize("fl", files, ids=ids)
def test_qcschema(fl, qcschema_models):
    import jsonschema

    model = fl.parent.stem
    instance = json.loads(fl.read_text())

    res = jsonschema.validate(instance, qcschema_models[model])
    assert res is None
