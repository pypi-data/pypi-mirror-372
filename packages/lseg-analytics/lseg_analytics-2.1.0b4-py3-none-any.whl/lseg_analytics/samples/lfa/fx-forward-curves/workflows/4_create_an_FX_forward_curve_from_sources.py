from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.market_data.fx_forward_curves import IndirectSourcesSwaps
from lseg_analytics.common import TenorType

# Build a new curve from FX Forwards
my_eurgbp_curve = fx_forward_curves.create_from_fx_forwards(
    cross_currency="EURGBP",
    reference_currency="USD",
    sources=IndirectSourcesSwaps(
        base_fx_forwards="RFB"
        ),
    additional_tenor_types=[TenorType.ODD, TenorType.LONG]
)

my_eurgbp_curve.description.summary = "My EURGBP curve from FxForward"

# Save the curve in the user storage space
my_eurgbp_curve.save(space="HOME", name="EURGBP_curve_from_FxForward")

# Build a new curve from Deposits
my_eurgbp_curve = fx_forward_curves.create_from_deposits(
    cross_currency="EURGBP",
    additional_tenor_types=[TenorType.ODD, TenorType.LONG]
)

my_eurgbp_curve.description.summary = "My EURGBP curve from Deposits"

# Save the curve in the user storage space
my_eurgbp_curve.save(space="HOME", name="EURGBP_curve_from_Deposits")

# ------------------------------------------------------------------------------
# Clean up
fx_forward_curves.delete(space="HOME", name="EURGBP_curve_from_Deposits")
fx_forward_curves.delete(space="HOME", name="EURGBP_curve_from_FxForward")