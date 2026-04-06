import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Forward Rates & Arbitrage", layout="wide")

st.title("Spot Rates, Forwards, & The Arbitrage Game")
st.markdown("""
Welcome to the Quant Desk. This dashboard visualizes how markets price time, how **Forward Rates** act as break-even "lines in the sand", and how traders actually make (or lose) money by betting against them.
""")

# ==========================================
# SIDEBAR: USER INPUTS
# ==========================================
st.sidebar.header("1. Market Environment (Spot Rates)")
st.sidebar.markdown("*The 'Direct Flight' prices available today.*")
P = st.sidebar.number_input("Starting Principal ($)", value=100000, step=10000)

r1_input = st.sidebar.number_input("1-Year Spot Rate (%)", value=5.0, step=0.1)
r2_input = st.sidebar.number_input("2-Year Spot Rate (%)", value=6.0, step=0.1)
r3_input = st.sidebar.number_input("3-Year Spot Rate (%)", value=6.5, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("2. The Trader's Bet (Realized Rate)")
st.sidebar.markdown("*What actually happens in Year 2? (For the Rich/Poor game)*")
realized_input = st.sidebar.number_input("Actual Year 2 Rate (%)", value=8.0, step=0.1)

# Convert to decimals
r1 = r1_input / 100
r2 = r2_input / 100
r3 = r3_input / 100
r_real = realized_input / 100

# ==========================================
# QUANT CALCULATIONS (The Math Engine)
# ==========================================

# Future Values (Spot)
fv1 = P * (1 + r1)**1
fv2 = P * (1 + r2)**2
fv3 = P * (1 + r3)**3

# Implied Forward Rates (No-Arbitrage Break-Even)
# f(1,2) = [ (1+r2)^2 / (1+r1)^1 ] - 1
f1_2 = ((1 + r2)**2 / (1 + r1)) - 1

# f(2,3) = [ (1+r3)^3 / (1+r2)^2 ] - 1
f2_3 = ((1 + r3)**3 / (1 + r2)**2) - 1

# The Trader's Reality (The Rich/Poor Gamble in Year 2)
fv_gamble_yr2 = fv1 * (1 + r_real)
pl_dollars = fv_gamble_yr2 - fv2


# ==========================================
# GRAPH 1: THE BREAK-EVEN (Spot vs Forward)
# ==========================================
st.header("1. The Break-Even: Spot vs. Forward")
st.info("""
**The Setup:** The "Lazy Man" takes the 2-Year Spot Rate (Direct Flight). The "Tricky Man" takes the 1-Year Spot, and locks in the 1-Year Forward Rate today (Connecting Flight). 
**The Quant Rule (No-Arbitrage):** The market calculates the Forward Rate so that both paths end up with the *exact same amount of money*. If they didn't, traders would exploit the difference for free money (Arbitrage).
""")

col1, col2 = st.columns([1, 2.5])
with col1:
    st.markdown("### The Math")
    st.latex(r"Forward = \frac{(1 + r_2)^2}{(1 + r_1)} - 1")
    st.markdown(f"**1-Year Spot ($r_1$):** {r1*100:.2f}%")
    st.markdown(f"**2-Year Spot ($r_2$):** {r2*100:.2f}%")
    st.markdown(f"**Implied Forward:** `{f1_2*100:.2f}%`")
    
    st.success(f"To break even with the 2-year Spot Rate, your Year 2 investment MUST yield **{f1_2*100:.2f}%**.")

with col2:
    fig1 = go.Figure()
    # Path A: Spot Curve
    y_spot = [P, P*(1+r2), fv2]
    fig1.add_trace(go.Scatter(x=[0,1,2], y=y_spot, mode='lines+markers', name='Spot Path (Lazy Man)', line=dict(color='#1f77b4', width=4, dash='dot'), marker=dict(size=10)))
    
    # Path B: Forward Curve
    y_fwd = [P, fv1, fv2]
    fig1.add_trace(go.Scatter(x=[0,1,2], y=y_fwd, mode='lines+markers', name='Forward Path (Tricky Man)', line=dict(color='#ff7f0e', width=4), marker=dict(size=10)))
    
    fig1.update_layout(title="Both paths lead to exactly the same Future Value (No Arbitrage)", xaxis_title="Year", yaxis_title="Account Value ($)", xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ==========================================
# GRAPH 2: THE RICH OR POOR GAME (Arbitrage P&L)
# ==========================================
st.header("2. The Bet: Getting Rich vs. Getting Poor")
st.info(f"""
**The Setup:** You didn't lock in the Forward Rate. You waited. Now it's Year 1, and the *actual* interest rate in the market is **{realized_input}%**. 
**The Quant Rule:** Because the market paid {realized_input}% instead of the Break-Even Forward Rate ({f1_2*100:.2f}%), a gap opens up. This gap is your net Profit or Loss (P&L).
""")

col3, col4 = st.columns([1, 2.5])
with col3:
    st.markdown("### The Scorecard")
    st.markdown(f"**Target to Beat (Forward):** {f1_2*100:.2f}%")
    st.markdown(f"**What you got (Realized):** {r_real*100:.2f}%")
    
    if pl_dollars > 0:
        st.success(f"**YOU GOT RICH!**\nYou beat the Forward Rate.\n\n**Bonus P&L: +${pl_dollars:,.2f}**")
    elif pl_dollars < 0:
        st.error(f"**YOU GOT POOR.**\nYou missed the Forward Rate.\n\n**Loss P&L: -${abs(pl_dollars):,.2f}**")
    else:
        st.warning("Exact Break-Even. No gain, no loss.")

with col4:
    fig2 = go.Figure()
    # Baseline Spot
    fig2.add_trace(go.Scatter(x=[0,1,2], y=[P, P*(1+r2), fv2], mode='lines', name='Baseline (Locked Spot)', line=dict(color='gray', dash='dash')))
    # Gamble Path
    fig2.add_trace(go.Scatter(x=[0,1,2], y=[P, fv1, fv_gamble_yr2], mode='lines+markers', name='Your Gamble (Realized)', line=dict(color='#2ca02c' if pl_dollars >= 0 else '#d62728', width=4), marker=dict(size=12)))
    
    # Highlight the P&L gap
    fig2.add_shape(type="line", x0=2, y0=fv2, x1=2, y1=fv_gamble_yr2, line=dict(color="red" if pl_dollars < 0 else "green", width=3, dash="dot"))
    fig2.add_annotation(x=2, y=(fv2 + fv_gamble_yr2)/2, text=f"P&L: ${pl_dollars:,.0f}", showarrow=False, xshift=40, font=dict(color="red" if pl_dollars < 0 else "green", size=14))

    fig2.update_layout(title="Divergence: How floating rates create Profit/Loss vs Fixed Rates", xaxis_title="Year", yaxis_title="Account Value ($)", xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ==========================================
# GRAPH 3: THE CHAIN (Term Structure Bootstrapping)
# ==========================================
st.header("3. The Chain: Building a 3-Year Spot Curve")
st.info("""
**The Setup:** A 3-Year Spot Rate is just a mask. Underneath, it is actually a chain of three distinct 1-year jumps multiplying together.
**The Quant Rule:** Quants use this "Chain" to extract what the market thinks will happen in Year 2 and Year 3. This is called the "Term Structure of Forward Rates".
""")

col5, col6 = st.columns([1, 2.5])
with col5:
    st.markdown("### The Links in the Chain")
    st.markdown(f"**Year 1 Link (Spot):** `{r1*100:.2f}%`")
    st.markdown(f"**Year 2 Link (Forward):** `{f1_2*100:.2f}%`")
    st.markdown(f"**Year 3 Link (Forward):** `{f2_3*100:.2f}%`")
    
    st.markdown("### The Proof")
    st.latex(r"(1+r_1) \times (1+f_{1,2}) \times (1+f_{2,3})")
    chain_math = (1+r1) * (1+f1_2) * (1+f2_3)
    st.markdown(f"$= {chain_math:.4f}$")
    st.markdown(f"Which perfectly equals $(1+r_3)^3$!")

with col6:
    fig3 = go.Figure()
    
    # Step by step values
    y_chain = [P, fv1, fv1*(1+f1_2), fv1*(1+f1_2)*(1+f2_3)]
    
    # Plotting the Chain as a stepped waterfall/line combo
    fig3.add_trace(go.Scatter(x=[0,1,2,3], y=y_chain, mode='lines+markers+text', name='The Forward Chain', 
                              line=dict(color='#9467bd', width=4, shape='spline'), marker=dict(size=12),
                              text=["", f"+{r1*100:.1f}%", f"+{f1_2*100:.1f}%", f"+{f2_3*100:.1f}%"],
                              textposition="top left", textfont=dict(color='white')))
    
    # Show the smooth 3-year spot curve for comparison
    x_smooth = np.linspace(0, 3, 50)
    y_smooth = P * (1 + r3)**x_smooth
    fig3.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='3-Yr Spot (Smooth)', line=dict(color='gray', dash='dot')))

    fig3.update_layout(title="Unlocking the Chain: Spot Rates are built from Forward Blocks", xaxis_title="Year", yaxis_title="Account Value ($)", xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig3, use_container_width=True)