from lseg_analytics.instruments import structured_products as sp 

import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

TARF_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "TARF_Leveraged_KO",
    inputs = [
        sp.NameTypeValue(name="Underlying", type = "string", value="USDEUR"),
        sp.NameTypeValue(name="StartDate", type = "date", value= dt.date(2022, 1, 25)),
        sp.NameTypeValue(name="EndDate", type = "string", value="StartDate + 1Y"),
        sp.NameTypeValue(name="Frequency", type = "string", value="1M"),
        sp.NameTypeValue(name="Notional", type = "string", value="1000000"),
        sp.NameTypeValue(name="Strike", type = "string", value="0.85"),
        sp.NameTypeValue(name="Barrier", type = "string", value="0.9"),
        sp.NameTypeValue(name="Leverage", type = "string", value="2"),
        sp.NameTypeValue(name="ProfitTarget", type = "string", value="0.05"),
        sp.NameTypeValue(name="KO_Payment", type = "string", value="Settlement[t]"),
    ],
    payoff_description = [
					[
                        "ScheduleType",
                        "Schedule description",
                        "FX",
                        "Coupon",
                        "OTMAlive",
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
                        "1",
                        "",
                        "0",
                        "1",
                        "",
                        ""
                    ],
                    [
                        "OnSchedule",
                        "DateTable(StartDate + Frequency, EndDate, Frequency, ResetGap := 0b)",
                        "FxSpot(Underlying)",
                        "If(FX[t] < Strike, Leverage  * Notional * (FX[t] - Strike), Notional * (FX[t] - Strike))",
                        "If(FX[t] >= Barrier, 0, OTMAlive[LastDate - 1])",
                        "If(Coupon[t] >= 0, Coupon[t], Coupon[t] * OTMAlive[t])",
                        "Sum[LastDate-1] + Max(FX[t] - Strike, 0)",
                        "If(Sum[t] >= ProfitTarget, 0, Alive[LastDate - 1])",
                        "Alive[LastDate - 1] * (1 - Alive[LastDate]) * KO_Payment",
                        "Alive[t] * Settlement[t] + KO_Amount[t]"
                    ],
                    [
                        "AtDate",
                        "EndDate",
                        "FxSpot(Underlying)",
                        "If(FX[t] < Strike, Leverage  * Notional * (FX[t] - Strike), Notional * (FX[t] - Strike))",
                        "If(FX[t] >= Barrier, 0, OTMAlive[LastDate - 1])",
                        "If(Coupon[t] >= 0, Coupon[t], Coupon[t] * OTMAlive[t])",
                        "Sum[LastDate-1] + Max(FX[t] - Strike, 0)",
                        "If(Sum[t] >= ProfitTarget, 0, Alive[LastDate - 1])",
                        "Alive[LastDate - 1] * (1 - Alive[LastDate]) * KO_Payment",
                        "Alive[t] * Settlement[t] + KO_Amount[t]"
                    ]
				]
)

# 2. Create SP instrument definition object

tarf_leveraged_ko = sp.StructuredProductsDefinitionInstrument(definition = TARF_definition)
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
    definitions=[tarf_leveraged_ko],
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
df_OTMAlive = pd.DataFrame(cashflows[2]['payments']).rename(columns={'amount': cashflows[2]['legTag']})
df_settlement = pd.DataFrame(cashflows[3]['payments']).rename(columns={'amount': cashflows[3]['legTag']})
df_sum  = pd.DataFrame(cashflows[4]['payments']).rename(columns={'amount': cashflows[4]['legTag']})
df_alive = pd.DataFrame(cashflows[5]['payments']).rename(columns={'amount': cashflows[5]['legTag']})
df_ko_amount = pd.DataFrame(cashflows[6]['payments']).rename(columns={'amount': cashflows[6]['legTag']})
df_price = pd.DataFrame(cashflows[7]['payments']).rename(columns={'amount': cashflows[7]['legTag']})

display(df_fx)
display(df_coupon)
display(df_OTMAlive)
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
     df_OTMAlive.add_suffix('_OTMAlive'), 
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
combined_df = combined_df.loc[:,['date_fx', 'discountFactor_fx', 'FX_fx', 'Coupon_coupon', 'OTMAlive_OTMAlive', 'Settlement_settlement','Sum_sum',  'Alive_alive',
       'KO_Amount_ko_amount','Price_price', 'currency_fx', 'event_fx','occurence_fx']]

# Rename columns to match the desired layout
combined_df.columns = ['date', 'discountFactor', 'FX', 'Coupon', 'OTMAlive', 'Settlement', 'Sum', 'Alive', 'KO_Amount', 'Price', 'currency', 'event', 'occurrence']

# Display the combined dataframe
display(combined_df)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_tarf_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_tarf_greeks)