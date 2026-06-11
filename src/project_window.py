import sys
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QSplitter, QVBoxLayout, QWidget, QMenuBar
from PyQt6.QtCore import Qt

from create_project_window import CreateProjectWindow
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
        create_action = file_menu.addAction("New Project")
        create_action.triggered.connect(self.create_new_project)

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
        
        
        self.chapter = None


       

        
        # Create viewers
        self.text_viewer = TextViewer(controller=self, chapter=self.chapter)
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
        base_index = self.chapter.get_current_page().extracted_bubbles
        for bubble_button in extracted_bubbles:
            
            segment = bubble_button.segment
            segment.nro = base_index + int(bubble_button.text)
            segment.text_extracted(bubble_button.text_box.text)
            segments.append(segment)
            bubble_button.has_been_extracted()
        self.text_viewer.create_segment_boxes(segments)
        self.chapter.get_current_page().extracted_bubbles += len(extracted_bubbles)


    def save_project(self):
        self.project_loader.save_project()
        self.image_viewer.status_label.setText("Project saved successfully! in " + self.project_loader.save_path)   

    def load_project(self):
        load_path = QFileDialog.getOpenFileName()
        self.chapter = self.project_loader.load_project(load_path[0])

        self.image_viewer.load_chapter(self.chapter)
        self.text_viewer.load_chapter(self.chapter)

    def export_translation(self):
        export_path = QFileDialog.getSaveFileName()
        self.project_loader.export_translation(export_path[0])

    def create_new_project(self):
        self.create_project_window = CreateProjectWindow()
        data = self.create_project_window.exec()
        if data == QDialog.DialogCode.Accepted:
            project_data = self.create_project_window.get_project_data()
            self.chapter = self.project_loader.create_project(project_data)
            self.image_viewer.chapter = self.chapter
            self.text_viewer.chapter = self.chapter

    def set_current_page(self, page):
        self.chapter.set_current_page(page)
        self.image_viewer._setup_page()