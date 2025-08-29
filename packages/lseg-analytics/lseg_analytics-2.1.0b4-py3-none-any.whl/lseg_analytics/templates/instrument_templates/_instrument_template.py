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
    InstrumentTemplateDefinition,
    InstrumentTemplateInfo,
    Location,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class InstrumentTemplate(ResourceBase):
    """
    InstrumentTemplate object.

    Contains all the necessary information to identify and define a InstrumentTemplate instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the InstrumentTemplate.
    location : Location
        Object defining the location of the InstrumentTemplate in the platform.
    description : Description, optional
        Object defining metadata for the InstrumentTemplate.
    definition : InstrumentTemplateDefinition
        Object defining the InstrumentTemplate.

    See Also
    --------


    Examples
    --------


    """

    _definition_class = InstrumentTemplateDefinition

    def __init__(
        self,
        definition: InstrumentTemplateDefinition,
        description: Optional[Description] = None,
    ):
        """
        InstrumentTemplate constructor

        Parameters
        ----------
        definition : InstrumentTemplateDefinition
            Object defining the InstrumentTemplate.
        description : Description, optional
            Object defining metadata for the InstrumentTemplate.

        Examples
        --------


        """
        self.definition: InstrumentTemplateDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "InstrumentTemplate"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the InstrumentTemplate id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the InstrumentTemplate.

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
        Returns the InstrumentTemplate location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the InstrumentTemplate in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new InstrumentTemplate in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the InstrumentTemplate in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating InstrumentTemplate")

            response = Client().instrument_templates_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"InstrumentTemplate created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating InstrumentTemplate:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a InstrumentTemplate that exists in the platform. The InstrumentTemplate can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting InstrumentTemplate with id: {self._id}")
        Client().instrument_template_resource.overwrite(
            template_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save InstrumentTemplate instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The InstrumentTemplate name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the InstrumentTemplate is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------


        """
        try:
            logger.info("Saving InstrumentTemplate")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("InstrumentTemplate saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"InstrumentTemplate saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("InstrumentTemplate save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "InstrumentTemplate":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        InstrumentTemplate
            The cloned InstrumentTemplate object


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
