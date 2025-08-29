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
    AmortizationDefinition,
    AmortizationTypeEnum,
    Amount,
    BachelierParameters,
    BasePricingParameters,
    BlackScholesEquityParameters,
    BlackScholesFxParameters,
    BlackScholesInterestRateFuture,
    BusinessDayAdjustmentDefinition,
    CapFloorDefinition,
    CapFloorTypeEnum,
    CmdtyOptionVolSurfaceChoice,
    CmdtyVolSurfaceInput,
    CompoundingModeEnum,
    ConvexityAdjustment,
    CouponReferenceDateEnum,
    CreditCurveChoice,
    CreditCurveInput,
    CurveDataPoint,
    Date,
    DatedRate,
    DatedValue,
    DateMovingConvention,
    DayCountBasis,
    Description,
    DirectionEnum,
    Dividend,
    DividendTypeEnum,
    EndOfMonthConvention,
    EqOptionVolSurfaceChoice,
    EqVolSurfaceInput,
    FixedRateDefinition,
    FloatingRateDefinition,
    FrequencyEnum,
    FutureDate,
    FutureDateCalculationMethodEnum,
    FxCurveInput,
    FxForwardCurveChoice,
    FxOptionVolSurfaceChoice,
    FxPricingParameters,
    FxRateTypeEnum,
    FxVolSurfaceInput,
    HestonEquityParameters,
    IndexCompoundingDefinition,
    IndexObservationMethodEnum,
    InnerError,
    InterestRateDefinition,
    InterestRateLegDefinition,
    IrCapVolSurfaceChoice,
    IrCurveChoice,
    IrMeasure,
    IrPricingParameters,
    IrRiskFields,
    IrSwapInstrumentRiskFields,
    IrSwapInstrumentValuationFields,
    IrSwapSolvingParameters,
    IrSwapSolvingTarget,
    IrSwapSolvingVariable,
    IrSwaptionVolCubeChoice,
    IrValuationFields,
    IrVolCubeInput,
    IrVolSurfaceInput,
    IrZcCurveInput,
    LoanAsCollectionItem,
    LoanDefinition,
    LoanDefinitionInstrument,
    LoanInstrumentDescriptionFields,
    LoanInstrumentRiskFields,
    LoanInstrumentSolveResponseFieldsOnResourceResponseData,
    LoanInstrumentSolveResponseFieldsResponseData,
    LoanInstrumentSolveResponseFieldsResponseWithError,
    LoanInstrumentValuationFields,
    LoanInstrumentValuationResponseFieldsOnResourceResponseData,
    LoanInstrumentValuationResponseFieldsResponseData,
    LoanInstrumentValuationResponseFieldsResponseWithError,
    Location,
    MarketData,
    MarketVolatility,
    Measure,
    ModelParameters,
    MonthEnum,
    NumericalMethodEnum,
    OffsetDefinition,
    OptionPricingParameters,
    OptionSolvingParameters,
    OptionSolvingTarget,
    OptionSolvingVariable,
    OptionSolvingVariableEnum,
    PartyEnum,
    PriceSideWithLastEnum,
    PrincipalDefinition,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    ResetDatesDefinition,
    ScheduleDefinition,
    ServiceError,
    SolvingLegEnum,
    SolvingMethod,
    SolvingMethodEnum,
    SolvingResult,
    SortingOrderEnum,
    Spot,
    SpreadCompoundingModeEnum,
    StepRateDefinition,
    StrikeTypeEnum,
    StubIndexReferences,
    StubRuleEnum,
    SwapSolvingVariableEnum,
    TimeStampEnum,
    UnitEnum,
    VolatilityTypeEnum,
    VolCubePoint,
    VolModelTypeEnum,
    VolSurfacePoint,
    ZcTypeEnum,
)

from ._loan import Loan
from ._logger import logger

