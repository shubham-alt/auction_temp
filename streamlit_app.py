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
        "bidding_teams": list(teams.keys())  # Keep track of bidding teams
    }

def display_team_info(team_name):
    # Function to display team info (e.g., players, purse)
    st.subheader(f"{team_name} Team")
    team_players = pd.DataFrame(teams[team_name]["players"])
    if not team_players.empty:
        st.dataframe(team_players[["Name", "Role", "Rating", "Selling Price"]])
    else:
        st.write("No players yet.")
    st.write(f"Purse: {teams[team_name]['purse']} Cr")

def display_available_players():
    # Function to display players still available for bidding
    st.subheader("Players Still Available")
    available_players = st.session_state.auction_state["available_players"]
    if not available_players.empty:
        st.dataframe(available_players[["Name", "Role", "Rating"]])
    else:
        st.write("No players left.")

def start_auction():
    """Start a new auction round."""
    if st.session_state.auction_state["current_player"] is None and not st.session_state.auction_state["available_players"].empty:
        selected_player = st.session_state.auction_state["available_players"].sample(1).iloc[0]
        st.session_state.auction_state["current_player"] = selected_player
        st.session_state.auction_state["current_bid"] = 2
        st.session_state.auction_state["winning_team"] = None
        st.session_state.auction_state["bidding_teams"] = list(teams.keys())  # Reset bidding teams
        st.write(f"Next Player: {selected_player['Name']} (Base Price: 2 Cr)")
    elif st.session_state.auction_state["current_player"] is not None:
        st.write(f"Current Player: {st.session_state.auction_state['current_player']['Name']}")

def finalize_auction():
    """Finalize the auction."""
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
    st.session_state.auction_state["current_player"] = None
    st.session_state.auction_state["current_bid"] = 0
    st.session_state.auction_state["winning_team"] = None
    st.session_state.auction_state["bidding_teams"] = list(teams.keys())  # Reset bidding teams

def handle_unsold_player():
    """Handle the case where a player goes unsold."""
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
            teams[last_auction["team"]]["players"].pop()
            last_player_df = pd.DataFrame([last_auction["player"]])
            st.session_state.auction_state["available_players"] = pd.concat([st.session_state.auction_state["available_players"], last_player_df], ignore_index=True)
        reset_current_player()
        st.success("Last auction undone.")
    else:
        st.warning("No auctions to undo.")

# Streamlit app layout
st.title("Player Auction")

if st.button("Start Auction", key="start_auction_button"):
    start_auction()

if st.button("Finalize Auction", key="finalize_auction_button"):
    finalize_auction()

if (current_player := st.session_state.auction_state.get("current_player")) is not None:
    cols = st.columns(3)
    bidding_teams = st.session_state.auction_state["bidding_teams"]
    for i, team_name in enumerate(teams):
        if team_name in bidding_teams:  # Only show bid buttons for bidding teams
            if cols[i].button(f"{team_name} Bid", key=f"bid_button_{team_name}"):
                bid_amount_increment = 0.5
                new_bid_amount = round(st.session_state.auction_state['current_bid'] + bid_amount_increment, 1)
                if new_bid_amount <= teams[team_name]["purse"]:
                    st.session_state.auction_state['current_bid'] = new_bid_amount
                    st.session_state.auction_state['winning_team'] = team_name
                    st.session_state.auction_state["bidding_teams"] = [t for t in bidding_teams if t != team_name]  # Remove current bidder

# Display current bid information
if (winning_team := st.session_state.auction_state.get("winning_team")) is not None:
    current_bid = round(st.session_state.auction_state['current_bid'], 1)
    st.write(f"Current Bid: {current_bid} Cr by {winning_team}")

if st.button("Undo Last Auction", key="undo_last_auction_button"):
    undo_last_auction()

st.write("---")

# Display teams' information
team_cols = st.columns(3)
for i, team_name in enumerate(teams):
    with team_cols[i]:
        display_team_info(team_name)

st.write("---")
display_available_players()
