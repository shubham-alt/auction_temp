import streamlit as st
import pandas as pd

# Set the app layout to wide mode
st.set_page_config(layout="wide")

# Load player data
try:
    players_df = pd.read_csv("players_data.csv")
except FileNotFoundError:
    st.error("players_data.csv not found. Please upload the file.")
    st.stop()

# Initialize teams. Use session state to persist team data.
if "teams" not in st.session_state:
    st.session_state.teams = {
        "Mospher": {"purse": 120, "players": []},
        "Goku": {"purse": 120, "players": []},
        "Maverick": {"purse": 120, "players": []},
    }
teams = st.session_state.teams  # Alias for easier access

# Section to pre-assign players (can be commented out if not needed)
# Uncomment the section below to pre-assign players to teams

pre_assigned_players = [
    {"Name": "KL Rahul", "Role": "WK", "Rating": 95, "Selling Price": 13, "Team": "Maverick"},
    {"Name": "Babar Azam", "Role": "BAT", "Rating": 90, "Selling Price": 8.5, "Team": "Goku"},
    {"Name": "Van der Dussen", "Role": "BAT", "Rating": 87, "Selling Price": 3, "Team": "Mospher"},
    {"Name": "Pat Cummins", "Role": "BOWL", "Rating": 89, "Selling Price": 10.5, "Team": "Maverick"},
    {"Name": "Saud Shakeel", "Role": "BAT", "Rating": 86, "Selling Price": 6.5, "Team": "Maverick"},
    {"Name": "Tim Southee", "Role": "BOWL", "Rating": 82, "Selling Price": 3, "Team": "Mospher"}    
]

for player in pre_assigned_players:
    team_name = player["Team"]
    if team_name in teams:
        # Deduct from the team's purse and add the player to the team
        teams[team_name]["purse"] -= player["Selling Price"]
        teams[team_name]["players"].append({key: player[key] for key in ["Name", "Role", "Rating", "Selling Price"]})
        # Remove pre-assigned players from the available players list
        players_df = players_df[players_df["Name"] != player["Name"]]


# Initialize session state for auction data
if "auction_state" not in st.session_state:
    st.session_state.auction_state = {
        "available_players": players_df.copy(),
        "current_player": None,
        "current_bid": 0,
        "winning_team": None,
        "auction_history": [],
    }

# Initialize bidding teams
def display_team_info(team_name):
    """Display team information including players and purse."""
    st.subheader(f"{team_name} - Purse: {teams[team_name]['purse']} Cr", anchor=team_name)
    
    team_players = pd.DataFrame(teams[team_name]["players"])
    
    if not team_players.empty:
        for role in team_players["Role"].unique():
            st.write(f"**{role}**")
            role_players = team_players[team_players["Role"] == role].sort_values(by="Rating", ascending=False)
            st.dataframe(role_players[["Name", "Rating", "Selling Price"]])
    else:
        st.write("No players yet.")
        
    st.markdown(f"---")

def display_available_players():
    """Display players still available for bidding."""
    st.subheader("Players Still Available")
    available_players = st.session_state.auction_state["available_players"]
    
    if not available_players.empty:
        # Create columns for each role
        roles = available_players["Role"].unique()
        cols = st.columns(len(roles))  # Create one column for each role

        for i, role in enumerate(roles):
            with cols[i]:
                st.write(f"**{role}**")
                role_players = available_players[available_players["Role"] == role].sort_values(by="Rating", ascending=False)
                st.dataframe(role_players[["Name", "Rating"]])

    else:
        st.write("No players left.")

def start_auction():
    """Start a new auction round by selecting a player."""
    if st.session_state.auction_state["current_player"] is None and not st.session_state.auction_state["available_players"].empty:
        selected_player = st.session_state.auction_state["available_players"].sample(1).iloc[0]
        st.session_state.auction_state["current_player"] = selected_player
        st.session_state.auction_state["current_bid"] = 1.5  # Set base price to 1.5 Cr
        st.session_state.auction_state["winning_team"] = None
        st.write(f"Next Player: {selected_player['Name']} (Base Price: 1.5 Cr)")
        st.write(f"**Role**: {selected_player['Role']}")
        st.write(f"**Rating**: {selected_player['Rating']}")
    elif st.session_state.auction_state["current_player"] is not None:
        current_player = st.session_state.auction_state["current_player"]
        st.write(f"Current Player: {current_player['Name']}")
        st.write(f"**Role**: {current_player['Role']}")
        st.write(f"**Rating**: {current_player['Rating']}")

