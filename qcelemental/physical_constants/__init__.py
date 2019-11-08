"""
Units handlers
"""

# Ensure pint exists
from importlib.util import find_spec

from .context import PhysicalConstantsContext, constants

spec = find_spec("pint")
if spec is None:
    raise ModuleNotFoundError(
        """Python module pint not found. Solve by installing it: `conda install pint -c conda-forge` or `pip install pint`"""
    )  # pragma: no cover
del spec, find_spec
