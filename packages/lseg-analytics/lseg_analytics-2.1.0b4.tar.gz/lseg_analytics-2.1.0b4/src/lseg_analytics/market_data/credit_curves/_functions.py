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
    BasisSplineSmoothModelEnum,
    BidAskFieldsDescription,
    BidAskFieldsFormulaDescription,
    BidAskFieldsFormulaOutput,
    BidAskFieldsOutput,
    BidAskFormulaFields,
    BondInstrument,
    BondInstrumentDefinition,
    BondInstrumentDescription,
    BondInstrumentOutput,
    BusinessSectorEnum,
    CalendarAdjustmentEnum,
    CalibrationModelEnum,
    CalibrationParameters,
    CategoryEnum,
    CompoundingTypeEnum,
    CreditConstituents,
    CreditConstituentsDescription,
    CreditConstituentsOutput,
    CreditCurveCreateDefinition,
    CreditCurveCreateRequest,
    CreditCurveDefinition,
    CreditCurveDefinitionDescription,
    CreditCurveDefinitionOutput,
    CreditCurveDefinitionResponse,
    CreditCurveDefinitionResponseItem,
    CreditCurveDefinitionsResponse,
    CreditCurveDefinitionsResponseItems,
    CreditCurveInstrumentsSegment,
    CreditCurveParameters,
    CreditCurveParametersDescription,
    CreditCurvePoint,
    CreditCurveRequestItem,
    CreditCurveResponse,
    CreditCurveSearchDefinition,
    CreditCurvesResponse,
    CreditCurvesResponseItem,
    CreditCurveTypeEnum,
    CreditDefaultSwapInstrument,
    CreditDefaultSwapInstrumentDefinition,
    CreditDefaultSwapInstrumentOutput,
    CreditDefaultSwapsInstrumentDescription,
    CreditInstruments,
    CreditInstrumentsOutput,
    CrossCurrencyInstrument,
    CrossCurrencyInstrumentDefinition,
    CrossCurrencyInstrumentDefinitionOutput,
    CrossCurrencyInstrumentOutput,
    CrossCurrencyInstruments,
    CrossCurrencyInstrumentsOutput,
    CrossCurrencyInstrumentsSources,
    CurveInfo,
    CurvesAndSurfacesBidAskFields,
    CurvesAndSurfacesInstrument,
    CurvesAndSurfacesInterestCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesQuotationModeEnum,
    CurvesAndSurfacesSeniorityEnum,
    CurveSubTypeEnum,
    DepositInstrumentOutput,
    EconomicSectorEnum,
    ErrorDetails,
    ErrorResponse,
    ExtrapolationModeEnum,
    ExtrapolationTypeEnum,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FieldFormulaDoubleOutput,
    FieldFormulaDoubleValue,
    FormulaParameter,
    FormulaParameterDescription,
    FormulaParameterOutput,
    FxForwardInstrument,
    FxForwardInstrumentDefinition,
    FxForwardInstrumentDefinitionOutput,
    FxForwardInstrumentOutput,
    FxForwardInstrumentsSource,
    FxSpotInstrument,
    FxSpotInstrumentDefinition,
    FxSpotInstrumentDefinitionOutput,
    FxSpotInstrumentOutput,
    FxSpotInstrumentsSource,
    IndustryEnum,
    IndustryGroupEnum,
    InstrumentDefinition,
    InstrumentDescription,
    InstrumentTypeEnum,
    InterpolationModeEnum,
    IssuerTypeEnum,
    MainConstituentAssetClassEnum,
    MarketDataLocationEnum,
    MarketDataTime,
    ProcessingInformation,
    RatingEnum,
    RatingScaleSourceEnum,
    ReferenceEntityTypeEnum,
    RiskTypeEnum,
)

from ._logger import logger

