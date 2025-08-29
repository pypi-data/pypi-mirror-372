from lseg_analytics.reference_data import calendars
from lseg_analytics.reference_data.calendars import Calendar, RestDays, HolidayRule, FullDayDuration, AbsolutePositionWhen, Observance, RelativeRescheduleDescription, CalendarDefinition
from lseg_analytics_basic_client.models import Description
from lseg_analytics.common import WeekDay, ValidityPeriod, Month

my_cal = Calendar(
    definition=CalendarDefinition(),
    description=Description(summary="My personal calendar"))
  
my_cal.definition.rest_days = [
    RestDays(
        rest_days=[WeekDay.SATURDAY, WeekDay.SUNDAY],
        validity_period=ValidityPeriod(
            start_date="2024-01-01",
            end_date="2024-12-31",
        ),
    )
]

my_cal.definition.holiday_rules = [
    HolidayRule(
        name="New Year's Day",
        duration=FullDayDuration(full_day=1),
        validity_period=ValidityPeriod(
            start_date="2024-01-01",
            end_date="2024-12-31",
        ),
        when=AbsolutePositionWhen(day_of_month=1, month=Month.JANUARY),
    ),
]

my_cal.definition.first_day_of_week = WeekDay.MONDAY

# Save the calendar
my_cal.save(name="My_Calendar", space="HOME")
 
# Search for calendars of the user's space
calendars.search(spaces=["HOME"])
 
# Load the calendar
my_cal = None
my_cal = calendars.load(name="My_Calendar", space="HOME")

# Add a holiday rule
my_cal.definition.holiday_rules.append(
    HolidayRule(
        name="My birthday",
        duration=FullDayDuration(full_day=1),
        validity_period=ValidityPeriod(
            start_date="2024-01-01",
            end_date="2024-12-31",
        ),
        when=AbsolutePositionWhen(day_of_month=18, month=Month.JUNE),
    )
)

# Save the updated calendar
my_cal.save()

for rule in my_cal.definition.holiday_rules:
    print(rule.name)

# Generate the list of holidays for 2024
holidays = calendars.generate_holidays(
    calendars=[
        "HOME/My_Calendar"
    ],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
  
# Display the generated holidays
for holiday in holidays:
    print(holiday.date, '-', holiday.names[0].name)

calendars.delete(name="My_Calendar", space="HOME")