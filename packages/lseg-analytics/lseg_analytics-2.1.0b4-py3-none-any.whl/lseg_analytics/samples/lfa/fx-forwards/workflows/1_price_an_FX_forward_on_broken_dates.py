from lseg_analytics.instruments import fx_forwards
from lseg_analytics_basic_client.models import RelativeAdjustableDate, AdjustableDate, ReferenceDate
import pandas as pd
from IPython.display import display

fx_forwards_map = {
    # Create an FX Forward whose start date is spot date, and end date is 3M after the start date.
    "SPOT/3M": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            end_date=RelativeAdjustableDate(
                tenor="3M", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward whose start date is spot date, and end date is the last open day of september after the start date.
    "SPOT/SEPM": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            end_date=RelativeAdjustableDate(
                tenor="SEPM", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward whose start date is spot date, and end date is the first open day of october after the start date.
    "SPOT/OCTM": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            end_date=RelativeAdjustableDate(
                tenor="OCTB", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward whose start date is spot date, and end date is the third Europen Central Bank meeting date after the start date.
    "SPOT/ECB3": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            end_date=RelativeAdjustableDate(
                tenor="ECB3", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward whose start date is spot date, and end date is one month and 15 days after the start date.
    "SPOT/1M15D": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            end_date=RelativeAdjustableDate(
                tenor="1M15D", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward Forward instrument whose start date is 3 months after spot date, and end date is 6 months after the start date
    "3M/6M": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            start_date=RelativeAdjustableDate(
                tenor="3M", reference_date=ReferenceDate.SPOT_DATE
            ),
            end_date=RelativeAdjustableDate(
                tenor="6M", reference_date=ReferenceDate.START_DATE
            ),
            payer="Party1",
            receiver="Party2",
        )
    ),
    # Create an FX Forward Forward instrument whose start date is the January 1rst 2026 (adjusted from holiday), and end date June 1rst 2026 (adjusted from holiday)
    "01JAN2026/06JAN2026": fx_forwards.FxForward(
        definition=fx_forwards.FxForwardDefinition(
            quoted_currency="USD",
            base_currency="EUR",
            start_date=AdjustableDate(date="2026-01-01"),
            end_date=AdjustableDate(date="2026-01-06"),
            payer="Party1",
            receiver="Party2",
        )
    ),
}

# Define the valuation date
valuation_date = "2024-02-11"

# Loop through each FX Forward in the map and price it
pricing_results = {}
for key, fx_forward in fx_forwards_map.items():
    fx_forward.save(name="temp_forward", space="HOME")
    pricing_results[key] = fx_forward.price(
        pricing_preferences=fx_forwards.FxPricingParameters(
            valuation_date=valuation_date
        )
    )
    fx_forwards.delete(name="temp_forward", space="HOME")

results = [
    {
        "Case": key,
        "StartDate": result.analytics.description.start_date.adjusted,
        "EndDate": result.analytics.description.end_date.adjusted,
        "Swap points (Bid)": result.analytics.pricing_analysis.fx_swaps_ccy1_ccy2.bid,
        "Swap points (Ask)": result.analytics.pricing_analysis.fx_swaps_ccy1_ccy2.ask,
    }
    for key, result in pricing_results.items()
]

df = pd.DataFrame(results)
display(df)