import pytest

import qcelemental
from qcelemental.testing import compare, compare_values


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("@ca_miNe", {"E": "ca", "Z": None, "user": "_miNe", "A": None, "real": False, "mass": None}),
        ("Gh(Ca_mine)", {"E": "Ca", "Z": None, "user": "_mine", "A": None, "real": False, "mass": None}),
        ("@Ca_mine@1.07", {"E": "Ca", "Z": None, "user": "_mine", "A": None, "real": False, "mass": 1.07}),
        ("Gh(cA_MINE@1.07)", {"E": "cA", "Z": None, "user": "_MINE", "A": None, "real": False, "mass": 1.07}),
        ("@40Ca_mine@1.07", {"E": "Ca", "Z": None, "user": "_mine", "A": 40, "real": False, "mass": 1.07}),
        ("Gh(40Ca_mine@1.07)", {"E": "Ca", "Z": None, "user": "_mine", "A": 40, "real": False, "mass": 1.07}),
        ("444lu333@4.0", {"E": "lu", "Z": None, "user": "333", "A": 444, "real": True, "mass": 4.0}),
        ("@444lu333@4.4", {"E": "lu", "Z": None, "user": "333", "A": 444, "real": False, "mass": 4.4}),
        ("8i", {"E": "i", "Z": None, "user": None, "A": 8, "real": True, "mass": None}),
        ("53_mI4", {"Z": 53, "E": None, "user": "_mI4", "A": None, "real": True, "mass": None}),
        ("@5_MINEs3@4.4", {"Z": 5, "E": None, "user": "_MINEs3", "A": None, "real": False, "mass": 4.4}),
        ("Gh(555_mines3@0.1)", {"Z": 555, "E": None, "user": "_mines3", "A": None, "real": False, "mass": 0.1}),
    ],
)
def test_parse_nucleus_label(inp, expected):
    lbl_A, lbl_Z, lbl_E, lbl_mass, lbl_real, lbl_user = qcelemental.molparse.nucleus.parse_nucleus_label(inp)

    assert compare(expected["real"], lbl_real, inp + " real")
    assert compare(expected["A"], lbl_A, inp + " A")
    assert compare(expected["Z"], lbl_Z, inp + " Z")
    assert compare(expected["E"], lbl_E, inp + " symbol")
    assert compare(expected["user"], lbl_user, inp + " user")
    assert compare_values(expected["mass"], lbl_mass, inp + " mass", passnone=True, atol=1.0e-6)


@pytest.mark.parametrize("inp", ["1L1A1B1"])
def test_parse_nucleus_label_error(inp):
    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.nucleus.parse_nucleus_label(inp)
