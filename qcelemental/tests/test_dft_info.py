import qcelemental


def test_svwn_is_lda():
    assert qcelemental.dftfunctionalinfo.functionals["svwn"].ansatz == 0
