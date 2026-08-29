#Small window with 3 buttons to load or create proyect 
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QPushButton,  QSplitter, QVBoxLayout, QWidget, QMenuBar
from aux_types.segment_combined import SegmentCombined
from create_project_window import CreateProjectWindow
from process.models_loader import ModelLoaderWorker
from project_loader import ProjectLoader
from project_window import ProjectWindow
from text_extractor import TextExtractor
from PyQt6.QtCore import QThreadPool


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        self.project_loader = ProjectLoader()
        self.thread_pool = QThreadPool.globalInstance()
        self.text_extractor = None  
        self.pending_chapter = None 

        self.setWindowTitle("Launcher")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.status_label = QLabel("")
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
        worker = ModelLoaderWorker(TextExtractor)
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
                self.project_window = ProjectWindow(text_extractor=self.text_extractor, chapter=self.pending_chapter, project_loader=self.project_loader)
                self.close()

    def set_buttons_enabled(self, enabled: bool):
        self.create_project_button.setEnabled(enabled)
        self.load_project_button.setEnabled(enabled)
            