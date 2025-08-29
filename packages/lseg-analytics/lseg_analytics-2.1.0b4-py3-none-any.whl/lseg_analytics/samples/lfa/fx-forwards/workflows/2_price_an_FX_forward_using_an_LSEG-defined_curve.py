from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.instruments import fx_forwards
from lseg_analytics_basic_client.models import RelativeAdjustableDate, ReferenceDate

# Load the EUR/GBP FX Forward curve
eurgbp_curve = fx_forward_curves.load(space="LSEG", name="EUR_GBP_FxForward")

eurgbp_fxfwd = fx_forwards.FxForward(
    definition=fx_forwards.FxForwardDefinition(
        quoted_currency="GBP",
        base_currency="EUR",
        rate=fx_forwards.FxRate(value=0.86),
        end_date=RelativeAdjustableDate(
            tenor="3M", reference_date=ReferenceDate.START_DATE
        ),
        start_date=RelativeAdjustableDate(
            tenor="1M", reference_date=ReferenceDate.SPOT_DATE
        ),
        deal_amount=1000000,
        payer="Party1",
        receiver="Party2",
    )
)
eurgbp_fxfwd.save(name="myforward", space="HOME")

market_data = fx_forwards.MarketData()
market_data.fx_forward_curves = [fx_forwards.FxForwardCurveChoice(reference="EUR_GBP_FxForward")]

pricing_response = eurgbp_fxfwd.price(
    market_data=market_data,
    pricing_preferences=fx_forwards.FxPricingParameters(
        valuation_date="2024-02-11",
        ignore_reference_currency_holidays=True, 
        reference_currency="EUR",
    ),
)

# Display the pricing analysis
print(pricing_response.analytics.description)
print("\t Deal amount:", pricing_response.analytics.pricing_analysis.deal_amount)
print("\t Countra amount:", pricing_response.analytics.pricing_analysis.contra_amount)
print("\t FX Spot - Bid:", pricing_response.analytics.pricing_analysis.fx_spot.bid)
print("\t FX Spot - Ask:", pricing_response.analytics.pricing_analysis.fx_spot.ask)
print(
    "\t FX Swaps Ccy1 - Bid:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy1.bid,
)
print(
    "\t FX Swaps Ccy1 - Ask:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy1.ask,
)
print(
    "\t FX Swaps Ccy2 - Bid:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy2.bid,
)
print(
    "\t FX Swaps Ccy2 - Ask:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy2.ask,
)
print(
    "\t FX Swaps Ccy1 Ccy2 - Bid:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy1_ccy2.bid,
)
print(
    "\t FX Swaps Ccy1 Ccy2 - Ask:",
    pricing_response.analytics.pricing_analysis.fx_swaps_ccy1_ccy2.ask,
)
print(
    "\t FX Outright Ccy1 Ccy2 - Bid:",
    pricing_response.analytics.pricing_analysis.fx_outright_ccy1_ccy2.bid,
)
print(
    "\t FX Outright Ccy1 Ccy2 - Ask:",
    pricing_response.analytics.pricing_analysis.fx_outright_ccy1_ccy2.ask,
)

fx_forwards.delete(name="myforward", space="HOME")