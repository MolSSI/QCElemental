"""
A wrapper for the pint ureg data
"""

# We only want the ureg builder exposed
__all__ = ["build_units_registry"]


def build_units_registry(context):
    """Builds a pint UnitRegistry based on a given PhysicalConstantsContext.

    Parameters
    ----------
    context : PhysicalConstantsContext
        The context to use for the values.
    """
    import pint

    phys_const = context.raw_codata
    ureg = pint.UnitRegistry(on_redefinition="ignore")

    # Explicitly update relevant 2014 codata

    # Definitions
    ureg.define("avogadro_constant = {} / mol = N_A".format(phys_const["avogadro constant"]["value"]))
    ureg.define("boltzmann_constant = {} * joule / kelvin".format(phys_const["boltzmann constant"]["value"]))
    ureg.define("speed_of_light = {} * meter / second".format(phys_const["speed of light in vacuum"]["value"]))
    ureg.define(
        "hartree_inverse_meter = {} / hartree / m".format(phys_const["hartree-inverse meter relationship"]["value"])
    )
    ureg.define("plank_constant = planks_constant")
    ureg.define("plancks_constant = {} * joule * s".format(phys_const["planck constant"]["value"]))

    # Energy
    ureg.define("hartree = {} * joule = E_h = hartree_energy = au_energy".format(phys_const["hartree energy"]["value"]))
    ureg.define("electron_volt = {} * J = eV".format(phys_const["electron volt-joule relationship"]["value"]))

    # Mass
    ureg.define("electron_mass = {} * kg = au_mass".format(phys_const["electron mass"]["value"]))
    ureg.define(
        "atomic_mass_unit = {} * kilogram = u = amu = dalton = Da".format(phys_const["atomic mass constant"]["value"])
    )

    # Charge
    ureg.define("elementary_charge = {} * coulomb = e = au_charge".format(phys_const["elementary charge"]["value"]))
    ureg.define("statcoulomb = coulomb / 2997924580 = statC")

    # Dipole moment
    ureg.define("debye = 1e-18 * statcoulomb * cm = D")

    # Distance
    ureg.define("bohr = {} * meter = bohr_radius = Bohr = au_length".format(phys_const["bohr radius"]["value"]))
    ureg.define("wavenumber = 1 / centimeter")
    ureg.define("Angstrom = angstrom")

    # Miscellaneous atomic units (https://en.wikipedia.org/wiki/Hartree_atomic_units)
    phys_const_map = {
        "au_1st_hyperpolarizability": "atomic unit of 1st hyperpolarizability",
        "au_2nd_hyperpolarizability": "atomic unit of 2nd hyperpolarizability",
        "au_action": "atomic unit of action",
        "au_charge_density": "atomic unit of charge density",
        "au_current": "atomic unit of current",
        "au_electric_dipole_moment": "atomic unit of electric dipole mom.",
        "au_electric_field": "atomic unit of electric field",
        "au_electric_field_gradient": "atomic unit of electric field gradient",
        "au_electric_polarizability": "atomic unit of electric polarizability",
        "au_electric_potential": "atomic unit of electric potential",
        "au_electric_quadrupole_moment": "atomic unit of electric quadrupole mom.",
        "au_force": "atomic unit of force",
        "au_magnetic_dipole_moment": "atomic unit of mag. dipole mom.",
        "au_magnetic_flux_density": "atomic unit of mag. flux density",
        "au_magnetizability": "atomic unit of magnetizability",
        "au_momentum": "atomic unit of mom.um",
        "au_permittivity": "atomic unit of permittivity",
        "au_time": "atomic unit of time",
        "au_velocity": "atomic unit of velocity",
    }

    # Accessing raw_codata here, so aliases in context.py not active
    if context.name == "CODATA2018":
        phys_const_map["au_momentum"] = "atomic unit of momentum"

    for k, v in phys_const_map.items():
        ureg.define(f"{k} = {phys_const[v]['value']} * {phys_const[v]['unit']}")

    ureg.define(f"au_pressure = au_energy / au_length**3")  # not in CODATA

    # Define relationships
    _const_rename = {
        "inverse meter": "inverse_meter",
        "atomic mass unit": "atomic_mass_unit",
        "electron volt": "electron_volt",
    }

    _nist_units = set()

    for k, v in phys_const.items():

        # Automatically builds the following:
        # electron_volt_to_kelvin = 1.16045221e4 / electron_volt * kelvin
        # hartree_to_atomic_mass_unit = 2.9212623197e-8 / hartree * atomic_mass_unit
        if not (("-" in k) and ("relationship" in k)):
            continue

        # Rename where needed
        left_unit, right_unit = k.split("-")
        left_unit = _const_rename.get(left_unit, left_unit)
        _nist_units.add(left_unit)

        right_unit = right_unit.replace(" relationship", "")
        right_unit = _const_rename.get(right_unit, right_unit)

        # Inverse is a special case

        if "inverse_meter" == left_unit:
            ratio1 = "* meter"
        else:
            ratio1 = "/ " + left_unit

        if "inverse_meter" == right_unit:
            ratio2 = "/ meter"
        else:
            ratio2 = "* " + right_unit

        definition = "{}_to_{} = {} {} {}".format(left_unit, right_unit, v["value"], ratio1, ratio2)
        ureg.define(definition)
        # print(definition)

    # Add contexts

    def _find_nist_unit(unit):
        """Converts pint datatypes to NIST datatypes
        """
        for value in unit.to_tuple()[1]:
            if value[1] < 1:
                continue
            if any(x in value[0] for x in _nist_units):
                return value[0]

        for value in unit.to_tuple()[1]:
            if (value[0] == "meter") and (value[1] == -1):
                return "inverse_meter"

        return None

    def build_transformer(right_unit, default):
        """Builds a transformer that attempts first to use the NIST values exactly and then falls back
        on to canonical Pint tech. The NIST values are not "exact" and will
        fail the triangle rule due to the inherent uncertainties of the values.

        Parameters
        ----------
        right_unit : str
            The NIST value to convert to
        default : str
            A fall back conversion rule to apply
        """

        def transformer(ureg, val):

            left_unit = _find_nist_unit(val)
            if left_unit is None:
                return val * ureg.parse_expression(default)
            else:
                return val * ureg.parse_expression("{}_to_{}".format(left_unit, right_unit))

        return transformer

    # Allows hartree <-> frequency
    c1 = pint.Context("energy_frequency")
    c1.add_transformation("[energy]", "[frequency]", build_transformer("hertz", "1 / plancks_constant"))
    c1.add_transformation("[frequency]", "[energy]", build_transformer("hartree", "plancks_constant"))

    # Allows hartree <-> inverse_length
    c2 = pint.Context("energy_inverse_length")
    c2.add_transformation("[energy]", "1 / [length]", build_transformer("inverse_meter", "hartree_to_inverse_meter"))
    c2.add_transformation("1 / [length]", "[energy]", build_transformer("hartree", "inverse_meter_to_hartree"))

    # Allows hartree <-> mass
    c3 = pint.Context("energy_mass")
    c3.add_transformation("[energy]", "[mass]", build_transformer("kilogram", "hartree_to_kilogram"))
    c3.add_transformation("[mass]", "[energy]", build_transformer("hartree", "kilogram_to_hartree"))

    # Allows hartree <-> temperature
    c4 = pint.Context("energy_temperature")
    c4.add_transformation("[energy]", "[temperature]", build_transformer("kelvin", "hartree_to_kelvin"))
    c4.add_transformation("[temperature]", "[energy]", build_transformer("hartree", "kelvin_to_hartree"))

    # Allows energy <-> energy / mol
    c5 = pint.Context("substance_relation")
    c5.add_transformation("[energy]", "[energy] / [substance]", lambda ureg, val: val * ureg.N_A)
    c5.add_transformation("[energy] / [substance]", "[energy]", lambda ureg, val: val / ureg.N_A)

    # Add the context
    ureg.enable_contexts(c1, c2, c3, c4, c5)

    return ureg
