from lseg_analytics.reference_data import calendars
from lseg_analytics.common import PeriodType

lseg_ukg_cal = calendars.load(name="UKG", space = "LSEG")

# Count working days between the 1st of January and the 31st of July 2024
count = lseg_ukg_cal.count_periods(
    start_date="2024-01-01",
    end_date="2024-07-31",
    period_type = PeriodType.WORKING_DAY
)

# Display the number of counted periods
print(count)

# Count working days between the 1st of January and the 31st of July 2024
count = calendars.count_periods(
    calendars=[
        "LSEG/UKG",
        "LSEG/EUR",
        "LSEG/USA",
        "LSEG/HKG",
    ],   
    start_date="2024-01-01",
    end_date="2024-07-31",
    period_type = PeriodType.WORKING_DAY
)
 
# Display the number of counted periods
print(count)