from lseg_analytics.market_data import eq_volatility as ev

import plotly.graph_objects as go
import pandas as pd
import datetime as dt
import copy

print("Step 1: Creating Surface Definition...")

ric = "NVDA.O@RIC"

# Create surface definition object to specify the underlying instrument
surface_definition = ev.EtiSurfaceDefinition(
        instrument_code = ric
        )

print(f"   ✓ Instrument: {surface_definition.instrument_code}")

print("Step 2: Configuring Surface Parameters...")

# Create surface parameters object to define how the surface is calculated
surface_parameters = ev.EtiSurfaceParameters(
    # ------------- core surface params
    calculation_date = dt.datetime.strptime("2025-07-15", "%Y-%m-%d"),
    time_stamp = ev.CurvesAndSurfacesTimeStampEnum.DEFAULT,  # Options: CLOSE, OPEN, SETTLE, DEFAULT
    input_volatility_type = ev.InputVolatilityTypeEnum.IMPLIED,  # Options: IMPLIED, QUOTED
    volatility_model = ev.CurvesAndSurfacesVolatilityModelEnum.SSVI, # Options: SVI, SSVI

    # ----------------- SURFACE LAYOUT CONFIGURATION -------------------
    # Surface axis configuration for output layout
    x_axis = ev.XAxisEnum.STRIKE,  # Options: DATE, DELTA, MONEYNESS, STRIKE, TENOR
    y_axis = ev.YAxisEnum.DATE  # Options: same as X-axis
)

# ============= MODEL COMPARISON SETUP =============

# Create a copy of the surface parameters for comparison
surface_parameters_compare = copy.deepcopy(surface_parameters)

# Change the volatility model for comparison
surface_parameters_compare.volatility_model = ev.CurvesAndSurfacesVolatilityModelEnum.SVI  # SVI model vs SSVI

print("Model Comparison Configuration:")
print(f"   ✓ Model 1: {surface_parameters.volatility_model.value}")
print(f"   ✓ Model 2: {surface_parameters_compare.volatility_model.value}")

print("\n Step 3: Creating Request Item...")

# Create the main request object that combines all configuration
request_item = ev.EtiVolatilitySurfaceRequestItem(
    surface_tag = 'NVDA_Volsurface_SSVI',
    underlying_definition = surface_definition,
    surface_parameters = surface_parameters,
    underlying_type = ev.CurvesAndSurfacesUnderlyingTypeEnum.ETI
)

request_item_compare = copy.deepcopy(request_item)
request_item_compare.surface_tag = 'NVDA_Volsurface_SVI'
request_item_compare.surface_parameters = surface_parameters_compare

