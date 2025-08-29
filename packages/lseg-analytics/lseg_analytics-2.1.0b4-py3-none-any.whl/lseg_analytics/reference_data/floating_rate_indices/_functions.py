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
    FieldDefinition,
    FloatingRateIndexDefinition,
    FloatingRateIndexInfo,
    Location,
    QuoteDefinition,
    RoundingDefinition,
    RoundingModeEnum,
    SortingOrderEnum,
    YearBasisEnum,
)

from ._floating_rate_index import FloatingRateIndex
from ._logger import logger

__all__ = [
    "FloatingRateIndexDefinition",
    "FloatingRateIndexInfo",
    "RoundingDefinition",
    "RoundingModeEnum",
    "delete",
    "load",
    "search",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a FloatingRateIndex using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The FloatingRateIndex id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The FloatingRateIndex name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the FloatingRateIndex is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    FloatingRateIndex
        The FloatingRateIndex instance.

    Examples
    --------
    >>> # Load using template name
    >>> index_by_name = load(name = index_templates[0].location.name)
    >>>
    >>> print(index_by_name.definition)
    {'currency': 'EUR', 'name': 'ESTR', 'tenor': 'ON', 'yearBasis': 'YB_360', 'rounding': {'decimalPlaces': 0, 'scale': 1}, 'quoteDefinition': {'instrumentCode': 'EUROSTR= (overwritten)'}}


    >>> # Load using template id
    >>> index_by_id = load(resource_id = index_templates[0].id)
    >>>
    >>> print(index_by_id.definition)
    {'currency': 'EUR', 'name': 'ESTR', 'tenor': 'ON', 'yearBasis': 'YB_360', 'rounding': {'decimalPlaces': 0, 'scale': 1}, 'quoteDefinition': {'instrumentCode': 'EUROSTR= (overwritten)'}}

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load FloatingRateIndex {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FloatingRateIndex {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FloatingRateIndex not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    elif len(result) > 1:
        logger.warn(f"Found more than one result for name={name!r} and space={space!r}, returning the first one")
    return _load_by_id(result[0].id)


def delete(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Delete FloatingRateIndex instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The FloatingRateIndex resource ID.
        Required if name is not provided.
    name : str, optional
        The FloatingRateIndex name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the FloatingRateIndex is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    >>> # Delete the index from a user space
    >>> delete(name="User_EUR_3M_Index", space="HOME")
    True

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete FloatingRateIndex {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"FloatingRateIndex {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource FloatingRateIndex not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def _delete_by_id(floating_rate_index_id: str) -> bool:
    """
    Delete a FloatingRateIndex that exists in the platform. The FloatingRateIndex can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    floating_rate_index_id : str
        A sequence of textual characters.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting FloatingRateIndex with id: {floating_rate_index_id}")
        Client().floating_rate_index_resource.delete(floating_rate_index_id=floating_rate_index_id)
        logger.info(f"Deleted FloatingRateIndex with id: {floating_rate_index_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting FloatingRateIndex with id: {floating_rate_index_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(floating_rate_index_id: str, fields: Optional[str] = None) -> FloatingRateIndex:
    """
    Access a FloatingRateIndex existing in the platform (read). The FloatingRateIndex can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    floating_rate_index_id : str
        A sequence of textual characters.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    FloatingRateIndex


    Examples
    --------


    """

    try:
        logger.info(f"Opening FloatingRateIndex with id: {floating_rate_index_id}")

        response = Client().floating_rate_index_resource.read(
            floating_rate_index_id=floating_rate_index_id, fields=fields
        )

        output = FloatingRateIndex(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening FloatingRateIndex:")
        check_exception_and_raise(err, logger)


def search(
    *,
    item_per_page: Optional[int] = None,
    page: Optional[int] = None,
    spaces: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    space_name_sort_order: Optional[Union[str, SortingOrderEnum]] = None,
    tags: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> List[FloatingRateIndexInfo]:
    """
    List the FloatingRateIndexs existing in the platform (depending on permissions)

    Parameters
    ----------
    item_per_page : int, optional
        A parameter used to select the number of items allowed per page. The valid range is 1-500. If not provided, 50 will be used.
    page : int, optional
        A parameter used to define the page number to display.
    spaces : List[str], optional
        A parameter used to search for platform resources stored in a given space. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space.
        If space is not specified, it will search within all spaces.
    names : List[str], optional
        A parameter used to search for platform resources with given names.
    space_name_sort_order : Union[str, SortingOrderEnum], optional
        A parameter used to sort platform resources by name based on a defined order.
    tags : List[str], optional
        A parameter used to search for platform resources with given tags.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[FloatingRateIndexInfo]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------
    >>> # Full search with no filters
    >>> index_templates = search()
    >>>
    >>> print(index_templates[:5])
    [{'type': 'FloatingRateIndex', 'id': '4436d66b-addb-46a5-9f66-13bb946f150e', 'location': {'space': 'HOME', 'name': 'TestIrIndex'}, 'description': {'summary': 'EUROSTR (overwritten)', 'tags': ['Tests', 'EUR', 'ESTR', 'ON', 'RFTB']}}, {'type': 'FloatingRateIndex', 'id': 'c1051f64-fb15-4984-91fb-2c97e97ac7e3', 'location': {'space': 'HOME', 'name': 'TestRefFri17443031935839942'}, 'description': {'summary': 'Test description', 'tags': ['tag1', 'tag2']}}, {'type': 'FloatingRateIndex', 'id': 'f882ded9-13b9-4456-ab56-134d93cec3d4', 'location': {'space': 'LSEG', 'name': 'AED_AEIBOR_1M'}, 'description': {'summary': 'AED AEIBOR', 'tags': ['currency:AED', 'indexTenor:1M', 'sourceLongName:Refinitiv', 'sourceShortName:RFTB']}}, {'type': 'FloatingRateIndex', 'id': '7a102320-d152-4ebf-9fce-b4b254ddc471', 'location': {'space': 'LSEG', 'name': 'AED_AEIBOR_1Y'}, 'description': {'summary': 'AED AEIBOR', 'tags': ['currency:AED', 'indexTenor:1Y', 'sourceLongName:Refinitiv', 'sourceShortName:RFTB']}}, {'type': 'FloatingRateIndex', 'id': '3d8b26aa-940a-45d0-9756-6af902ce5738', 'location': {'space': 'LSEG', 'name': 'AED_AEIBOR_3M'}, 'description': {'summary': 'AED AEIBOR', 'tags': ['currency:AED', 'indexTenor:3M', 'sourceLongName:Refinitiv', 'sourceShortName:RFTB']}}]

    """

    try:
        logger.info("Calling search")

        response = Client().floating_rate_indices_resource.list(
            item_per_page=item_per_page,
            page=page,
            spaces=spaces,
            names=names,
            space_name_sort_order=space_name_sort_order,
            tags=tags,
            fields=fields,
        )

        output = response.data
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
