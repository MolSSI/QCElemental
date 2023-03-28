from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pytest
from pydantic import BaseModel, Field

import qcelemental as qcel
from qcelemental.testing import compare_recursive, compare_values

from .addons import serialize_extensions


@pytest.fixture(scope="function")
def doc_fixture():
    class Nest(BaseModel):
        """A nested model"""

        n: float = 56

    class X(BaseModel):
        """A Pydantic model made up of many, many different combinations of ways of mapping types in Pydantic"""

        x: int
        y: str = Field(...)
        n: Nest
        n2: Nest = Field(Nest(), description="A detailed description")
        z: float = 5
        z2: float = None
        z3: Optional[float]
        z4: Optional[float] = Field(5, description="Some number I just made up")
        z5: Optional[Union[float, int]]
        z6: Optional[List[int]]
        l: List[int]
        l2: List[Union[int, str]]
        t: Tuple[str, int]
        t2: Tuple[List[int]]
        t3: Tuple[Any]
        d: Dict[str, Any]
        dlu: Dict[Union[int, str], List[Union[int, str, float]]] = Field(..., description="this is complicated")
        dlu2: Dict[Any, List[Union[int, str, float]]]
        dlu3: Dict[str, Any]
        si: int = Field(..., description="A level of constraint", gt=0)
        sf: float = Field(None, description="Optional Constrained Number", le=100.3)

    yield X


@pytest.mark.parametrize("inp,expected", [(["AAAABBBCCDAABBB"], "ABCD"), (["ABBCcAD", str.lower], "ABCD")])
def test_unique_everseen(inp, expected):
    ue = qcel.util.unique_everseen(*inp)
    assert list(ue) == list(expected)


@pytest.mark.parametrize(
    "inp,expected",
    [
        (
            ({1: {"a": "A"}, 2: {"b": "B"}}, {2: {"c": "C"}, 3: {"d": "D"}}),
            {1: {"a": "A"}, 2: {"b": "B", "c": "C"}, 3: {"d": "D"}},
        ),
        (
            ({1: {"a": "A"}, 2: {"b": "B", "c": None}}, {2: {"c": "C"}, 3: {"d": "D"}}),
            {1: {"a": "A"}, 2: {"b": "B", "c": "C"}, 3: {"d": "D"}},
        ),
        (({1: [None, 1]}, {1: [2, 1], 3: {"d": "D"}}), {1: [2, 1], 3: {"d": "D"}}),
    ],
)
def test_updatewitherror(inp, expected):
    assert compare_recursive(expected, qcel.util.update_with_error(inp[0], inp[1]))


@pytest.mark.parametrize(
    "inp",
    [
        ({1: {"a": "A"}, 2: {"b": "B"}}, {1: {"a": "A"}, 2: {"b": "C"}}),
        ({1: {"a": "A"}, 2: {"b": "B"}}, {1: {"a": "A"}, 2: {"b": None}}),
        ({1: [None, 1]}, {1: [2, 2], 3: {"d": "D"}}),
    ],
)
def test_updatewitherror_error(inp):
    with pytest.raises(KeyError):
        qcel.util.update_with_error(inp[0], inp[1])


@pytest.mark.parametrize(
    "inp,expected",
    [
        ({"dicary": {"a": "A", "b": "B"}}, {"a": "A", "b": "B"}),
        ({"dicary": {"a": np.arange(2), "b": [1, 2]}}, {"a": [0, 1], "b": [1, 2]}),
        ({"dicary": {"c": {"a": np.arange(2), "b": [1, 2]}}}, {"c": {"a": [0, 1], "b": [1, 2]}}),
        ({"dicary": {"c": {"a": np.arange(2), "b": [1, 2]}}, "flat": True}, {"c": {"a": [0, 1], "b": [1, 2]}}),
        (
            {"dicary": {"c": {"a": np.arange(2), "b": [1, 2]}, "d": np.arange(6).reshape((2, 3))}},
            {"c": {"a": [0, 1], "b": [1, 2]}, "d": [[0, 1, 2], [3, 4, 5]]},
        ),
        (
            {"dicary": {"c": {"a": np.arange(2), "b": [1, 2]}, "d": np.arange(6).reshape((2, 3))}, "flat": True},
            {"c": {"a": [0, 1], "b": [1, 2]}, "d": [0, 1, 2, 3, 4, 5]},
        ),
        (
            {"dicary": {"a": np.arange(2), "e": ["mouse", np.arange(4).reshape(2, 2)]}},
            {"a": [0, 1], "e": ["mouse", [[0, 1], [2, 3]]]},
        ),
        (
            {"dicary": {"a": np.arange(2), "e": ["mouse", {"f": np.arange(4).reshape(2, 2)}]}},
            {"a": [0, 1], "e": ["mouse", {"f": [[0, 1], [2, 3]]}]},
        ),
        (
            {
                "dicary": {
                    "a": np.arange(2),
                    "e": ["mouse", [np.arange(4).reshape(2, 2), {"f": np.arange(6).reshape(2, 3), "g": [[11], [12]]}]],
                }
            },
            {"a": [0, 1], "e": ["mouse", [[[0, 1], [2, 3]], {"f": [[0, 1, 2], [3, 4, 5]], "g": [[11], [12]]}]]},
        ),
        (
            {"dicary": {"a": np.arange(2), "e": ["mouse", np.arange(4).reshape(2, 2)]}, "flat": True},
            {"a": [0, 1], "e": ["mouse", [0, 1, 2, 3]]},
        ),
        (
            {"dicary": {"a": np.arange(2), "e": ["mouse", {"f": np.arange(4).reshape(2, 2)}]}, "flat": True},
            {"a": [0, 1], "e": ["mouse", {"f": [0, 1, 2, 3]}]},
        ),
        (
            {
                "dicary": {
                    "a": np.arange(2),
                    "e": ["mouse", [np.arange(4).reshape(2, 2), {"f": np.arange(6).reshape(2, 3), "g": [[11], [12]]}]],
                },
                "flat": True,
            },
            {"a": [0, 1], "e": ["mouse", [[0, 1, 2, 3], {"f": [0, 1, 2, 3, 4, 5], "g": [[11], [12]]}]]},
        ),
    ],
)
def test_unnp(inp, expected):
    assert compare_recursive(expected, qcel.util.unnp(**inp), atol=1.0e-4)


