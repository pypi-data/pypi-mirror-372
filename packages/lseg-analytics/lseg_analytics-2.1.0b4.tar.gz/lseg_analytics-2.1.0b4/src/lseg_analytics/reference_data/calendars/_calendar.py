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
    CalendarDefinition,
    CalendarInfo,
    ComputeDatesBatched,
    CountPeriodsOutput,
    DateMovingConvention,
    DayCountBasis,
    Description,
    EndOfMonthConvention,
    Frequency,
    Holiday,
    Location,
    PeriodType,
    ResourceType,
    SortingOrderEnum,
    WeekDay,
)

from ._logger import logger


class Calendar(ResourceBase):
    """
    Calendar object.

    Contains all the necessary information to identify and define a Calendar instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the Calendar.
    location : Location
        Object defining the location of the Calendar in the platform.
    description : Description, optional
        Object defining metadata for the Calendar.
    definition : CalendarDefinition
        Object defining the Calendar.

    See Also
    --------
    Calendar.generateHolidays : Gets the holidays for the calendar within a date range. Start and End Dates are included in the calculation. Only saved calendars are supported.
    Calendar.computeDates : Computes dates for the calendar according to specified conditions. Start Date is included in the calculation. Only saved calendars are supported.
    Calendar.generateDateSchedule : Generates a date schedule for the calendar according to specified conditions. Start and End Dates are included in the calculation. Only saved calendars are supported.
    Calendar.countPeriods : Counts the time periods that satisfy specified conditions. Note the use of date strings for convenience. Start and End Dates are included in the calculation. Only saved calendars are supported.

    Examples
    --------
    >>> # Create a calendar instance with parameter.
    >>> my_cal_definition = CalendarDefinition(rest_days=[
    >>>                     RestDays(
    >>>                         rest_days=[WeekDay.SATURDAY, WeekDay.SUNDAY],
    >>>                         validity_period=ValidityPeriod(
    >>>                             start_date="2024-01-01",
    >>>                             end_date="2024-12-31",
    >>>                         ),
    >>>                     )
    >>>                 ],
    >>>                     first_day_of_week=WeekDay.FRIDAY,
    >>>                     holiday_rules=[
    >>>                     HolidayRule(
    >>>                         name="New Year's Day",
    >>>                         duration=FullDayDuration(full_day=1),
    >>>                         validity_period=ValidityPeriod(
    >>>                             start_date="2024-01-01",
    >>>                             end_date="2024-12-31",
    >>>                         ),
    >>>                         when=AbsolutePositionWhen(day_of_month=1, month=Month.JANUARY),
    >>>                     ),
    >>>                 ]
    >>>                 )
    >>> my_cal = Calendar(definition=my_cal_definition)


    >>> # Save the instance with name and space.
    >>> my_cal.save(name="my_personal_calendar", space="HOME")
    True

    """

    _definition_class = CalendarDefinition

    def __init__(self, definition: CalendarDefinition, description: Optional[Description] = None):
        """
        Calendar constructor

        Parameters
        ----------
        definition : CalendarDefinition
            Object defining the Calendar.
        description : Description, optional
            Object defining metadata for the Calendar.

        Examples
        --------
        >>> # Create a calendar instance with parameter.
        >>> my_cal_definition = CalendarDefinition(rest_days=[
        >>>                     RestDays(
        >>>                         rest_days=[WeekDay.SATURDAY, WeekDay.SUNDAY],
        >>>                         validity_period=ValidityPeriod(
        >>>                             start_date="2024-01-01",
        >>>                             end_date="2024-12-31",
        >>>                         ),
        >>>                     )
        >>>                 ],
        >>>                     first_day_of_week=WeekDay.FRIDAY,
        >>>                     holiday_rules=[
        >>>                     HolidayRule(
        >>>                         name="New Year's Day",
        >>>                         duration=FullDayDuration(full_day=1),
        >>>                         validity_period=ValidityPeriod(
        >>>                             start_date="2024-01-01",
        >>>                             end_date="2024-12-31",
        >>>                         ),
        >>>                         when=AbsolutePositionWhen(day_of_month=1, month=Month.JANUARY),
        >>>                     ),
        >>>                 ]
        >>>                 )
        >>> my_cal = Calendar(definition=my_cal_definition)

        """
        self.definition: CalendarDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "Calendar"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the Calendar id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the Calendar.

        Examples
        --------
        >>> # Get the instance id.
        >>> my_cal.id
        '41d42531-2e1c-48c1-84e6-ea324c96eacd'

        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the Calendar location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the Calendar in the platform.

        Examples
        --------
        >>> # Get the location property.
        >>> my_cal.location.name
        'my_personal_calendar'


        >>> my_cal.location.space
        'HOME'

        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def compute_dates(
        self,
        *,
        tenors: List[str],
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
        >>> my_cal.compute_dates(start_date="2023-11-01", date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY, tenors=["1M", "2M"])
        [{'endDate': '2023-12-01', 'tenor': '1M'},
         {'endDate': '2024-01-02', 'tenor': '2M'}]

        """

        try:
            logger.info("Calling compute_dates for calendar with id")
            check_id(self._id)

            response = Client().calendar_resource.compute_dates(
                calendar_id=self._id,
                fields=fields,
                tenors=tenors,
                start_date=start_date,
                date_moving_convention=date_moving_convention,
                end_of_month_convention=end_of_month_convention,
            )

            output = response.data
            logger.info("Called compute_dates for calendar with id")

            return output
        except Exception as err:
            logger.error("Error compute_dates for calendar with id.")
            check_exception_and_raise(err, logger)

    def count_periods(
        self,
        *,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date],
        day_count_basis: Optional[Union[str, DayCountBasis]] = None,
        period_type: Optional[Union[str, PeriodType]] = None,
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
        >>> my_cal.count_periods(
        >>>     start_date="2023-01-01",
        >>>     end_date="2023-12-31",
        >>>     day_count_basis=DayCountBasis.DCB_30_360,
        >>>     period_type=PeriodType.WORKING_DAY,
        >>> )
        {'count': 243, 'periodType': 'WorkingDay'}

        """

        try:
            logger.info("Calling count_periods for calendar with id")
            check_id(self._id)

            response = Client().calendar_resource.count_periods(
                calendar_id=self._id,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                day_count_basis=day_count_basis,
                period_type=period_type,
            )

            output = response.data
            logger.info("Called count_periods for calendar with id")

            return output
        except Exception as err:
            logger.error("Error count_periods for calendar with id.")
            check_exception_and_raise(err, logger)

    def _create(self, location: Location) -> None:
        """
        Save a new Calendar in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the Calendar in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating Calendar")

            response = Client().calendars_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"Calendar created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating Calendar:")
            raise err

    def generate_date_schedule(
        self,
        *,
        frequency: Union[str, Frequency],
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
        >>> my_cal.generate_date_schedule(
        >>>     start_date="2023-04-30", frequency=Frequency.WEEKLY, count=20, day_of_week=WeekDay.TUESDAY
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
            logger.info("Calling generate_date_schedule for calendar with id")
            check_id(self._id)

            response = Client().calendar_resource.generate_date_schedule(
                calendar_id=self._id,
                fields=fields,
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                calendar_day_of_month=calendar_day_of_month,
                count=count,
                day_of_week=day_of_week,
            )

            output = response.data
            logger.info("Called generate_date_schedule for calendar with id")

            return output
        except Exception as err:
            logger.error("Error generate_date_schedule for calendar with id.")
            check_exception_and_raise(err, logger)

    def generate_holidays(
        self,
        *,
        end_date: Union[str, datetime.date],
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
        >>> response = my_cal.generate_holidays(start_date='2023-01-01', end_date='2023-01-31')
        >>> response[0]
        {'date': '2023-01-01', 'names': [{'name': "New Year's Day", 'calendars': ['LSEG/ARG'], 'countries': ['ARG']}]}

        """

        try:
            logger.info("Calling generate_holidays for calendar with id")
            check_id(self._id)

            response = Client().calendar_resource.generate_holidays(
                calendar_id=self._id,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
            )

            output = response.data
            logger.info("Called generate_holidays for calendar with id")

            return output
        except Exception as err:
            logger.error("Error generate_holidays for calendar with id.")
            check_exception_and_raise(err, logger)

    def _overwrite(self) -> None:
        """
        Overwrite a Calendar that exists in the platform. The Calendar can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting Calendar with id: {self._id}")
        Client().calendar_resource.overwrite(
            calendar_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save Calendar instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The Calendar name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the Calendar is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # Create a calendar instance with parameter.
        >>> my_cal_definition = CalendarDefinition(rest_days=[
        >>>                     RestDays(
        >>>                         rest_days=[WeekDay.SATURDAY, WeekDay.SUNDAY],
        >>>                         validity_period=ValidityPeriod(
        >>>                             start_date="2024-01-01",
        >>>                             end_date="2024-12-31",
        >>>                         ),
        >>>                     )
        >>>                 ],
        >>>                     first_day_of_week=WeekDay.FRIDAY,
        >>>                     holiday_rules=[
        >>>                     HolidayRule(
        >>>                         name="New Year's Day",
        >>>                         duration=FullDayDuration(full_day=1),
        >>>                         validity_period=ValidityPeriod(
        >>>                             start_date="2024-01-01",
        >>>                             end_date="2024-12-31",
        >>>                         ),
        >>>                         when=AbsolutePositionWhen(day_of_month=1, month=Month.JANUARY),
        >>>                     ),
        >>>                 ]
        >>>                 )
        >>> my_cal = Calendar(definition=my_cal_definition)


        >>> # Save the instance with name and space.
        >>> my_cal.save(name="my_personal_calendar", space="HOME")
        True

        """
        try:
            logger.info("Saving Calendar")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("Calendar saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"Calendar saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("Calendar save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "Calendar":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        Calendar
            The cloned Calendar object


        Examples
        --------
        >>> # Clone the existing instance on definition and description.
        >>> my_cal_clone = my_cal.clone()
        >>> my_cal_clone.save(name="my_cloned_calendar", space="HOME")
        True

        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
