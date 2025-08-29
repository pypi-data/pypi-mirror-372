"""IrSwap module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._ir_swap import IrSwap

__all__ = ["IrSwap"]
__all__.extend(functions_all)

_main_class = IrSwap
