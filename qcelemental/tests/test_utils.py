import numpy as np
import pytest
import qcelemental
from qcelemental.testing import compare_recursive, compare_values


@pytest.mark.parametrize("inp,expected", [
    (['AAAABBBCCDAABBB'], 'ABCD'),
    (['ABBCcAD', str.lower], 'ABCD'),
])
def test_unique_everseen(inp, expected):
    ue = qcelemental.util.unique_everseen(*inp)
    assert list(ue) == list(expected)

@pytest.mark.parametrize("inp,expected", [
    (({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}}), {1:{"a":"A"},2:{"b":"B","c":"C"},3:{"d":"D"}}),
    (({1:{"a":"A"},2:{"b":"B","c":None}}, {2:{"c":"C"},3:{"d":"D"}}), {1:{"a":"A"},2:{"b":"B","c":"C"},3:{"d":"D"}}),
    (({1: [None, 1]}, {1: [2, 1],3:{"d":"D"}}), {1:[2, 1], 3:{"d":"D"}})
]) # yapf: disable
def test_updatewitherror(inp, expected):
    assert compare_recursive(expected, qcelemental.util.update_with_error(inp[0], inp[1]))

@pytest.mark.parametrize("inp", [
    ({1: {"a": "A"}, 2: {"b": "B"}}, {1: {"a": "A"}, 2: {"b": "C"}}),
    ({1: {"a": "A"}, 2: {"b": "B"}}, {1: {"a": "A"}, 2: {"b": None}}),
    ({1: [None, 1]}, {1: [2, 2], 3: {"d": "D"}}),
]) # yapf: disable
def test_updatewitherror_error(inp):
    with pytest.raises(KeyError):
        qcelemental.util.update_with_error(inp[0], inp[1])

@pytest.mark.parametrize("inp,expected", [
    ({'dicary': {"a":"A", "b":"B"}}, {"a":"A", "b":"B"}),
    ({'dicary': {"a":np.arange(2), "b":[1, 2]}}, {"a":[0, 1], "b":[1, 2]}),
    ({'dicary': {"c":{"a":np.arange(2), "b":[1, 2]}}}, {"c":{"a":[0, 1], "b":[1, 2]}}),
    ({'dicary': {"c":{"a":np.arange(2), "b":[1, 2]}}, 'flat': True}, {"c":{"a":[0, 1], "b":[1, 2]}}),
    ({'dicary': {"c":{"a":np.arange(2), "b":[1, 2]}, "d":np.arange(6).reshape((2, 3))}}, {"c":{"a":[0, 1], "b":[1, 2]}, "d":[[0, 1, 2], [3, 4, 5]]}),
    ({'dicary': {"c":{"a":np.arange(2), "b":[1, 2]}, "d":np.arange(6).reshape((2, 3))}, 'flat': True}, {"c":{"a":[0, 1], "b":[1, 2]}, "d":[0, 1, 2, 3, 4, 5]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", np.arange(4).reshape(2, 2)]}}, {"a": [0, 1], "e": ["mouse", [[0, 1], [2, 3]]]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", {"f": np.arange(4).reshape(2, 2)}]}}, {"a": [0, 1], "e": ["mouse", {"f": [[0, 1], [2, 3]]}]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", [np.arange(4).reshape(2, 2), {"f": np.arange(6).reshape(2, 3), "g": [[11], [12]]}]]}}, {"a": [0, 1], "e": ["mouse", [[[0, 1], [2, 3]], {"f": [[0, 1, 2], [3, 4, 5]], "g": [[11], [12]]}]]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", np.arange(4).reshape(2, 2)]}, 'flat': True}, {"a": [0, 1], "e": ["mouse", [0, 1, 2, 3]]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", {"f": np.arange(4).reshape(2, 2)}]}, 'flat': True}, {"a": [0, 1], "e": ["mouse", {"f": [0, 1, 2, 3]}]}),
    ({'dicary': {"a": np.arange(2), "e": ["mouse", [np.arange(4).reshape(2, 2), {"f": np.arange(6).reshape(2, 3), "g": [[11], [12]]}]]}, 'flat': True}, {"a": [0, 1], "e": ["mouse", [[0, 1, 2, 3], {"f": [0, 1, 2, 3, 4, 5], "g": [[11], [12]]}]]}),
]) # yapf: disable
def test_unnp(inp, expected):
    assert compare_recursive(expected, qcelemental.util.unnp(**inp), atol=1.e-4)


