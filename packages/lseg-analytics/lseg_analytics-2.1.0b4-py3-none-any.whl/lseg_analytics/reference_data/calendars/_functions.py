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
    AbsolutePositionWhen,
    CalendarDefinition,
    CalendarInfo,
    ComputeDatesBatched,
    CountPeriodsOutput,
    DateMovingConvention,
    DayCountBasis,
    Description,
    Direction,
    Duration,
    EndOfMonthConvention,
    Frequency,
    FullDayDuration,
    HalfDayDuration,
    Holiday,
    HolidayNames,
    HolidayRule,
    IndexOrder,
    InnerError,
    LagDaysRescheduleDescription,
    Location,
    Month,
    Observance,
    PeriodType,
    PeriodTypeOutput,
    RelativePositionWhen,
    RelativeRescheduleDescription,
    RelativeToRulePositionWhen,
    RescheduleDescription,
    RestDays,
    ServiceError,
    SortingOrderEnum,
    Time,
    TimezoneEnum,
    ValidityPeriod,
    WeekDay,
    When,
)

from ._calendar import Calendar
from ._logger import logger

__all__ = [
    "AbsolutePositionWhen",
    "CalendarDefinition",
    "CalendarInfo",
    "ComputeDatesBatched",
    "CountPeriodsOutput",
    "FullDayDuration",
    "HalfDayDuration",
    "Holiday",
    "HolidayNames",
    "HolidayRule",
    "LagDaysRescheduleDescription",
    "Observance",
    "RelativePositionWhen",
    "RelativeRescheduleDescription",
    "RelativeToRulePositionWhen",
    "RescheduleDescription",
    "RestDays",
    "When",
    "compute_dates",
    "count_periods",
    "delete",
    "generate_date_schedule",
    "generate_holidays",
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
    Load a Calendar using its name and space to perform date-based operations such as calculating working days, generating schedules, and retrieving holiday information on a predefined calendar.

    Parameters
    ----------
    resource_id : str, optional
        The Calendar id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The Calendar name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the Calendar is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    Calendar
        The Calendar instance.

    Examples
    --------
    Load by Id.

    >>> load(resource_id="125B1FCD-6EE9-4B1F-870F-5BA89EBE71AF")
    <Calendar space='HOME' name='my_personal_calendar' 125B1FCD‥>

    Load by name and space.

    >>> load(name="EMU", space="LSEG")
    <Calendar space='HOME' name='my_personal_calendar' 125B1FCD‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load Calendar {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Calendar {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Calendar not found by identifier name={name} space={space}")
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
    Delete Calendar instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The Calendar resource ID.
        Required if name is not provided.
    name : str, optional
        The Calendar name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the Calendar is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    Delete by Id.

    >>> delete(resource_id='125B1FCD-6EE9-4B1F-870F-5BA89EBE71AF')
    True

    Delete by name and space.

    >>> delete(name="my_calendar", space="my_personal_space")
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
    logger.info(f"Delete Calendar {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"Calendar {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource Calendar not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def compute_dates(
    *,
    tenors: List[str],
    calendars: List[str],
    start_date: Optional[Union[str, datetime.date]] = None,
    date_moving_convention: Optional[Union[str, DateMovingConvention]] = None,
    end_of_month_convention: Optional[Union[str, EndOfMonthConvention]] = None,
    fields: Optional[str] = None,
) -> List[ComputeDatesBatched]:
    """
    Computes dates for the calendar according to specified conditions. Start Date is included in the calculation. Only saved calendars are supported.

    Parameters
    ----------
    tenors : List[str]
        Tenors to be added to startDate to calculate the resultant dates (e.g., 1M, 1Y).
        A tenor expresses a period of time using a specific syntax. There are two kinds of tenor:
        - Ad-hoc tenors explicitly state the length of time in Days (D), Weeks (W), Months (M) and Years (Y).
        For example "1D" for one day, "2W" for two weeks or "3M1D" for three months and a day.
        When mixing units, units must be written in descending order of size (Y > M > W > D).  So, 5M3D is valid, but 3D5M is not.
        - Common tenors are expressed as letter codes:
        - ON (Overnight) - A one business day period that starts today.
        - TN (Tomorrow-Next) - A one business day period that starts next business day.
        - SPOT (Spot Date) - A period that ends on the spot date.  Date is calculated as trade date (today) + days to spot.
        - SN (Spot-Next) - A one business day period that starts at the spot date.
        - SW (Spot-Week) - A one business week period that starts at the spot date.
    start_date : Union[str, datetime.date], optional
        The start date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2023-01-01). Default is Today.
    date_moving_convention : Union[str, DateMovingConvention], optional
        The method to adjust dates to working days. The default value is ModifiedFollowing.
    end_of_month_convention : Union[str, EndOfMonthConvention], optional
        Conventions to adjust payment dates when they fall at the end of a month.
    calendars : List[str]
        An array of calendar defining objects for which the calculation should be done. Each string being composed of the space and name of a calendar. For example 'LSEG/UKG' is the string referencing the 'UKG' calendar stored in the 'LSEG' space.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[ComputeDatesBatched]
        An object to definine the properties of the calculated dates returned, with a dedicated error object for each calculation. This serializable object behaves exactly like a list of dictionaries when iterated or displayed. It can be converted to a DataFrame without transformation.

    Examples
    --------
    >>> computed_dates = compute_dates(
    >>>     calendars=["LSEG/UKG", "LSEG/EUR"],
    >>>     tenors=["1M", "2M"],
    >>>     start_date=datetime.date(2023, 11, 1),
    >>>     date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY,
    >>> )
    >>>
    >>> computed_dates
    [{'endDate': '2023-12-01', 'tenor': '1M'},
     {'endDate': '2024-01-02', 'tenor': '2M'}]


    >>> # Display computed dates
    >>> pd.DataFrame(computed_dates)
          endDate tenor
    0  2023-12-01    1M
    1  2024-01-02    2M

    """

    try:
        logger.info("Calling compute_dates")

        response = Client().calendars_resource.compute_dates(
            fields=fields,
            tenors=tenors,
            start_date=start_date,
            date_moving_convention=date_moving_convention,
            end_of_month_convention=end_of_month_convention,
            calendars=calendars,
        )

        output = response.data
        logger.info("Called compute_dates")

        return output
    except Exception as err:
        logger.error("Error compute_dates.")
        check_exception_and_raise(err, logger)


def count_periods(
    *,
    start_date: Union[str, datetime.date],
    end_date: Union[str, datetime.date],
    day_count_basis: Optional[Union[str, DayCountBasis]] = None,
    period_type: Optional[Union[str, PeriodType]] = None,
    calendars: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> CountPeriodsOutput:
    """
    Counts the time periods that satisfy specified conditions. Note the use of date strings for convenience. Start and End Dates are included in the calculation. Only saved calendars are supported.

    Parameters
    ----------
    start_date : Union[str, datetime.date]
        The start date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2023-01-01).
    end_date : Union[str, datetime.date]
        The end date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2024-01-01).
    day_count_basis : Union[str, DayCountBasis], optional
        The day count basis convention used to calculate the period between two dates.
        It is used when periodType is set to Year.
        Each convention defines the number of days between two dates and the year length in days (basis) for the period calculation.
        Default is DCB_ACTUAL_ACTUAL.
    period_type : Union[str, PeriodType], optional
        The method of the period calculation. Default is Day.
    calendars : List[str], optional
        An array of calendar defining objects for which the calculation should be done. Each string being composed of the space and name of a calendar.
        For example 'LSEG/UKG' is the string referencing the 'UKG' calendar stored in the 'LSEG' space.
        The calendars parameter is optional only when periodType is "Day" or "Year".
        For a given day to be considered a working day, it must be a working day in all of the selected calendars. If it is a non-working day in any of the calendars, it is a non-working day.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CountPeriodsOutput
        The result of the period calculation for the count periods endpoint.

    Examples
    --------
    >>> count_periods(
    >>>     calendars=['LSEG/UKG'],
    >>>     start_date=datetime.date(2023, 2, 1),
    >>>     end_date=datetime.date(2023, 12, 31),
    >>>     day_count_basis=DayCountBasis.DCB_30_360,
    >>>     period_type=PeriodType.WORKING_DAY
    >>> )
    {'count': 247, 'periodType': 'WorkingDay'}

    """

    try:
        logger.info("Calling count_periods")

        response = Client().calendars_resource.count_periods(
            fields=fields,
            start_date=start_date,
            end_date=end_date,
            day_count_basis=day_count_basis,
            period_type=period_type,
            calendars=calendars,
        )

        output = response.data
        logger.info("Called count_periods")

        return output
    except Exception as err:
        logger.error("Error count_periods.")
        check_exception_and_raise(err, logger)


def _delete_by_id(calendar_id: str) -> bool:
    """
    Delete a Calendar that exists in the platform. The Calendar can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    calendar_id : str
        A sequence of textual characters.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting Calendar with id: {calendar_id}")
        Client().calendar_resource.delete(calendar_id=calendar_id)
        logger.info(f"Deleted Calendar with id: {calendar_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting Calendar with id: {calendar_id}")
        check_exception_and_raise(err, logger)


def generate_date_schedule(
    *,
    frequency: Union[str, Frequency],
    calendars: List[str],
    start_date: Optional[Union[str, datetime.date]] = None,
    end_date: Optional[Union[str, datetime.date]] = None,
    calendar_day_of_month: Optional[int] = None,
    count: Optional[int] = None,
    day_of_week: Optional[Union[str, WeekDay]] = None,
    fields: Optional[str] = None,
) -> List[datetime.date]:
    """
    Generates a date schedule for the calendar according to specified conditions. Start and End Dates are included in the calculation. Only saved calendars are supported.

    Parameters
    ----------
    frequency : Union[str, Frequency]
        The frequency of dates in the schedule which should be generated. Note that "Daily" refers to working days only.
    start_date : Union[str, datetime.date], optional
        The start date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2023-01-01).
        The start date must be less or equal to the end date.
        Required if endDate is in the past.
    end_date : Union[str, datetime.date], optional
        The end date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2024-01-01).
        If startDate is not specified, endDate is used to define the list of dates from today's date to the end date.
        The end date must be greater or equal to the start date.
        Required if count is not specified. Only one of endDate and count can be set at a time.
    calendar_day_of_month : int, optional
        The number of the day of the month. Required if frequency is Monthly; do not use otherwise. The minimum value is 1. The maximum value is 31.
    count : int, optional
        The number of dates to be generated,  counting from the start date (or today's date if the start day is not set) to the end date.
        It should not have a negative value.
        Required if endDate is not specified. Only one of endDate and count can be set at a time.
    day_of_week : Union[str, WeekDay], optional
        The day of the week. Required if frequency is Weekly or BiWeekly; do not use otherwise.
    calendars : List[str]
        An array of calendar defining objects for which the calculation should be done. Each string being composed of the space and name of a calendar. For example 'LSEG/UKG' is the string referencing the 'UKG' calendar stored in the 'LSEG' space.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"

    Examples
    --------
    >>> generate_date_schedule(
    >>>     calendars=['LSEG/UKG'],
    >>>     frequency=Frequency.WEEKLY,
    >>>     start_date=datetime.date(2023, 4, 30),
    >>>     calendar_day_of_month=5,
    >>>     count=20,
    >>>     day_of_week=WeekDay.TUESDAY
    >>> )
    [datetime.date(2023, 5, 9),
     datetime.date(2023, 5, 16),
     datetime.date(2023, 5, 23),
     datetime.date(2023, 5, 30),
     datetime.date(2023, 6, 6),
     datetime.date(2023, 6, 13),
     datetime.date(2023, 6, 16),
     datetime.date(2023, 6, 27),
     datetime.date(2023, 7, 4),
     datetime.date(2023, 7, 11),
     datetime.date(2023, 7, 18),
     datetime.date(2023, 7, 25),
     datetime.date(2023, 8, 1),
     datetime.date(2023, 8, 8),
     datetime.date(2023, 8, 15),
     datetime.date(2023, 8, 22),
     datetime.date(2023, 8, 29),
     datetime.date(2023, 9, 5),
     datetime.date(2023, 9, 12),
     datetime.date(2023, 9, 19)]

    """

    try:
        logger.info("Calling generate_date_schedule")

        response = Client().calendars_resource.generate_date_schedule(
            fields=fields,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            calendar_day_of_month=calendar_day_of_month,
            count=count,
            day_of_week=day_of_week,
            calendars=calendars,
        )

        output = response.data
        logger.info("Called generate_date_schedule")

        return output
    except Exception as err:
        logger.error("Error generate_date_schedule.")
        check_exception_and_raise(err, logger)


def generate_holidays(
    *,
    end_date: Union[str, datetime.date],
    calendars: List[str],
    start_date: Optional[Union[str, datetime.date]] = None,
    fields: Optional[str] = None,
) -> List[Holiday]:
    """
    Gets the holidays for the calendar within a date range. Start and End Dates are included in the calculation. Only saved calendars are supported.

    Parameters
    ----------
    start_date : Union[str, datetime.date], optional
        The start date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2023-01-01). Default is today.
    end_date : Union[str, datetime.date]
        The end date of the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., 2024-01-01).
    calendars : List[str]
        An array of calendar defining objects for which the calculation should be done. Each string being composed of the space and name of a calendar. For example 'LSEG/UKG' is the string referencing the 'UKG' calendar stored in the 'LSEG' space.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[Holiday]
        Dates and names of holidays for a requested calendar.

    Examples
    --------
    >>> response = generate_holidays(calendars=["LSEG/UKG"], start_date="2023-01-01", end_date="2023-01-31")
    >>> response[0]
    {'date': '2023-01-01', 'names': [{'name': "New Year's Day", 'calendars': ['LSEG/ARG', 'LSEG/UKG'], 'countries': ['ARG', 'GBR']}]}

    """

    try:
        logger.info("Calling generate_holidays")

        response = Client().calendars_resource.generate_holidays(
            fields=fields, start_date=start_date, end_date=end_date, calendars=calendars
        )

        output = response.data
        logger.info("Called generate_holidays")

        return output
    except Exception as err:
        logger.error("Error generate_holidays.")
        check_exception_and_raise(err, logger)


def _load_by_id(calendar_id: str, fields: Optional[str] = None) -> Calendar:
    """
    Access a Calendar existing in the platform (read). The Calendar can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    calendar_id : str
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
    Calendar


    Examples
    --------


    """

    try:
        logger.info(f"Opening Calendar with id: {calendar_id}")

        response = Client().calendar_resource.read(calendar_id=calendar_id, fields=fields)

        output = Calendar(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening Calendar:")
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
) -> List[CalendarInfo]:
    """
    List the Calendars existing in the platform (depending on permissions)

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
    List[CalendarInfo]
        Object defining the links available on a Calendar resource.

    Examples
    --------
    Search all previously saved calendars.

    >>> search()
    [{'type': 'Calendar', 'id': '0cee3640-8063-49b4-a1a1-50ab1ee0030f', 'description': {'tags': [], 'summary': 'LSEG Euroland Calendar'}, 'location': {'name': 'EMU', 'space': 'LSEG'}}]

    Search by names and spaces.

    >>> search(names=["EMU"], spaces=["LSEG"])
    [{'type': 'Calendar', 'id': '0cee3640-8063-49b4-a1a1-50ab1ee0030f', 'description': {'tags': [], 'summary': 'LSEG Euroland Calendar'}, 'location': {'name': 'EMU', 'space': 'LSEG'}}]

    Search by names.

    >>> search(names=["EMU"])
    [{'type': 'Calendar', 'id': '0cee3640-8063-49b4-a1a1-50ab1ee0030f', 'description': {'tags': [], 'summary': 'LSEG Euroland Calendar'}, 'location': {'name': 'EMU', 'space': 'LSEG'}}]

    Search by spaces.

    >>> search(spaces=["LSEG"])
    [{'type': 'Calendar', 'id': '0cee3640-8063-49b4-a1a1-50ab1ee0030f', 'description': {'tags': [], 'summary': 'LSEG Euroland Calendar'}, 'location': {'name': 'EMU', 'space': 'LSEG'}}]

    Search by tags.

    >>> search(tags=["EU calendar"])
    [{'type': 'Calendar', 'id': '0cee3640-8063-49b4-a1a1-50ab1ee0030f', 'description': {'tags': [], 'summary': 'LSEG Euroland Calendar'}, 'location': {'name': 'EMU', 'space': 'LSEG'}}]

    """

    try:
        logger.info("Calling search")

        response = Client().calendars_resource.list(
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
