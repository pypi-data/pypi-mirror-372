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
    CalendarAdjustmentEnum,
    CalibrationMethodEnum,
    CommoditiesCalendarSpreadFields,
    CommoditiesCalendarSpreadFieldsDescription,
    CommoditiesCalendarSpreadFieldsFormulaDescription,
    CommoditiesCalendarSpreadFieldsOutput,
    CommoditiesCalendarSpreadFormulaFields,
    CommoditiesCalendarSpreadFormulaParameter,
    CommoditiesCalendarSpreadFormulaParameterDescription,
    CommoditiesCalendarSpreadFormulaParameterOutput,
    CommoditiesCalendarSpreadInstrument,
    CommoditiesCalendarSpreadInstrumentDefinition,
    CommoditiesCalendarSpreadInstrumentDescription,
    CommoditiesCalendarSpreadInstrumentOutput,
    CommoditiesChainSource,
    CommoditiesCurveConstituents,
    CommoditiesCurveConstituentsDescription,
    CommoditiesCurveConstituentsOutput,
    CommoditiesCurveCreateRequest,
    CommoditiesCurveDefinition,
    CommoditiesCurveDefinitionBase,
    CommoditiesCurveDefinitionDescription,
    CommoditiesCurveDefinitionOutput,
    CommoditiesCurveDefinitionRequest,
    CommoditiesCurveDefinitionRequestKeys,
    CommoditiesCurveDefinitionResponse,
    CommoditiesCurveDefinitionsResponse,
    CommoditiesCurveDefinitionsResponseItems,
    CommoditiesCurveParameters,
    CommoditiesCurveParametersDescription,
    CommoditiesCurvePoint,
    CommoditiesCurvePointsInstrument,
    CommoditiesCurveReferenceUpdateDefinition,
    CommoditiesCurveRequestItem,
    CommoditiesCurveResponse,
    CommoditiesCurveSegmentReferenceCurve,
    CommoditiesCurvesReferenceResponseItem,
    CommoditiesCurvesResponse,
    CommoditiesCurvesResponseItem,
    CommoditiesFieldsFormulaOutput,
    CommoditiesFuturesFields,
    CommoditiesFuturesFieldsDescription,
    CommoditiesFuturesFieldsFormulaDescription,
    CommoditiesFuturesFieldsOutput,
    CommoditiesFuturesFormulaFields,
    CommoditiesFuturesFormulaParameter,
    CommoditiesFuturesFormulaParameterDescription,
    CommoditiesFuturesFormulaParameterOutput,
    CommoditiesFuturesInstrument,
    CommoditiesFuturesInstrumentDefinition,
    CommoditiesFuturesInstrumentDescription,
    CommoditiesFuturesInstrumentOutput,
    CommoditiesInstrumentDefinitionDescription,
    CommoditiesInstrumentsOutput,
    CommoditiesInstrumentsRequest,
    CommoditiesInstrumentsSegment,
    CommoditiesInstrumentsSegmentCreate,
    CommoditiesInterestRateCurve,
    CommoditiesInterestRateCurveDefinition,
    CommoditiesInterProductSpreadFields,
    CommoditiesInterProductSpreadFieldsDescription,
    CommoditiesInterProductSpreadFieldsFormulaDescription,
    CommoditiesInterProductSpreadFieldsFormulaOutput,
    CommoditiesInterProductSpreadFieldsOutput,
    CommoditiesInterProductSpreadFormulaFields,
    CommoditiesInterProductSpreadFormulaParameter,
    CommoditiesInterProductSpreadFormulaParameterDescription,
    CommoditiesInterProductSpreadFormulaParameterOutput,
    CommoditiesInterProductSpreadInstrument,
    CommoditiesInterProductSpreadInstrumentDefinition,
    CommoditiesInterProductSpreadInstrumentDefinitionDescription,
    CommoditiesInterProductSpreadInstrumentDescription,
    CommoditiesInterProductSpreadInstrumentsOutput,
    CommoditiesReferenceCurve,
    CompoundingTypeEnum,
    ConstantForwardRateParameters,
    ConstituentOverrideModeEnum,
    ConstituentsFiltersDescription,
    CurveInfo,
    CurvesAndSurfacesConvexityAdjustment,
    CurvesAndSurfacesInterestCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesUnitEnum,
    CurvesAndSurfacesValuationTime,
    CurveTenorsFrequencyEnum,
    ExtrapolationModeEnum,
    FieldDateOutput,
    FieldDateValue,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FieldFormulaDoubleOutput,
    FieldFormulaDoubleValue,
    FieldTimeOutput,
    FieldTimeValue,
    InstrumentTypeEnum,
    InterestRateCurveParameters,
    InterpolationModeEnum,
    MainConstituentAssetClassEnum,
    MarketDataAccessDeniedFallbackEnum,
    MarketDataLookBack,
    MarketDataTime,
    ProductEnum,
    RiskTypeEnum,
    Seasonality,
    SeasonalityCurvePoint,
    SeasonalityDescription,
    SectorEnum,
    Step,
    StepModeEnum,
    SubSectorEnum,
    Turn,
    ZcCurve,
    ZcCurveInstrument,
    ZcCurveParameters,
    ZcCurvePoint,
)

