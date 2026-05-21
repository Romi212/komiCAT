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

        self.text_areas = []
        self.dragging = None
        self.drag_start = None
        self.segment_height = 220
        
    def set_adapter(self, adapter):
        self.adapter = adapter
    
    def _start_drag(self, event, segment):
        self.dragging = segment
        self.drag_start = event.y_root
        self.canvas.config(cursor="hand2")

    def _drag(self, event, segment):
        if self.dragging == segment and self.drag_start is not None:
            dy = event.y_root - self.drag_start
            
            # Find the canvas item and move it only on y-axis
            for item_id in self.canvas.find_all():
                if self.canvas.itemcget(item_id, "window") == str(segment):
                    coords = self.canvas.coords(item_id)
                    self.canvas.coords(item_id, coords[0], coords[1] + dy)
                    break
            
            self.drag_start = event.y_root

    def _end_drag(self, event):
        if self.dragging:
            self.canvas.config(cursor="arrow")
            # Reorder segments based on their y positions
            self._reorder_segments()
            self.dragging = None
            self.drag_start = None
    
    def _reorder_segments(self):
        # Get all segments with their current y positions
        segment_positions = []
        for segment in self.text_areas:
            for item_id in self.canvas.find_all():
                if self.canvas.itemcget(item_id, "window") == str(segment):
                    coords = self.canvas.coords(item_id)
                    segment_positions.append((segment, coords[1]))
                    break
        
        # Sort by y position
        segment_positions.sort(key=lambda x: x[1])
        self.text_areas = [s[0] for s in segment_positions]
        
        # Reposition all segments in order at fixed x=10
        for i, segment in enumerate(self.text_areas):
            for item_id in self.canvas.find_all():
                if self.canvas.itemcget(item_id, "window") == str(segment):
                    self.canvas.coords(item_id, 10, i * self.segment_height)
                    break
    
    def _on_canvas_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_segment(self, japanese_text=""):
        segment = SegmentBox(self.canvas, japanese_text)
        
        # Bind drag events to the label
        segment.label.bind("<Button-1>", lambda e, s=segment: self._start_drag(e, s))
        segment.label.bind("<B1-Motion>", lambda e, s=segment: self._drag(e, s))
        segment.label.bind("<ButtonRelease-1>", self._end_drag)
        
        self.text_areas.append(segment)
        self.canvas.create_window(10, len(self.text_areas)*self.segment_height, anchor=tk.NW, window=segment)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        return segment
    
    def load_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if self.text_areas:
                self.text_areas[0].set_translation(content)
