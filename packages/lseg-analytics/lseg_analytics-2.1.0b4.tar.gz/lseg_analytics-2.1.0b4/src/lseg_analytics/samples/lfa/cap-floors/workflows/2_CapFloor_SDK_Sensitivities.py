from lseg_analytics.instruments import cap_floor as cf

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from IPython.display import display

# 1. Define the cap instrument
cap_definition = cf.IPACapFloorDefinition(
    buy_sell = cf.IPABuySellEnum.BUY.value,                                   # Buy cap protection
    cap_strike_percent = 2.0,                                                 # 2% strike rate
    start_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),              # Start date
    end_date = dt.datetime.strptime("2030-01-01", "%Y-%m-%d"),                # Maturity date
    notional_amount = 1_000_000,                                              # $1M notional
    notional_ccy = "USD",                                                     # USD currency
    index_name = "SOFR",                                                      # SOFR index
    index_tenor = "ON",
    interest_payment_frequency = cf.IndexResetFrequencyEnum.QUARTERLY.value,  # Quarterly payments
)

cap_instrument = cf.IPACapFloorDefinitionInstrument(definition = cap_definition)
print("Instrument definition created")

# 2. Configure pricing parameters
pricing_params = cf.CapFloorPricingParameters(
    valuation_date = dt.datetime.strptime("2025-07-18", "%Y-%m-%d"),                
)
print("Pricing parameters configured")

#  Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

response = cf.price(
    definitions = [cap_instrument],
    pricing_preferences = pricing_params
)

print("Pricing execution completed")

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Extract Cap/Floor level Greeks directly (non-array values)
cap_greeks_data = {greek: value for greek, value in greeks.items() if not isinstance(value, list)}

# Convert the dictionary to a DataFrame
df_cap_greeks = pd.DataFrame(list(cap_greeks_data.items()), columns=["Greeks", "Value"])

# Display the DataFrame with Cap/Floor level Greeks
display(df_cap_greeks) 

print("DV01 (Deal Currency):", greeks.dv01_amount_in_deal_ccy)
print("Delta (%):", greeks.delta_percent)
print("Vega (Deal Currency):", greeks.vega_amount_in_deal_ccy)

# Extract caplets Greeks directly from response and create DataFrame
caplets_data = {greek: values for greek, values in greeks.items() if isinstance(values, list)}
df_caplets_greeks = pd.DataFrame(caplets_data)

# Caplets Greeks DataFrame
display(df_caplets_greeks)

# Create figure with specified size
plt.figure(figsize=(10, 6))

# Create bar plot for each Greek value
bars = plt.bar(df_cap_greeks.index, df_cap_greeks["Value"], color='skyblue', align='center')

# Set chart title and labels
plt.title("Cap/Floor Greeks")
plt.ylabel("Value")

# Set x-axis to show Greek names with rotation for readability
plt.xticks(ticks=df_cap_greeks.index, labels=df_cap_greeks["Greeks"], rotation=45, ha='right')

# Add grid lines for better value reading
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom')

# Adjust layout to prevent label cutoff
plt.tight_layout()
plt.show()