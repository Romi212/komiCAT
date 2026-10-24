import time
from pathlib import Path

from PyQt6.QtCore import QObject, QThreadPool

from CATtools.text_extractor import TextExtractor
from storage.process.background_worker import BackgroundWorker
from storage.project_loader import ProjectLoader
from ui.controllers.config_controller import ConfigController
from ui.controllers.project_manager import ProjectManager
from data_structure.app_config import config


class LauncherController(QObject):
    MAX_STORED = 10      # kept in config.json
    MAX_SHOWN = 3        # cards in the launcher

    def __init__(self, window, storage):
        super().__init__(window)
        self.window = window
        self.storage = storage
        self.config = config
        self.loader = ProjectLoader(storage)
        self.prefs = ConfigController(storage=storage, parent=self)
        self.thread_pool = QThreadPool.globalInstance()

        self.text_extractor = None
        self.pending_project = None
        self.project_manager = None

        window.create_requested.connect(self.create_project)
        window.load_requested.connect(self.load_project)
        window.preferences_requested.connect(lambda: self.prefs.open(self.window))
        window.recent_open_requested.connect(self.open_recent)
        window.recent_remove_requested.connect(self.remove_recent)

        self.refresh_recents()
        self.preload_models()

    # ---------- models ----------
    def preload_models(self):
        self.window.set_status("Loading AI models in background...")
        worker = BackgroundWorker(TextExtractor)
        worker.signals.finished.connect(self._on_models_loaded)
        worker.signals.error.connect(self._on_models_error)
        self.thread_pool.start(worker)

    def _on_models_loaded(self, text_extractor):
        self.text_extractor = text_extractor
        self.window.set_status("AI models loaded successfully.")
        if self.pending_project is not None:
            self._open_pending()
        else:
            self.window.set_busy(False)

    def _on_models_error(self, error):
        self.window.set_status(f"Error loading AI models: {error}")
        print(f"Error loading AI models: {error}")

    # ---------- create / load ----------
    def create_project(self):
        try:
            project = self.loader.create_new_project()
        except Exception as e:                      # e.g. FileExistsError
            self.window.show_error("Could not create project", str(e))
            return
        self._start(project)

    def load_project(self):
        try:
            project = self.loader.load_project()
        except Exception as e:
            self.window.show_error("Could not open project", str(e))
            return
        self._start(project)

    def open_recent(self, path):
        if not Path(path).exists():
            self.window.show_warning("Project not found",
                                     f"This project no longer exists:\n{path}")
            self.remove_recent(path)
            return
        try:
            project = self.loader.load_project(path)
        except Exception as e:
            self.window.show_error("Could not open project", str(e))
            return
        self._start(project)

    def _start(self, project):
        if project is None:                         # user cancelled a dialog
            return
        manifest = self.storage.resolve(project.project_name+".romi")
        self.add_recent(str(manifest), project.project_name)
        self.pending_project = project
        self._open_pending()

    def _open_pending(self):
        if self.text_extractor is None:
            self.window.set_busy(True)
            self.window.set_status("AI models are still loading. Please wait...")
            return
        self.project_manager = ProjectManager(
            self.pending_project, self.loader, self.text_extractor)
        self.window.close()

    # ---------- recents (stored inside config.json) ----------
    def add_recent(self, path, name):
        entries = [e for e in self.config.recent_projects if e["path"] != path]
        entries.insert(0, {"path": path, "name": name, "last_opened": time.time()})
        self.config.recent_projects = entries[:self.MAX_STORED]
        self._save_config()
        

    def remove_recent(self, path):
        self.config.recent_projects = [
            e for e in self.config.recent_projects if e["path"] != path]
        self._save_config()
        self.refresh_recents()

    def refresh_recents(self):
        valid = [e for e in self.config.recent_projects if Path(e["path"]).exists()]
        if len(valid) != len(self.config.recent_projects):   # drop moved/deleted ones
            self.config.recent_projects = valid
            self._save_config()

        shown = []
        for e in valid[:self.MAX_SHOWN]:
            root = Path(e["path"]).parent
            self.storage.set_project_root(root)
            shown.append({"path": e["path"], "name": e["name"],
                          "cover": self.storage.get_cover_image_path()})
        self.window.set_recents(shown)

    def _save_config(self):
        print(self.config.recent_projects)
        self.storage.save_config_data(self.config.get_data())