from pathlib import Path
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QInputDialog, QLabel, QMenu, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

CARD_SIZE = (130, 180)
def load_pixmap(path, size):
    """Scaled and center-cropped pixmap, or None if the file is missing or unreadable."""
    if not path or not Path(path).exists():
        return None
    pix = QPixmap(str(path))
    if pix.isNull():
        return None
    scaled = pix.scaled(QSize(*size), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
    x = (scaled.width() - size[0]) // 2
    y = (scaled.height() - size[1]) // 2
    return scaled.copy(x, y, size[0], size[1])


class ImageCard(QWidget):
    """Thumbnail + name. kind is "chapter" or "recent".
    Left click opens. Right click: chapter -> rename/delete, recent -> remove from list."""
    open_requested = pyqtSignal(object)
    rename_requested = pyqtSignal(object, str)   # chapter only
    delete_requested = pyqtSignal(object)        # chapter only
    remove_requested = pyqtSignal(object)        # recent only

    def __init__(self, kind, item, name, image_path, size = CARD_SIZE, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.item = item        # Chapter object for "chapter", project path for "recent"
        self.name = name

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.thumb = QPushButton()
        self.thumb.setObjectName("chapterThumb" if kind == "chapter" else "recentThumb")
        self.thumb.setFixedSize(*size)
        self.thumb.setIconSize(QSize(*size))
        self.thumb.setCursor(Qt.CursorShape.PointingHandCursor)
        pix = load_pixmap(image_path, size)
        if pix:
            self.thumb.setIcon(QIcon(pix))
        else:
            self.thumb.setText("No pages" if kind == "chapter" else "No cover")
        self.thumb.clicked.connect(lambda: self.open_requested.emit(self.item))
        layout.addWidget(self.thumb)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFixedWidth(size[0])
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        if kind == "recent":
            self.setToolTip(str(item))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if self.kind == "chapter":
            rename = menu.addAction("Rename")
            delete = menu.addAction("Delete")
            chosen = menu.exec(event.globalPos())
            if chosen == rename:
                new_name, ok = QInputDialog.getText(self, "Rename chapter", "Name:",
                                                    text=self.name)
                if ok and new_name.strip():
                    self.rename_requested.emit(self.item, new_name.strip())
            elif chosen == delete:
                reply = QMessageBox.question(
                    self, "Delete chapter",
                    f'Delete "{self.name}"? This removes its images and translations.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.delete_requested.emit(self.item)
        else:
            remove = menu.addAction("Remove from list")
            if menu.exec(event.globalPos()) == remove:
                self.remove_requested.emit(self.item)