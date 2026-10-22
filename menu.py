
from customtkinter import *
import requests
import json
import sys
import subprocess

# Load the configuration containing the server address
with open("server.json", "r", encoding="utf-8") as file:
    config = json.load(file)

server = config["server"].rstrip("/")


# Create the main menu window
menu = CTk()
menu.title("CMor - Menu")
menu.geometry("300x400")
menu.resizable(False, False)


# Display the game title
CTkLabel(
    menu,
    text="CMor",
    font=("Arial", 30, "bold")
).pack(pady=10)


def join_a_game():
    """Open a window to join an existing game."""

    # Create a secondary window
    join_game = CTkToplevel(menu)
    join_game.title("CMor - Join a game")
    join_game.geometry("300x180")
    join_game.resizable(False, False)

    # Ask the player to enter the game ID
    CTkLabel(
        join_game,
        text="Game ID:"
    ).pack(pady=(20, 5))

    game_id_entry = CTkEntry(
        join_game,
        placeholder_text="Enter the game ID"
    )
    game_id_entry.pack(padx=20, pady=5, fill="x")

    def close_and_start():
        """Launch the game using the entered game ID."""

        # Retrieve and validate the entered game ID
        game_id = game_id_entry.get().strip()

        if not game_id:
            CTkLabel(
                join_game,
                text="Please enter a game ID.",
                text_color="red"
            ).pack(pady=5)
            return

        # Launch the game and pass the game ID as an argument
        subprocess.Popen(
            [sys.executable, "main.py", game_id]
        )

        # Close the join window after launching the game
        join_game.destroy()
        menu.destroy()

    # Add the button used to join the game
    CTkButton(
        join_game,
        text="Join game",
        command=close_and_start
    ).pack(pady=15)


def start_new_game():
    subprocess.Popen(
                [sys.executable, "main.py"]
            )
    menu.destroy()


# Create the button used to start a new game
start_button = CTkButton(
    menu,
    text="Start a new game",
    width=150,
    height=80,
    corner_radius=10,
    command=start_new_game
)

# Create the button used to join an existing game
join_button = CTkButton(
    menu,
    text="Join a game",
    width=150,
    height=80,
    corner_radius=10,
    command=join_a_game
)

# Position the buttons in the main menu
start_button.pack(padx=20, pady=20)
join_button.pack(padx=20, pady=20)


# Start the main application event loop
menu.mainloop()
