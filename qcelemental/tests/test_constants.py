import os
from decimal import Decimal

import pytest

import qcelemental

_pc_default = "2014"
_ctxt = ["default", "2014", "2018"]


@pytest.fixture(scope="module")
def constantss():
    return {
        "default": qcelemental.constants,
        "2014": qcelemental.PhysicalConstantsContext("CODATA2014"),
        "2018": qcelemental.PhysicalConstantsContext("CODATA2018"),
    }


@pytest.mark.parametrize("context", _ctxt)
def test_access_1a(constantss, context):
    assert constantss[context].c == 299792458


@pytest.mark.parametrize("context", _ctxt)
def test_access_1b(constantss, context):
    assert constantss[context].speed_of_light_in_vacuum == 299792458


@pytest.mark.parametrize("context", _ctxt)
def test_access_1c(constantss, context):
    assert constantss[context].pc["speed of light in vacuum"].data == 299792458


@pytest.mark.parametrize("context", _ctxt)
def test_access_1d(constantss, context):
    assert constantss[context].get("speed of light in vacuum") == 299792458


@pytest.mark.parametrize("context", _ctxt)
def test_access_1e(constantss, context):
    if context == "2014" or (context == "default" and _pc_default == "2014"):
        doi = "10.18434/T4WW24"
    elif context == "2018" or (context == "default" and _pc_default == "2018"):
        doi = ""

    qca = constantss[context].get("speed of light in vacuum", return_tuple=True)

    assert qca.units == "m s^{-1}"
    assert qca.comment == "uncertainty=(exact)"
    assert qca.doi == doi
    assert qca.data == 299792458


@pytest.mark.parametrize("context", _ctxt)
def test_access_1f(constantss, context):
    assert constantss[context].get("speed of LIGHT in vacuum") == 299792458


_eV_2014 = "27.21138602"
_eV_2018 = "27.211386245988"
_eV_ans = [
    ("default", {"2014": _eV_2014, "2018": _eV_2018}[_pc_default]),
    ("2014", _eV_2014),
    ("2018", _eV_2018),
]


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2a(constantss, context, ans):
    assert constantss[context].Hartree_energy_in_eV == float(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2b(constantss, context, ans):
    assert constantss[context].hartree2ev == float(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2c(constantss, context, ans):
    assert constantss[context].pc["hartree energy in ev"].data == Decimal(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2d(constantss, context, ans):
    assert constantss[context].get("hartree energy in ev") == float(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2e(constantss, context, ans):
    if context == "2014" or (context == "default" and _pc_default == "2014"):
        doi = "10.18434/T4WW24"
        comment = "uncertainty=0.000 000 17"
    elif context == "2018" or (context == "default" and _pc_default == "2018"):
        doi = ""
        comment = "uncertainty=0.000 000 000 053"

    qca = constantss[context].get("Hartree energy in eV", return_tuple=True)
    print(qca)

    assert qca.units == "eV"
    assert qca.comment == comment
    assert qca.doi == doi
    assert qca.data == Decimal(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2f(constantss, context, ans):
    assert constantss[context].get("hARTREE energy in eV") == float(ans)


@pytest.mark.parametrize("context,ans", _eV_ans)
def test_access_2g(constantss, context, ans):
    ref = {"label": "Hartree energy in eV", "units": "eV", "data": Decimal(ans)}
    dqca = constantss[context].get("Hartree energy in eV", return_tuple=True).dict()

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
