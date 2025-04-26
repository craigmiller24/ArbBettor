from typing import List, Tuple, Optional
import math as m
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def down(val: float) -> float:
    """
    Round down the value to two decimal places.
    
    Args:
        val (float): The value to round down.
    
    Returns:
        float: The rounded down value.
    """
    return m.floor(100 * val) / 100

def assess_risk_free(o1: float, o2: float) -> Tuple[float, bool]:
    """
    Asses total implied probability of two bets to determine if there exists a risk-free bet
    
    Args:
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.
    
    Returns:
        tuple: (S (float): Total implied probability, valid (bool): True if the bets are risk-free; False otherwise).
    """
    
    # Calculate the total implied probabilitiy
    S = (1 / o1) + (1 / o2)
    valid = S < 1

    return S, valid

def add_bet(bets: List[dict], odds: float) -> None:
    """
    Add a new bet to the list.
    
    Args:
        bets (list): List of bets.
        odds (float): The odds of the bet.
    """
    
    # For each bet, create a dictionary defining its odds, stake, return, and profit
    new_bet = {
        'odds': odds,
        'stake': 0,
        'return': 0,
        'profit': 0
    }

    bets.append(new_bet)

def update_bet(bets: List[dict], stake1: float, stake2: float) -> None:
    """
    Update the bets with the calculated return and profit.
    
    Args:
        bets (list): List of bets.
        stake1 (float): Stake for the first bet.
        stake2 (float): Stake for the second bet.
    """

    # Update the stakes for each bet
    bets[0]['stake'] = stake1
    bets[1]['stake'] = stake2

    # Calculate the return and profit for each bet and update the bet dictionaries
    for bet in bets:
        bet['return'] = down(bet['stake'] * bet['odds'])
        bet['profit'] = down(bet['return'] - bet['stake'])

def split_stakes(bets: List[dict], payout: float, o1: float, o2: float) -> None:
    """
    Split the funds between the bets based on their odds.
    
    Args:
        bets (list): List of bets.
        payout (float): The total payout following the bet.
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.
    """

    # Calculate the stakes for each bet based on the payout and odds
    stake1 = payout / o1
    stake2 = payout / o2

    # Round the stakes to two decimal places to reflect bookmaker's rules
    if o1 < o2:
        stake1 = m.ceil(100 * stake1) / 100
        stake2 = down(stake2)
    else:
        stake1 = down(stake1)
        stake2 = m.ceil(100 * stake2) / 100

    # Update the bets with the newly calculated stakes
    update_bet(bets, stake1, stake2)

def process_bets(o1: float, o2: float, T: float) -> Tuple[Optional[List[dict]], Optional[float]]:
    """
    Process the bets and calculate the payout and profit.
    
    Args:
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.
        T (float): The total funds available for betting.
    
    Returns:
        tuple: (bets, profit) if valid, otherwise None.
    """
    # Check if the odds are valid for risk-free arbitrage betting
    S, valid = assess_risk_free(o1, o2)
    if not valid:
        return None, None, None

    # Construct the bets
    bets = []
    add_bet(bets, o1)
    add_bet(bets, o2)

    # Calculate final payout and profit based on the total funds and implied probability
    payout = down(T / S)
    profit = down(payout - T)

    # Calculate the required stakes for each bet
    split_stakes(bets, payout, o1, o2)

    return bets, profit

