import ctypes
import sys

from data_structure.app_config import AppConfig
from ui.windows.launcher_window import LauncherWindow
from ui.windows.chapter.chapter_window import ChapterWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QApplication
from ui import theme
from data_structure import app_config
import sys, traceback, datetime
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThreadPool, QEventLoop
from PyQt6.QtWidgets import QProgressDialog, QMessageBox
import first_run
from storage.project_storage import ProjectStorage
from storage.resources import get_image_path, IMG_ICON, IMG_PEEK
from storage.process.background_worker import BackgroundWorker   # wherever your class lives
from ui.controllers.launcher_controller import LauncherController

LOG_FILE = Path.home() / "komicat_error.log"

def run_setup(app):
    
    if not first_run.needs_setup():
        return True

    dlg = QProgressDialog("Preparing KomiCAT (first run, needs internet)...", None, 0, 0)
    dlg.setWindowTitle("KomiCAT setup")
    dlg.setCancelButton(None)
    dlg.setMinimumDuration(0)
    dlg.show()

    def do_setup():
        first_run.download_models()
        first_run.download_jamdict()
        first_run.download_dictionaries()

    result = {"ok": True, "error": ""}
    loop = QEventLoop()

    worker = BackgroundWorker(do_setup)

    def on_error(msg):
        result["ok"] = False
        result["error"] = msg
        loop.quit()

    worker.signals.finished.connect(lambda _: loop.quit())
    worker.signals.error.connect(on_error)

    QThreadPool.globalInstance().start(worker)
    loop.exec()          # keeps the UI responsive until a signal fires
    dlg.close()

    if not result["ok"]:
        QMessageBox.critical(None, "Setup failed",
            f"Could not download the required files:\n{result['error']}\n\n"
            "Check your connection and restart.")
    return result["ok"]

def handle_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    # 1. always write to a log file, so nothing is lost
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n{text}")
    except OSError:
        pass

    # 2. show it on screen (only if the app exists)
    if QApplication.instance():
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("KomiCAT - unexpected error")
        box.setText("Something went wrong. Please send me the log file:\n" + str(LOG_FILE))
        box.setDetailedText(text)          # expandable "Show Details" with the traceback
        box.exec()

#sys.excepthook = handle_exception
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Romi.KomiCAT")
except Exception:
    pass
app = QApplication(sys.argv)

if not run_setup(app):
    sys.exit(1)

def apply_theme(t):
    app.setStyleSheet(theme.build_qss(t))

def main():
    first_run.load_config(app_config.config)
    storage = ProjectStorage()
    app.setWindowIcon(QIcon(str(get_image_path(IMG_ICON))))
    app_config.config.load_data(storage.get_config_data())
    theme.theme_manager.set_theme(app_config.config.theme)
    apply_theme(theme.current())                              # apply at startup
    theme.theme_manager.theme_changed.connect(apply_theme)
    launcher_window = LauncherWindow(get_image_path(IMG_PEEK))
    launcher = LauncherController(launcher_window, storage)   # keep a reference
    launcher_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
