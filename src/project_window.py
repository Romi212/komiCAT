import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from image_viewer import ImageViewer
from text_viewer import TextViewer
from aux_types.chapter import Chapter

class ProjectWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        

        # Create main window
        
        self.setWindowTitle("Text and Image Viewer")
        self.resize(1600, 900)
        
        # Create central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)

        
        self.chapter = Chapter("Kuro no sekai","",4)
        # Create viewers
        self.text_viewer = TextViewer(chapter=self.chapter)
        self.image_viewer = ImageViewer(controller=self, chapter=self.chapter)
        
        # Add to splitter
        splitter.addWidget(self.text_viewer)
        splitter.addWidget(self.image_viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        
        self.show()
       


    def extracted(self, extracted_bubbles):
        segments = []
        for bubble_button in extracted_bubbles:
            bubble_button.has_been_extracted()
            segment = bubble_button.segment
            segment.text_extracted(bubble_button.text_box.text)
            segments.append(segment)
        self.text_viewer.create_segment_boxes(segments)
