from lseg_analytics.instruments import structured_products as sp

import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

TARF_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "BarrierTARF",
    inputs = [
        sp.NameTypeValue(name="Underlying", type = "string", value="USDEUR"),
        sp.NameTypeValue(name="StartDate", type = "date", value= dt.date(2022, 1, 25)),
        sp.NameTypeValue(name="EndDate", type = "string", value="StartDate + 1Y"),
        sp.NameTypeValue(name="Frequency", type = "string", value="2M"),
        sp.NameTypeValue(name="Notional", type = "string", value="100000"),
        sp.NameTypeValue(name="Strike", type = "string", value="1.02"),
        sp.NameTypeValue(name="Barrier", type = "string", value="1.5"),
        sp.NameTypeValue(name="BarrierSide", type = "string", value="1"),
        sp.NameTypeValue(name="ProfitTarget", type = "string", value="100%"),
        sp.NameTypeValue(name="Leverage", type = "string", value="2"),
        sp.NameTypeValue(name="AppliedLeverage", type = "string", value="If(FX[t] <= Strike, 1, If(BarrierSide * FX[t] > BarrierSide * Barrier, Leverage, 0))"),
        sp.NameTypeValue(name="KO_Payment", type = "string", value="Settlement[t]"),
    ],
    payoff_description = [
					[
						"Schedule Type",
						"Schedule description",
						"FX",
						"Coupon",
						"Settlement",
						"Sum",
						"Alive",
						"KO_Amount",
						"Price"
					],
					[
						"AtDate",
						"StartDate",
						"",
						"",
						"0",
						"",
						"IF(ProfitTarget >= 0, 1, 0)",
						"",
						""
					],
					[
						"OnSchedule",
						"DateTable(StartDate + Frequency, EndDate, Frequency, ResetGap := 0b)",
						"FxSpot(Underlying)",
						"AppliedLeverage * (Strike - FX[t]) ",
						"Coupon[t] * Notional",
						"Sum[LastDate] + max(Coupon[t],0)",
						"If(Sum[t] >= ProfitTarget, 0, Alive[LastDate-1])",
						"Alive[LastDate-1] * (1-Alive[LastDate]) * KO_Payment",
						"Receive (Alive[t] * Settlement[t] + KO_Amount[t])"
					],
					[
						"AtDate",
						"EndDate",
						"FxSpot(Underlying)",
						"AppliedLeverage * (Strike - FX[t]) ",
						"Coupon[t] * Notional",
						"Sum[LastDate] + max(Coupon[t],0)",
						"If(Sum[t] >= ProfitTarget, 0, Alive[LastDate-1])",
						"Alive[LastDate-1] * (1-Alive[LastDate]) * KO_Payment",
						"Receive (Alive[t] * Settlement[t] + KO_Amount[t])"
					]
				]
)

# 2. Create SP instrument definition object

barrier_tarf = sp.StructuredProductsDefinitionInstrument(definition = TARF_definition)
print("Instrument definition created")

# 3. Create SP parameters object - optional

TARF_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2022, 3, 16),  # Set your desired valuation date
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    models=[sp.ModelDefinition(
            underlying_code = "USDEUR",
            underlying_tag = "USDEUR",
            underlying_currency = "EUR",
            asset_class = "ForeignExchange",
            model_name= "Heston")]
)
print("Pricing parameters configured")

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

response = sp.price(
    definitions=[barrier_tarf],
    pricing_preferences=TARF_pricing_params,
    market_data=None,
    return_market_data=True,  # or False
    fields=None  # or specify fields as a string
)

print("Pricing execution completed")

# Extract description from response
description = response.data.analytics[0].description

# Convert to dictionary for display
description.as_dict()

# Extract vauation from the response
valuation = response.data.analytics[0].valuation

# Convert the dictionary to a DataFrame
df_tarf_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_tarf_valuation)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows["cashFlows"]

# Build dataframes for all cash flow types
df_fx = pd.DataFrame(cashflows[0]['payments']).rename(columns={'amount': cashflows[0]['legTag']})
df_coupon = pd.DataFrame(cashflows[1]['payments']).rename(columns={'amount': cashflows[1]['legTag']})
df_settlement = pd.DataFrame(cashflows[2]['payments']).rename(columns={'amount': cashflows[2]['legTag']})
df_sum  = pd.DataFrame(cashflows[3]['payments']).rename(columns={'amount': cashflows[3]['legTag']})
df_alive = pd.DataFrame(cashflows[4]['payments']).rename(columns={'amount': cashflows[4]['legTag']})
df_ko_amount = pd.DataFrame(cashflows[5]['payments']).rename(columns={'amount': cashflows[5]['legTag']})
df_price = pd.DataFrame(cashflows[6]['payments']).rename(columns={'amount': cashflows[6]['legTag']})

display(df_fx)
display(df_coupon)
display(df_settlement)
display(df_sum)
display(df_alive)
display(df_ko_amount)
display(df_price)

# Merge all dataframes on the 'date' column
# Add suffix to distinguish between different data sources
combined_df = pd.concat(
    [df_fx.add_suffix('_fx'), 
     df_coupon.add_suffix('_coupon'), 
     df_settlement.add_suffix('_settlement'), 
     df_sum.add_suffix('_sum'), 
     df_alive.add_suffix('_alive'), 
     df_ko_amount.add_suffix('_ko_amount'), 
     df_price.add_suffix('_price')], 
    axis=1
)

# Remove duplicate columns with the same values
combined_df = combined_df.loc[:, ~combined_df.T.duplicated()]

# Keep only one discountFactor column and sort the columns
combined_df = combined_df.loc[:,['date_fx', 'discountFactor_fx', 'FX_fx', 'Coupon_coupon','Settlement_settlement','Sum_sum',  'Alive_alive',
       'KO_Amount_ko_amount','Price_price', 'currency_fx', 'event_fx','occurence_fx']]

# Rename columns to match the desired layout
combined_df.columns = ['date', 'discountFactor', 'FX', 'Coupon', 'Settlement', 'Sum', 'Alive', 'KO_Amount', 'Price', 'currency', 'event', 'occurrence']

# Display the combined dataframe
display(combined_df)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_tarf_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_tarf_greeks)