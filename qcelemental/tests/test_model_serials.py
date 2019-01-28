import numpy as np
import pytest
from pydantic import ValidationError

from qcelemental.models import (Molecule, ResultInput, Result, OptimizationInput, Optimization, ComputeError,
                                FailedOperation)


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
    return {"id": "12345a",
            "driver": "gradient",
            "model": {"method": "filler"}}


@pytest.fixture
def res_success():
    return {"success": True,
            "return_result": 536.2}


@pytest.fixture
def res_failure(res_success):
    return {**res_success,
            "success": False,
            "error": {
                "error_type": "expected_testing_error",
                "error_message": "If you see this, its all good"
            }}


@pytest.fixture
def opti_input():
    return {"input_specification": {
        "driver": "gradient",
        "model": {"method": "filler"}
    }}


@pytest.fixture
def opti_success(water, result_input, res_success):
    res = Result(molecule=water, **result_input, **res_success)
    return {"success": True,
            "trajectory": [res]*3,
            "final_molecule": water,
            "energies": [1.0, 2.0, 3.0]}


@pytest.fixture
def opti_failure(opti_success):
    return {**opti_success,
            "success": False,
            "error": {
                "error_type": "expected_testing_error",
                "error_message": "If you see this, its all good"
            }}


def test_molecule_serialization(water):
    assert isinstance(water.dict(), dict)
    assert isinstance(water.json(), str)


def test_result_pass_serialization(water, result_input, res_success):
    res_in = ResultInput(molecule=water, **result_input)
    assert isinstance(res_in.dict(), dict)
    assert isinstance(res_in.json(), str)
    res_out = Result(molecule=water, **result_input, **res_success)
    assert isinstance(res_out.dict(), dict)
    assert isinstance(res_out.json(), str)


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


def test_optimization_wrong_serialization(water, opti_input, opti_failure):
    opti_out = Optimization(initial_molecule=water, **opti_input, **opti_failure)
    assert isinstance(opti_out.error, ComputeError)
    assert isinstance(opti_out.dict(), dict)
    out_json = opti_out.json()
    assert isinstance(out_json, str)
    assert 'its all good' in out_json


def test_failed_operation(water, result_input, opti_failure):
    failed = FailedOperation(garbage=water, **result_input, **opti_failure)
    assert isinstance(failed.error, ComputeError)
    assert isinstance(failed.dict(), dict)
    failed_json = failed.json()
    assert isinstance(failed_json, str)
    assert 'its all good' in failed_json
