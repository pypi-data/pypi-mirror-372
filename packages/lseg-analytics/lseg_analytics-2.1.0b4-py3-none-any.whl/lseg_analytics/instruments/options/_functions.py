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
    Amount,
    AsianDefinition,
    AsianOtcOptionOverride,
    AsianTypeEnum,
    AverageTypeEnum,
    BachelierParameters,
    BarrierDefinition,
    BarrierModeEnum,
    BasePricingParameters,
    BinaryDefinition,
    BinaryTypeEnum,
    BlackScholesEquityParameters,
    BlackScholesFxParameters,
    BlackScholesInterestRateFuture,
    BusinessDayAdjustmentDefinition,
    CallPutEnum,
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
    DoubleBarrierOtcOptionOverride,
    DoubleBinaryOtcOptionOverride,
    EndOfMonthConvention,
    EqOptionVolSurfaceChoice,
    EqVolSurfaceInput,
    ExerciseDefinition,
    ExerciseStyleEnum,
    FrequencyEnum,
    FutureDate,
    FutureDateCalculationMethodEnum,
    FxCurveInput,
    FxForwardCurveChoice,
    FxOptionVolSurfaceChoice,
    FxPricingParameters,
    FxRateTypeEnum,
    FxVolSurfaceInput,
    Greeks,
    HestonEquityParameters,
    InnerError,
    InOrOutEnum,
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
    OptionDefinition,
    OptionDefinitionInstrument,
    OptionDescriptionFields,
    OptionInfo,
    OptionPricingParameters,
    OptionRiskFields,
    OptionSolveResponseFieldsOnResourceResponseData,
    OptionSolveResponseFieldsResponseData,
    OptionSolveResponseFieldsResponseWithError,
    OptionSolvingParameters,
    OptionSolvingTarget,
    OptionSolvingVariable,
    OptionSolvingVariableEnum,
    OptionValuationFields,
    OptionValuationResponseFieldsOnResourceResponseData,
    OptionValuationResponseFieldsResponseData,
    OptionValuationResponseFieldsResponseWithError,
    PaymentTypeEnum,
    PriceSideWithLastEnum,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    ScheduleDefinition,
    ServiceError,
    SettlementDefinition,
    SettlementType,
    SingleBarrierOtcOptionOverride,
    SingleBinaryOtcOptionOverride,
    SolvingLegEnum,
    SolvingMethod,
    SolvingMethodEnum,
    SolvingResult,
    SortingOrderEnum,
    Spot,
    StrikeTypeEnum,
    StubRuleEnum,
    SwapSolvingVariableEnum,
    TimeStampEnum,
    UnderlyingBond,
    UnderlyingBondFuture,
    UnderlyingCommodity,
    UnderlyingDefinition,
    UnderlyingEquity,
    UnderlyingFx,
    UnderlyingIrs,
    UnitEnum,
    VanillaOtcOptionOverride,
    VolatilityTypeEnum,
    VolCubePoint,
    VolModelTypeEnum,
    VolSurfacePoint,
    ZcTypeEnum,
)

from ._logger import logger
from ._option import Option

