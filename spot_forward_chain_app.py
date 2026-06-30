# Import Streamlit because it creates the web dashboard.
import streamlit as st

# Import NumPy because it helps with arrays, grids, and numerical calculations.
import numpy as np

# Import pandas because it helps create tables and structured financial data.
import pandas as pd

# Import Plotly because it creates interactive charts.
import plotly.graph_objects as go


# Set the Streamlit browser tab title and use wide layout.
st.set_page_config(
    page_title="Spot-Forward No-Arbitrage Dashboard",
    layout="wide"
)


# Add small CSS improvements for a cleaner dashboard look.
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }

        .small-note {
            color: #9ca3af;
            font-size: 0.90rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Show the main dashboard title.
st.title("Spot-Forward No-Arbitrage & Reinvestment Risk Dashboard")


# Show a short professional subtitle.
st.caption(
    "A capital markets dashboard for comparing long-term spot investment, implied forward rates, and realized rate paths."
)


# Show a short explanation message at the top.
st.info(
    "This dashboard explains how spot rates imply forward rates under no-arbitrage logic, "
    "and how realized future rates create profit or loss versus a locked spot-rate baseline."
)


# Create the sidebar header for all user controls.
st.sidebar.header("Inputs / Controls")


# Ask the user for the starting amount of money.
principal = st.sidebar.number_input(
    "Starting Principal",
    min_value=1_000.0,
    max_value=1_000_000_000.0,
    value=100_000.0,
    step=10_000.0
)


# Ask the user for the total investment horizon in years.
total_years = st.sidebar.number_input(
    "Total Investment Horizon (Years)",
    min_value=2,
    max_value=30,
    value=5,
    step=1
)


# Ask the user for the total maturity spot rate.
spot_total_percent = st.sidebar.number_input(
    f"{total_years}-Year Spot Rate (%)",
    min_value=-50.0,
    max_value=100.0,
    value=6.0,
    step=0.1
)


# Ask the user for the one-year spot rate.
spot_one_year_percent = st.sidebar.number_input(
    "1-Year Spot Rate (%)",
    min_value=-50.0,
    max_value=100.0,
    value=5.0,
    step=0.1
)


# Ask the user for the realized future rate after year 1.
realized_remaining_percent = st.sidebar.number_input(
    f"Your Realized Rate for Years 2 to {total_years} (%)",
    min_value=-50.0,
    max_value=100.0,
    value=7.0,
    step=0.1
)


# Add an expandable area for yearly chain-rate assumptions.
with st.sidebar.expander("Year-by-Year Chain Rates", expanded=True):
    # Create an empty list to store the yearly rates entered by the user.
    chain_rate_percent_list = []

    # Loop through each year in the total horizon.
    for year_number in range(1, total_years + 1):
        # Create a default increasing rate path for demonstration.
        default_rate = 5.0 + 0.5 * (year_number - 1)

        # Ask the user for this year's realized one-year rate.
        user_rate = st.number_input(
            f"Year {year_number} Realized Rate (%)",
            min_value=-50.0,
            max_value=100.0,
            value=float(default_rate),
            step=0.1,
            key=f"chain_rate_{year_number}"
        )

        # Store the user-entered yearly rate in the list.
        chain_rate_percent_list.append(user_rate)


# Convert the total spot rate from percent into decimal.
spot_total_rate = spot_total_percent / 100.0


# Convert the one-year spot rate from percent into decimal.
spot_one_year_rate = spot_one_year_percent / 100.0


# Convert the realized remaining rate from percent into decimal.
realized_remaining_rate = realized_remaining_percent / 100.0


# Convert all chain rates from percent into decimals.
chain_rates = [rate_percent / 100.0 for rate_percent in chain_rate_percent_list]


# Stop the app if rates are mathematically invalid for compounding.
if (1 + spot_total_rate) <= 0 or (1 + spot_one_year_rate) <= 0 or (1 + realized_remaining_rate) <= 0:
    st.error("Rates must be greater than -100% so compounding remains mathematically valid.")
    st.stop()


# Stop the app if any yearly chain rate is invalid for compounding.
if any((1 + rate) <= 0 for rate in chain_rates):
    st.error("Every chain rate must be greater than -100% so compounding remains mathematically valid.")
    st.stop()


# Create a helper function that formats money nicely.
def format_money(value):
    # Return N/A if value is missing.
    if pd.isna(value):
        return "N/A"

    # Format value as a dollar amount with commas.
    return f"${value:,.0f}"


# Create a helper function that formats decimal values as percentages.
def format_percent(value):
    # Return N/A if value is missing.
    if pd.isna(value):
        return "N/A"

    # Convert decimal into percentage string.
    return f"{value * 100:.2f}%"


# Create a helper function that calculates future value with annual compounding.
def compounded_future_value(starting_value, annual_rate, years):
    # Apply the compound interest formula.
    return starting_value * ((1 + annual_rate) ** years)


# Create a helper function that calculates CAGR.
def calculate_cagr(starting_value, ending_value, years):
    # Return missing value if inputs are not valid.
    if starting_value <= 0 or ending_value <= 0 or years <= 0:
        return np.nan

    # Apply the CAGR formula.
    return (ending_value / starting_value) ** (1 / years) - 1


# Create a helper function that calculates implied average forward rate.
def calculate_implied_forward_rate(total_spot_rate, one_year_spot_rate, years):
    # Calculate the future value growth factor from the full-period spot rate.
    total_growth_factor = (1 + total_spot_rate) ** years

    # Calculate the one-year growth factor.
    one_year_growth_factor = 1 + one_year_spot_rate

    # Calculate the remaining-period growth factor needed after year one.
    remaining_growth_factor = total_growth_factor / one_year_growth_factor

    # Convert the remaining-period growth factor into an annualized forward rate.
    implied_forward = remaining_growth_factor ** (1 / (years - 1)) - 1

    # Return the implied forward rate.
    return implied_forward


# Calculate the implied forward rate from year 1 to year T.
implied_forward_rate = calculate_implied_forward_rate(
    spot_total_rate,
    spot_one_year_rate,
    total_years
)


# Create a year index from 0 to total_years.
years = np.arange(0, total_years + 1)


# Calculate the baseline path using the total spot rate.
baseline_values = principal * ((1 + spot_total_rate) ** years)


# Create the no-arbitrage forward path starting with principal.
forward_break_even_values = [principal]


# Add the value after year one using the one-year spot rate.
forward_break_even_values.append(principal * (1 + spot_one_year_rate))


# Loop from year 2 to maturity.
for year_number in range(2, total_years + 1):
    # Grow the previous value by the implied forward rate.
    next_value = forward_break_even_values[-1] * (1 + implied_forward_rate)

    # Store the new value in the forward path.
    forward_break_even_values.append(next_value)


# Create the realized split strategy path starting with principal.
realized_split_values = [principal]


# Add the value after year one using the one-year spot rate.
realized_split_values.append(principal * (1 + spot_one_year_rate))


# Loop from year 2 to maturity.
for year_number in range(2, total_years + 1):
    # Grow the previous value by the user's realized remaining rate.
    next_value = realized_split_values[-1] * (1 + realized_remaining_rate)

    # Store the new value in the realized split path.
    realized_split_values.append(next_value)


# Create the chain strategy path starting with principal.
chain_values = [principal]


# Loop through every yearly chain rate.
for yearly_rate in chain_rates:
    # Grow the previous value by the current year's realized rate.
    next_value = chain_values[-1] * (1 + yearly_rate)

    # Store the chain value after this year.
    chain_values.append(next_value)


# Convert the forward path into a NumPy array.
forward_break_even_values = np.array(forward_break_even_values)


# Convert the realized split path into a NumPy array.
realized_split_values = np.array(realized_split_values)


# Convert the chain path into a NumPy array.
chain_values = np.array(chain_values)


# Create the main path DataFrame for charting and download.
path_df = pd.DataFrame(
    {
        "Year": years,
        "Baseline_Spot_Path": baseline_values,
        "No_Arbitrage_Forward_Path": forward_break_even_values,
        "Realized_Split_Path": realized_split_values,
        "Yearly_Chain_Path": chain_values
    }
)


# Calculate realized split P&L gap versus baseline for every year.
path_df["Realized_Split_Gap"] = path_df["Realized_Split_Path"] - path_df["Baseline_Spot_Path"]


# Calculate chain P&L gap versus baseline for every year.
path_df["Yearly_Chain_Gap"] = path_df["Yearly_Chain_Path"] - path_df["Baseline_Spot_Path"]


# Calculate no-arbitrage path gap versus baseline for every year.
path_df["No_Arbitrage_Gap"] = path_df["No_Arbitrage_Forward_Path"] - path_df["Baseline_Spot_Path"]


# Store the final baseline future value.
baseline_terminal_value = baseline_values[-1]


# Store the final no-arbitrage forward future value.
forward_terminal_value = forward_break_even_values[-1]


# Store the final realized split future value.
realized_split_terminal_value = realized_split_values[-1]


# Store the final chain future value.
chain_terminal_value = chain_values[-1]


# Calculate realized split P&L versus baseline.
realized_split_pnl = realized_split_terminal_value - baseline_terminal_value


# Calculate chain P&L versus baseline.
chain_pnl = chain_terminal_value - baseline_terminal_value


# Calculate realized spread versus implied forward in basis points.
realized_spread_bps = (realized_remaining_rate - implied_forward_rate) * 10000


# Calculate chain CAGR.
chain_cagr = calculate_cagr(principal, chain_terminal_value, total_years)


# Calculate realized split CAGR.
realized_split_cagr = calculate_cagr(principal, realized_split_terminal_value, total_years)


# Calculate baseline CAGR.
baseline_cagr = calculate_cagr(principal, baseline_terminal_value, total_years)


# Calculate chain edge versus baseline in basis points.
chain_edge_bps = (chain_cagr - baseline_cagr) * 10000


# Calculate the worst realized split shortfall during the path.
worst_split_gap = path_df["Realized_Split_Gap"].min()


# Calculate the worst chain shortfall during the path.
worst_chain_gap = path_df["Yearly_Chain_Gap"].min()


# Create a terminal summary table.
terminal_summary = pd.DataFrame(
    {
        "Strategy": [
            "Baseline Spot Investment",
            "No-Arbitrage Forward Path",
            "Realized Split Strategy",
            "Yearly Chain Strategy"
        ],
        "Terminal Value": [
            baseline_terminal_value,
            forward_terminal_value,
            realized_split_terminal_value,
            chain_terminal_value
        ],
        "P&L vs Baseline": [
            0.0,
            forward_terminal_value - baseline_terminal_value,
            realized_split_pnl,
            chain_pnl
        ],
        "CAGR": [
            baseline_cagr,
            calculate_cagr(principal, forward_terminal_value, total_years),
            realized_split_cagr,
            chain_cagr
        ]
    }
)


# Create the executive summary section.
st.header("1. Executive Summary")


# Create six columns for the most important metrics.
metric_1, metric_2, metric_3, metric_4, metric_5, metric_6 = st.columns(6)


# Show the baseline terminal value.
metric_1.metric(
    "Baseline FV",
    format_money(baseline_terminal_value)
)


# Show the implied forward rate.
metric_2.metric(
    "Implied Forward",
    format_percent(implied_forward_rate)
)


# Show the realized spread versus forward.
metric_3.metric(
    "Realized vs Forward",
    f"{realized_spread_bps:.0f} bps"
)


# Show realized split P&L.
metric_4.metric(
    "Split P&L",
    format_money(realized_split_pnl)
)


# Show chain P&L.
metric_5.metric(
    "Chain P&L",
    format_money(chain_pnl)
)


# Show chain CAGR.
metric_6.metric(
    "Chain CAGR",
    format_percent(chain_cagr)
)


# Create a simple interpretation at the top.
if realized_remaining_rate > implied_forward_rate:
    # Show positive interpretation if realized rate beats forward.
    st.success(
        "The realized remaining rate is above the implied forward rate, so the split strategy beats the locked spot baseline."
    )
elif realized_remaining_rate < implied_forward_rate:
    # Show negative interpretation if realized rate is below forward.
    st.warning(
        "The realized remaining rate is below the implied forward rate, so the split strategy loses versus the locked spot baseline."
    )
else:
    # Show neutral interpretation if realized rate equals forward.
    st.info(
        "The realized remaining rate equals the implied forward rate, so the split strategy approximately matches the baseline."
    )


# Create the input summary section.
st.header("2. Inputs / Controls")


# Create a compact input table.
input_table = pd.DataFrame(
    {
        "Input": [
            "Starting Principal",
            "Investment Horizon",
            "Total Spot Rate",
            "1-Year Spot Rate",
            "Realized Remaining Rate",
            "Implied Forward Rate"
        ],
        "Value": [
            format_money(principal),
            f"{total_years} years",
            f"{spot_total_percent:.2f}%",
            f"{spot_one_year_percent:.2f}%",
            f"{realized_remaining_percent:.2f}%",
            format_percent(implied_forward_rate)
        ]
    }
)


# Display the input table.
st.dataframe(
    input_table,
    hide_index=True,
    use_container_width=True
)


# Show formula section.
st.header("3. Key Formulas")


# Put formulas inside an expander to keep the dashboard clean.
with st.expander("Open formula explanation", expanded=True):
    # Create two columns for formula layout.
    formula_col_1, formula_col_2 = st.columns(2)

    # Put spot and forward formulas in the left column.
    with formula_col_1:
        # Explain spot future value.
        st.markdown("### Spot Investment")

        # Show spot future value formula.
        st.latex(r"FV_{spot} = P(1+S_T)^T")

        # Explain no-arbitrage equality.
        st.markdown("### No-Arbitrage Equality")

        # Show no-arbitrage equality formula.
        st.latex(r"P(1+S_T)^T = P(1+S_1)(1+F_{1,T})^{T-1}")

        # Show implied forward formula.
        st.latex(r"F_{1,T} = \left(\frac{(1+S_T)^T}{(1+S_1)}\right)^{\frac{1}{T-1}} - 1")

    # Put chain and P&L formulas in the right column.
    with formula_col_2:
        # Explain chain compounding.
        st.markdown("### Year-by-Year Chain")

        # Show chain formula.
        st.latex(r"FV_{chain} = P\prod_{i=1}^{T}(1+r_i)")

        # Explain P&L formula.
        st.markdown("### Profit / Loss vs Baseline")

        # Show P&L formula.
        st.latex(r"PnL = FV_{strategy} - FV_{spot}")

        # Show CAGR formula.
        st.markdown("### CAGR")

        # Show CAGR formula.
        st.latex(r"CAGR = \left(\frac{FV}{P}\right)^{\frac{1}{T}} - 1")


# Create main visualization section.
st.header("4. Main Visualization")


# Create visualization tabs.
tab_paths, tab_gap, tab_terminal, tab_heatmap = st.tabs(
    [
        "Strategy Paths",
        "P&L Gap",
        "Terminal Comparison",
        "Rate Sensitivity"
    ]
)


# Create strategy path chart.
with tab_paths:
    # Create a Plotly figure.
    fig_paths = go.Figure()

    # Add baseline path.
    fig_paths.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["Baseline_Spot_Path"],
            mode="lines+markers",
            name="Baseline Spot Path"
        )
    )

    # Add no-arbitrage forward path.
    fig_paths.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["No_Arbitrage_Forward_Path"],
            mode="lines+markers",
            name="No-Arbitrage Forward Path"
        )
    )

    # Add realized split path.
    fig_paths.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["Realized_Split_Path"],
            mode="lines+markers",
            name="Realized Split Path"
        )
    )

    # Add yearly chain path.
    fig_paths.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["Yearly_Chain_Path"],
            mode="lines+markers",
            name="Yearly Chain Path"
        )
    )

    # Improve the chart layout.
    fig_paths.update_layout(
        template="plotly_dark",
        height=520,
        title="Investment Path Comparison",
        xaxis_title="Year",
        yaxis_title="Portfolio Value",
        hovermode="x unified",
        legend_title="Strategy"
    )

    # Display the chart.
    st.plotly_chart(fig_paths, use_container_width=True)

    # Display the path table.
    st.dataframe(
        path_df.style.format(
            {
                "Baseline_Spot_Path": "${:,.0f}",
                "No_Arbitrage_Forward_Path": "${:,.0f}",
                "Realized_Split_Path": "${:,.0f}",
                "Yearly_Chain_Path": "${:,.0f}",
                "Realized_Split_Gap": "${:,.0f}",
                "Yearly_Chain_Gap": "${:,.0f}",
                "No_Arbitrage_Gap": "${:,.2f}"
            }
        ),
        hide_index=True,
        use_container_width=True
    )


