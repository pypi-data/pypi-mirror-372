from lseg_analytics.market_data import fx_volatility as fxv

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import copy
from IPython.display import display

print("Step 1: Creating Surface Definition...")

currencyPair = "EURUSD"

# Create surface definition object
surface_definition = fxv.FxVolatilitySurfaceDefinition(
        instrument_code = currencyPair
        )
print(f"   ✓ Instrument: {surface_definition.instrument_code}")

print("Step 2: Configuring Surface Parameters...")
surface_parameters_svi = fxv.FxVolatilityPricingParameters(
        calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
        volatility_model = fxv.CurvesAndSurfacesVolatilityModelEnum.SVI,  # Options: SVI, SABR, TWIN_LOGNORMAL
        x_axis = fxv.XAxisEnum.DELTA,                                     # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
        y_axis = fxv.YAxisEnum.TENOR                                      # Options: same as X-axis
    )
print(f"   ✓ Surface Parameters: {surface_parameters_svi}")

print("Step 3: Create request item...")
# Create the main request object  with basic configuration
request_item_svi = fxv.FxVolatilitySurfaceRequestItem(
        surface_tag = f"{currencyPair}_SVI_Volsurface",
        underlying_definition = surface_definition,
        surface_parameters = surface_parameters_svi,
        underlying_type = fxv.CurvesAndSurfacesUnderlyingTypeEnum.FX,
        surface_layout = fxv.SurfaceOutput(
            format = fxv.FormatEnum.MATRIX,  # Options: LIST, MATRIX
        )
    )
print(f"   ✓ Request Item: {request_item_svi}")

# Changing the model and keeping the same other parameters
surface_parameters_sabr = copy.deepcopy(surface_parameters_svi)
surface_parameters_sabr.volatility_model = fxv.CurvesAndSurfacesVolatilityModelEnum.SABR

# Create another request Item for SABR
request_item_sabr = copy.deepcopy(request_item_svi)
request_item_sabr.surface_tag = f"{currencyPair}_SABR_Volsurface"
request_item_sabr.surface_parameters = surface_parameters_sabr
print(f"   ✓ Request Item: {request_item_sabr}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = fxv.calculate(universe=[request_item_svi, request_item_sabr])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Surface data points available: {len(surface_data['surface'])}")
    else:
        print("   No surface data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Display the raw surface data
print(response['data'][0]['surfaceTag'])
print(response['data'][1]['surfaceTag'])

# Create DataFrame for SVI surface
vol_surface_svi = response['data'][0]['surface']
expiries = vol_surface_svi[0][1:]
deltas = []
values = []
for row in vol_surface_svi[1:]:
    deltas.append(row[0])
    values.append(row[1:])

surface_df_svi = pd.DataFrame(values, index=deltas, columns=expiries).T.astype(float)

# Create DataFrame for SABR surface
vol_surface_sabr = response['data'][1]['surface']
values = []
for row in vol_surface_sabr[1:]:
    values.append(row[1:])

surface_df_sabr = pd.DataFrame(values, index=deltas, columns=expiries).T.astype(float)

# DataFrame of Differences
differences_df = surface_df_svi - surface_df_sabr
display(differences_df.round(2))

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
plt.plot(surface_df_svi.columns.map(str), surface_df_svi.T["2Y"], label = "SVI")
plt.plot(surface_df_sabr.columns.map(str), surface_df_sabr.T["2Y"], label = "SABR")
plt.title(f"{currencyPair} Volatility Smiles SVI vs SABR", fontdict={'fontweight':'bold','fontsize':15})
plt.legend(loc='upper right')
plt.xlabel('Delta')
plt.ylabel('Volatility')
