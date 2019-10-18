from typing import Dict, List

import numpy as np
import pytest

from qcelemental.models import (ComputeError, FailedOperation, Molecule, Optimization, OptimizationInput, ProtoModel,
                                Provenance, Result, ResultInput, ResultProperties)
from qcelemental.models.types import Array
from qcelemental.util import provenance_stamp

from .addons import serialize_extensions, using_msgpack


class TrialModel(ProtoModel):
    a: Array[float] = np.array(3)  # type: ignore
    b: List[Array[float]] = [np.random.rand(3)]  # type: ignore
    c: Dict[str, int] = {"hi": 3}
    d: Dict[str, Array[float]] = {"hi": np.random.rand(3)}  # type: ignore


@pytest.fixture
def water():
    """Water dimer minima"""
    return Molecule.from_data("""
        0 1
        O  -1.551007  -0.114520   0.000000
        H  -1.934259   0.762503   0.000000
        H  -0.599677   0.040712   0.000000
        --
        O   1.350625   0.111469   0.000000
        H   1.680398  -0.373741  -0.758561
        H   1.680398  -0.373741   0.758561
        """,
                              dtype="psi4",
                              orient=True)


@pytest.fixture
def result_input():
    return {
        "id": "5c754f049642c7c861d67de5",
        "driver": "gradient",
        "model": {
            "method": "filler"
        },
    }


@pytest.fixture
def res_success():
    return {
        "success": True,
        "return_result": [536.2, 546.2, 556.2],
        "properties": {
            "scf_one_electron_energy": 5
        },
        "provenance": provenance_stamp("QCEl")
    }


@pytest.fixture
def res_failure(res_success):
    return {
        **res_success, "success": False,
        "error": {
            "error_type": "expected_testing_error",
            "error_message": "If you see this, its all good"
        }
    }


@pytest.fixture
def opti_input():
    return {"input_specification": {"driver": "gradient", "model": {"method": "filler"}}}


@pytest.fixture
def opti_success(water, result_input, res_success):
    res = Result(molecule=water, **result_input, **res_success)
    return {
        "success": True,
        "trajectory": [res] * 3,
        "final_molecule": water,
        "energies": [1.0, 2.0, 3.0],
        "provenance": provenance_stamp("QCEl")
    }


@pytest.mark.parametrize("encoding", serialize_extensions)
def test_proto_file(tmp_path, encoding):
    obj = TrialModel(a=np.array(3), b=[np.random.rand(3)], c={"hi": 3}, d={"hi": np.random.rand(3)})

    p = tmp_path / ("data.dat")
    if "msgpack" in encoding:
        p.write_bytes(obj.serialize(encoding))
    else:
        p.write_text(obj.serialize(encoding))

    obj2 = TrialModel.parse_file(p, encoding=encoding)

    assert obj.compare(obj2)


def test_driverenum_derivative_int(water, result_input):
    res = ResultInput(molecule=water, **result_input)

    assert res.driver == 'gradient'
    assert res.driver.derivative_int() == 1


def test_molecule_serialization_types(water):
    assert isinstance(water.dict(), dict)
    assert isinstance(water.json(), str)


@pytest.mark.parametrize("encoding", serialize_extensions)
def test_molecule_serialization(water, encoding):
    blob = water.serialize(encoding)
    assert water.compare(Molecule.parse_raw(blob, encoding=encoding))


@pytest.mark.parametrize("dtype, filext", [
    ("json", "json"),
    pytest.param("msgpack", "msgpack", marks=using_msgpack),
])
def test_protomodel_to_from_file(tmp_path, dtype, filext):

    benchmol = Molecule.from_data("""
    O 0 0 0
    H 0 1.5 0
    H 0 0 1.5
    """)

    p = tmp_path / ("water." + filext)
    benchmol.to_file(p)

    mol = Molecule.parse_file(p)

    assert mol.compare(benchmol)


