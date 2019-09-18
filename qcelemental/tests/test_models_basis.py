import copy

import numpy as np
import pytest

from qcelemental.models import basis

basis_data = {
    "bs_sto3g_h": {
        "electron_shells": [{
            "harmonic_type": "spherical",
            "angular_momentum": [0],
            "exponents": [3.42525091, 0.62391373, 0.16885540],
            "coefficients": [[0.15432897, 0.53532814, 0.44463454]]
        }]
    },
    "bs_sto3g_o": {
        "electron_shells": [{
            "harmonic_type": "spherical",
            "angular_momentum": [0],
            "exponents": [130.70939, 23.808861, 6.4436089],
            "coefficients": [[0.15432899, 0.53532814, 0.44463454]]
        }, {
            "harmonic_type":
            "cartesian",
            "angular_momentum": [0, 1],
            "exponents": [5.0331513, 1.1695961, 0.3803890],
            "coefficients": [[-0.09996723, 0.39951283, 0.70011547], [0.15591629, 0.60768379, 0.39195739]]
        }]
    },
    "bs_def2tzvp_zr": {
        "electron_shells": [{
            "harmonic_type": "spherical",
            "angular_momentum": [0],
            "exponents": [11.000000000, 9.5000000000, 3.6383667759, 0.76822026698],
            "coefficients": [[-0.19075595259, 0.33895588754, 0.0000000, 0.0000000],
                             [0.0000000, 0.0000000, 1.0000000000, 0.0000000]]
        }, {
            "harmonic_type": "spherical",
            "angular_momentum": [2],
            "exponents": [4.5567957795, 1.2904939799, 0.51646987229],
            "coefficients": [[-0.96190569023E-09, 0.20569990155, 0.41831381851], [0.0000000, 0.0000000, 0.0000000],
                             [0.0000000, 0.0000000, 0.0000000]]
        }, {
            "harmonic_type": "spherical",
            "angular_momentum": [3],
            "exponents": [0.3926100],
            "coefficients": [[1.0000000]]
        }],
        "ecp_electrons": 28,
        "ecp_potentials": [{
            "ecp_type": "scalar",
            "angular_momentum": [0],
            "r_exponents": [2, 2, 2, 2],
            "gaussian_exponents": [7.4880494, 3.7440249, 6.5842120, 3.2921060],
            "coefficients": [[135.15384419, 15.55244130, 19.12219811, 2.43637549]]
        }, {
            "ecp_type": "spinorbit",
            "angular_momentum": [1],
            "r_exponents": [2, 2, 2, 2],
            "gaussian_exponents": [6.4453779, 3.2226886, 6.5842120, 3.2921060],
            "coefficients": [[87.78499169, 11.56406599, 19.12219811, 2.43637549]]
        }]
    }
} # yapf: disable


@pytest.mark.parametrize("center_name", basis_data.keys())
def test_basis_shell_centers(center_name):
    assert basis.BasisCenter(**basis_data[center_name])


def test_basis_set_build():
    assert basis.BasisSet(basis_name="custom_basis",
                          basis_data=basis_data,
                          basis_atom_map=["bs_sto3g_o", "bs_sto3g_h", "bs_sto3g_h", "bs_def2tzvp_zr"])


def test_basis_electron_center_raises():
    data = basis_data["bs_sto3g_h"]["electron_shells"][0].copy()
    data["coefficients"] = [[5, 3]]

    with pytest.raises(ValueError):
        basis.ElectronShell(**data)


def test_basis_ecp_center_raises():
    # Check coefficients
    data = basis_data["bs_def2tzvp_zr"]["ecp_potentials"][0].copy()
    data["coefficients"] = [[5, 3]]

    with pytest.raises(ValueError):
        basis.ECPPotential(**data)

    # Check gaussian_exponents
    data = basis_data["bs_def2tzvp_zr"]["ecp_potentials"][0].copy()
    data["gaussian_exponents"] = [5, 3]

    with pytest.raises(ValueError):
        basis.ECPPotential(**data)

def test_basis_map_raises():

    with pytest.raises(ValueError) as e:
        assert basis.BasisSet(basis_name="custom_basis",
                          basis_data=basis_data,
                          basis_atom_map=["something_odd"])
