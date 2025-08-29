import pandas as pd
import json
from lseg_analytics.templates.instrument_templates import search, load 
from lseg_analytics.common import SortingOrderEnum
from lseg_analytics.instruments.ir_swaps import load
from lseg_analytics.instruments.ir_swaps import value, IrPricingParameters, IrSwapDefinitionInstrument
from lseg_analytics.instruments.ir_swaps import solve, IrPricingParameters, IrSwapSolvingParameters, IrSwapSolvingTarget, IrSwapSolvingVariable, IrMeasure, IrSwapDefinitionInstrument
from lseg_analytics.instruments.ir_swaps import create_from_vanilla_irs_template, VanillaIrsOverride
from lseg_analytics_basic_client.models import PayerReceiverEnum, ReferenceDate, AdjustableDate, RelativeAdjustableDate, Rate, UnitEnum
from datetime import date
from IPython.display import display

def extract_tag_key(tag):
    return tag.split(":")[0] if ":" in tag else tag

def list_unique_tags(all_swaps):
    unique_tags = set()
    for item in all_swaps:
        tags = item.get("description", {}).get("tags", [])
        for tag in tags:
            key = extract_tag_key(tag)
            unique_tags.add(key)
    return unique_tags

def display_templates(templates):
    unique_tag_keys = list(list_unique_tags(templates))

    rows = []
    for item in templates:
        row = {
            "Space": item.get("location", {}).get("space", ""),
            "Id": item.get("id", ""),
            "Name": item.get("location", {}).get("name", ""),
            "Summary": item.get("description", {}).get("summary", ""),
        }
        tags = item.get("description", {}).get("tags", [])
        tag_dict = {extract_tag_key(tag): tag for tag in tags}
        for key in unique_tag_keys:
            tag_val = tag_dict.get(key, None)
            if tag_val is not None and ":" in tag_val:
                row[key] = tag_val.split(":", 1)[1]
            else:
                row[key] = tag_val
        rows.append(row)

    display(pd.DataFrame(rows))

def build_legs_comparison_df(first_leg, second_leg):
    """Builds a DataFrame comparing key fields of first_leg and second_leg."""
    def get_nested_attr(obj, attrs, default=None):
        for attr in attrs:
            obj = getattr(obj, attr, None)
            if obj is None:
                return default
        return obj

    rows = [
        {
            "Field": "description",
            "First Leg": get_nested_attr(first_leg, ["description", "leg_description"]),
            "Second Leg": get_nested_attr(second_leg, ["description", "leg_description"]),
        },
        {
            "Field": "market value",
            "First Leg": get_nested_attr(first_leg, ["valuation", "market_value", "deal_currency", "value"]),
            "Second Leg": get_nested_attr(second_leg, ["valuation", "market_value", "deal_currency", "value"]),
        },
        {
            "Field": "DV01",
            "First Leg": get_nested_attr(first_leg, ["risk", "dv01", "value"]),
            "Second Leg": get_nested_attr(second_leg, ["risk", "dv01", "value"]),
        },
    ]

    display(pd.DataFrame(rows))

#use the search function to find a USD swap template referenced on SOFR index
sofr_ois = search(
    item_per_page= 1,
    tags=["instrumentType:VanillaSwap", "currency:USD", "index:USD_SOFR_ON"],
    spaces=["LSEG"])

display_templates(sofr_ois)

# define a 1 year forward start date for swap
start_date = RelativeAdjustableDate(tenor = "1Y", reference_date= ReferenceDate.VALUATION_DATE)

# setup a 2Y swap maturity from the start date
end_date = RelativeAdjustableDate(tenor = "2Y", reference_date= ReferenceDate.START_DATE)

# override the OIS with a 1M USD, notional, the previous start_date and end_date, and a 10bp spread on the float leg
par_overrides = VanillaIrsOverride(
    payer_receiver=PayerReceiverEnum.PAYER,
    start_date = start_date,
    end_date=end_date,
    amount=1000000,
    spread=Rate(value=10.0, unit = UnitEnum.BASIS_POINT))

# build the swap from 'LSEG/OIS_SOFR' template and previously defined overrides
fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR", overrides = par_overrides)

fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)

# define solving parameters in order to compute the par fixed rate
solving_params = IrSwapSolvingParameters(
    target=IrSwapSolvingTarget(market_value=IrMeasure(value=0.0)),
    variable= IrSwapSolvingVariable(leg = "FirstLeg", name = "FixedRate"))

# define a solving date
solving_date = date(2025, 5, 10)

# solve the swap par rate
valuation_response = solve(
    definitions=[fwd_start_sofr_def],
    pricing_preferences= IrPricingParameters(
        solving_parameters = solving_params,
        valuation_date=solving_date
    )
)

# print the solved par fixed rate
solved_rate = valuation_response.analytics[0].solving.result

print(
    "\t Solved fixed rate, in %:", solved_rate,
)

build_legs_comparison_df(valuation_response.analytics[0].first_leg, valuation_response.analytics[0].second_leg)

instrument_id = "SOFR_OIS_1Y2Y"

# create a 'booked_trade' updated with the solved fixed rate
trade_overrides = VanillaIrsOverride(
    payer_receiver=PayerReceiverEnum.PAYER,
    start_date = start_date,
    end_date=end_date,
    amount=1000000,
    fixed_rate=Rate(value=solved_rate, unit = UnitEnum.PERCENTAGE),
    spread=Rate(value=10.0, unit = UnitEnum.BASIS_POINT))

# Create the swap using the ESTR template
booked_trade = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR", overrides = trade_overrides)

try:
    # Check if the instrument already exists in HOME space
    booked_trade = load(name=instrument_id, space="HOME")
    print(f"Instrument {instrument_id} already exists in HOME space.")
except:
    # If the instrument does not exist in HOME space, we can save it
    booked_trade.save(name=instrument_id, space="HOME")
    print(f"Instrument {instrument_id} saved in HOME space.")

definition = IrSwapDefinitionInstrument(definition = booked_trade.definition)

# define a mark to market date as of 2025-05-15
mtm_date = date(2025, 5, 15)

# value the  swap
valuation_response = value(
    definitions=[definition],
    pricing_preferences= IrPricingParameters(valuation_date=mtm_date, report_currency="USD")
)

# print mark to market results
print(
    "\t MtM in USD:", valuation_response.analytics[0].valuation.market_value.deal_currency.value,
)

build_legs_comparison_df(valuation_response.analytics[0].first_leg, valuation_response.analytics[0].second_leg)

# Delete the instrument we created in HOME space
from lseg_analytics.instruments.ir_swaps import delete

delete(name=instrument_id, space="HOME")