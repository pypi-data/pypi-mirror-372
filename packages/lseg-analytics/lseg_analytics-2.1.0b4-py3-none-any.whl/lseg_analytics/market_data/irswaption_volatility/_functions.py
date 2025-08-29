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
    CurvesAndSurfacesCalibrationTypeEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesStrikeTypeEnum,
    CurvesAndSurfacesTimeStampEnum,
    CurvesAndSurfacesUnderlyingTypeEnum,
    DiscountingTypeEnum,
    FormatEnum,
    InputVolatilityTypeEnum,
    OutputVolatilityTypeEnum,
    SurfaceOutput,
    VolatilityAdjustmentTypeEnum,
    VolatilityCubeDefinition,
    VolatilityCubeSurfaceParameters,
    VolatilityCubeSurfaceRequestItem,
    VolatilitySurfacePoint,
    VolatilitySurfaceResponse,
    VolatilitySurfaceResponseItem,
    XAxisEnum,
    YAxisEnum,
    ZAxisEnum,
)

from ._logger import logger

__all__ = [
    "CurvesAndSurfacesCalibrationTypeEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesStrikeTypeEnum",
    "CurvesAndSurfacesTimeStampEnum",
    "CurvesAndSurfacesUnderlyingTypeEnum",
    "DiscountingTypeEnum",
    "FormatEnum",
    "InputVolatilityTypeEnum",
    "OutputVolatilityTypeEnum",
    "SurfaceOutput",
    "VolatilityAdjustmentTypeEnum",
    "VolatilityCubeDefinition",
    "VolatilityCubeSurfaceParameters",
    "VolatilityCubeSurfaceRequestItem",
    "VolatilitySurfacePoint",
    "VolatilitySurfaceResponse",
    "VolatilitySurfaceResponseItem",
    "XAxisEnum",
    "YAxisEnum",
    "ZAxisEnum",
    "calculate",
]


def calculate(
    *, universe: Optional[List[VolatilityCubeSurfaceRequestItem]] = None, fields: Optional[str] = None
) -> VolatilitySurfaceResponse:
    """
    Generates the surfaces for the definitions provided

    Parameters
    ----------
    universe : List[VolatilityCubeSurfaceRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    VolatilitySurfaceResponse


    Examples
    --------


    """

    try:
        logger.info("Calling calculate")

        response = Client().irswaption_volatility.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)
