import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Arbitrage & The Rich/Poor Game", layout="wide")

st.title("Spot Rates, Forwards, & The Rich/Poor Game")
st.markdown("Follow the journey below to see how market expectations (Forward Rates) compare to trader bets (Realized Rates).")
st.markdown("---")

# ==========================================
# SECTION 1: THE LAZY MAN (Total Spot Rate)
# ==========================================
st.header("1. The Direct Flight (The Baseline Spot Rate)")
st.markdown("Set your baseline. This is the 'Lazy Man' who locks in his money today for the entire trip.")

col1, col2, col3 = st.columns(3)
with col1:
    P = st.number_input("Starting Principal ($)", value=100000, step=10000)
with col2:
    T = st.number_input("Total Years to Invest", min_value=2, max_value=10, value=3, step=1)
with col3:
    r_total_input = st.number_input(f"Total {T}-Year Spot Rate (%)", value=6.0, step=0.1)

r_total = r_total_input / 100
fv_total = P * (1 + r_total)**T

# Graph 1
fig1 = go.Figure()
x_spot = np.arange(0, T + 1)
y_spot = P * (1 + r_total)**x_spot
fig1.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines+markers', name=f'{T}-Year Spot Curve', line=dict(color='#1f77b4', width=4)))
fig1.update_layout(title=f"The Baseline: Guaranteed ${fv_total:,.0f} at Year {T}", xaxis_title="Years", yaxis_title="Account Value ($)", height=400)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 2: THE ONE-STOP FLIGHT (Single Split)
# ==========================================
st.header("2. The Single Split: Forward Rate vs. Your Bet")
st.markdown(f"Now, let's split the {T}-year journey. You invest for **Year 1**, and then make a bet on the remaining **{T-1} years**.")

col4, col5 = st.columns(2)
with col4:
    r1_input = st.number_input("Year 1 Spot Rate (%)", value=5.0, step=0.1)
    r1 = r1_input / 100
    
    # Calculate implied forward rate for the remaining years
    # Formula: (1 + r_total)^T = (1 + r1)^1 * (1 + fwd)^(T-1)
    fwd_rate = (((1 + r_total)**T / (1 + r1))**(1 / (T - 1))) - 1
    
    st.info(f"**The Market's Line in the Sand:**\nTo match the Lazy Man, you MUST earn **{fwd_rate*100:.2f}%** per year for the remaining {T-1} years.")

with col5:
    realized_input = st.number_input(f"Your Bet: Actual Rate for remaining {T-1} years (%)", value=7.0, step=0.1)
    r_realized = realized_input / 100

fv_year1 = P * (1 + r1)
fv_bet = fv_year1 * (1 + r_realized)**(T - 1)
pl_1 = fv_bet - fv_total

# Graph 2
fig2 = go.Figure()
# Baseline
fig2.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines', name='Baseline', line=dict(color='gray', dash='dash')))

# Trader Path
x_trader = [0, 1, T]
y_trader = [P, fv_year1, fv_bet]
color2 = '#2ca02c' if pl_1 >= 0 else '#d62728'

fig2.add_trace(go.Scatter(x=x_trader, y=y_trader, mode='lines+markers', name='Your Realized Path', line=dict(color=color2, width=4), marker=dict(size=10)))

fig2.update_layout(
    title=f"Rich/Poor Result: {'+$' if pl_1 >= 0 else '-$'}{abs(pl_1):,.0f}", 
    xaxis_title="Years", yaxis_title="Account Value ($)", height=400,
    xaxis=dict(tickmode='linear', dtick=1)
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 3: THE CHAIN (Year-by-Year Gauntlet)
# ==========================================
st.header("3. The Chain: Running the Gauntlet")
st.markdown(f"Instead of one big bet, what if you ride the market year-by-year? Input your guess for what the market will actually pay during *each specific year* of the {T}-year journey.")

# Dynamically generate columns based on T
cols = st.columns(T)
chain_rates = []

for i in range(T):
    with cols[i]:
        # Default values to make the initial chart look interesting
        default_val = float(5.0 + i) 
        rate_in = st.number_input(f"Year {i+1} Actual (%)", value=default_val, step=0.1, key=f"chain_{i}")
        chain_rates.append(rate_in / 100)

# Calculate the Chain path
x_chain = np.arange(0, T + 1)
y_chain = [P]
current_val = P

for rate in chain_rates:
    current_val = current_val * (1 + rate)
    y_chain.append(current_val)

pl_chain = y_chain[-1] - fv_total

# Graph 3
fig3 = go.Figure()
# Baseline
fig3.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines', name='Baseline (Lazy Man)', line=dict(color='gray', dash='dash')))

# Chain Path
color3 = '#2ca02c' if pl_chain >= 0 else '#d62728'
fig3.add_trace(go.Scatter(x=x_chain, y=y_chain, mode='lines+markers', name='Your Step-by-Step Chain', line=dict(color=color3, width=4, shape='spline'), marker=dict(size=10)))

fig3.update_layout(
    title=f"Final Chain Result: {'+$' if pl_chain >= 0 else '-$'}{abs(pl_chain):,.0f} vs Baseline", 
    xaxis_title="Years", yaxis_title="Account Value ($)", height=400,
    xaxis=dict(tickmode='linear', dtick=1)
)
st.plotly_chart(fig3, use_container_width=True)