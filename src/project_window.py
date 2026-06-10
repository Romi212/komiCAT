import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QSplitter, QVBoxLayout, QWidget, QMenuBar
from PyQt6.QtCore import Qt

from image_viewer import ImageViewer
from project_loader import ProjectLoader
from text_viewer import TextViewer
from aux_types.chapter import Chapter

class ProjectWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        

        # Create main window
        
        self.setWindowTitle("Text and Image Viewer")
        self.resize(1600, 900)

        #Create menu bar
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("File")
        #Save project button
        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(self.save_project)

        #Load project button
        load_action = file_menu.addAction("Load Project")
        load_action.triggered.connect(self.load_project)

        load_action = file_menu.addAction("Export Translation")
        load_action.triggered.connect(self.export_translation)

        # Create central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)


        self.project_loader = ProjectLoader()
        
        self.chapter = self.project_loader.create_project()
        # Create viewers
        self.text_viewer = TextViewer(chapter=self.chapter)
        self.image_viewer = ImageViewer(controller=self, chapter=self.chapter)
        
        # Add to splitter
        splitter.addWidget(self.text_viewer)
        splitter.addWidget(self.image_viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.setMenuBar(self.menu_bar)
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


    def save_project(self):
        save_path = QFileDialog.getSaveFileName()
        self.project_loader.save_project(save_path[0])

    def load_project(self):
        load_path = QFileDialog.getOpenFileName()
        self.chapter = self.project_loader.load_project(load_path[0])

        self.image_viewer.load_chapter(self.chapter)
        self.text_viewer.load_chapter(self.chapter)

    def export_translation(self):
        export_path = QFileDialog.getSaveFileName()
        self.project_loader.export_translation(export_path[0])