# Create P&L gap chart.
with tab_gap:
    # Create a Plotly figure.
    fig_gap = go.Figure()

    # Add realized split gap.
    fig_gap.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["Realized_Split_Gap"],
            mode="lines+markers",
            name="Realized Split Gap"
        )
    )

    # Add yearly chain gap.
    fig_gap.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=path_df["Yearly_Chain_Gap"],
            mode="lines+markers",
            name="Yearly Chain Gap"
        )
    )

    # Add zero reference line.
    fig_gap.add_trace(
        go.Scatter(
            x=path_df["Year"],
            y=[0] * len(path_df),
            mode="lines",
            name="Break-even Line",
            line=dict(dash="dash")
        )
    )

    # Improve gap chart layout.
    fig_gap.update_layout(
        template="plotly_dark",
        height=500,
        title="Profit / Loss Gap Versus Baseline Spot Investment",
        xaxis_title="Year",
        yaxis_title="P&L Gap",
        hovermode="x unified"
    )

    # Display gap chart.
    st.plotly_chart(fig_gap, use_container_width=True)


# Create terminal comparison chart.
with tab_terminal:
    # Create a Plotly bar chart for terminal values.
    fig_terminal = go.Figure()

    # Add terminal value bars.
    fig_terminal.add_trace(
        go.Bar(
            x=terminal_summary["Strategy"],
            y=terminal_summary["Terminal Value"],
            name="Terminal Value"
        )
    )

    # Improve terminal value chart.
    fig_terminal.update_layout(
        template="plotly_dark",
        height=500,
        title="Terminal Value by Strategy",
        xaxis_title="Strategy",
        yaxis_title="Terminal Value"
    )

    # Display terminal value chart.
    st.plotly_chart(fig_terminal, use_container_width=True)

    # Show terminal summary table.
    st.dataframe(
        terminal_summary.style.format(
            {
                "Terminal Value": "${:,.0f}",
                "P&L vs Baseline": "${:,.0f}",
                "CAGR": "{:.2%}"
            }
        ),
        hide_index=True,
        use_container_width=True
    )


