import streamlit as st
import pandas as pd

# Load player data from CSV file
players_data = pd.read_csv('players_data.csv')  # Ensure the CSV has columns: Name, Rating, Role

# Check if the required columns exist in the CSV
required_columns = ['Name', 'Rating', 'Role']
if not all(col in players_data.columns for col in required_columns):
    st.error("CSV file must contain columns: Name, Rating, Role")
    st.stop()

# Function to get the next player
def get_next_player():
    available_players = players_data[~players_data['Name'].isin([p['Name'] for team in st.session_state.teams.values() for p in team['players']])]
    if not available_players.empty:
        return available_players.sample().iloc[0]
    return None

# Initialize auction state
if 'teams' not in st.session_state:
    st.session_state.teams = {
        'Mospher': {'budget': 120, 'players': []},
        'Goku': {'budget': 120, 'players': []},
        'Maverick': {'budget': 120, 'players': []}
    }
if 'current_player' not in st.session_state:
    st.session_state.current_player = None
if 'current_bid' not in st.session_state:
    st.session_state.current_bid = 2.0
if 'last_auction' not in st.session_state:
    st.session_state.last_auction = None
if 'highest_bidder' not in st.session_state:
    st.session_state.highest_bidder = None

# Auction logic
def finalize_auction(winning_team):
    if winning_team and st.session_state.current_player is not None:
        # Add player with all details including Rating and Role
        st.session_state.teams[winning_team]['players'].append({
            'Name': st.session_state.current_player['Name'],
            'Price': st.session_state.current_bid,
            'Role': st.session_state.current_player['Role'],
            'Rating': st.session_state.current_player['Rating']
        })
        st.session_state.teams[winning_team]['budget'] -= st.session_state.current_bid
        st.session_state.last_auction = (st.session_state.current_player['Name'], winning_team, st.session_state.current_bid)
        reset_auction()

def reset_auction():
    # Resetting the auction state
    for team in st.session_state.teams.values():
        team['players'] = []
        team['budget'] = 120  # Reset budget to initial value
    st.session_state.current_player = None
    st.session_state.current_bid = 2.0
    st.session_state.last_auction = None
    st.session_state.highest_bidder = None

# Start auction function to initialize first player
def start_auction():
    st.session_state.current_player = get_next_player()
    if st.session_state.current_player is None:
        st.error("No players available for auction.")
    else:
        st.session_state.current_bid = 2.0
        st.session_state.highest_bidder = None

# Display current auction information
st.title("Player Auction")

# Buttons to control auction flow
if st.button("Start Auction"):
    start_auction()

if st.button("Restart Auction"):
    reset_auction()

st.write("Current Player: ", 
         st.session_state.current_player['Name'] if st.session_state.current_player is not None else "No player available")
st.write("Current Bid: ₹", st.session_state.current_bid)
st.write("Current Highest Bidder: ", 
         st.session_state.highest_bidder if st.session_state.highest_bidder else "No bids placed yet")

# Buttons for bidding
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Mospher Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Mospher']['budget']:
            st.session_state.current_bid += 0.5
            st.session_state.highest_bidder = "Mospher"

with col2:
    if st.button("Goku Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Goku']['budget']:
            st.session_state.current_bid += 0.5
            st.session_state.highest_bidder = "Goku"

with col3:
    if st.button("Maverick Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Maverick']['budget']:
            st.session_state.current_bid += 0.5
            st.session_state.highest_bidder = "Maverick"

# Finalizing auction button
if st.button("Finalize Auction"):
    winning_team = max(st.session_state.teams.keys(), key=lambda k: (st.session_state.current_bid if k == st.session_state.highest_bidder else 0))
    
    # Ensure we only finalize if there's a current player and a valid winning team.
    if winning_team and st.session_state.current_player is not None:
        finalize_auction(winning_team)

# Next player button
if st.button("Next Player"):
    reset_auction()
    
# Pass button for unsold player
if st.button("Pass"):
    reset_auction()

# Undo last auction button
if st.button("Undo Last Auction"):
    if st.session_state.last_auction:
        last_name, last_team, last_price = st.session_state.last_auction
        for team in st.session_state.teams.values():
            if last_team in team and any(player['Name'] == last_name for player in team['players']):
                team['players'].remove(next(player for player in team['players'] if player['Name'] == last_name))
                team['budget'] += last_price
                break

# Display teams and their players
for team_name, team_info in st.session_state.teams.items():
    players_df = pd.DataFrame(team_info['players'])
    
    # Check if DataFrame is empty before sorting and displaying
    if not players_df.empty:
        players_df.sort_values(by='Rating', ascending=False, inplace=True)
    
    # Display each team's budget and players sorted by rating and role.
    with st.expander(f"{team_name} - Budget: ₹{team_info['budget']}"):
        if not players_df.empty:
            players_df[['Name', 'Price', 'Role', 'Rating']]
            # Display sorted players by role and rating.
            sorted_players_by_role = players_df.sort_values(by=['Role', 'Rating'], ascending=[True, False])
            for _, row in sorted_players_by_role.iterrows():
                st.write(f"{row['Name']} - ₹{row['Price']} ({row['Role']} - Rating: {row['Rating']})")
    
# Display remaining players to be auctioned
remaining_players = players_data[~players_data['Name'].isin([p['Name'] for team in st.session_state.teams.values() for p in team['players']])]
if not remaining_players.empty:
    remaining_df = remaining_players.sort_values(by='Rating', ascending=False)
    with st.expander("Remaining Players:"):
        for _, row in remaining_df.iterrows():
            # Group by role and display remaining players.
            role_grouped_players = remaining_df.groupby('Role')
            for role, group in role_grouped_players:
                group_sorted = group.sort_values(by='Rating', ascending=False)
                for _, player_row in group_sorted.iterrows():
                    # Display each remaining player's details.
                    st.write(f"{player_row['Name']} - Rating: {player_row['Rating']} ({player_row['Role']})")