from ._logger import logger

__all__ = [
    "CalendarAdjustmentEnum",
    "CalibrationMethodEnum",
    "CommoditiesCalendarSpreadFields",
    "CommoditiesCalendarSpreadFieldsDescription",
    "CommoditiesCalendarSpreadFieldsFormulaDescription",
    "CommoditiesCalendarSpreadFieldsOutput",
    "CommoditiesCalendarSpreadFormulaFields",
    "CommoditiesCalendarSpreadFormulaParameter",
    "CommoditiesCalendarSpreadFormulaParameterDescription",
    "CommoditiesCalendarSpreadFormulaParameterOutput",
    "CommoditiesCalendarSpreadInstrument",
    "CommoditiesCalendarSpreadInstrumentDefinition",
    "CommoditiesCalendarSpreadInstrumentDescription",
    "CommoditiesCalendarSpreadInstrumentOutput",
    "CommoditiesChainSource",
    "CommoditiesCurveConstituents",
    "CommoditiesCurveConstituentsDescription",
    "CommoditiesCurveConstituentsOutput",
    "CommoditiesCurveDefinition",
    "CommoditiesCurveDefinitionBase",
    "CommoditiesCurveDefinitionDescription",
    "CommoditiesCurveDefinitionOutput",
    "CommoditiesCurveDefinitionRequest",
    "CommoditiesCurveDefinitionRequestKeys",
    "CommoditiesCurveDefinitionResponse",
    "CommoditiesCurveDefinitionsResponse",
    "CommoditiesCurveDefinitionsResponseItems",
    "CommoditiesCurveParameters",
    "CommoditiesCurveParametersDescription",
    "CommoditiesCurvePoint",
    "CommoditiesCurvePointsInstrument",
    "CommoditiesCurveReferenceUpdateDefinition",
    "CommoditiesCurveRequestItem",
    "CommoditiesCurveResponse",
    "CommoditiesCurveSegmentReferenceCurve",
    "CommoditiesCurvesReferenceResponseItem",
    "CommoditiesCurvesResponse",
    "CommoditiesCurvesResponseItem",
    "CommoditiesFieldsFormulaOutput",
    "CommoditiesFuturesFields",
    "CommoditiesFuturesFieldsDescription",
    "CommoditiesFuturesFieldsFormulaDescription",
    "CommoditiesFuturesFieldsOutput",
    "CommoditiesFuturesFormulaFields",
    "CommoditiesFuturesFormulaParameter",
    "CommoditiesFuturesFormulaParameterDescription",
    "CommoditiesFuturesFormulaParameterOutput",
    "CommoditiesFuturesInstrument",
    "CommoditiesFuturesInstrumentDefinition",
    "CommoditiesFuturesInstrumentDescription",
    "CommoditiesFuturesInstrumentOutput",
    "CommoditiesInstrumentDefinitionDescription",
    "CommoditiesInstrumentsOutput",
    "CommoditiesInstrumentsRequest",
    "CommoditiesInstrumentsSegment",
    "CommoditiesInstrumentsSegmentCreate",
    "CommoditiesInterProductSpreadFields",
    "CommoditiesInterProductSpreadFieldsDescription",
    "CommoditiesInterProductSpreadFieldsFormulaDescription",
    "CommoditiesInterProductSpreadFieldsFormulaOutput",
    "CommoditiesInterProductSpreadFieldsOutput",
    "CommoditiesInterProductSpreadFormulaFields",
    "CommoditiesInterProductSpreadFormulaParameter",
    "CommoditiesInterProductSpreadFormulaParameterDescription",
    "CommoditiesInterProductSpreadFormulaParameterOutput",
    "CommoditiesInterProductSpreadInstrument",
    "CommoditiesInterProductSpreadInstrumentDefinition",
    "CommoditiesInterProductSpreadInstrumentDefinitionDescription",
    "CommoditiesInterProductSpreadInstrumentDescription",
    "CommoditiesInterProductSpreadInstrumentsOutput",
    "CommoditiesInterestRateCurve",
    "CommoditiesInterestRateCurveDefinition",
    "CommoditiesReferenceCurve",
    "CompoundingTypeEnum",
    "ConstantForwardRateParameters",
    "ConstituentOverrideModeEnum",
    "ConstituentsFiltersDescription",
    "CurveInfo",
    "CurveTenorsFrequencyEnum",
    "CurvesAndSurfacesConvexityAdjustment",
    "CurvesAndSurfacesInterestCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesUnitEnum",
    "CurvesAndSurfacesValuationTime",
    "ExtrapolationModeEnum",
    "FieldDateOutput",
    "FieldDateValue",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FieldFormulaDoubleOutput",
    "FieldFormulaDoubleValue",
    "FieldTimeOutput",
    "FieldTimeValue",
    "InstrumentTypeEnum",
    "InterestRateCurveParameters",
    "InterpolationModeEnum",
    "MainConstituentAssetClassEnum",
    "MarketDataAccessDeniedFallbackEnum",
    "MarketDataLookBack",
    "MarketDataTime",
    "ProductEnum",
    "RiskTypeEnum",
    "Seasonality",
    "SeasonalityCurvePoint",
    "SeasonalityDescription",
    "SectorEnum",
    "Step",
    "StepModeEnum",
    "SubSectorEnum",
    "Turn",
    "ZcCurve",
    "ZcCurveInstrument",
    "ZcCurveParameters",
    "ZcCurvePoint",
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
    universe: Optional[List[CommoditiesCurveRequestItem]] = None,
    fields: Optional[str] = None,
) -> CommoditiesCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[CommoditiesCurveRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurvesResponse
        CommoditiesCurvesResponse

    Examples
    --------


    """

    try:
        logger.info("Calling calculate")

        response = Client().commodities_curves.calculate(fields=fields, universe=universe)

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
) -> CommoditiesCurvesResponseItem:
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
    CommoditiesCurvesResponseItem
        CommoditiesCurvesResponseItem

    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().commodities_curves.calculate_by_id(
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
    curve_definition: Optional[CommoditiesCurveDefinitionDescription] = None,
    segments: Optional[List[CommoditiesInstrumentsSegmentCreate]] = None,
) -> CommoditiesCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : CommoditiesCurveDefinitionDescription, optional
        CommoditiesCurveDefinitionDescription
    segments : List[CommoditiesInstrumentsSegmentCreate], optional
        Get segments

    Returns
    --------
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling create")

        response = Client().commodities_curves.create(
            body=CommoditiesCurveCreateRequest(curve_definition=curve_definition, segments=segments)
        )

        output = response
        logger.info("Called create")

        return output
    except Exception as err:
        logger.error("Error create.")
        check_exception_and_raise(err, logger)


def delete(*, curve_id: str) -> bool:
    """
    Delete a CommoditiesCurveDefinition that exists in the platform. The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting CommoditiesCurvesResource with id: {curve_id}")
        Client().commodities_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted CommoditiesCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[CommoditiesCurveDefinitionDescription] = None,
    segments: Optional[List[CommoditiesInstrumentsSegmentCreate]] = None,
) -> CommoditiesCurveResponse:
    """
    Overwrite a CommoditiesCurveDefinition that exists in the platform. The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : CommoditiesCurveDefinitionDescription, optional
        CommoditiesCurveDefinitionDescription
    segments : List[CommoditiesInstrumentsSegmentCreate], optional
        Get segments
    curve_id : str
        The curve identifier.

    Returns
    --------
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling overwrite")

        response = Client().commodities_curves.overwrite(
            body=CommoditiesCurveCreateRequest(curve_definition=curve_definition, segments=segments),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> CommoditiesCurveResponse:
    """
    Access a CommoditiesCurveDefinition existing in the platform (read). The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling read")

        response = Client().commodities_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[CommoditiesCurveDefinitionRequest]] = None,
    fields: Optional[str] = None,
) -> CommoditiesCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[CommoditiesCurveDefinitionRequest], optional
        Get universe
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurveDefinitionsResponse
        CommoditiesCurveDefinitionsResponse

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().commodities_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
