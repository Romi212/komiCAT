#Small window with 3 buttons to load or create proyect 
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QPushButton,  QSplitter, QVBoxLayout, QWidget, QMenuBar
from data_structure.segment_combined import SegmentCombined
from ui.windows.project.create_project_window import CreateProjectWindow
from storage.process.background_worker import BackgroundWorker
from storage.project_loader import ProjectLoader
from ui.windows.chapter.chapter_window import ChapterWindow
from CATtools.text_extractor import TextExtractor
from PyQt6.QtCore import QThreadPool

from ui.controllers.project_manager import ProjectManager
from ui.controllers.config_controller import ConfigController
from ui.windows.project.project_window import ProjectWindow


class LauncherWindow(QMainWindow):
    def __init__(self, storage = None):
        super().__init__()
        self.storage = storage
        self.config_controller = ConfigController(storage=self.storage, parent=self)
        self.config_window = None
        self.project_loader = ProjectLoader(storage)
        self.thread_pool = QThreadPool.globalInstance()
        self.text_extractor = None  
        self.pending_chapter = None 

        self.setWindowTitle("Launcher")
        self.resize(400, 200)
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("App")
        #Save project button
        create_action = file_menu.addAction("Preferences")
        create_action.triggered.connect(self.open_preferences)
        layout = QVBoxLayout()

        self.status_label = QLabel("")
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.status_label)
        
        self.create_project_button = QPushButton("Create New Project")
        self.create_project_button.clicked.connect(self.create_new_project)
        layout.addWidget(self.create_project_button)

        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        layout.addWidget(self.load_project_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.show()
        self.preload_models()  # Start loading models in the background


    def preload_models(self):
        self.status_label.setText("Loading AI models in background...")
        
        # Instantiate TextExtractor inside the worker thread execution
        worker = BackgroundWorker(TextExtractor)
        worker.signals.finished.connect(self._on_models_loaded)
        worker.signals.error.connect(self._on_models_error)

        self.thread_pool.start(worker)

    def _on_models_loaded(self, text_extractor):
        self.text_extractor = text_extractor
        self.status_label.setText("AI models loaded successfully.")
        if self.pending_chapter is not None:
            self.open_project_window()

    def _on_models_error(self, error):
        self.status_label.setText(f"Error loading AI models: {error}")
        print(f"Error loading AI models: {error}")

    def create_new_project(self):
        self.pending_chapter = self.project_loader.create_new_project()
        self.open_project_window()

    def load_project(self):
        self.pending_chapter = self.project_loader.load_project()
        self.open_project_window()

    def open_project_window(self):
        if self.text_extractor is None:
            self.set_buttons_enabled(False)
            self.status_label.setText("AI models are still loading. Please wait...")   
        else:
            if self.pending_chapter is not None:
                self.project_manager = ProjectManager(self.pending_chapter,self.project_loader, self.text_extractor)
                self.close()

    def set_buttons_enabled(self, enabled: bool):
        self.create_project_button.setEnabled(enabled)
        self.load_project_button.setEnabled(enabled)

    def open_preferences(self):
        self.config_window = self.config_controller.open(self)
        