# Create rate sensitivity heatmap.
with tab_heatmap:
    # Create a grid of possible total spot rates.
    total_spot_grid = np.linspace(
        max(-0.50, spot_total_rate - 0.03),
        spot_total_rate + 0.03,
        25
    )

    # Create a grid of possible realized remaining rates.
    realized_rate_grid = np.linspace(
        max(-0.50, implied_forward_rate - 0.03),
        implied_forward_rate + 0.03,
        25
    )

    # Create an empty list for heatmap rows.
    heatmap_rows = []

    # Loop through each total spot rate.
    for grid_spot_rate in total_spot_grid:
        # Create an empty row for this spot rate.
        heatmap_row = []

        # Loop through each realized future rate.
        for grid_realized_rate in realized_rate_grid:
            # Calculate baseline terminal value at this spot rate.
            grid_baseline_fv = principal * ((1 + grid_spot_rate) ** total_years)

            # Calculate split terminal value using selected one-year rate and grid realized rate.
            grid_split_fv = principal * (1 + spot_one_year_rate) * ((1 + grid_realized_rate) ** (total_years - 1))

            # Calculate P&L versus baseline.
            grid_pnl = grid_split_fv - grid_baseline_fv

            # Store this P&L value in the row.
            heatmap_row.append(grid_pnl)

        # Store the full row.
        heatmap_rows.append(heatmap_row)

    # Convert heatmap rows into NumPy array.
    heatmap_values = np.array(heatmap_rows)

    # Create the heatmap figure.
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_values,
            x=[f"{rate * 100:.2f}%" for rate in realized_rate_grid],
            y=[f"{rate * 100:.2f}%" for rate in total_spot_grid],
            colorbar=dict(title="P&L")
        )
    )

    # Improve heatmap layout.
    fig_heatmap.update_layout(
        template="plotly_dark",
        height=600,
        title="Rate Sensitivity: Split Strategy P&L vs Spot Baseline",
        xaxis_title="Realized Remaining Rate",
        yaxis_title=f"{total_years}-Year Spot Rate"
    )

    # Display heatmap.
    st.plotly_chart(fig_heatmap, use_container_width=True)


