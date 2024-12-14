import streamlit as st
import pandas as pd
import random

# Load the player data
players_data = pd.read_csv('players_data.csv')

# Initializing global variables
if 'players' not in st.session_state:
    st.session_state.players = players_data
    st.session_state.teams = {
        'Mospher': {'budget': 120, 'players': [], 'bidded': False},
        'Goku': {'budget': 120, 'players': [], 'bidded': False},
        'Maverick': {'budget': 120, 'players': [], 'bidded': False}
    }
    st.session_state.current_player = None
    st.session_state.last_auction = None
    st.session_state.unsold_players = []

# Function to pick the next player randomly
def get_next_player():
    available_players = st.session_state.players[~st.session_state.players['Name'].isin(
        [p['Name'] for team in st.session_state.teams.values() for p in team['players']])]
    if not available_players.empty:
        return available_players.sample().iloc[0]
    return None

# Display current purse of each team
def display_team_details():
    st.write("### Team Budgets")
    for team_name, team in st.session_state.teams.items():
        st.write(f"{team_name}: ₹{team['budget']} cr")

# Display players by role, sorted by rating
def display_players_by_role():
    st.write("### Players in Auction (Grouped by Role)")
    remaining_players = st.session_state.players[~st.session_state.players['Name'].isin(
        [p['Name'] for team in st.session_state.teams.values() for p in team['players']])]
    if not remaining_players.empty:
        sorted_players = remaining_players.sort_values(by=['Role', 'Rating'], ascending=[True, False])
        st.dataframe(sorted_players[['Name', 'Role', 'Rating']])

# Display each team's roster
def display_team_rosters():
    st.write("### Team Rosters")
    for team_name, team in st.session_state.teams.items():
        st.write(f"#### {team_name}")
        if team['players']:
            team_roster = pd.DataFrame(team['players'])
            st.dataframe(team_roster[['Name', 'Role', 'Rating', 'Price']])
        else:
            st.write("No players bought yet.")

# Start auction for the next player
def start_auction():
    st.session_state.current_player = get_next_player()
    if st.session_state.current_player is None:
        st.write("No more players to auction.")
        return

    st.session_state.current_bid = 2  # Starting bid price
    st.session_state.highest_bidder = None

# Finalize auction for the current player
def finalize_auction():
    if st.session_state.highest_bidder:
        team = st.session_state.teams[st.session_state.highest_bidder]
        team['players'].append({
            'Name': st.session_state.current_player['Name'],
            'Role': st.session_state.current_player['Role'],
            'Rating': st.session_state.current_player['Rating'],
            'Price': st.session_state.current_bid
        })
        team['budget'] -= st.session_state.current_bid
        st.write(f"{st.session_state.current_player['Name']} has been sold to {st.session_state.highest_bidder} for ₹{st.session_state.current_bid} cr!")
    else:
        st.session_state.unsold_players.append(st.session_state.current_player['Name'])
        st.write(f"{st.session_state.current_player['Name']} is unsold.")

    # Reset bids for all teams
    for team in st.session_state.teams.values():
        team['bidded'] = False

    st.session_state.last_auction = st.session_state.current_player
    st.session_state.current_player = None

# Undo the last auction
def undo_last_auction():
    if st.session_state.last_auction:
        last_player = st.session_state.last_auction
        # Return the budget and remove player from the team
        for team in st.session_state.teams.values():
            for player in team['players']:
                if player['Name'] == last_player['Name']:
                    team['players'].remove(player)
                    team['budget'] += player['Price']
                    break
        st.session_state.last_auction = None
        st.session_state.current_player = last_player
        st.write(f"Undid last auction for {last_player['Name']}.")

# Create Streamlit UI components
st.title("Player Auction")

# Display current ongoing auction at the top
if st.session_state.current_player is not None:
    st.write(f"### Ongoing Auction: {st.session_state.current_player['Name']} - {st.session_state.current_player['Role']}")
    st.write(f"Current Bid: ₹{st.session_state.current_bid} cr")

# Display teams first side by side
col1, col2, col3 = st.columns(3)
with col1:
    st.write("#### Mospher")
    st.write(f"Budget: ₹{st.session_state.teams['Mospher']['budget']} cr")
with col2:
    st.write("#### Goku")
    st.write(f"Budget: ₹{st.session_state.teams['Goku']['budget']} cr")
with col3:
    st.write("#### Maverick")
    st.write(f"Budget: ₹{st.session_state.teams['Maverick']['budget']} cr")

# Display team rosters
display_team_rosters()

# Display players yet to come for auction
display_players_by_role()

# Auction controls
if st.session_state.current_player:
    col1, col2, col3 = st.columns(3)

    with col1:
        if not st.session_state.teams['Mospher']['bidded']:
            if st.button("Mospher Bid"):
                st.session_state.current_bid += 0.5
                st.session_state.highest_bidder = 'Mospher'
                st.session_state.teams['Mospher']['bidded'] = True

    with col2:
        if not st.session_state.teams['Goku']['bidded']:
            if st.button("Goku Bid"):
                st.session_state.current_bid += 0.5
                st.session_state.highest_bidder = 'Goku'
                st.session_state.teams['Goku']['bidded'] = True

    with col3:
        if not st.session_state.teams['Maverick']['bidded']:
            if st.button("Maverick Bid"):
                st.session_state.current_bid += 0.5
                st.session_state.highest_bidder = 'Maverick'
                st.session_state.teams['Maverick']['bidded'] = True

    # Finalize auction
    if st.button("Finalize Auction"):
        finalize_auction()

    # Next player button
    if st.button("Next Player"):
        start_auction()

    # Pass button
    if st.button("Pass"):
        st.session_state.unsold_players.append(st.session_state.current_player['Name'])
        st.session_state.current_player = None

    # Undo last auction button
    if st.button("Undo Last Player Auction"):
        undo_last_auction()

else:
    st.write("No player is currently up for auction.")
    if st.button("Start Auction"):
        start_auction()

