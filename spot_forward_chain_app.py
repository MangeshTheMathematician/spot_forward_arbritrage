import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Arbitrage & The Rich/Poor Game", layout="wide")

st.title("Spot Rates, Forwards, & The Rich/Poor Game")
st.markdown("Set your master parameters below, then scroll down to see the math, the tables, and the visuals for each strategy.")
st.markdown("---")

# ==========================================
# MASTER INPUTS
# ==========================================
col_m1, col_m2 = st.columns(2)
with col_m1:
    P = st.number_input("Starting Principal ($)", value=100000, step=10000)
with col_m2:
    T = st.number_input("Total Years to Invest (Minimum 5 for tables)", min_value=5, max_value=20, value=5, step=1)

st.markdown("---")

# ==========================================
# SECTION 1: THE LAZY MAN (Total Spot Rate)
# ==========================================
st.header("1. The Direct Flight (Baseline Spot Rate)")
r_total_input = st.number_input(f"Total {T}-Year Spot Rate (%)", value=6.0, step=0.1)
r_total = r_total_input / 100
fv_total = P * (1 + r_total)**T

col1, col2 = st.columns([1.2, 2])

with col1:
    st.markdown("### The Math")
    st.latex(r"FV = P \times (1 + r_{spot})^T")
    
    st.markdown("### Year-by-Year Accrual")
    # Generate Table Data
    years_s1 = np.arange(1, T + 1)
    vals_s1 = [P * (1 + r_total)**y for y in years_s1]
    int_s1 = [vals_s1[i] - (P if i==0 else vals_s1[i-1]) for i in range(len(vals_s1))]
    
    df1 = pd.DataFrame({
        'Year': years_s1,
        'Rate': [f"{r_total_input:.2f}%"] * T,
        'Interest Added': int_s1,
        'Total Value': vals_s1
    })
    
    st.dataframe(df1.style.format({
        'Interest Added': '${:,.0f}',
        'Total Value': '${:,.0f}'
    }), hide_index=True, use_container_width=True)

with col2:
    fig1 = go.Figure()
    x_spot = np.arange(0, T + 1)
    y_spot = P * (1 + r_total)**x_spot
    fig1.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines+markers', name=f'{T}-Year Spot Curve', line=dict(color='#1f77b4', width=4)))
    fig1.update_layout(title=f"The Baseline: Guaranteed ${fv_total:,.0f} at Year {T}", xaxis_title="Years", yaxis_title="Account Value ($)", height=450)
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 2: THE SINGLE SPLIT (Forward vs Bet)
# ==========================================
st.header("2. The Single Split: Forward Rate vs. Your Bet")
col_s2_1, col_s2_2 = st.columns(2)
with col_s2_1:
    r1_input = st.number_input("Year 1 Spot Rate (%)", value=5.0, step=0.1)
    r1 = r1_input / 100
with col_s2_2:
    realized_input = st.number_input(f"Your Bet: Actual Rate for remaining {T-1} years (%)", value=7.0, step=0.1)
    r_realized = realized_input / 100

# Calculate Forward
fwd_rate = (((1 + r_total)**T / (1 + r1))**(1 / (T - 1))) - 1

col3, col4 = st.columns([1.2, 2])

with col3:
    st.markdown("### The No-Arbitrage Forward Math")
    st.latex(r"Forward = \left( \frac{(1 + r_{total})^T}{(1 + r_1)^1} \right)^{\frac{1}{T-1}} - 1")
    st.info(f"**Break-Even Rate:** {fwd_rate*100:.2f}%")
    
    st.markdown("### Baseline vs. Bet")
    years_s2 = np.arange(1, T + 1)
    
    # Trader's actual path calculation
    vals_bet = []
    for y in years_s2:
        if y == 1:
            vals_bet.append(P * (1 + r1))
        else:
            vals_bet.append(vals_bet[-1] * (1 + r_realized))
            
    df2 = pd.DataFrame({
        'Year': years_s2,
        'Baseline Value': vals_s1,
        'Your Bet Value': vals_bet,
        'P&L Gap': [vals_bet[i] - vals_s1[i] for i in range(T)]
    })
    
    st.dataframe(df2.style.format({
        'Baseline Value': '${:,.0f}',
        'Your Bet Value': '${:,.0f}',
        'P&L Gap': '${:,.0f}'
    }).applymap(lambda x: 'color: green' if x > 0 else ('color: red' if x < 0 else ''), subset=['P&L Gap']), 
    hide_index=True, use_container_width=True)

with col4:
    fv_year1 = P * (1 + r1)
    fv_bet = vals_bet[-1]
    pl_1 = fv_bet - fv_total
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines', name='Baseline', line=dict(color='gray', dash='dash')))
    
    x_trader = [0, 1] + list(range(2, T+1))
    y_trader = [P] + vals_bet
    color2 = '#2ca02c' if pl_1 >= 0 else '#d62728'
    
    fig2.add_trace(go.Scatter(x=x_trader, y=y_trader, mode='lines+markers', name='Your Realized Path', line=dict(color=color2, width=4), marker=dict(size=8)))
    fig2.update_layout(title=f"Rich/Poor Result: {'+$' if pl_1 >= 0 else '-$'}{abs(pl_1):,.0f}", xaxis_title="Years", yaxis_title="Account Value ($)", height=450)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 3: THE CHAIN (Year-by-Year Gauntlet)
# ==========================================
st.header("3. The Chain: Running the Gauntlet")
st.markdown("Input your guess for what the market will actually pay during *each specific year*.")

# Dynamic Inputs
cols_in = st.columns(T)
chain_rates = []
for i in range(T):
    with cols_in[i]:
        rate_in = st.number_input(f"Yr {i+1} (%)", value=float(5.0 + i*0.5), step=0.1, key=f"chain_{i}")
        chain_rates.append(rate_in / 100)

col5, col6 = st.columns([1.2, 2])

with col5:
    st.markdown("### The Chain Math (Bootstrapping)")
    st.latex(r"FV = P \times (1+r_1) \times (1+r_2) \dots \times (1+r_T)")
    
    # Calculate Chain Path
    y_chain = [P]
    for rate in chain_rates:
        y_chain.append(y_chain[-1] * (1 + rate))
        
    df3 = pd.DataFrame({
        'Year': np.arange(1, T + 1),
        'Your Actual Rate': [f"{r*100:.2f}%" for r in chain_rates],
        'Interest Added': [y_chain[i+1] - y_chain[i] for i in range(T)],
        'Total Value': y_chain[1:]
    })
    
    st.markdown("### Your Step-by-Step Accrual")
    st.dataframe(df3.style.format({
        'Interest Added': '${:,.0f}',
        'Total Value': '${:,.0f}'
    }), hide_index=True, use_container_width=True)

with col6:
    pl_chain = y_chain[-1] - fv_total
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x_spot, y=y_spot, mode='lines', name='Baseline (Lazy Man)', line=dict(color='gray', dash='dash')))
    
    color3 = '#2ca02c' if pl_chain >= 0 else '#d62728'
    fig3.add_trace(go.Scatter(x=np.arange(0, T + 1), y=y_chain, mode='lines+markers', name='Your Step-by-Step Chain', line=dict(color=color3, width=4, shape='spline'), marker=dict(size=8)))
    
    fig3.update_layout(title=f"Final Chain Result: {'+$' if pl_chain >= 0 else '-$'}{abs(pl_chain):,.0f} vs Baseline", xaxis_title="Years", yaxis_title="Account Value ($)", height=450)
    st.plotly_chart(fig3, use_container_width=True)