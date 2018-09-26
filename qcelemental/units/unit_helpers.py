"""
A file for unit helpers
"""

import pint
from .ureg import ureg

__all__ = ["conversion_dict", "conversion_factor", "convert_contexts"]

def conversion_factor(base_unit, conv_unit):
    """
    Provides the conversion factor from one unit to another

    Examples
    --------

    >>> conversion_factor("meter", "picometer")
    1e-12

    >>> conversion_factor("feet", "meter")
    0.30479999999999996

    >>> conversion_factor(10 * ureg.feet, "meter")
    3.0479999999999996

    """

    # Add a little magic incase the incoming values have scalars

    factor = 1.0

    # First make sure we either have Units or Quantities
    if isinstance(base_unit, str):
        base_unit = ureg.parse_expression(base_unit)

    if isinstance(conv_unit, str):
        conv_unit = ureg.parse_expression(conv_unit)

    # Need to play with prevector if we have Quantities
    if isinstance(base_unit, pint.quantity._Quantity):
        factor *= base_unit.magnitude
        base_unit = base_unit.units

    if isinstance(conv_unit, pint.quantity._Quantity):
        factor /= conv_unit.magnitude
        conv_unit = conv_unit.units

    return ureg.convert(factor, base_unit, conv_unit)

