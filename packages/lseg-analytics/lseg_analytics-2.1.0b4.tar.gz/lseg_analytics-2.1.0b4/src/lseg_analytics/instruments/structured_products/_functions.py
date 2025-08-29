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
    BasketItem,
    BasketUnderlying,
    Calibration,
    CalibrationTypeEnum,
    FinancialContractAssetClassEnum,
    FinancialContractResponse,
    GenericNumericalMethod,
    Header,
    InnerError,
    IPAModelParameters,
    MarketDataQps,
    MethodEnum,
    ModelDefinition,
    ModelNameEnum,
    NameTypeValue,
    ProductTypeEnum,
    ServiceError,
    StructuredProductsAnalyticsResponseData,
    StructuredProductsAnalyticsResponseWithError,
    StructuredProductsCalculationResponse,
    StructuredProductsCashflows,
    StructuredProductsDefinition,
    StructuredProductsDefinitionInstrument,
    StructuredProductsDescription,
    StructuredProductsGreeks,
    StructuredProductsPricingAnalysis,
    StructuredProductsPricingParameters,
    StructuredProductsValuation,
    TypeEnum,
)

from ._logger import logger

__all__ = [
    "BasketItem",
    "BasketUnderlying",
    "Calibration",
    "CalibrationTypeEnum",
    "FinancialContractAssetClassEnum",
    "FinancialContractResponse",
    "GenericNumericalMethod",
    "Header",
    "IPAModelParameters",
    "MarketDataQps",
    "MethodEnum",
    "ModelDefinition",
    "ModelNameEnum",
    "NameTypeValue",
    "ProductTypeEnum",
    "StructuredProductsAnalyticsResponseData",
    "StructuredProductsAnalyticsResponseWithError",
    "StructuredProductsCalculationResponse",
    "StructuredProductsCashflows",
    "StructuredProductsDefinition",
    "StructuredProductsDefinitionInstrument",
    "StructuredProductsDescription",
    "StructuredProductsGreeks",
    "StructuredProductsPricingAnalysis",
    "StructuredProductsPricingParameters",
    "StructuredProductsValuation",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[StructuredProductsDefinitionInstrument],
    pricing_preferences: Optional[StructuredProductsPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> StructuredProductsCalculationResponse:
    """
    Calculate StructuredProducts analytics

    Parameters
    ----------
    definitions : List[StructuredProductsDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : StructuredProductsPricingParameters, optional
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
    StructuredProductsCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------


    """

    try:
        logger.info("Calling price")

        response = Client().structured_products.price(
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
