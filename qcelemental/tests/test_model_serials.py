import numpy as np
import pytest
from pydantic import ValidationError
from qcelemental.models import (ComputeError, FailedOperation, Molecule, Optimization, OptimizationInput, Result,
                                ResultInput)
from qcelemental.util import provenance_stamp


@pytest.fixture
def water():
    """Water dimer minima"""
    return Molecule.from_data(
        """
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
        "return_result": 536.2,
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


def test_driverenum_derivative_int(water, result_input):
    res = ResultInput(molecule=water, **result_input)

    assert res.driver == 'gradient'
    assert res.driver.derivative_int() == 1


def test_molecule_serialization(water):
    assert isinstance(water.dict(), dict)
    assert isinstance(water.json(), str)
    assert isinstance(water.json_dict(), dict)


def test_molecule_sparsity():
    m = Molecule(**{"symbols": ["He"], "geometry": [0, 0, 0], "identifiers": {"molecular_formula": "He"}})
    assert set(m.dict()["identifiers"].keys()) == {"molecular_formula"}
    assert set(m.identifiers.dict().keys()) == {"molecular_formula"}


def test_result_pass_serialization(water, result_input, res_success):
    res_in = ResultInput(molecule=water, **result_input)
    assert isinstance(res_in.dict(), dict)
    assert isinstance(res_in.json(), str)
    assert isinstance(res_in.json_dict(), dict)

    res_out = Result(molecule=water, **result_input, **res_success)
    assert isinstance(res_out.dict(), dict)
    assert isinstance(res_out.json(), str)
    assert isinstance(res_out.json_dict(), dict)


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
    assert isinstance(opti_in.json_dict(), dict)

    opti_out = Optimization(initial_molecule=water, **opti_input, **opti_success)
    assert isinstance(opti_out.dict(), dict)
    assert isinstance(opti_out.json(), str)
    assert isinstance(opti_out.json_dict(), dict)


def test_failed_operation(water, result_input):
    failed = FailedOperation(
        extras={"garbage": water},
        input_data=result_input,
        error={"error_type": "expected_testing_error",
               "error_message": "If you see this, its all good"})
    assert isinstance(failed.error, ComputeError)
    assert isinstance(failed.dict(), dict)
    failed_json = failed.json()
    assert isinstance(failed_json, str)
    assert 'its all good' in failed_json
