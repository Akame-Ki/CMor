
from customtkinter import *
from random import choice
import requests
import json
import sys
import subprocess

# Load the server address from the configuration file
with open("server.json", "r", encoding="utf-8") as file:
    config = json.load(file)

server = config["server"].rstrip("/")

# Configure the main application window
app = CTk()
app.title("CMor")
app.geometry("300x390")
app.resizable(False, False)


player1_state_label = CTkLabel(app,text=f"Player 1 state : Not connected")
player2_state_label = CTkLabel(app,text=f"Player 2 state : Not connected")

# default gameover to false
game_over = False

# Initialize the local game board and its buttons
game_table = [[None for _ in range(3)] for _ in range(3)]
buttons = [[None for _ in range(3)] for _ in range(3)]

# Determine whether this client is joining an existing game
joining_game = len(sys.argv) > 1

try:
    if joining_game:
        # Retrieve the session ID passed by the menu
        if len(sys.argv) < 5:
            print("code must be provided with6 charcters")

        session_id = sys.argv[1].strip()

        # Ask the server to assign the remaining player ID
        response = requests.post(
            f"{server}/game/{session_id}/join",
            timeout=5
        )
    else:
        # Randomly select the host player's ID
        host_player = choice([1, 2])

        # Ask the server to create a new game
        response = requests.post(
            f"{server}/game/start",
            json={"player_id": host_player},
            timeout=5
        )

    # Display the server response if the request fails
    if not response.ok:
        print(f"HTTP error: {response.status_code}")
        print(f"Server response: {response.text}")
        response.raise_for_status()

    # Decode the server response
    response_data = response.json()

    if joining_game:
        # Retrieve the session ID and assigned player ID
        host_player = response_data["player_id"]
    else:
        # Retrieve the session ID created by the server
        session_id = response_data["session_id"]

except requests.RequestException as error:
    # Display network and HTTP errors
    print(f"Connection error: {error}")
    app.destroy()
    sys.exit(1)

except (ValueError, KeyError) as error:
    # Handle invalid JSON or missing response fields
    print(f"Invalid server response: {error}")
    app.destroy()
    sys.exit(1)

# Define both player IDs
player1 = host_player
player2 = 2 if host_player == 1 else 1

# Store the local player's ID
my_player = host_player

# Player 1 always starts the game
current_player = 1

# Track whether the game board is currently being refreshed
refresh_in_progress = False

# Display the session ID
CTkLabel(
    app,
    text=f"Session: {session_id}",
    font=("Arial", 14, "bold")
).pack(pady=(10, 2))

# Display the local player's ID
player_label = CTkLabel(
    app,
    text=f"You are player {my_player}"
)
player_label.pack(pady=2)

# Display whose turn it is
turn_label = CTkLabel(
    app,
    text=f"Player {current_player}'s turn"
)
turn_label.pack(pady=2)


def get_game():
    global game_over,player1_state_label,player2_state_label
    """Retrieve the latest game board from the server."""
    response = requests.get(
        f"{server}/game/{session_id}/board",
        timeout=5
    )
    player1_state = response.json()["player1_stage"]
    player2_state = response.json()["player2_stage"]
    if(player1_state == 1):
        player1_state = "Connected"
    else:
        player1_state = "Not connected"
    if(player2_state == 1):
        player2_state = "Connected"
    else:
        player2_state = "Not connected"
    player1_state_label.configure(text=f"Player 1 state : {player1_state}")
    player2_state_label.configure(text=f"Player 2 state : {player2_state}")

    

    end_game = response.json()["end_game"]
    if end_game and game_over == False:
        game_over = True
        win_popup = CTkToplevel(app)
        win_popup.title("Game over")
        win_popup.geometry("250x150")
        win_popup.resizable(False, False)
        CTkLabel(
            win_popup,
            text=f"Résultat: {end_game}",
            font=("Arial", 18, "bold")
        ).pack(pady=20)
        def win_and_go_to_menu():
            win_popup.destroy()
            app.destroy()
            subprocess.Popen([sys.executable, "menu.py"])
        CTkButton(
            win_popup,
            text="OK",
            command=win_and_go_to_menu
        ).pack(pady=5)
        win_popup.protocol("WM_DELETE_WINDOW", win_and_go_to_menu)
        win_popup.transient(app)
        win_popup.grab_set()

        


    response.raise_for_status()
    return response.json()["table"]


