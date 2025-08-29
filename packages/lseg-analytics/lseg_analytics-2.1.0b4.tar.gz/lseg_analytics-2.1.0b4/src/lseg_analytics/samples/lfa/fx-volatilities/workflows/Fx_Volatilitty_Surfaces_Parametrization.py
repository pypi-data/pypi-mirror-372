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
surface_parameters = fxv.FxVolatilityPricingParameters(
        calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
        volatility_model = fxv.CurvesAndSurfacesVolatilityModelEnum.SVI,  # Options: SVI, SABR, TWIN_LOGNORMAL
        x_axis = fxv.XAxisEnum.DELTA,                                     # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
        y_axis = fxv.YAxisEnum.TENOR                                      # Options: same as X-axis
    )
print(f"   ✓ Surface Parameters: {surface_parameters}")

print("Step 3: Create request item...")
# Create the main request object  with basic configuration
request_item = fxv.FxVolatilitySurfaceRequestItem(
        surface_tag = f"{currencyPair}_svi_Volsurface",
        underlying_definition = surface_definition,
        surface_parameters = surface_parameters,
        underlying_type = fxv.CurvesAndSurfacesUnderlyingTypeEnum.FX,
        surface_layout = fxv.SurfaceOutput(
            format = fxv.FormatEnum.MATRIX,  # Options: LIST, MATRIX
        )
    )
print(f"   ✓ Request Item: {request_item}")

# Changing the model and keeping the same other parameters
surface_parameters_sabr = copy.deepcopy(surface_parameters)
surface_parameters_sabr.fx_swap_calculation_method = fxv.CurvesAndSurfacesFxSwapCalculationMethodEnum.FX_SWAP_IMPLIED_FROM_DEPOSIT
surface_parameters_sabr.fx_spot_object = fxv.BidAskMid(ask=2, bid=2, mid=2)
surface_parameters_sabr.interpolation_weight = fxv.InterpolationWeight(holidays=0, week_days=1, week_ends=0)
surface_parameters_sabr.price_side = fxv.CurvesAndSurfacesPriceSideEnum.BID
# surface_parameters_sabr.domestic_deposit_rate_percent_object = BidAskMid(ask=2, bid=2, mid=2)

# We can introduce quotes for FX strategies
surface_parameters_sabr.atm_volatility_object = fxv.BidAskMid(ask=10, bid=10, mid=10)
surface_parameters_sabr.butterfly10_dobject = fxv.BidAskMid(ask=10, bid=10, mid=10)
surface_parameters_sabr.butterfly25_dobject = fxv.BidAskMid(ask=10, bid=10, mid=10)
surface_parameters_sabr.risk_reversal10_dobject = fxv.BidAskMid(ask=10, bid=10, mid=10)
surface_parameters_sabr.risk_reversal25_dobject = fxv.BidAskMid(ask=10, bid=10, mid=10)

# Create another request Item for SABR
request_item_sabr = copy.deepcopy(request_item)
request_item_sabr.surface_tag = f"{currencyPair}_sabr_Volsurface"
request_item_sabr.surface_parameters = surface_parameters_sabr
print(f"   ✓ Request Item: {request_item_sabr}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = fxv.calculate(universe=[request_item, request_item_sabr])

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
display(differences_df.round(5))

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
plt.plot(surface_df_svi.columns.map(str), surface_df_svi.T["2Y"], label = "SVI")
plt.plot(surface_df_sabr.columns.map(str), surface_df_sabr.T["2Y"], label = "SABR")
plt.title(f"{currencyPair} Volatility Smiles SVI vs SABR", fontdict={'fontweight':'bold','fontsize':15})
plt.legend(loc='upper right')
plt.xlabel('Delta')
plt.ylabel('Volatility')
