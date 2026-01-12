try:
    import pydantic
except ImportError:  # pragma: no cover
    raise ImportError(
        "Python module pydantic not found. Solve by installing it: "
        "`conda install pydantic -c conda-forge` or `pip install pydantic`"
    )

import sys

from . import v1, v2
from .v1 import *

# V1V2TEST if True:
if sys.version_info >= (3, 14):
    # avoid using the _v1v2 below if at all possible and *never* return objects of these
    from . import _v1v2

# Note that changing .v1 as default requires changing the shim classes in this dir, too.
