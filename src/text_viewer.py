import tkinter as tk
from tkinter import ttk
from aux_types.segment_box import SegmentBox

class TextViewer:
    def __init__(self, parent):
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_canvas_scroll)

        # Create 3 draggable text areas
        self.text_areas = []
        self.dragging = None
        self.drag_start = None
        
       
    def set_adapter(self, adapter):
        self.adapter = adapter
    def _on_canvas_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_segment(self, japanese_text=""):
        segment = SegmentBox(self.canvas, japanese_text)
        self.text_areas.append(segment)
        self.canvas.create_window(10, len(self.text_areas)*110, anchor=tk.NW, window=segment)
        return segment
    
    def load_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if self.text_areas:
                self.text_areas[0].delete(1.0, tk.END)
                self.text_areas[0].insert(tk.END, content)
