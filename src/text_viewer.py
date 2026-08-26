from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from aux_types.segment_box import SegmentBox
from spell_checker import SpellChecker


class TextViewer(QWidget):
    def __init__(self, controller= None, parent=None, chapter=None):
        super().__init__(parent)
        self.chapter = chapter
        self.segment_boxes = []
        self.current_segment_index = 0
        self.dragging = None
        self.drag_start = None
        self.controller = controller
        
        self.text_size = 12  # Default text size
        
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
            aux = segment
            segment_box = self.create_segment(segment)
            segment.set_segment_box(segment_box)
            if(aux.get_child()):
                # Create a container widget for combined segments
                container = QWidget()
                container.setObjectName("combinedSegmentContainer")
                container.setStyleSheet("#combinedSegmentContainer { border: 2px solid #6e2130; border-radius: 5px; }")
                layout = QVBoxLayout()
                layout.setContentsMargins(8, 8, 8, 8)
                layout.setSpacing(5)
                layout.addWidget(segment_box)
                while (aux.get_child()):
                    aux = aux.get_child()
                    segment_box = self.create_segment(aux)
                    aux.set_segment_box(segment_box)
                    layout.addWidget(segment_box)
                container.setLayout(layout)
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, container)
            else:
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, segment_box)
         # Insert before the stretch (at second-to-last position)
        
    
    def create_segment(self, logic_segment):
        segment = SegmentBox(logic_segment, self.text_size)
        
        self.segment_boxes.append(segment)
        # Install event filter to intercept Tab key presses
        segment.installEventFilter(self)
        
       
        return segment
    

    def load_chapter(self, chapter):
        self.chapter = chapter
        self.spell_checker = SpellChecker(language=chapter.language)  # Initialize the spell checker for Spanish
        
        for page in chapter.pages:
            to_show= []
            for segment in page.segments:
                if segment.source_text:  
                    to_show.append(segment)
            self.create_segment_boxes(to_show)

    def zoom_in(self):
        print("Zooming in")
        self.text_size += 2
        for segment in self.segment_boxes:

            segment.zoom(self.text_size)  
    
    def zoom_out(self):
        self.text_size = max(2, self.text_size - 2)  
        for segment in self.segment_boxes:
            segment.zoom(self.text_size)  # Zoom out by adjusting the text size

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
        if next_segment.segment.page != self.chapter.current_page:
            self.controller.set_current_page(next_segment.segment.page)  # Switch to the page of the next segment
        
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

        if prev_segment.segment.page != self.chapter.current_page:
            self.controller.set_current_page(prev_segment.segment.page)  # Switch to the page of the previous segment
        
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