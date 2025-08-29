from lseg_analytics.instruments import term_deposit as td

import datetime as dt
import json
import pandas as pd
from IPython.display import display

# Create term deposit defintion object
term_deposit_definition = td.TermDepositDefinition(
    end_date = dt.datetime.strptime("2026-05-10", "%Y-%m-%d"),
    notional_ccy = "GBP", 
    notional_amount = 1000000,
    start_tenor = "2M",
    fixed_rate_percent = 4.0
)

# Create term deposit instrument defintion object
term_deposit_instrument = td.TermDepositDefinitionInstrument(
    definition = term_deposit_definition
)

# Create term deposit pricing parameters object - optional
term_deposit_parameters = td.TermDepositPricingParameters(
    valuation_date  = dt.datetime.strptime("2025-07-21", "%Y-%m-%d"),
    report_ccy = "USD"
)

#  Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

term_deposit_response = td.price(
    definitions  =[term_deposit_instrument], 
    pricing_preferences = term_deposit_parameters
)

# Access the description object
description = term_deposit_response.data.analytics[0].description
print(json.dumps(description.as_dict(), indent=4))

# Access the pricing analysis object
pricing_analysis = term_deposit_response.data.analytics[0].pricing_analysis
print(json.dumps(pricing_analysis.as_dict(), indent=4))

# Access to payments/cash-flows
payments = term_deposit_response.data.analytics[0].cashflows.cash_flows[0]["payments"]
df_payments = pd.DataFrame(payments)
display(df_payments)

ir_cash_flow_amount = payments[1]["amount"]
nb_days = nb_days = (description.end_date - description.start_date).days
computed_ir_cash_flow_amount = description.notional_amount * (pricing_analysis.fixed_rate_percent / 100) * (nb_days / 365)
print("Computed interest cash-flow:", computed_ir_cash_flow_amount)
print("Interest cash-flow returned by pricer:", ir_cash_flow_amount)
print("Difference:", computed_ir_cash_flow_amount - ir_cash_flow_amount)