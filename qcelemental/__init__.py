from .physics import constants
from .chemistry import periodictable
from .exceptions import *
from .datum import Datum

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
