import json
from pathlib import Path

import pytest

import qcelemental as qcel

from .addons import _data_path


def _example_files():
    return sorted(_data_path.glob("v*/*/*.json"))


files = _example_files()
params = files or [pytest.param(None, id="no-generated-examples")]


def _model_and_version(path: Path):
    version_name, model_name = path.relative_to(_data_path).parts[:2]
    version = int(version_name.removeprefix("v"))
    namespace = qcel.models.v1 if version == 1 else qcel.models.v2
    return getattr(namespace, model_name), version


def _schema(model, version):
    return model.schema() if version == 1 else model.model_json_schema()


def _validate_json_schema(instance, model, version):
    import jsonschema

    schema = _schema(model, version)
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    validator_class(schema).validate(instance)


@pytest.mark.parametrize("fl", params, ids=lambda fl: str(fl.relative_to(_data_path)) if fl else None)
def test_qcschema_example(fl):
    if fl is None:
        pytest.fail("No generated QCSchema examples found; run pytest --qcschema-examples first")

    model, version = _model_and_version(fl)
    raw = fl.read_text()
    data = json.loads(raw)

    instance = model.parse_raw(raw) if version == 1 else model.model_validate_json(raw)
    _validate_json_schema(data, model, version)

    if hasattr(instance, "convert_v"):
        target_version = 2 if version == 1 else 1
        converted = instance.convert_v(target_version)
        converted_model = type(converted)
        converted_data = json.loads(converted.model_dump_json(exclude_unset=True, exclude_none=True))
        _validate_json_schema(converted_data, converted_model, target_version)
