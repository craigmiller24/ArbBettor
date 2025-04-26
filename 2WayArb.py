from typing import List, Tuple, Optional
import math as m
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
        bet['return'] = down(bet['stake'] * bet['odds'] + bet['stake'])
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

def process_bets(o1: float, o2: float, T: float) -> Tuple[Optional[List[dict]], Optional[float], Optional[float]]:
    """
    Process the bets and calculate the payout and profit.
    
    Args:
        o1 (float): The odds of the first bet.
        o2 (float): The odds of the second bet.
        T (float): The total funds available for betting.
    
    Returns:
        tuple: (bets, payout, profit) if valid, otherwise None.
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

    return bets, payout, profit

if __name__ == "__main__":
    st.title("2-Way Arbitrage Betting Calculator")

    st.header("Plot ROI vs Second Outcome Odds")
    o1 = st.number_input("Input Known Odds (Decimal)", min_value=1.01, value=1.01, step=0.01)
    max_o2 = st.slider("Max Odds for Outcome 2 (Decimal)", min_value=20.0, max_value=500.0, value=100.0, step=0.01)
    o2_range = np.linspace(0, max_o2, 500)
    roi_values = []

    for o2 in o2_range:
        S = (1/o1) + (1/o2)
        roi = (1/S - 1) * 100
        roi_values.append(roi)

    fig, ax = plt.subplots()
    ax.plot(o2_range, roi_values)

    ax.set_xlim(0, max_o2)
    ax.set_ylim(0, max(roi_values) + 0.1 * max(roi_values))

    ax.set_xlabel("Odds for Outcome 2")
    ax.set_ylabel("ROI (%)")
    ax.set_title("ROI vs Odds for Outcome 2")
    ax.grid(True)

    st.pyplot(fig)

    st.header("Input Odds and Stake")
    o1 = st.number_input("Odds for Outcome 1 (Decimal)", min_value=1.01, value=1.01, step=0.01)
    o2 = st.number_input("Odds for Outcome 2 (Decimal)", min_value=1.01, value=1.01, step=0.01)
    T = st.number_input("Total Stake (£)", min_value=0.01, value=100.0, step=1.0)

    if st.button("Calculate Optimal Stakes"):
        bets, payout, profit = process_bets(o1, o2, T)
            
        # If no valid betting opportunity is found, return None
        if bets is None:
            st.error("No arbitrage opportunity exists with these odds.")

        else:
            # Calculate the return on investment (ROI)
            roi = (profit / T) * 100

            st.success("Arbitrage Opportunity Found!")
            st.write(f"Stake on Bet 1: £{bets[0]['stake']}")
            st.write(f"Stake on Bet 2: £{bets[1]['stake']}")
            st.write(f"Guaranteed Profit: £{profit} ({roi:.2f}%)")

