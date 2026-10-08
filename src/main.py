import sys
from launcher_window import LauncherWindow
from project_window import ProjectWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QApplication
from ui import theme

app = QApplication(sys.argv)

def apply_theme(t):
    app.setStyleSheet(theme.build_qss(t))


if __name__ == "__main__":
    #app = QApplication(sys.argv)
    apply_theme(theme.current())                              # apply at startup
    theme.theme_manager.theme_changed.connect(apply_theme)
    launcher = LauncherWindow()
    sys.exit(app.exec())
    
