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
    Amount,
    BidAskMidSimpleValues,
    BusinessDayAdjustmentDefinition,
    CityNameEnum,
    CompoundingType,
    ConvexityAdjustment,
    CurrencyBasisSwapConstituent,
    CurrencyBasisSwapConstituentDefinition,
    Curve,
    CurveCalculationParameters,
    CurvePointRelatedInstruments,
    DateMovingConvention,
    DayCountBasis,
    DepositConstituentDefinition,
    DepositFxConstituent,
    Description,
    DiscountCurveAssignment,
    DividendCurve,
    DividendCurvePoint,
    ExtrapolationMode,
    FieldDefinition,
    FieldValue,
    ForwardCurveAssignment,
    FxConstituent,
    FxForwardConstituent,
    FxForwardConstituentDefinition,
    FxForwardCurveCalculationParameters,
    FxForwardCurveCalculationPreferences,
    FxForwardCurveDataOnResourceResponseData,
    FxForwardCurveDataResponseData,
    FxForwardCurveDataResponseWithError,
    FxForwardCurveDefinition,
    FxForwardCurveDefinitionInstrument,
    FxForwardCurveInfo,
    FxForwardCurveInterpolationMode,
    FxOutrightCurve,
    FxOutrightCurveDescription,
    FxOutrightCurvePoint,
    FxSpotConstituent,
    FxSpotConstituentDefinition,
    IndirectSourcesDeposits,
    IndirectSourcesSwaps,
    InnerError,
    InterestRateCurveCalculationParameters,
    InterestRateCurveInterpolationMode,
    IrZcCurve,
    IrZcCurvePoint,
    Location,
    PriceSide,
    Quote,
    QuoteDefinition,
    Rate,
    ServiceError,
    SortingOrderEnum,
    TenorType,
    UnitEnum,
    ValuationTime,
    Values,
)

from ._fx_forward_curve import FxForwardCurve
from ._logger import logger

