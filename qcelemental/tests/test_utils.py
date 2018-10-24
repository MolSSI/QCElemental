import sys

import pytest

from utils import *

import qcelemental


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
])
def test_updatewitherror(inp, expected):
    print('ans', qcelemental.util.update_with_error(inp[0], inp[1]))
    print('exp', expected)
    assert compare_dicts(expected, qcelemental.util.update_with_error(inp[0], inp[1]), 4, tnm())

@pytest.mark.parametrize("inp", [
({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}}),
({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":None}}),
({1: [None, 1]}, {1: [2, 2],3:{"d":"D"}}),
])
def test_updatewitherror_error(inp):
    with pytest.raises(KeyError):
        qcelemental.util.update_with_error(inp[0], inp[1])
