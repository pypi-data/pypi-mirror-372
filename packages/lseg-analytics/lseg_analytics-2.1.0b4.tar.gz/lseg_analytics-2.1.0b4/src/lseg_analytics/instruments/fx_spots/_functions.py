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
    AdjustableDate,
    AdjustedDate,
    Amount,
    BachelierParameters,
    BasePricingParameters,
    BidAskSimpleValues,
    BlackScholesEquityParameters,
    BlackScholesFxParameters,
    BlackScholesInterestRateFuture,
    CmdtyOptionVolSurfaceChoice,
    CmdtyVolSurfaceInput,
    ConvexityAdjustment,
    CreditCurveChoice,
    CreditCurveInput,
    CurveDataPoint,
    Date,
    DateMovingConvention,
    Description,
    Dividend,
    DividendTypeEnum,
    EqOptionVolSurfaceChoice,
    EqVolSurfaceInput,
    FutureDate,
    FutureDateCalculationMethodEnum,
    FxAnalyticsDescription,
    FxCurveInput,
    FxForwardAnalyticsDescription,
    FxForwardCurveChoice,
    FxForwardDefinition,
    FxForwardPricingAnalysis,
    FxForwardRisk,
    FxForwardValuation,
    FxOptionVolSurfaceChoice,
    FxPricingAnalysis,
    FxPricingParameters,
    FxRate,
    FxRateTypeEnum,
    FxRisk,
    FxSpotAnalyticsDescription,
    FxSpotAnalyticsPricingOnResourceResponseData,
    FxSpotAnalyticsPricingResponseData,
    FxSpotAnalyticsPricingResponseWithError,
    FxSpotAnalyticsValuationOnResourceResponseData,
    FxSpotAnalyticsValuationResponseData,
    FxSpotAnalyticsValuationResponseWithError,
    FxSpotDefinition,
    FxSpotDefinitionInstrument,
    FxSpotInfo,
    FxSpotOverride,
    FxSpotPricingAnalysis,
    FxSpotRisk,
    FxSpotValuation,
    FxValuation,
    FxVolSurfaceInput,
    HestonEquityParameters,
    InnerError,
    IrCapVolSurfaceChoice,
    IrCurveChoice,
    IrMeasure,
    IrPricingParameters,
    IrSwapSolvingParameters,
    IrSwapSolvingTarget,
    IrSwapSolvingVariable,
    IrSwaptionVolCubeChoice,
    IrVolCubeInput,
    IrVolSurfaceInput,
    IrZcCurveInput,
    Location,
    MarketData,
    MarketVolatility,
    Measure,
    ModelParameters,
    MonthEnum,
    NumericalMethodEnum,
    OptionPricingParameters,
    OptionSolvingParameters,
    OptionSolvingTarget,
    OptionSolvingVariable,
    OptionSolvingVariableEnum,
    PartyEnum,
    PriceSideWithLastEnum,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    ServiceError,
    SettlementType,
    SolvingLegEnum,
    SortingOrderEnum,
    Spot,
    StrikeTypeEnum,
    SwapSolvingVariableEnum,
    TimeStampEnum,
    UnitEnum,
    VolatilityTypeEnum,
    VolCubePoint,
    VolModelTypeEnum,
    VolSurfacePoint,
    ZcTypeEnum,
)

from ._fx_spot import FxSpot
from ._logger import logger

