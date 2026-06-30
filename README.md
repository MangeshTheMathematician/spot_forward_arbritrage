Spot-Forward No-Arbitrage & Reinvestment Risk Dashboard

Live Dashboard: hessian-ai-spot-forward-chain-arbitrage.streamlit.app

1. Project Summary

This project is an interactive Streamlit dashboard that demystifies the relationship between spot rates, forward rates, no-arbitrage pricing, and reinvestment risk.

Finance textbooks are notorious for taking simple concepts and dressing them up in confusing jargon. I built this project to strip out the BS, translate the math into plain English, and demonstrate a core capital markets truth: Forward rates are not random guesses. They are exact mathematical targets implied by spot rates under no-arbitrage logic.

It is an interactive tool for understanding yield curve logic, fixed-income analytics, derivatives foundations, and treasury decision-making.

2. The Concept in Plain English

Imagine you have $100,000 and you want to invest it for 5 years. You have a choice of different paths.

Path 1: The Safe Route (Baseline Spot Path)

What it means: You lock your money in a vault for 5 years straight, and it earns exactly 6% every single year ($S_5 = 6\%$).

The Reality: You don't touch it. It's simple, predictable, and safe. You go to sleep and wake up 5 years later with your guaranteed money.

Path 2: The Gambler Route (Split Path)

What it means: You only lock your money in for 1 year at 5% ($S_1 = 5\%$).

The Reality: You sacrifice the guaranteed 6% because maybe you think rates will go up next year, and you don't want to be trapped in a 5-year contract.

The Forward Rate: The "Breakeven" ($F_{1,5} = 6.25\%$)

Because you only got 5% in year one, you are behind the Safe Route. To catch up over the remaining 4 years, you need a higher rate. The Forward Rate (6.25%) is the exact mathematical rate you need to hit over the next 4 years just to break even with the Safe Route. It's a theoretical target.

The Realized Rate: What Actually Happens (e.g., $7\%$)

"Realized" is just the finance word for "what actually happened in real life." Once your 1-year contract ends, your money unlocks. You look at the bank's board and see they are offering 7%. You lock it in. Because your Realized Rate (7%) is higher than your Breakeven target (6.25%), your gamble paid off! You beat the baseline.

Path 3: The "Commitment-Phobe" Route (Yearly Chain Path)

What it means: You refuse to sign any long-term contract. You only do 1-year deals.

The Reality: Year 1 ends, you check the new rate, sign for 1 year. Year 2 ends, you check the new rate, sign for 1 year. You do this 5 times in a row, riding the rollercoaster of whatever the 1-year rate happens to be each year.

3. What is "No-Arbitrage"?

Arbitrage means ZERO risk, ZERO guessing, and ZERO of your own money. It means locking in a guaranteed profit today.

If the math between the Safe Route and the Gambler Route breaks—for example, if a bank accidentally offers a guaranteed 7% forward contract when the mathematical breakeven is 6.25%—free money exists.

In real markets, no retail bank makes this mistake. But in the chaotic, trillion-dollar institutional bond markets, microscopic mathematical gaps (like 0.005%) open up for milliseconds. Automated algorithms spot the glitch, borrow millions of dollars, execute trades instantly, and pocket the cash before the market corrects itself.

The "No-Arbitrage Formula" calculates the exact theoretical rate where no free money exists, because if it did, the market would exploit it until it vanished.

4. The Formal Math & Proofs

Formula 1: Direct Spot Investment (Baseline)

If you invest Principal ($P$) for $T$ years at the annual spot rate ($S_T$):

$$FV_{spot} = P(1+S_T)^T$$

Formula 2: One-Year Spot + Forward (No-Arbitrage Equality)

If you invest for 1 year at $S_1$, then reinvest for the remaining $T-1$ years at the forward rate $F_{1,T}$, the future value is:

$$FV_{split} = P(1+S_1)(1+F_{1,T})^{T-1}$$

The Proof: Under no-arbitrage, $FV_{spot} = FV_{split}$.

$$P(1+S_T)^T = P(1+S_1)(1+F_{1,T})^{T-1}$$

Cancel $P$ and divide by $(1+S_1)$:

$$\frac{(1+S_T)^T}{(1+S_1)} = (1+F_{1,T})^{T-1}$$

Take the power of $\frac{1}{T-1}$ and subtract 1 to isolate the Forward Rate:

$$F_{1,T} = \left(\frac{(1+S_T)^T}{(1+S_1)}\right)^{\frac{1}{T-1}} - 1$$

Formula 3: Chain of Yearly Rates

If you invest year by year using different actual yearly rates ($r_1, r_2, ..., r_T$):

$$FV_{chain} = P \prod_{i=1}^{T}(1+r_i)$$

Formula 4: Profit & Loss (P&L)

The dashboard compares each strategy to the baseline spot investment.

$$PnL = FV_{strategy} - FV_{spot}$$

If PnL > 0: Your path beats the baseline.

If PnL < 0: Your path loses versus the baseline.

Formula 5: Compound Annual Growth Rate (CAGR)

CAGR is an imaginary, perfectly smooth interest rate. It cuts through the chaos of changing yearly rates to give you a single, flat average.

$$CAGR = \left(\frac{FV}{P}\right)^{\frac{1}{T}} - 1$$

5. Step-by-Step Example (From the Dashboard)

Inputs:

$P = 100,000$

$T = 5$ years

$S_5 = 6\%$ (0.06)

$S_1 = 5\%$ (0.05)

Realized remaining rate $= 7\%$ (0.07)

Yearly Chain rates $= 5\%, 5.5\%, 6\%, 6.5\%, 7\%$

Step 1: Baseline 5-Year Spot

$$FV_{spot} = 100,000(1.06)^5 = \$133,822.56$$

Step 2: Calculate Implied Forward Rate

$$F_{1,5} = \left(\frac{(1.06)^5}{1.05}\right)^{\frac{1}{4}} - 1 = 6.25\%$$

(You need 6.25% for the last 4 years to break even).

Step 3: Realized Split Strategy (7%)

$$FV_{split} = 100,000(1.05)(1.07)^4 = \$137,633.58$$

$$PnL = 137,633.58 - 133,822.56 = \mathbf{+\$3,811.02}$$

(Because 7% > 6.25%, you won the gamble).

Step 4: Yearly Chain Path

$$FV_{chain} = 100,000(1.05)(1.055)(1.06)(1.065)(1.07) = \$133,807.67$$

$$PnL = 133,807.67 - 133,822.56 = \mathbf{-\$14.89}$$

(The chain path slightly underperformed the safe 6% baseline).

6. Dashboard Features

Dynamic Inputs: Adjust Principal, Time horizons, and expected rates.

Strategy Paths Chart: Visualizes the Baseline, No-Arbitrage, Realized, and Chain paths over time.

P&L Gap Tracking: Real-time calculation of how much money you are leaving on the table (or gaining).

Rate Sensitivity Heatmap: Shows how P&L changes when overall spot rates and realized rates shift.

Data Export: Download the underlying simulation data as a CSV.

Built to make quantitative finance accessible.
