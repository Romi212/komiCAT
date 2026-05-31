import sys
from project_window import ProjectWindow
from PyQt6.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    project_window = ProjectWindow()
    sys.exit(app.exec())
    
