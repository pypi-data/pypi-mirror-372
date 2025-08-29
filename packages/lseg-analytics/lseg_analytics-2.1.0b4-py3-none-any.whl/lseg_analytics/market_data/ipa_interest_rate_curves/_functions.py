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
    BasisInstrumentFutures,
    BasisInstrumentFuturesOutput,
    BidAskFieldsDescription,
    BidAskFieldsFormulaDescription,
    BidAskFieldsFormulaOutput,
    BidAskFieldsOutput,
    BidAskFormulaFields,
    ButterflyShift,
    CalendarAdjustmentEnum,
    CalibrationMethodEnum,
    CategoryEnum,
    CombinedShift,
    CompoundingTypeEnum,
    ConstantForwardRateParameters,
    ConstituentOverrideModeEnum,
    Constituents,
    ConstituentsOutput,
    CrossCurrencyCurveDefinitionPricing,
    CrossCurrencyInstrument,
    CrossCurrencyInstrumentDefinition,
    CrossCurrencyInstrumentDefinitionOutput,
    CrossCurrencyInstrumentOutput,
    CrossCurrencyInstruments,
    CrossCurrencyInstrumentsOutput,
    CrossCurrencyInstrumentsSources,
    CurveInfo,
    CurvesAndSurfacesBidAskFields,
    CurvesAndSurfacesConvexityAdjustment,
    CurvesAndSurfacesInterestCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesQuotationModeEnum,
    CurvesAndSurfacesUnitEnum,
    CurvesAndSurfacesValuationTime,
    DepositInstrumentsSource,
    ErrorDetails,
    ErrorResponse,
    ExtrapolationModeEnum,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FieldFormulaDoubleOutput,
    FieldFormulaDoubleValue,
    FlatteningShift,
    FormulaParameter,
    FormulaParameterDescription,
    FormulaParameterOutput,
    FutureShiftMethodEnum,
    FuturesInstrumentDefinition,
    FuturesInstrumentDefinitionOutput,
    FuturesInstrumentDescription,
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
    InstrumentDefinition,
    InstrumentDefinitionOutput,
    InstrumentTypeEnum,
    InterestRateConstituentsDescription,
    InterestRateCurveCreateRequest,
    InterestRateCurveDefinition,
    InterestRateCurveDefinitionDescription,
    InterestRateCurveDefinitionResponse,
    InterestRateCurveInstrumentDescription,
    InterestRateCurveParameters,
    InterestRateCurveParametersSegmentDescription,
    InterestRateInstrument,
    InterestRateInstrumentOutput,
    InterestRateInstruments,
    InterestRateInstrumentsOutput,
    InterestRateInstrumentsSegment,
    InterestRateInstrumentsSources,
    InterpolationModeEnum,
    IPAInterestRateCurveResponse,
    IslamicProductCategoryEnum,
    LongEndShift,
    MainConstituentAssetClassEnum,
    MarketDataAccessDeniedFallbackEnum,
    MarketDataLocationEnum,
    MarketDataLookBack,
    MarketDataLookBackDefinition,
    MarketDataTime,
    OverrideBidAsk,
    OverrideBidAskFields,
    ParallelShift,
    ParRateShift,
    ProcessingInformation,
    RiskTypeEnum,
    ShiftCrossCurrencyInstrumentsItem,
    ShiftDefinition,
    ShiftDefinitionFutures,
    ShiftedUnderlyingCurves,
    ShiftFuturesParameter,
    ShiftInterestRateInstrumentsItem,
    ShiftInterestRateInstrumentsPerBasis,
    ShiftScenario,
    ShiftTypeEnum,
    ShiftUnitEnum,
    ShortEndShift,
    Step,
    StepCurvePoint,
    StepModeEnum,
    StubBasisInterestRateCurveInstrumentDescription,
    StubBasisInterestRateInstrument,
    StubBasisInterestRateInstrumentOutput,
    SyntheticInstrumentDefinition,
    TimeBucketShift,
    Turn,
    TwistShift,
    UnderlyingCurves,
    UnderlyingZcCurves,
    ZcCurve,
    ZcCurveDefinition,
    ZcCurveDefinitionOutput,
    ZcCurveDefinitionRequest,
    ZcCurveDefinitions,
    ZcCurveDefinitionsItem,
    ZcCurveDefinitionsOutput,
    ZcCurveDefinitionsResponse,
    ZcCurveDefinitionsResponseItem,
    ZcCurveInstrument,
    ZcCurveParameters,
    ZcCurvePoint,
    ZcCurveRequestItem,
    ZcCurvesResponse,
    ZcCurvesResponseItem,
    ZcShiftedCurve,
)

