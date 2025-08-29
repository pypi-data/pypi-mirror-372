from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.instruments import fx_forwards
from lseg_analytics_basic_client.models import RelativeAdjustableDate, ReferenceDate
import datetime

# Load the EUR/GBP FX Forward curve from the LSEG storage space
eurgbp_curve = fx_forward_curves.load(space="LSEG", name="EUR_GBP_FxForward")

# Create an FX Forward instrument¶
eurgbp_fxfwd = fx_forwards.FxForward(
    definition=fx_forwards.FxForwardDefinition(
        quoted_currency="GBP",
        base_currency="EUR",
        rate=fx_forwards.FxRate(value=0.86),
        end_date=RelativeAdjustableDate(
            tenor="3M", reference_date=ReferenceDate.START_DATE
        ),
        deal_amount=1000000,
        payer="Party1",
        receiver="Party2",
    )
)
eurgbp_fxfwd.save(name="myforward", space="HOME")

market_data = fx_forwards.MarketData()
market_data.fx_forward_curves = [
    fx_forwards.FxForwardCurveChoice(reference="EUR_GBP_FxForward")
]

valuation_response = eurgbp_fxfwd.value(
    market_data=market_data,
    pricing_preferences=fx_forwards.FxPricingParameters(
        valuation_date=datetime.date(2024, 1, 11),
        report_currency="USD",
    ),
)

# Display the valuation analysis
print(valuation_response.analytics.description)
print(
    "\t Market value in deal currency:",
    valuation_response.analytics.valuation.market_value_in_deal_ccy,
)
print(
    "\t Market value in contra currency:",
    valuation_response.analytics.valuation.market_value_in_contra_ccy,
)
print(
    "\t Market value in report currency:",
    valuation_response.analytics.valuation.market_value_in_report_ccy,
)
print("\t Greeks - Delta percent:", valuation_response.analytics.greeks.delta_percent)
print(
    "\t Greeks - Delta amount in deal currency:",
    valuation_response.analytics.greeks.delta_amount_in_deal_ccy,
)
print(
    "\t Greeks - Delta amount in contra currency:",
    valuation_response.analytics.greeks.delta_amount_in_contra_ccy,
)

fx_forwards.delete(name="myforward", space="HOME")