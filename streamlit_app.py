import streamlit as st
import pandas as pd

# Load player data
try:
    players_df = pd.read_csv("players_data.csv")
except FileNotFoundError:
    st.error("players_data.csv not found. Please upload the file.")
    st.stop()

# Initialize teams
teams = {
    "Mospher": {"purse": 120, "players": []},
    "Goku": {"purse": 120, "players": []},
    "Maverick": {"purse": 120, "players": []},
}

# Initialize session state if not already done
if "auction_state" not in st.session_state:
    st.session_state.auction_state = {
        "available_players": players_df.copy(),
        "current_player": None,
        "current_bid": 0,
        "winning_team": None,
        "auction_history": [],
    }

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
        for role in available_players["Role"].unique():
            st.write(f"**{role}**")
            role_players = available_players[available_players["Role"] == role].sort_values(by="Rating", ascending=False)
            st.dataframe(role_players[["Name", "Rating"]])
    else:
        st.write("No players left.")

def start_auction():
    """Start a new auction round by selecting a player."""
    if st.session_state.auction_state["current_player"] is None and not st.session_state.auction_state["available_players"].empty:
        # Select a random player from available players
        selected_player = st.session_state.auction_state["available_players"].sample(1).iloc[0]
        st.session_state.auction_state["current_player"] = selected_player
        st.session_state.auction_state["current_bid"] = 2
        st.session_state.auction_state["winning_team"] = None
        st.write(f"Next Player: {selected_player['Name']} (Base Price: 2 Cr)")
    else:
        current_player = st.session_state.auction_state["current_player"]
        if current_player is not None:
            st.write(f"Current Player: {current_player['Name']}")

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
            # Re-add player to available players
            last_player_df = pd.DataFrame([last_auction["player"]])
            st.session_state.auction_state["available_players"] = pd.concat(
                [st.session_state.auction_state["available_players"], last_player_df], ignore_index=True)

        reset_current_player()
        
        st.success("Last auction undone.")
    else:
        st.warning("No auctions to undo.")

# Streamlit app layout
st.title("Player Auction")

# Adding unique keys to buttons to avoid duplicate IDs error
if (st.button("Start Auction", key="start_auction_button")):
    start_auction()

if (st.button("Finalize Auction", key="finalize_auction_button")):
    finalize_auction()

if (current_player := st.session_state.auction_state.get("current_player")) is not None:
    cols = st.columns(3)
    
    for i, team_name in enumerate(teams):
        # Prevent the winning team from placing a bid again
        if team_name != (st.session_state.auction_state.get("winning_team")):
            if cols[i].button(f"{team_name} Bid", key=f"bid_button_{team_name}"):
                # Increase bid and set winning team
                bid_amount_increment = 0.5
                new_bid_amount = round(st.session_state.auction_state['current_bid'] + bid_amount_increment, 1)
                
                if new_bid_amount <= teams[team_name]["purse"]:  # Check if the team can afford the new bid
                    # Update current bid and winning team
                    st.session_state.auction_state['current_bid'] = new_bid_amount
                    st.session_state.auction_state['winning_team'] = team_name
