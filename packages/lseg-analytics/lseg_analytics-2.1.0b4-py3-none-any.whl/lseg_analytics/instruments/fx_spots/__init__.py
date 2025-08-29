"""FxSpot module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._fx_spot import FxSpot

__all__ = ["FxSpot"]
__all__.extend(functions_all)

_main_class = FxSpot
