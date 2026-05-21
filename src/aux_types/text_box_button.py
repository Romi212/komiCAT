
from tkinter import filedialog, ttk


class TextBoxButton(ttk.Button):
    def __init__(self, text_box, onClick):
        super().__init__( command=onClick)
        self.text_box = text_box
        self.text = ""

    def selected(self, number):
        print(number)
        self.text = f"{number}"
        self.config(text=f"{number}")



    