def plot_roi(o1: float, o2: float, o2_range, max_o2: float) -> None:
    """
    Plot the ROI vs Odds for Outcome 2.

    Args:
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.
        o2_range (array): Range of odds for Outcome 2.
        max_o2 (float): Maximum odds for Outcome 2.
    """
    roi_values = []

    for o2_val in o2_range:
        S = (1/o1) + (1/o2_val)
        roi = (1/S - 1) * 100
        roi_values.append(roi)

    # Create a plot for ROI vs Odds for Outcome 2
    fig, ax = plt.subplots()
    ax.plot(o2_range, roi_values)

    # Highlight the selected odds
    ax.axhline(0, color='green', linestyle='--')
    ax.axvline(o2, color='black', linestyle='--')
    ax.axhline(roi_values[np.where(o2_range == o2)[0][0]], color='black', linestyle='--')
    ax.plot(o2, roi_values[np.where(o2_range == o2)[0][0]], 'black', marker='o', label=f'ROI: {roi_values[np.where(o2_range == o2)[0][0]]:.2f}%')

    # Format plot range
    ax.set_xlim(0, max_o2)
    ax.set_ylim(-5, max(roi_values) + 0.1 * max(roi_values))

    ax.set_xlabel("Odds for Outcome 2")
    ax.set_ylabel("ROI (%)")
    ax.set_title("ROI vs Odds for Outcome 2")
    ax.legend(loc='lower right')
    ax.grid(True)

    # Display the plot
    st.pyplot(fig)

def bet_data(bets, o1, o2):
    """
    Create a DataFrame with the bet data.

    Args:
        bets (list): List of bets.
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.

    Returns:
        float: The guaranteed minimum profit from the bets.
    """
    # Format results 
    stake1 = bets[0]['stake']
    stake2 = bets[1]['stake']

    win1 = bets[0]['return']
    win2 = bets[1]['return']

    profit1 = bets[0]['profit']
    profit2 = bets[1]['profit']

    # Create DataFrame for the table
    data = {
        "Bet 1 (Profit/Loss)": [
            o1,
            stake1,
            f"{win1:.2f} ({profit1:.2f})",
            f"{down(-stake1):.2f} ({down(-stake1):.2f})"
        ],
        "Bet 2 (Profit/Loss)": [
            o2, 
            stake2, 
            f"{down(-stake2):.2f} ({down(-stake2):.2f})", 
            f"{win2:.2f} ({profit2:.2f})"
        ],
        "Total (£)": [
            None, 
            f"{T:.2f}", 
            f"{down(win1 - T):.2f}", 
            f"{down(win2 - T):.2f}"
        ]
    }
    index = ["Odds (Decimal)", "Stake (£)", "Outcome 1 Return (£)", "Outcome 2 Return (£)"]
    df = pd.DataFrame(data, index=index)

    # Display results in a table
    st.table(df)

    min_profit = min(down(win1 - T), down(win2 - T))

    return min_profit
                
if __name__ == "__main__":
    st.title("2-Way Arbitrage Betting Calculator")

    step = 0.01

    # Inputs
    o1 = st.number_input("Outcome 1 odds (Decimal)", min_value=1.01, value=2.0, step=step)
    max_o2 = st.slider("Maximum odds for Outcome 2 (Decimal)", min_value=10.0, max_value=500.0, value=10.0, step=step)
    o2_range = np.round(np.arange(1.01, max_o2 + step, step),2)
    o2 = st.select_slider('Outcome 2 Odds:', options=o2_range.tolist(), value=o2_range[0])

    # Display graph of ROI vs Odds for Outcome 2
    plot_roi(o1, o2, o2_range, max_o2)

    # Stake input
    T = st.number_input("Set Stake (£)", min_value=0.01, value=100.0, step=step)

    if st.button("Calculate Stakes"):
        bets, profit = process_bets(o1, o2, T)
            
        # If no valid betting opportunity is found, return None
        if bets is None:
            st.error("No arbitrage opportunity exists with these odds.")

        else:
            # Calculate the return on investment (ROI)
            roi = (profit / T) * 100
            
            min_profit = bet_data(bets, o1, o2)

            # Display guaranteed profit with larger font
            st.markdown(f"""
            <div style='text-align: center; font-size:24px; padding:10px; border:2px solid green; border-radius:10px;'>
            Guaranteed Profit: {profit} <strong>£{min_profit:.2f}</strong> ({roi:.2f}%)
            </div>
            """, unsafe_allow_html=True)