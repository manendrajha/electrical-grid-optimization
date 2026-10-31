
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Grid Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"

NAVY = "#14283F"
NAVY_LIGHT = "#203B56"
TEAL = "#159A91"
GREEN = "#36B78F"
AMBER = "#D99A35"
RED = "#D65A5A"
MUTED = "#718096"
WHITE = "#FFFFFF"
BG = "#F3F6F9"
BORDER = "#E1E7ED"


# =========================================================
# APPLICATION STYLING
# =========================================================

st.markdown("""
<style>
    :root {
        --bg: #0B1422;
        --surface: #142238;
        --surface-2: #1A2B42;
        --border: #263B53;
        --text: #EAF1F8;
        --muted: #91A4B9;
        --teal: #36C6A0;
        --cyan: #69BCEB;
        --amber: #E7AD4D;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1600px;
        padding: 2rem 2.5rem 3rem;
    }

    /* Typography */

    h1, h2, h3, h4 {
        color: var(--text) !important;
        font-weight: 650 !important;
        letter-spacing: -0.5px;
    }

    p, label {
        color: var(--text);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background: #101D2D;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] * {
        color: #DCE7F1;
    }

    section[data-testid="stSidebar"] input {
        background: var(--surface-2) !important;
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] {
        background: var(--surface-2) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: var(--text) !important;
    }

    /* Sidebar branding */

    .sidebar-brand {
        font-size: 19px;
        font-weight: 750;
        letter-spacing: 1px;
        color: #FFFFFF;
    }

    .sidebar-subtitle {
        color: #8FA6BD;
        font-size: 10px;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 115px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 13px !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 27px !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button {
        background: var(--teal);
        color: #071923 !important;
        border: none;
        border-radius: 8px;
        font-weight: 650;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #56D9B5;
        border: none;
    }

    /* Inputs */

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    [data-baseweb="select"] {
        background: var(--surface) !important;
    }

    [data-baseweb="select"] * {
        color: var(--text) !important;
    }

    /* Radio and segmented controls */

    [data-testid="stSegmentedControl"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 9px;
    }

    /* Tabs */

    .stTabs [data-baseweb="tab"] {
        color: var(--muted) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--teal) !important;
    }

    /* Dataframes */

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    /* Containers */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    /* Dividers */

    hr {
        border-color: var(--border) !important;
    }

    /* Custom headers */

    .eyebrow {
        color: var(--teal);
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 2px;
        margin-bottom: 7px;
    }

    .page-description {
        color: var(--muted);
        font-size: 14px;
        margin-top: -8px;
    }

    /* Alerts */

    [data-testid="stAlert"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text);
    }

    /* Plotly charts */

    [data-testid="stPlotlyChart"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 8px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data
def load_data():

    energy = pd.read_csv(
        DATA / "energy_data.csv",
        parse_dates=["Timestamp"]
    )

    heuristic = pd.read_csv(
        DATA / "heuristic_simulation_results.csv",
        parse_dates=["Timestamp"]
    )

    optimized = pd.read_csv(
        DATA / "optimized_dispatch_results.csv",
        parse_dates=["Timestamp"]
    )

    return energy, heuristic, optimized


try:
    energy, heuristic, optimized = load_data()

except FileNotFoundError as error:
    st.error(f"Required data file not found: {error}")
    st.stop()


# Join all simulation outputs to historical observations.
simulation = optimized.merge(
    heuristic[
        [
            "Timestamp",
            "forecast_demand",
            "optimized_grid_import",
            "optimized_battery_level",
            "optimized_battery_charged",
            "optimized_battery_discharged",
            "conventional_demand"
        ]
    ],
    on="Timestamp",
    how="inner"
)

simulation = simulation.merge(
    energy[
        [
            "Timestamp",
            "Demand (MW)",
            "Wind (MW)",
            "Solar (MW)"
        ]
    ],
    on="Timestamp",
    how="inner"
)

simulation = simulation.sort_values("Timestamp").reset_index(drop=True)

# Three distinct strategies: baseline, forecast heuristic, offline LP benchmark.
simulation["Conventional"] = simulation["Net_Demand"]
simulation["Forecast Heuristic"] = simulation["optimized_grid_import"]
simulation["Linear Optimizer"] = simulation["Grid_Import"]


# =========================================================
# PLOTLY THEME
# =========================================================



def style_chart(fig, height=400):
    fig.update_layout(
        height=height,

        # Dark chart surfaces
        paper_bgcolor="#142238",
        plot_bgcolor="#142238",

        # Typography
        font=dict(
            family="Arial",
            color="#DCE7F1",
            size=12
        ),

        # Spacing
        margin=dict(l=45, r=25, t=55, b=40),

        # Interactions
        hovermode="x unified",

        # Legend
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
            font=dict(
                color="#B8C8D8",
                size=11
            ),
            bgcolor="rgba(20,34,56,0)"
        ),

        # Tooltip
        hoverlabel=dict(
            bgcolor="#203B56",
            bordercolor="#36C6A0",
            font=dict(
                color="#FFFFFF",
                family="Arial",
                size=12
            )
        )
    )

    # X-axis
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#344B63",
        tickfont=dict(color="#91A4B9", size=10),
        title_font=dict(color="#B8C8D8"),
        zeroline=False
    )

    # Y-axis
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(145,164,185,0.13)",
        showline=False,
        tickfont=dict(color="#91A4B9", size=10),
        title_font=dict(color="#B8C8D8"),
        zeroline=False
    )

    return fig


#
# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

# Sidebar-specific styling
st.markdown("""
<style>
    /* Sidebar layout */
    section[data-testid="stSidebar"] .block-container {
        padding: 2rem 1.1rem 2rem;
    }

    .sidebar-brand-wrapper {
        padding: 8px 4px 18px 4px;
    }

    .sidebar-brand {
        font-size: 19px;
        font-weight: 800;
        letter-spacing: 1.3px;
        color: #EAF1F8;
    }

    .sidebar-subtitle {
        color: #36C6A0;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 7px;
    }

    .sidebar-section-label {
        color: #7189A2;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 1.7px;
        margin: 12px 0 10px 4px;
    }

    .sidebar-info-card {
        background: #142238;
        border: 1px solid #263B53;
        border-radius: 10px;
        padding: 13px;
        margin: 5px 0;
    }

    .sidebar-info-title {
        color: #36C6A0;
        font-size: 9px;
        font-weight: 750;
        letter-spacing: 1.2px;
        margin-bottom: 5px;
    }

    .sidebar-info-value {
        color: #DCE7F1;
        font-size: 12px;
        line-height: 1.5;
    }

    /* Navigation radio buttons */
    section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 5px;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 9px 11px;
        transition: background 0.2s ease;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #1A2B42;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #1A3445;
        border: 1px solid #28566A;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #55DDB8 !important;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-size: 13px;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
        display: none;
    }

    section[data-testid="stSidebar"] [data-testid="stDateInput"] label {
        color: #91A4B9 !important;
        font-size: 12px;
    }

    .sidebar-footer {
        color: #7189A2;
        font-size: 10px;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


# BRANDING
st.sidebar.markdown(
    """
    <div class="sidebar-brand-wrapper">
        <div class="sidebar-brand">◈ GRID INTELLIGENCE</div>
        <div class="sidebar-subtitle">SMART CITY ENERGY SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()


# WORKSPACE NAVIGATION
st.sidebar.markdown(
    '<div class="sidebar-section-label">WORKSPACE</div>',
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Demand Analytics",
        "Energy Management",
        "Battery Operations",
        "Grid Simulator",
        "Data Explorer"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()


# SIMULATION PERIOD
st.sidebar.markdown(
    '<div class="sidebar-section-label">SIMULATION CONTROLS</div>',
    unsafe_allow_html=True
)

minimum_date = simulation["Timestamp"].min().date()
maximum_date = simulation["Timestamp"].max().date()

st.sidebar.caption("Choose the historical evaluation period.")

date_range = st.sidebar.date_input(
    "Analysis period",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date
)

if len(date_range) != 2:
    st.warning("Select a start date and an end date.")
    st.stop()

start_date, end_date = date_range

if start_date > end_date:
    st.error("Invalid date range.")
    st.stop()

start = pd.Timestamp(start_date)
end = pd.Timestamp(end_date) + pd.Timedelta(days=1)

filtered = simulation[
    (simulation["Timestamp"] >= start) &
    (simulation["Timestamp"] < end)
].copy()

if filtered.empty:
    st.warning("No simulation data available for this period.")
    st.stop()


# DATASET INFORMATION
st.sidebar.divider()

st.sidebar.markdown(
    '<div class="sidebar-section-label">DATA INFORMATION</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div class="sidebar-info-card">
        <div class="sidebar-info-title">DATA SOURCE</div>
        <div class="sidebar-info-value">
            Indian National Grid<br>
            Historical observations
        </div>
    </div>

    <div class="sidebar-info-card">
        <div class="sidebar-info-title">TEMPORAL RESOLUTION</div>
        <div class="sidebar-info-value">
            Hourly measurements
        </div>
    </div>

    <div class="sidebar-info-card">
        <div class="sidebar-info-title">EVALUATION MODE</div>
        <div class="sidebar-info-value">
            Chronological held-out test period
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        GRID INTELLIGENCE · 2026<br>
        ENERGY ANALYTICS PLATFORM
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SHARED METRICS
# =========================================================

baseline = filtered["Conventional"]
heuristic_import = filtered["Forecast Heuristic"]
lp_import = filtered["Linear Optimizer"]

baseline_peak = baseline.max()
heuristic_peak = heuristic_import.max()
lp_peak = lp_import.max()

peak_reduction = baseline_peak - lp_peak
peak_reduction_pct = peak_reduction / baseline_peak * 100


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    '<div class="eyebrow">ENERGY INTELLIGENCE PLATFORM</div>',
    unsafe_allow_html=True
)

st.title(page)

st.markdown(
    f'<div class="page-description">'
    f'{start_date} — {end_date} | '
    f'{len(filtered):,} hourly observations'
    f'</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# OVERVIEW
# =========================================================


if page == "Overview":

    # =====================================================
    # PAGE HEADER
    # =====================================================

    st.markdown(
        '<div class="eyebrow">ENERGY INTELLIGENCE / OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.title("Grid Performance Overview")

    st.markdown(
        '<div class="page-description">'
        'Monitor grid demand, evaluate battery-assisted strategies, '
        'and compare optimization performance.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.caption(
        f"Analysis period: {start_date.strftime('%d %b %Y')} "
        f"— {end_date.strftime('%d %b %Y')} "
        f"| {len(filtered):,} hourly observations"
    )

    st.divider()


    # =====================================================
    # KEY PERFORMANCE INDICATORS
    # =====================================================

    st.markdown("### System Performance")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Baseline Peak Import",
            f"{baseline_peak:,.0f} MW",
            help="Maximum grid import under the conventional strategy."
        )

    with c2:
        st.metric(
            "Optimized Peak Import",
            f"{lp_peak:,.0f} MW",
            delta=f"{-peak_reduction:,.0f} MW",
            help="Maximum grid import under the linear optimization strategy."
        )

    with c3:
        st.metric(
            "Peak Reduction",
            f"{peak_reduction_pct:.2f}%",
            help="Percentage reduction in peak grid import compared with the conventional baseline."
        )

    with c4:
        st.metric(
            "Simulation Duration",
            f"{len(filtered):,} hrs",
            help="Number of hourly observations in the selected period."
        )

    st.write("")


    # =====================================================
    # GRID IMPORT COMPARISON
    # =====================================================

    st.markdown("### Grid Import Comparison")

    st.caption(
        "Hourly grid import across the three energy management strategies."
    )

    fig = go.Figure()

    strategies = [
        ("Conventional", "Conventional Grid", "#91A4B9", "solid"),
        ("Forecast Heuristic", "Forecast Heuristic", "#E7AD4D", "solid"),
        ("Linear Optimizer", "Linear Optimizer", "#36C6A0", "solid")
    ]

    for column, label, color, dash in strategies:

        fig.add_trace(go.Scatter(
            x=filtered["Timestamp"],
            y=filtered[column],
            name=label,
            mode="lines",
            line=dict(
                color=color,
                width=2,
                dash=dash
            ),
            hovertemplate=(
                "<b>" + label + "</b><br>"
                "Time: %{x}<br>"
                "Grid Import: %{y:,.0f} MW"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Grid Import (MW)"
    )

    st.plotly_chart(
        style_chart(fig, 440),
        use_container_width=True
    )


    # =====================================================
    # STRATEGY PERFORMANCE
    # =====================================================

    st.markdown("### Strategy Performance")

    st.caption(
        "Comparison of grid import statistics across the selected period."
    )

    summary = pd.DataFrame({
        "Strategy": [
            "Conventional Grid",
            "Forecast Heuristic",
            "Linear Optimizer"
        ],
        "Peak Import (MW)": [
            baseline.max(),
            heuristic_import.max(),
            lp_import.max()
        ],
        "Average Import (MW)": [
            baseline.mean(),
            heuristic_import.mean(),
            lp_import.mean()
        ],
        "Total Imports (MWh)": [
            baseline.sum(),
            heuristic_import.sum(),
            lp_import.sum()
        ],
        "95th Percentile (MW)": [
            baseline.quantile(0.95),
            heuristic_import.quantile(0.95),
            lp_import.quantile(0.95)
        ]
    })

    st.dataframe(
        summary.round(2),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Strategy": st.column_config.TextColumn(
                "Energy Strategy"
            ),
            "Peak Import (MW)": st.column_config.NumberColumn(
                "Peak Import",
                format="%,.2f MW"
            ),
            "Average Import (MW)": st.column_config.NumberColumn(
                "Average Import",
                format="%,.2f MW"
            ),
            "Total Imports (MWh)": st.column_config.NumberColumn(
                "Total Imports",
                format="%,.2f MWh"
            ),
            "95th Percentile (MW)": st.column_config.NumberColumn(
                "95th Percentile",
                format="%,.2f MW"
            )
        }
    )

    st.write("")


    # =====================================================
    # INTERPRETATION
    # =====================================================

    st.markdown("### Performance Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">
                    FORECAST-GUIDED CONTROL
                </div>
                <div class="sidebar-info-value">
                    The heuristic controller uses demand forecasts
                    to make battery charging and discharging decisions.
                    Its performance depends on forecast accuracy and
                    available battery capacity.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="sidebar-info-card">
                <div class="sidebar-info-title">
                    LINEAR OPTIMIZATION BENCHMARK
                </div>
                <div class="sidebar-info-value">
                    The linear optimizer uses actual demand across
                    the evaluation horizon to minimize peak grid import.
                    It is an offline benchmark, not a deployable
                    real-time controller.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.info(
        "Interpretation note: The linear optimizer has access to "
        "future actual demand over the selected evaluation horizon. "
        "Its results should therefore be treated as an offline "
        "benchmark rather than a directly comparable real-time "
        "forecasting controller."
    )





# =========================================================

# DEMAND ANALYTICS

# =========================================================

elif page == "Demand Analytics":

    st.markdown(

        '<div class="eyebrow">ENERGY INTELLIGENCE / DEMAND</div>',

        unsafe_allow_html=True

    )

    st.title("Demand & Renewable Analytics")

    st.caption("Explore electricity demand, renewable generation patterns, and forecast accuracy.")

    renewable = (

        filtered["Wind (MW)"] +

        filtered["Solar (MW)"].clip(lower=0)

    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Average Demand", f"{filtered['Demand (MW)'].mean():,.0f} MW")

    c2.metric("Average Wind", f"{filtered['Wind (MW)'].mean():,.0f} MW")

    c3.metric("Average Solar", f"{filtered['Solar (MW)'].clip(lower=0).mean():,.0f} MW")

    c4.metric("Average Renewables", f"{renewable.mean():,.0f} MW")

    st.divider()

    # Demand and generation trends

    st.markdown("### Demand & Generation Trends")

    st.caption("Hourly electricity demand and renewable generation over the selected period.")

    fig = go.Figure()

    for column, label, color in [

        ("Demand (MW)", "Electricity Demand", "#69BCEB"),

        ("Wind (MW)", "Wind Generation", "#36C6A0"),

        ("Solar (MW)", "Solar Generation", "#E7AD4D")

    ]:

        values = filtered[column]

        if label == "Solar Generation":

            values = values.clip(lower=0)

        fig.add_trace(go.Scatter(

            x=filtered["Timestamp"],

            y=values,

            name=label,

            mode="lines",

            line=dict(color=color, width=2),

            hovertemplate=(

                f"<b>{label}</b><br>"

                "Time: %{x}<br>"

                "Generation / Demand: %{y:,.0f} MW"

                "<extra></extra>"

            )

        ))

    fig.update_layout(

        xaxis_title="Time",

        yaxis_title="Power (MW)"

    )

    st.plotly_chart(style_chart(fig, 420), use_container_width=True)

    # Hourly demand pattern

    st.markdown("### Daily Demand Pattern")

    st.caption("Average demand for each hour of the day across the selected period.")

    hourly = (

        filtered.assign(Hour=filtered["Timestamp"].dt.hour)

        .groupby("Hour")["Demand (MW)"]

        .mean()

        .reset_index()

    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=hourly["Hour"],

        y=hourly["Demand (MW)"],

        mode="lines+markers",

        name="Average Demand",

        line=dict(color="#36C6A0", width=3),

        marker=dict(size=6),

        fill="tozeroy",

        fillcolor="rgba(54,198,160,0.10)"

    ))

    fig.update_layout(

        xaxis=dict(

            title="Hour of Day",

            tickmode="linear",

            dtick=2

        ),

        yaxis_title="Average Demand (MW)"

    )

    st.plotly_chart(style_chart(fig, 340), use_container_width=True)

    # Forecast comparison

    st.markdown("### Actual vs Forecast Demand")

    st.caption("Comparison of observed demand and one-hour-ahead model predictions.")

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=filtered["Timestamp"],

        y=filtered["Demand (MW)"],

        name="Actual Demand",

        line=dict(color="#69BCEB", width=2)

    ))

    fig.add_trace(go.Scatter(

        x=filtered["Timestamp"],

        y=filtered["forecast_demand"],

        name="Forecast Demand",

        line=dict(color="#E7AD4D", width=2, dash="dash")

    ))

    fig.update_layout(

        xaxis_title="Time",

        yaxis_title="Demand (MW)"

    )

    st.plotly_chart(style_chart(fig, 400), use_container_width=True)

    st.markdown("### Forecast Model Performance")

    m1, m2, m3 = st.columns(3)

    m1.metric("MAE", "2,451.51 MW")

    m2.metric("RMSE", "3,820.39 MW")

    m3.metric("R² Score", "0.9244")

    st.caption(

        "Metrics represent the chronological held-out test set, "

        "not a recalculation for the currently selected date range."

    )



# =========================================================

# ENERGY MANAGEMENT

# =========================================================

elif page == "Energy Management":

    st.markdown(

        '<div class="eyebrow">ENERGY INTELLIGENCE / STRATEGIES</div>',

        unsafe_allow_html=True

    )

    st.title("Energy Management")

    st.caption("Compare conventional grid operation, forecast-guided battery control, and linear optimization.")

    strategies = [

        "Conventional",

        "Forecast Heuristic",

        "Linear Optimizer"

    ]

    colors = {

        "Conventional": "#91A4B9",

        "Forecast Heuristic": "#E7AD4D",

        "Linear Optimizer": "#36C6A0"

    }

    selected_strategies = st.multiselect(

        "Compare strategies",

        strategies,

        default=strategies

    )

    if not selected_strategies:

        st.warning("Select at least one strategy to display the comparison.")

        st.stop()

    st.divider()

    # Grid import comparison

    st.markdown("### Grid Import Comparison")

    st.caption("Observe how each strategy changes the amount of power imported from the grid.")

    fig = go.Figure()

    for strategy in selected_strategies:

        fig.add_trace(go.Scatter(

            x=filtered["Timestamp"],

            y=filtered[strategy],

            name=strategy,

            mode="lines",

            line=dict(

                color=colors[strategy],

                width=2

            )

        ))

    fig.update_layout(

        xaxis_title="Time",

        yaxis_title="Grid Import (MW)"

    )

    st.plotly_chart(style_chart(fig, 440), use_container_width=True)

    # Peak import comparison

    st.markdown("### Peak Import Comparison")

    st.caption("Maximum grid import recorded for each strategy in the selected period.")

    peak_table = pd.DataFrame({

        "Strategy": strategies,

        "Peak Import (MW)": [

            baseline.max(),

            heuristic_import.max(),

            lp_import.max()

        ]

    })

    fig = go.Figure()

    for strategy in selected_strategies:

        value = peak_table.loc[

            peak_table["Strategy"] == strategy,

            "Peak Import (MW)"

        ].iloc[0]

        fig.add_trace(go.Bar(

            x=[strategy],

            y=[value],

            name=strategy,

            marker_color=colors[strategy],

            text=[f"{value:,.0f} MW"],

            textposition="outside"

        ))

    fig.update_layout(

        showlegend=False,

        yaxis_title="Peak Grid Import (MW)",

        xaxis_title="Strategy",

        margin=dict(t=45, b=45)

    )

    st.plotly_chart(style_chart(fig, 350), use_container_width=True)

    # Performance metrics

    st.markdown("### Detailed Performance")

    metrics = pd.DataFrame({

        "Metric": [

            "Peak Import (MW)",

            "95th Percentile (MW)",

            "Average Import (MW)",

            "Total Imports (MWh)"

        ],

        "Conventional": [

            baseline.max(),

            baseline.quantile(0.95),

            baseline.mean(),

            baseline.sum()

        ],

        "Forecast Heuristic": [

            heuristic_import.max(),

            heuristic_import.quantile(0.95),

            heuristic_import.mean(),

            heuristic_import.sum()

        ],

        "Linear Optimizer": [

            lp_import.max(),

            lp_import.quantile(0.95),

            lp_import.mean(),

            lp_import.sum()

        ]

    })

    st.dataframe(

        metrics.round(2),

        use_container_width=True,

        hide_index=True

    )

    st.info(

        "Benchmark limitation: The linear optimizer uses actual demand "

        "over the complete optimization horizon. It is an offline "

        "perfect-information benchmark, not a real-time controller."

    )



# =========================================================

# BATTERY OPERATIONS

# =========================================================

elif page == "Battery Operations":

    st.markdown(

        '<div class="eyebrow">ENERGY INTELLIGENCE / STORAGE</div>',

        unsafe_allow_html=True

    )

    st.title("Battery Operations")

    st.caption("Monitor battery state of charge, charging activity, and discharging behaviour.")

    BATTERY_CAPACITY = 25000

    MAX_POWER = 5000

    # Battery KPIs

    total_charging = filtered["Battery_Charging"].sum()

    total_discharging = filtered["Battery_Discharging"].sum()

    current_soc = filtered["Battery_Level"].iloc[-1]

    average_soc = filtered["Battery_Level"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Battery Capacity", f"{BATTERY_CAPACITY:,} MWh")

    c2.metric("Final State of Charge", f"{current_soc:,.0f} MWh")

    c3.metric("Total Charging", f"{total_charging:,.0f} MWh")

    c4.metric("Total Discharging", f"{total_discharging:,.0f} MWh")

    st.divider()

    # State of charge

    st.markdown("### Battery State of Charge")

    st.caption("Stored energy over the selected simulation period.")

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=filtered["Timestamp"],

        y=filtered["Battery_Level"],

        name="Battery SOC",

        mode="lines",

        fill="tozeroy",

        line=dict(color="#36C6A0", width=2),

        fillcolor="rgba(54,198,160,0.12)"

    ))

    fig.add_hline(

        y=BATTERY_CAPACITY,

        line_dash="dash",

        line_color="#E7AD4D",

        annotation_text="Maximum capacity"

    )

    fig.add_hline(

        y=2500,

        line_dash="dot",

        line_color="#91A4B9",

        annotation_text="Initial SOC"

    )

    fig.update_layout(

        xaxis_title="Time",

        yaxis_title="Stored Energy (MWh)",

        yaxis=dict(range=[0, BATTERY_CAPACITY * 1.08])

    )

    st.plotly_chart(style_chart(fig, 400), use_container_width=True)

    # Charging and discharging

    st.markdown("### Charging & Discharging Activity")

    st.caption("Charging is positive; discharging is displayed below zero for comparison.")

    fig = go.Figure()

    fig.add_trace(go.Bar(

        x=filtered["Timestamp"],

        y=filtered["Battery_Charging"],

        name="Charging",

        marker_color="#36C6A0"

    ))

    fig.add_trace(go.Bar(

        x=filtered["Timestamp"],

        y=-filtered["Battery_Discharging"],

        name="Discharging",

        marker_color="#E7AD4D"

    ))

    fig.update_layout(

        barmode="relative",

        xaxis_title="Time",

        yaxis_title="Battery Power (MW)"

    )

    st.plotly_chart(style_chart(fig, 380), use_container_width=True)

    # Battery statistics

    st.markdown("### Battery Statistics")

    battery_stats = pd.DataFrame({

        "Metric": [

            "Total Charging",

            "Total Discharging",

            "Average SOC",

            "Maximum SOC",

            "Minimum SOC",

            "Final SOC"

        ],

        "Value": [

            total_charging,

            total_discharging,

            average_soc,

            filtered["Battery_Level"].max(),

            filtered["Battery_Level"].min(),

            current_soc

        ],

        "Unit": [

            "MWh",

            "MWh",

            "MWh",

            "MWh",

            "MWh",

            "MWh"

        ]

    })

    st.dataframe(

        battery_stats.round(2),

        use_container_width=True,

        hide_index=True

    )

    st.caption(

        f"Battery operating limits: maximum charging power "

        f"{MAX_POWER:,} MW | maximum discharging power "

        f"{MAX_POWER:,} MW | round-trip efficiency assumptions "

        f"are applied in the simulation."

    )




# =========================================================
# GRID SIMULATOR
# =========================================================

elif page == "Grid Simulator":

    from src.simulation.grid_visualization import render_grid_animation

    # -----------------------------------------------------
    # PAGE HEADER
    # -----------------------------------------------------

    st.markdown(
        '<div class="eyebrow">ENERGY INTELLIGENCE / LIVE SIMULATION</div>',
        unsafe_allow_html=True
    )

    st.title("Interactive Grid Simulator")

    st.caption(
        "Explore energy flows and battery dispatch decisions "
        "under different grid-management strategies."
    )

    st.divider()

    # -----------------------------------------------------
    # SIMULATION CONTROLS
    # -----------------------------------------------------

    st.markdown("### Simulation Controls")

    control1, control2 = st.columns([2, 1])

    with control1:
        selected_index = st.slider(
            "Select simulation hour",
            min_value=0,
            max_value=len(filtered) - 1,
            value=0,
            key="grid_simulation_hour"
        )

    with control2:
        speed = st.select_slider(
            "Animation speed",
            options=[1.0, 1.5, 2.5, 4.0],
            value=2.5
        )

    row = filtered.iloc[selected_index]

    timestamp = row["Timestamp"]

    st.caption(
        f"Selected observation: {timestamp.strftime('%d %B %Y, %H:%M')} "
        f"| Observation {selected_index + 1:,} of {len(filtered):,}"
    )

    strategy = st.segmented_control(
        "Operating strategy",
        [
            "Conventional",
            "Forecast Heuristic",
            "Linear Optimizer"
        ],
        default="Forecast Heuristic",
        key="grid_strategy"
    )

    if strategy is None:
        strategy = "Forecast Heuristic"

    # -----------------------------------------------------
    # ENERGY FLOW INPUTS
    # -----------------------------------------------------

    demand = float(row["Demand (MW)"])
    wind = float(row["Wind (MW)"])
    solar = max(0.0, float(row["Solar (MW)"]))

    if strategy == "Conventional":

        grid_import = float(row["Conventional"])
        charge = 0.0
        discharge = 0.0
        soc = 0.0

    elif strategy == "Forecast Heuristic":

        grid_import = float(row["optimized_grid_import"])
        charge = float(row["optimized_battery_charged"])
        discharge = float(row["optimized_battery_discharged"])
        soc = float(row["optimized_battery_level"])

    else:

        grid_import = float(row["Grid_Import"])
        charge = float(row["Battery_Charging"])
        discharge = float(row["Battery_Discharging"])
        soc = float(row["Battery_Level"])

    # -----------------------------------------------------
    # STRATEGY DESCRIPTION
    # -----------------------------------------------------

    descriptions = {
        "Conventional": (
            "BASELINE OPERATION",
            "Renewable generation is utilized first, with remaining "
            "demand supplied by the conventional grid. Battery dispatch "
            "is disabled."
        ),
        "Forecast Heuristic": (
            "FORECAST-GUIDED CONTROL",
            "Predicted demand informs battery charging and discharging "
            "decisions. This represents a forecast-based heuristic "
            "energy management approach."
        ),
        "Linear Optimizer": (
            "OFFLINE OPTIMIZATION BENCHMARK",
            "Linear programming determines battery dispatch using "
            "actual demand across the complete evaluation horizon. "
            "This is an offline benchmark, not a real-time controller."
        )
    }

    description_title, description_text = descriptions[strategy]

    st.markdown(
        f"""
        <div class="sidebar-info-card">
            <div class="sidebar-info-title">{description_title}</div>
            <div class="sidebar-info-value">{description_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # GRID VISUALIZATION
    # -----------------------------------------------------

    st.markdown("### Energy Flow Visualization")

    st.caption(
        "The visualization represents the selected hour and "
        "the energy management strategy currently in operation."
    )

    render_grid_animation(
        demand=demand,
        wind=wind,
        solar=solar,
        grid_import=grid_import,
        battery_charge=charge,
        battery_discharge=discharge,
        battery_soc=soc,
        battery_capacity=25000,
        mode=strategy,
        speed=speed
    )

    st.divider()

    # -----------------------------------------------------
    # CURRENT OPERATING CONDITIONS
    # -----------------------------------------------------

    st.markdown("### Current Operating Conditions")

    renewable_generation = wind + solar

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "City Demand",
        f"{demand:,.0f} MW"
    )

    c2.metric(
        "Renewable Generation",
        f"{renewable_generation:,.0f} MW"
    )

    c3.metric(
        "Grid Import",
        f"{grid_import:,.0f} MW"
    )

    c4.metric(
        "Battery SOC",
        "Not dispatched" if strategy == "Conventional"
        else f"{soc:,.0f} MWh"
    )

    # Battery activity
    if strategy != "Conventional":

        st.markdown("### Battery Dispatch")

        b1, b2, b3 = st.columns(3)

        b1.metric("Charging Power", f"{charge:,.0f} MW")
        b2.metric("Discharging Power", f"{discharge:,.0f} MW")
        b3.metric(
            "State of Charge",
            f"{(soc / 25000) * 100:.1f}%"
        )

    st.divider()

    # -----------------------------------------------------
    # STRATEGY COMPARISON
    # -----------------------------------------------------

    st.markdown("### Strategy Comparison at Selected Hour")

    st.caption(
        "Compare grid import requirements across all three "
        "strategies for the same timestamp."
    )

    comparison = pd.DataFrame({
        "Strategy": [
            "Conventional",
            "Forecast Heuristic",
            "Linear Optimizer"
        ],
        "Grid Import (MW)": [
            float(row["Conventional"]),
            float(row["Forecast Heuristic"]),
            float(row["Linear Optimizer"])
        ]
    })

    strategy_colors = {
        "Conventional": "#91A4B9",
        "Forecast Heuristic": "#E7AD4D",
        "Linear Optimizer": "#36C6A0"
    }

    fig = go.Figure()

    for _, item in comparison.iterrows():

        fig.add_trace(go.Bar(
            x=[item["Strategy"]],
            y=[item["Grid Import (MW)"]],
            name=item["Strategy"],
            marker_color=strategy_colors[item["Strategy"]],
            text=[f"{item['Grid Import (MW)']:,.0f} MW"],
            textposition="outside",
            showlegend=False
        ))

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Grid Import (MW)",
        margin=dict(t=50, b=40)
    )

    st.plotly_chart(
        style_chart(fig, 350),
        use_container_width=True
    )

    st.dataframe(
        comparison.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "The Linear Optimizer is an offline perfect-information "
        "benchmark. It uses actual future demand across the "
        "optimization horizon and should not be interpreted as "
        "a deployable real-time controller."
    )




# =========================================================
# DATA EXPLORER
# =========================================================

elif page == "Data Explorer":

    st.markdown(
        '<div class="eyebrow">ENERGY INTELLIGENCE / DATA</div>',
        unsafe_allow_html=True
    )

    st.title("Simulation Data Explorer")

    st.caption(
        "Inspect historical observations, simulation outputs, "
        "and battery dispatch records."
    )

    st.divider()

    # -----------------------------------------------------
    # DATASET SELECTION
    # -----------------------------------------------------

    st.markdown("### Dataset Selection")

    dataset_name = st.selectbox(
        "Choose a dataset",
        [
            "Optimized Dispatch",
            "Heuristic Simulation",
            "Historical Energy Data"
        ]
    )

    if dataset_name == "Optimized Dispatch":

        selected_data = filtered.copy()

    elif dataset_name == "Heuristic Simulation":

        selected_data = heuristic[
            (heuristic["Timestamp"] >= start) &
            (heuristic["Timestamp"] < end)
        ].copy()

    else:

        selected_data = filtered[
            [
                "Timestamp",
                "Demand (MW)",
                "Wind (MW)",
                "Solar (MW)"
            ]
        ].copy()

    # -----------------------------------------------------
    # DATASET SUMMARY
    # -----------------------------------------------------

    st.markdown("### Dataset Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Records",
        f"{len(selected_data):,}"
    )

    c2.metric(
        "Total Columns",
        f"{len(selected_data.columns):,}"
    )

    c3.metric(
        "Memory Usage",
        f"{selected_data.memory_usage(deep=True).sum() / 1024:.1f} KB"
    )

    st.divider()

    # -----------------------------------------------------
    # SEARCH AND FILTER
    # -----------------------------------------------------

    st.markdown("### Search & Filter")

    filter_col1, filter_col2 = st.columns([1, 2])

    with filter_col1:

        search_column = st.selectbox(
            "Search column",
            ["None"] + selected_data.columns.tolist()
        )

    with filter_col2:

        search_value = st.text_input(
            "Search value",
            placeholder="Enter a value to filter records..."
        )

    if search_column != "None" and search_value:

        selected_data = selected_data[
            selected_data[search_column]
            .astype(str)
            .str.contains(
                search_value,
                case=False,
                na=False
            )
        ]

    st.caption(
        f"Displaying {len(selected_data):,} matching records."
    )

    # -----------------------------------------------------
    # DATA PREVIEW
    # -----------------------------------------------------

    st.markdown("### Data Preview")

    st.dataframe(
        selected_data,
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    st.divider()

    st.markdown("### Export Dataset")

    st.caption(
        "Export the currently selected and filtered records "
        "as a CSV file."
    )

    csv_data = selected_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=(
            dataset_name.lower()
            .replace(" ", "_")
            .replace("-", "_")
            + "_export.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "GRID INTELLIGENCE  |  Smart City Energy Management  "
    "|  Data Science Ecosystems"
)
