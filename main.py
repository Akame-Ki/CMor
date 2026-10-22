from customtkinter import *
from random import choice
import requests

# Load Window
app = CTk()
app.title("CMor")
app.geometry("300x300")

# Server address
server = "http://192.168.1.250:8000"

game_table = [[None for _ in range(3)] for _ in range(3)]
# Setup buttons table
buttons = [[None for _ in range(3)] for _ in range(3)]


# Load player ID
player1 = choice([1, 2])
player2 = 2 if player1 == 1 else 1
current_player = player1  # Player 1 starts

# post the actual game table
def post_game(actual_game):
    global server
    response = requests.post(
    f"{server}/table",
    json={"table": actual_game}
    )
    return response.json()



# Add sign to the button and to the game table
def add_sign(button, lines, rows):
    global current_player
    #if current_player == player2:
            #print("It's not your turn")
            #return
    if button.cget("fg_color") != "white":
        print("Button already clicked")
        return
    

    sign = "X" if current_player == player1 else "O"
    color_sign = "red" if current_player == player1 else "blue"
    # reload game table with the sign
    game_table[lines][rows] = sign
    button.configure(text=sign, fg_color=color_sign)
    print(f"actual game table on the server : {post_game(game_table)}")

    print(game_table)

    current_player = player2 if current_player == player1 else player1


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

        button.place(x=10 + rows * 90, y=10 + lines * 90)
        
# Run the application
app.mainloop()