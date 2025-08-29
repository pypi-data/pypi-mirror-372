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
    Description,
    FxForwardCurveCalculationParameters,
    FxForwardCurveDataOnResourceResponseData,
    FxForwardCurveDataResponseData,
    FxForwardCurveDefinition,
    FxForwardCurveDefinitionInstrument,
    FxForwardCurveInfo,
    IndirectSourcesDeposits,
    IndirectSourcesSwaps,
    Location,
    ResourceType,
    SortingOrderEnum,
    TenorType,
)

from ._logger import logger


class FxForwardCurve(ResourceBase):
    """
    FxForwardCurve object.

    Contains all the necessary information to identify and define a FxForwardCurve instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the FxForwardCurve.
    location : Location
        Object defining the location of the FxForwardCurve in the platform.
    description : Description, optional
        Object defining metadata for the FxForwardCurve.
    definition : FxForwardCurveDefinition
        Object defining the FxForwardCurve.

    See Also
    --------
    FxForwardCurve.calculate : Calculate points for a curve stored in the platform.
        The user must provide a curve ID to use an available definition. Only calculation preferences can be overridden.

    Examples
    --------
    >>> # Create a new curve from scratch.
    >>> fx_curve = FxForwardCurve(
    >>>     description=Description(summary="My FX Forward Curve", tags=["tag1", "tag2"]),
    >>>     definition=FxForwardCurveDefinition(
    >>>         cross_currency="EURJPY",
    >>>         reference_currency="USD",
    >>>         constituents=[
    >>>             FxSpotConstituent(
    >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPY=")),
    >>>                 definition=FxSpotConstituentDefinition(template="USDJPY"),
    >>>             ),
    >>>             FxForwardConstituent(
    >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPY1M=")),
    >>>                 definition=FxForwardConstituentDefinition(tenor="1M", template="USDJPY"),
    >>>             ),
    >>>             CurrencyBasisSwapConstituent(
    >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPYCBS10Y=")),
    >>>                 definition=CurrencyBasisSwapConstituentDefinition(tenor="10Y", template="JPYCBS"),
    >>>             ),
    >>>             DepositFxConstituent(
    >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="EURIMM1=")),
    >>>                 definition=DepositConstituentDefinition(tenor="IMM1", template="EUR"),
    >>>             ),
    >>>         ],
    >>>     ),
    >>> )


    >>>
    >>> # Save the instance with name and space.
    >>> fx_curve.save(name="EURCHF_Fx_Forward_Curve", space="MYCURVE")
    True

    """

    _definition_class = FxForwardCurveDefinition

    def __init__(
        self,
        definition: FxForwardCurveDefinition,
        description: Optional[Description] = None,
    ):
        """
        FxForwardCurve constructor

        Parameters
        ----------
        definition : FxForwardCurveDefinition
            Object defining the FxForwardCurve.
        description : Description, optional
            Object defining metadata for the FxForwardCurve.

        Examples
        --------
        >>> # Create a new curve from scratch.
        >>> fx_curve = FxForwardCurve(
        >>>     description=Description(summary="My FX Forward Curve", tags=["tag1", "tag2"]),
        >>>     definition=FxForwardCurveDefinition(
        >>>         cross_currency="EURJPY",
        >>>         reference_currency="USD",
        >>>         constituents=[
        >>>             FxSpotConstituent(
        >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPY=")),
        >>>                 definition=FxSpotConstituentDefinition(template="USDJPY"),
        >>>             ),
        >>>             FxForwardConstituent(
        >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPY1M=")),
        >>>                 definition=FxForwardConstituentDefinition(tenor="1M", template="USDJPY"),
        >>>             ),
        >>>             CurrencyBasisSwapConstituent(
        >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="JPYCBS10Y=")),
        >>>                 definition=CurrencyBasisSwapConstituentDefinition(tenor="10Y", template="JPYCBS"),
        >>>             ),
        >>>             DepositFxConstituent(
        >>>                 quote=Quote(definition=QuoteDefinition(instrument_code="EURIMM1=")),
        >>>                 definition=DepositConstituentDefinition(tenor="IMM1", template="EUR"),
        >>>             ),
        >>>         ],
        >>>     ),
        >>> )

        """
        self.definition: FxForwardCurveDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "FxForwardCurve"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the FxForwardCurve id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the FxForwardCurve.

        Examples
        --------
        >>> # Get the instance id.
        >>> fx_curve.id
        '194fbcb0-868f-4129-bc5d-556b49b18cce'

        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the FxForwardCurve location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the FxForwardCurve in the platform.

        Examples
        --------
        >>> # Get the location property.
        >>> fx_curve.location.name
        'EURCHF_Fx_Forward_Curve'


        >>> fx_curve.location.space
        'MYCURVE'

        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def calculate(
        self,
        *,
        pricing_preferences: Optional[FxForwardCurveCalculationParameters] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> FxForwardCurveDataOnResourceResponseData:
        """
        Calculate points for a curve stored in the platform.
        The user must provide a curve ID to use an available definition. Only calculation preferences can be overridden.

        Parameters
        ----------
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
        FxForwardCurveDataOnResourceResponseData


        Examples
        --------
        >>> # Calling calculate on a FxForwardCurve instance.
        >>> response = fx_curve.calculate()
        >>> print(json.dumps(response.analytics.as_dict(), indent=2)[:500] + "...")
        {
          "outrightCurve": {
            "curveType": "FxOutrightCurve",
            "points": [
              {
                "startDate": "2025-05-23",
                "endDate": "2025-05-27",
                "tenor": "ON",
                "outright": {
                  "bid": 162.79586525762826,
                  "ask": 162.8566343562079,
                  "mid": 162.8262498069181
                },
                "instruments": [
                  {
                    "instrumentCode": "JPONMU=RR"
                  },
                  {
                    "instrumentCode": "USDOND="
                  },
                  {
                    "ins...


        >>> # Calling calculate on a FxForwardCurve instance with parameters.
        >>> response = fx_curve.calculate(
        >>>     pricing_preferences=FxForwardCurveCalculationParameters(valuation_date=datetime.date(2024, 1, 1))
        >>> )
        >>> print(json.dumps(response.analytics.as_dict(), indent=2)[:500] + "...")
        {
          "outrightCurve": {
            "curveType": "FxOutrightCurve",
            "points": [
              {
                "startDate": "2025-05-23",
                "endDate": "2025-05-27",
                "tenor": "ON",
                "outright": {
                  "bid": 162.79586525762826,
                  "ask": 162.8566343562079,
                  "mid": 162.8262498069181
                },
                "instruments": [
                  {
                    "instrumentCode": "JPONMU=RR"
                  },
                  {
                    "instrumentCode": "USDOND="
                  },
                  {
                    "ins...

        """

        try:
            logger.info("Calling calculate for fxForwardCurve with id")
            check_id(self._id)

            response = Client().fx_forward_curve_resource.calculate(
                curve_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called calculate for fxForwardCurve with id")

            return output
        except Exception as err:
            logger.error("Error calculate for fxForwardCurve with id.")
            check_exception_and_raise(err, logger)

    def _create(self, location: Location) -> None:
        """
        Save a new FxForwardCurve in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the FxForwardCurve in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating FxForwardCurve")

            response = Client().fx_forward_curves_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"FxForwardCurve created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating FxForwardCurve:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a FxForwardCurve that exists in the platform. The FxForwardCurve can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting FxForwardCurve with id: {self._id}")
        Client().fx_forward_curve_resource.overwrite(
            curve_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save FxForwardCurve instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The FxForwardCurve name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the FxForwardCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>>
        >>> # Save the instance with name and space.
        >>> fx_curve.save(name="EURCHF_Fx_Forward_Curve", space="MYCURVE")
        True

        """
        try:
            logger.info("Saving FxForwardCurve")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("FxForwardCurve saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"FxForwardCurve saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("FxForwardCurve save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "FxForwardCurve":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        FxForwardCurve
            The cloned FxForwardCurve object


        Examples
        --------
        >>> # Clone the existing instance on definition and description.
        >>> fx_curve_clone = fx_curve.clone()
        >>> fx_curve_clone.save(name="my_cloned_curve", space="HOME")
        >>>
        >>> print(f"Curve id: {fx_curve.id}")
        >>> print(f"Cloned curve id: {fx_curve_clone.id}")
        >>> fx_curve_clone = fx_curve.clone()
        >>> fx_curve_clone.save(name="my_cloned_curve", space="HOME")
        >>>
        >>> print(f"Curve id: {fx_curve.id}")
        >>> print(f"Cloned curve id: {fx_curve_clone.id}")
        Curve id: 194fbcb0-868f-4129-bc5d-556b49b18cce
        Cloned curve id: 125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR
        Curve id: 194fbcb0-868f-4129-bc5d-556b49b18cce
        Cloned curve id: 125B1CUR-6EE9-4B1F-870F-5BA89EBE71CR

        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
