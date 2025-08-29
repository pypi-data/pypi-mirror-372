"""FloatingRateIndex module"""

from ._floating_rate_index import FloatingRateIndex
from ._functions import *
from ._functions import __all__ as functions_all

__all__ = ["FloatingRateIndex"]
__all__.extend(functions_all)

_main_class = FloatingRateIndex
