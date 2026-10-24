from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from ui.windows.project.widgets.image_card import ImageCard      # adjust to where ImageCard lives

CARD_COVER = (110, 155)


class LauncherWindow(QMainWindow):
    create_requested = pyqtSignal()
    load_requested = pyqtSignal()
    preferences_requested = pyqtSignal()
    recent_open_requested = pyqtSignal(str)       # project (.romi) path
    recent_remove_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KomiCAT")
        self.resize(560, 460)

        root = QVBoxLayout()
        root.setContentsMargins(16, 12, 16, 20)

        # ---- top row: gear | title | spacer (same width, keeps title centered) ----
        top = QHBoxLayout()
        self.prefs_button = QPushButton("⚙")
        self.prefs_button.setFixedSize(36, 36)
        self.prefs_button.setToolTip("Preferences")
        self.prefs_button.setObjectName("preferencesButton")
        self.prefs_button.clicked.connect(self.preferences_requested)

        title = QLabel("KomiCAT")
        title.setObjectName("launcherTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("launcherTitle")

        spacer = QWidget()
        spacer.setFixedSize(36, 36)

        top.addWidget(self.prefs_button)
        top.addWidget(title, 1)
        top.addWidget(spacer)
        root.addLayout(top)
        root.addStretch(1)

        # ---- recent projects row ----
        self.recent_host = QWidget()
        self.recent_layout = QHBoxLayout(self.recent_host)
        self.recent_layout.setSpacing(24)
        root.addWidget(self.recent_host, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(1)

        # ---- status ----
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status_label)

        # ---- buttons side by side ----
        buttons = QHBoxLayout()
        self.create_button = QPushButton("Create New")
        self.load_button = QPushButton("Load Project")
        self.create_button.clicked.connect(self.create_requested)
        self.load_button.clicked.connect(self.load_requested)
        buttons.addWidget(self.create_button)
        buttons.addWidget(self.load_button)
        root.addLayout(buttons)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

    # ---------- API used by the controller ----------
    def set_status(self, text):
        self.status_label.setText(text)

    def set_busy(self, busy: bool):
        for w in (self.create_button, self.load_button, self.recent_host):
            w.setEnabled(not busy)

    def set_recents(self, entries):
        """entries: list of dicts {"path": str, "name": str, "cover": Path | None}"""
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()

        if not entries:
            self.recent_layout.addWidget(QLabel("No recent projects"))
            return

        for e in entries:
            card = ImageCard("recent", e["path"], e["name"], e["cover"], CARD_COVER)
            card.open_requested.connect(lambda p: self.recent_open_requested.emit(str(p)))
            card.remove_requested.connect(lambda p: self.recent_remove_requested.emit(str(p)))
            self.recent_layout.addWidget(card)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)