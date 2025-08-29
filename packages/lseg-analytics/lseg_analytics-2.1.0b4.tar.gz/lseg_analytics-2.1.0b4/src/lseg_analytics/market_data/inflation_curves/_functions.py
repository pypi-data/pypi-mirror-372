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
    BidAskFieldsDescription,
    BidAskFieldsFormulaDescription,
    BidAskFieldsFormulaOutput,
    BidAskFormulaFields,
    CategoryEnum,
    CodeEnum,
    ConstituentOverrideModeEnum,
    ConsumerPriceIndex,
    ConsumerPriceIndexCurvePoint,
    CurveInfo,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesUnitEnum,
    CurvesAndSurfacesValuationTime,
    ErrorDetails,
    ErrorResponse,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FormulaParameterDescription,
    InflationConstituents,
    InflationConstituentsDescription,
    InflationConstituentsOutput,
    InflationCurveCreateRequest,
    InflationCurveDefinition,
    InflationCurveDefinitionDescriptionRequest,
    InflationCurveDefinitionDescriptionResponse,
    InflationCurveDefinitionItem,
    InflationCurveDefinitionResponse,
    InflationCurveDefinitionResponseItem,
    InflationCurveDefinitionsResponse,
    InflationCurveGetDefinitionItem,
    InflationCurveParameters,
    InflationCurveParametersDescription,
    InflationCurveResponse,
    InflationCurves,
    InflationCurvesRequestItem,
    InflationCurvesResponse,
    InflationCurvesResponseItem,
    InflationIndex,
    InflationIndexDescription,
    InflationInstruments,
    InflationInstrumentsOutput,
    InflationInstrumentsSegment,
    InflationRateCurvePoint,
    InflationSeasonality,
    InflationSeasonalityCurvePoint,
    InflationSeasonalityItem,
    InflationSwapInstrument,
    InflationSwapInstrumentDefinitionOutput,
    InflationSwapInstrumentOutput,
    InflationSwapsInstrumentDescription,
    InstrumentDefinition,
    InstrumentTypeEnum,
    InterpolationModeEnum,
    MarketDataLookBack,
    MarketDataTime,
    MonthEnum,
    OverrideBidAsk,
    OverrideBidAskFields,
    PeriodicityEnum,
    ProcessingInformation,
    RiskTypeEnum,
)

from ._logger import logger

__all__ = [
    "BidAskFieldsDescription",
    "BidAskFieldsFormulaDescription",
    "BidAskFieldsFormulaOutput",
    "BidAskFormulaFields",
    "CategoryEnum",
    "CodeEnum",
    "ConstituentOverrideModeEnum",
    "ConsumerPriceIndex",
    "ConsumerPriceIndexCurvePoint",
    "CurveInfo",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesUnitEnum",
    "CurvesAndSurfacesValuationTime",
    "ErrorDetails",
    "ErrorResponse",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FormulaParameterDescription",
    "InflationConstituents",
    "InflationConstituentsDescription",
    "InflationConstituentsOutput",
    "InflationCurveDefinition",
    "InflationCurveDefinitionDescriptionRequest",
    "InflationCurveDefinitionDescriptionResponse",
    "InflationCurveDefinitionItem",
    "InflationCurveDefinitionResponse",
    "InflationCurveDefinitionResponseItem",
    "InflationCurveDefinitionsResponse",
    "InflationCurveGetDefinitionItem",
    "InflationCurveParameters",
    "InflationCurveParametersDescription",
    "InflationCurveResponse",
    "InflationCurves",
    "InflationCurvesRequestItem",
    "InflationCurvesResponse",
    "InflationCurvesResponseItem",
    "InflationIndex",
    "InflationIndexDescription",
    "InflationInstruments",
    "InflationInstrumentsOutput",
    "InflationInstrumentsSegment",
    "InflationRateCurvePoint",
    "InflationSeasonality",
    "InflationSeasonalityCurvePoint",
    "InflationSeasonalityItem",
    "InflationSwapInstrument",
    "InflationSwapInstrumentDefinitionOutput",
    "InflationSwapInstrumentOutput",
    "InflationSwapsInstrumentDescription",
    "InstrumentDefinition",
    "InstrumentTypeEnum",
    "InterpolationModeEnum",
    "MarketDataLookBack",
    "MarketDataTime",
    "MonthEnum",
    "OverrideBidAsk",
    "OverrideBidAskFields",
    "PeriodicityEnum",
    "ProcessingInformation",
    "RiskTypeEnum",
    "calculate",
    "calculate_by_id",
    "create",
    "delete",
    "overwrite",
    "read",
    "search",
]


