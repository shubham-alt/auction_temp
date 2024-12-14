import streamlit as st
import pandas as pd
import random

# Load initial player data
player_data = pd.read_csv("players_data.csv")  # Ensure players_data.csv has columns: Name, Rating, Role
player_data = player_data.sort_values(by=["Role", "Rating"], ascending=[True, False])

# Initialize session state variables
if "auction_pool" not in st.session_state:
    st.session_state.auction_pool = player_data.to_dict(orient="records")
    st.session_state.teams = {"Mospher": [], "Goku": [], "Maverick": []}
    st.session_state.team_purse = {"Mospher": 120, "Goku": 120, "Maverick": 120}
    st.session_state.current_player = None
    st.session_state.current_bid = {"price": 0, "winner": None}
    st.session_state.auction_history = []  # Store auction history for undo functionality

# Functions
def start_new_auction():
    """Start auction for a new player."""
    if not st.session_state.auction_pool:
        st.warning("Auction has ended! No more players in the pool.")
        return

    st.session_state.current_player = random.choice(st.session_state.auction_pool)
    st.session_state.auction_pool.remove(st.session_state.current_player)
    st.session_state.current_bid = {
        "price": 2,  # Base price for every player
        "winner": None,
    }

def place_bid(bidder):
    """Place a bid for the current player."""
    if st.session_state.current_player and st.session_state.current_bid["winner"] != bidder:
        next_bid = st.session_state.current_bid["price"] + 0.5
        if st.session_state.team_purse[bidder] >= next_bid:
            st.session_state.current_bid["price"] = next_bid
            st.session_state.current_bid["winner"] = bidder
        else:
            st.error(f"{bidder} does not have enough funds for this bid!")


def finalize_auction():
    """Finalize the auction for the current player."""
    if st.session_state.current_player:
        winner = st.session_state.current_bid["winner"]
        if winner:
            # Deduct funds and add player to the winning team
            st.session_state.team_purse[winner] -= st.session_state.current_bid["price"]
            st.session_state.teams[winner].append({
                **st.session_state.current_player,
                "price": st.session_state.current_bid["price"],
            })
            st.success(f"{st.session_state.current_player['Name']} sold to {winner} for ₹{st.session_state.current_bid['price']} crore.")
        else:
            st.warning(f"{st.session_state.current_player['Name']} remains unsold.")

        # Save auction history for undo functionality
        st.session_state.auction_history.append({
            "player": st.session_state.current_player,
            "bid": st.session_state.current_bid,
        })

        # Reset current auction
        st.session_state.current_player = None
        st.session_state.current_bid = {"price": 0, "winner": None}


def undo_last_auction():
    """Undo the last auction and restore the player to the pool."""
    if st.session_state.auction_history:
        last_auction = st.session_state.auction_history.pop()
        player = last_auction["player"]
        bid = last_auction["bid"]

        if bid["winner"]:
            winner = bid["winner"]
            st.session_state.team_purse[winner] += bid["price"]
            st.session_state.teams[winner] = [p for p in st.session_state.teams[winner] if p["Name"] != player["Name"]]

        st.session_state.auction_pool.append(player)
        st.info(f"Undid auction for {player['Name']}. Player restored to the pool.")

# Sidebar: Team Purse and Teams
st.sidebar.header("Team Information")
st.sidebar.subheader("Team Purse Remaining")
for team, purse in st.session_state.team_purse.items():
    st.sidebar.markdown(f"**{team}:** ₹{purse} crore")

st.sidebar.subheader("Teams")
for team, players in st.session_state.teams.items():
    st.sidebar.markdown(f"### {team}")
    team_df = pd.DataFrame(players).sort_values(by="Role", ascending=True)
    for role, grouped_players in team_df.groupby("Role"):
        st.sidebar.markdown(f"**{role}:**")
        for _, player in grouped_players.iterrows():
            st.sidebar.markdown(f"- {player['Name']} (₹{player['price']} crore)")

# Main Area
st.title("Player Auction System")

if st.session_state.current_player:
    st.header("Current Auction")
    player = st.session_state.current_player
    st.markdown(f"**Player:** {player['Name']} ({player['Role']})")
    st.markdown(f"**Rating:** {player['Rating']}")
    st.markdown(f"**Current Bid:** ₹{st.session_state.current_bid['price']} crore by {st.session_state.current_bid['winner'] or 'None'}")
else:
    st.markdown("No player is currently being auctioned.")

# Buttons for bidding and actions
st.subheader("Actions")
col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("Mospher Bid"):
    place_bid("Mospher")

if col2.button("Goku Bid"):
    place_bid("Goku")

if col3.button("Maverick Bid"):
    place_bid("Maverick")

if col4.button("Finalize Auction"):
    finalize_auction()

if col5.button("Undo Last Auction"):
    undo_last_auction()

if st.button("Next Player"):
    start_new_auction()

# Display remaining players in the auction pool
st.subheader("Players Yet to Be Auctioned")
pool_df = pd.DataFrame(st.session_state.auction_pool).sort_values(by=["Role", "Rating"], ascending=[True, False])
for role, grouped_players in pool_df.groupby("Role"):
    st.markdown(f"**{role}:**")
    st.dataframe(grouped_players[["Name", "Rating"]])
