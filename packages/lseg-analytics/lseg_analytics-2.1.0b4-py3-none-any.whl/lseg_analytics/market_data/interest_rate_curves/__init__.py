"""InterestRateCurve module"""

from ._functions import *
from ._functions import __all__ as functions_all
from ._interest_rate_curve import InterestRateCurve

__all__ = ["InterestRateCurve"]
__all__.extend(functions_all)

_main_class = InterestRateCurve