def test_molecule_skip_defaults(water):
    mol = Molecule(**{"symbols": ["He"], "geometry": [0, 0, 0]}, validate=False)
    assert {"symbols", "geometry"} == mol.dict().keys()


def test_molecule_sparsity():
    m = Molecule(**{"symbols": ["He"], "geometry": [0, 0, 0], "identifiers": {"molecular_formula": "He"}})
    assert set(m.dict()["identifiers"].keys()) == {"molecular_formula"}
    assert set(m.identifiers.dict().keys()) == {"molecular_formula"}


def test_result_pass_serialization(water, result_input, res_success):
    res_in = ResultInput(molecule=water, **result_input)
    assert isinstance(res_in.dict(), dict)
    assert isinstance(res_in.json(), str)

    res_out = Result(molecule=water, **result_input, **res_success)
    assert isinstance(res_out.dict(), dict)
    assert isinstance(res_out.json(), str)


def test_result_sparsity(water, result_input, res_success):
    res_in = ResultInput(molecule=water, **result_input)
    assert set(res_in.dict()["model"].keys()) == {"method", "basis"}


def test_result_wrong_serialization(water, result_input, res_failure):
    res_out = Result(molecule=water, **result_input, **res_failure)
    assert isinstance(res_out.error, ComputeError)
    assert isinstance(res_out.dict(), dict)
    out_json = res_out.json()
    assert isinstance(out_json, str)
    assert 'its all good' in out_json


def test_optimization_pass_serialization(water, opti_input, opti_success):
    opti_in = OptimizationInput(initial_molecule=water, **opti_input)
    assert isinstance(opti_in.dict(), dict)
    assert isinstance(opti_in.json(), str)

    opti_out = Optimization(initial_molecule=water, **opti_input, **opti_success)
    assert isinstance(opti_out.dict(), dict)
    assert isinstance(opti_out.json(), str)


def test_failed_operation(water, result_input):
    failed = FailedOperation(extras={"garbage": water},
                             input_data=result_input,
                             error={
                                 "error_type": "expected_testing_error",
                                 "error_message": "If you see this, its all good"
                             })
    assert isinstance(failed.error, ComputeError)
    assert isinstance(failed.dict(), dict)
    failed_json = failed.json()
    assert isinstance(failed_json, str)
    assert 'its all good' in failed_json


def test_default_skip():

    obj = ResultProperties(scf_one_electron_energy="-5.0")

    assert pytest.approx(obj.scf_one_electron_energy) == -5.0

    assert obj.dict().keys() == {"scf_one_electron_energy"}


def test_result_properties_default_repr():
    obj = ResultProperties(scf_one_electron_energy="-5.0")
    assert "none" not in str(obj).lower()
    assert "scf_one_electron_energy" in str(obj)
    assert len(str(obj)) < 100
    assert len(repr(obj)) < 100


def test_repr_provenance():

    prov = Provenance(creator="qcel", version="v0.3.2")

    assert "qcel" in str(prov)
    assert "qcel" in repr(prov)


def test_repr_compute_error():
    ce = ComputeError(error_type="random_error", error_message="this is bad")

    assert "random_error" in str(ce)
    assert "random_error" in repr(ce)


def test_repr_failed_op():
    fail_op = FailedOperation(error=ComputeError(error_type="random_error", error_message="this is bad"))

    assert "random_error" in str(fail_op)
    assert "random_error" in repr(fail_op)


def test_repr_result():

    result = ResultInput(**{
        "driver": "gradient",
        "model": {
            "method": "UFF"
        },
        "molecule": {
            "symbols": ["He"],
            "geometry": [0, 0, 0]
        }
    })
    assert "UFF" in str(result)
    assert "UFF" in repr(result)


def test_repr_optimization():

    opt = OptimizationInput(
        **{
            "input_specification": {
                "driver": "gradient",
                "model": {
                    "method": "UFF"
                },
            },
            "initial_molecule": {
                "symbols": ["He"],
                "geometry": [0, 0, 0]
            }
        })

    assert "UFF" in str(opt)
    assert "UFF" in repr(opt)
