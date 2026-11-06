from pathlib import Path
from storage.resources import get_image_path, IMG_PEEK, IMG_LOGO
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
    """A bordered panel with a logo on top and a character peeking over its top edge."""

    def __init__(self, image_path, logo_path=None, title="Recent Projects",
                 image_height=90, paw_overlap=10, right_margin=24,
                 logo_height=60, logo_overlap=20, peek_drop=0, parent=None):
        super().__init__(parent)

        self.right_margin = right_margin
        self.peek_drop = peek_drop      # extra px pushing Komi lower

        pix = QPixmap(str(image_path))
        has_image = not pix.isNull()
        logo_pix = QPixmap(str(logo_path)) if logo_path else QPixmap()
        has_logo = not logo_pix.isNull()

        # the strip above the frame: tall enough for the logo minus its overlap onto the panel
        logo_strip = (logo_height - logo_overlap) if has_logo else 0
        peek_strip = (image_height - paw_overlap) if has_image else 0
        self.top_margin = max(logo_strip, peek_strip)
        self.paw_overlap = paw_overlap

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, self.top_margin, 0, 0)
        outer.setSpacing(0)

        self.panel = QFrame()
        self.panel.setObjectName("recentPanel")
        outer.addWidget(self.panel)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(16, 12, 16, 14)
        panel_layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("recentTitle")
        panel_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        row = QHBoxLayout()
        row.addStretch(1)
        self.content = QHBoxLayout()
        self.content.setSpacing(24)
        row.addLayout(self.content)
        row.addStretch(1)
        panel_layout.addLayout(row)

        # ---- logo, child of this widget, aligned to the top ----
        self.logo = QLabel(self)
        self.logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.logo.setStyleSheet("background: transparent; border: none;")
        if has_logo:
            self.logo.setPixmap(logo_pix.scaledToHeight(
                logo_height, Qt.TransformationMode.SmoothTransformation))
            self.logo.adjustSize()
        else:
            self.logo.hide()

        # ---- character, child of this widget ----
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
        # logo: top aligned, horizontally centered
        self.logo.move((self.width() - self.logo.width()) // 2, 0)
        # Komi: paws land paw_overlap px inside the frame, plus an optional drop
        peek_y = self.top_margin - self.peek.height() + self.paw_overlap + self.peek_drop
        self.peek.move(self.width() - self.peek.width() - self.right_margin, peek_y)
        self.logo.raise_()
        self.peek.raise_()

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
        root.setContentsMargins(16, 20, 16, 20)
        root.setSpacing(0)

        self.prefs_button = QPushButton("⚙")
        self.prefs_button.setFixedSize(36, 36)
        self.prefs_button.setToolTip("Preferences")
        self.prefs_button.setObjectName("preferencesButton")
        self.prefs_button.clicked.connect(self.preferences_requested)

        self.peek_panel = PeekPanel(
            get_image_path(IMG_PEEK),
            logo_path=get_image_path(IMG_LOGO),
            title="Recent Projects",
            image_height=90, paw_overlap=5, right_margin=24,
            logo_height=90, logo_overlap=-20, peek_drop=0,
        )
        self.recent_layout = self.peek_panel.content
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

        self.prefs_button.setParent(central)
        self.prefs_button.move(16, 12)
        self.prefs_button.show()
        self.prefs_button.raise_()

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