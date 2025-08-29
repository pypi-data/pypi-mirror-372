from lseg_analytics.market_data import inflation_curves as infc
import json
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

print("Step 1: Creating Curve Definition...")
# Select an Inflation Index
inflation_index = 'AGBRPI'

# Create curve definition object
curve_definition = infc.InflationCurveDefinitionItem(
        inflation_index = infc.InflationIndex(code=inflation_index),
        )
print(f"   ✓ Instrument: {curve_definition.inflation_index}")

print("Step 2: Configuring Curve Parameters...")
# Create CPIs for the wanted month and year to be overriden
cpi_jan_2025 = infc.ConsumerPriceIndex(index_value=315, month=infc.MonthEnum.JANUARY, year=2025)
cpi_feb_2025 = infc.ConsumerPriceIndex(index_value=315, month=infc.MonthEnum.FEBRUARY, year=2025)

curve_parameters = infc.InflationCurveParameters(
        valuation_date_time = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
        consumer_price_indexes = [cpi_jan_2025, cpi_feb_2025]
    )
print(f"   ✓ Curve Parameters: {curve_parameters}")

print("Step 3: Create request item...")
# Create the main request object  with basic configuration
request_item = infc.InflationCurvesRequestItem(
        curve_tag = f"{inflation_index}_InflationCurve",
        curve_definition = curve_definition,
        curve_parameters = curve_parameters,
    )
print(f"   ✓ Request Item: {json.dumps(request_item.as_dict(), indent=4)}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
response = infc.calculate(universe=[request_item])
curve_data = response['data'][0]

cpis = curve_data['curves']['consumerPriceIndexCurvePoints']
cpis_df = pd.DataFrame(cpis)
cpis_df["Month/Year"] = cpis_df['month'] + ' ' + cpis_df['year'].astype(str)
del cpis_df['month'],cpis_df['year']
cpis_df.set_index("Month/Year", inplace = True)
cpis_df.head(5) # remove .head(5) to get the entire dataframe

curve_parameters.interpolation_mode = "Step" # Possible values: Step or Linear
curve_parameters.look_back_month = 1 # Number of months to go back in historical CPIs
curve_parameters.price_side = infc.CurvesAndSurfacesPriceSideEnum.BID # Bid, Ask or Mid

response = infc.calculate(universe=[request_item])
curve_data = response['data'][0]

cpis = curve_data['curves']['consumerPriceIndexCurvePoints']
cpis_df = pd.DataFrame(cpis)
cpis_df["Month/Year"] = cpis_df['month'] + ' ' + cpis_df['year'].astype(str)
del cpis_df['month'],cpis_df['year']
cpis_df.set_index("Month/Year", inplace = True)
cpis_df.head(5) # remove .head(5) to get the entire dataframe
