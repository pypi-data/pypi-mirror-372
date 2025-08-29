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
    IrPricingParameters,
    LoanAsCollectionItem,
    LoanDefinition,
    LoanDefinitionInstrument,
    LoanInstrumentSolveResponseFieldsOnResourceResponseData,
    LoanInstrumentSolveResponseFieldsResponseData,
    LoanInstrumentValuationResponseFieldsOnResourceResponseData,
    LoanInstrumentValuationResponseFieldsResponseData,
    Location,
    MarketData,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class Loan(ResourceBase):
    """
    Loan object.

    Contains all the necessary information to identify and define a Loan instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the Loan.
    location : Location
        Object defining the location of the Loan in the platform.
    description : Description, optional
        Object defining metadata for the Loan.
    definition : LoanDefinition
        Object defining the Loan.

    See Also
    --------
    Loan.price : Calculate the price of a loan (i.e., its fixed rate) stored in the platform so that a chosen property (e.g., market value, duration) equals a target value.
    Loan.value : Calculate the market value of a loan stored in the platform.

    Examples
    --------


    """

    _definition_class = LoanDefinition

    def __init__(self, definition: LoanDefinition, description: Optional[Description] = None):
        """
        Loan constructor

        Parameters
        ----------
        definition : LoanDefinition
            Object defining the Loan.
        description : Description, optional
            Object defining metadata for the Loan.

        Examples
        --------


        """
        self.definition: LoanDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "Loan"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the Loan id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the Loan.

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
        Returns the Loan location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the Loan in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new Loan in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the Loan in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating Loan")

            response = Client().loans_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"Loan created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating Loan:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a Loan that exists in the platform. The Loan can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting Loan with id: {self._id}")
        Client().loan_resource.overwrite(
            instrument_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def price(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> LoanInstrumentSolveResponseFieldsOnResourceResponseData:
        """
        Calculate the price of a loan (i.e., its fixed rate) stored in the platform so that a chosen property (e.g., market value, duration) equals a target value.

        Parameters
        ----------
        pricing_preferences : IrPricingParameters, optional
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
        LoanInstrumentSolveResponseFieldsOnResourceResponseData


        Examples
        --------


        """

        try:
            logger.info("Calling price for loan with id")
            check_id(self._id)

            response = Client().loan_resource.price(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called price for loan with id")

            return output
        except Exception as err:
            logger.error("Error price for loan with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> LoanInstrumentValuationResponseFieldsOnResourceResponseData:
        """
        Calculate the market value of a loan stored in the platform.

        Parameters
        ----------
        pricing_preferences : IrPricingParameters, optional
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
        LoanInstrumentValuationResponseFieldsOnResourceResponseData


        Examples
        --------


        """

        try:
            logger.info("Calling value for loan with id")
            check_id(self._id)

            response = Client().loan_resource.value(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called value for loan with id")

            return output
        except Exception as err:
            logger.error("Error value for loan with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save Loan instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The Loan name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the Loan is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # Clone template to save original
        >>> cloned_template = loaded_template.clone()
        >>>
        >>> # Save the cloned template to a space
        >>> cloned_template.save(name='template_for_deletion', space='HOME')
        >>>
        >>> # Check that the loan with name 'template_for_deletion' exists
        >>> loan_templates = search()
        >>>
        >>> print(loan_templates)
        [{'type': 'Loan', 'id': '7caf85a5-7c3c-4ce8-b9f5-7db8918cb7a8', 'location': {'space': 'HOME', 'name': 'LoanResourceCreatd_For_Sdk_Notebooks'}, 'description': {'summary': '', 'tags': ['test']}}, {'type': 'Loan', 'id': '3a57e3ff-ec3c-4b60-99d1-4d60abb84e62', 'location': {'space': 'HOME', 'name': 'template_for_deletion'}, 'description': {'summary': '', 'tags': ['test']}}]

        """
        try:
            logger.info("Saving Loan")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("Loan saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"Loan saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("Loan save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "Loan":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        Loan
            The cloned Loan object


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
