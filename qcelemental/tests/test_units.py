from decimal import Decimal

import pytest

import qcelemental

_pc_default = qcelemental.constants.name[-4:]


@pytest.fixture(scope="module")
def constantss():
    return {
        "default": qcelemental.constants,
        "2014": qcelemental.PhysicalConstantsContext("CODATA2014"),
        "2018": qcelemental.PhysicalConstantsContext("CODATA2018"),
    }


@pytest.mark.parametrize("context", ["default", "2014", "2018"])
# 2014 CODATA values, 2018 CODATA values
@pytest.mark.parametrize(
    "from_unit, to_unit, expecteds",
    [
        # First check the 7 canonical NIST conversions
        ("hartree", "Hz", ("6.579683920711e15", "6.579683920502e15")),
        ("amu", "hartree", ("3.4231776902e7", "3.4231776874e7")),  # potentially another sigfig in 2018
        ("hartree", "kilogram", ("4.850870129e-35", "4.8508702095432e-35")),
        ("hartree", "J/mol", ("2625499.638", "2625499.6394798")),
        ("hartree", "eV", ("27.21138602", "27.211386245988")),
        ("hartree", "wavenumber", ("2.194746313702e5", "2.1947463136320e5")),
        ("hartree", "kelvin", ("3.1577513e5", "3.1577502480407e5")),
        # Check other values
        ("millihartree", "Hz", ("6.579683920711e9", "6.579683920502e9")),
        ("mhartree", "Hz", ("6.579683920711e9", "6.579683920502e9")),
        ("hartree", "microgram", ("4.850870129e-26", "4.8508702095432e-26")),
        ("microhartree", "wavenumber", ("2.194746313702e-7", "2.1947463136320e-7")),
        ("uhartree", "wavenumber", ("2.194746313702e-7", "2.1947463136320e-7")),
        ("kilohartree", "kiloeV", ("27.21138602", "27.211386245988")),
        ("hartree", "kiloeV", ("0.02721138602", "0.027211386245988")),
        ("millihartree", "J/mol", ("2625.499638", "2625.4996394798")),
        ("hartree", "kJ/mol", ("2625.499638", "2625.4996394798")),
        ("hartree", "J", ("4.359744650e-18", "4.3597447222071e-18")),
        ("1/m", "hartree", ("4.556335e-8", "4.556335252912e-08")),  # potentially another sigfig in 2018
    ],
)
def test_unit_conversion_nist(from_unit, to_unit, expecteds, constantss, context):
    if context == "2014" or (context == "default" and _pc_default == "2014"):
        expected = expecteds[0]
    elif context == "2018" or (_pc_default == "2018" and _pc_default == "2018"):
        expected = expecteds[1]

    # Build values and quantize to the tolerance
    expected = Decimal(expected)
    from_to_value = Decimal(constantss[context].conversion_factor(from_unit, to_unit)).quantize(expected)
    assert from_to_value == expected


@pytest.mark.parametrize("context", ["default", "2014", "2018"])
@pytest.mark.parametrize(
    "from_unit, to_unit, expecteds",
    [
        ("hartree", "kcal/mol", ("627.509474", "627.509474063")),  # 627.50947406305
        ("hartree", "kJ/mol", ("2625.499638", "2625.4996394798")),
        ("bohr", "angstrom", ("0.52917721067", "0.529177210903")),
        ("bohr", "nanometer", ("5.2917721067e-2", "5.29177210903e-2")),
        ("bohr", "cm", ("5.2917721067e-9", "5.29177210903e-9")),
        ("bohr", "miles", ("3.288154743E-14", "3.28815474444e-14")),
        ("amu", "kg", ("1.660539040e-27", "1.66053906660e-27")),
        ("amu", "g", ("1.660539040e-24", "1.66053906660e-24")),
        ("Bohr", "bohr", ("1.0",)),
        ("Angstrom", "Angstrom", ("1.0",)),
        ("coulomb", "statC", ("2997924580",)),
        ("debye", "e * Bohr", ("0.393430273", "0.39343027")),  # 0.3934302694
        # Derived atomic units (https://en.wikipedia.org/wiki/Hartree_atomic_units)
        ("au_1st_hyperpolarizability", "au_charge**3 * au_length**3 / au_energy**2", ("1.0",)),
        ("au_2nd_hyperpolarizability", "au_charge**4 * au_length**4 / au_energy**3", ("1.0",)),
        ("au_charge_density", "au_charge / au_length**3", ("1.0",)),
        ("au_current", "au_charge * au_energy / au_action", ("1.0",)),
        ("au_electric_dipole_moment", "au_charge * au_length", ("1.0",)),
        ("au_electric_field", "au_energy / (au_charge * au_length)", ("1.0",)),
        ("au_electric_field_gradient", "au_energy / (au_charge * au_length**2)", ("1.0",)),
        ("au_electric_polarizability", "au_charge**2 * au_length**2 / au_energy", ("1.0",)),
        ("au_electric_potential", "au_energy / au_charge", ("1.0",)),
        ("au_electric_quadrupole_moment", "au_charge * au_length**2", ("1.0",)),
        ("au_force", "au_energy / au_length", ("1.0",)),
        ("au_magnetic_dipole_moment", "au_charge * au_action / au_mass", ("1.0",)),
        ("au_magnetic_flux_density", "au_action / (au_charge * au_length**2)", ("1.0",)),
        ("au_magnetizability", "au_charge**2 * au_length**2 / au_mass", ("1.0",)),
        ("au_momentum", "au_action / au_length", ("1.0",)),
        ("au_permittivity", "au_charge**2 / (au_length * au_energy)", ("1.0",)),
        ("au_time", "au_action / au_energy", ("1.0",)),
        ("au_velocity", "au_length * au_energy / au_action", ("1.0",)),
        ("au_pressure", "J / m^3", ("2.94210e13", "2.94210e13")),  # note precision loss due to absence in CODATA
    ],
)
def test_unit_conversion_other(from_unit, to_unit, expecteds, constantss, context):
    print(expecteds, len(expecteds), context)
    if len(expecteds) == 1 or context == "2014" or (context == "default" and _pc_default == "2014"):
        expected = expecteds[0]
    elif context == "2018" or (_pc_default == "2018" and _pc_default == "2018"):
        expected = expecteds[1]

    # Build values and quantize to the tolerance
    expected = Decimal(expected)
    from_to_value = Decimal(constantss[context].conversion_factor(from_unit, to_unit)).quantize(expected)
    assert from_to_value == expected

    # Build inverse
    inv_expected = 1 / Decimal(expected)
    to_from_value = Decimal(constantss[context].conversion_factor(to_unit, from_unit))

    # Expected to a relative tolerance as the number of digits plus one for rounding
    # Using float comparisons as we are taking an (1 / float) inverse in the conversion code
    rel_tol = float("10e-{}".format(len(expected.as_tuple().digits) + 1))
    assert pytest.approx(float(inv_expected), rel_tol) == float(to_from_value)


def test_quantities_smoke():
    """
    Smoke test to ensure Quantities are correctly returned
    """
    assert 5 == qcelemental.constants.Quantity("5 kcal").magnitude


@pytest.mark.parametrize("context", ["default", "2014", "2018"])
def test_speed_of_light(constantss, context):
    assert (
        pytest.approx(
            constantss[context].speed_of_light_in_vacuum * constantss[context].conversion_factor("m/s", "bohr/au_time"),
            1e-8,
        )
        == constantss[context].c_au
    )