__all__ = [
    "BasisSplineSmoothModelEnum",
    "BidAskFieldsDescription",
    "BidAskFieldsFormulaDescription",
    "BidAskFieldsFormulaOutput",
    "BidAskFieldsOutput",
    "BidAskFormulaFields",
    "BondInstrument",
    "BondInstrumentDefinition",
    "BondInstrumentDescription",
    "BondInstrumentOutput",
    "BusinessSectorEnum",
    "CalendarAdjustmentEnum",
    "CalibrationModelEnum",
    "CalibrationParameters",
    "CategoryEnum",
    "CompoundingTypeEnum",
    "CreditConstituents",
    "CreditConstituentsDescription",
    "CreditConstituentsOutput",
    "CreditCurveCreateDefinition",
    "CreditCurveDefinition",
    "CreditCurveDefinitionDescription",
    "CreditCurveDefinitionOutput",
    "CreditCurveDefinitionResponse",
    "CreditCurveDefinitionResponseItem",
    "CreditCurveDefinitionsResponse",
    "CreditCurveDefinitionsResponseItems",
    "CreditCurveInstrumentsSegment",
    "CreditCurveParameters",
    "CreditCurveParametersDescription",
    "CreditCurvePoint",
    "CreditCurveRequestItem",
    "CreditCurveResponse",
    "CreditCurveSearchDefinition",
    "CreditCurveTypeEnum",
    "CreditCurvesResponse",
    "CreditCurvesResponseItem",
    "CreditDefaultSwapInstrument",
    "CreditDefaultSwapInstrumentDefinition",
    "CreditDefaultSwapInstrumentOutput",
    "CreditDefaultSwapsInstrumentDescription",
    "CreditInstruments",
    "CreditInstrumentsOutput",
    "CrossCurrencyInstrument",
    "CrossCurrencyInstrumentDefinition",
    "CrossCurrencyInstrumentDefinitionOutput",
    "CrossCurrencyInstrumentOutput",
    "CrossCurrencyInstruments",
    "CrossCurrencyInstrumentsOutput",
    "CrossCurrencyInstrumentsSources",
    "CurveInfo",
    "CurveSubTypeEnum",
    "CurvesAndSurfacesBidAskFields",
    "CurvesAndSurfacesInstrument",
    "CurvesAndSurfacesInterestCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesQuotationModeEnum",
    "CurvesAndSurfacesSeniorityEnum",
    "DepositInstrumentOutput",
    "EconomicSectorEnum",
    "ErrorDetails",
    "ErrorResponse",
    "ExtrapolationModeEnum",
    "ExtrapolationTypeEnum",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FieldFormulaDoubleOutput",
    "FieldFormulaDoubleValue",
    "FormulaParameter",
    "FormulaParameterDescription",
    "FormulaParameterOutput",
    "FxForwardInstrument",
    "FxForwardInstrumentDefinition",
    "FxForwardInstrumentDefinitionOutput",
    "FxForwardInstrumentOutput",
    "FxForwardInstrumentsSource",
    "FxSpotInstrument",
    "FxSpotInstrumentDefinition",
    "FxSpotInstrumentDefinitionOutput",
    "FxSpotInstrumentOutput",
    "FxSpotInstrumentsSource",
    "IndustryEnum",
    "IndustryGroupEnum",
    "InstrumentDefinition",
    "InstrumentDescription",
    "InstrumentTypeEnum",
    "InterpolationModeEnum",
    "IssuerTypeEnum",
    "MainConstituentAssetClassEnum",
    "MarketDataLocationEnum",
    "MarketDataTime",
    "ProcessingInformation",
    "RatingEnum",
    "RatingScaleSourceEnum",
    "ReferenceEntityTypeEnum",
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
    universe: Optional[List[CreditCurveRequestItem]] = None,
    fields: Optional[str] = None,
) -> CreditCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[CreditCurveRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CreditCurvesResponse
        CreditCurvesResponse

    Examples
    --------


    """

    try:
        logger.info("Calling calculate")

        response = Client().credit_curves.calculate(fields=fields, universe=universe)

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
) -> CreditCurvesResponseItem:
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
    CreditCurvesResponseItem


    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().credit_curves.calculate_by_id(
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
    curve_definition: Optional[CreditCurveCreateDefinition] = None,
    segments: Optional[List[CreditCurveInstrumentsSegment]] = None,
) -> CreditCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : CreditCurveCreateDefinition, optional
        CreditCurveCreateDefinition
    segments : List[CreditCurveInstrumentsSegment], optional
        Get segments

    Returns
    --------
    CreditCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling create")

        response = Client().credit_curves.create(
            body=CreditCurveCreateRequest(curve_definition=curve_definition, segments=segments)
        )

        output = response
        logger.info("Called create")

        return output
    except Exception as err:
        logger.error("Error create.")
        check_exception_and_raise(err, logger)


def delete(*, curve_id: str) -> bool:
    """
    Delete a CreditCurveDefinition that exists in the platform. The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting CreditCurvesResource with id: {curve_id}")
        Client().credit_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted CreditCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[CreditCurveCreateDefinition] = None,
    segments: Optional[List[CreditCurveInstrumentsSegment]] = None,
) -> CreditCurveResponse:
    """
    Overwrite a CreditCurveDefinition that exists in the platform. The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : CreditCurveCreateDefinition, optional
        CreditCurveCreateDefinition
    segments : List[CreditCurveInstrumentsSegment], optional
        Get segments
    curve_id : str
        The curve identifier.

    Returns
    --------
    CreditCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling overwrite")

        response = Client().credit_curves.overwrite(
            body=CreditCurveCreateRequest(curve_definition=curve_definition, segments=segments),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> CreditCurveResponse:
    """
    Access a CreditCurveDefinition existing in the platform (read). The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    CreditCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling read")

        response = Client().credit_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[CreditCurveSearchDefinition]] = None,
    fields: Optional[str] = None,
) -> CreditCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[CreditCurveSearchDefinition], optional
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
    CreditCurveDefinitionsResponse
        CreditCurveDefinitionsResponse

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().credit_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
