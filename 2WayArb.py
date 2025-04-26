from typing import List, Tuple, Optional, Dict
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
        tuple: (S (float): Total implied probability, is_risk_free (bool): True if the bets are risk-free; False otherwise).
    """
    
    # Calculate the total implied probabilitiy
    S = (1 / o1) + (1 / o2)
    is_risk_free = S < 1

    return S, is_risk_free

def add_bet(bets: List[dict], odds: float) -> None:
    """
    Add a new bet to the list.
    
    Args:
        bets (list): List of bets.
        odds (float): The odds of the bet.
    """
    
    # For each bet, create a dictionary defining its odds, stake, return, and profit
    bets.append({
        'odds': odds,
        'stake': 0,
        'return': 0,
        'profit': 0
    })

def update_bet(bets: List[Dict[str, float]], stake1: float, stake2: float) -> None:
    """
    Update the bets with the calculated return and profit.
    
    Args:
        bets (list): List of bets.
        stake1 (float): Stake for the first bet.
        stake2 (float): Stake for the second bet.
    """

    # Update the first bet
    bets[0]['stake'] = stake1
    bets[0]['return'] = down(stake1 * bets[0]['odds'])
    bets[0]['profit'] = down(bets[0]['return'] - stake1)

    # Update the second bet
    bets[1]['stake'] = stake2
    bets[1]['return'] = down(stake2 * bets[1]['odds'])
    bets[1]['profit'] = down(bets[1]['return'] - stake2)

def round_stake(stake: float, round_up: bool) -> float:
    """
    Round a stake to two decimal places, either up or down.

    Args:
        stake (float): The stake to round.
        round_up (bool): Whether to round up (True) or down (False).

    Returns:
        float: The rounded stake.
    """
    return m.ceil(100 * stake) / 100 if round_up else down(stake)

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

    # Round stakes based on the odds
    stake1 = round_stake(stake1, round_up=(o1 < o2))
    stake2 = round_stake(stake2, round_up=(o2 < o1))

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
    S, is_risk_free = assess_risk_free(o1, o2)
    if not is_risk_free:
        return None, None

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
    # Vectorized calculation of ROI values
    S = (1 / o1) + (1 / o2_range)
    roi_values = (1 / S - 1) * 100

    # Create a plot for ROI vs Odds for Outcome 2
    fig, ax = plt.subplots()
    ax.plot(o2_range, roi_values)

    # Highlight the selected odds
    selected_index = np.where(o2_range == o2)[0][0]
    ax.axhline(0, color='green', linestyle='--')
    ax.axvline(o2, color='black', linestyle='--')
    ax.axhline(roi_values[selected_index], color='black', linestyle='--')
    ax.plot(o2, roi_values[selected_index], 'black', marker='o', label=f'ROI: {roi_values[selected_index]:.2f}%')

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

def bet_data(bets: List[Dict[str, float]], o1: float, o2: float) -> float:
    """
    Create a DataFrame with the bet data.

    Args:
        bets (list): List of bets.
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.

    Returns:
        float: The guaranteed minimum profit from the bets.
    """
    # Extract bet details
    stake1, stake2 = bets[0]['stake'], bets[1]['stake']
    win1, win2 = bets[0]['return'], bets[1]['return']

    # Precompute repeated values
    loss1 = -stake1
    loss2 = -stake2
    net_profit1 = win1 - T
    net_profit2 = win2 - T

    # Create DataFrame for the table
    data = {
        "Bet 1": [o1, stake1, win1, loss1],
        "Bet 2": [o2, stake2, loss2, win2],
        "Profit (£)": ["", T, net_profit1, net_profit2],
    }
    index = ["Odds (Decimal)", "Stake (£)", "Outcome 1 (£)", "Outcome 2 (£)"]
    df = pd.DataFrame(data, index=index)

    # Apply formatting to the DataFrame
    df = df.applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)

    # Display results in a table
    st.table(df)

    # Calculate and return the guaranteed minimum profit
    min_profit = min(net_profit1, net_profit2)
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
            Guaranteed Profit: <strong>£{min_profit:.2f}</strong> ({roi:.2f}%)
            </div>
            """, unsafe_allow_html=True)