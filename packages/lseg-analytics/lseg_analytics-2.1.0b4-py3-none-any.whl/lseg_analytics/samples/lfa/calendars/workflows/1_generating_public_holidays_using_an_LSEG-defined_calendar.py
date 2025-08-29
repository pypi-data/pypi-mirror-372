from lseg_analytics.reference_data import calendars
from lseg_analytics.helpers import to_rows
import pandas as pd
from IPython.display import display

lseg_ukg_cal = calendars.load(name="UKG", space = "LSEG")

# Generate the list of holidays for 2024
holidays = lseg_ukg_cal.generate_holidays(start_date="2024-01-01", end_date="2024-12-31")

# Convert holidays to DataFrame and display them
df = pd.DataFrame(to_rows(holidays))
display(df)

# Generate the list of holidays for 2024
holidays = calendars.generate_holidays(
    calendars=[
        "LSEG/UKG",
        "LSEG/EUR",
        "LSEG/USA",
        "LSEG/HKG",
    ],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
  
# Convert holidays to DataFrame and display them
df = pd.DataFrame(to_rows(holidays))
display(df)