from ._logger import logger

__all__ = [
    "BasisInstrumentFutures",
    "BasisInstrumentFuturesOutput",
    "BidAskFieldsDescription",
    "BidAskFieldsFormulaDescription",
    "BidAskFieldsFormulaOutput",
    "BidAskFieldsOutput",
    "BidAskFormulaFields",
    "ButterflyShift",
    "CalendarAdjustmentEnum",
    "CalibrationMethodEnum",
    "CategoryEnum",
    "CombinedShift",
    "CompoundingTypeEnum",
    "ConstantForwardRateParameters",
    "ConstituentOverrideModeEnum",
    "Constituents",
    "ConstituentsOutput",
    "CrossCurrencyCurveDefinitionPricing",
    "CrossCurrencyInstrument",
    "CrossCurrencyInstrumentDefinition",
    "CrossCurrencyInstrumentDefinitionOutput",
    "CrossCurrencyInstrumentOutput",
    "CrossCurrencyInstruments",
    "CrossCurrencyInstrumentsOutput",
    "CrossCurrencyInstrumentsSources",
    "CurveInfo",
    "CurvesAndSurfacesBidAskFields",
    "CurvesAndSurfacesConvexityAdjustment",
    "CurvesAndSurfacesInterestCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesQuotationModeEnum",
    "CurvesAndSurfacesUnitEnum",
    "CurvesAndSurfacesValuationTime",
    "DepositInstrumentsSource",
    "ErrorDetails",
    "ErrorResponse",
    "ExtrapolationModeEnum",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FieldFormulaDoubleOutput",
    "FieldFormulaDoubleValue",
    "FlatteningShift",
    "FormulaParameter",
    "FormulaParameterDescription",
    "FormulaParameterOutput",
    "FutureShiftMethodEnum",
    "FuturesInstrumentDefinition",
    "FuturesInstrumentDefinitionOutput",
    "FuturesInstrumentDescription",
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
    "IPAInterestRateCurveResponse",
    "InstrumentDefinition",
    "InstrumentDefinitionOutput",
    "InstrumentTypeEnum",
    "InterestRateConstituentsDescription",
    "InterestRateCurveDefinition",
    "InterestRateCurveDefinitionDescription",
    "InterestRateCurveDefinitionResponse",
    "InterestRateCurveInstrumentDescription",
    "InterestRateCurveParameters",
    "InterestRateCurveParametersSegmentDescription",
    "InterestRateInstrument",
    "InterestRateInstrumentOutput",
    "InterestRateInstruments",
    "InterestRateInstrumentsOutput",
    "InterestRateInstrumentsSegment",
    "InterestRateInstrumentsSources",
    "InterpolationModeEnum",
    "IslamicProductCategoryEnum",
    "LongEndShift",
    "MainConstituentAssetClassEnum",
    "MarketDataAccessDeniedFallbackEnum",
    "MarketDataLocationEnum",
    "MarketDataLookBack",
    "MarketDataLookBackDefinition",
    "MarketDataTime",
    "OverrideBidAsk",
    "OverrideBidAskFields",
    "ParRateShift",
    "ParallelShift",
    "ProcessingInformation",
    "RiskTypeEnum",
    "ShiftCrossCurrencyInstrumentsItem",
    "ShiftDefinition",
    "ShiftDefinitionFutures",
    "ShiftFuturesParameter",
    "ShiftInterestRateInstrumentsItem",
    "ShiftInterestRateInstrumentsPerBasis",
    "ShiftScenario",
    "ShiftTypeEnum",
    "ShiftUnitEnum",
    "ShiftedUnderlyingCurves",
    "ShortEndShift",
    "Step",
    "StepCurvePoint",
    "StepModeEnum",
    "StubBasisInterestRateCurveInstrumentDescription",
    "StubBasisInterestRateInstrument",
    "StubBasisInterestRateInstrumentOutput",
    "SyntheticInstrumentDefinition",
    "TimeBucketShift",
    "Turn",
    "TwistShift",
    "UnderlyingCurves",
    "UnderlyingZcCurves",
    "ZcCurve",
    "ZcCurveDefinition",
    "ZcCurveDefinitionOutput",
    "ZcCurveDefinitionRequest",
    "ZcCurveDefinitions",
    "ZcCurveDefinitionsItem",
    "ZcCurveDefinitionsOutput",
    "ZcCurveDefinitionsResponse",
    "ZcCurveDefinitionsResponseItem",
    "ZcCurveInstrument",
    "ZcCurveParameters",
    "ZcCurvePoint",
    "ZcCurveRequestItem",
    "ZcCurvesResponse",
    "ZcCurvesResponseItem",
    "ZcShiftedCurve",
    "calculate",
    "calculate_by_id",
    "create",
    "delete",
    "overwrite",
    "read",
    "search",
]


