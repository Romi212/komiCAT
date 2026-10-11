import sys
from launcher_window import LauncherWindow
from project_window import ProjectWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QApplication
from ui import theme
import sys, traceback, datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox

LOG_FILE = Path.home() / "komicat_error.log"

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

sys.excepthook = handle_exception
app = QApplication(sys.argv)


def apply_theme(t):
    app.setStyleSheet(theme.build_qss(t))

def main():
    apply_theme(theme.current())                              # apply at startup
    theme.theme_manager.theme_changed.connect(apply_theme)
    launcher = LauncherWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
