"""
A wrapper for the pint ureg data
"""

import pint
import os

from ..data import nist_codata_2014

# We only want the ureg exposed
__all__ = ["ureg", "Quantity"]

ureg = UnitRegistry()
Quantity = ureg.Quantity

# Add contexts
c = pint.Context("quantum_chemistry")

# Allows hartree <-> energy / mol 
c.add_transformation(energy, energy_substance, lambda ureg, val : val * ureg.N_A)
c.add_transformation(energy_substance, energy, lambda ureg, val : val / ureg.N_A)


# Add the context
ureg.add_context(c)
ureg.enable_contexts("quantum_chemistry")
