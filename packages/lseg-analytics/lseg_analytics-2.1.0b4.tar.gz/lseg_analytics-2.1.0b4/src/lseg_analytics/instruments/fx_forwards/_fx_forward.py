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
    FxForwardAnalyticsPricingOnResourceResponseData,
    FxForwardAnalyticsPricingResponseData,
    FxForwardAnalyticsValuationOnResourceResponseData,
    FxForwardAnalyticsValuationResponseData,
    FxForwardDefinition,
    FxForwardDefinitionInstrument,
    FxForwardInfo,
    FxForwardOverride,
    FxPricingParameters,
    Location,
    MarketData,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class FxForward(ResourceBase):
    """
    FxForward object.

    Contains all the necessary information to identify and define a FxForward instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the FxForward.
    location : Location
        Object defining the location of the FxForward in the platform.
    description : Description, optional
        Object defining metadata for the FxForward.
    definition : FxForwardDefinition
        Object defining the FxForward.

    See Also
    --------
    FxForward.price : Pricing a FxForward existing in the platform (FxForward must be saved or loaded beforehand). Currently, only NextBusinessDay is supported for the date moving convention in the start date or end date.
    FxForward.value : Valuing a FxForward existing in the platform (FxForward must be saved or loaded beforehand). Currently, only NextBusinessDay is supported for the date moving convention in the start date or end date.

    Examples
    --------
    >>> # Create a FxForward instance.
    >>> fx_forward = FxForward(
    >>>     FxForwardDefinition(
    >>>         quoted_currency="EUR",
    >>>         base_currency="CHF",
    >>>         payer=PartyEnum.PARTY1,
    >>>         receiver=PartyEnum.PARTY2,
    >>>         rate=FxRate(value=1.10, rate_precision=2),
    >>>         start_date=AdjustableDate(
    >>>             date=datetime.date(2022, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>         end_date=AdjustableDate(
    >>>             date=datetime.date(2023, 12, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
    >>>         ),
    >>>     )
    >>> )


    >>> # Save the instance with name and space.
    >>> fx_forward.save(name="EURCHF", space="MYSPACE")
    True

    """

    _definition_class = FxForwardDefinition

    def __init__(self, definition: FxForwardDefinition, description: Optional[Description] = None):
        """
        FxForward constructor

        Parameters
        ----------
        definition : FxForwardDefinition
            Object defining the FxForward.
        description : Description, optional
            Object defining metadata for the FxForward.

        Examples
        --------
        >>> # Create a FxForward instance.
        >>> fx_forward = FxForward(
        >>>     FxForwardDefinition(
        >>>         quoted_currency="EUR",
        >>>         base_currency="CHF",
        >>>         payer=PartyEnum.PARTY1,
        >>>         receiver=PartyEnum.PARTY2,
        >>>         rate=FxRate(value=1.10, rate_precision=2),
        >>>         start_date=AdjustableDate(
        >>>             date=datetime.date(2022, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>         end_date=AdjustableDate(
        >>>             date=datetime.date(2023, 12, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>     )
        >>> )

        """
        self.definition: FxForwardDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "FxForward"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the FxForward id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the FxForward.

        Examples
        --------
        >>> # Get the instance id.
        >>> fx_forward.id
        'c37f18fc-95ab-45f2-9b50-313bc4f2bcd8'

        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the FxForward location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the FxForward in the platform.

        Examples
        --------
        >>> # Get the location property.
        >>> fx_forward.location.name
        'EURCHF'


        >>> fx_forward.location.space
        'MYSPACE'

        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new FxForward in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the FxForward in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating FxForward")

            response = Client().fx_forwards_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"FxForward created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating FxForward:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a FxForward that exists in the platform. The FxForward can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting FxForward with id: {self._id}")
        Client().fx_forward_resource.overwrite(
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
    ) -> FxForwardAnalyticsPricingOnResourceResponseData:
        """
        Pricing a FxForward existing in the platform (FxForward must be saved or loaded beforehand). Currently, only NextBusinessDay is supported for the date moving convention in the start date or end date.

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
        FxForwardAnalyticsPricingOnResourceResponseData


        Examples
        --------
        >>> # Calling price on a FxForward instance
        >>> fx_forward.price()
        {'resource': {'type': 'FxForward', 'id': 'a4bf03a9-7924-4e9b-91d2-1e353d524b54', 'description': {'tags': ['string'], 'summary': 'string'}, 'location': {'name': 'Test', 'space': 'HOME'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2025-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'settlementType': 'Physical', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2025-01-01', 'adjusted': '2025-01-02', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-01-01'}, 'endDate': {'unAdjusted': '2025-12-31', 'adjusted': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-12-31'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSwapsCcy1': {'bid': 0, 'ask': 0}, 'fxSwapsCcy2': {'bid': -135.0187047433792, 'ask': -129.13121827673604}, 'fxSwapsCcy1Ccy2': {'bid': 162.23105305305907, 'ask': 170.01029230246934}, 'fxOutrightCcy1Ccy2': {'bid': 1.129417564643121, 'ask': 1.1302655927426335}, 'rate': 0.5, 'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 42.7681916939807, 'deltaAmountInDealCcy': 427681.916939807, 'deltaAmountInContraCcy': 966425.624427335}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}


        >>> # Calling price on a FxForward instance with parameters, using an existing LSEG curve.
        >>> fx_forward = FxForward(
        >>>     FxForwardDefinition(
        >>>         quoted_currency="EUR",
        >>>         base_currency="CHF",
        >>>         payer=PartyEnum.PARTY1,
        >>>         receiver=PartyEnum.PARTY2,
        >>>         rate=FxRate(value=1.10, rate_precision=2),
        >>>         start_date=AdjustableDate(
        >>>             date=datetime.date(2022, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>         end_date=AdjustableDate(
        >>>             date=datetime.date(2023, 12, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> fx_forward.save(name="EURCHF", space="MYSPACE")
        >>>
        >>> fx_forward.price(
        >>>     pricing_preferences=FxPricingParameters(
        >>>         ignore_reference_currency_holidays=True,
        >>>         reference_currency="USD",
        >>>         report_currency="USD",
        >>>         valuation_date="2024-01-11",
        >>>     ),
        >>>     market_data=MarketData(fx_forward_curves=[FxForwardCurveChoice(reference="LSEG/EUR_CHF_FxForward")]),
        >>> )
        {'resource': {'type': 'FxForward', 'id': 'a4bf03a9-7924-4e9b-91d2-1e353d524b54', 'description': {'tags': ['string'], 'summary': 'string'}, 'location': {'name': 'Test', 'space': 'HOME'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2025-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'settlementType': 'Physical', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2025-01-01', 'adjusted': '2025-01-02', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-01-01'}, 'endDate': {'unAdjusted': '2025-12-31', 'adjusted': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-12-31'}, 'valuationDate': '2024-01-11'}, 'pricingAnalysis': {'fxSwapsCcy1': {'bid': 0, 'ask': 0}, 'fxSwapsCcy2': {'bid': -135.0187047433792, 'ask': -129.13121827673604}, 'fxSwapsCcy1Ccy2': {'bid': 162.23105305305907, 'ask': 170.01029230246934}, 'fxOutrightCcy1Ccy2': {'bid': 1.129417564643121, 'ask': 1.1302655927426335}, 'rate': 0.5, 'fxSpot': {'bid': 1.097, 'ask': 1.0974}, 'dealAmount': 1000000, 'contraAmount': 500000}, 'greeks': {'deltaPercent': 42.7681916939807, 'deltaAmountInDealCcy': 427681.916939807, 'deltaAmountInContraCcy': 966425.624427335}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [], 'fxCrossCode': 'USDEUR'}}]}}

        """

        try:
            logger.info("Calling price for fxForward with id")
            check_id(self._id)

            response = Client().fx_forward_resource.price(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called price for fxForward with id")

            return output
        except Exception as err:
            logger.error("Error price for fxForward with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[FxPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> FxForwardAnalyticsValuationOnResourceResponseData:
        """
        Valuing a FxForward existing in the platform (FxForward must be saved or loaded beforehand). Currently, only NextBusinessDay is supported for the date moving convention in the start date or end date.

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
        FxForwardAnalyticsValuationOnResourceResponseData


        Examples
        --------
        >>> # Calling value on a FxForward instance
        >>> fx_forward.value()
        {'resource': {'type': 'FxForward', 'id': 'a4bf03a9-7924-4e9b-91d2-1e353d524b54', 'description': {'tags': ['string'], 'summary': 'string'}, 'location': {'name': 'Test', 'space': 'HOME'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2025-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'settlementType': 'Physical', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2025-01-01', 'adjusted': '2025-01-02', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-01-01'}, 'endDate': {'unAdjusted': '2025-12-31', 'adjusted': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-12-31'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 594260.839617766, 'marketValueInReportCcy': 514407.470653874, 'discountFactor': 0.966425624427335, 'marketValueInDealCcy': 514407.470653874}, 'greeks': {'deltaPercent': 42.7681916939807, 'deltaAmountInDealCcy': 427681.916939807, 'deltaAmountInContraCcy': 966425.624427335}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}


        >>> # Calling value on a FxForward instance with parameters, using a definition of a pre-loaded curve.
        >>> fx_forward = FxForward(
        >>>     FxForwardDefinition(
        >>>         quoted_currency="EUR",
        >>>         base_currency="CHF",
        >>>         payer=PartyEnum.PARTY1,
        >>>         receiver=PartyEnum.PARTY2,
        >>>         rate=FxRate(value=1.10, rate_precision=2),
        >>>         start_date=AdjustableDate(
        >>>             date=datetime.date(2022, 1, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>         end_date=AdjustableDate(
        >>>             date=datetime.date(2023, 12, 1), date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> fx_forward.save(name="EURCHF", space="MYSPACE")
        >>>
        >>> fx_forward.value(
        >>>     pricing_preferences=FxPricingParameters(
        >>>         ignore_reference_currency_holidays=True,
        >>>         reference_currency="USD",
        >>>         report_currency="USD",
        >>>         valuation_date="2024-01-11",
        >>>     ),
        >>>     market_data=MarketData(fx_forward_curves=[FxForwardCurveChoice(reference="LSEG/EUR_CHF_FxForward")]),
        >>> )
        {'resource': {'type': 'FxForward', 'id': 'a4bf03a9-7924-4e9b-91d2-1e353d524b54', 'description': {'tags': ['string'], 'summary': 'string'}, 'location': {'name': 'Test', 'space': 'HOME'}, 'definition': {'startDate': {'dateType': 'AdjustableDate', 'date': '2025-01-01', 'dateMovingConvention': 'NextBusinessDay'}, 'endDate': {'dateType': 'AdjustableDate', 'date': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay'}, 'quotedCurrency': 'EUR', 'baseCurrency': 'USD', 'payer': 'Party1', 'receiver': 'Party1', 'settlementType': 'Physical', 'dealAmount': 1000000.1, 'rate': {'value': 0.5, 'scalingFactor': 1, 'ratePrecision': 4}}}, 'analytics': {'description': {'startDate': {'unAdjusted': '2025-01-01', 'adjusted': '2025-01-02', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-01-01'}, 'endDate': {'unAdjusted': '2025-12-31', 'adjusted': '2025-12-31', 'dateMovingConvention': 'NextBusinessDay', 'date': '2025-12-31'}, 'valuationDate': '2024-01-11'}, 'valuation': {'marketValueInContraCcy': 594260.839617766, 'marketValueInReportCcy': 514407.470653874, 'discountFactor': 0.966425624427335, 'marketValueInDealCcy': 514407.470653874}, 'greeks': {'deltaPercent': 42.7681916939807, 'deltaAmountInDealCcy': 427681.916939807, 'deltaAmountInContraCcy': 966425.624427335}}, 'pricingPreferences': {'ignoreReferenceCurrencyHolidays': True, 'referenceCurrency': 'USD', 'valuationDate': '2024-01-11', 'reportCurrency': 'USD'}, 'marketData': {'fxForwardCurves': [{'curve': {'fxType': 'Outright', 'fxCrossCode': 'EURUSD', 'points': [{'value': 0.9115906876315911, 'date': '2024-01-12'}, {'value': 0.9115552049551991, 'date': '2024-01-16'}, {'value': 0.911374512869765, 'date': '2024-01-17'}, {'value': 0.9111567832996935, 'date': '2024-01-23'}, {'value': 0.9109044687788547, 'date': '2024-01-30'}, {'value': 0.9106464970455429, 'date': '2024-02-06'}, {'value': 0.9102834202202881, 'date': '2024-02-16'}, {'value': 0.9091368121542458, 'date': '2024-03-18'}, {'value': 0.908087929694051, 'date': '2024-04-16'}, {'value': 0.9070048652092904, 'date': '2024-05-16'}, {'value': 0.9059424145590768, 'date': '2024-06-17'}, {'value': 0.904911939852928, 'date': '2024-07-16'}, {'value': 0.9036240342503064, 'date': '2024-08-16'}, {'value': 0.9025197984674378, 'date': '2024-09-16'}, {'value': 0.9015060829422432, 'date': '2024-10-16'}, {'value': 0.9001022272276912, 'date': '2024-11-18'}, {'value': 0.8990760694621955, 'date': '2024-12-16'}, {'value': 0.8976380124189622, 'date': '2025-01-16'}, {'value': 0.8942113912123242, 'date': '2025-04-16'}, {'value': 0.8910435800687821, 'date': '2025-07-16'}, {'value': 0.8878945888535744, 'date': '2025-10-16'}, {'value': 0.884487408232818, 'date': '2026-01-16'}, {'value': 0.8738901591852978, 'date': '2027-01-19'}, {'value': 0.8625526727180695, 'date': '2028-01-18'}, {'value': 0.8516033523308432, 'date': '2029-01-16'}, {'value': 0.8402686622956788, 'date': '2030-01-16'}, {'value': 0.8299485612360556, 'date': '2031-01-16'}, {'value': 0.8197783893419468, 'date': '2032-01-16'}, {'value': 0.8099854502443474, 'date': '2033-01-18'}, {'value': 0.8010012499584567, 'date': '2034-01-17'}, {'value': 0.8010012499584567, 'date': '2036-01-16'}, {'value': 0.8010012499584567, 'date': '2039-01-18'}, {'value': 0.8010012499584567, 'date': '2044-01-19'}, {'value': 0.8010012499584567, 'date': '2049-01-19'}, {'value': 0.8010012499584567, 'date': '2054-01-16'}, {'value': 0.8010012499584567, 'date': '2064-01-16'}, {'value': 0.8010012499584567, 'date': '2074-01-16'}]}}, {'curve': {'fxType': 'Outright', 'points': [{'value': 1.0969836, 'date': '2024-01-12'}, {'value': 1.0970263, 'date': '2024-01-16'}, {'value': 1.0972438, 'date': '2024-01-17'}, {'value': 1.097506, 'date': '2024-01-23'}, {'value': 1.09781, 'date': '2024-01-30'}, {'value': 1.098121, 'date': '2024-02-06'}, {'value': 1.0985589999999998, 'date': '2024-02-16'}, {'value': 1.0999444999999999, 'date': '2024-03-18'}, {'value': 1.1012149999999998, 'date': '2024-04-16'}, {'value': 1.10253, 'date': '2024-05-16'}, {'value': 1.103823, 'date': '2024-06-17'}, {'value': 1.10508, 'date': '2024-07-16'}, {'value': 1.106655, 'date': '2024-08-16'}, {'value': 1.108009, 'date': '2024-09-16'}, {'value': 1.1092549999999999, 'date': '2024-10-16'}, {'value': 1.110985, 'date': '2024-11-18'}, {'value': 1.112253, 'date': '2024-12-16'}, {'value': 1.1140349999999999, 'date': '2025-01-16'}, {'value': 1.1183044999999998, 'date': '2025-04-16'}, {'value': 1.12228, 'date': '2025-07-16'}, {'value': 1.1262599999999998, 'date': '2025-10-16'}, {'value': 1.1305985, 'date': '2026-01-16'}, {'value': 1.1443115000000001, 'date': '2027-01-19'}, {'value': 1.1593499999999999, 'date': '2028-01-18'}, {'value': 1.174259, 'date': '2029-01-16'}, {'value': 1.1901, 'date': '2030-01-16'}, {'value': 1.2048999999999999, 'date': '2031-01-16'}, {'value': 1.2198499999999999, 'date': '2032-01-16'}, {'value': 1.2346, 'date': '2033-01-18'}, {'value': 1.24845, 'date': '2034-01-17'}, {'value': 1.24845, 'date': '2036-01-16'}, {'value': 1.24845, 'date': '2039-01-18'}, {'value': 1.24845, 'date': '2044-01-19'}, {'value': 1.24845, 'date': '2049-01-19'}, {'value': 1.24845, 'date': '2054-01-16'}, {'value': 1.24845, 'date': '2064-01-16'}, {'value': 1.24845, 'date': '2074-01-16'}], 'fxCrossCode': 'USDEUR'}}]}}

        """

        try:
            logger.info("Calling value for fxForward with id")
            check_id(self._id)

            response = Client().fx_forward_resource.value(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called value for fxForward with id")

            return output
        except Exception as err:
            logger.error("Error value for fxForward with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save FxForward instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The FxForward name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the FxForward is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # Save the instance with name and space.
        >>> fx_forward.save(name="EURCHF", space="MYSPACE")
        True

        """
        try:
            logger.info("Saving FxForward")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("FxForward saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"FxForward saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("FxForward save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "FxForward":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        FxForward
            The cloned FxForward object


        Examples
        --------
        >>> # Clone the existing instance on definition and description.
        >>> fx_forward_clone = fx_forward.clone()

        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