# Create risk metrics section.
st.header("5. Risk / Sensitivity Metrics")


# Add a note explaining what risk means here.
st.caption(
    "This dashboard does not model equity-style volatility. Here, risk means reinvestment risk and rate-path risk."
)


# Create six columns for risk metrics.
risk_1, risk_2, risk_3, risk_4, risk_5, risk_6 = st.columns(6)


# Show implied forward rate.
risk_1.metric(
    "Break-even Forward",
    format_percent(implied_forward_rate)
)


# Show realized spread in bps.
risk_2.metric(
    "Realized Spread",
    f"{realized_spread_bps:.0f} bps"
)


# Show split terminal P&L.
risk_3.metric(
    "Split Terminal P&L",
    format_money(realized_split_pnl)
)


# Show chain terminal P&L.
risk_4.metric(
    "Chain Terminal P&L",
    format_money(chain_pnl)
)


# Show worst split path shortfall.
risk_5.metric(
    "Worst Split Shortfall",
    format_money(worst_split_gap)
)


# Show chain edge in bps.
risk_6.metric(
    "Chain Edge vs Spot",
    f"{chain_edge_bps:.1f} bps"
)


# Create interpretation section.
st.header("6. Interpretation")


# Interpret realized split result.
if realized_split_pnl > 0:
    # Show positive result.
    st.success(
        f"The realized split strategy ends at {format_money(realized_split_terminal_value)}, "
        f"beating the baseline by {format_money(realized_split_pnl)}."
    )
