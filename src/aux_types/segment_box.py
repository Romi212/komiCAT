import tkinter as tk
from tkinter import ttk

class SegmentBox(ttk.Frame):
    def __init__(self, parent, japanese_text=""):
        super().__init__(parent, relief=tk.SUNKEN, borderwidth=2)
        
        # Label with Japanese text
        self.label = ttk.Label(self, text=japanese_text, font=('Arial', 10, 'bold'), wraplength=300)
        self.label.pack(fill=tk.X, padx=5, pady=5)
        
        # Text area for translation
        self.text_area = tk.Text(self, height=4, width=40, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def set_japanese_text(self, text):
        self.label.config(text=text)
    
    def get_translation(self):
        return self.text_area.get(1.0, tk.END).strip()
    
    def set_translation(self, text):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)