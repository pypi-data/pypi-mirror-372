"""Calendar module"""

from ._calendar import Calendar
from ._functions import *
from ._functions import __all__ as functions_all

__all__ = ["Calendar"]
__all__.extend(functions_all)

_main_class = Calendar
