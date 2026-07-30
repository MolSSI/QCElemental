import numpy as np
import pytest

import qcelemental as qcel
from qcelemental.molparse.mae import _coerce_bond_order, _import_schrodinger

from .addons import using_schrodinger


@pytest.mark.parametrize("order", [0, 1, 2, 3, 1.0])
def test_mae_supported_bond_orders(order):
    assert _coerce_bond_order(order, permissive=False) == (int(order), False)


@pytest.mark.parametrize(
    "order, expected",
    [
        (0.4, 0),
        (0.5, 1),
        (1.5, 2),
        (2.5, 3),
        (3.7, 3),
        (5.0, 3),
    ],
)
def test_mae_permissive_bond_orders(order, expected):
    assert _coerce_bond_order(order, permissive=True) == (expected, True)


def test_mae_strict_bond_order_error():
    with pytest.raises(ValueError, match="permissive=True"):
        _coerce_bond_order(1.5, permissive=False)


@using_schrodinger
def test_mae_round_trip(tmp_path):
    molecule = qcel.models.v2.Molecule(
        symbols=["C", "H", "X", "O"],
        geometry=[
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        name="MAE round trip",
        molecular_charge=1,
        molecular_multiplicity=1,
        real=[True, True, False, False],
        connectivity=[(0, 1, 1), (0, 2, 0), (0, 3, 2)],
    )
    mae_file = tmp_path / "round_trip.mae"

    qcel.molparse.to_mae(molecule, mae_file)

    structure, mm = _import_schrodinger()
    with structure.StructureReader(mae_file) as reader:
        [mae_structure] = list(reader)
    assert not bool(mae_structure.atom[3].property.get(mm.M2IO_DATA_ATOM_COUNTERPOISE, 0))
    assert bool(mae_structure.atom[4].property.get(mm.M2IO_DATA_ATOM_COUNTERPOISE, 0))

    results = qcel.molparse.from_mae(mae_file)

    [result] = results

    assert result.name == molecule.name
    assert result.symbols.tolist() == molecule.symbols.tolist()
    assert result.real.tolist() == molecule.real.tolist()
    assert result.molecular_charge == molecule.molecular_charge
    assert result.molecular_multiplicity == molecule.molecular_multiplicity
    assert result.connectivity == molecule.connectivity
    assert np.allclose(result.geometry, molecule.geometry)


@using_schrodinger
def test_mae_permissive_round_trip(tmp_path):
    molecule = qcel.models.v2.Molecule(
        symbols=["C", "C"],
        geometry=[[0.0, 0.0, 0.0], [2.5, 0.0, 0.0]],
        connectivity=[(0, 1, 1.5)],
    )
    mae_file = tmp_path / "permissive.mae"

    with pytest.warns(UserWarning, match=r"1\.5 -> 2"):
        qcel.molparse.to_mae(molecule, mae_file, permissive=True)

    [result] = qcel.molparse.from_mae(mae_file)
    assert result.connectivity == [(0, 1, 2.0)]


@using_schrodinger
def test_mae_multiple_structures(tmp_path):
    first = qcel.models.v2.Molecule(
        symbols=["He"],
        geometry=[[0.0, 0.0, 0.0]],
        name="first",
    )
    second = qcel.models.v2.Molecule(
        symbols=["H"],
        geometry=[[1.0, 2.0, 3.0]],
        name="second",
        molecular_multiplicity=2,
    )
    mae_file = tmp_path / "multiple.mae"

    qcel.molparse.to_mae(first, mae_file)
    qcel.molparse.to_mae(second, mae_file, overwrite=False)

    results = qcel.molparse.from_mae(mae_file)

    assert [molecule.name for molecule in results] == ["first", "second"]
    assert results[0].symbols.tolist() == ["He"]
    assert results[1].symbols.tolist() == ["H"]
    assert np.allclose(results[1].geometry, second.geometry)
