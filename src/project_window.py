import sys
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QSplitter, QVBoxLayout, QWidget, QMenuBar
from PyQt6.QtCore import Qt, pyqtSignal

from data_structure.page import Page
from data_structure.segment_combined import SegmentCombined
from create_project_window import CreateProjectWindow
from image_viewer import ImageViewer
from project_loader import ProjectLoader
from text_viewer import TextViewer
from data_structure.chapter import Chapter
from tool_windows.termbase_panel import TermbasePanel

class ProjectWindow(QMainWindow):
    edit_mode_changed = pyqtSignal(Page, bool)
    def __init__(self, text_extractor=None, chapter=None, project_loader=None):
        super().__init__()
        
        self.text_extractor = text_extractor;
        self.project_loader = project_loader;
        
        
        # Create main window
        
        self.setWindowTitle("KomiCAT")
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

        project_menu = self.menu_bar.addMenu("Project")
        

        export_action = project_menu.addAction("Export Translation")
        export_action.triggered.connect(self.export_translation)

        termbase_action = project_menu.addAction("Termbase")
        termbase_action.triggered.connect(self.show_termbase)

        

        # Create central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
       

        
        # Create viewers
        self.text_viewer = TextViewer(controller=self, chapter=chapter)
        self.image_viewer = ImageViewer(controller=self, chapter=chapter, text_extractor=self.text_extractor)
        
        self.set_up_chapter(chapter)

        open_images = project_menu.addAction("Open Images")
        open_images.triggered.connect(self.image_viewer.open_images)
        
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
       

    def set_up_chapter(self, chapter):
        self.chapter = chapter
        self.termbase = self.chapter.get_termbase()
        self.termbase_panel = TermbasePanel(self.termbase, self)
        self.image_viewer.load_chapter(self.chapter)
        self.text_viewer.load_chapter(self.chapter)

    def extracted(self, page, segments):
        self.text_viewer.add_extracted_segments(page,segments)


    def save_project(self):
        self.project_loader.save_project()
        self.image_viewer.status_label.setText("Project saved successfully! in " + self.project_loader.save_path)   

    def load_project(self):

        chapter = self.project_loader.load_project()
        if(chapter):
            self.set_up_chapter(chapter)
        #TODO ELSE TIRAR ERROR CANT OPEN PROJECT

    def export_translation(self):
        export_path = QFileDialog.getSaveFileName()
        self.project_loader.export_translation(export_path[0])

    def show_termbase(self):
        self.termbase_panel.show()
        self.termbase_panel.raise_()
        self.termbase_panel.activateWindow()

    def create_new_project(self):
        
        chapter = self.project_loader.create_new_project()
        if(chapter):
            self.set_up_chapter(chapter)
        #TODO: ELSE mostrar error creando nuevo

    def set_current_page(self, page):
        self.chapter.set_current_page(page)
        self.image_viewer._setup_page()

    def set_panel_zoom(self,panel):
        self.image_viewer.set_panel_zoom(panel)

    def delete_segment(self, segment):
        self.text_viewer.delete_segment(segment)

    def change_edit_mode(self, page, can_edit):
            page.set_edit_mode(can_edit)
            self.edit_mode_changed.emit(page, can_edit)
            if not can_edit:
                self.text_viewer.update_tab_order(page)