def test_distance():
    def _test_distance(p1, p2, value):
        tmp = qcel.util.compute_distance(p1, p2)
        assert compare_values(value, float(tmp))

    _test_distance([0, 0, 0], [0, 0, 1], 1.0)
    _test_distance([0, 0, 0], [0, 0, 0], 0.0)

    tmp1 = np.random.rand(20, 3) * 4
    tmp2 = np.random.rand(20, 3) * 4
    np_dist = np.linalg.norm(tmp1 - tmp2, axis=1)
    ee_dist = qcel.util.compute_distance(tmp1, tmp2)
    assert np.allclose(np_dist, ee_dist)


def test_angle():
    def _test_angle(p1, p2, p3, value, degrees=True):
        tmp = qcel.util.compute_angle(p1, p2, p3, degrees=degrees)
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
        tmp = qcel.util.compute_dihedral(p1, p2, p3, p4, degrees=degrees)
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
    _test_dihedral(p1, p2, p3, [3, 2 + 1.0e-14, 0], 180)
    _test_dihedral(p1, p2, p3, [3, 2 - 1.0e-14, 0], 0)
    _test_dihedral(p1, p2, p3, [3, 2, 0 + 1.0e-14], -90)
    _test_dihedral(p1, p2, p3, [3, 2, 0 - 1.0e-14], 90)


def test_dihedral2():
    # FROM: https://stackoverflow.com/questions/20305272/

    def _test_dihedral(p1, p2, p3, p4, value, degrees=True):
        tmp = qcel.util.compute_dihedral(p1, p2, p3, p4, degrees=degrees)
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
    _test_dihedral(p3, p2, p1, p0, -71.21515114671394)

    _test_dihedral(p0, p1, p4, p5, -171.94319947953642)
    _test_dihedral(p5, p4, p1, p0, -171.94319947953642)

    _test_dihedral(p1, p4, p5, p6, 60.82226735264638)
    _test_dihedral(p6, p5, p4, p1, 60.82226735264638)

    _test_dihedral(p1, p4, p5, p7, -177.63641151521261)
    _test_dihedral(p7, p5, p4, p1, -177.63641151521261)


def test_auto_gen_doc(doc_fixture):
    assert "this is complicated" not in doc_fixture.__doc__
    qcel.util.auto_gen_docs_on_demand(doc_fixture, allow_failure=False, ignore_reapply=False)
    assert "this is complicated" in doc_fixture.__doc__
    assert "z3 : float, Optional" in doc_fixture.__doc__
    # Check that docstring does not get duplicated for some reason
    assert doc_fixture.__doc__.count("z3 : float, Optional") == 1


def test_auto_gen_doc_exiting(doc_fixture):
    doc_fixture.__doc__ = "Parameters\n"
    qcel.util.auto_gen_docs_on_demand(doc_fixture, allow_failure=False, ignore_reapply=False)
    assert "this is complicated" not in doc_fixture.__doc__


def test_auto_gen_doc_reapply_failure(doc_fixture):
    qcel.util.auto_gen_docs_on_demand(doc_fixture, allow_failure=False, ignore_reapply=False)
    with pytest.raises(ValueError):
        # Allow true here because we are testing application, not errors in the doc generation itself
        qcel.util.auto_gen_docs_on_demand(doc_fixture, allow_failure=True, ignore_reapply=False)


def test_auto_gen_doc_delete(doc_fixture):
    qcel.util.auto_gen_docs_on_demand(doc_fixture, allow_failure=False, ignore_reapply=False)
    assert "this is complicated" in doc_fixture.__doc__
    assert "A Pydantic model" in doc_fixture.__doc__
    del doc_fixture.__doc__
    assert "this is complicated" not in doc_fixture.__doc__
    assert "A Pydantic model" in doc_fixture.__doc__


@pytest.mark.parametrize(
    "obj",
    [
        5,
        1.11111,
        "hello",
        "\u0394",
        np.random.rand(4),
        {"a": 5},
        {"a": 1.111111111111},
        {"a": "hello"},
        {"a": np.random.rand(4), "b": np.array(5.1111111), "c": np.array("hello")},
        ["12345"],
        ["hello", "world"],
        [5, 123.234, "abcdé", "\u0394", "\U00000394"],
        [5, "B63", np.random.rand(4)],
        ["abcdé", {"a": np.random.rand(2), "b": np.random.rand(5)}],
        [np.array(3), np.arange(3, dtype=np.uint16), {"b": np.array(["a", "b"])}],
    ],
)
@pytest.mark.parametrize("encoding", serialize_extensions)
def test_serialization(obj, encoding):
    new_obj = qcel.util.deserialize(qcel.util.serialize(obj, encoding=encoding), encoding=encoding)
    assert compare_recursive(obj, new_obj)
