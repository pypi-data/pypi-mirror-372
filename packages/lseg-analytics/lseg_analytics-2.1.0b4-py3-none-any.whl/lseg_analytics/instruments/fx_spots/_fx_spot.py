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
    FxPricingParameters,
    FxSpotAnalyticsPricingOnResourceResponseData,
    FxSpotAnalyticsPricingResponseData,
    FxSpotAnalyticsValuationOnResourceResponseData,
    FxSpotAnalyticsValuationResponseData,
    FxSpotDefinition,
    FxSpotDefinitionInstrument,
    FxSpotInfo,
    FxSpotOverride,
    Location,
    MarketData,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class FxSpot(ResourceBase):
    """
    FxSpot object.

    Contains all the necessary information to identify and define a FxSpot instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the FxSpot.
    location : Location
        Object defining the location of the FxSpot in the platform.
    description : Description, optional
        Object defining metadata for the FxSpot.
    definition : FxSpotDefinition
        Object defining the FxSpot.

    See Also
    --------
    FxSpot.price : Pricing a FxForward existing on the platform (FxSpot must be saved or loaded beforehand).
    FxSpot.value : Valuing a FxForward existing on the platform (FxSpot must be saved or loaded beforehand).

    Examples
    --------
    >>> # Create a FxSpot instance.
    >>> fx_spot = FxSpot(FxSpotDefinition(quoted_currency="EUR", base_currency="CHF", payer=PartyEnum.PARTY1, receiver=PartyEnum.PARTY2))


    >>> # Save the instance with name and space.
    >>> fx_spot.save(name="MyFxSpot", space="HOME")
    True

    """

    _definition_class = FxSpotDefinition

    def __init__(self, definition: FxSpotDefinition, description: Optional[Description] = None):
        """
        FxSpot constructor

        Parameters
        ----------
        definition : FxSpotDefinition
            Object defining the FxSpot.
        description : Description, optional
            Object defining metadata for the FxSpot.

        Examples
        --------
        >>> # Create a FxSpot instance.
        >>> fx_spot = FxSpot(FxSpotDefinition(quoted_currency="EUR", base_currency="CHF", payer=PartyEnum.PARTY1, receiver=PartyEnum.PARTY2))

        """
        self.definition: FxSpotDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "FxSpot"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the FxSpot id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the FxSpot.

        Examples
        --------
        >>> # Get the instance id.
        >>> fx_spot.id
        '1f009c8a-6a48-4b06-9e94-656d0cef8250'

        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the FxSpot location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the FxSpot in the platform.

        Examples
        --------
        >>> # Get the location property.
        >>> fx_spot.location.name
        'MyFxSpot'


        >>> fx_spot.location.space
        'HOME'

        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new FxSpot in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the FxSpot in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating FxSpot")

            response = Client().fx_spots_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"FxSpot created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating FxSpot:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a FxSpot that exists in the platform. The FxSpot can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting FxSpot with id: {self._id}")
        Client().fx_spot_resource.overwrite(
            instrument_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def price(
        self,
        *,
        pricing_preferences: Optional[FxPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> FxSpotAnalyticsPricingOnResourceResponseData:
        """
        Pricing a FxForward existing on the platform (FxSpot must be saved or loaded beforehand).

        Parameters
        ----------
        pricing_preferences : FxPricingParameters, optional
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
        FxSpotAnalyticsPricingOnResourceResponseData


        Examples
        --------
        >>> # Calling price on a FxSpot instance
        >>> fx_spot.price()
        {'resource': {'type': 'FxSpot', 'id': 'b1ce5a63-3800-4d83-bdd5-676563bd7729', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'TestFXSpots_2EJVer', 'space': 'TestSpace'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2024-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2024-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'analytics': {'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}], 'fxCrossCode': 'EURUSD'}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}


        >>> # Calling price on a FxSpot instance with parameters.
        >>> fx_spot = FxSpot(
        >>>     FxSpotDefinition(quoted_currency="EUR", base_currency="CHF", payer=PartyEnum.PARTY1, receiver=PartyEnum.PARTY2)
        >>> )
        >>>
        >>> fx_spot.save(name="EURCHF", space="MYSPACE")
        >>>
        >>> fx_spot.price(
        >>>     pricing_preferences=FxPricingParameters(
        >>>         ignore_reference_currency_holidays=True,
        >>>         reference_currency="USD",
        >>>         report_currency="USD",
        >>>         valuation_date="2024-01-11",
        >>>     ),
        >>>     market_data=MarketData(fx_forward_curves=[FxForwardCurveChoice(reference="LSEG/EUR_CHF_FxForward")]),
        >>> )
        {'resource': {'type': 'FxSpot', 'id': 'b1ce5a63-3800-4d83-bdd5-676563bd7729', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'TestFXSpots_2EJVer', 'space': 'TestSpace'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2024-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2024-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}, 'payer': 'Party1', 'receiver': 'Party1'}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'analytics': {'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}], 'fxCrossCode': 'EURUSD'}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}

        """

        try:
            logger.info("Calling price for fxSpot with id")
            check_id(self._id)

            response = Client().fx_spot_resource.price(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called price for fxSpot with id")

            return output
        except Exception as err:
            logger.error("Error price for fxSpot with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[FxPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> FxSpotAnalyticsValuationOnResourceResponseData:
        """
        Valuing a FxForward existing on the platform (FxSpot must be saved or loaded beforehand).

        Parameters
        ----------
        pricing_preferences : FxPricingParameters, optional
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
        FxSpotAnalyticsValuationOnResourceResponseData


        Examples
        --------
        >>> # Calling value on a FxSpot.
        >>> fx_spot.value()
        {'resource': {'type': 'FxSpot', 'id': 'b1ce5a63-3800-4d83-bdd5-676563bd7729', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'TestFXSpots_2EJVer', 'space': 'TestSpace'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2024-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2024-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 596873.601432359, 'marketValueInReportCcy': 543893.314580022, 'marketValueInDealCcy': 543893.314580022}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}


        >>> # Calling value on a FxSpot instance with parameters.
        >>> fx_spot = FxSpot(
        >>>     FxSpotDefinition(quoted_currency="EUR", base_currency="CHF", payer=PartyEnum.PARTY1, receiver=PartyEnum.PARTY2)
        >>> )
        >>>
        >>> fx_spot.save(name="EURCHF", space="MYSPACE")
        >>>
        >>> fx_spot.value(
        >>>     pricing_preferences=FxPricingParameters(
        >>>         ignore_reference_currency_holidays=True,
        >>>         reference_currency="USD",
        >>>         report_currency="USD",
        >>>         valuation_date="2024-01-11",
        >>>     ),
        >>>     market_data=MarketData(fx_forward_curves=[FxForwardCurveChoice(reference="LSEG/EUR_CHF_FxForward")]),
        >>> )
        {'resource': {'type': 'FxSpot', 'id': 'b1ce5a63-3800-4d83-bdd5-676563bd7729', 'description': {'tags': ['Test'], 'summary': 'Some summary'}, 'location': {'name': 'TestFXSpots_2EJVer', 'space': 'TestSpace'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2024-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2024-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'unAdjusted': '2024-01-16', 'adjusted': '2024-01-16', 'dateMovingConvention': 'NextBusinessDay', 'referenceDate': 'SpotDate', 'tenor': '0D'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 596873.601432359, 'marketValueInReportCcy': 543893.314580022, 'marketValueInDealCcy': 543893.314580022}, 'greeks': {'deltaPercent': 45.570543200875, 'deltaAmountInDealCcy': 455705.43200875, 'deltaAmountInContraCcy': 1000000}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}

        """

        try:
            logger.info("Calling value for fxSpot with id")
            check_id(self._id)

            response = Client().fx_spot_resource.value(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called value for fxSpot with id")

            return output
        except Exception as err:
            logger.error("Error value for fxSpot with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save FxSpot instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The FxSpot name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the FxSpot is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # Save the instance with name and space.
        >>> fx_spot.save(name="MyFxSpot", space="HOME")
        True

        """
        try:
            logger.info("Saving FxSpot")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("FxSpot saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"FxSpot saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("FxSpot save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "FxSpot":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        FxSpot
            The cloned FxSpot object


        Examples
        --------
        >>> # Clone the existing instance on definition and description.
        >>> fx_spot_clone = fx_spot.clone()

        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