elif realized_split_pnl < 0:
    # Show negative result.
    st.error(
        f"The realized split strategy ends at {format_money(realized_split_terminal_value)}, "
        f"losing {format_money(abs(realized_split_pnl))} versus the baseline."
    )
else:
    # Show neutral result.
    st.info(
        "The realized split strategy exactly matches the baseline."
    )


# Interpret chain result.
if chain_pnl > 0:
    # Show positive chain result.
    st.success(
        f"The yearly chain strategy beats the baseline by {format_money(chain_pnl)}."
    )
elif chain_pnl < 0:
    # Show negative chain result.
    st.warning(
        f"The yearly chain strategy loses {format_money(abs(chain_pnl))} versus the baseline."
    )
else:
    # Show neutral chain result.
    st.info(
        "The yearly chain strategy exactly matches the baseline."
    )


# Explain the core forward-rate lesson.
st.markdown(
    f"""
    The no-arbitrage forward rate is **{format_percent(implied_forward_rate)}**.

    If your realized future rate is above this level, waiting and reinvesting wins.

    If your realized future rate is below this level, locking the full-period spot rate wins.
    """
)


# Create limitations section.
st.header("7. Limitations")


# Put limitations in an expander to keep the dashboard clean.
with st.expander("Read limitations"):
    # Explain limitations in markdown.
    st.markdown(
        """
        - This is an educational no-arbitrage dashboard, not a trading recommendation.
        - The model assumes annual compounding.
        - The model uses one average forward rate from year 1 to maturity, not a full forward curve.
        - Taxes, transaction costs, liquidity, credit risk, and bid-ask spread are not included.
        - The baseline path is an accrued value path, not a mark-to-market bond price path.
        - Real markets use full zero curves, discount factors, bootstrapping, convexity adjustments, and collateral conventions.
        """
    )


# Create download section.
st.header("8. Download CSV")


# Create CSV bytes for yearly path data.
path_csv = path_df.to_csv(index=False).encode("utf-8")


# Create CSV bytes for terminal summary data.
terminal_csv = terminal_summary.to_csv(index=False).encode("utf-8")


# Create two columns for download buttons.
download_col_1, download_col_2 = st.columns(2)


# Add download button for yearly path data.
with download_col_1:
    st.download_button(
        label="Download Yearly Path Data",
        data=path_csv,
        file_name="spot_forward_yearly_paths.csv",
        mime="text/csv"
    )


# Add download button for terminal summary data.
with download_col_2:
    st.download_button(
        label="Download Terminal Summary",
        data=terminal_csv,
        file_name="spot_forward_terminal_summary.csv",
        mime="text/csv"
    )
