from lseg_analytics.market_data import inflation_curves as infc

import datetime as dt
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

print("Step 1: Creating Curve Definition...")
# Select an Inflation Index
inflation_index = 'AGBRPI'

# Create curve definition object
curve_definition = infc.InflationCurveDefinitionItem(
        inflation_index = infc.InflationIndex(code=inflation_index) 
        )
print(f"   ✓ Instrument: {curve_definition.inflation_index}")

print("Step 2: Configuring Curve Parameters...")
# Create curve parameters object - optional
curve_parameters = infc.InflationCurveParameters(
        valuation_date_time = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
        seasonality= infc.InflationSeasonality(apply_seasonality=False)  # Parameter to not use seasonal factors
    )
print(f"   ✓ Curve Parameters: {curve_parameters}")

print("Step 3: Create request item...")
# Create the main request object with basic configuration
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

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
plt.plot(cpis_df.index, cpis_df['indexValue'], label = inflation_index)
plt.title(f"{inflation_index} Deseasonalized Curve", fontdict={'fontweight':'bold','fontsize':15})
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=20))
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.xlabel('Month/Year')
plt.ylabel('CPI Value')

# This time we set apply_seasonality to True 
curve_parameters.seasonality = infc.InflationSeasonality(apply_seasonality=True)

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
response = infc.calculate(universe=[request_item])
curve_data = response['data'][0]

cpis = curve_data['curves']['consumerPriceIndexCurvePoints']
cpis_df = pd.DataFrame(cpis)
cpis_df["Month/Year"] = cpis_df['month'] + ' ' + cpis_df['year'].astype(str)
del cpis_df['month'],cpis_df['year']
cpis_df.set_index("Month/Year", inplace = True)
cpis_df.head(5)

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
plt.plot(cpis_df.index, cpis_df['indexValue'], label = inflation_index)
plt.title(f"{inflation_index} Seasonalized Curve", fontdict={'fontweight':'bold','fontsize':15})
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=20))
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.xlabel('Month/Year')
plt.ylabel('CPI Value')

# seasonality factors
pd.DataFrame(curve_data['curves']['seasonalityCurvePoints'])

# Override some of factors with user defined ones
seasonality_factor_june = infc.InflationSeasonalityItem(factor=1, month=infc.MonthEnum.JUNE) # Create factor for June
seasonality_factor_july = infc.InflationSeasonalityItem(factor=1, month=infc.MonthEnum.JULY) # Create factor for July
seasonality_factor_august = infc.InflationSeasonalityItem(factor=1, month=infc.MonthEnum.AUGUST) # Create factor for August

curve_parameters.seasonality = infc.InflationSeasonality(
    apply_seasonality=True,
    seasonalities = [seasonality_factor_june, seasonality_factor_july, seasonality_factor_august]
    )

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
response = infc.calculate(universe=[request_item])
curve_data = response['data'][0]

cpis = curve_data['curves']['consumerPriceIndexCurvePoints']
pd.DataFrame(curve_data['curves']['seasonalityCurvePoints'])
