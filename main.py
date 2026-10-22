from customtkinter import *

app = CTk()
app.title("Morpion")
app.geometry("300x300")


def add_sign(button_id):
    print(f"Bouton {button_id} cliqué")
    



    

for lines in range(3):
    for rows in range(3):
        index = rows + lines * 3

        button = CTkButton(
            app,
            text="",
            width=80,
            height=80,
            command=lambda n=index: add_sign(n)
        )
        button.place(x=10 + rows * 90, y=10 + lines * 90)



app.mainloop()
