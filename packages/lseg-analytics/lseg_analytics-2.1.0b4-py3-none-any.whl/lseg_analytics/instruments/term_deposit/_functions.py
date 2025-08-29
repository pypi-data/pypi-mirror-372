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
    FinancialContractResponse,
    FinancialContractYearBasisEnum,
    Header,
    InnerError,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    MarketDataQps,
    PaymentBusinessDayConventionEnum,
    PaymentRollConventionEnum,
    PriceSideEnum,
    ServiceError,
    TermDepositAnalyticsResponseData,
    TermDepositAnalyticsResponseWithError,
    TermDepositCalculationResponse,
    TermDepositCashflows,
    TermDepositDefinition,
    TermDepositDefinitionInstrument,
    TermDepositDescription,
    TermDepositNominalMeasures,
    TermDepositPricingAnalysis,
    TermDepositPricingParameters,
    TermDepositValuation,
    TypeEnum,
)

from ._logger import logger

__all__ = [
    "FinancialContractResponse",
    "FinancialContractYearBasisEnum",
    "Header",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "MarketDataQps",
    "PaymentBusinessDayConventionEnum",
    "PaymentRollConventionEnum",
    "PriceSideEnum",
    "TermDepositAnalyticsResponseData",
    "TermDepositAnalyticsResponseWithError",
    "TermDepositCalculationResponse",
    "TermDepositCashflows",
    "TermDepositDefinition",
    "TermDepositDefinitionInstrument",
    "TermDepositDescription",
    "TermDepositNominalMeasures",
    "TermDepositPricingAnalysis",
    "TermDepositPricingParameters",
    "TermDepositValuation",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[TermDepositDefinitionInstrument],
    pricing_preferences: Optional[TermDepositPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> TermDepositCalculationResponse:
    """
    Calculate TermDeposit analytics

    Parameters
    ----------
    definitions : List[TermDepositDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : TermDepositPricingParameters, optional
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
    TermDepositCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # Create term deposit defintion object
    >>> term_deposit_definition = td.TermDepositDefinition(
    >>>     instrument_code = "EUR3MD=",
    >>>     notional_amount = 1000000
    >>> )
    >>>
    >>> # Create term deposit instrument defintion object
    >>> term_deposit_instrument = td.TermDepositDefinitionInstrument(
    >>>     definition = term_deposit_definition
    >>> )
    >>>
    >>> # Create term deposit pricing parameters object - optional
    >>> term_deposit_parameters = td.TermDepositPricingParameters(
    >>>     valuation_date  = dt.datetime.strptime("2025-07-21", "%Y-%m-%d"),
    >>> )


    >>> #  Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instruments definitions for batch processing
    >>>
    >>> term_deposit_response = td.price(
    >>>     definitions = [term_deposit_instrument],
    >>>     pricing_preferences = term_deposit_parameters
    >>> )

    """

    try:
        logger.info("Calling price")

        response = Client().term_deposit.price(
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
