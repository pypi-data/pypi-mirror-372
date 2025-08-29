from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.market_data.fx_forward_curves import *
from lseg_analytics.common import Quote, QuoteDefinition

# Build a new curve by defining its currencies and constituents
curve_definition = fx_forward_curves.FxForwardCurveDefinition(
    cross_currency="EURGBP",
    reference_currency="USD",
    constituents=[
        # As USD reference currency is used, EURUSD and GBPUSD fx constituents are required
        FxSpotConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR=")),
            definition=FxSpotConstituentDefinition(template="EURUSD"),
        ),
        FxSpotConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="GBP=")),
            definition=FxSpotConstituentDefinition(template="GBPUSD"),
        ),
        FxForwardConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR3M=")),
            definition=FxForwardConstituentDefinition(template="EURUSD", tenor="3M"),
        ),
        FxForwardConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="GBP3M=")),
            definition=FxForwardConstituentDefinition(template="GBPUSD", tenor="3M"),
        ),
        FxForwardConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR6M=")),
            definition=FxForwardConstituentDefinition(template="EURUSD", tenor="6M"),
        ),
        FxForwardConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="GBP6M=")),
            definition=FxForwardConstituentDefinition(template="GBPUSD", tenor="6M"),
        ),
    ],
)

my_eurgbp_curve = fx_forward_curves.FxForwardCurve(definition=curve_definition)
my_eurgbp_curve.description.summary = "My EURGBP FxForward curve"
  
# Save the curve in the user storage space
my_eurgbp_curve.save(space="HOME", name="EURGBP_FxForward_curve")

# Print the curve to confirm its creation
print(my_eurgbp_curve)

fx_forward_curves.delete(space="HOME", name="EURGBP_FxForward_curve")