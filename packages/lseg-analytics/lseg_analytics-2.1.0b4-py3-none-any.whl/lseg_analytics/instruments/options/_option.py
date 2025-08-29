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
    AsianOtcOptionOverride,
    Description,
    DoubleBarrierOtcOptionOverride,
    DoubleBinaryOtcOptionOverride,
    Location,
    MarketData,
    OptionDefinition,
    OptionDefinitionInstrument,
    OptionInfo,
    OptionPricingParameters,
    OptionSolveResponseFieldsOnResourceResponseData,
    OptionSolveResponseFieldsResponseData,
    OptionValuationResponseFieldsOnResourceResponseData,
    OptionValuationResponseFieldsResponseData,
    ResourceType,
    SingleBarrierOtcOptionOverride,
    SingleBinaryOtcOptionOverride,
    SortingOrderEnum,
    VanillaOtcOptionOverride,
)

from ._logger import logger


class Option(ResourceBase):
    """
    Option object.

    Contains all the necessary information to identify and define a Option instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the Option.
    location : Location
        Object defining the location of the Option in the platform.
    description : Description, optional
        Object defining metadata for the Option.
    definition : OptionDefinition
        Object defining the Option.

    See Also
    --------
    Option.solve : Calculate the solvable properties of an Option provided in the request so that a chosen property equals a target value.
    Option.value : Calculate the market value of a option stored on the platform.

    Examples
    --------


    """

    _definition_class = OptionDefinition

    def __init__(self, definition: OptionDefinition, description: Optional[Description] = None):
        """
        Option constructor

        Parameters
        ----------
        definition : OptionDefinition
            Object defining the Option.
        description : Description, optional
            Object defining metadata for the Option.

        Examples
        --------


        """
        self.definition: OptionDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "Option"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the Option id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the Option.

        Examples
        --------


        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the Option location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the Option in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new Option in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the Option in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating Option")

            response = Client().options_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"Option created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating Option:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a Option that exists in the platform. The Option can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting Option with id: {self._id}")
        Client().option_resource.overwrite(
            instrument_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def solve(
        self,
        *,
        pricing_preferences: Optional[OptionPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> OptionSolveResponseFieldsOnResourceResponseData:
        """
        Calculate the solvable properties of an Option provided in the request so that a chosen property equals a target value.

        Parameters
        ----------
        pricing_preferences : OptionPricingParameters, optional
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
        OptionSolveResponseFieldsOnResourceResponseData


        Examples
        --------


        """

        try:
            logger.info("Calling solve for option with id")
            check_id(self._id)

            response = Client().option_resource.solve(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called solve for option with id")

            return output
        except Exception as err:
            logger.error("Error solve for option with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[OptionPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> OptionValuationResponseFieldsOnResourceResponseData:
        """
        Calculate the market value of a option stored on the platform.

        Parameters
        ----------
        pricing_preferences : OptionPricingParameters, optional
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
        OptionValuationResponseFieldsOnResourceResponseData


        Examples
        --------


        """

        try:
            logger.info("Calling value for option with id")
            check_id(self._id)

            response = Client().option_resource.value(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called value for option with id")

            return output
        except Exception as err:
            logger.error("Error value for option with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save Option instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The Option name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the Option is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------


        """
        try:
            logger.info("Saving Option")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("Option saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"Option saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("Option save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "Option":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        Option
            The cloned Option object


        Examples
        --------


        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
