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
    Curve,
    CurveCalculationParameters,
    CurvePointRelatedInstruments,
    DateMovingConvention,
    DayCountBasis,
    DepositConstituentDefinition,
    DepositIrConstituent,
    Description,
    DividendCurve,
    DividendCurvePoint,
    ExtrapolationMode,
    FieldDefinition,
    FieldValue,
    FloatingRateIndexConstituent,
    FloatingRateIndexConstituentDefinition,
    ForwardRateAgreementConstituent,
    ForwardRateAgreementConstituentDefinition,
    FuturesQuotationMode,
    FxForwardCurveCalculationParameters,
    FxForwardCurveCalculationPreferences,
    FxForwardCurveInterpolationMode,
    FxOutrightCurve,
    FxOutrightCurvePoint,
    InnerError,
    InterestRateCurveCalculationParameters,
    InterestRateCurveInfo,
    InterestRateCurveInterpolationMode,
    InterestRateSwapConstituent,
    InterestRateSwapConstituentDefinition,
    IrConstituent,
    IrCurveDataOnResourceResponseData,
    IrCurveDataResponseData,
    IrCurveDataResponseWithError,
    IrCurveDefinition,
    IrCurveDefinitionInstrument,
    IrZcCurve,
    IrZcCurveDescription,
    IrZcCurvePoint,
    Location,
    OvernightIndexSwapConstituent,
    OvernightIndexSwapConstituentDefinition,
    PriceSide,
    Quote,
    QuoteDefinition,
    Rate,
    RoundingDefinition,
    RoundingModeEnum,
    ServiceError,
    SortingOrderEnum,
    StirFutureConstituent,
    StirFutureConstituentDefinition,
    TenorBasisSwapConstituent,
    TenorBasisSwapConstituentDefinition,
    UnitEnum,
    ValuationTime,
    Values,
    YearBasisEnum,
)

from ._interest_rate_curve import InterestRateCurve
from ._logger import logger

