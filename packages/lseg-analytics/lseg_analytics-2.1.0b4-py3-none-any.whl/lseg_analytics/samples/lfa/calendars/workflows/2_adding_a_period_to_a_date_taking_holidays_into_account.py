from lseg_analytics.reference_data import calendars
from lseg_analytics.common import DateMovingConvention

lseg_ukg_cal = calendars.load(name="UKG", space = "LSEG")

# Compute dates 2 day, 3 weeks, 6 months , 1 year after the 1st of January 2024
tenors=["2D", "3W", "6M", "1Y"]
dates = lseg_ukg_cal.compute_dates(start_date="2024-01-01", tenors=tenors)

for tenor, date in zip(tenors, dates):
    print('Today +', tenor, '=', date)

# Compute dates 2, 3, 6 months and 1 year after the 1st of January 2024
tenors=["2M", "3M", "6M", "1Y"]
dates = calendars.compute_dates(
    calendars=[
        "LSEG/UKG",
        "LSEG/EUR",
        "LSEG/USA",
        "LSEG/HKG",
    ],
    start_date = "2024-01-01",
    tenors = tenors,
    date_moving_convention=DateMovingConvention.NEXT_BUSINESS_DAY
)
  
# Display the computed dates
for tenor, date in zip(tenors, dates):
    print('Today +', tenor, '=', date)