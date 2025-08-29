"""InstrumentTemplate module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._instrument_template import InstrumentTemplate

__all__ = ["InstrumentTemplate"]
__all__.extend(functions_all)

_main_class = InstrumentTemplate
