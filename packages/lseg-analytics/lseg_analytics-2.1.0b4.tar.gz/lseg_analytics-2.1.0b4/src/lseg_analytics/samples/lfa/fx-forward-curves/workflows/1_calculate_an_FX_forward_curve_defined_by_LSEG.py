from lseg_analytics.market_data import fx_forward_curves
from lseg_analytics.helpers import to_rows
from lseg_analytics.market_data.fx_forward_curves import (
    FxForwardCurveCalculationParameters,
)
from IPython.display import display
import pandas as pd

# Load the AUD/CHF FX Forward curve
audchf_curve = fx_forward_curves.load(space="LSEG", name="AUD_CHF_FxForward")

response = audchf_curve.calculate(
    pricing_preferences=FxForwardCurveCalculationParameters(valuation_date="2024-02-07")
)
curve_data = response.analytics.outright_curve

# Convert the curve points to DataFrame and display them
df = pd.DataFrame(to_rows(response.analytics.outright_curve.points))
display(df)

# Clone the curve
cloned_fx_forward = audchf_curve.clone()
  
# Save a newly cloned curve
cloned_fx_forward.save(name="clone_audchf_curve", space="HOME")

# Delete a curve by providing its name
fx_forward_curves.delete(name="clone_audchf_curve")