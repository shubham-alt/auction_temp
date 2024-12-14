import streamlit as st
import pandas as pd
import random
import time

# Load player data
player_data = pd.read_csv("players_data.csv")  # File must have columns: Name, Rating, Role

# Initialize state
if "auction_pool" not in st.session_state:
    st.session_state.auction_pool = player_data.to_dict(orient="records")
    st.session_state.teams = {"Mospher": [], "Goku": [], "Maverick": []}
    st.session_state.team_purse = {"Mospher": 120, "Goku": 120, "Maverick": 120}
    st.session_state.current_player = None
    st.session_state.current_bid = {"price": 0, "winner": None}
    st.session_state.timer_start = None
    st.session_state.timer_duration = 15
    st.session_state.auction_history = []

# Helper functions
def reset_timer():
    st.session_state.timer_start = time.time()

def get_remaining_time():
    if st.session_state.timer_start:
        elapsed = time.time() - st.session_state.timer_start
        return max(0, st.session_state.timer_duration - elapsed)
    return st.session_state.timer_duration

def start_new_auction():
    if not st.session_state.auction_pool:
        st.error("Auction has ended! No more players in the pool.")
        return

    st.session_state.current_player = random.choice(st.session_state.auction_pool)
    st.session_state.auction_pool.remove(st.session_state.current_player)

    st.session_state.current_bid["price"] = 2  # Base price
    st.session_state.current_bid["winner"] = None
    reset_timer()

def place_bid(team):
    if st.session_state.current_player:
        next_bid = st.session_state.current_bid["price"] + 0.5
        if st.session_state.team_purse[team] >= next_bid and st.session_state.current_bid["winner"] != team:
            st.session_state.current_bid["price"] = next_bid
            st.session_state.current_bid["winner"] = team
            reset_timer()
        else:
            st.warning(f"{team} cannot bid. Insufficient funds or current highest bidder!")

def finalize_auction():
    current_player = st.session_state.current_player
    current_bid = st.session_state.current_bid

    if current_bid["winner"]:
        winner = current_bid["winner"]
        st.session_state.team_purse[winner] -= current_bid["price"]
        st.session_state.teams[winner].append({**current_player, "price": current_bid["price"]})
        st.success(f"{current_player['Name']} sold to {winner} for ₹{current_bid['price']} crore.")
    else:
        st.warning(f"{current_player['Name']} remains unsold.")

    st.session_state.current_player = None
    st.session_state.current_bid = {"price": 0, "winner": None}

def pass_player():
    finalize_auction()

def undo_last_auction():
    if st.session_state.auction_history:
        last_auction = st.session_state.auction_history.pop()
        if last_auction["winner"] != "Unsold":
            st.session_state.team_purse[last_auction["winner"]] += last_auction["price"]
            st.session_state.teams[last_auction["winner"]].remove(last_auction["player"])
        st.session_state.auction_pool.append(last_auction["player"])
        st.success("Last auction undone.")
    else:
        st.warning("No auction to undo.")

# UI Layout
st.title("Player Auction")

# Timer and Auction Status
with st.empty() as timer_placeholder:
    if st.session_state.current_player:
        for _ in range(int(get_remaining_time())):
            time_left = int(get_remaining_time())
            if time_left <= 0:
                finalize_auction()
                break
            timer_placeholder.markdown(f"**Time Remaining:** {time_left} seconds")
            time.sleep(1)
    else:
        timer_placeholder.markdown("No player is currently being auctioned.")

st.subheader("Current Auction")
if st.session_state.current_player:
    st.write(f"**Player:** {st.session_state.current_player['Name']} ({st.session_state.current_player['Role']})")
    st.write(f"**Rating:** {st.session_state.current_player['Rating']}")
    st.write(f"**Current Bid:** ₹{st.session_state.current_bid['price']} crore by {st.session_state.current_bid['winner'] or 'None'}")

# Buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Mospher Bid"):
        place_bid("Mospher")
with col2:
    if st.button("Goku Bid"):
        place_bid("Goku")
with col3:
    if st.button("Maverick Bid"):
        place_bid("Maverick")
with col4:
    if st.button("Pass"):
        pass_player()
with col5:
    if st.button("Next Player"):
        start_new_auction()

if st.button("Undo Last Auction"):
    undo_last_auction()

# Display Team Information
st.subheader("Team Status")
team_cols = st.columns(3)
for i, (team, players) in enumerate(st.session_state.teams.items()):
    with team_cols[i]:
        st.write(f"**{team} (Remaining Purse: ₹{st.session_state.team_purse[team]} crore)**")
        if players:
            df = pd.DataFrame(players).sort_values(by=["Role", "Rating"], ascending=[True, False])
            st.table(df[["Name", "Role", "Rating", "price"]])
        else:
            st.write("No players.")

# Remaining Players
st.subheader("Remaining Players")
remaining_players = pd.DataFrame(st.session_state.auction_pool).sort_values(by=["Role", "Rating"], ascending=[True, False])
for role, group in remaining_players.groupby("Role"):
    st.write(f"**{role}**")
    st.table(group[["Name", "Rating"]])


