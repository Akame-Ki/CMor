from customtkinter import *
from random import choice
import requests
import json

# Load Window
app = CTk()
app.title("CMor")
app.geometry("300x300")

# Server address
with open("server.json", "r") as file:
    server = json.load(file)
file.close
server = server["server"]

game_table = [[None for _ in range(3)] for _ in range(3)]
# Setup buttons table
buttons = [[None for _ in range(3)] for _ in range(3)]


# Load player ID
player1 = choice([1, 2])
player2 = 2 if player1 == 1 else 1
host_player = player1  # Player 1 starts
response = requests.post(
    f"{server}/game/start",
    json={"player_id": host_player}
    )
response = response.json()
session_id = response["session_id"]

# Request the session_id and send the host player id 
response = requests.post(
    f"{server}/game/{session_id}/join",json={"player_id": host_player}
)

response = response.json()
print(response)


# post the actual game table
def post_game(actual_game,session_id):
    global server
    response = requests.post(
    f"{server}/game/{session_id}/board",
    json={"table": actual_game}
    )
    return response.json()



# Add sign to the button and to the game table
def add_sign(button, lines, rows):
    global host_player,host_player_sign
    if host_player == player2:
            print("It's not your turn")
            return
    if button.cget("fg_color") != "white":
        print("Button already clicked")
        return
    

    sign = "X" if host_player == player1 else "O"
    color_sign = "red" if host_player == player1 else "blue"
    # reload game table with the sign
    game_table[lines][rows] = sign
    button.configure(text=sign, fg_color=color_sign)
    print(f"actual game table on the server : {post_game(game_table,session_id)}")

    host_player = player2 if host_player == player1 else player1


session_info = CTkLabel(app,text=f"Code de la session : [{session_id}] Joueur {host_player}").pack()
session_info = CTkLabel(app,text=f"Tour de {"joueur actuel"}").pack()

# Create buttons
for lines in range(3):
    for rows in range(3):

        button = CTkButton(
            app,
            text="",
            width=80,
            height=80,
            fg_color="white",
        )
        buttons[lines][rows] = button
        button.configure(command=lambda b=button, l=lines, r=rows: add_sign(b, l, r))

        button.place(x=10 + rows * 90, y=70 + lines * 90)
        
# Run the application
app.mainloop()