import pytest

from qcelemental.models import (
    AtomicInput,
    AtomicResult,
    AtomicResultProperties,
    ComputeError,
    FailedOperation,
    Molecule,
    Optimization,
    OptimizationInput,
    ProtoModel,
    Provenance,
)


def test_result_properties_default_skip():

    obj = AtomicResultProperties(scf_one_electron_energy="-5.0")

    assert pytest.approx(obj.scf_one_electron_energy) == -5.0

    assert obj.dict().keys() == {"scf_one_electron_energy"}


def test_result_properties_default_repr():
    obj = AtomicResultProperties(scf_one_electron_energy="-5.0")
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
    assert (
        str(fail_op)
        == """FailedOperation(error=ComputeError(error_type='random_error', error_message='this is bad'))"""
    )


def test_repr_result():

    result = AtomicInput(
        **{"driver": "gradient", "model": {"method": "UFF"}, "molecule": {"symbols": ["He"], "geometry": [0, 0, 0]}}
    )
    assert "molecule_hash" in str(result)
    assert "molecule_hash" in repr(result)
    assert "'gradient'" in str(result)


def test_repr_optimization():

    opt = OptimizationInput(
        **{
            "input_specification": {"driver": "gradient", "model": {"method": "UFF"}},
            "initial_molecule": {"symbols": ["He"], "geometry": [0, 0, 0]},
        }
    )

    assert "molecule_hash" in str(opt)
    assert "molecule_hash" in repr(opt)


def test_model_custom_repr():
    class Model(ProtoModel):
        a: int

        def __repr__(self) -> str:
            return "Hello world!"

    m = Model(a=5)
    assert repr(m) == "Hello world!"
    assert "Model(" in str(m)

    class Model2(ProtoModel):
        a: int

        def __str__(self) -> str:
            return "Hello world!"

    m = Model2(a=5)
    assert "Model2(" in repr(m)
    assert str(m) == "Hello world!"
