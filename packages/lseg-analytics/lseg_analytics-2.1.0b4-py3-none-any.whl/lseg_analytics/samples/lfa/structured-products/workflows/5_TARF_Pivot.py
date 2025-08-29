from lseg_analytics.instruments import structured_products as sp

import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

TARF_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "TARF_Pivot",
    inputs = [
        sp.NameTypeValue(name="Underlying", type = "string", value="USDEUR"),
        sp.NameTypeValue(name="StartDate", type = "date", value= dt.date(2022, 1, 25)),
        sp.NameTypeValue(name="EndDate", type = "string", value="StartDate + 1Y"),
        sp.NameTypeValue(name="Frequency", type = "string", value="1M"),
        sp.NameTypeValue(name="Notional", type = "string", value="1000000"),
        sp.NameTypeValue(name="UpperStrike", type = "string", value="0.9"),
        sp.NameTypeValue(name="Pivot", type = "string", value="0.85"),
        sp.NameTypeValue(name="LowerStrike", type = "string", value="0.8"),
        sp.NameTypeValue(name="Leverage", type = "string", value="2"),
        sp.NameTypeValue(name="ProfitTarget", type = "string", value="0.05"),
        sp.NameTypeValue(name="KO_Payment", type = "string", value="Settlement[t]"),
    ],
    payoff_description = [
					[
						"ScheduleType",
						"Schedule description",
						"FX",
						"BuyerSideCoupon",
						"SellerSideCoupon",
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
						"",
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
						"If(FX[t] < Pivot, If(FX[t] < LowerStrike, Leverage  * Notional * (FX[t] - LowerStrike), Notional * (FX[t] - LowerStrike)), 0)",
						"If(FX[t] >= Pivot, If(FX[t] < UpperStrike, Notional * (UpperStrike - FX[t]), Leverage * Notional * (UpperStrike - FX[t])), 0)",
						"BuyerSideCoupon[t] + SellerSideCoupon[t]",
						"Sum[LastDate-1] + If(FX[t] < Pivot, Max(FX[t] - LowerStrike, 0), Max(UpperStrike - FX[t], 0))",
						"If(Sum[t] >= ProfitTarget, 0, Alive[LastDate - 1])",
						"Alive[LastDate - 1] * (1 - Alive[LastDate]) * KO_Payment",
						"Alive[t] * Settlement[t] + KO_Amount[t]"
					],
					[
						"AtDate",
						"EndDate",
						"FxSpot(Underlying)",
						"If(FX[t] < Pivot, If(FX[t] < LowerStrike, Leverage  * Notional * (FX[t] - LowerStrike), Notional * (FX[t] - LowerStrike)), 0)",
						"If(FX[t] >= Pivot, If(FX[t] < UpperStrike, Notional * (UpperStrike - FX[t]), Leverage * Notional * (UpperStrike - FX[t])), 0)",
						"BuyerSideCoupon[t] + SellerSideCoupon[t]",
						"Sum[LastDate-1] + If(FX[t] < Pivot, Max(FX[t] - LowerStrike, 0), Max(UpperStrike - FX[t], 0))",
						"If(Sum[t] >= ProfitTarget, 0, Alive[LastDate - 1])",
						"Alive[LastDate - 1] * (1 - Alive[LastDate]) * KO_Payment",
						"Alive[t] * Settlement[t] + KO_Amount[t]"
					]
				]
)

# 2. Create SP instrument definition object

tarf_pivot = sp.StructuredProductsDefinitionInstrument(definition = TARF_definition)
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
    definitions=[tarf_pivot],
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
df_BuyerSideCoupon = pd.DataFrame(cashflows[1]['payments']).rename(columns={'amount': cashflows[1]['legTag']})
df_SellerSideCoupon = pd.DataFrame(cashflows[2]['payments']).rename(columns={'amount': cashflows[2]['legTag']})
df_settlement = pd.DataFrame(cashflows[3]['payments']).rename(columns={'amount': cashflows[3]['legTag']})
df_sum  = pd.DataFrame(cashflows[4]['payments']).rename(columns={'amount': cashflows[4]['legTag']})
df_alive = pd.DataFrame(cashflows[5]['payments']).rename(columns={'amount': cashflows[5]['legTag']})
df_ko_amount = pd.DataFrame(cashflows[6]['payments']).rename(columns={'amount': cashflows[6]['legTag']})
df_price = pd.DataFrame(cashflows[7]['payments']).rename(columns={'amount': cashflows[7]['legTag']})

display(df_fx)
display(df_BuyerSideCoupon)
display(df_SellerSideCoupon)
display(df_settlement)
display(df_sum)
display(df_alive)
display(df_ko_amount)
display(df_price)

# Merge all dataframes on the 'date' column
# Add suffix to distinguish between different data sources
combined_df = pd.concat(
    [df_fx.add_suffix('_fx'), 
     df_BuyerSideCoupon.add_suffix('_buyer_coupon'),
     df_SellerSideCoupon.add_suffix('_seller_coupon'),
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
combined_df = combined_df.loc[:,['date_fx', 'discountFactor_fx', 'FX_fx', 'BuyerSideCoupon_buyer_coupon', 'SellerSideCoupon_seller_coupon', 'Settlement_settlement','Sum_sum',  'Alive_alive',
       'KO_Amount_ko_amount','Price_price', 'currency_fx', 'event_fx','occurence_fx']]

# Rename columns to match the desired layout
combined_df.columns = ['date', 'discountFactor', 'FX', 'BuyerSideCoupon', 'SellerSideCoupon', 'Settlement', 'Sum', 'Alive', 'KO_Amount', 'Price', 'currency', 'event', 'occurrence']

# Display the combined dataframe
display(combined_df)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_tarf_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_tarf_greeks)