"""Option module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._option import Option

__all__ = ["Option"]
__all__.extend(functions_all)

_main_class = Option
