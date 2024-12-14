import streamlit as st
import pandas as pd
import random

# ... (Data Loading and Team Initialization remain the same)

if "auction_state" not in st.session_state:
    st.session_state.auction_state = {
        "available_players": players_df.copy(),
        "current_player": None,
        "current_bid": 0,
        "winning_team": None,
        "auction_in_progress": False, # Flag to track auction status
        "auction_history": [],
    }

# ... (display_team_info and display_available_players remain the same)

def start_auction():
    if not st.session_state.auction_state["auction_in_progress"]: # Check if auction is already running
        if not st.session_state.auction_state["available_players"].empty:
            st.session_state.auction_state["current_player"] = st.session_state.auction_state["available_players"].sample(1).iloc[0]
            st.session_state.auction_state["current_bid"] = 2
            st.session_state.auction_state["winning_team"] = None
            st.session_state.auction_state["auction_in_progress"] = True #Set auction in progress
            st.write(f"Next Player: {st.session_state.auction_state['current_player']['Name']} (Base Price: 2 Cr)")
        else:
            st.write("No more players available for auction.")

def finalize_auction():
    if st.session_state.auction_state["winning_team"]:  # Ensure closing parenthesis here
        # ... (rest of finalize_auction remains the same)
    else:
        # ... (rest of finalize_auction remains the same)
    st.session_state.auction_state["auction_in_progress"] = False  # Reset auction status

# ... (undo_last_auction remains the same)

st.title("Player Auction")

if st.button("Start Auction"):
    start_auction()

if st.session_state.auction_state["current_player"] is not None:
    cols = st.columns(3)

    for i, team_name in enumerate(teams):
        if st.button(f"{team_name} Bid"): #Removed the condition that was causing the buttons to disappear
            if st.session_state.auction_state["auction_in_progress"] : #check if auction is in progress
                if st.session_state.auction_state["winning_team"] != team_name: #check if this team is not already winning
                    st.session_state.auction_state["current_bid"] += 0.5
                    st.session_state.auction_state["winning_team"] = team_name
                else:
                    st.write(f"{team_name} is already the highest bidder")
            else:
                st.write("Auction is not in progress")

    if st.session_state.auction_state["winning_team"]:
        st.write(f"Current Bid: {st.session_state.auction_state['current_bid']} Cr by {st.session_state.auction_state['winning_team']}")


if st.button("Finalize Auction"):
    finalize_auction()

if st.button("Next Player"):
    start_auction()

if st.button("Pass"):
    finalize_auction()

# ... (rest of the code remains the same)
