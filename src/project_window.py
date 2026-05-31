import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from image_viewer import ImageViewer
from text_viewer import TextViewer
from views_adapter import ViewsAdapter

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

        
        
        # Create viewers
        self.text_viewer = TextViewer()
        self.image_viewer = ImageViewer()
        
        # Add to splitter
        splitter.addWidget(self.text_viewer)
        splitter.addWidget(self.image_viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Setup adapter
        views_adapter = ViewsAdapter(self.image_viewer, self.text_viewer)
        self.image_viewer.set_adapter(views_adapter)
        
        self.show()
       


    