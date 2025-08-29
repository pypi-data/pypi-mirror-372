from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.market_data.fx_forward_curves import *
from lseg_analytics.common import Quote, QuoteDefinition

# Build a new curve by defining its currencies and constituents
curve_definition = fx_forward_curves.FxForwardCurveDefinition(
    cross_currency="EURUSD",
    constituents=[
        # As USD reference currency is used, EURUSD and GBPUSD fx constituents are required
        FxSpotConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR=")),
            definition=FxSpotConstituentDefinition(template="EURUSD"),
        ),
        DepositFxConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR3MD=")),
            definition=DepositConstituentDefinition(template="EUR", tenor="3M"),
        ),
        DepositFxConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="EUR6MD=")),
            definition=DepositConstituentDefinition(template="EUR", tenor="6M"),
        ),
        DepositFxConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="USD3MD=")),
            definition=DepositConstituentDefinition(template="USD", tenor="3M"),
        ),
        DepositFxConstituent(
            quote=Quote(definition=QuoteDefinition(instrument_code="USD6MD=")),
            definition=DepositConstituentDefinition(template="USD", tenor="6M"),
        ),
    ],
)

my_eurusd_curve = fx_forward_curves.FxForwardCurve(definition=curve_definition)
my_eurusd_curve.description.summary = "My EURUSD FxForward curve from deposits"

# Save the curve in the user storage space
my_eurusd_curve.save(space="HOME", name="EURUSD_FxForward_curve_from_deposits")

# Print the curve to confirm its creation
print(my_eurusd_curve)

fx_forward_curves.delete(space="HOME", name="EURUSD_FxForward_curve_from_deposits")