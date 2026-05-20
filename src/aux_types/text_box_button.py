
from tkinter import filedialog, ttk


class TextBoxButton(ttk.Button):
    def __init__(self, text_box, onClick):
        super().__init__(onClick)
        self.text_box = text_box
        self.text = "";

    def selected(self, number):
        self.config(text=f"{number}")



    
