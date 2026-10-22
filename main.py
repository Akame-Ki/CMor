
from customtkinter import *
from random import choice
import requests
import json
import sys

# Load the server address from the configuration file
with open("server.json", "r", encoding="utf-8") as file:
    config = json.load(file)

server = config["server"].rstrip("/")

# Configure the main application window
app = CTk()
app.title("CMor")
app.geometry("300x350")
app.resizable(False, False)

# Initialize the game board and its buttons
game_table = [[None for _ in range(3)] for _ in range(3)]
buttons = [[None for _ in range(3)] for _ in range(3)]

# Determine whether this client is joining an existing game
joining_game = len(sys.argv) > 1

try:
    if joining_game:
        # Retrieve the session ID passed by the menu
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
        # Retrieve the player ID assigned by the server
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

# Store the local player's ID separately from the current turn
my_player = host_player
current_player = 1

# Display the session ID and the local player's number
CTkLabel(
    app,
    text=f"Session: {session_id}",
    font=("Arial", 14, "bold")
).pack(pady=(10, 2))

player_label = CTkLabel(
    app,
    text=f"You are player {my_player}"
)
player_label.pack(pady=2)

turn_label = CTkLabel(
    app,
    text=f"Player {current_player}'s turn"
)
turn_label.pack(pady=2)


def post_game(actual_game, session_id):
    """Send the current board to the server."""

    response = requests.post(
        f"{server}/game/{session_id}/board",
        json={"table": actual_game},
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def add_sign(button, row, col):
    """Place the local player's sign on the board."""

    global current_player

    # Prevent moves when it is not the local player's turn
    if current_player != my_player:
        print("It's not your turn.")
        return

    # Prevent a player from clicking an occupied cell
    if game_table[row][col] is not None:
        print("This cell is already occupied.")
        return

    # Select the sign and its color
    sign = "X" if my_player == 1 else "O"
    color_sign = "red" if my_player == 1 else "blue"

    # Update the local board and button
    game_table[row][col] = sign
    button.configure(text=sign, fg_color=color_sign)

    try:
        # Send the updated board to the server
        result = post_game(game_table, session_id)
        print(f"Server board response: {result}")

    except requests.RequestException as error:
        # Report an error when sending the board
        print(f"Failed to update the server board: {error}")

    # Switch to the other player's turn
    current_player = player2 if current_player == player1 else player1
    turn_label.configure(text=f"Player {current_player}'s turn")


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


# Start the application's event loop
app.mainloop()
