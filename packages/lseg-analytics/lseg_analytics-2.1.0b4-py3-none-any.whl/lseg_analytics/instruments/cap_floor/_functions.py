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
    AdjustInterestToPaymentDateEnum,
    AmortizationFrequencyEnum,
    AmortizationItemDefinition,
    BarrierDefinitionElement,
    BarrierDirectionEnum,
    BarrierTypeEnum,
    CapFloorAnalyticsResponseData,
    CapFloorAnalyticsResponseWithError,
    CapFloorCalculationResponse,
    CapFloorCashflows,
    CapFloorDescription,
    CapFloorGreeks,
    CapFloorPricingAnalysis,
    CapFloorPricingParameters,
    CapFloorValuation,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
    Header,
    IndexConvexityAdjustmentIntegrationMethodEnum,
    IndexConvexityAdjustmentMethodEnum,
    IndexPriceSideEnum,
    IndexResetFrequencyEnum,
    IndexResetTypeEnum,
    InnerError,
    InputFlow,
    InterestCalculationConventionEnum,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    IPAAmortizationTypeEnum,
    IPABuySellEnum,
    IPACapFloorDefinition,
    IPACapFloorDefinitionInstrument,
    IPAIndexObservationMethodEnum,
    MarketDataQps,
    PaymentBusinessDayConventionEnum,
    PaymentRollConventionEnum,
    PriceSideEnum,
    ServiceError,
    TypeEnum,
)

from ._logger import logger

__all__ = [
    "AdjustInterestToPaymentDateEnum",
    "AmortizationFrequencyEnum",
    "AmortizationItemDefinition",
    "BarrierDefinitionElement",
    "BarrierDirectionEnum",
    "BarrierTypeEnum",
    "CapFloorAnalyticsResponseData",
    "CapFloorAnalyticsResponseWithError",
    "CapFloorCalculationResponse",
    "CapFloorCashflows",
    "CapFloorDescription",
    "CapFloorGreeks",
    "CapFloorPricingAnalysis",
    "CapFloorPricingParameters",
    "CapFloorValuation",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
    "Header",
    "IPAAmortizationTypeEnum",
    "IPABuySellEnum",
    "IPACapFloorDefinition",
    "IPACapFloorDefinitionInstrument",
    "IPAIndexObservationMethodEnum",
    "IndexConvexityAdjustmentIntegrationMethodEnum",
    "IndexConvexityAdjustmentMethodEnum",
    "IndexPriceSideEnum",
    "IndexResetFrequencyEnum",
    "IndexResetTypeEnum",
    "InputFlow",
    "InterestCalculationConventionEnum",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "MarketDataQps",
    "PaymentBusinessDayConventionEnum",
    "PaymentRollConventionEnum",
    "PriceSideEnum",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[IPACapFloorDefinitionInstrument],
    pricing_preferences: Optional[CapFloorPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> CapFloorCalculationResponse:
    """
    Calculate CapFloor analytics

    Parameters
    ----------
    definitions : List[IPACapFloorDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : CapFloorPricingParameters, optional
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
    CapFloorCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # 1. Define the cap instrument
    >>> cap_definition = cf.IPACapFloorDefinition(
    >>>     buy_sell = cf.IPABuySellEnum.BUY.value,                                      # Buy cap protection
    >>>     cap_strike_percent = 2.0,                                                 # 2% strike rate
    >>>     start_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),              # Start date
    >>>     end_date = dt.datetime.strptime("2030-01-01", "%Y-%m-%d"),                # Maturity date
    >>>     notional_amount = 1_000_000,                                              # $1M notional
    >>>     notional_ccy = "USD",                                                     # USD currency
    >>>     index_name = "SOFR",                                                      # SOFR index
    >>>     index_tenor = "ON",
    >>>     interest_payment_frequency = cf.IndexResetFrequencyEnum.QUARTERLY.value,     # Quarterly payments
    >>> )
    >>>
    >>> cap_instrument = cf.IPACapFloorDefinitionInstrument(definition = cap_definition)
    >>> print("Instrument definition created")
    >>>
    >>> # 2. Configure pricing parameters
    >>> pricing_params = cf.CapFloorPricingParameters(
    >>>     valuation_date = dt.datetime.strptime("2025-07-18", "%Y-%m-%d"),
    >>> )
    >>> print("Pricing parameters configured")
    Instrument definition created
    Pricing parameters configured


    >>> #  Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instruments definitions for batch processing
    >>>
    >>> response = cf.price(
    >>>     definitions = [cap_instrument],
    >>>     pricing_preferences = pricing_params,
    >>>     fields = "MarketValueInDealCcy, marketValueInReportCcy, premiumPercent, premiumBp"  # optional
    >>> )
    >>>
    >>> print("Pricing execution completed")
    Pricing execution completed

    """

    try:
        logger.info("Calling price")

        response = Client().cap_floor.price(
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
