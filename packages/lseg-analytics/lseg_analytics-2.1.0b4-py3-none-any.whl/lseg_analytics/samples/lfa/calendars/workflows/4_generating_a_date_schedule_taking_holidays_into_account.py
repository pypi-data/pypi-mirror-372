from lseg_analytics.reference_data import calendars
from lseg_analytics.common import Frequency, WeekDay

lseg_ukg_cal = calendars.load(name="UKG", space = "LSEG")

# Generate a schedule for 10 weeks, every Mondays, starting the 01-Jan-2025
generated_date_schedule = lseg_ukg_cal.generate_date_schedule(
    start_date="2025-01-01",
    count=10,
    day_of_week=WeekDay.MONDAY,
    frequency=Frequency.WEEKLY
)

for date in generated_date_schedule:
    print(date)

# Generate a schedule for 10 weeks, every Mondays, starting the 01-Jan-2025
generated_date_schedule = calendars.generate_date_schedule(
    calendars=[
        "LSEG/UKG",
        "LSEG/EUR",
        "LSEG/USA",
        "LSEG/HKG",
    ],     
    frequency=Frequency.MONTHLY,
    start_date="2025-01-01",
    count=10,
    calendar_day_of_month=4
)
 
# Display the generated dates
for date in generated_date_schedule:
    print(date)