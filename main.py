
from customtkinter import *

app = CTk()
app.title("Morpion")
app.geometry("300x300")

for i in range(3):
    for j in range(3):
        bouton = CTkButton(
            app,
            text="",
            width=80,
            height=80
        )
        bouton.place(x=10 + j * 90, y=10 + i * 90)

app.mainloop()
