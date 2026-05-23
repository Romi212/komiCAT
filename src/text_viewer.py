from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from aux_types.segment_box import SegmentBox


class TextViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_areas = []
        self.dragging = None
        self.drag_start = None
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Container for segments
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_container.setLayout(self.scroll_layout)
        
        self.scroll_area.setWidget(self.scroll_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def set_adapter(self, adapter):
        self.adapter = adapter
    
    def create_segment(self, japanese_text=""):
        segment = SegmentBox(japanese_text)
        self.text_areas.append(segment)
        self.scroll_layout.addWidget(segment)
        return segment
    
    def load_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if self.text_areas:
                self.text_areas[0].set_translation(content)
