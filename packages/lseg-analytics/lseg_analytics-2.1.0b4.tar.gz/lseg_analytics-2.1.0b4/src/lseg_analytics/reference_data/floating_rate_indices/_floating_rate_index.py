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
    FloatingRateIndexDefinition,
    FloatingRateIndexInfo,
    Location,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class FloatingRateIndex(ResourceBase):
    """
    FloatingRateIndex object.

    Contains all the necessary information to identify and define a FloatingRateIndex instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the FloatingRateIndex.
    location : Location
        Object defining the location of the FloatingRateIndex in the platform.
    description : Description, optional
        Object defining metadata for the FloatingRateIndex.
    definition : FloatingRateIndexDefinition
        Object defining the FloatingRateIndex.

    See Also
    --------


    Examples
    --------
    >>> rounding=RoundingDefinition(
    >>>     decimal_places=0,
    >>>     scale=1
    >>> )
    >>>
    >>> quote_definition = QuoteDefinition(
    >>>     instrument_code="EUROSTR="
    >>> )
    >>>
    >>> index_definition = FloatingRateIndexDefinition(
    >>>     currency='EUR',
    >>>     name='New_EUR_3M_FR',
    >>>     tenor='3M',
    >>>     year_basis='YB_360',
    >>>     rounding=rounding,
    >>>     quote_definition=quote_definition)
    >>>
    >>> index_description=Description(summary="User defined EUR 3M Floating Rate Index", tags=["EUR"])
    >>>
    >>> user_defined_index = FloatingRateIndex(definition=index_definition, description=index_description)
    >>>
    >>> print(user_defined_index.definition)
    {'currency': 'EUR', 'name': 'New_EUR_3M_FR', 'tenor': '3M', 'yearBasis': 'YB_360', 'rounding': {'decimalPlaces': 0, 'scale': 1}, 'quoteDefinition': {'instrumentCode': 'EUROSTR='}}

    """

    _definition_class = FloatingRateIndexDefinition

    def __init__(
        self,
        definition: FloatingRateIndexDefinition,
        description: Optional[Description] = None,
    ):
        """
        FloatingRateIndex constructor

        Parameters
        ----------
        definition : FloatingRateIndexDefinition
            Object defining the FloatingRateIndex.
        description : Description, optional
            Object defining metadata for the FloatingRateIndex.

        Examples
        --------
        >>> rounding=RoundingDefinition(
        >>>     decimal_places=0,
        >>>     scale=1
        >>> )
        >>>
        >>> quote_definition = QuoteDefinition(
        >>>     instrument_code="EUROSTR="
        >>> )
        >>>
        >>> index_definition = FloatingRateIndexDefinition(
        >>>     currency='EUR',
        >>>     name='New_EUR_3M_FR',
        >>>     tenor='3M',
        >>>     year_basis='YB_360',
        >>>     rounding=rounding,
        >>>     quote_definition=quote_definition)
        >>>
        >>> index_description=Description(summary="User defined EUR 3M Floating Rate Index", tags=["EUR"])
        >>>
        >>> user_defined_index = FloatingRateIndex(definition=index_definition, description=index_description)
        >>>
        >>> print(user_defined_index.definition)
        {'currency': 'EUR', 'name': 'New_EUR_3M_FR', 'tenor': '3M', 'yearBasis': 'YB_360', 'rounding': {'decimalPlaces': 0, 'scale': 1}, 'quoteDefinition': {'instrumentCode': 'EUROSTR='}}

        """
        self.definition: FloatingRateIndexDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "FloatingRateIndex"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the FloatingRateIndex id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the FloatingRateIndex.

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
        Returns the FloatingRateIndex location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the FloatingRateIndex in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new FloatingRateIndex in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the FloatingRateIndex in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating FloatingRateIndex")

            response = Client().floating_rate_indices_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"FloatingRateIndex created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating FloatingRateIndex:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a FloatingRateIndex that exists in the platform. The FloatingRateIndex can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting FloatingRateIndex with id: {self._id}")
        Client().floating_rate_index_resource.overwrite(
            floating_rate_index_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save FloatingRateIndex instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The FloatingRateIndex name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the FloatingRateIndex is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # Save the index to a user space
        >>> user_defined_index.save(name="User_EUR_3M_Index", space="HOME")
        True

        """
        try:
            logger.info("Saving FloatingRateIndex")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("FloatingRateIndex saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"FloatingRateIndex saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("FloatingRateIndex save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "FloatingRateIndex":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        FloatingRateIndex
            The cloned FloatingRateIndex object


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
