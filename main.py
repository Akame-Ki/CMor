from customtkinter import *
from random import choice
# Load Window
app = CTk()
app.title("CMor")
app.geometry("300x300")


# Load player ID
player = choice([2, 1])
color_sign = "red" if player == 1 else "blue"
sign = "X" if player == 1 else "O"



# Add sign to the button
def add_sign(button):
    print("Bouton cliqué")
    if button.cget("fg_color") == "white":
        button.configure(text=sign, fg_color=color_sign)
    else:
        print("Button already clicked")

# Setup buttons table
buttons = [[None for _ in range(3)] for _ in range(3)]
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

        button.configure(command=lambda b=button: add_sign(b))

        button.place(x=10 + rows * 90, y=10 + lines * 90)
        buttons[lines][rows] = button
# Run the application
app.mainloop()