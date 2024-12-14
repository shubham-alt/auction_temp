import streamlit as st
import pandas as pd

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

# Make sure 'bidding_teams' exists in auction_state
if "bidding_teams" not in st.session_state.auction_state:
    st.session_state.auction_state["bidding_teams"] = list(teams.keys())  # Initialize bidding teams


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
        selected_player = st.session_state.auction_state["available_players"].sample(1).iloc[0]
        st.session_state.auction_state["current_player"] = selected_player
        st.session_state.auction_state["current_bid"] = 2  # Set base price to 2 Cr
        st.session_state.auction_state["winning_team"] = None
        st.session_state.auction_state["bidding_teams"] = list(teams.keys())  # Reset bidding teams
        st.write(f"Next Player: {selected_player['Name']} (Base Price: 2 Cr)")
    elif st.session_state.auction_state["current_player"] is not None:
        st.write(f"Current Player: {st.session_state.auction_state['current_player']['Name']}")

def finalize_auction():
    """Finalize the auction for the current player."""
    winning_team = st.session_state.auction_state["winning_team"]
    if winning_team:
        player = st.session_state.auction_state["current_player"]
        price = st.session_state.auction_state["current_bid"]
        teams[winning_team]["purse"] -= price
        teams[winning_team]["players"].append({**player.to_dict(), "Selling Price": price})
        st.session_state.auction_state["available_players"] = st.session_state.auction_state["available_players"][st.session_state.auction_state["available_players"]["Name"] != player["Name"]]
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
    st.session_state.auction_state["bidding_teams"] = list(teams.keys())  # Reset bidding teams

def handle_unsold_player():
    """Handle case when no bids are placed for the current player."""
    player = st.session_state.auction_state["current_player"]
    if player is not None:
        st.session_state.auction_state["auction_history"].append({"player": player, "team": None, "price": 0})
        reset_current_player()
        st.warning(f"{player['Name']} goes unsold")

def undo_last_auction():
    """Undo the last auction action."""
    if st.session_state.auction_state["auction_history"]:
        last_auction = st.session_state.auction_state["auction_history"].pop()
        if last_auction.get("team"):
            teams[last_auction["team"]]["purse"] += last_auction["price"]
            teams[last_auctio
