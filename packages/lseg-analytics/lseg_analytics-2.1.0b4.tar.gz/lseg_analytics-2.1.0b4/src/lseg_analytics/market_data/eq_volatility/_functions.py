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
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesTimeStampEnum,
    CurvesAndSurfacesUnderlyingTypeEnum,
    CurvesAndSurfacesVolatilityModelEnum,
    EtiSurfaceDefinition,
    EtiSurfaceParameters,
    EtiVolatilitySurfaceRequestItem,
    FormatEnum,
    InputVolatilityTypeEnum,
    MaturityFilter,
    MoneynessTypeEnum,
    MoneynessWeight,
    StrikeFilter,
    StrikeFilterRange,
    SurfaceFilters,
    SurfaceOutput,
    VolatilitySurfacePoint,
    VolatilitySurfaceResponse,
    VolatilitySurfaceResponseItem,
    XAxisEnum,
    YAxisEnum,
)

from ._logger import logger

__all__ = [
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesTimeStampEnum",
    "CurvesAndSurfacesUnderlyingTypeEnum",
    "CurvesAndSurfacesVolatilityModelEnum",
    "EtiSurfaceDefinition",
    "EtiSurfaceParameters",
    "EtiVolatilitySurfaceRequestItem",
    "FormatEnum",
    "InputVolatilityTypeEnum",
    "MaturityFilter",
    "MoneynessTypeEnum",
    "MoneynessWeight",
    "StrikeFilter",
    "StrikeFilterRange",
    "SurfaceFilters",
    "SurfaceOutput",
    "VolatilitySurfacePoint",
    "VolatilitySurfaceResponse",
    "VolatilitySurfaceResponseItem",
    "XAxisEnum",
    "YAxisEnum",
    "calculate",
]


def calculate(
    *, universe: Optional[List[EtiVolatilitySurfaceRequestItem]] = None, fields: Optional[str] = None
) -> VolatilitySurfaceResponse:
    """
    Generates the surfaces for the definitions provided

    Parameters
    ----------
    universe : List[EtiVolatilitySurfaceRequestItem], optional

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
    >>> # Select a RIC for equities and indices
    >>> ric = "AAPL.O@RIC"
    >>>
    >>> # Create surface definition object
    >>> surface_definition = ev.EtiSurfaceDefinition(
    >>>         instrument_code = ric
    >>>         # exchange = 'NSQ'  # NASDAQ
    >>>         )
    >>> print(f"   ✓ Instrument: {surface_definition.instrument_code}")
    >>>
    >>>
    >>> print("Step 2: Configuring Surface Parameters...")
    >>> surface_parameters = ev.EtiSurfaceParameters(
    >>>         calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
    >>>         time_stamp = ev.CurvesAndSurfacesTimeStampEnum.DEFAULT,          # Options: CLOSE, OPEN, SETTLE, DEFAULT
    >>>         input_volatility_type = ev.InputVolatilityTypeEnum.IMPLIED,      # Options: IMPLIED, QUOTED
    >>>         volatility_model = ev.CurvesAndSurfacesVolatilityModelEnum.SSVI, # Options: SVI, SSVI
    >>>         moneyness_type = ev.MoneynessTypeEnum.SPOT,                      # Options: SPOT
    >>>         price_side = ev.CurvesAndSurfacesPriceSideEnum.MID,              # Options: BID, MID, ASK
    >>>         x_axis = ev.XAxisEnum.STRIKE,                                    # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
    >>>         y_axis = ev.YAxisEnum.DATE                                       # Options: same as X-axis
    >>>     )
    >>> print(f"   ✓ Surface Parameters: {surface_parameters}")
    >>>
    >>>
    >>> print("Step 3: Create request item...")
    >>> # Create the main request object  with basic configuration
    >>> request_item = ev.EtiVolatilitySurfaceRequestItem(
    >>>         surface_tag = f"{ric}_Volsurface",
    >>>         underlying_definition = surface_definition,
    >>>         surface_parameters = surface_parameters,
    >>>         underlying_type = ev.CurvesAndSurfacesUnderlyingTypeEnum.ETI,
    >>>         surface_layout = ev.SurfaceOutput(
    >>>             format = ev.FormatEnum.MATRIX,  # Options: LIST, MATRIX
    >>>         )
    >>>     )
    >>> print(f"   ✓ Request Item: {request_item}")
    Step 1: Creating Surface Definition...
       ✓ Instrument: AAPL.O@RIC
    Step 2: Configuring Surface Parameters...
       ✓ Surface Parameters: {'calculationDate': '2025-01-18T00:00:00Z', 'timeStamp': 'Default', 'inputVolatilityType': 'Implied', 'volatilityModel': 'SSVI', 'moneynessType': 'Spot', 'priceSide': 'Mid', 'xAxis': 'Strike', 'yAxis': 'Date'}
    Step 3: Create request item...
       ✓ Request Item: {'surfaceTag': 'AAPL.O@RIC_Volsurface', 'underlyingDefinition': {'instrumentCode': 'AAPL.O@RIC'}, 'surfaceParameters': {'calculationDate': '2025-01-18T00:00:00Z', 'timeStamp': 'Default', 'inputVolatilityType': 'Implied', 'volatilityModel': 'SSVI', 'moneynessType': 'Spot', 'priceSide': 'Mid', 'xAxis': 'Strike', 'yAxis': 'Date'}, 'underlyingType': 'Eti', 'surfaceLayout': {'format': 'Matrix'}}


    >>> # Execute the calculation using the calculate function
    >>> # The 'universe' parameter accepts a list of request items for batch processing
    >>> try:
    >>>     response = ev.calculate(universe=[request_item])
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
       Surface data points available: 20

    """

    try:
        logger.info("Calling calculate")

        response = Client().eq_volatility.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)
