"""
A wrapper for the pint ureg data
"""

import pint
import os

from ..data import nist_2014_codata
phys_const = nist_2014_codata["constants"]

# We only want the ureg exposed
__all__ = ["ureg", "Quantity"]

ureg = pint.UnitRegistry()
Quantity = ureg.Quantity

# Explicitly update relevant 2014 codata
ureg.define("avogadro_constant = {} / mol = N_A".format(phys_const["avogadro constant"]["value"]))
ureg.define("hartree = {} * joule = E_h = hartree_energy".format(phys_const["hartree energy"]["value"]))
ureg.define("bohr = {} * meter = bohr_radius".format(phys_const["bohr radius"]["value"]))
ureg.define("boltzmann_constant = {} * joule / kelvin".format(phys_const["boltzmann constant"]["value"]))
ureg.define("elementary_charge = {} * coulomb = e".format(phys_const["elementary charge"]["value"]))

# Add contexts
c = pint.Context("quantum_chemistry")

# Allows hartree <-> energy / mol
energy = pint.util.UnitsContainer({'[energy]': 1})
energy_substance = pint.util.UnitsContainer({'[energy]': 1, '[substance]': -1})
c.add_transformation(energy, energy_substance, lambda ureg, val : val * ureg.N_A)
c.add_transformation(energy_substance, energy, lambda ureg, val : val / ureg.N_A)


# Add the context
ureg.add_context(c)
ureg.enable_contexts("quantum_chemistry")