def test_distance():
    def _test_distance(p1, p2, value):
        tmp = qcelemental.util.compute_distance(p1, p2)
        assert compare_values(value, float(tmp))

    _test_distance([0, 0, 0], [0, 0, 1], 1.0)
    _test_distance([0, 0, 0], [0, 0, 0], 0.0)

    tmp1 = np.random.rand(20, 3) * 4
    tmp2 = np.random.rand(20, 3) * 4
    np_dist = np.linalg.norm(tmp1 - tmp2, axis=1)
    ee_dist = qcelemental.util.compute_distance(tmp1, tmp2)
    assert np.allclose(np_dist, ee_dist)


def test_angle():
    def _test_angle(p1, p2, p3, value, degrees=True):
        tmp = qcelemental.util.compute_angle(p1, p2, p3, degrees=degrees)
        assert compare_values(value, float(tmp))

    # Check all 90 degree domains
    p1 = [5, 0, 0]
    p2 = [0, 0, 0]
    p3 = [0, 2, 0]
    p4 = [0, 0, 4]
    _test_angle(p1, p2, p3, 90)
    _test_angle(p3, p2, p1, 90)

    _test_angle(p1, p2, p4, 90)
    _test_angle(p4, p2, p1, 90)

    _test_angle(p3, p2, p4, 90)
    _test_angle(p4, p2, p3, 90)
    _test_angle(p4, p2, p3, np.pi / 2, degrees=False)

    # Zero angle
    p5 = [6, 0, 0]
    _test_angle(p1, p2, p1, 0)
    _test_angle(p1, p2, p5, 0)
    _test_angle(p1, p2, p5, 0, degrees=False)

    # Linear
    p6 = [-5, 0, 0]
    p7 = [-4, 0, 0]
    _test_angle(p1, p2, p6, 180)
    _test_angle(p1, p2, p6, 180)
    _test_angle(p1, p2, p7, np.pi, degrees=False)


def test_dihedral1():
    def _test_dihedral(p1, p2, p3, p4, value, degrees=True):
        tmp = qcelemental.util.compute_dihedral(p1, p2, p3, p4, degrees=degrees)
        assert compare_values(value, float(tmp), label="test_dihedral1")

    p1 = [0, 0, 0]
    p2 = [0, 2, 0]
    p3 = [2, 2, 0]
    p4 = [2, 0, 0]
    p5 = [2, 4, 0]

    # Cis check
    _test_dihedral(p1, p2, p3, p4, 0)

    # Trans check
    _test_dihedral(p1, p2, p3, p5, 180)

    # 90 phase checks
    p6 = [2, 2, -2]
    p7 = [2, 2, 2]
    _test_dihedral(p1, p2, p3, p6, 90)
    _test_dihedral(p1, p2, p3, p7, -90)

    p8 = [0, 4, 0]
    _test_dihedral(p8, p2, p3, p6, -90)
    _test_dihedral(p8, p2, p3, p7, 90)

    # Linear checks
    _test_dihedral(p1, p2, p3, [3, 2, 0], 0)
    _test_dihedral(p1, p2, p3, [3, 2 + 1.e-14, 0], 180)
    _test_dihedral(p1, p2, p3, [3, 2 - 1.e-14, 0], 0)
    _test_dihedral(p1, p2, p3, [3, 2, 0 + 1.e-14], -90)
    _test_dihedral(p1, p2, p3, [3, 2, 0 - 1.e-14], 90)


def test_dihedral2():
    # FROM: https://stackoverflow.com/questions/20305272/

    def _test_dihedral(p1, p2, p3, p4, value, degrees=True):
        tmp = qcelemental.util.compute_dihedral(p1, p2, p3, p4, degrees=degrees)
        assert compare_values(value, float(tmp), label="test_dihedral1")

    p0 = [24.969, 13.428, 30.692]
    p1 = [24.044, 12.661, 29.808]
    p2 = [22.785, 13.482, 29.543]
    p3 = [21.951, 13.670, 30.431]
    p4 = [23.672, 11.328, 30.466]
    p5 = [22.881, 10.326, 29.620]
    p6 = [23.691, 9.935, 28.389]
    p7 = [22.557, 9.096, 30.459]

    _test_dihedral(p0, p1, p2, p3, -71.21515114671394)
    _test_dihedral(p0, p1, p4, p5, -171.94319947953642)
    _test_dihedral(p1, p4, p5, p6, 60.82226735264638)
    _test_dihedral(p1, p4, p5, p7, -177.63641151521261)