def post_game(actual_game):
    """Send the current game board to the server."""

    response = requests.post(
        f"{server}/game/{session_id}/board",
        json={"table": actual_game},
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def update_board(new_table):
    """Update the local board and its buttons using server data."""

    global game_table, current_player

    # Copy the received board to avoid modifying the server response
    game_table = [row[:] for row in new_table]

    # Update every button to match the latest server board
    for row in range(3):
        for col in range(3):
            sign = game_table[row][col]
            button = buttons[row][col]

            if sign == "X":
                # Display player 1's sign
                button.configure(
                    text="X",
                    fg_color="red",
                    text_color="white"
                )

            elif sign == "O":
                # Display player 2's sign
                button.configure(
                    text="O",
                    fg_color="blue",
                    text_color="white"
                )

            else:
                # Reset an empty cell
                button.configure(
                    text="",
                    fg_color="white",
                    text_color="black"
                )

    # Count the moves currently stored on the server
    move_count = sum(
        1
        for row in game_table
        for cell in row
        if cell is not None
    )

    # Alternate turns according to the number of moves
    current_player = 1 if move_count % 2 == 0 else 2

    # Display the current turn
    if current_player == my_player:
        turn_label.configure(
            text=f"Your turn (Player {current_player})"
        )
    else:
        turn_label.configure(
            text=f"Player {current_player}'s turn"
        )


def refresh_game():
    """Refresh the board from the server every three seconds."""

    global refresh_in_progress

    try:
        # Retrieve the latest board from the server
        latest_table = get_game()

        # Update the interface with the received board
        update_board(latest_table)

    except requests.RequestException as error:
        # Report connection errors without closing the application
        print(f"Failed to refresh the board: {error}")

    finally:
        # Schedule the next refresh after three seconds
        if app.winfo_exists():
            app.after(1000, refresh_game)


def add_sign(button, row, col):
    """Place the local player's sign on the board."""

    # Prevent moves when it is not the local player's turn
    if current_player != my_player:
        print("It's not your turn.")
        return

    # Prevent a player from clicking an occupied cell
    if game_table[row][col] is not None:
        print("This cell is already occupied.")
        return

    # Select the sign belonging to the local player
    sign = "X" if my_player == 1 else "O"

    # Create a copy of the board before applying the move
    updated_table = [line[:] for line in game_table]
    updated_table[row][col] = sign

    try:
        # Send the updated board to the server
        post_game(updated_table)

        # Retrieve the authoritative board after the move
        latest_table = get_game()
        update_board(latest_table)

        print(f"Board synchronized: {game_table}")

    except requests.RequestException as error:
        # Report errors when sending or retrieving the board
        print(f"Failed to synchronize the board: {error}")

        # Restore the board from the server if possible
        try:
            update_board(get_game())
        except requests.RequestException:
            print("Could not retrieve the latest server board.")


# Create the 3x3 game board
for row in range(3):
    for col in range(3):

        # Create one button for each cell
        button = CTkButton(
            app,
            text="",
            width=80,
            height=65,
            fg_color="white",
            text_color="black",
            hover_color="lightgray"
        )

        # Store the button in the grid
        buttons[row][col] = button

        # Connect the button to its corresponding cell
        button.configure(
            command=lambda b=button, r=row, c=col: add_sign(b, r, c)
        )

        # Position the button in the window
        button.place(
            x=10 + col * 95,
            y=105 + row * 75
        )

player1_state_label.place(y=330)
player2_state_label.place(y=360)

# Retrieve the initial board and start automatic refreshing
refresh_game()

# Start the application's event loop
app.mainloop()