__all__ = [
    "Amount",
    "BusinessDayAdjustmentDefinition",
    "CityNameEnum",
    "CompoundingType",
    "ConvexityAdjustment",
    "Curve",
    "CurveCalculationParameters",
    "CurvePointRelatedInstruments",
    "DepositConstituentDefinition",
    "DepositIrConstituent",
    "DividendCurve",
    "DividendCurvePoint",
    "FloatingRateIndexConstituent",
    "FloatingRateIndexConstituentDefinition",
    "ForwardRateAgreementConstituent",
    "ForwardRateAgreementConstituentDefinition",
    "FuturesQuotationMode",
    "FxForwardCurveCalculationParameters",
    "FxForwardCurveCalculationPreferences",
    "FxOutrightCurve",
    "FxOutrightCurvePoint",
    "InterestRateCurve",
    "InterestRateCurveCalculationParameters",
    "InterestRateCurveInfo",
    "InterestRateCurveInterpolationMode",
    "InterestRateSwapConstituent",
    "InterestRateSwapConstituentDefinition",
    "IrConstituent",
    "IrCurveDataOnResourceResponseData",
    "IrCurveDataResponseData",
    "IrCurveDataResponseWithError",
    "IrCurveDefinition",
    "IrCurveDefinitionInstrument",
    "IrZcCurve",
    "IrZcCurveDescription",
    "IrZcCurvePoint",
    "OvernightIndexSwapConstituent",
    "OvernightIndexSwapConstituentDefinition",
    "PriceSide",
    "Rate",
    "RoundingDefinition",
    "RoundingModeEnum",
    "StirFutureConstituent",
    "StirFutureConstituentDefinition",
    "TenorBasisSwapConstituent",
    "TenorBasisSwapConstituentDefinition",
    "UnitEnum",
    "ValuationTime",
    "calculate",
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
    Load a InterestRateCurve using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The InterestRateCurve id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The InterestRateCurve name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the InterestRateCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    InterestRateCurve
        The InterestRateCurve instance.

    Examples
    --------
    >>> # execute the search of interest rate curves templates using id
    >>> loaded_template = load(resource_id=irCurve_templates[0].id)
    >>>
    >>> print(loaded_template)
    <InterestRateCurve space='LSEG' name='AUD_AONIA_Swap_ZC_Curve' 72379282‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load InterestRateCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InterestRateCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InterestRateCurve not found by identifier name={name} space={space}")
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
    Delete InterestRateCurve instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The InterestRateCurve resource ID.
        Required if name is not provided.
    name : str, optional
        The InterestRateCurve name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the InterestRateCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
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
    logger.info(f"Delete InterestRateCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InterestRateCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InterestRateCurve not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def calculate(
    *,
    definitions: List[IrCurveDefinitionInstrument],
    pricing_preferences: Optional[InterestRateCurveCalculationParameters] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> IrCurveDataResponseData:
    """
    Calculate the points of the interest rate curve by requesting a custom definition (on the fly).

    Parameters
    ----------
    definitions : List[IrCurveDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : InterestRateCurveCalculationParameters, optional
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
    IrCurveDataResponseData


    Examples
    --------
    >>> deposit_constituent_definition = DepositConstituentDefinition( tenor= "ON", template= "LSEG/EUR")
    >>> ois_constituent_definition = OvernightIndexSwapConstituentDefinition( tenor = "SW", template="LSEG/OIS_ESTR")
    >>> deposit_quote_definition = QuoteDefinition(instrument_code="EUROSTR=")
    >>> ois_quote_definition = QuoteDefinition(instrument_code="EURESTSW=")
    >>> deposit_quote = Quote(definition= deposit_quote_definition)
    >>> ois_quote = Quote(definition= ois_quote_definition)
    >>> deposit_curve_constituent = DepositIrConstituent(index= "LSEG/EUR_ESTR_ON_FTSE", quote= deposit_quote, definition = deposit_constituent_definition)
    >>> ois_curve_constituent = OvernightIndexSwapConstituent(index= "LSEG/EUR_ESTR_ON_FTSE", quote= ois_quote, definition= ois_constituent_definition)
    >>> curve_defition = IrCurveDefinition(index = "LSEG/EUR_ESTR_ON_FTSE", constituents= [deposit_curve_constituent, ois_curve_constituent])
    >>> irCurve = IrCurveDefinitionInstrument(definition= curve_defition)
    >>> print(irCurve)
    {'definition': {'index': 'LSEG/EUR_ESTR_ON_FTSE', 'constituents': [{'type': 'Deposit', 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'definition': {'instrumentCode': 'EUROSTR='}}, 'definition': {'tenor': 'ON', 'template': 'LSEG/EUR'}}, {'type': 'OvernightIndexSwap', 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'definition': {'instrumentCode': 'EURESTSW='}}, 'definition': {'tenor': 'SW', 'template': 'LSEG/OIS_ESTR'}}]}}


    >>> calculation_result = calculate( definitions= [irCurve])
    >>> print(calculation_result)
    {'definitions': [{'definition': {'index': 'LSEG/EUR_ESTR_ON_FTSE', 'constituents': [{'type': 'Deposit', 'definition': {'tenor': 'ON', 'template': 'LSEG/EUR'}, 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'definition': {'instrumentCode': 'EUROSTR='}}}, {'type': 'OvernightIndexSwap', 'definition': {'tenor': 'SW', 'template': 'LSEG/OIS_ESTR'}, 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'definition': {'instrumentCode': 'EURESTSW='}}}]}}], 'pricingPreferences': {'extrapolationMode': 'Constant', 'interpolationMode': 'CubicDiscount', 'priceSide': 'Mid', 'useDelayedDataIfDenied': True, 'ignoreInvalidInstruments': True, 'interestCalculationMethod': 'Dcb_Actual_Actual', 'compoundingType': 'Compounded', 'useConvexityAdjustment': True, 'convexityAdjustment': {'meanReversionPercent': 0.547, 'volatilityPercent': 0.731}, 'useMultiDimensionalSolver': True, 'valuationDate': '2025-08-21'}, 'analytics': [{'constituents': [{'type': 'Deposit', 'definition': {'tenor': 'ON', 'template': 'EUR'}, 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'startDate': '2025-08-21', 'endDate': '2025-08-22', 'definition': {'instrumentCode': 'EUROSTR='}, 'values': {'bid': {'value': 1.926}, 'ask': {'value': 1.926}}}, 'status': []}, {'type': 'OvernightIndexSwap', 'definition': {'tenor': 'SW', 'template': 'LBOTH PASTFLOW:YES SETTLE:2WD LPAID CUR:EUR CLDR:EMU PDELAY:1 LTYPE:FIXED FRQ:1 CCM:MMA0 ACC:A0 EMC:S DMC:F LRECEIVED CUR:EUR CLDR:EMU PDELAY:1 LTYPE:FLOAT FRQ:1 CCM:MMA0 ACC:A0 EMC:S DMC:F RESETFRQ:1WD INDEXCM:CMP IDX:OESTR'}, 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'quote': {'startDate': '2025-08-25', 'endDate': '2025-09-01', 'definition': {'instrumentCode': 'EURESTSW='}, 'values': {'bid': {'value': 1.9179}, 'ask': {'value': 1.9271}}}}], 'zcCurves': [{'curveType': 'IrZcCurve', 'index': 'LSEG/EUR_ESTR_ON_FTSE', 'points': [{'startDate': '2025-08-21', 'tenor': '0D', 'endDate': '2025-08-21', 'rate': {'value': 1.9718876116663786, 'unit': 'Percentage'}, 'discountFactor': {'value': 1.0, 'unit': 'Absolute'}}, {'startDate': '2025-08-21', 'tenor': 'ON', 'endDate': '2025-08-22', 'rate': {'value': 1.9718876116663786, 'unit': 'Percentage'}, 'discountFactor': {'value': 0.999946502862097, 'unit': 'Absolute'}, 'instruments': [{'instrumentCode': 'EUROSTR='}]}, {'startDate': '2025-08-21', 'tenor': 'SW', 'endDate': '2025-09-01', 'rate': {'value': 1.9687190691631828, 'unit': 'Percentage'}, 'discountFactor': {'value': 0.9994126247664965, 'unit': 'Absolute'}, 'instruments': [{'instrumentCode': 'EURESTSW='}]}]}], 'underlyingCurves': []}]}

    """

    try:
        logger.info("Calling calculate")

        response = Client().interest_rate_curves_service.calculate(
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


def _delete_by_id(curve_id: str) -> bool:
    """
    Delete a InterestRateCurve that exists in the platform. The InterestRateCurve can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting InterestRateCurve with id: {curve_id}")
        Client().interest_rate_curve_service.delete(curve_id=curve_id)
        logger.info(f"Deleted InterestRateCurve with id: {curve_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting InterestRateCurve with id: {curve_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(curve_id: str, fields: Optional[str] = None) -> InterestRateCurve:
    """
    Access a InterestRateCurve existing in the platform (read). The InterestRateCurve can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    InterestRateCurve


    Examples
    --------


    """

    try:
        logger.info(f"Opening InterestRateCurve with id: {curve_id}")

        response = Client().interest_rate_curve_service.read(curve_id=curve_id, fields=fields)

        output = InterestRateCurve(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening InterestRateCurve:")
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
) -> List[InterestRateCurveInfo]:
    """
    List the InterestRateCurves existing in the platform (depending on permissions)

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
    List[InterestRateCurveInfo]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------
    >>> # execute the search of irCurves templates
    >>> irCurve_templates = search()
    >>>
    >>> print(irCurve_templates)
    [{'type': 'InterestRateCurve', 'id': '72379282-f4d0-4ebe-a5fb-09196298a924', 'location': {'space': 'LSEG', 'name': 'AUD_AONIA_Swap_ZC_Curve'}, 'description': {'summary': 'AUD AONIA Swap ZC Curve', 'tags': ['qpsName:AUD AONIA Swap ZC Curve', 'currency:AUD', 'indexName:AONIA', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '01d60137-54ec-47bc-bc08-c60a8f69292c', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW__EMEA__Swap_ZC_Curve_1M'}, 'description': {'summary': 'AUD BBSW (EMEA) Swap ZC Curve for 1M tenor', 'tags': ['qpsName:AUD BBSW (EMEA) Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'e7d123aa-3f49-453c-892a-3e2f6256cc4c', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW__EMEA__Swap_ZC_Curve_3M'}, 'description': {'summary': 'AUD BBSW (EMEA) Swap ZC Curve for 3M tenor', 'tags': ['qpsName:AUD BBSW (EMEA) Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'bd19b6e3-e16f-4065-80f8-49c4cbae3e1e', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW__EMEA__Swap_ZC_Curve_6M'}, 'description': {'summary': 'AUD BBSW (EMEA) Swap ZC Curve for 6M tenor', 'tags': ['qpsName:AUD BBSW (EMEA) Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '87a356a3-793f-4cc1-b5b9-15135e87e6f4', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW_Swap_ZC_Curve_1M'}, 'description': {'summary': 'AUD BBSW Swap ZC Curve for 1M tenor', 'tags': ['qpsName:AUD BBSW Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'd0adb5f4-ca2b-4fa8-b572-af5c7e10358c', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW_Swap_ZC_Curve_3M'}, 'description': {'summary': 'AUD BBSW Swap ZC Curve for 3M tenor', 'tags': ['qpsName:AUD BBSW Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'd9328c4b-58af-49f1-b7f0-9ee3077c2fcd', 'location': {'space': 'LSEG', 'name': 'AUD_BBSW_Swap_ZC_Curve_6M'}, 'description': {'summary': 'AUD BBSW Swap ZC Curve for 6M tenor', 'tags': ['qpsName:AUD BBSW Swap ZC Curve', 'currency:AUD', 'indexName:BBSW', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'd4f30718-5775-49aa-803d-0902e3043aae', 'location': {'space': 'LSEG', 'name': 'AUD_Bills__IRS_vs_3M6M'}, 'description': {'summary': 'AUD Bills, IRS vs 3M/6M', 'tags': ['qpsName:AUD Bills, IRS vs 3M/6M', 'currency:AUD', 'indexName:BBSW', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '0d2ca431-c889-4d00-96cb-59b3e4fba800', 'location': {'space': 'LSEG', 'name': 'CAD___Depo__IRS_vs_3M'}, 'description': {'summary': 'CAD - Depo, IRS vs 3M', 'tags': ['qpsName:CAD - Depo, IRS vs 3M', 'currency:CAD', 'indexName:BA', 'indexTenor:3M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '6824a2b8-ca0e-4c50-b127-4c07c4290c4e', 'location': {'space': 'LSEG', 'name': 'CAD_BA_Swap_ZC_Curve_1M'}, 'description': {'summary': 'CAD BA Swap ZC Curve for 1M tenor', 'tags': ['qpsName:CAD BA Swap ZC Curve', 'currency:CAD', 'indexName:BA', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '10fdd39f-129f-49da-8cb4-58284996d5d8', 'location': {'space': 'LSEG', 'name': 'CAD_BA_Swap_ZC_Curve_3M'}, 'description': {'summary': 'CAD BA Swap ZC Curve for 3M tenor', 'tags': ['qpsName:CAD BA Swap ZC Curve', 'currency:CAD', 'indexName:BA', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'adee5697-41e4-4dfd-9242-5b8f70a2d61d', 'location': {'space': 'LSEG', 'name': 'CAD_CORRA_Swap_ZC_Curve'}, 'description': {'summary': 'CAD CORRA Swap ZC Curve', 'tags': ['qpsName:CAD CORRA Swap ZC Curve', 'currency:CAD', 'indexName:CORRA', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '66c5f2b6-1840-4409-8c52-fbb7b1bcf14d', 'location': {'space': 'LSEG', 'name': 'CAD_CRA_Future_ZC_Curve'}, 'description': {'summary': 'CAD CRA Future ZC Curve', 'tags': ['qpsName:CAD CRA Future ZC Curve', 'currency:CAD', 'indexName:CORRA', 'indexTenor:ON', 'mainConstituentAssetClass:Futures']}}, {'type': 'InterestRateCurve', 'id': 'd2ea3f91-7b74-46e9-800a-d1d8ce264b00', 'location': {'space': 'LSEG', 'name': 'CHF___Depo__IRS_vs_6M'}, 'description': {'summary': 'CHF - Depo, IRS vs 6M', 'tags': ['qpsName:CHF - Depo, IRS vs 6M', 'currency:CHF', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '4241c5ef-cd47-4e3d-974a-7c602027a804', 'location': {'space': 'LSEG', 'name': 'CHF_LIBOR_Swap_ZC_Curve_1M'}, 'description': {'summary': 'CHF LIBOR Swap ZC Curve for 1M tenor', 'tags': ['qpsName:CHF LIBOR Swap ZC Curve', 'currency:CHF', 'indexName:LIBOR', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'd0940c55-6c81-4b84-b308-03972b52e66a', 'location': {'space': 'LSEG', 'name': 'CHF_LIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'CHF LIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:CHF LIBOR Swap ZC Curve', 'currency:CHF', 'indexName:LIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '3a47925c-582d-483b-b1b8-28bdad4c79a0', 'location': {'space': 'LSEG', 'name': 'CHF_LIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'CHF LIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:CHF LIBOR Swap ZC Curve', 'currency:CHF', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'a4b3f66c-0b19-4293-b536-6346ab279b11', 'location': {'space': 'LSEG', 'name': 'CHF_SARON_Swap_ZC_Curve'}, 'description': {'summary': 'CHF SARON Swap ZC Curve', 'tags': ['qpsName:CHF SARON Swap ZC Curve', 'currency:CHF', 'indexName:SARON', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'fe1c3c53-c583-4ff2-adcd-35c1e56e9c8e', 'location': {'space': 'LSEG', 'name': 'EUR___Depo__IRS_vs_6M'}, 'description': {'summary': 'EUR - Depo, IRS vs 6M', 'tags': ['qpsName:EUR - Depo, IRS vs 6M', 'currency:EUR', 'indexName:EURIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': 'c7a3eff1-abe8-4061-9f5e-83a76c09ee09', 'location': {'space': 'LSEG', 'name': 'EUR_ESTR_Swap_ZC_Curve'}, 'description': {'summary': 'EUR ESTR Swap ZC Curve', 'tags': ['qpsName:EUR ESTR Swap ZC Curve', 'currency:EUR', 'indexName:ESTR', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'fa71cf17-f9b8-49b4-a5df-b85d6efbae69', 'location': {'space': 'LSEG', 'name': 'EUR_EURIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'EUR EURIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:EUR EURIBOR Swap ZC Curve', 'currency:EUR', 'indexName:EURIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'c0614731-6785-46f1-bdcb-b11c4db23015', 'location': {'space': 'LSEG', 'name': 'EUR_EURIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'EUR EURIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:EUR EURIBOR Swap ZC Curve', 'currency:EUR', 'indexName:EURIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '3a36b566-a635-4bd9-9a2a-c6516d530dea', 'location': {'space': 'LSEG', 'name': 'EUR_FEI_Future_ZC_Curve'}, 'description': {'summary': 'EUR FEI Future ZC Curve', 'tags': ['qpsName:EUR FEI Future ZC Curve', 'currency:EUR', 'indexName:EURIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Futures']}}, {'type': 'InterestRateCurve', 'id': '4d3a08f3-724c-471e-b5b0-f37882c65bf4', 'location': {'space': 'LSEG', 'name': 'EUR_FEU3_Future_ZC_Curve'}, 'description': {'summary': 'EUR FEU3 Future ZC Curve', 'tags': ['qpsName:EUR FEU3 Future ZC Curve', 'currency:EUR', 'indexName:EURIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Futures']}}, {'type': 'InterestRateCurve', 'id': 'c569b8bf-900d-4edd-9e0d-5f28e839efae', 'location': {'space': 'LSEG', 'name': 'GBP___Depo__IRS_vs_6M'}, 'description': {'summary': 'GBP - Depo, IRS vs 6M', 'tags': ['qpsName:GBP - Depo, IRS vs 6M', 'currency:GBP', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': 'e2d24f38-a4b1-41ef-b6ee-45db77eb28cd', 'location': {'space': 'LSEG', 'name': 'GBP_LIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'GBP LIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:GBP LIBOR Swap ZC Curve', 'currency:GBP', 'indexName:LIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '68a822c8-1e69-4914-bb07-bab177dd13c5', 'location': {'space': 'LSEG', 'name': 'GBP_LIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'GBP LIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:GBP LIBOR Swap ZC Curve', 'currency:GBP', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'cbcf4062-9eb9-45d2-bb82-428bced3b063', 'location': {'space': 'LSEG', 'name': 'GBP_LIBOR_Swap_ZC_Curve_ON'}, 'description': {'summary': 'GBP LIBOR Swap ZC Curve for ON tenor', 'tags': ['qpsName:GBP LIBOR Swap ZC Curve', 'currency:GBP', 'indexName:LIBOR', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'fc4ae917-3e75-4176-a496-52f861d9b699', 'location': {'space': 'LSEG', 'name': 'GBP_MPZ_Future_ZC_Curve'}, 'description': {'summary': 'GBP MPZ Future ZC Curve', 'tags': ['qpsName:GBP MPZ Future ZC Curve', 'currency:GBP', 'indexName:SONIA', 'indexTenor:ON', 'mainConstituentAssetClass:Futures']}}, {'type': 'InterestRateCurve', 'id': 'f1669b21-114d-4f8d-9078-122e1b3915a1', 'location': {'space': 'LSEG', 'name': 'GBP_SNO_Future_ZC_Curve'}, 'description': {'summary': 'GBP SNO Future ZC Curve', 'tags': ['qpsName:GBP SNO Future ZC Curve', 'currency:GBP', 'indexName:SONIA', 'indexTenor:ON', 'mainConstituentAssetClass:Futures']}}, {'type': 'InterestRateCurve', 'id': '39a9c3bc-25da-4600-9a60-74a59fe2a174', 'location': {'space': 'LSEG', 'name': 'GBP_SONIA_Swap_ZC_Curve'}, 'description': {'summary': 'GBP SONIA Swap ZC Curve', 'tags': ['qpsName:GBP SONIA Swap ZC Curve', 'currency:GBP', 'indexName:SONIA', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '86c8c9ed-f54b-4927-8c97-3a18cd010efa', 'location': {'space': 'LSEG', 'name': 'JPY___Depo__IRS_vs_6M'}, 'description': {'summary': 'JPY - Depo, IRS vs 6M', 'tags': ['qpsName:JPY - Depo, IRS vs 6M', 'currency:JPY', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '3f02b0a4-307e-40b7-bb4f-038f56e1c570', 'location': {'space': 'LSEG', 'name': 'JPY_LIBOR_Swap_ZC_Curve_1M'}, 'description': {'summary': 'JPY LIBOR Swap ZC Curve for 1M tenor', 'tags': ['qpsName:JPY LIBOR Swap ZC Curve', 'currency:JPY', 'indexName:LIBOR', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '28e5697a-fe66-4c93-a18b-2db9419792db', 'location': {'space': 'LSEG', 'name': 'JPY_LIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'JPY LIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:JPY LIBOR Swap ZC Curve', 'currency:JPY', 'indexName:LIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '826121e8-35ef-43ba-8edc-df42ea79983c', 'location': {'space': 'LSEG', 'name': 'JPY_LIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'JPY LIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:JPY LIBOR Swap ZC Curve', 'currency:JPY', 'indexName:LIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '412e074c-15d4-43a0-81b5-5d47ade047f6', 'location': {'space': 'LSEG', 'name': 'JPY_TIBOR_Swap_ZC_Curve_1M'}, 'description': {'summary': 'JPY TIBOR Swap ZC Curve for 1M tenor', 'tags': ['qpsName:JPY TIBOR Swap ZC Curve', 'currency:JPY', 'indexName:TIBOR', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '412034e0-e87a-42da-98b0-ec3da63ed0bb', 'location': {'space': 'LSEG', 'name': 'JPY_TIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'JPY TIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:JPY TIBOR Swap ZC Curve', 'currency:JPY', 'indexName:TIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '025137a3-5183-470e-999f-1e2e75653588', 'location': {'space': 'LSEG', 'name': 'JPY_TIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'JPY TIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:JPY TIBOR Swap ZC Curve', 'currency:JPY', 'indexName:TIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '8367a1cd-160b-4944-8bcb-8d4177244e1b', 'location': {'space': 'LSEG', 'name': 'JPY_TONAR_Swap_ZC_Curve'}, 'description': {'summary': 'JPY TONAR Swap ZC Curve', 'tags': ['qpsName:JPY TONAR Swap ZC Curve', 'currency:JPY', 'indexName:TONAR', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '2d959b3f-b52c-4fcb-84ae-040f9fb499cf', 'location': {'space': 'LSEG', 'name': 'NOK___Depo__IRS_vs_6M'}, 'description': {'summary': 'NOK - Depo, IRS vs 6M', 'tags': ['qpsName:NOK - Depo, IRS vs 6M', 'currency:NOK', 'indexName:OIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '12255ecc-ab9f-4926-9620-8430dbe299a7', 'location': {'space': 'LSEG', 'name': 'NOK_NOWA_Swap_ZC_Curve'}, 'description': {'summary': 'NOK NOWA Swap ZC Curve', 'tags': ['qpsName:NOK NOWA Swap ZC Curve', 'currency:NOK', 'indexName:NOWA', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '4268fbd8-f6b0-46e6-a038-9983f40c4a09', 'location': {'space': 'LSEG', 'name': 'NOK_OIBOR_Swap_ZC_Curve'}, 'description': {'summary': 'NOK OIBOR Swap ZC Curve', 'tags': ['qpsName:NOK OIBOR Swap ZC Curve', 'currency:NOK', 'indexName:OIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'f49f0ba6-9610-4170-8b54-4034114d969e', 'location': {'space': 'LSEG', 'name': 'NZD_BKBM_Swap_ZC_Curve_1M'}, 'description': {'summary': 'NZD BKBM Swap ZC Curve for 1M tenor', 'tags': ['qpsName:NZD BKBM Swap ZC Curve', 'currency:NZD', 'indexName:BKBM', 'indexTenor:1M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '2cb48a67-792e-432a-86cd-7bb73bd07453', 'location': {'space': 'LSEG', 'name': 'NZD_BKBM_Swap_ZC_Curve_3M'}, 'description': {'summary': 'NZD BKBM Swap ZC Curve for 3M tenor', 'tags': ['qpsName:NZD BKBM Swap ZC Curve', 'currency:NZD', 'indexName:BKBM', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '81f80b59-5bc9-4142-aeb6-99be3ecb80f6', 'location': {'space': 'LSEG', 'name': 'NZD_BKBM_Swap_ZC_Curve_6M'}, 'description': {'summary': 'NZD BKBM Swap ZC Curve for 6M tenor', 'tags': ['qpsName:NZD BKBM Swap ZC Curve', 'currency:NZD', 'indexName:BKBM', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '2794749e-8a89-49ba-a22c-3cce61395bdb', 'location': {'space': 'LSEG', 'name': 'SEK___Depo__IRS_vs_3M'}, 'description': {'summary': 'SEK - Depo, IRS vs 3M', 'tags': ['qpsName:SEK - Depo, IRS vs 3M', 'currency:SEK', 'indexName:STIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Deposit']}}, {'type': 'InterestRateCurve', 'id': '5dd188da-c41a-471a-abfb-d698d15d4ce1', 'location': {'space': 'LSEG', 'name': 'SEK_STIBOR_Swap_ZC_Curve_3M'}, 'description': {'summary': 'SEK STIBOR Swap ZC Curve for 3M tenor', 'tags': ['qpsName:SEK STIBOR Swap ZC Curve', 'currency:SEK', 'indexName:STIBOR', 'indexTenor:3M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': 'af5f17ec-0e68-45a8-b483-088ffbd8ea77', 'location': {'space': 'LSEG', 'name': 'SEK_STIBOR_Swap_ZC_Curve_6M'}, 'description': {'summary': 'SEK STIBOR Swap ZC Curve for 6M tenor', 'tags': ['qpsName:SEK STIBOR Swap ZC Curve', 'currency:SEK', 'indexName:STIBOR', 'indexTenor:6M', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '6a698ed3-0bf3-4b95-87f2-6f1bdacd2528', 'location': {'space': 'LSEG', 'name': 'SEK_SWESTR_Swap_ZC_Curve'}, 'description': {'summary': 'SEK SWESTR Swap ZC Curve', 'tags': ['qpsName:SEK SWESTR Swap ZC Curve', 'currency:SEK', 'indexName:SWESTR', 'indexTenor:ON', 'mainConstituentAssetClass:Swap']}}, {'type': 'InterestRateCurve', 'id': '60ad0dad-2e5a-4163-bca4-85d0765da981', 'location': {'space': 'LSEG', 'name': 'Test___USD_S1R_Future_ZC_Curve'}, 'description': {'summary': 'Test - USD S1R Future ZC Curve', 'tags': ['qpsName:Test - USD S1R Future ZC Curve', 'currency:USD', 'indexName:SOFR', 'indexTenor:ON', 'mainConstituentAssetClass:Futures']}}]

    """

    try:
        logger.info("Calling search")

        response = Client().interest_rate_curves_service.list(
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
