from PyQt6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from text_area_widgets.combined_container import CombinedContainer
from text_area_widgets.page_container import PageContainer
from text_area_widgets.segment_box import SegmentBox
from CATtools.jp_dictionaries import JPDictionary
from CATtools.spell_checker import SpellChecker


class TextViewer(QWidget):
    def __init__(self, controller= None, parent=None, chapter=None):
        super().__init__(parent)
        self.chapter = chapter
        self.segment_boxes = []
        self.current_segment_index = 0
        self.dragging = None
        self.drag_start = None
        self.controller = controller
        self.page_containers = []
        self.current_panel = None
        self.text_size = 14  # Default text size
        
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

    def add_extracted_segments(self,page, segments):
        if len(self.page_containers) < len(self.chapter.pages):
            self._update_page_containers()
        page_container = self.page_containers[page.number]
        self.create_segment_boxes(segments, page_container)
        self.update_tab_order(page)

    #Called from ProjectWindow when the user clicks the "Extract" button, passing the list of segments with the source text gud
    def create_segment_boxes(self, segments, page_container):
        for segment in segments.heads:
            if segment.source_text: 
                aux = segment
                segment_box = self.create_segment(segment)
                segment.set_segment_box(segment_box)
                
                if(aux.get_child()):
                    # Create a container widget for combined segments
                    container = CombinedContainer(segment_box)
                    
                    head_segment = segment_box
                    while (aux.get_child()):
                        aux = aux.get_child()
                        segment_box = self.create_segment(aux)
                        aux.set_segment_box(segment_box)
                        container.addChild(segment_box)
                    
                    page_container.addCombinedSegment(container,head_segment)
                else:
                    page_container.addSegment(segment_box)
            # Insert before the stretch (at second-to-last position)
        
        

    def update_tab_order(self,page):
        previous = page.get_previous_page_last_segment()
        for segment in page.segments:
            if previous and segment.segment_box:
                segment.segment_box.set_prev_focus(previous)
            previous = segment

    def create_segment(self, logic_segment):
        segment = SegmentBox(self.spell_checker, self.jp_dict,logic_segment, self.text_size)
        
        self.segment_boxes.append(segment)
        # Install event filter to intercept Tab key presses
        segment.installEventFilter(self)

        segment.check_spelling()
        segment.focused.connect(self.focus_next_segment)
        return segment
    
   
    def load_chapter(self, chapter):
        self.chapter = chapter
        self.spell_checker = SpellChecker(language=chapter.language, termbase=self.chapter.get_termbase())  # Initialize the spell checker for Spanish
        self.jp_dict = JPDictionary()
        
        for page in chapter.pages:
            page_container = self._create_page_container(page)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, page_container)
            self.page_containers.append(page_container)
            
            self.create_segment_boxes(page.segments, page_container)
            self.update_tab_order(page)
            

    def zoom_in(self):
        print("Zooming in")
        self.text_size += 2
        for segment in self.segment_boxes:

            segment.zoom(self.text_size)  
    
    def zoom_out(self):
        self.text_size = max(2, self.text_size - 2)  
        for segment in self.segment_boxes:
            segment.zoom(self.text_size)  # Zoom out by adjusting the text size

    def focus_next_segment(self, next_segment):
                
        if next_segment.page != self.chapter.current_page:
            self.controller.set_current_page(next_segment.page)  # Switch to the page of the next segment
        
        if next_segment.panel != self.current_panel:
            self.current_panel = next_segment.panel
            self.controller.set_panel_zoom(next_segment.panel)
        


    def _create_page_container(self,page = None):
        if not page:
            page = self.chapter.get_current_page()
        page_container = PageContainer(page=page, parent=self)
        self.controller.edit_mode_changed.connect(page_container.set_edit_mode)
        return page_container

    def _update_page_containers(self):
        index = len(self.page_containers)
        for page in self.chapter.pages[index:]:
            page_container = self._create_page_container(page = page)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, page_container)
            self.page_containers.append(page_container)

    def delete_segment(self, segment):
        segment_box = segment.segment_box
        if(False):
            container = self.page_containers[segment.page.number]
            container.remove_segment(segment_box)