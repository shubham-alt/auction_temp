import pandas as pd
import random
import time
from IPython.display import display, clear_output
from ipywidgets import Button, HBox, VBox, Output
import threading

# Mock player data for testing
player_data = pd.DataFrame([
    {"name": "Player A", "role": "Batsman", "rating": 88},
    {"name": "Player B", "role": "Bowler", "rating": 84},
    {"name": "Player C", "role": "All-Rounder", "rating": 92},
    {"name": "Player D", "role": "Wicketkeeper", "rating": 80},
    {"name": "Player E", "role": "Batsman", "rating": 76},
])

# Sort players by role and rating
player_data.sort_values(by=["role", "rating"], ascending=[True, False], inplace=True)

# Auction state
auction_pool = player_data.to_dict(orient="records")
teams = {"Ayush": [], "Shobhit": [], "Shubham": []}
team_purse = {"Ayush": 120, "Shobhit": 120, "Shubham": 120}  # Initial purse for each team
current_player = None
current_bid = {"price": 0, "winner": None}
auction_running = False
timer_start = None
timer_duration = 15

# Outputs
output = Output()
summary_output = Output()
teams_output = Output()

# Buttons
ayush_button = Button(description="Ayush Bid")
shobhit_button = Button(description="Shobhit Bid")
shubham_button = Button(description="Shubham Bid")
pass_button = Button(description="Pass")
next_player_button = Button(description="Start Auction")

# Functions
def reset_timer():
    global timer_start
    timer_start = time.time()

def get_remaining_time():
    if timer_start:
        elapsed = time.time() - timer_start
        return max(0, timer_duration - elapsed)
    return timer_duration

def start_new_auction():
    """Start a new auction for a player."""
    global current_player, current_bid, auction_running
    if auction_running:
        with output:
            clear_output(wait=True)
            print("Auction already running.")
        return
    
    if not auction_pool:
        with output:
            clear_output(wait=True)
            print("Auction has ended! No more players in the pool.")
        return

    current_player = random.choice(auction_pool)
    auction_pool.remove(current_player)

    # Set initial bid price based on rating
    current_bid["price"] = (
        2 if current_player["rating"] > 85 else
        1.5 if current_player["rating"] > 80 else 1
    )
    current_bid["winner"] = None
    reset_timer()
    auction_running = True
    start_auction_thread()  # Start the live auction thread
    update_display()

def place_bid(bidder):
    """Place a bid for the current player."""
    global current_bid, team_purse
    if not auction_running or current_player is None:
        with output:
            print("No auction is running.")
        return
    
    next_bid = current_bid["price"] + 0.5
    if team_purse[bidder] >= next_bid:
        current_bid["price"] = next_bid
        current_bid["winner"] = bidder
        reset_timer()  # Reset the timer after a successful bid
    else:
        with output:
            print(f"{bidder} does not have enough funds for this bid!")
    update_display()

def pass_bid():
    finalize_auction()

def finalize_auction():
    """Finalize the auction for the current player."""
    global current_player, current_bid, team_purse, auction_running
    auction_running = False
    if current_player is None:
        with output:
            clear_output(wait=True)
            print("No player to finalize.")
        return

    if current_bid["winner"]:
        winner = current_bid["winner"]
        team_purse[winner] -= current_bid["price"]
        teams[winner].append({**current_player, "price": current_bid["price"]})
        with output:
            print(f"{current_player['name']} won by {winner} for ₹{current_bid['price']} crore.")
    else:
        with output:
            print(f"{current_player['name']} remains unsold.")

    current_player = None
    current_bid = {"price": 0, "winner": None}
    update_summary()
    update_teams()

def update_display():
    """Update the auction display."""
    with output:
        clear_output(wait=True)
        if current_player:
            print(f"Auctioning: {current_player['name']} ({current_player['role']})")
            print(f"Rating: {current_player['rating']}")
            print(f"Current Bid: ₹{current_bid['price']} crore by {current_bid['winner'] or 'None'}")
            print(f"Time Remaining: {int(get_remaining_time())} seconds")
        else:
            print("No player is currently being auctioned.")
        print("\nTeam Purse Remaining:")
        for team, purse in team_purse.items():
            print(f"{team}: ₹{purse} crore")

def update_summary():
    """Update the summary of available players."""
    with summary_output:
        clear_output(wait=True)
        print("Players in Auction Pool:")
        pool_df = pd.DataFrame(auction_pool).sort_values(by=["role", "rating"], ascending=[True, False])
        display(pool_df[["name", "role", "rating"]])

def update_teams():
    """Update the teams and their players."""
    with teams_output:
        clear_output(wait=True)
        print("Teams and Their Players:")
        for team, players in teams.items():
            print(f"\n{team}  Remaining Purse: ₹{team_purse[team]} crore")
            for player in players:
                print(f"  {player['name']} (₹{player['price']} crore)")

def auction_loop():
    """Runs the auction logic in a background thread."""
    while auction_running:
        remaining_time = get_remaining_time()
        if remaining_time <= 0:
            finalize_auction()
            break
        time.sleep(1)
        update_display()

def start_auction_thread():
    """Start the auction in a separate thread."""
    thread = threading.Thread(target=auction_loop, daemon=True)
    thread.start()

# Button actions
ayush_button.on_click(lambda _: place_bid("Ayush"))
shobhit_button.on_click(lambda _: place_bid("Shobhit"))
shubham_button.on_click(lambda _: place_bid("Shubham"))
pass_button.on_click(lambda _: pass_bid())
next_player_button.on_click(lambda _: start_new_auction())

# Display layout
button_layout = HBox([ayush_button, shobhit_button, shubham_button, pass_button])
auction_info_layout = VBox([output, button_layout, next_player_button])
summary_layout = VBox([auction_info_layout, HBox([summary_output, teams_output])])

# Show the app
display(summary_layout)

# Initial updates
update_summary()
update_teams()
