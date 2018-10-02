"""
A wrapper for the pint ureg data
"""

import pint
import os

from ..data import nist_2014_codata
phys_const = nist_2014_codata["constants"]

# We only want the ureg exposed
__all__ = ["ureg", "Quantity"]

ureg = pint.UnitRegistry(on_redefinition="ignore")
Quantity = ureg.Quantity

# Explicitly update relevant 2014 codata

# Definitions
ureg.define("avogadro_constant = {} / mol = N_A".format(phys_const["avogadro constant"]["value"]))
ureg.define("boltzmann_constant = {} * joule / kelvin".format(phys_const["boltzmann constant"]["value"]))
ureg.define("speed_of_light = {} * meter / second".format(phys_const["speed of light in vacuum"]["value"]))
ureg.define(
    "hartree_inverse_meter = {} / hartree / m".format(phys_const["hartree-inverse meter relationship"]["value"]))

# Energy
ureg.define("hartree = {} * joule = E_h = hartree_energy".format(phys_const["hartree energy"]["value"]))
ureg.define("electron_volt = {} * J = eV".format(phys_const["electron volt-joule relationship"]["value"]))

# Constants
ureg.define("electron_mass = {} * kg".format(phys_const["electron mass"]["value"]))
ureg.define("elementary_charge = {} * coulomb = e".format(phys_const["elementary charge"]["value"]))
ureg.define("plancks_constant = {} * joule * s".format(phys_const["planck constant"]["value"]))

# Distance
ureg.define("bohr = {} * meter = bohr_radius".format(phys_const["bohr radius"]["value"]))
ureg.define("wavenumber = 1 / centimeter")

# Masses
ureg.define(
    "atomic_mass_unit = {} * kilogram = u = amu = dalton = Da".format(phys_const["atomic mass constant"]["value"]))

# Define relationships
_const_rename = {
    "inverse meter": "inverse_meter",
    "atomic mass unit": "atomic_mass_unit",
    "electron volt": "electron_volt"
}

_nist_units = set()

for k, v in phys_const.items():

    # Automatically builds the following:
    # electron_volt_to_kelvin = 1.16045221e4 / electron_volt * kelvin
    # hartree_to_atomic_mass_unit = 2.9212623197e-8 / hartree * atomic_mass_unit
    if not (("-" in k) and ("relationship" in k)): continue

    # Rename where needed
    left_unit, right_unit = k.split('-')
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
    print(definition)

# Add contexts


def _find_nist_unit(unit):
    """Converts pint datatypes to NIST datatypes
    """
    for value in unit.to_tuple()[1]:
        if (value[0] in _nist_units) and (value[1] > 0):
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
c1.add_transformation("[energy]", "[frequency]", build_transformer("hertz", "1 / plancks_consant"))
c1.add_transformation("[frequency]", "[energy]", build_transformer("hartree", "plancks_consant"))

# Allows hartree <-> length
c2 = pint.Context("energy_length")
c2.add_transformation("[energy]", "1 / [length]", build_transformer("inverse_meter", "hartree_to_inverse_meter"))
c2.add_transformation("1 / [length]", "[energy]", build_transformer("hartree", "inverse_meter_to_hartree"))

# Allows energy <-> energy / mol
c3 = pint.Context("substance_relation")
c3.add_transformation("[energy]", "[energy] / [substance]", lambda ureg, val: val * ureg.N_A)
c3.add_transformation("[energy] / [substance]", "[energy]", lambda ureg, val: val / ureg.N_A)

# Add the context
ureg.enable_contexts(c1, c2, c3)
