import pytest

import qcelemental


@pytest.mark.parametrize("inp,expected", [
    (['AAAABBBCCDAABBB'], 'ABCD'),
    (['ABBCcAD', str.lower], 'ABCD'),
])
def test_unique_everseen(inp, expected):
    ue = qcelemental.util.unique_everseen(*inp)
    assert list(ue) == list(expected)
