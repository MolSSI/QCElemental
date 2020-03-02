import os
from decimal import Decimal

import pytest

import qcelemental


@pytest.fixture(scope="module", params=[None, "CODATA2014", "CODATA2018"])
def contexts(request):
    if request.param:
        constants = qcelemental.PhysicalConstantsContext(request.param)
        context = request.param
    else:
        constants = qcelemental.constants
        context = constants.name

    if context == "CODATA2014":
        return (constants, "27.21138602", "10.18434/T4WW24", "uncertainty=0.000 000 17")
    elif context == "CODATA2018":
        return (constants, "27.211386245988", "", "uncertainty=0.000 000 000 053")


def test_access_1a(contexts):
    constants, _, _, _ = contexts
    assert constants.c == 299792458


def test_access_1b(contexts):
    constants, _, _, _ = contexts
    assert constants.speed_of_light_in_vacuum == 299792458


def test_access_1c(contexts):
    constants, _, _, _ = contexts
    assert constants.pc["speed of light in vacuum"].data == 299792458


def test_access_1d(contexts):
    constants, _, _, _ = contexts
    assert constants.get("speed of light in vacuum") == 299792458


def test_access_1e(contexts, request):
    constants, _, doi, _ = contexts

    qca = constants.get("speed of light in vacuum", return_tuple=True)

    assert qca.units == "m s^{-1}"
    assert qca.comment == "uncertainty=(exact)"
    assert qca.doi == doi
    assert qca.data == 299792458


def test_access_1f(contexts):
    constants, _, _, _ = contexts
    assert constants.get("speed of LIGHT in vacuum") == 299792458


def test_access_2a(contexts):
    constants, ans, _, _ = contexts
    assert constants.Hartree_energy_in_eV == float(ans)


def test_access_2b(contexts):
    constants, ans, _, _ = contexts
    assert constants.hartree2ev == float(ans)


def test_access_2c(contexts):
    constants, ans, _, _ = contexts
    assert constants.pc["hartree energy in ev"].data == Decimal(ans)


def test_access_2d(contexts):
    constants, ans, _, _ = contexts
    assert constants.get("hartree energy in ev") == float(ans)


def test_access_2e(contexts):
    constants, ans, doi, comment = contexts

    qca = constants.get("Hartree energy in eV", return_tuple=True)
    print(qca)

    assert qca.units == "eV"
    assert qca.comment == comment
    assert qca.doi == doi
    assert qca.data == Decimal(ans)


def test_access_2f(contexts):
    constants, ans, _, _ = contexts
    assert constants.get("hARTREE energy in eV") == float(ans)


def test_access_2g(contexts):
    constants, ans, _, _ = contexts
    ref = {"label": "Hartree energy in eV", "units": "eV", "data": Decimal(ans)}
    dqca = constants.get("Hartree energy in eV", return_tuple=True).dict()

    for itm in ref:
        assert ref[itm] == dqca[itm]


def test_c_header():
    from qcelemental.physical_constants.context import write_c_header

    write_c_header("CODATA2018", "header.h")
    os.remove("header.h")


@pytest.mark.xfail(True, reason="comparison data not available for installed repository", run=True, strict=False)
def test_constants_comparison():
    from qcelemental.physical_constants.context import run_comparison

    run_comparison("CODATA2014")


def test_representation():
    qcelemental.constants.string_representation()


def test_str():
    assert "PhysicalConstantsContext(" in str(qcelemental.constants)


def test_codata2022():
    with pytest.raises(KeyError) as e:
        qcelemental.PhysicalConstantsContext("CODATA2022")

    assert "only contexts {'CODATA2014', 'CODATA2018', } are currently supported" in str(e.value)


def test_codata_comparison():
    from qcelemental.physical_constants.context import run_internal_comparison

    run_internal_comparison("CODATA2014", "CODATA2018")
