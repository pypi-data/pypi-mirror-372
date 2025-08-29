# coding=utf-8

# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._operations import YieldBookRestOperations  # type: ignore
from ._operations import bondFutureOperations  # type: ignore
from ._operations import bondOperations  # type: ignore
from ._operations import calendarResourceOperations  # type: ignore
from ._operations import calendarsResourceOperations  # type: ignore
from ._operations import capFloorOperations  # type: ignore
from ._operations import cdsOperations  # type: ignore
from ._operations import commoditiesCurvesOperations  # type: ignore
from ._operations import creditCurvesOperations  # type: ignore
from ._operations import eqVolatilityOperations  # type: ignore
from ._operations import floatingRateIndexResourceOperations  # type: ignore
from ._operations import floatingRateIndicesResourceOperations  # type: ignore
from ._operations import forwardRateAgreementOperations  # type: ignore
from ._operations import fxForwardCurveResourceOperations  # type: ignore
from ._operations import fxForwardCurvesResourceOperations  # type: ignore
from ._operations import fxForwardResourceOperations  # type: ignore
from ._operations import fxForwardsResourceOperations  # type: ignore
from ._operations import fxSpotResourceOperations  # type: ignore
from ._operations import fxSpotsResourceOperations  # type: ignore
from ._operations import fxVolatilityOperations  # type: ignore
from ._operations import inflationCurvesOperations  # type: ignore
from ._operations import instrumentTemplateResourceOperations  # type: ignore
from ._operations import instrumentTemplatesResourceOperations  # type: ignore
from ._operations import interestRateCurveServiceOperations  # type: ignore
from ._operations import interestRateCurvesServiceOperations  # type: ignore
from ._operations import ipaInterestRateCurvesOperations  # type: ignore
from ._operations import ircapletVolatilityOperations  # type: ignore
from ._operations import irSwapResourceOperations  # type: ignore
from ._operations import irSwapsResourceOperations  # type: ignore
from ._operations import irswaptionVolatilityOperations  # type: ignore
from ._operations import loanResourceOperations  # type: ignore
from ._operations import loansResourceOperations  # type: ignore
from ._operations import optionResourceOperations  # type: ignore
from ._operations import optionsResourceOperations  # type: ignore
from ._operations import repoOperations  # type: ignore
from ._operations import structuredProductsOperations  # type: ignore
from ._operations import swaptionOperations  # type: ignore
from ._operations import termDepositOperations  # type: ignore
from ._patch import *
from ._patch import __all__ as _patch_all
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "calendarsResourceOperations",
    "calendarResourceOperations",
    "fxForwardCurvesResourceOperations",
    "fxForwardCurveResourceOperations",
    "fxForwardsResourceOperations",
    "fxForwardResourceOperations",
    "fxSpotsResourceOperations",
    "fxSpotResourceOperations",
    "YieldBookRestOperations",
    "instrumentTemplatesResourceOperations",
    "instrumentTemplateResourceOperations",
    "irSwapsResourceOperations",
    "irSwapResourceOperations",
    "floatingRateIndicesResourceOperations",
    "floatingRateIndexResourceOperations",
    "commoditiesCurvesOperations",
    "creditCurvesOperations",
    "inflationCurvesOperations",
    "ipaInterestRateCurvesOperations",
    "bondOperations",
    "bondFutureOperations",
    "capFloorOperations",
    "cdsOperations",
    "forwardRateAgreementOperations",
    "repoOperations",
    "structuredProductsOperations",
    "swaptionOperations",
    "termDepositOperations",
    "eqVolatilityOperations",
    "fxVolatilityOperations",
    "ircapletVolatilityOperations",
    "irswaptionVolatilityOperations",
    "optionsResourceOperations",
    "optionResourceOperations",
    "interestRateCurvesServiceOperations",
    "interestRateCurveServiceOperations",
    "loansResourceOperations",
    "loanResourceOperations",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