__all__ = [
    "AmortizationDefinition",
    "AmortizationTypeEnum",
    "Amount",
    "BachelierParameters",
    "BasePricingParameters",
    "BlackScholesEquityParameters",
    "BlackScholesFxParameters",
    "BlackScholesInterestRateFuture",
    "BusinessDayAdjustmentDefinition",
    "CapFloorDefinition",
    "CapFloorTypeEnum",
    "CmdtyOptionVolSurfaceChoice",
    "CmdtyVolSurfaceInput",
    "CompoundingModeEnum",
    "ConvexityAdjustment",
    "CouponReferenceDateEnum",
    "CreditCurveChoice",
    "CreditCurveInput",
    "CurveDataPoint",
    "DatedRate",
    "DatedValue",
    "DirectionEnum",
    "Dividend",
    "DividendTypeEnum",
    "EqOptionVolSurfaceChoice",
    "EqVolSurfaceInput",
    "FixedRateDefinition",
    "FloatingRateDefinition",
    "FutureDate",
    "FutureDateCalculationMethodEnum",
    "FxCurveInput",
    "FxForwardCurveChoice",
    "FxOptionVolSurfaceChoice",
    "FxPricingParameters",
    "FxRateTypeEnum",
    "FxVolSurfaceInput",
    "HestonEquityParameters",
    "IndexCompoundingDefinition",
    "IndexObservationMethodEnum",
    "InterestRateDefinition",
    "InterestRateLegDefinition",
    "IrCapVolSurfaceChoice",
    "IrCurveChoice",
    "IrMeasure",
    "IrPricingParameters",
    "IrRiskFields",
    "IrSwapInstrumentRiskFields",
    "IrSwapInstrumentValuationFields",
    "IrSwapSolvingParameters",
    "IrSwapSolvingTarget",
    "IrSwapSolvingVariable",
    "IrSwaptionVolCubeChoice",
    "IrValuationFields",
    "IrVolCubeInput",
    "IrVolSurfaceInput",
    "IrZcCurveInput",
    "Loan",
    "LoanAsCollectionItem",
    "LoanDefinition",
    "LoanDefinitionInstrument",
    "LoanInstrumentDescriptionFields",
    "LoanInstrumentRiskFields",
    "LoanInstrumentSolveResponseFieldsOnResourceResponseData",
    "LoanInstrumentSolveResponseFieldsResponseData",
    "LoanInstrumentSolveResponseFieldsResponseWithError",
    "LoanInstrumentValuationFields",
    "LoanInstrumentValuationResponseFieldsOnResourceResponseData",
    "LoanInstrumentValuationResponseFieldsResponseData",
    "LoanInstrumentValuationResponseFieldsResponseWithError",
    "MarketData",
    "MarketVolatility",
    "Measure",
    "ModelParameters",
    "MonthEnum",
    "NumericalMethodEnum",
    "OffsetDefinition",
    "OptionPricingParameters",
    "OptionSolvingParameters",
    "OptionSolvingTarget",
    "OptionSolvingVariable",
    "OptionSolvingVariableEnum",
    "PartyEnum",
    "PriceSideWithLastEnum",
    "PrincipalDefinition",
    "Rate",
    "ResetDatesDefinition",
    "ScheduleDefinition",
    "SolvingLegEnum",
    "SolvingMethod",
    "SolvingMethodEnum",
    "SolvingResult",
    "Spot",
    "SpreadCompoundingModeEnum",
    "StepRateDefinition",
    "StrikeTypeEnum",
    "StubIndexReferences",
    "SwapSolvingVariableEnum",
    "TimeStampEnum",
    "UnitEnum",
    "VolCubePoint",
    "VolModelTypeEnum",
    "VolSurfacePoint",
    "VolatilityTypeEnum",
    "ZcTypeEnum",
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
    Load a Loan using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The Loan id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The Loan name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the Loan is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    Loan
        The Loan instance.

    Examples
    --------
    >>> # execute the search of loan templates using id
    >>> loaded_template = load(resource_id=loan_templates[0].id)
    >>>
    >>> print(loaded_template)
    <Loan space='HOME' name='LoanResourceCreatd_For_Sdk_Notebooks' 7caf85a5‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load Loan {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Loan {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Loan not found by identifier name={name} space={space}")
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
    Delete Loan instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The Loan resource ID.
        Required if name is not provided.
    name : str, optional
        The Loan name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the Loan is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    >>> # Delete cloned template
    >>> delete(resource_id=cloned_template.id)
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
    logger.info(f"Delete Loan {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Loan {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Loan not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a Loan that exists in the platform. The Loan can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting Loan with id: {instrument_id}")
        Client().loan_resource.delete(instrument_id=instrument_id)
        logger.info(f"Deleted Loan with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting Loan with id: {instrument_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> Loan:
    """
    Access a Loan existing in the platform (read). The Loan can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    Loan


    Examples
    --------


    """

    try:
        logger.info(f"Opening Loan with id: {instrument_id}")

        response = Client().loan_resource.read(instrument_id=instrument_id, fields=fields)

        output = Loan(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening Loan:")
        check_exception_and_raise(err, logger)


def price(
    *,
    definitions: List[LoanDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> LoanInstrumentSolveResponseFieldsResponseData:
    """
    Calculate the price (i.e., their respective fixed rates) of loans provided in the request so that a chosen property (e.g., market value, duration) equals a target value.

    Parameters
    ----------
    definitions : List[LoanDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : IrPricingParameters, optional
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
    LoanInstrumentSolveResponseFieldsResponseData


    Examples
    --------
    >>> business_day_adj = BusinessDayAdjustmentDefinition(calendars= [] , convention= "ModifiedFollowing")
    >>> start = AdjustableDate(date= "2021-03-02")
    >>> end =  RelativeAdjustableDate( reference_date= "StartDate", tenor= "10Y")
    >>> rate_definition = FloatingRateDefinition(index= "LSEG/EUR_ESTR_ON_FTSE")
    >>> interest_periods = ScheduleDefinition(business_day_adjustment= business_day_adj, start_date= start , end_date= end,frequency= "Annual", roll_convention= "Same")
    >>> offset_def = OffsetDefinition( business_day_adjustment= business_day_adj, direction= "Backward", reference_date= "PeriodEndDate", tenor= "0D" )
    >>> principal_definition = PrincipalDefinition( amount= 1000000, currency= "EUR")
    >>> loan_definition  = LoanDefinition(rate=rate_definition, interest_periods= interest_periods, payment_offset= offset_def, coupon_day_count= 'Dcb_Actual_360', accrual_day_count= 'Dcb_Actual_360', principal= principal_definition, payer= 'Party2', receiver= 'Party1')


    >>> loan_definition_Instrument = LoanDefinitionInstrument(definition=loan_definition)
    >>> pricing_parameters = IrPricingParameters( valuation_date= '2021-03-02')


    >>> price_result = price(definitions= [loan_definition_Instrument], pricing_preferences= pricing_parameters)
    >>> print(price_result)
    {'pricingPreferences': {'valuationDate': '2021-03-02', 'reportCurrency': 'EUR'}, 'analytics': [{'description': {'instrumentTag': '', 'instrumentDescription': 'Receive EUR Annual +0bp ESTR', 'startDate': '2021-03-02', 'endDate': '2031-03-03', 'tenor': '10Y'}, 'valuation': {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}, 'marketValue': {'value': -18572.358113432358, 'dealCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}, 'reportCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}}, 'cleanMarketValue': {'value': -18572.358113432358, 'dealCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}, 'reportCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}}}, 'risk': {'duration': {'value': 1.0}, 'modifiedDuration': {'value': -6.501023075545686e-05}, 'benchmarkHedgeNotional': {'value': 0.0, 'currency': 'EUR'}, 'annuity': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}, 'dv01': {'value': -0.006501023075543344, 'bp': -6.501023075543344e-05, 'dealCurrency': {'value': -0.006501023075543344, 'currency': 'EUR'}, 'reportCurrency': {'value': -0.006501023075543344, 'currency': 'EUR'}}, 'pv01': {'value': -1020.7340782749961, 'bp': -10.207340782749963, 'dealCurrency': {'value': -1020.7340782749961, 'currency': 'EUR'}, 'reportCurrency': {'value': -1020.7340782749961, 'currency': 'EUR'}}, 'br01': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}}}]}

    """

    try:
        logger.info("Calling price")

        response = Client().loans_resource.price(
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
) -> List[LoanAsCollectionItem]:
    """
    List the Loans existing in the platform (depending on permissions)

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
    List[LoanAsCollectionItem]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------
    >>> # execute the search of loan templates
    >>> loan_templates = search()
    >>>
    >>> print(loan_templates)
    [{'type': 'Loan', 'id': '7caf85a5-7c3c-4ce8-b9f5-7db8918cb7a8', 'location': {'space': 'HOME', 'name': 'LoanResourceCreatd_For_Sdk_Notebooks'}, 'description': {'summary': '', 'tags': ['test']}}]

    """

    try:
        logger.info("Calling search")

        response = Client().loans_resource.list(
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
    definitions: List[LoanDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> LoanInstrumentValuationResponseFieldsResponseData:
    """
    Calculate the market value of loans provided in the request.

    Parameters
    ----------
    definitions : List[LoanDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : IrPricingParameters, optional
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
    LoanInstrumentValuationResponseFieldsResponseData


    Examples
    --------
    >>> business_day_adj = BusinessDayAdjustmentDefinition(calendars= [] , convention= "ModifiedFollowing")
    >>> start = AdjustableDate(date= "2021-03-02")
    >>> end =  RelativeAdjustableDate( reference_date= "StartDate", tenor= "10Y")
    >>> rate_definition = FloatingRateDefinition(index= "LSEG/EUR_ESTR_ON_FTSE")
    >>> interest_periods = ScheduleDefinition(business_day_adjustment= business_day_adj, start_date= start , end_date= end,frequency= "Annual", roll_convention= "Same")
    >>> offset_def = OffsetDefinition( business_day_adjustment= business_day_adj, direction= "Backward", reference_date= "PeriodEndDate", tenor= "0D" )
    >>> principal_definition = PrincipalDefinition( amount= 1000000, currency= "EUR")
    >>> loan_definition  = LoanDefinition(rate=rate_definition, interest_periods= interest_periods, payment_offset= offset_def, coupon_day_count= 'Dcb_Actual_360', accrual_day_count= 'Dcb_Actual_360', principal= principal_definition, payer= 'Party2', receiver= 'Party1')


    >>> loan_definition_Instrument = LoanDefinitionInstrument(definition=loan_definition)
    >>> pricing_parameters = IrPricingParameters( valuation_date= '2021-03-02')


    >>> value_result = value(definitions= [loan_definition_Instrument], pricing_preferences= pricing_parameters)
    >>> print(value_result)
    {'definitions': [{'definition': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'AdjustableDate', 'date': '2021-03-02'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Annual', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'EUR', 'amount': 1000000.0}, 'payer': 'Party2', 'receiver': 'Party1'}}], 'pricingPreferences': {'valuationDate': '2021-03-02'}, 'analytics': [{'description': {'instrumentTag': '', 'instrumentDescription': 'Receive EUR Annual +0bp ESTR', 'startDate': '2021-03-02', 'endDate': '2031-03-03', 'tenor': '10Y'}, 'valuation': {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}, 'marketValue': {'value': -18572.358113432358, 'dealCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}, 'reportCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}}, 'cleanMarketValue': {'value': -18572.358113432358, 'dealCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}, 'reportCurrency': {'value': -18572.358113432358, 'currency': 'EUR'}}}, 'risk': {'duration': {'value': 1.0}, 'modifiedDuration': {'value': -6.501023075545686e-05}, 'benchmarkHedgeNotional': {'value': 0.0, 'currency': 'EUR'}, 'annuity': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}, 'dv01': {'value': -0.006501023075543344, 'bp': -6.501023075543344e-05, 'dealCurrency': {'value': -0.006501023075543344, 'currency': 'EUR'}, 'reportCurrency': {'value': -0.006501023075543344, 'currency': 'EUR'}}, 'pv01': {'value': -1020.7340782749961, 'bp': -10.207340782749963, 'dealCurrency': {'value': -1020.7340782749961, 'currency': 'EUR'}, 'reportCurrency': {'value': -1020.7340782749961, 'currency': 'EUR'}}, 'br01': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'EUR'}, 'reportCurrency': {'value': 0.0, 'currency': 'EUR'}}}}]}

    """

    try:
        logger.info("Calling value")

        response = Client().loans_resource.value(
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
