import tkinter as tk

class TextViewer:
    def __init__(self, parent):
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a text widget for the text area
        self.text_area = tk.Text(self.main_frame)
        self.text_area.pack(expand=True, fill=tk.BOTH)

    def load_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