def calculate(
    *,
    universe: Optional[List[InflationCurvesRequestItem]] = None,
    fields: Optional[str] = None,
) -> InflationCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[InflationCurvesRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    InflationCurvesResponse
        InflationCurvesResponse

    Examples
    --------
    >>> print("Step 1: Creating Curve Definition...")
    >>> # Select an Inflation Index
    >>> inflation_index = 'AGBRPI'
    >>>
    >>> # Create curve definition object
    >>> curve_definition = infc.InflationCurveDefinitionItem(
    >>>         inflation_index = infc.InflationIndex(code=inflation_index)
    >>>         )
    >>> print(f"   ✓ Instrument: {curve_definition.inflation_index}")
    >>>
    >>> print("Step 2: Configuring Curve Parameters...")
    >>> # Create curve parameters object - optional
    >>> curve_parameters = infc.InflationCurveParameters(
    >>>         valuation_date_time = dt.datetime.strptime("2025-01-18", "%Y-%m-%d")
    >>>     )
    >>> print(f"   ✓ Curve Parameters: {curve_parameters}")
    >>>
    >>>
    >>> print("Step 3: Create request item...")
    >>> # Create the main request object with basic configuration
    >>> request_item = infc.InflationCurvesRequestItem(
    >>>         curve_tag = f"{inflation_index}_InflationCurve",
    >>>         curve_definition = curve_definition,
    >>>         curve_parameters = curve_parameters,
    >>>     )
    >>> print(f"   ✓ Request Item: {json.dumps(request_item.as_dict(), indent=4)}")
    Step 1: Creating Curve Definition...
       ✓ Instrument: {'code': 'AGBRPI'}
    Step 2: Configuring Curve Parameters...
       ✓ Curve Parameters: {'valuationDateTime': '2025-01-18T00:00:00Z'}
    Step 3: Create request item...
       ✓ Request Item: {
        "curveTag": "AGBRPI_InflationCurve",
        "curveDefinition": {
            "inflationIndex": {
                "code": "AGBRPI"
            }
        },
        "curveParameters": {
            "valuationDateTime": "2025-01-18T00:00:00Z"
        }
    }


    >>> # Execute the calculation using the calculate function
    >>> # The 'universe' parameter accepts a list of request items for batch processing
    >>> response = infc.calculate(universe=[request_item])
    >>> curve_data = response['data'][0]

    """

    try:
        logger.info("Calling calculate")

        response = Client().inflation_curves.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)


def calculate_by_id(
    *,
    curve_id: str,
    valuation_date: Optional[Union[str, datetime.date]] = None,
    fields: Optional[str] = None,
) -> InflationCurvesResponseItem:
    """
    Generates the curve for the given curve id

    Parameters
    ----------
    valuation_date : Union[str, datetime.date], optional
        The date on which the curve is constructed. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01').
        The valuation date should not be in the future.
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
    InflationCurvesResponseItem


    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().inflation_curves.calculate_by_id(
            curve_id=curve_id, fields=fields, valuation_date=valuation_date
        )

        output = response
        logger.info("Called calculate_by_id")

        return output
    except Exception as err:
        logger.error("Error calculate_by_id.")
        check_exception_and_raise(err, logger)


def create(
    *,
    curve_definition: Optional[InflationCurveDefinitionDescriptionRequest] = None,
    overrides: Optional[List[OverrideBidAsk]] = None,
    segments: Optional[List[InflationInstrumentsSegment]] = None,
) -> InflationCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : InflationCurveDefinitionDescriptionRequest, optional
        InflationCurveDefinitionDescriptionRequest
    overrides : List[OverrideBidAsk], optional
        Get overrides
    segments : List[InflationInstrumentsSegment], optional
        Get segments

    Returns
    --------
    InflationCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling create")

        response = Client().inflation_curves.create(
            body=InflationCurveCreateRequest(
                curve_definition=curve_definition,
                overrides=overrides,
                segments=segments,
            )
        )

        output = response
        logger.info("Called create")

        return output
    except Exception as err:
        logger.error("Error create.")
        check_exception_and_raise(err, logger)


def delete(*, curve_id: str) -> bool:
    """
    Delete a InflationCurveDefinition that exists in the platform. The InflationCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_id : str
        The curve identifier.

    Returns
    --------
    bool
        A ResultAsync object specifying a status message or error response

    Examples
    --------


    """

    try:
        logger.info(f"Deleting InflationCurvesResource with id: {curve_id}")
        Client().inflation_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted InflationCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[InflationCurveDefinitionDescriptionRequest] = None,
    overrides: Optional[List[OverrideBidAsk]] = None,
    segments: Optional[List[InflationInstrumentsSegment]] = None,
) -> InflationCurveResponse:
    """
    Overwrite a InflationCurveDefinition that exists in the platform. The InflationCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : InflationCurveDefinitionDescriptionRequest, optional
        InflationCurveDefinitionDescriptionRequest
    overrides : List[OverrideBidAsk], optional
        Get overrides
    segments : List[InflationInstrumentsSegment], optional
        Get segments
    curve_id : str
        The curve identifier.

    Returns
    --------
    InflationCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling overwrite")

        response = Client().inflation_curves.overwrite(
            body=InflationCurveCreateRequest(
                curve_definition=curve_definition,
                overrides=overrides,
                segments=segments,
            ),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> InflationCurveResponse:
    """
    Access a InflationCurveDefinition existing in the platform (read). The InflationCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    InflationCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling read")

        response = Client().inflation_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[InflationCurveGetDefinitionItem]] = None,
    fields: Optional[str] = None,
) -> InflationCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[InflationCurveGetDefinitionItem], optional
        The list of the curve items which can be requested
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    InflationCurveDefinitionsResponse
        InflationCurveDefinitionsResponse

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().inflation_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
