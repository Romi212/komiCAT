from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from ui.windows.project.widgets.image_card import ImageCard      # adjust to where ImageCard lives

CARD_COVER = (110, 155)

class PeekPanel(QWidget):
    """A bordered panel with a character peeking over its top edge."""

    def __init__(self, image_path, title="Recent Projects", image_height=90,
                 paw_overlap=10, right_margin=24, parent=None):
        super().__init__(parent)

        self.right_margin = right_margin

        pix = QPixmap(str(image_path))
        has_image = not pix.isNull()

        # the layout leaves room above the panel for the image, minus the overlap
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, (image_height - paw_overlap) if has_image else 0, 0, 0)
        outer.setSpacing(0)

        self.panel = QFrame()
        self.panel.setObjectName("recentPanel")
        outer.addWidget(self.panel)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(16, 12, 16, 14)
        panel_layout.setSpacing(10)

        # ---- title, top left ----
        self.title_label = QLabel(title)
        self.title_label.setObjectName("recentTitle")
        panel_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # ---- cards row, centered: stretch | cards | stretch ----
        row = QHBoxLayout()
        row.addStretch(1)
        self.content = QHBoxLayout()          # the launcher puts the cards in this layout
        self.content.setSpacing(24)
        row.addLayout(self.content)
        row.addStretch(1)
        panel_layout.addLayout(row)

        # ---- character, child of this widget (not of the panel) ----
        self.peek = QLabel(self)
        self.peek.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.peek.setStyleSheet("background: transparent; border: none;")
        if has_image:
            self.peek.setPixmap(pix.scaledToHeight(
                image_height, Qt.TransformationMode.SmoothTransformation))
            self.peek.adjustSize()
        else:
            self.peek.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.peek.move(self.width() - self.peek.width() - self.right_margin, 0)
        self.peek.raise_()       

class LauncherWindow(QMainWindow):
    create_requested = pyqtSignal()
    load_requested = pyqtSignal()
    preferences_requested = pyqtSignal()
    recent_open_requested = pyqtSignal(str)       # project (.romi) path
    recent_remove_requested = pyqtSignal(str)

    def __init__(self, image_path):
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
        # ---- recent projects panel with Komi peeking ----
        self.peek_panel = PeekPanel(image_path, title="Recent Projects",
                            image_height=90, paw_overlap=5, right_margin=24)
        self.recent_layout = self.peek_panel.content        # set_recents keeps working as is
        root.addWidget(self.peek_panel)
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
        for w in (self.create_button, self.load_button, self.peek_panel.panel):
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