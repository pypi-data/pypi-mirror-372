import copy
import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from lseg_analytics._client.client import Client
from lseg_analytics.common._resource_base import ResourceBase
from lseg_analytics.exceptions import (
    LibraryException,
    ResourceNotFound,
    check_exception_and_raise,
    check_id,
)
from lseg_analytics_basic_client.models import (
    AccruedCalculationMethodEnum,
    AccruedRoundingEnum,
    AccruedRoundingTypeEnum,
    AdjustInterestToPaymentDateEnum,
    AmortizationFrequencyEnum,
    AmortizationItemDefinition,
    AssignmentKey,
    BenchmarkYieldSelectionModeEnum,
    BondDefinition,
    BondPricingParameters,
    BondRoundingParameters,
    CreditSpreadTypeEnum,
    DayCountBasisEnum,
    DefaultBondQuote,
    DiscountMarketDataAssignmentKey,
    DiscountMarketDataAssignmentKeyAssignmentItem,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
    ForwardMarketDataAssignmentKey,
    ForwardMarketDataAssignmentKeyAssignmentItem,
    FxPriceSideEnum,
    Header,
    HullWhiteParameters,
    IndexAverageMethodEnum,
    IndexCompoundingMethodEnum,
    IndexResetFrequencyEnum,
    InflationModeEnum,
    InnerError,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    InterestRateAssignment,
    InterestTypeEnum,
    IPAAmortizationTypeEnum,
    IPABuySellEnum,
    IPADirectionEnum,
    IPADividendTypeEnum,
    IPAIndexObservationMethodEnum,
    IPAVolatilityTypeEnum,
    MarketDataAssignments,
    MarketDataQps,
    PaymentBusinessDayConventionEnum,
    PaymentRollConventionEnum,
    PriceRoundingEnum,
    PriceRoundingTypeEnum,
    PriceSideEnum,
    ProjectedIndexCalculationMethodEnum,
    QuotationModeEnum,
    QuoteFallbackLogicEnum,
    RedemptionDateTypeEnum,
    RepoAnalyticsResponseData,
    RepoAnalyticsResponseWithError,
    RepoCalculationResponse,
    RepoCashflows,
    RepoCurveTypeEnum,
    RepoDefinition,
    RepoDefinitionInstrument,
    RepoDescription,
    RepoParameters,
    RepoPricingAnalysis,
    RepoPricingParameters,
    RepoRateFrequencyEnum,
    RepoRateTypeEnum,
    RepoUnderlyingContract,
    RepoUnderlyingPricingParameters,
    RepoValuation,
    ServiceError,
    SpreadRoundingEnum,
    SpreadRoundingTypeEnum,
    TypeEnum,
    VolatilityTermStructureTypeEnum,
    YieldRoundingEnum,
    YieldRoundingTypeEnum,
    YieldTypeEnum,
)

from ._logger import logger

__all__ = [
    "AccruedCalculationMethodEnum",
    "AccruedRoundingEnum",
    "AccruedRoundingTypeEnum",
    "AdjustInterestToPaymentDateEnum",
    "AmortizationFrequencyEnum",
    "AmortizationItemDefinition",
    "AssignmentKey",
    "BenchmarkYieldSelectionModeEnum",
    "BondDefinition",
    "BondPricingParameters",
    "BondRoundingParameters",
    "CreditSpreadTypeEnum",
    "DayCountBasisEnum",
    "DefaultBondQuote",
    "DiscountMarketDataAssignmentKey",
    "DiscountMarketDataAssignmentKeyAssignmentItem",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
    "ForwardMarketDataAssignmentKey",
    "ForwardMarketDataAssignmentKeyAssignmentItem",
    "FxPriceSideEnum",
    "Header",
    "HullWhiteParameters",
    "IPAAmortizationTypeEnum",
    "IPABuySellEnum",
    "IPADirectionEnum",
    "IPADividendTypeEnum",
    "IPAIndexObservationMethodEnum",
    "IPAVolatilityTypeEnum",
    "IndexAverageMethodEnum",
    "IndexCompoundingMethodEnum",
    "IndexResetFrequencyEnum",
    "InflationModeEnum",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "InterestRateAssignment",
    "InterestTypeEnum",
    "MarketDataAssignments",
    "MarketDataQps",
    "PaymentBusinessDayConventionEnum",
    "PaymentRollConventionEnum",
    "PriceRoundingEnum",
    "PriceRoundingTypeEnum",
    "PriceSideEnum",
    "ProjectedIndexCalculationMethodEnum",
    "QuotationModeEnum",
    "QuoteFallbackLogicEnum",
    "RedemptionDateTypeEnum",
    "RepoAnalyticsResponseData",
    "RepoAnalyticsResponseWithError",
    "RepoCalculationResponse",
    "RepoCashflows",
    "RepoCurveTypeEnum",
    "RepoDefinition",
    "RepoDefinitionInstrument",
    "RepoDescription",
    "RepoParameters",
    "RepoPricingAnalysis",
    "RepoPricingParameters",
    "RepoRateFrequencyEnum",
    "RepoRateTypeEnum",
    "RepoUnderlyingContract",
    "RepoUnderlyingPricingParameters",
    "RepoValuation",
    "SpreadRoundingEnum",
    "SpreadRoundingTypeEnum",
    "TypeEnum",
    "VolatilityTermStructureTypeEnum",
    "YieldRoundingEnum",
    "YieldRoundingTypeEnum",
    "YieldTypeEnum",
    "price",
]


def price(
    *,
    definitions: List[RepoDefinitionInstrument],
    pricing_preferences: Optional[RepoPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> RepoCalculationResponse:
    """
    Calculate Repo analytics

    Parameters
    ----------
    definitions : List[RepoDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : RepoPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketDataQps, optional
        The market data used to compute the analytics.
    return_market_data : bool, optional
        Boolean property to determine if undelying market data used for calculation should be returned in the response
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    RepoCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------


    """

    try:
        logger.info("Calling price")

        response = Client().repo.price(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            market_data=market_data,
            return_market_data=return_market_data,
        )

        output = response
        logger.info("Called price")

        return output
    except Exception as err:
        logger.error("Error price.")
        check_exception_and_raise(err, logger)
