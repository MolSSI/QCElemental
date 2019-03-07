"""
Tests the imports and exports of the Molecule object.
"""

import numpy as np
import pytest
from qcelemental.models import Molecule
import qcelemental as qcel

water_molecule = Molecule.from_data("""
    0 1
    O  -1.551007  -0.114520   0.000000
    H  -1.934259   0.762503   0.000000
    H  -0.599677   0.040712   0.000000
    """)

water_dimer_minima = Molecule.from_data(
    """
    0 1
    O  -1.551007  -0.114520   0.000000
    H  -1.934259   0.762503   0.000000
    H  -0.599677   0.040712   0.000000
    --
    O   1.350625   0.111469   0.000000
    H   1.680398  -0.373741  -0.758561
    H   1.680398  -0.373741   0.758561
    """,
    dtype="psi4",
    orient=True)


def test_molecule_data_constructor_numpy():
    water_psi = water_dimer_minima.copy()
    ele = np.array(water_psi.atomic_numbers).reshape(-1, 1)
    npwater = np.hstack((ele, water_psi.geometry))

    water_from_np = Molecule.from_data(npwater, name="water dimer", dtype="numpy", frags=[3])
    assert water_psi.compare(water_psi, water_from_np)

    water_from_np = Molecule.from_data(npwater, name="water dimer", frags=[3])
    assert water_psi.compare(water_psi, water_from_np)
    assert water_psi.get_molecular_formula() == "H4O2"


def test_molecule_data_constructor_dict():
    water_psi = water_dimer_minima.copy()

    # Check the JSON construct/deconstruct
    water_from_json = Molecule.from_data(water_psi.dict())
    assert water_psi.compare(water_psi, water_from_json)

    water_from_json = Molecule.from_data(water_psi.json(), "json")
    assert water_psi.compare(water_psi, water_from_json)
    assert water_psi.compare(Molecule.from_data(water_psi.to_string(), dtype="psi4"))

    assert water_psi.get_hash() == 'b41f1e38bc4be5482fcd1d4dd53ca7c65146ab91'  # copied from schema_version=1
    assert water_psi.schema_version == 2
    assert water_psi.schema_name == 'qcschema_molecule'


def test_molecule_data_constructor_error():
    with pytest.raises(TypeError):
        Molecule.from_data([])

    with pytest.raises(KeyError):
        Molecule.from_data({}, dtype="bad")


def test_molecule_np_constructors():
    """
    Neon tetramer fun
    """
    ### Neon Tetramer
    neon_from_psi = Molecule.from_data(
        """
        Ne 0.000000 0.000000 0.000000
        --
        Ne 3.100000 0.000000 0.000000
        --
        Ne 0.000000 3.200000 0.000000
        --
        Ne 0.000000 0.000000 3.300000
        units bohr""",
        dtype="psi4")
    ele = np.array([10, 10, 10, 10]).reshape(-1, 1)
    npneon = np.hstack((ele, neon_from_psi.geometry))
    neon_from_np = Molecule.from_data(npneon, name="neon tetramer", dtype="numpy", frags=[1, 2, 3], units="bohr")

    assert neon_from_psi.compare(neon_from_psi, neon_from_np)

    # Check the JSON construct/deconstruct
    neon_from_json = Molecule.from_data(neon_from_psi.json(), dtype="json")
    assert neon_from_psi.compare(neon_from_psi, neon_from_json)
    assert neon_from_json.get_molecular_formula() == "Ne4"


