from lseg_analytics.market_data import fx_volatility as fxv

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
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
        price_side = fxv.CurvesAndSurfacesPriceSideEnum.MID,              # Options: BID, MID, ASK
        x_axis = fxv.XAxisEnum.DELTA,                                     # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
        y_axis = fxv.YAxisEnum.TENOR                                      # Options: same as X-axis
    )
print(f"   ✓ Surface Parameters: {surface_parameters}")

print("Step 3: Create request item...")
# Create the main request object  with basic configuration
request_item = fxv.FxVolatilitySurfaceRequestItem(
        surface_tag = f"{currencyPair}_Volsurface",
        underlying_definition = surface_definition,
        surface_parameters = surface_parameters,
        underlying_type = fxv.CurvesAndSurfacesUnderlyingTypeEnum.FX,
        surface_layout = fxv.SurfaceOutput(
            format = fxv.FormatEnum.MATRIX,  # Options: LIST, MATRIX
        )
    )
print(f"   ✓ Request Item: {request_item}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = fxv.calculate(universe=[request_item])

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

vol_surface = response['data'][0]['surface']
expiries = vol_surface[0][1:]
deltas = []
values = []
for row in vol_surface[1:]:
    deltas.append(row[0])
    values.append(row[1:])

surface_df = pd.DataFrame(values, index=deltas, columns=expiries).T
display(surface_df.astype(float).round(2))

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
for tenor in ["1M", "1Y", "2Y"]:
    plt.plot(surface_df.columns.map(str), surface_df.T[tenor], label = tenor)
plt.title(f"{currencyPair} Volatility Smiles", fontdict={'fontweight':'bold','fontsize':15})
plt.legend(loc='upper right')
plt.xlabel('Delta')
plt.ylabel('Volatility')

# Change X axis to use STRIKE
surface_parameters.x_axis = fxv.XAxisEnum.STRIKE
# Change Y axis to use DATE
surface_parameters.y_axis = fxv.YAxisEnum.DATE

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = fxv.calculate(universe=[request_item])

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

vol_surface = response['data'][0]['surface']
expiries = vol_surface[0][1:]
strikes = []
values = []
for row in vol_surface[1:]:
    strikes.append(row[0])
    values.append(row[1:])

strikes = [round(float(strike), 5) if isinstance(strike, (int, float)) else strike for strike in strikes]

surface_df = pd.DataFrame(values, index=strikes, columns=expiries).T
display(surface_df.astype(float).round(2))

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
for tenor in list(surface_df.index)[0:4]:
    plt.plot(surface_df.columns, surface_df.T[tenor], label = tenor)
plt.title(f"Volatility Smiles by Expiry", fontdict={'fontweight':'bold','fontsize':15})
plt.legend(loc='upper right')
plt.xlabel('Strike')
plt.ylabel('Volatility')

# Change X axis to use MONEYNESS
surface_parameters.x_axis = fxv.XAxisEnum.MONEYNESS
# Change Y axis to use TENOR
surface_parameters.y_axis = fxv.YAxisEnum.TENOR

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = fxv.calculate(universe=[request_item])

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

vol_surface = response['data'][0]['surface']
expiries = vol_surface[0][1:]
moneyness_axis = []
values = []
for row in vol_surface[1:]:
    moneyness_axis.append(row[0])
    values.append(row[1:])

# Change ATM to O, more relevant for moneyness
moneyness_axis[moneyness_axis.index("ATM")] = 0

surface_df = pd.DataFrame(values, index=moneyness_axis, columns=expiries).T
display(surface_df.astype(float).round(2))

plt.figure()
plt.figure(figsize=(10, 5), dpi=150)
for tenor in list(surface_df.index)[0:4]:
    plt.plot(surface_df.columns.map(float), surface_df.T[tenor], label = tenor)
plt.title(f"Volatility Smiles by Expiry", fontdict={'fontweight':'bold','fontsize':15})
plt.legend(loc='upper right')
plt.xlabel('Moneyness')
plt.ylabel('Volatility')
