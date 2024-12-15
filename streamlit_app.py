import streamlit as st
import pandas as pd
import time

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
        "auction_progress": "Starting",  # Initial state for auction progress
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
        st.session_state.auction_state["auction_progress"] = "Bidding in Progress"
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
        
        # Display winner animation
        winner_animation(winning_team, player['Name'])

    else:
        handle_unsold_player()

def reset_current_player():
    """Reset the current player and bid state."""
    st.session_state.auction_state["current_player"] = None
    st.session_state.auction_state["current_bid"] = 0
    st.session_state.auction_state["winning_team"] = None
    st.session_state.auction_state["auction_progress"] = "Waiting for Next Player"

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

def winner_animation(winning_team, player_name):
    """Animate the winner and the sold player with a flashing text effect."""
    for i in range(5):  # Flashing text for 5 times
        st.markdown(f"<h1 style='color: green; text-align: center;'>🎉 {winning_team} wins {player_name}! 🎉</h1>", unsafe_allow_html=True)
        time.sleep(0.5)
        st.markdown("<h1 style='color: white; text-align: center;'>🎉 🎉 🎉 </h1>", unsafe_allow_html=True)
        time.sleep(0.5)

# Streamlit app layout
st.title("Player Auction")

# Add a background color and layout
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
        }
        .main {
            background-color: #ffffff;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

if (st.button("Start Auction", key="start_auction_button")):
    start_auction()

if (st.button("Finalize Auction", key="finalize_auction_button")):
    finalize_auction()

# Display current bid information if there is a winning team
if (current_player := st.session_state.auction_state.get("current_player")) is not None:
    cols = st.columns(3)

    st.write(f"**Current Player**: {current_player['Name']}")
    st.write(f"**Role**: {current_player['Role']}")
    st.write(f"**Rating**: {current_player['Rating']}")
    
    for i, team_name in enumerate(teams):
        with cols[i]:
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

# Display auction progress indicator
st.subheader(f"Auction Progress: {st.session_state.auction_state['auction_progress']}")

# Display top 5 players by selling price
top_players = sorted(st.session_state.auction_state["auction_history"], key=lambda x: x["price"], reverse=True)[:5]
top_players_info = [{"Player": p["player"]["Name"], "Team": p["team"], "Price": p["price"]} for p in top_players]
st.subheader("Top 5 Players by Selling Price")
st.table(top_players_info)

# Display auction progress with current purse remaining for each team
st.subheader("Teams Purse Progress")
team_purse_data = [{"Team": team_name, "Purse Left": teams[team_name]["purse"]} for team_name in teams]
st.table(team_purse_data)

# Display auction history (top 10 most recent auctions)
st.subheader("Auction History")
auction_history = [{"Player": h["player"]["Name"], "Team": h["team"], "Price": h["price"]} for h in
                   st.session_state.auction_state["auction_history"]]
st.table(auction_history[:10])
