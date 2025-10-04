import sys
import warnings

import pytest


def _test_instantiate_mol(clsins):
    if sys.version_info < (3, 14):
        clsins(geometry=[0, 0, 0], symbols=["He"])

    else:
        with pytest.raises(RuntimeError) as exc:
            clsins(geometry=[0, 0, 0], symbols=["He"])

        assert "pydantic.v1 is unavailable" in str(exc.value)


def test_ins_mol_var_models_models():
    from qcelemental.models import Molecule as MyMol

    _test_instantiate_mol(MyMol)


def test_ins_mol_var_models_models_v1():
    from qcelemental.models.v1 import Molecule as MyMol

    _test_instantiate_mol(MyMol)


def test_ins_mol_var_models_models_molecule():
    from qcelemental.models.molecule import Molecule as MyMol

    _test_instantiate_mol(MyMol)


def test_ins_mol_from_data():
    from qcelemental.models import Molecule as MyMol

    if sys.version_info < (3, 14):
        MyMol.from_data("He 0 0 0")

    else:
        with pytest.raises(RuntimeError) as exc:
            MyMol.from_data("He 0 0 0")

        assert "pydantic.v1 is unavailable" in str(exc.value)
