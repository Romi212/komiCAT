import sys
from launcher_window import LauncherWindow
from project_window import ProjectWindow
from PyQt6.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = LauncherWindow()
    sys.exit(app.exec())
    