def test_water_minima_data():
    # Give it a name
    mol_dict = water_dimer_minima.dict()
    mol_dict['name'] = "water dimer"
    mol = Molecule(orient=True, **mol_dict)

    assert len(str(mol)) == 661
    assert len(mol.to_string()) == 442

    assert sum(x == y for x, y in zip(mol.symbols, ['O', 'H', 'H', 'O', 'H', 'H'])) == mol.geometry.shape[0]
    assert mol.name == "water dimer"
    assert mol.molecular_charge == 0
    assert mol.molecular_multiplicity == 1
    assert np.sum(mol.real) == mol.geometry.shape[0]
    assert np.allclose(mol.fragments, [[0, 1, 2], [3, 4, 5]])
    assert np.allclose(mol.fragment_charges, [0, 0])
    assert np.allclose(mol.fragment_multiplicities, [1, 1])
    assert hasattr(mol, "provenance")
    assert np.allclose(mol.geometry, [[2.81211080, 0.1255717, 0.], [3.48216664, -1.55439981, 0.],
                                      [1.00578203, -0.1092573, 0.], [-2.6821528, -0.12325075, 0.],
                                      [-3.27523824, 0.81341093, 1.43347255], [-3.27523824, 0.81341093, -1.43347255]])
    assert mol.get_hash() == "b41f1e38bc4be5482fcd1d4dd53ca7c65146ab91"


def test_water_minima_fragment():

    mol = water_dimer_minima.copy()
    frag_0 = mol.get_fragment(0, orient=True)
    frag_1 = mol.get_fragment(1, orient=True)
    assert frag_0.get_hash() == "0b13814f79b8f74f17499b31fe7b76cd97b89449"
    assert frag_1.get_hash() == "4469ff05895a6375a91ce9a225f96e3f9938450b"

    frag_0_1 = mol.get_fragment(0, 1)
    frag_1_0 = mol.get_fragment(1, 0)

    assert mol.symbols[:3] == frag_0.symbols
    assert np.allclose(mol.masses[:3], frag_0.masses)

    assert mol.symbols == frag_0_1.symbols
    assert np.allclose(mol.geometry, frag_0_1.geometry)

    assert mol.symbols[3:] + mol.symbols[:3] == frag_1_0.symbols
    assert np.allclose(mol.masses[3:] + mol.masses[:3], frag_1_0.masses)


def test_pretty_print():

    mol = water_dimer_minima.copy()
    assert isinstance(mol.pretty_print(), str)


def test_to_string():

    mol = water_dimer_minima.copy()
    assert isinstance(mol.to_string(), str)


def test_from_file_string(tmp_path):

    p = tmp_path / "water.psimol"
    p.write_text(water_dimer_minima.to_string())

    mol = Molecule.from_file(p)

    assert mol.compare(water_dimer_minima)
    assert mol.compare(water_dimer_minima.dict())


def test_from_file_json(tmp_path):

    p = tmp_path / "water.json"
    p.write_text(water_dimer_minima.json())

    mol = Molecule.from_file(p)
    assert mol.compare(water_dimer_minima)


def test_from_file_numpy(tmp_path):

    ele = np.array(water_molecule.atomic_numbers).reshape(-1, 1)
    npwater = np.hstack((ele, water_molecule.geometry))

    # Try npy
    p = tmp_path / "water.npy"
    np.save(p, npwater)
    mol = Molecule.from_file(p)

    assert mol.compare(water_molecule)


