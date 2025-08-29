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
    BidAskMid,
    CurvesAndSurfacesFxSwapCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesTimeStampEnum,
    CurvesAndSurfacesUnderlyingTypeEnum,
    CurvesAndSurfacesVolatilityModelEnum,
    DayWeight,
    FormatEnum,
    FxVolatilityPricingParameters,
    FxVolatilityStatisticsParameters,
    FxVolatilitySurfaceDefinition,
    FxVolatilitySurfaceRequestItem,
    InterpolationWeight,
    SurfaceOutput,
    VolatilitySurfacePoint,
    VolatilitySurfaceResponse,
    VolatilitySurfaceResponseItem,
    XAxisEnum,
    YAxisEnum,
)

from ._logger import logger

__all__ = [
    "BidAskMid",
    "CurvesAndSurfacesFxSwapCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesTimeStampEnum",
    "CurvesAndSurfacesUnderlyingTypeEnum",
    "CurvesAndSurfacesVolatilityModelEnum",
    "DayWeight",
    "FormatEnum",
    "FxVolatilityPricingParameters",
    "FxVolatilityStatisticsParameters",
    "FxVolatilitySurfaceDefinition",
    "FxVolatilitySurfaceRequestItem",
    "InterpolationWeight",
    "SurfaceOutput",
    "VolatilitySurfacePoint",
    "VolatilitySurfaceResponse",
    "VolatilitySurfaceResponseItem",
    "XAxisEnum",
    "YAxisEnum",
    "calculate",
]


def calculate(
    *, universe: Optional[List[FxVolatilitySurfaceRequestItem]] = None, fields: Optional[str] = None
) -> VolatilitySurfaceResponse:
    """
    Generates the surfaces for the definitions provided

    Parameters
    ----------
    universe : List[FxVolatilitySurfaceRequestItem], optional

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
    >>> print("Step 1: Creating Surface Definition...")
    >>>
    >>> currencyPair = "EURUSD"
    >>>
    >>> # Create surface definition object
    >>> surface_definition = fxv.FxVolatilitySurfaceDefinition(
    >>>         instrument_code = currencyPair
    >>>         )
    >>> print(f"   ✓ Instrument: {surface_definition.instrument_code}")
    >>>
    >>> print("Step 2: Configuring Surface Parameters...")
    >>> surface_parameters = fxv.FxVolatilityPricingParameters(
    >>>         calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
    >>>         volatility_model = fxv.CurvesAndSurfacesVolatilityModelEnum.SVI,  # Options: SVI, SABR, TWIN_LOGNORMAL
    >>>         price_side = fxv.CurvesAndSurfacesPriceSideEnum.MID,              # Options: BID, MID, ASK
    >>>         x_axis = fxv.XAxisEnum.DELTA,                                     # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
    >>>         y_axis = fxv.YAxisEnum.TENOR                                      # Options: same as X-axis
    >>>     )
    >>> print(f"   ✓ Surface Parameters: {surface_parameters}")
    >>>
    >>>
    >>> print("Step 3: Create request item...")
    >>> # Create the main request object  with basic configuration
    >>> request_item = fxv.FxVolatilitySurfaceRequestItem(
    >>>         surface_tag = f"{currencyPair}_Volsurface",
    >>>         underlying_definition = surface_definition,
    >>>         surface_parameters = surface_parameters,
    >>>         underlying_type = fxv.CurvesAndSurfacesUnderlyingTypeEnum.FX,
    >>>         surface_layout = fxv.SurfaceOutput(
    >>>             format = fxv.FormatEnum.MATRIX,  # Options: LIST, MATRIX
    >>>         )
    >>>     )
    >>> print(f"   ✓ Request Item: {request_item}")
    Step 1: Creating Surface Definition...
       ✓ Instrument: EURUSD
    Step 2: Configuring Surface Parameters...
       ✓ Surface Parameters: {'calculationDate': '2025-01-18T00:00:00Z', 'volatilityModel': 'SVI', 'priceSide': 'Mid', 'xAxis': 'Delta', 'yAxis': 'Tenor'}
    Step 3: Create request item...
       ✓ Request Item: {'surfaceTag': 'EURUSD_Volsurface', 'underlyingDefinition': {'instrumentCode': 'EURUSD'}, 'surfaceParameters': {'calculationDate': '2025-01-18T00:00:00Z', 'volatilityModel': 'SVI', 'priceSide': 'Mid', 'xAxis': 'Delta', 'yAxis': 'Tenor'}, 'underlyingType': 'Fx', 'surfaceLayout': {'format': 'Matrix'}}


    >>> # Execute the calculation using the calculate function
    >>> # The 'universe' parameter accepts a list of request items for batch processing
    >>> try:
    >>>     response = fxv.calculate(universe=[request_item])
    >>>
    >>>     # Display response structure information
    >>>     surface_data = response['data'][0]
    >>>     if 'surface' in surface_data:
    >>>         print(f"   Calculation successful!")
    >>>         print(f"   Surface data points available: {len(surface_data['surface'])}")
    >>>     else:
    >>>         print("   No surface data found in response")
    >>>
    >>> except Exception as e:
    >>>     print(f"   Calculation failed: {str(e)}")
    >>>     raise
       Calculation successful!
       Surface data points available: 18

    """

    try:
        logger.info("Calling calculate")

        response = Client().fx_volatility.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)