print(f"   ✓ Request Item: {request_item}")
print(f"   ✓ Request Item Compare: {request_item_compare}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = ev.calculate(universe=[request_item, request_item_compare])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Surface data points available: {len(surface_data['surface'])}")
    else:
        print("   No surface data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Plotting utils

def get_vol_surface_df(response, index=0):
    """
    Extract and format volatility surface data from API response into a DataFrame.
    
    This function processes the raw volatility surface data from an API response,
    handles various error conditions, and returns a properly formatted DataFrame
    suitable for visualization functions.

    """
    try:
        vol_surface = response['data'][index]['surface']
    except KeyError:
        print("No surface data available in response.")
        return None
    except TypeError:
        print("No surface data available in response.")
        return None

    expiries = vol_surface[0][1:]
    strikes = []
    values = []

    for row in vol_surface[1:]:
        strikes.append(row[0])
        values.append(row[1:])

    strikes = [round(float(s), 2) if isinstance(s, (int, float)) else s for s in strikes]

    surface_df = pd.DataFrame(values, index=strikes, columns=expiries).T
    surface_df = surface_df.astype(float).round(2)

    return surface_df

def plot_volatility_surface_plot(surf_table, x_axis, y_axis, colorscale="Turbo"):
    """
    Create an interactive 3D surface plot of the volatility surface with contour lines.
    
    This function generates a three-dimensional visualization where the x-axis represents
    moneyness/strikes, y-axis represents expiries, and z-axis represents volatility values.
    Contour lines are added for better depth perception.

    Parameters
    ----------
    surf_table : pd.DataFrame
        A DataFrame representing the volatility surface with expiries as index
        and strike prices/moneyness as columns. Values should be volatility levels.
    colorscale : str or list, optional
        Plotly colorscale name (e.g., 'Viridis', 'Turbo', 'Plasma') or custom colorscale list.
        Default is "Turbo".

    Returns
    -------
    plotly.graph_objects.Figure
  
    """
    if len(surf_table) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data to display 3D surface",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18),
            align="center"
        )
        fig.update_layout(
            title=dict(
                text="3D Surface Plot of Volatility Surface",
                x=0.5,
                xanchor="center",
                yanchor="top",
                y=0.95,
                font=dict(size=16)
            ),
            autosize=True,
            height=450,
            margin={"l": 0, "r": 0, "b": 0, "t": 50},
            dragmode=False,
        )
        return fig

    x = surf_table.columns
    y = surf_table.index
    z = surf_table.values

    fig = go.Figure(data=[go.Surface(
        z=z, 
        x=x, 
        y=y, 
        colorscale=colorscale,
        showscale=False,
        contours={
            "y": {
                "show": True,
                "color": "black",
                "highlightcolor": "black",
                "size": 0.05
            },
            "z": {
                "show": True,
                "color": "black",
                "highlightcolor": "black",
                "size": 0.05
            }
        }
    )])

    fig.update_layout(
        title=dict(
            text="3D Surface Plot of Volatility Surface",
            x=0.5,
            xanchor="center",
            yanchor="top",
            y=0.95,
            font=dict(size=16)
        ),
        scene={
            "xaxis_title": x_axis,
            "yaxis_title": y_axis,
            "zaxis_title": "Volatility",
            "xaxis": {"showgrid": True},
            "yaxis": {"showgrid": True},
            "zaxis": {"showgrid": True},
            "camera": {
                "eye": {"x": 0.96, "y": -1.53, "z": 0.39},
                "center": {"x": 0.02, "y": -0.07, "z": -0.21},
                "up": {"x": -0.18, "y": 0.27, "z": 0.95},
                "projection": {"type": "perspective"}
            }
        },
        dragmode=False,
        autosize=True,
        height=450,
        width=800,
    )

    return fig

def plot_surface_smile_by_expiry(surf_table, x_axis, y_axis):
    """
    Create a 2D line plot showing volatility smiles for different expiry dates.
    
    This function plots multiple volatility smile curves, with each curve representing
    a different expiry date. The x-axis shows moneyness/strikes and the y-axis shows
    volatility levels.

    Parameters
    ----------
    surf_table : pd.DataFrame
        A DataFrame with expiries as index and strike prices/moneyness as columns.
        Values should be volatility levels for each expiry-strike combination.

    Returns
    -------
    plotly.graph_objects.Figure
        Interactive line plot with each expiry represented as a separate trace.
        
    """
    fig = go.Figure()

    for expiry in surf_table.index:
        fig.add_trace(go.Scatter(
            x=surf_table.columns.astype(float),
            y=surf_table.loc[expiry],
            mode='lines+markers',
            name=expiry
        ))

    fig.update_layout(
        title=dict(
            text='Surface Smile by Expiry',
            x=0.5,
            xanchor="center",
            yanchor="top",
            y=0.95,
            font=dict(size=16)
        ),
        xaxis_title=x_axis,
        yaxis_title='Volatility',
        legend_title=y_axis,
        template='plotly_white',
        dragmode=False,
        autosize=True,
        height=450,
        width=800,
    )

    return fig

# Convert API response to pandas DataFrame for easier manipulation 
surface_df = get_vol_surface_df(response, index=0)           # SSVI model surface
surface_compare_df = get_vol_surface_df(response, index=1)   # SVI model surface

# Extract axis names for labeling plots
x_axis = surface_parameters.x_axis.name
y_axis = surface_parameters.y_axis.name

print("Surface Comparison Info:") 
print(f"   ✓ SSVI Surface: {surface_df.shape} (rows × columns)")
print(f"   ✓ SVI Surface: {surface_compare_df.shape} (rows × columns)") 
print(f"   ✓ x_axis: {x_axis}") 
print(f"   ✓ y_axis: {y_axis}") 

# Individual Surface Plots
print("SSVI Model Surface:")
plot_volatility_surface_plot(surface_df, x_axis, y_axis)

print("SVI Model Surface:")
plot_volatility_surface_plot(surface_compare_df, x_axis, y_axis)

from IPython.display import display

# Difference Analysis
print("Model Difference (SSVI - SVI):")
diff_df = surface_df - surface_compare_df
display(diff_df)
