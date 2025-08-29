"""FxForward module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._fx_forward import FxForward

__all__ = ["FxForward"]
__all__.extend(functions_all)

_main_class = FxForward
