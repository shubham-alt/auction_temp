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

# Auction logic
def finalize_auction(winning_team):
    if winning_team and st.session_state.current_player is not None:
        # Add player with all details including Rating and Role
        st.session_state.teams[winning_team]['players'].append({
            'Name': st.session_state.current_player['Name'],
            'Price': st.session_state.current_bid,
            'Role': st.session_state.current_player['Role'],
            'Rating': st.session_state.current_player['Rating']  # Include Rating here
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

# Start auction function to initialize first player
def start_auction():
    st.session_state.current_player = get_next_player()
    if st.session_state.current_player is None:
        st.error("No players available for auction.")
    else:
        st.session_state.current_bid = 2.0

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

# Buttons for bidding
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Mospher Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Mospher']['budget']:
            st.session_state.current_bid += 0.5

with col2:
    if st.button("Goku Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Goku']['budget']:
            st.session_state.current_bid += 0.5

with col3:
    if st.button("Maverick Bid"):
        if (st.session_state.current_bid + 0.5) <= st.session_state.teams['Maverick']['budget']:
            st.session_state.current_bid += 0.5

# Finalizing auction button
if st.button("Finalize Auction"):
    winning_team = max(st.session_state.teams.keys(), key=lambda k: (st.session_state.current_bid if k in ['Mospher', 'Goku', 'Maverick'] else 0))
    
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
    st.write(f"### {team_name} - Budget: ₹{team_info['budget']}")
    
    # Create DataFrame from players list and sort by Rating
    players_df = pd.DataFrame(team_info['players'])
    
    # Check if DataFrame is empty before sorting and displaying
    if not players_df.empty:
        players_df.sort_values(by='Rating', ascending=False, inplace=True)
        st.write(players_df[['Name', 'Price', 'Role', 'Rating']])  # Include Rating here

# Display remaining players to be auctioned
remaining_players = players_data[~players_data['Name'].isin([p['Name'] for team in st.session_state.teams.values() for p in team['players']])]
if not remaining_players.empty:
    remaining_df = remaining_players.sort_values(by='Rating', ascending=False)
    st.write("### Remaining Players:")
    st.write(remaining_df[['Name', 'Rating', 'Role']])