def finalize_auction():
    """Finalize the auction for the current player."""
    winning_team = st.session_state.auction_state["winning_team"]
    
    if winning_team:
        player = st.session_state.auction_state["current_player"]
        price = st.session_state.auction_state["current_bid"]

        # Update team purse and player list
        teams[winning_team]["purse"] -= price
        teams[winning_team]["players"].append({**player.to_dict(), "Selling Price": price})

        # Remove player from available players
        st.session_state.auction_state["available_players"] = \
            st.session_state.auction_state["available_players"][st.session_state.auction_state["available_players"]["Name"] != player["Name"]]

        # Log auction history
        st.session_state.auction_state["auction_history"].append({"player": player, "team": winning_team, "price": price})
        
        reset_current_player()
        
        st.success(f"{player['Name']} ({player['Role']}, Rating: {player['Rating']}) sold to {winning_team} for {price} Cr")
        
    else:
        handle_unsold_player()


def reset_current_player():
    """Reset the current player and bid state."""
    st.session_state.auction_state["current_player"] = None
    st.session_state.auction_state["current_bid"] = 0
    st.session_state.auction_state["winning_team"] = None

def handle_unsold_player():
    """Handle case when no bids are placed for the current player."""
    player = st.session_state.auction_state["current_player"]
    
    if player is not None:
        # Log unsold player in auction history
        st.session_state.auction_state["auction_history"].append({"player": player, "team": None, "price": 0})
        
        # Remove the player from the available players list permanently
        st.session_state.auction_state["available_players"] = \
            st.session_state.auction_state["available_players"][st.session_state.auction_state["available_players"]["Name"] != player["Name"]]
        
        reset_current_player()
        
        st.warning(f"{player['Name']} goes unsold")

def undo_last_auction():
    """Undo the last auction action."""
    if st.session_state.auction_state["auction_history"]:
        last_auction = st.session_state.auction_state["auction_history"].pop()
        
        if last_auction.get("team"):
            teams[last_auction["team"]]["purse"] += last_auction["price"]
            teams[last_auction["team"]]["players"].pop()
            last_player_df = pd.DataFrame([last_auction["player"]])
            # Re-add player to available players
            st.session_state.auction_state["available_players"] = pd.concat(
                [st.session_state.auction_state["available_players"], last_player_df], ignore_index=True)

        reset_current_player()
        
        st.success("Last auction undone.")
    else:
        st.warning("No auctions to undo.")

# Streamlit app layout
st.title("Player Auction")

if (st.button("Start Auction", key="start_auction_button")):
    start_auction()

if (st.button("Finalize Auction", key="finalize_auction_button")):
    finalize_auction()

# Prevent further bid from the winning team
if (current_player := st.session_state.auction_state.get("current_player")) is not None:
    cols = st.columns(3)

    st.write(f"**Current Player**: {current_player['Name']}")
    st.write(f"**Role**: {current_player['Role']}")
    st.write(f"**Rating**: {current_player['Rating']}")
    st.write(f"**Current Bid**: {st.session_state.auction_state['current_bid']} Cr")
    
    for i, team_name in enumerate(teams):
        # Ensure the team's bid button stays visible for all teams
        with cols[i]:
#            st.markdown(f"<div style='background-color: {'#FFD700' if team_name == 'Mospher' else '#1E90FF' if team_name == 'Goku' else '#32CD32'}; padding: 10px;'>", unsafe_allow_html=True)
            if st.button(f"{team_name} Bid", key=f"bid_button_{team_name}"):
                # If the team already has the current bid, prevent them from bidding
                if st.session_state.auction_state['winning_team'] == team_name:
                    st.write(f"{team_name} has already placed the highest bid of {st.session_state.auction_state['current_bid']} Cr!")
                    continue  # Skip this team
                
                bid_amount_increment = 0.5
                new_bid_amount = round(st.session_state.auction_state['current_bid'] + bid_amount_increment, 1)
                
                if new_bid_amount <= teams[team_name]["purse"]:  # Ensure the team can afford the bid
                    # Update current bid and set the winning team
                    if new_bid_amount > st.session_state.auction_state['current_bid']:
                        # Only update winning team if new bid exceeds current bid
                        st.session_state.auction_state['current_bid'] = new_bid_amount
                        st.session_state.auction_state['winning_team'] = team_name
                    
                    # Notify about the bid placed
                    st.write(f"{team_name} placed a bid of {new_bid_amount} Cr!")
                else:
                    st.write(f"{team_name} cannot bid due to insufficient purse.")
#            st.markdown(f"</div>", unsafe_allow_html=True)

# Display current bid information if there is a winning team
if (winning_team := st.session_state.auction_state.get("winning_team")) is not None:
    current_bid = round(st.session_state.auction_state['current_bid'], 1)
    st.markdown(f"**Current Bid:** {current_bid} Cr by **{winning_team}**", unsafe_allow_html=True)

if (st.button("Undo Last Auction", key="undo_last_auction_button")):
    undo_last_auction()

st.write("---")

# Display teams' information
team_cols = st.columns(3)
for i, team_name in enumerate(teams):
    with team_cols[i]:
        display_team_info(team_name)

st.write("---")
display_available_players()
