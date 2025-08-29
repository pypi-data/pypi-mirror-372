from lseg_analytics.instruments import cap_floor as cf

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from IPython.display import display
import matplotlib.dates as mdates

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

# Extract and filter Cap/Floor level valuation data
valuation = response.data.analytics[0].valuation
cap_valuation_data = {k: v for k, v in valuation.items() if not isinstance(v, (list, dict))}

# Convert to DataFrame
df_cap_valuation = pd.DataFrame(list(cap_valuation_data.items()), columns=["Fields", "Value"])

display(df_cap_valuation)

# Extract caplets market values directly from response
caplets_values = valuation["capletsMarketValuesInDealCcyArray"]
df_caplets_values = pd.DataFrame(caplets_values, columns=["Caplets Market Value"])

# Convert caplets values to DataFrame
display(df_caplets_values)

# Extract premium schedule directly from response
premium_schedule = valuation["capFloorPremiumSchedule"]
df_premium_schedule = pd.DataFrame(premium_schedule)

# Convert premium schedule to DataFrame
display(df_premium_schedule)

# Extract pricing analysis from response
pricing_analysis = response.data.analytics[0].pricing_analysis

# Create summary metrics DataFrame
df_pricing_metrics = pd.DataFrame([
    ["Cap Strike (%)", pricing_analysis["capStrikePercent"]],
    ["ATM Strike (%)", pricing_analysis["atmStrikePercent"]],
    ["Implied Volatility (%)", pricing_analysis["impliedVolatilityPercent"]],
    ["Implied Volatility (bp)", pricing_analysis["impliedVolatilityBp"]],
    ["Spread Equivalent (bp)", pricing_analysis["spreadEquivalentBp"]],
    ["Valuation Date", pricing_analysis["valuationDate"]],
    ["Market Data Date", pricing_analysis["marketDataDate"]]
], columns=["Fields", "Value"])

# Convert pricing metrics to DataFrame
display(df_pricing_metrics)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows

# Extract caplets cashflow data directly from response
caplets_cashflow_data = {
    "Start_Date": cashflows["capletsStartDatesArray"],
    "End_Date": cashflows["capletsEndDatesArray"],
    "Strike_Percent": cashflows["capletsStrikePercentArray"],
    "Forward_Rate_Percent": cashflows["capletsForwardRatePercentArray"],
    "Amortization": cashflows["amortizationAmountsInDealCcyArray"],
    "Remaining_Notional": cashflows["capletsRemainingNotionalAmountsInDealCcyArray"],
    "Caplets_Payoff_Amount": cashflows["capletsPayoffAmountsInDealCcyArray"]
}

df_caplets_cashflows = pd.DataFrame(caplets_cashflow_data)

# Convert caplets cashflows to DataFrame
display(df_caplets_cashflows)

# Extract end dates and forward rates from the cashflows dictionary (optimized)
end_dates = pd.to_datetime(cashflows["capletsEndDatesArray"])
forward_rates = cashflows["capletsForwardRatePercentArray"]

# Plot
plt.figure(figsize=(9, 5))
plt.plot(end_dates, forward_rates, marker='o', linestyle='-', color='blue', linewidth=2, markersize=6)

# Enhancements
plt.title("Caplet Forward Rate (%)", fontsize=14, fontweight='bold')
plt.xlabel("Caplet End Date", fontsize=12)
plt.ylabel("Caplet Forward Rate (%)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=120))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Simple extraction and flattening of cashFlows
cf = response.data.analytics[0].cashflows["cashFlows"]
df_cap_cashflows = pd.json_normalize(cf, 'payments', ['instrumentType'])

# Convert cap cashflows to DataFrame
display(df_cap_cashflows)

# Filter and prepare data
df_Cashflows = df_cap_cashflows.dropna(subset=['amount']).copy()
df_Cashflows['date'] = pd.to_datetime(df_Cashflows['date'])

# Plot df_Cashflows
plt.figure(figsize=(12, 6))
plt.bar(df_Cashflows['date'].dt.strftime('%Y-%m-%d'), df_Cashflows['amount'], width=0.8, color='blue')

plt.title('Cashflow Amounts Over Time', fontsize=18, fontweight='bold')
plt.xlabel('Date', fontsize=14)
plt.ylabel('Amount', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()