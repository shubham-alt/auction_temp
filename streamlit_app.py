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
    st.subheader(team_name)
    team_players = pd.DataFrame(teams[team_name]["players"])
    
    if not team_players.empty:
        for role in team_players["Role"].unique():
            st.write(f"**{role}**")
            role_players = team_players[team_players["Role"] == role].sort_values(by="Rating", ascending=False)
            st.dataframe(role_players[["Name", "Rating", "Selling Price"]])
    else:
        st.write("No players yet.")
    
    st.write(f"Purse: {teams[team_name]['purse']} Cr")

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
    elif st.session_state.auction_state["current_player"] is not None:
        st.write(f"Current Player: {st.session_state.auction_state['current_player']['Name']}")

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
        
        st.success(f"{player['Name']} sold to {winning_team} for {price} Cr")
        
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

if (current_player := st.session_state.auction_state.get("current_player")) is not None:
    cols = st.columns(3)
    
    for i, team_name in enumerate(teams):
        # Ensure the team's bid button stays visible for all teams
        if cols[i].button(f"{team_name} Bid", key=f"bid_button_{team_name}"):
            bid_amount_increment = 0.5
            new_bid_amount = round(st.session_state.auction_state['current_bid'] + bid_amount_increment, 1)
            
            if new_bid_amount <= teams[team_name]["purse"]:  # Ensure the team can afford the bid
                # Update current bid and set the winning team
                if new_bid_amount > (st.session_state.auction_state['current_bid']):
                    # Only update winning team if new bid exceeds current bid
                    st.session_state.auction_state['current_bid'] = new_bid_amount
                    st.session_state.auction_state['winning_team'] = team_name
                
                # Notify about the bid placed
                st.write(f"{team_name} placed a bid of {new_bid_amount} Cr!")
            else:
                cols[i].write(f"{team_name} cannot bid due to insufficient purse.")

# Display current bid information if there is a winning team
if (winning_team := st.session_state.auction_state.get("winning_team")) is not None:
    current_bid = round(st.session_state.auction_state['current_bid'], 1)
    st.write(f"Current Bid: {current_bid} Cr by {winning_team}")

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