__all__ = [
    "Amount",
    "BachelierParameters",
    "BasePricingParameters",
    "BlackScholesEquityParameters",
    "BlackScholesFxParameters",
    "BlackScholesInterestRateFuture",
    "CmdtyOptionVolSurfaceChoice",
    "CmdtyVolSurfaceInput",
    "ConvexityAdjustment",
    "CreditCurveChoice",
    "CreditCurveInput",
    "CurveDataPoint",
    "Dividend",
    "DividendTypeEnum",
    "EqOptionVolSurfaceChoice",
    "EqVolSurfaceInput",
    "FutureDate",
    "FutureDateCalculationMethodEnum",
    "FxAnalyticsDescription",
    "FxCurveInput",
    "FxForwardAnalyticsDescription",
    "FxForwardCurveChoice",
    "FxForwardDefinition",
    "FxForwardPricingAnalysis",
    "FxForwardRisk",
    "FxForwardValuation",
    "FxOptionVolSurfaceChoice",
    "FxPricingAnalysis",
    "FxPricingParameters",
    "FxRate",
    "FxRateTypeEnum",
    "FxRisk",
    "FxSpot",
    "FxSpotAnalyticsDescription",
    "FxSpotAnalyticsPricingOnResourceResponseData",
    "FxSpotAnalyticsPricingResponseData",
    "FxSpotAnalyticsPricingResponseWithError",
    "FxSpotAnalyticsValuationOnResourceResponseData",
    "FxSpotAnalyticsValuationResponseData",
    "FxSpotAnalyticsValuationResponseWithError",
    "FxSpotDefinition",
    "FxSpotDefinitionInstrument",
    "FxSpotInfo",
    "FxSpotOverride",
    "FxSpotPricingAnalysis",
    "FxSpotRisk",
    "FxSpotValuation",
    "FxValuation",
    "FxVolSurfaceInput",
    "HestonEquityParameters",
    "IrCapVolSurfaceChoice",
    "IrCurveChoice",
    "IrMeasure",
    "IrPricingParameters",
    "IrSwapSolvingParameters",
    "IrSwapSolvingTarget",
    "IrSwapSolvingVariable",
    "IrSwaptionVolCubeChoice",
    "IrVolCubeInput",
    "IrVolSurfaceInput",
    "IrZcCurveInput",
    "MarketData",
    "MarketVolatility",
    "Measure",
    "ModelParameters",
    "MonthEnum",
    "NumericalMethodEnum",
    "OptionPricingParameters",
    "OptionSolvingParameters",
    "OptionSolvingTarget",
    "OptionSolvingVariable",
    "OptionSolvingVariableEnum",
    "PartyEnum",
    "PriceSideWithLastEnum",
    "Rate",
    "SolvingLegEnum",
    "Spot",
    "StrikeTypeEnum",
    "SwapSolvingVariableEnum",
    "TimeStampEnum",
    "UnitEnum",
    "VolCubePoint",
    "VolModelTypeEnum",
    "VolSurfacePoint",
    "VolatilityTypeEnum",
    "ZcTypeEnum",
    "create_from_template",
    "delete",
    "load",
    "price",
    "search",
    "value",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a FxSpot using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The FxSpot id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The FxSpot name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the FxSpot is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    FxSpot
        The FxSpot instance.

    Examples
    --------
    Load by Id.

    >>> load(resource_id="94da9f98-343f-4dca-9b34-479987060f91")
    <FxSpot space='HOME' name='MyFxSpot' 1f009c8a‥>

    Load by name and space.

    >>> load(name="myFxSpot", space="MySpace")
    <FxSpot space='HOME' name='MyFxSpot' 1f009c8a‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load FxSpot {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxSpot {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxSpot not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    elif len(result) > 1:
        logger.warn(f"Found more than one result for name={name!r} and space={space!r}, returning the first one")
    return _load_by_id(result[0].id)


def delete(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Delete FxSpot instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The FxSpot resource ID.
        Required if name is not provided.
    name : str, optional
        The FxSpot name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the FxSpot is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    Delete by Id.

    >>> delete(resource_id="5125e2a4-f7db-48dd-ab35-7d05d6886be8")
    True

    Delete by name and space.

    >>> delete(name="myFxSpot", space="MySpace")
    True

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete FxSpot {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxSpot {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxSpot not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def create_from_template(
    *,
    reference: str,
    overrides: Optional[FxSpotOverride] = None,
    fields: Optional[str] = None,
) -> FxSpot:
    """
    Creating FxSpots from an existing template and a set of overrides.

    Parameters
    ----------
    reference : str
        The reference to the Fx Spot template.
    overrides : FxSpotOverride, optional
        The object that contains the overridden properties.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FxSpot
        FxSpot

    Examples
    --------
    >>> overrides = FxSpotOverride(
    >>>     deal_amount=10000,
    >>>     contra_amount=10000,
    >>>     rate=FxRate(value=0.5, scaling_factor=1, rate_precision=1),
    >>>     end_date=AdjustableDate(
    >>>         date=datetime.date(2021, 3, 1), date_moving_convention=DateMovingConvention.MODIFIED_FOLLOWING
    >>>     ),
    >>>     start_date=AdjustableDate(
    >>>         date=datetime.date(2020, 1, 1), date_moving_convention=DateMovingConvention.MODIFIED_FOLLOWING
    >>>     ),
    >>> )
    >>>
    >>> create_from_template(reference="c5f6b1ff-26d7-4fdc-9b61-d94610f7ece1", overrides=overrides)
    <FxSpot space=None name='' unsaved>

    """

    try:
        logger.info("Calling create_from_template")

        response = Client().fx_spots_resource.build_fx_spot_from_template(
            fields=fields, reference=reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_template")

        return FxSpot(output)
    except Exception as err:
        logger.error("Error create_from_template")
        check_exception_and_raise(err, logger)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a FxSpot that exists in the platform. The FxSpot can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting FxSpot with id: {instrument_id}")
        Client().fx_spot_resource.delete(instrument_id=instrument_id)
        logger.info(f"Deleted FxSpot with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting FxSpot with id: {instrument_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> FxSpot:
    """
    Access a FxSpot existing in the platform (read). The FxSpot can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FxSpot


    Examples
    --------


    """

    try:
        logger.info(f"Opening FxSpot with id: {instrument_id}")

        response = Client().fx_spot_resource.read(instrument_id=instrument_id, fields=fields)

        output = FxSpot(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening FxSpot:")
        check_exception_and_raise(err, logger)


def price(
    *,
    definitions: List[FxSpotDefinitionInstrument],
    pricing_preferences: Optional[FxPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> FxSpotAnalyticsPricingResponseData:
    """
    Pricing FxSpots by providing their definitions.

    Parameters
    ----------
    definitions : List[FxSpotDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : FxPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
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
    FxSpotAnalyticsPricingResponseData


    Examples
    --------
    >>> # Calling FxSpots price with parameters.
    >>>
    >>> fx_spot_definition = FxSpotDefinitionInstrument(
    >>>     definition=FxSpotDefinition(
    >>>         quoted_currency="EUR",
    >>>         base_currency="CHF",
    >>>         deal_amount=2000000,
    >>>         rate=FxRate(value=1.1, scaling_factor=1, rate_precision=1),
    >>>         start_date=AdjustableDate(date=datetime.date(2024, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY),
    >>>         end_date=AdjustableDate(date=datetime.date(2024, 3, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY),
    >>>         payer=PartyEnum.PARTY1,
    >>>         receiver=PartyEnum.PARTY2,
    >>>     )
    >>> )
    >>>
    >>> params = FxPricingParameters(
    >>>     ignore_reference_currency_holidays=True,
    >>>     reference_currency="USD",
    >>>     report_currency="USD",
    >>>     valuation_date="2024-01-11",
    >>> )
    >>>
    >>> price(definitions=[fx_spot_definition], pricing_preferences=params, return_market_data=False)
    {'analytics': [{'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}], 'definitions': [{'definition': {'startDate': {'dateType': 'RelativeAdjustableDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}, 'reference': '0d946061-1c76-414e-a35c-b5dc592fe207', 'code': 'FxSpot1'}], 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}

    """

    try:
        logger.info("Calling price")

        response = Client().fx_spots_resource.price(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            market_data=market_data,
            return_market_data=return_market_data,
        )

        output = response.data
        logger.info("Called price")

        return output
    except Exception as err:
        logger.error("Error price.")
        check_exception_and_raise(err, logger)


def search(
    *,
    item_per_page: Optional[int] = None,
    page: Optional[int] = None,
    spaces: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    space_name_sort_order: Optional[Union[str, SortingOrderEnum]] = None,
    tags: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> List[FxSpotInfo]:
    """
    List the FxSpots existing in the platform (depending on permissions)

    Parameters
    ----------
    item_per_page : int, optional
        A parameter used to select the number of items allowed per page. The valid range is 1-500. If not provided, 50 will be used.
    page : int, optional
        A parameter used to define the page number to display.
    spaces : List[str], optional
        A parameter used to search for platform resources stored in a given space. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space.
        If space is not specified, it will search within all spaces.
    names : List[str], optional
        A parameter used to search for platform resources with given names.
    space_name_sort_order : Union[str, SortingOrderEnum], optional
        A parameter used to sort platform resources by name based on a defined order.
    tags : List[str], optional
        A parameter used to search for platform resources with given tags.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[FxSpotInfo]
        Object defining the related links available on a FxSpot resource.

    Examples
    --------
    Search all previously saved FxSpots.

    >>> search()
    [{'type': 'FxSpot', 'id': '1f009c8a-6a48-4b06-9e94-656d0cef8250', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'MyFxSpot', 'space': 'HOME'}}]

    Search by names and spaces.

    >>> search(names=["USDEUR"], spaces=["MYSPOT"])
    [{'type': 'FxSpot', 'id': '1f009c8a-6a48-4b06-9e94-656d0cef8250', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'MyFxSpot', 'space': 'HOME'}}]

    Search by names.

    >>> search(names=["USDEUR"])
    [{'type': 'FxSpot', 'id': '1f009c8a-6a48-4b06-9e94-656d0cef8250', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'MyFxSpot', 'space': 'HOME'}}]

    Search by spaces.

    >>> search(spaces=["MYSPOT"])
    [{'type': 'FxSpot', 'id': '1f009c8a-6a48-4b06-9e94-656d0cef8250', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'MyFxSpot', 'space': 'HOME'}}]

    Search by tags.

    >>> search(tags=["USDEUR"])
    [{'type': 'FxSpot', 'id': '1f009c8a-6a48-4b06-9e94-656d0cef8250', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'MyFxSpot', 'space': 'HOME'}}]

    """

    try:
        logger.info("Calling search")

        response = Client().fx_spots_resource.list(
            item_per_page=item_per_page,
            page=page,
            spaces=spaces,
            names=names,
            space_name_sort_order=space_name_sort_order,
            tags=tags,
            fields=fields,
        )

        output = response.data
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)


def value(
    *,
    definitions: List[FxSpotDefinitionInstrument],
    pricing_preferences: Optional[FxPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> FxSpotAnalyticsValuationResponseData:
    """
    Valuing FxSpots by providing their definitions.

    Parameters
    ----------
    definitions : List[FxSpotDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : FxPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
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
    FxSpotAnalyticsValuationResponseData


    Examples
    --------
    >>> # Calling FxSpots value with parameters.
    >>>
    >>> fx_spot_definition = FxSpotDefinitionInstrument(
    >>>     definition=FxSpotDefinition(
    >>>         quoted_currency="EUR",
    >>>         base_currency="CHF",
    >>>         deal_amount=2000000,
    >>>         rate=FxRate(value=1.1, scaling_factor=1, rate_precision=1),
    >>>         start_date=AdjustableDate(
    >>>             date=datetime.date(2024, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         end_date=AdjustableDate(
    >>>             date=datetime.date(2024, 3, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         payer=PartyEnum.PARTY1,
    >>>         receiver=PartyEnum.PARTY2,
    >>>     )
    >>> )
    >>>
    >>> params = FxPricingParameters(
    >>>     ignore_reference_currency_holidays=True,
    >>>     reference_currency="USD",
    >>>     report_currency="USD",
    >>>     valuation_date="2024-01-11",
    >>> )
    >>>
    >>> value(definitions=[fx_spot_definition], pricing_preferences=params, return_market_data=False)
    {'definitions': [{'definition': {'startDate': {'dateType': 'RelativeAdjustableDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}, 'reference': '0d946061-1c76-414e-a35c-b5dc592fe207', 'code': 'FxSpot1'}], 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'analytics': [{'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 596873.601432359, 'marketValueInReportCcy': 543893.314580022, 'marketValueInDealCcy': 543893.314580022}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}], 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}], 'fxCrossCode': 'EURUSD'}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}

    """

    try:
        logger.info("Calling value")

        response = Client().fx_spots_resource.value(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            market_data=market_data,
            return_market_data=return_market_data,
        )

        output = response.data
        logger.info("Called value")

        return output
    except Exception as err:
        logger.error("Error value.")
        check_exception_and_raise(err, logger)
