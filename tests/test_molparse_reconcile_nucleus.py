import pytest

import qcelemental

co_dominant = (59, 27, "Co", 58.93319429, True, "")
co_dominant_mine = (59, 27, "Co", 58.93319429, True, "_mine")
co_dominant_shortmass = (59, 27, "Co", 58.933, True, "")
co60 = (60, 27, "Co", 59.93381630, True, "")
co60_mine = (60, 27, "Co", 59.93381630, True, "_mine")
co60ghost = (60, 27, "Co", 59.93381630, False, "")
co_unspecified = (-1, 27, "Co", 60.6, True, "")


@pytest.mark.parametrize(
    "inp,expected",
    [
        ({"E": "co"}, co_dominant),
        ({"Z": 27}, co_dominant),
        ({"A": 59, "Z": 27}, co_dominant),
        ({"E": "cO", "mass": 58.93319429}, co_dominant),
        ({"A": 59, "Z": 27, "E": "CO"}, co_dominant),
        ({"A": 59, "E": "cO", "mass": 58.93319429}, co_dominant),
        ({"label": "co", "verbose": 2}, co_dominant),
        ({"label": "59co"}, co_dominant),
        ({"label": "co@58.93319429"}, co_dominant),
        ({"A": 59, "Z": 27, "E": "cO", "mass": 58.93319429, "label": "co@58.93319429"}, co_dominant),
        ({"A": 59, "Z": 27, "E": "cO", "mass": 58.93319429, "label": "27@58.93319429"}, co_dominant),
        ({"label": "27"}, co_dominant),
        ({"label": "co_miNe"}, co_dominant_mine),
        ({"label": "co_mIne@58.93319429"}, co_dominant_mine),
        ({"E": "cO", "mass": 58.933}, co_dominant_shortmass),
        ({"label": "cO@58.933"}, co_dominant_shortmass),
        ({"E": "Co", "A": 60}, co60),
        ({"Z": 27, "A": 60, "real": True}, co60),
        ({"E": "Co", "A": 60}, co60),
        ({"Z": 27, "mass": 59.93381630}, co60),
        ({"A": 60, "Z": 27, "mass": 59.93381630}, co60),
        ({"label": "60Co"}, co60),
        ({"label": "27", "mass": 59.93381630}, co60),
        ({"label": "Co", "mass": 59.93381630}, co60),
        ({"A": 60, "label": "Co"}, co60),
        ({"mass": 60.6, "Z": 27}, co_unspecified),
        ({"mass": 60.6, "E": "Co"}, co_unspecified),
        ({"mass": 60.6, "label": "27"}, co_unspecified),
        ({"label": "Co@60.6"}, co_unspecified),
        ({"E": "Co", "A": 60, "real": False}, co60ghost),
        ({"A": 60, "Z": 27, "mass": 59.93381630, "real": 0}, co60ghost),
        ({"label": "@60Co"}, co60ghost),
        ({"label": "Gh(27)", "mass": 59.93381630}, co60ghost),
        ({"label": "@Co", "mass": 59.93381630}, co60ghost),
        ({"A": 60, "label": "Gh(Co)"}, co60ghost),
        ({"label": "60co_miNe"}, co60_mine),
        ({"label": "_miNe", "A": 59, "E": "Co", "speclabel": False}, co_dominant_mine),
    ],
)
def test_reconcile_nucleus(inp, expected):
    assert expected == qcelemental.molparse.reconcile_nucleus(**inp)


@pytest.mark.parametrize("inp", [{"E": "cO", "mass": 58.933, "mtol": 1.0e-4}, {"label": "27@58.933", "mtol": 1.0e-4}])
def test_reconcile_nucleus_assertionerror(inp):
    with pytest.raises(AssertionError):
        assert co_dominant_shortmass == qcelemental.molparse.reconcile_nucleus(**inp)


@pytest.mark.parametrize(
    "inp",
    [{"A": 80, "Z": 27}, {"Z": -27, "mass": 200, "nonphysical": True}, {"A": 100, "E": "He", "nonphysical": True}],
)
def test_reconcile_nucleus_notanelementerror(inp):
    with pytest.raises(qcelemental.NotAnElementError):
        qcelemental.molparse.reconcile_nucleus(**inp)


def test_reconcile_nucleus_41():
    ans = qcelemental.molparse.reconcile_nucleus(Z=27, mass=200, nonphysical=True)
    assert ans == (-1, 27, "Co", 200.0, True, "")

    ans = qcelemental.molparse.reconcile_nucleus(A=None, Z=None, E="He", mass=100, label=None, nonphysical=True)
    assert ans == (-1, 2, "He", 100.0, True, "")


@pytest.mark.parametrize(
    "inp",
    [
        {"mass": 60.6, "Z": 27, "A": 61},
        {"Z": 27, "mass": 200},
        {"Z": 27, "mass": -200, "nonphysical": True},
        {"Z": 1, "label": "he"},
        {"A": 4, "label": "3he"},
        {"label": "@U", "real": True},
        {"label": "U", "real": False},
        {"label": "_miNe", "A": 59, "E": "Co", "speclabel": True},
    ],
)
def test_reconcile_nucleus_validationerror(inp):
    with pytest.raises(qcelemental.ValidationError):
        qcelemental.molparse.reconcile_nucleus(**inp)
