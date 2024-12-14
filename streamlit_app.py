import streamlit as st
import pandas as pd
import random

# Load player data
player_data = pd.read_csv('players_data.csv')

# Initialize team purses and auction state
team_purses = {'Mospher': 120, 'Goku': 120, 'Maverick': 120}
auction_state = []

def display_auction_state():
    for player in auction_state:
        st.write(f"{player['Name']} sold to {player['Winner']} for {player['Price']}")

def display_team_purses():
    for team, purse in team_purses.items():
        st.write(f"{team}: {purse}")

def display_team_squads():
    # ... (Implement logic to display team squads based on auction_state)

def display_remaining_players():
    # ... (Implement logic to display remaining players, grouped and sorted)

def bid(team):
    if team_purses[team] >= current_bid + 0.5:
        team_purses[team] -= 0.5
        return current_bid + 0.5
    else:
        st.write(f"{team} cannot afford this bid!")
        return current_bid

def finalize_auction():
    if current_bid > 2:  # Minimum bid to avoid free transfers
        auction_state.append({'Name': current_player['Name'], 'Winner': highest_bidder, 'Price': current_bid})
        st.write(f"{current_player['Name']} sold to {highest_bidder} for {current_bid}")
    else:
        st.write("Player passed")

def undo_last_auction():
    if auction_state:
        last_player = auction_state.pop()
        team_purses[last_player['Winner']] += last_player['Price']

def start_auction():
    global current_player, current_bid, highest_bidder
    current_player = random.choice(remaining_players)
    current_bid = 2
    highest_bidder = None
    remaining_players.remove(current_player)

def restart_auction():
    global auction_state, team_purses, remaining_players
    auction_state = []
    team_purses = {'Mospher': 120, 'Goku': 120, 'Maverick': 120}
    remaining_players = player_data.copy()

# Main app
st.title("Player Auction")

if 'started' not in st.session_state:
    st.session_state.started = False
    remaining_players = player_data.copy()

if st.session_state.started:
    # Display current auction state
    st.write(f"Current Player: {current_player['Name']}")
    st.write(f"Current Bid: {current_bid}")
    st.write(f"Highest Bidder: {highest_bidder}")

    # Bid buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Mospher Bid"):
            current_bid = bid('Mospher')
            highest_bidder = 'Mospher'
    with col2:
        if st.button("Goku Bid"):
            current_bid = bid('Goku')
            highest_bidder = 'Goku'
    with col3:
        if st.button("Maverick Bid"):
            current_bid = bid('Maverick')
            highest_bidder = 'Maverick'

    # Other buttons
    st.button("Finalize Auction", on_click=finalize_auction)
    st.button("Next Player", on_click=start_auction)
    st.button("Pass", on_click=finalize_auction)
    st.button("Undo Last Auction", on_click=undo_last_auction)

    # Display team purses, squads, and remaining players
    display_team_purses()
    display_team_squads()
    display_remaining_players()

else:
    if st.button("Start Auction"):
        st.session_state.started = True
        start_auction()

st.button("Restart Auction", on_click=restart_auction)