__all__ = [
    "Amount",
    "BusinessDayAdjustmentDefinition",
    "CityNameEnum",
    "CompoundingType",
    "ConvexityAdjustment",
    "CurrencyBasisSwapConstituent",
    "CurrencyBasisSwapConstituentDefinition",
    "Curve",
    "CurveCalculationParameters",
    "CurvePointRelatedInstruments",
    "DepositConstituentDefinition",
    "DepositFxConstituent",
    "DiscountCurveAssignment",
    "DividendCurve",
    "DividendCurvePoint",
    "ForwardCurveAssignment",
    "FxConstituent",
    "FxForwardConstituent",
    "FxForwardConstituentDefinition",
    "FxForwardCurve",
    "FxForwardCurveCalculationParameters",
    "FxForwardCurveCalculationPreferences",
    "FxForwardCurveDataOnResourceResponseData",
    "FxForwardCurveDataResponseData",
    "FxForwardCurveDataResponseWithError",
    "FxForwardCurveDefinition",
    "FxForwardCurveDefinitionInstrument",
    "FxForwardCurveInfo",
    "FxOutrightCurve",
    "FxOutrightCurveDescription",
    "FxOutrightCurvePoint",
    "FxSpotConstituent",
    "FxSpotConstituentDefinition",
    "IndirectSourcesDeposits",
    "IndirectSourcesSwaps",
    "InterestRateCurveCalculationParameters",
    "InterestRateCurveInterpolationMode",
    "IrZcCurve",
    "IrZcCurvePoint",
    "PriceSide",
    "Rate",
    "UnitEnum",
    "ValuationTime",
    "calculate",
    "create_from_deposits",
    "create_from_fx_forwards",
    "delete",
    "load",
    "search",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a FxForwardCurve using its name and space.
    This function should be used for various financial operations like calculating curve points, valuating FX Forwards, and pricing based on historical or forecasted valuation dates on a predefined FX Forward Curve.

    Parameters
    ----------
    resource_id : str, optional
        The FxForwardCurve id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The FxForwardCurve name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the FxForwardCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    FxForwardCurve
        The FxForwardCurve instance.

    Examples
    --------
    Load by Id.

    >>> load(resource_id="125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR")
    <FxForwardCurve space='MYCURVE' name='EURCHF_Fx_Forward_Curve' 125B1CUR‥>

    Load by name and space.

    >>> load(name="EURCHF_Fx_Forward_Curve", space="MYCURVE")
    <FxForwardCurve space='MYCURVE' name='EURCHF_Fx_Forward_Curve' 125B1CUR‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load FxForwardCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxForwardCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxForwardCurve not found by identifier name={name} space={space}")
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
    Delete FxForwardCurve instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The FxForwardCurve resource ID.
        Required if name is not provided.
    name : str, optional
        The FxForwardCurve name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the FxForwardCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    Delete by Id.

    >>> delete(resource_id='125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR')
    True

    Delete by name and space.

    >>> delete(name="EURCHF_Fx_Forward_Curve", space="MYCURVE")
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
    logger.info(f"Delete FxForwardCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FxForwardCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FxForwardCurve not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def calculate(
    *,
    definitions: List[FxForwardCurveDefinitionInstrument],
    pricing_preferences: Optional[FxForwardCurveCalculationParameters] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> FxForwardCurveDataResponseData:
    """
    Calculate curve points from a custom definition - on the fly.
    The user can override a reference currency, constituents and calculation preferences.

    Parameters
    ----------
    definitions : List[FxForwardCurveDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : FxForwardCurveCalculationParameters, optional
        The parameters that control the computation of the analytics.
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
    FxForwardCurveDataResponseData


    Examples
    --------
    >>> parameters = FxForwardCurveCalculationPreferences(
    >>>     extrapolation_mode=ExtrapolationMode.CONSTANT,
    >>>     ignore_pivot_currency_holidays=False,
    >>>     interpolation_mode=FxForwardCurveInterpolationMode.LINEAR,
    >>>     use_delayed_data_if_denied=False,
    >>>     ignore_invalid_instruments=True
    >>> )
    >>>
    >>> pricing_params = FxForwardCurveCalculationParameters(
    >>>     fx_forward_curve_calculation_preferences=parameters, valuation_date=datetime.date(2022, 10, 12), curve_tenors=["1M"]
    >>> )
    >>>
    >>> fx_fwd_curve_definition = FxForwardCurveDefinitionInstrument(
    >>>     definition=FxForwardCurveDefinition(
    >>>         cross_currency="EURCHF",
    >>>         reference_currency="USD",
    >>>         constituents=[
    >>>             FxSpotConstituent(
    >>>                 definition=FxSpotConstituentDefinition(template="EURUSD"),
    >>>                 quote=Quote(
    >>>                     definition=QuoteDefinition(instrument_code="EURUSD=", source="Composite"),
    >>>                     values_property=Values(bid=FieldValue(value=0.9396), ask=FieldValue(value=0.9401)),
    >>>                 ),
    >>>             )
    >>>         ],
    >>>     ),
    >>>     reference="NF",
    >>>     code="UEV",
    >>> )
    >>>
    >>> # Calling calculate of FxForwardCurves with parameters.
    >>> response = calculate(definitions=[fx_fwd_curve_definition], pricing_preferences=pricing_params)
    >>> print(json.dumps(response.analytics[0].as_dict(), indent=2)[:500] + "...")
    {
      "outrightCurve": {
        "curveType": "FxOutrightCurve",
        "points": [
          {
            "startDate": "2022-10-14",
            "endDate": "2022-11-14",
            "tenor": "1M",
            "outright": {
              "bid": 0.936387922958,
              "ask": 0.937568268472,
              "mid": 0.936978095715
            },
            "instruments": [
              {
                "instrumentCode": "EUR1M="
              },
              {
                "instrumentCode": "CHF1M="
              }
            ]
          }
        ]
      },
      "invalidCons...

    """

    try:
        logger.info("Calling calculate")

        response = Client().fx_forward_curves_resource.calculate(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            return_market_data=return_market_data,
        )

        output = response.data
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)


def create_from_deposits(
    *,
    cross_currency: str,
    reference_currency: Optional[str] = None,
    additional_tenor_types: Optional[List[Union[str, TenorType]]] = None,
    sources: Optional[IndirectSourcesDeposits] = None,
    fields: Optional[str] = None,
) -> FxForwardCurve:
    """
    The request used to build a curve from FxSpot and Deposit constituents when the cross-currency quotation can be derived via a reference currency.
    For example, if a reference currency is specified, available FxSpot constituents are returned for each currency in the pair against the reference (e.g., EURGBP via EURUSD and GBPUSD).
    If the reference currency is one of the pair, only constituents for that pair are returned; if not specified, the first currency of the pair is used as the reference.
    Available Deposit constituents are returned for each currency of the pair.
    The output tenors depend on the construction path; by default, market-contributed tenors are returned.

    Parameters
    ----------
    cross_currency : str
        A string to define the cross currency pair of the curve, expressed in ISO 4217 alphabetical format (e.g., 'EURCHF'). Maximum of 6 characters.
    reference_currency : str, optional
        A string to define the reference currency for the cross-currency pair of the curve, expressed in ISO 4217 alphabetical format (e.g., 'EUR'). Maximum of 3 characters. Default is the base currency of the specified cross currency pair.
    additional_tenor_types : List[Union[str, TenorType]], optional
        An array of tenor types that can be used for instruments, in addition to the standard tenor. When passing a string value, it must be one of the TenorType values.
    sources : IndirectSourcesDeposits, optional
        An object that defines the sources containing the market data for the instruments used to create the curve definition.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FxForwardCurve
        FxForwardCurve

    Examples
    --------
    >>> create_from_deposits(
    >>>     cross_currency="EURGBP",
    >>>     reference_currency="USD",
    >>>     sources=IndirectSourcesDeposits(
    >>>         base_fx_spot="ICAP",
    >>>         quoted_fx_spot="ICAP",
    >>>         base_deposit="ICAP",
    >>>         quoted_deposit="CRDA",
    >>>     ),
    >>>     additional_tenor_types=[TenorType.LONG, TenorType.END_OF_MONTH],
    >>> )
    <FxForwardCurve space=None name='' unsaved>

    """

    try:
        logger.info("Calling create_from_deposits")

        response = Client().fx_forward_curves_resource.build_from_deposits(
            fields=fields,
            cross_currency=cross_currency,
            reference_currency=reference_currency,
            additional_tenor_types=additional_tenor_types,
            sources=sources,
        )

        output = response.data
        logger.info("Called create_from_deposits")

        return FxForwardCurve(output)
    except Exception as err:
        logger.error("Error create_from_deposits")
        check_exception_and_raise(err, logger)


def create_from_fx_forwards(
    *,
    cross_currency: str,
    reference_currency: Optional[str] = None,
    additional_tenor_types: Optional[List[Union[str, TenorType]]] = None,
    sources: Optional[IndirectSourcesSwaps] = None,
    fields: Optional[str] = None,
) -> FxForwardCurve:
    """
    The request used to build a curve from FxSpot and FxForward constituents when the cross-currency quotation can be derived via a reference currency.
    For example, if a reference currency is specified, available constituents are returned for each currency in the pair against the reference (e.g., EURGBP via EURUSD and GBPUSD).
    If the reference currency is one of the pair, only constituents for that pair are returned; if not specified, the first currency of the pair is used as the reference.
    The output tenors depend on the construction path; by default, market-contributed tenors are returned.

    Parameters
    ----------
    cross_currency : str
        A string to define the cross currency pair of the curve, expressed in ISO 4217 alphabetical format (e.g., 'EURCHF'). Maximum of 6 characters.
    reference_currency : str, optional
        A string to define the reference currency for the cross-currency pair of the curve, expressed in ISO 4217 alphabetical format (e.g., 'EUR'). Maximum of 3 characters. Default is the base currency of the specified cross currency pair.
    additional_tenor_types : List[Union[str, TenorType]], optional
        An array of tenor types that can be used for instruments, in addition to the standard tenor. When passing a string value, it must be one of the TenorType types.
    sources : IndirectSourcesSwaps, optional
        An object that defines the sources containing the market data for the instruments used to create the curve definition. It will return from all the accessible sources if not specified.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FxForwardCurve
        FxForwardCurve

    Examples
    --------
    >>> create_from_fx_forwards(
    >>>     cross_currency="EURGBP",
    >>>     reference_currency="USD",
    >>>     sources=IndirectSourcesSwaps(
    >>>         base_fx_spot="ICAP",
    >>>         base_fx_forwards="ICAP",
    >>>         quoted_fx_spot="TTKL",
    >>>         quoted_fx_forwards="TTKL",
    >>>     ),
    >>>     additional_tenor_types=[TenorType.LONG, TenorType.END_OF_MONTH],
    >>> )
    <FxForwardCurve space=None name='' unsaved>

    """

    try:
        logger.info("Calling create_from_fx_forwards")

        response = Client().fx_forward_curves_resource.build_from_fx_forwards(
            fields=fields,
            cross_currency=cross_currency,
            reference_currency=reference_currency,
            additional_tenor_types=additional_tenor_types,
            sources=sources,
        )

        output = response.data
        logger.info("Called create_from_fx_forwards")

        return FxForwardCurve(output)
    except Exception as err:
        logger.error("Error create_from_fx_forwards")
        check_exception_and_raise(err, logger)


def _delete_by_id(curve_id: str) -> bool:
    """
    Delete a FxForwardCurve that exists in the platform. The FxForwardCurve can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_id : str
        The curve identifier.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting FxForwardCurve with id: {curve_id}")
        Client().fx_forward_curve_resource.delete(curve_id=curve_id)
        logger.info(f"Deleted FxForwardCurve with id: {curve_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting FxForwardCurve with id: {curve_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(curve_id: str, fields: Optional[str] = None) -> FxForwardCurve:
    """
    Access a FxForwardCurve existing in the platform (read). The FxForwardCurve can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_id : str
        The curve identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FxForwardCurve


    Examples
    --------


    """

    try:
        logger.info(f"Opening FxForwardCurve with id: {curve_id}")

        response = Client().fx_forward_curve_resource.read(curve_id=curve_id, fields=fields)

        output = FxForwardCurve(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening FxForwardCurve:")
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
) -> List[FxForwardCurveInfo]:
    """
    List the FxForwardCurves existing in the platform (depending on permissions)

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
    List[FxForwardCurveInfo]
        A model partially describing the FXForward Curve returned by the GET list service.

    Examples
    --------
    Search all previously saved curves.

    >>> search()
    [{'type': 'FxForwardCurve', 'id': '315B1CUR-6EE9-4B1F-870F-5BA89EBE71EU', 'location': {'name': 'EURUSD Fx Forward Curve', 'space': 'LSEG'}},
     {'type': 'FxForwardCurve', 'id': '225B1CUR-6EE9-4B1F-870F-5BA89EBE71CR', 'description': {'tags': ['EURGBP', 'EUR', 'GBP', 'FxForwardCurve'], 'summary': 'EURGBP Fx Forward Curve via USD'}, 'location': {'name': 'EURGBP Fx Forward Curve', 'space': 'MYSPACE'}},
     {'type': 'FxForwardCurve', 'id': '125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForwardCurve'], 'summary': 'EURCHF Fx Forward Curve via USD and user surces'}, 'location': {'name': 'EURCHF Fx Forward Curve', 'space': 'MYCURVE'}}]

    Search by names and spaces.

    >>> search(names=["EURCHF_Fx_Forward_Curve"], spaces=["MYCURVE"])
    [{'type': 'FxForwardCurve', 'id': 'b4abc17d-c199-4dc5-87de-7c2f206dfcaa', 'location': {'space': 'LSEG', 'name': 'EUR_CHF_FxCross'}, 'description': {'summary': 'LSEG EUR CHF FxCross', 'tags': []}}]

    Search by names.

    >>> search(names=["EURCHF_Fx_Forward_Curve"])
    [{'type': 'FxForwardCurve', 'id': 'b4abc17d-c199-4dc5-87de-7c2f206dfcaa', 'location': {'space': 'LSEG', 'name': 'EUR_CHF_FxCross'}, 'description': {'summary': 'LSEG EUR CHF FxCross', 'tags': []}}]

    Search by spaces.

    >>> search(spaces=["MYCURVE"])
    [{'type': 'FxForwardCurve', 'id': 'b4abc17d-c199-4dc5-87de-7c2f206dfcaa', 'location': {'space': 'LSEG', 'name': 'EUR_CHF_FxCross'}, 'description': {'summary': 'LSEG EUR CHF FxCross', 'tags': []}}]

    Search by tags.

    >>> search(tags=["EURCHF"])
    [{'type': 'FxForwardCurve', 'id': '315B1CUR-6EE9-4B1F-870F-5BA89EBE71EU', 'location': {'name': 'EURUSD Fx Forward Curve', 'space': 'LSEG'}},
     {'type': 'FxForwardCurve', 'id': '225B1CUR-6EE9-4B1F-870F-5BA89EBE71CR', 'description': {'tags': ['EURGBP', 'EUR', 'GBP', 'FxForwardCurve'], 'summary': 'EURGBP Fx Forward Curve via USD'}, 'location': {'name': 'EURGBP Fx Forward Curve', 'space': 'MYSPACE'}},
     {'type': 'FxForwardCurve', 'id': '125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR', 'description': {'tags': ['EURCHF', 'EUR', 'CHF', 'FxForwardCurve'], 'summary': 'EURCHF Fx Forward Curve via USD and user surces'}, 'location': {'name': 'EURCHF Fx Forward Curve', 'space': 'MYCURVE'}}]

    """

    try:
        logger.info("Calling search")

        response = Client().fx_forward_curves_resource.list(
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
