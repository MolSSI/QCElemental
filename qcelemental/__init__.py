from .physics import constants
from .chemistry import periodictable
from .exceptions import *
from .datastructures import QCAspect

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