def calculate(*, universe: Optional[List[ZcCurveRequestItem]] = None, fields: Optional[str] = None) -> ZcCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[ZcCurveRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    ZcCurvesResponse
        ZcCurvesResponse

    Examples
    --------


    """

    try:
        logger.info("Calling calculate")

        response = Client().ipa_interest_rate_curves.calculate(fields=fields, universe=universe)

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
) -> ZcCurvesResponseItem:
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
    ZcCurvesResponseItem
        ZcCurvesResponseItem

    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().ipa_interest_rate_curves.calculate_by_id(
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
    curve_definition: Optional[InterestRateCurveDefinitionDescription] = None,
    overrides: Optional[List[OverrideBidAsk]] = None,
    segments: Optional[List[InterestRateInstrumentsSegment]] = None,
    steps: Optional[List[Step]] = None,
) -> IPAInterestRateCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : InterestRateCurveDefinitionDescription, optional

    overrides : List[OverrideBidAsk], optional
        Get overrides
    segments : List[InterestRateInstrumentsSegment], optional
        Get segments
    steps : List[Step], optional
        Get steps

    Returns
    --------
    IPAInterestRateCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling create")

        response = Client().ipa_interest_rate_curves.create(
            body=InterestRateCurveCreateRequest(
                curve_definition=curve_definition,
                overrides=overrides,
                segments=segments,
                steps=steps,
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
    Delete a InterestRateCurveDefinition that exists in the platform. The InterestRateCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
        logger.info(f"Deleting IpaInterestRateCurvesResource with id: {curve_id}")
        Client().ipa_interest_rate_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted IpaInterestRateCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[InterestRateCurveDefinitionDescription] = None,
    overrides: Optional[List[OverrideBidAsk]] = None,
    segments: Optional[List[InterestRateInstrumentsSegment]] = None,
    steps: Optional[List[Step]] = None,
) -> IPAInterestRateCurveResponse:
    """
    Overwrite a InterestRateCurveDefinition that exists in the platform. The InterestRateCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : InterestRateCurveDefinitionDescription, optional

    overrides : List[OverrideBidAsk], optional
        Get overrides
    segments : List[InterestRateInstrumentsSegment], optional
        Get segments
    steps : List[Step], optional
        Get steps
    curve_id : str
        The curve identifier.

    Returns
    --------
    IPAInterestRateCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling overwrite")

        response = Client().ipa_interest_rate_curves.overwrite(
            body=InterestRateCurveCreateRequest(
                curve_definition=curve_definition,
                overrides=overrides,
                segments=segments,
                steps=steps,
            ),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> IPAInterestRateCurveResponse:
    """
    Access a InterestRateCurveDefinition existing in the platform (read). The InterestRateCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    IPAInterestRateCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling read")

        response = Client().ipa_interest_rate_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[ZcCurveDefinitionRequest]] = None,
    fields: Optional[str] = None,
) -> ZcCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[ZcCurveDefinitionRequest], optional
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
    ZcCurveDefinitionsResponse
        ZcCurveDefinitionsResponse

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().ipa_interest_rate_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