def test_water_orient():
    # These are identical molecules, should find the correct results
    mol = Molecule.from_data("""
        O  -1.551007  -0.114520   0.000000
        H  -1.934259   0.762503   0.000000
        H  -0.599677   0.040712   0.000000
        --
        O  -0.114520  -1.551007  10.000000
        H   0.762503  -1.934259  10.000000
        H   0.040712  -0.599677  10.000000
        """)

    frag_0 = mol.get_fragment(0, orient=True)
    frag_1 = mol.get_fragment(1, orient=True)

    # Make sure the fragments match
    assert frag_0.get_hash() == frag_1.get_hash()

    # Make sure the complexes match
    frag_0_1 = mol.get_fragment(0, 1, orient=True)
    frag_1_0 = mol.get_fragment(1, 0, orient=True)

    assert frag_0_1.get_hash() == frag_1_0.get_hash()

    # These are identical molecules, but should be different with ghost
    mol = Molecule.from_data(
        """
        O  -1.551007  -0.114520   0.000000
        H  -1.934259   0.762503   0.000000
        H  -0.599677   0.040712   0.000000
        --
        O  -11.551007  -0.114520   0.000000
        H  -11.934259   0.762503   0.000000
        H  -10.599677   0.040712   0.000000
        """,
        dtype="psi4",
        orient=True)

    frag_0 = mol.get_fragment(0, orient=True)
    frag_1 = mol.get_fragment(1, orient=True)

    # Make sure the fragments match
    assert frag_0.molecular_multiplicity == 1
    assert frag_0.get_hash() == frag_1.get_hash()

    # Make sure the complexes match
    frag_0_1 = mol.get_fragment(0, 1, orient=True)
    frag_1_0 = mol.get_fragment(1, 0, orient=True)

    # Ghost fragments should prevent overlap
    assert frag_0_1.molecular_multiplicity == 1
    assert frag_0_1.get_hash() != frag_1_0.get_hash()


def test_molecule_errors_extra():
    data = water_dimer_minima.dict()
    data["whatever"] = 5
    with pytest.raises(Exception):
        Molecule(**data)


def test_molecule_errors_connectivity():
    data = water_molecule.dict()
    data["connectivity"] = [(-1, 5, 5)]
    with pytest.raises(Exception):
        Molecule(**data)


def test_molecule_errors_shape():
    data = water_molecule.dict()
    data["geometry"] = list(range(8))
    with pytest.raises(Exception):
        Molecule(**data)


def test_molecule_serialization():
    assert isinstance(water_dimer_minima.json(), str)

    assert isinstance(water_dimer_minima.json_dict()["geometry"], list)


def test_charged_fragment():
    mol = Molecule(
        symbols=["Li", "Li"],
        geometry=[0, 0, 0, 0, 0, 5],
        fragment_charges=[0.0, 0.0],
        fragment_multiplicities=[2, 2],
        fragments=[[0], [1]])
    assert mol.molecular_multiplicity == 3
    assert mol.molecular_charge == 0
    f1 = mol.get_fragment(0)
    assert f1.molecular_multiplicity == 2
    assert f1.fragment_multiplicities == [2]
    assert pytest.approx(f1.molecular_charge) == 0
    assert pytest.approx(f1.fragment_charges) == [0]


def test_molecule_repeated_hashing():

    mol = Molecule(**{
        'symbols': ['H', 'O', 'O', 'H'],
        'geometry': [
             1.7317,  1.2909,  1.037100000000001,
             1.3156, -0.0074, -0.2807,
            -1.3143,  0.0084, -0.2741,
            -1.7241, -1.3079,  1.0277
        ]
    }) # yapf: disable

    h1 = mol.get_hash()
    assert mol.get_molecular_formula() == "H2O2"

    mol2 = Molecule(orient=False, **mol.dict())
    assert h1 == mol2.get_hash()

    mol3 = Molecule(orient=False, **mol2.dict())
    assert h1 == mol3.get_hash()


@pytest.mark.parametrize("measure,result", [
    ([0, 1], 1.8086677572537304),
    ([0, 1, 2], 37.98890673587713),
    ([0, 1, 2, 3], 180.0),
    ([[0, 1, 2, 3]], [180.0]),
    ([[1, 3], [3, 1], [1, 2, 3]], [6.3282716, 6.3282716, 149.51606694803903]),
])
def test_measurements(measure, result):

    mol = Molecule(**{
        'symbols': ['H', 'O', 'O', 'H'],
        'geometry': [
             1.7317,  1.2909,  1.0371,
             1.3156, -0.0074, -0.2807,
            -1.3143,  0.0084, -0.2741,
            -1.7241, -1.3079,  1.0277
        ]
    }) # yapf: disable

    assert pytest.approx(water_dimer_minima.measure(measure)) == result
