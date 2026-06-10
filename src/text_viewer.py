from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from aux_types.segment_box import SegmentBox


class TextViewer(QWidget):
    def __init__(self, parent=None, chapter=None):
        super().__init__(parent)
        self.chapter = chapter
        self.segment_boxes = []
        self.current_segment_index = 0
        self.dragging = None
        self.drag_start = None
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container for segments
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.addStretch()  # Push segments to the top
        self.scroll_container.setLayout(self.scroll_layout)
        
        # Set size policy so it doesn't expand to fill scroll area
        self.scroll_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.scroll_area.setWidget(self.scroll_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)

        button_layout = QHBoxLayout()
        
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        button_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        button_layout.addWidget(self.zoom_out_button)
        
        layout.addLayout(button_layout)
                
    #Called from ProjectWindow when the user clicks the "Extract" button, passing the list of segments with the source text gud
    def create_segment_boxes(self, segments):
        for segment in segments:
            segment_box = self.create_segment(segment)
            segment.set_segment_box(segment_box)
    
    def create_segment(self, logic_segment):
        segment = SegmentBox(logic_segment)
        
        self.segment_boxes.append(segment)
        # Install event filter to intercept Tab key presses
        segment.installEventFilter(self)
        
        # Insert before the stretch (at second-to-last position)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, segment)
        return segment
    

    def load_chapter(self, chapter):
        self.chapter = chapter
        for page in chapter.pages:
            for segment in page.segments:
                if segment.source_text:  
                    segment_box = self.create_segment(segment)
                    segment.set_segment_box(segment_box)

    def zoom_in(self):
        print("Zooming in")
        for segment in self.segment_boxes:

            segment.zoom(1.2)  # Zoom in by 20%
    
    def zoom_out(self):
        for segment in self.segment_boxes:
            segment.zoom(0.8)  # Zoom out by 20%

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.focus_next_segment()
            event.accept()
        elif event.key() == Qt.Key.Key_Backtab:  # Shift+Tab
            self.focus_previous_segment()
            event.accept()
        else:
            super().keyPressEvent(event)

    def focus_next_segment(self):
        if not self.segment_boxes:
            return
        
        # Find currently focused segment box
        current_index = self.current_segment_index
        next_index = (current_index + 1) % len(self.segment_boxes)
        
        self.current_segment_index = next_index
        next_segment = self.segment_boxes[next_index]
        next_segment.text_area.setFocus()
        
        # Scroll to make it visible
        self.scroll_area.ensureWidgetVisible(next_segment)

    def focus_previous_segment(self):
        if not self.segment_boxes:
            return
        
        # Find currently focused segment box
        current_index = self.current_segment_index
        prev_index = (current_index - 1) % len(self.segment_boxes)
        
        self.current_segment_index = prev_index
        prev_segment = self.segment_boxes[prev_index]
        prev_segment.text_area.setFocus()
        
        # Scroll to make it visible
        self.scroll_area.ensureWidgetVisible(prev_segment)

    def eventFilter(self, obj, event):
        """Handle Tab key presses from segment boxes"""
        if event.type() == 6:  # QEvent.KeyPress
            if event.key() == Qt.Key.Key_Tab:
                # Find which segment box this came from
                for i, segment in enumerate(self.segment_boxes):
                    if segment.isAncestorOf(obj) or segment == obj:
                        self.current_segment_index = i
                        self.focus_next_segment()
                        return True
            elif event.key() == Qt.Key.Key_Backtab:  # Shift+Tab
                for i, segment in enumerate(self.segment_boxes):
                    if segment.isAncestorOf(obj) or segment == obj:
                        self.current_segment_index = i
                        self.focus_previous_segment()
                        return True
        return super().eventFilter(obj, event)