import streamlit as st
import pandas as pd
import random

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

if "auction_state" not in st.session_state:
    st.session_state.auction_state = {
        "available_players": players_df.copy(),
        "current_player": None,
        "current_bid": 0,
        "winning_team": None,
        "auction_history": [],  # Store auction history for undo
    }


def display_team_info(team_name):
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
    if not st.session_state.auction_state["available_players"].empty:
        st.session_state.auction_state["current_player"] = st.session_state.auction_state["available_players"].sample(1).iloc[0]
        st.session_state.auction_state["current_bid"] = 2
        st.session_state.auction_state["winning_team"] = None
        st.write(f"Next Player: {st.session_state.auction_state['current_player']['Name']} (Base Price: 2 Cr)")
    else:
        st.write("No more players available for auction.")

def finalize_auction():
    if st.session_state.auction_state["winning_team"]:
        winning_team = st.session_state.auction_state["winning_team"]
        player = st.session_state.auction_state["current_player"]
        price = st.session_state.auction_state["current_bid"]

        teams[winning_team]["purse"] -= price
        teams[winning_team]["players"].append({**player.to_dict(), "Selling Price": price})

        st.session_state.auction_state["available_players"] = st.session_state.auction_state["available_players"][st.session_state.auction_state["available_players"]["Name"] != player["Name"]]
        st.write(f"{player['Name']} sold to {winning_team} for {price} Cr")
        st.session_state.auction_state["auction_history"].append({"player": player, "team": winning_team, "price": price})
        st.session_state.auction_state["current_player"] = None

    else:
        st.write("No bids placed for this player.")
        if st.session_state.auction_state["current_player"] is not None:
            st.session_state.auction_state["auction_history"].append({"player": st.session_state.auction_state["current_player"], "team": None, "price": 0})
            st.session_state.auction_state["current_player"] = None
            st.write(f"{player['Name']} goes unsold")


def undo_last_auction():
    if st.session_state.auction_state["auction_history"]:
        last_auction = st.session_state.auction_state["auction_history"].pop()
        if last_auction["team"]:
            teams[last_auction["team"]]["purse"] += last_auction["price"]
            teams[last_auction["team"]]["players"].pop()
            st.session_state.auction_state["available_players"] = pd.concat([st.session_state.auction_state["available_players"], pd.DataFrame([last_auction["player"]])], ignore_index=True)
        st.write("Last auction undone.")
    else:
        st.write("No auctions to undo.")

st.title("Player Auction")

if st.button("Start Auction"):
    start_auction()

if st.session_state.auction_state["current_player"] is not None:
    cols = st.columns(3)
    bid_placed = False
    for i, team_name in enumerate(teams):
        if st.session_state.auction_state["winning_team"] != team_name:
            if cols[i].button(f"{team_name} Bid"):
                st.session_state.auction_state["current_bid"] += 0.5
                st.session_state.auction_state["winning_team"] = team_name
                bid_placed = True
    if st.session_state.auction_state["winning_team"]:
        st.write(f"Current Bid: {st.session_state.auction_state['current_bid']} Cr by {st.session_state.auction_state['winning_team']}")

if st.button("Finalize Auction"):
    finalize_auction()

if st.button("Next Player"):
    start_auction()

if st.button("Pass"):
    finalize_auction()

if st.button("Undo Last Auction"):
    undo_last_auction()

st.write("---")
team_cols = st.columns(3)
for i, team_name in enumerate(teams):
    with team_cols[i]:
        display_team_info(team_name)

st.write("---")
display_available_players()
