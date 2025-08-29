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
    FxForwardAnalyticsPricingOnResourceResponseData,
    FxForwardAnalyticsPricingResponseData,
    FxForwardAnalyticsPricingResponseWithError,
    FxForwardAnalyticsValuationOnResourceResponseData,
    FxForwardAnalyticsValuationResponseData,
    FxForwardAnalyticsValuationResponseWithError,
    FxForwardCurveChoice,
    FxForwardDefinition,
    FxForwardDefinitionInstrument,
    FxForwardInfo,
    FxForwardOverride,
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
    FxSpotDefinition,
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

from ._fx_forward import FxForward
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
    "FxForward",
    "FxForwardAnalyticsDescription",
    "FxForwardAnalyticsPricingOnResourceResponseData",
    "FxForwardAnalyticsPricingResponseData",
    "FxForwardAnalyticsPricingResponseWithError",
    "FxForwardAnalyticsValuationOnResourceResponseData",
    "FxForwardAnalyticsValuationResponseData",
    "FxForwardAnalyticsValuationResponseWithError",
    "FxForwardCurveChoice",
    "FxForwardDefinition",
    "FxForwardDefinitionInstrument",
    "FxForwardInfo",
    "FxForwardOverride",
    "FxForwardPricingAnalysis",
    "FxForwardRisk",
    "FxForwardValuation",
    "FxOptionVolSurfaceChoice",
    "FxPricingAnalysis",
    "FxPricingParameters",
    "FxRate",
    "FxRateTypeEnum",
    "FxRisk",
    "FxSpotAnalyticsDescription",
    "FxSpotDefinition",
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
    Load a FxForward using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The FxForward id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The FxForward name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the FxForward is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    FxForward
        The FxForward instance.

    Examples
    --------
    Load by Id.

    >>> load(resource_id="995B1CUR-6EE9-4B1F-870F-5BA89EBE71CR")
    <FxForward space='MYSPACE' name='EURCHF' c37f18fc‥>

    Load by name and space.

    >>> load(name="EURCHF", space="MYSPACE")
    <FxForward space='MYSPACE' name='EURCHF' c37f18fc‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load FxForward {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxForward {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxForward not found by identifier name={name} space={space}")
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
    Delete FxForward instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The FxForward resource ID.
        Required if name is not provided.
    name : str, optional
        The FxForward name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the FxForward is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    Delete by Id.

    >>> delete(resource_id='995B1CUR-6EE9-4B1F-870F-5BA89EBE71CR')
    True

    Delete by name and space.

    >>> delete(name="EURCHF", space="MYSPACE")
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
    logger.info(f"Delete FxForward {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxForward {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxForward not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def create_from_template(
    *,
    reference: str,
    overrides: Optional[FxForwardOverride] = None,
    fields: Optional[str] = None,
) -> FxForward:
    """
    Creating FxForwards from an existing template and a set of overrides.

    Parameters
    ----------
    reference : str
        The reference to the Fx Forward template.
    overrides : FxForwardOverride, optional
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
    FxForward
        FxForward

    Examples
    --------
    >>> overrides = FxForwardOverride(
    >>>     deal_amount=10000,
    >>>     contra_amount=10000,
    >>>     rate=FxRate(value=0.5, scaling_factor=1, rate_precision=1),
    >>>     end_date=AdjustableDate(
    >>>         date=datetime.date(2024, 3, 1), date_moving_convention=DateMovingConvention.MODIFIED_FOLLOWING
    >>>     ),
    >>>     start_date=AdjustableDate(
    >>>         date=datetime.date(2024, 1, 1), date_moving_convention=DateMovingConvention.MODIFIED_FOLLOWING
    >>>     ),
    >>>     settlement_type="Cash",
    >>> )
    >>> create_from_template(reference="810d2c52-f904-4314-845b-ea4595d40f35", overrides=overrides)
    <FxForward space=None name='' unsaved>

    """

    try:
        logger.info("Calling create_from_template")

        response = Client().fx_forwards_resource.build_fx_forward_from_template(
            fields=fields, reference=reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_template")

        return FxForward(output)
    except Exception as err:
        logger.error("Error create_from_template")
        check_exception_and_raise(err, logger)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a FxForward that exists in the platform. The FxForward can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting FxForward with id: {instrument_id}")
        Client().fx_forward_resource.delete(instrument_id=instrument_id)
        logger.info(f"Deleted FxForward with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting FxForward with id: {instrument_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> FxForward:
    """
    Access a FxForward existing in the platform (read). The FxForward can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    FxForward


    Examples
    --------


    """

    try:
        logger.info(f"Opening FxForward with id: {instrument_id}")

        response = Client().fx_forward_resource.read(instrument_id=instrument_id, fields=fields)

        output = FxForward(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening FxForward:")
        check_exception_and_raise(err, logger)


def price(
    *,
    definitions: List[FxForwardDefinitionInstrument],
    pricing_preferences: Optional[FxPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> FxForwardAnalyticsPricingResponseData:
    """
    Pricing FxForwards by providing their definitions.

    Parameters
    ----------
    definitions : List[FxForwardDefinitionInstrument]
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
    FxForwardAnalyticsPricingResponseData


    Examples
    --------
    >>> # Calling FxForwards price with parameters
    >>>
    >>> fxforward_definition = FxForwardDefinitionInstrument(
    >>>     definition=FxForwardDefinition(
    >>>         quoted_currency="EUR",
    >>>         base_currency="CHF",
    >>>         deal_amount=2000000,
    >>>         rate=FxRate(value=1.1, scaling_factor=1, rate_precision=1),
    >>>         end_date=AdjustableDate(
    >>>             date=datetime.date(2024, 3, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         payer=PartyEnum.PARTY1,
    >>>         receiver=PartyEnum.PARTY2,
    >>>         start_date=AdjustableDate(
    >>>             date=datetime.date(2024, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         settlement_type="Cash",
    >>>     ),
    >>> )
    >>> market_data = MarketData(fx_forward_curves=[FxForwardCurveChoice(reference="EUR_GBP_FxForward")])
    >>> params = FxPricingParameters(
    >>>     ignore_reference_currency_holidays=True,
    >>>     reference_currency="USD",
    >>>     report_currency="USD",
    >>>     valuation_date="2024-01-11",
    >>> )
    >>>
    >>> price(definitions=[fxforward_definition], pricing_preferences=params, return_market_data=False, market_data=market_data)
    {'analytics': [{'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}], 'definitions': [{'definition': {'startDate': {'dateType': 'RelativeAdjustableDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}, 'reference': '0d946061-1c76-414e-a35c-b5dc592fe207', 'code': 'FxSpot1'}], 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}

    """

    try:
        logger.info("Calling price")

        response = Client().fx_forwards_resource.price(
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
) -> List[FxForwardInfo]:
    """
    List the FxForwards existing in the platform (depending on permissions)

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
    List[FxForwardInfo]
        Object defining the related links available on a FxForward resource.

    Examples
    --------
    Search all previously saved FxForwards.

    >>> search()
    [{'type': 'FxForward', 'id': 'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForward'], 'summary': 'EURCHF Fx Forward via USD'}, 'location': {'name': 'EURCHF', 'space': 'MYSPACE'}}]

    Search by names and spaces.

    >>> search(names=["EURCHF"], spaces=["MYSPACE"])
    [{'type': 'FxForward', 'id': 'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForward'], 'summary': 'EURCHF Fx Forward via USD'}, 'location': {'name': 'EURCHF', 'space': 'MYSPACE'}}]

    Search by names.

    >>> search(names=["EURCHF"])
    [{'type': 'FxForward', 'id': 'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForward'], 'summary': 'EURCHF Fx Forward via USD'}, 'location': {'name': 'EURCHF', 'space': 'MYSPACE'}}]

    Search by spaces.

    >>> search(spaces=["MYSPACE"])
    [{'type': 'FxForward', 'id': 'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForward'], 'summary': 'EURCHF Fx Forward via USD'}, 'location': {'name': 'EURCHF', 'space': 'MYSPACE'}}]

    Search by tags.

    >>> search(tags=["EURCHF"])
    [{'type': 'FxForward', 'id': 'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForward'], 'summary': 'EURCHF Fx Forward via USD'}, 'location': {'name': 'EURCHF', 'space': 'MYSPACE'}}]

    """

    try:
        logger.info("Calling search")

        response = Client().fx_forwards_resource.list(
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
    definitions: List[FxForwardDefinitionInstrument],
    pricing_preferences: Optional[FxPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> FxForwardAnalyticsValuationResponseData:
    """
    Valuing FxForwards by providing their definitions.

    Parameters
    ----------
    definitions : List[FxForwardDefinitionInstrument]
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
    FxForwardAnalyticsValuationResponseData


    Examples
    --------
    >>> # Calling FxForwards value with parameters
    >>>
    >>> fxforward_definition = FxForwardDefinitionInstrument(
    >>>     definition=FxForwardDefinition(
    >>>         quoted_currency="EUR",
    >>>         base_currency="CHF",
    >>>         deal_amount=2000000,
    >>>         contra_amount=1969900,
    >>>         end_date=AdjustableDate(
    >>>             date=datetime.date(2024, 3, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         payer=PartyEnum.PARTY1,
    >>>         receiver=PartyEnum.PARTY2,
    >>>         start_date=AdjustableDate(
    >>>             date=datetime.date(2024, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         settlement_type="Cash",
    >>>     ),
    >>> )
    >>>
    >>> params = FxPricingParameters(
    >>>     ignore_reference_currency_holidays=True,
    >>>     reference_currency="USD",
    >>>     report_currency="USD",
    >>>     valuation_date="2024-01-11",
    >>> )
    >>>
    >>> value(definitions=[fxforward_definition], pricing_preferences=params, return_market_data=False)
    {'analytics': [{'description': {'startDate': {'unAdjusted': '2025-01-01', 'adjusted': '2025-01-02', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-01-01'}, 'endDate': {'unAdjusted': '2025-12-31', 'adjusted': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-12-31'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 594260.839617766, 'marketValueInReportCcy': 514407.470653874, 'discountFactor': 0.966425624427335, 'marketValueInDealCcy': 514407.470653874}, 'greeks': {'deltaPercent': 42.7681916939807, 'deltaAmountInDealCcy': 427681.916939807, 'deltaAmountInContraCcy': 966425.624427335}}], 'definitions': [{'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2025-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'settlementType': 'Physical', 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}, 'reference': 'de049073-a9d2-8326-2128-1bb4964a6f86', 'code': 'FxForward1'}], 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}

    """

    try:
        logger.info("Calling value")

        response = Client().fx_forwards_resource.value(
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
