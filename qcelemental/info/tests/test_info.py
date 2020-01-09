import pytest

from qcelemental.info import dft_info


@pytest.mark.parametrize(
    "functional,ansatz", [("svwn", 0), ("b3lyp", 1), ("b3lyp-d3", 1), ("b3lyp-nlc", 1), ("dsd-blyp", 1)]
)
def test_dft_info_names(functional, ansatz):
    assert dft_info.get(functional).ansatz == ansatz