__all__ = [
    "Amount",
    "AsianDefinition",
    "AsianOtcOptionOverride",
    "AsianTypeEnum",
    "AverageTypeEnum",
    "BachelierParameters",
    "BarrierDefinition",
    "BarrierModeEnum",
    "BasePricingParameters",
    "BinaryDefinition",
    "BinaryTypeEnum",
    "BlackScholesEquityParameters",
    "BlackScholesFxParameters",
    "BlackScholesInterestRateFuture",
    "BusinessDayAdjustmentDefinition",
    "CallPutEnum",
    "CmdtyOptionVolSurfaceChoice",
    "CmdtyVolSurfaceInput",
    "ConvexityAdjustment",
    "CreditCurveChoice",
    "CreditCurveInput",
    "CurveDataPoint",
    "Dividend",
    "DividendTypeEnum",
    "DoubleBarrierOtcOptionOverride",
    "DoubleBinaryOtcOptionOverride",
    "EqOptionVolSurfaceChoice",
    "EqVolSurfaceInput",
    "ExerciseDefinition",
    "ExerciseStyleEnum",
    "FutureDate",
    "FutureDateCalculationMethodEnum",
    "FxCurveInput",
    "FxForwardCurveChoice",
    "FxOptionVolSurfaceChoice",
    "FxPricingParameters",
    "FxRateTypeEnum",
    "FxVolSurfaceInput",
    "Greeks",
    "HestonEquityParameters",
    "InOrOutEnum",
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
    "Option",
    "OptionDefinition",
    "OptionDefinitionInstrument",
    "OptionDescriptionFields",
    "OptionInfo",
    "OptionPricingParameters",
    "OptionRiskFields",
    "OptionSolveResponseFieldsOnResourceResponseData",
    "OptionSolveResponseFieldsResponseData",
    "OptionSolveResponseFieldsResponseWithError",
    "OptionSolvingParameters",
    "OptionSolvingTarget",
    "OptionSolvingVariable",
    "OptionSolvingVariableEnum",
    "OptionValuationFields",
    "OptionValuationResponseFieldsOnResourceResponseData",
    "OptionValuationResponseFieldsResponseData",
    "OptionValuationResponseFieldsResponseWithError",
    "PaymentTypeEnum",
    "PriceSideWithLastEnum",
    "Rate",
    "ScheduleDefinition",
    "SettlementDefinition",
    "SingleBarrierOtcOptionOverride",
    "SingleBinaryOtcOptionOverride",
    "SolvingLegEnum",
    "SolvingMethod",
    "SolvingMethodEnum",
    "SolvingResult",
    "Spot",
    "StrikeTypeEnum",
    "SwapSolvingVariableEnum",
    "TimeStampEnum",
    "UnderlyingBond",
    "UnderlyingBondFuture",
    "UnderlyingCommodity",
    "UnderlyingDefinition",
    "UnderlyingEquity",
    "UnderlyingFx",
    "UnderlyingIrs",
    "UnitEnum",
    "VanillaOtcOptionOverride",
    "VolCubePoint",
    "VolModelTypeEnum",
    "VolSurfacePoint",
    "VolatilityTypeEnum",
    "ZcTypeEnum",
    "create_asian_otc_option_from_template",
    "create_double_barrier_otc_option_from_template",
    "create_double_binary_otc_option_from_template",
    "create_single_barrier_otc_option_from_template",
    "create_single_binary_otc_option_from_template",
    "create_vanilla_otc_option_from_template",
    "delete",
    "load",
    "search",
    "solve",
    "value",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a Option using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The Option id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The Option name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the Option is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    Option
        The Option instance.

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load Option {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Option {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Option not found by identifier name={name} space={space}")
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
    Delete Option instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The Option resource ID.
        Required if name is not provided.
    name : str, optional
        The Option name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the Option is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete Option {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Option {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Option not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def create_asian_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[AsianOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create an asian OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the Asian OTC option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : AsianOtcOptionOverride, optional
        An object that contains the properties of an Asian OTC option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_asian_otc_option_from_template")

        response = Client().options_resource.create_asian_otc_option_from_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_asian_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_asian_otc_option_from_template")
        check_exception_and_raise(err, logger)


def create_double_barrier_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[DoubleBarrierOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create a double barrier OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the double barrier OTC option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : DoubleBarrierOtcOptionOverride, optional
        An object that contains the properties of a double barrier OTC option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_double_barrier_otc_option_from_template")

        response = Client().options_resource.create_double_barrier_otc_option_from_template(
            fields=fields,
            template_reference=template_reference,
            overrides=overrides,
        )

        output = response.data
        logger.info("Called create_double_barrier_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_double_barrier_otc_option_from_template")
        check_exception_and_raise(err, logger)


def create_double_binary_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[DoubleBinaryOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create a double binary OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the double binary OTC option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : DoubleBinaryOtcOptionOverride, optional
        An object that contains the properties of a double binary OTC option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_double_binary_otc_option_from_template")

        response = Client().options_resource.create_double_binary_otc_option_from_template(
            fields=fields,
            template_reference=template_reference,
            overrides=overrides,
        )

        output = response.data
        logger.info("Called create_double_binary_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_double_binary_otc_option_from_template")
        check_exception_and_raise(err, logger)


def create_single_barrier_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[SingleBarrierOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create a single barrier OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the single barrier OTC option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : SingleBarrierOtcOptionOverride, optional
        An object that contains the properties of a single barrier OTC option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_single_barrier_otc_option_from_template")

        response = Client().options_resource.create_single_barrier_otc_option_from_template(
            fields=fields,
            template_reference=template_reference,
            overrides=overrides,
        )

        output = response.data
        logger.info("Called create_single_barrier_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_single_barrier_otc_option_from_template")
        check_exception_and_raise(err, logger)


def create_single_binary_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[SingleBinaryOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create a single binary OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the single binary OTC option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : SingleBinaryOtcOptionOverride, optional
        An object that contains the properties of a single binary OTC option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_single_binary_otc_option_from_template")

        response = Client().options_resource.create_single_binary_otc_option_from_template(
            fields=fields,
            template_reference=template_reference,
            overrides=overrides,
        )

        output = response.data
        logger.info("Called create_single_binary_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_single_binary_otc_option_from_template")
        check_exception_and_raise(err, logger)


def create_vanilla_otc_option_from_template(
    *,
    template_reference: str,
    overrides: Optional[VanillaOtcOptionOverride] = None,
    fields: Optional[str] = None,
) -> Option:
    """
    Create a vanilla OTC option from a template.

    Parameters
    ----------
    template_reference : str
        The identifier of the OTC vanilla option template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : VanillaOtcOptionOverride, optional
        An object that contains the properties of an OTC vanilla option that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    Option
        Option

    Examples
    --------


    """

    try:
        logger.info("Calling create_vanilla_otc_option_from_template")

        response = Client().options_resource.create_vanilla_otc_option_from_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_vanilla_otc_option_from_template")

        return Option(output)
    except Exception as err:
        logger.error("Error create_vanilla_otc_option_from_template")
        check_exception_and_raise(err, logger)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a Option that exists in the platform. The Option can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting Option with id: {instrument_id}")
        Client().option_resource.delete(instrument_id=instrument_id)
        logger.info(f"Deleted Option with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting Option with id: {instrument_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> Option:
    """
    Access a Option existing in the platform (read). The Option can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    Option


    Examples
    --------


    """

    try:
        logger.info(f"Opening Option with id: {instrument_id}")

        response = Client().option_resource.read(instrument_id=instrument_id, fields=fields)

        output = Option(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening Option:")
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
) -> List[OptionInfo]:
    """
    List the Options existing in the platform (depending on permissions)

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
    List[OptionInfo]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().options_resource.list(
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


def solve(
    *,
    definitions: List[OptionDefinitionInstrument],
    pricing_preferences: Optional[OptionPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> OptionSolveResponseFieldsResponseData:
    """
    Calculate the solvable properties of an Option provided in the request so that a chosen property equals a target value.

    Parameters
    ----------
    definitions : List[OptionDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : OptionPricingParameters, optional
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
    OptionSolveResponseFieldsResponseData


    Examples
    --------


    """

    try:
        logger.info("Calling solve")

        response = Client().options_resource.solve(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            market_data=market_data,
            return_market_data=return_market_data,
        )

        output = response.data
        logger.info("Called solve")

        return output
    except Exception as err:
        logger.error("Error solve.")
        check_exception_and_raise(err, logger)


def value(
    *,
    definitions: List[OptionDefinitionInstrument],
    pricing_preferences: Optional[OptionPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> OptionValuationResponseFieldsResponseData:
    """
    Calculate the market value of the Option provided in the request.

    Parameters
    ----------
    definitions : List[OptionDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : OptionPricingParameters, optional
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
    OptionValuationResponseFieldsResponseData


    Examples
    --------
    >>> definition = OptionDefinition(
    >>>     underlying = UnderlyingDefinition(
    >>>         code="AAPL.O",
    >>>         underlying_type="Equity"
    >>>     ),
    >>>     exercise = ExerciseDefinition(
    >>>         strike=150,
    >>>         exercise_style="European",
    >>>         schedule = ScheduleDefinition(
    >>>             end_date = AdjustableDate(
    >>>                 date = date(2025, 9, 13)
    >>>             )
    >>>         )
    >>>     ),
    >>>     option_type="Call"
    >>> )
    >>>
    >>> print(js.dumps(definition.as_dict(), indent=4))
    {
        "underlying": {
            "code": "AAPL.O",
            "underlyingType": "Equity"
        },
        "exercise": {
            "strike": 150,
            "exerciseStyle": "European",
            "schedule": {
                "endDate": {
                    "dateType": "AdjustableDate",
                    "date": "2025-09-13"
                }
            }
        },
        "optionType": "Call"
    }


    >>> definition_instrument = OptionDefinitionInstrument(
    >>>     definition=definition
    >>> )
    >>>
    >>> print(js.dumps(definition_instrument.as_dict(), indent=4))
    {
        "definition": {
            "underlying": {
                "code": "AAPL.O",
                "underlyingType": "Equity"
            },
            "exercise": {
                "strike": 150,
                "exerciseStyle": "European",
                "schedule": {
                    "endDate": {
                        "dateType": "AdjustableDate",
                        "date": "2025-09-13"
                    }
                }
            },
            "optionType": "Call"
        }
    }


    >>> pricing_parameters=OptionPricingParameters(
    >>>     pricing_model="BlackScholes",
    >>>     underlying_price_side="Mid",
    >>>     option_price_side="Mid",
    >>>     valuation_date=date(2024, 12, 31)
    >>> )
    >>>
    >>> print(js.dumps(pricing_parameters.as_dict(), indent=4))
    {
        "pricingModel": "BlackScholes",
        "underlyingPriceSide": "Mid",
        "optionPriceSide": "Mid",
        "valuationDate": "2024-12-31"
    }


    >>> response = value(
    >>>     definitions=[definition_instrument],
    >>>     pricing_preferences=pricing_parameters
    >>> )
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "definitions": [
            {
                "definition": {
                    "underlying": {
                        "underlyingType": "Equity",
                        "code": "AAPL.O"
                    },
                    "exercise": {
                        "strike": 150.0,
                        "schedule": {
                            "endDate": {
                                "dateType": "AdjustableDate",
                                "date": "2025-09-13"
                            }
                        },
                        "exerciseStyle": "European"
                    },
                    "optionType": "Call"
                }
            }
        ],
        "pricingPreferences": {
            "pricingModel": "BlackScholes",
            "underlyingPriceSide": "Mid",
            "optionPriceSide": "Mid",
            "valuationDate": "2024-12-31"
        },
        "analytics": [
            {
                "description": {
                    "instrumentCode": "",
                    "underlyingRic": "AAPL.O",
                    "instrumentDescription": "Cash_EURO_AAPL.O"
                },
                "valuation": {
                    "volatility": {
                        "value": 37.7696072740024,
                        "unit": "Percentage"
                    },
                    "marketValue": {
                        "value": 102.475596197359,
                        "dealCurrency": {
                            "value": 102.475596197359,
                            "currency": "USD"
                        }
                    },
                    "totalMarketValue": {
                        "value": 10247.5596197359,
                        "dealCurrency": {
                            "value": 10247.5596197359,
                            "currency": "USD"
                        }
                    },
                    "intrinsicValue": {
                        "value": 100.41,
                        "dealCurrency": {
                            "value": 100.41,
                            "currency": "USD"
                        }
                    },
                    "timeValue": {
                        "value": 2.06559619735947,
                        "dealCurrency": {
                            "value": 2.06559619735947,
                            "currency": "USD"
                        }
                    },
                    "premiumOverCash": {
                        "value": 0.00824885666450808,
                        "percent": 0.824885666450808,
                        "dealCurrency": {
                            "value": 2.06559619735947,
                            "currency": "USD"
                        }
                    },
                    "moneyness": {
                        "value": 166.94,
                        "unit": "Percentage"
                    },
                    "annualizedYield": {
                        "value": 0.0117153022667138,
                        "unit": "Absolute"
                    }
                },
                "risk": {
                    "delta": {
                        "value": 0.952586822496096,
                        "percent": 95.2586822496096,
                        "dealCurrency": {
                            "value": 95.2586822496096,
                            "currency": "USD"
                        }
                    },
                    "gamma": {
                        "value": 0.000936940308187526,
                        "percent": 0.0936940308187526,
                        "dealCurrency": {
                            "value": 0.0936940308187526,
                            "currency": "USD"
                        }
                    },
                    "rho": {
                        "value": 0.956625371777541,
                        "percent": 95.6625371777541,
                        "dealCurrency": {
                            "value": 95.6625371777541,
                            "currency": "USD"
                        }
                    },
                    "theta": {
                        "value": -0.0141399555383412,
                        "percent": -1.41399555383412,
                        "dealCurrency": {
                            "value": -1.41399555383412,
                            "currency": "USD"
                        }
                    },
                    "vega": {
                        "value": 0.156014091557627,
                        "percent": 15.601409155762699,
                        "dealCurrency": {
                            "value": 15.6014091557627,
                            "currency": "USD"
                        }
                    },
                    "hedgeRatio": -1.0497730772505,
                    "leverage": 2.32774704488515
                }
            }
        ]
    }

    """

    try:
        logger.info("Calling value")

        response = Client().options_resource.value(
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
