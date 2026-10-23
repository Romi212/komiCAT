from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QMenu, QInputDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal

CARD_SIZE = (130, 180)      # chapter thumbnail, width x height
COVER_SIZE = (150, 210)


def _load_pixmap(path, size):
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


class ChapterCard(QWidget):
    """Thumbnail + name. Left click opens, right click shows rename/delete."""
    open_requested = pyqtSignal(object)
    rename_requested = pyqtSignal(object, str)
    delete_requested = pyqtSignal(object)

    def __init__(self, chapter, thumb_path=None, parent=None):
        super().__init__(parent)
        self.chapter = chapter

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.thumb = QPushButton()
        self.thumb.setObjectName("chapterThumb")
        self.thumb.setFixedSize(*CARD_SIZE)
        self.thumb.setIconSize(QSize(*CARD_SIZE))
        self.thumb.setCursor(Qt.CursorShape.PointingHandCursor)
        pix = _load_pixmap(thumb_path, CARD_SIZE)
        if pix:
            self.thumb.setIcon(QIcon(pix))
        else:
            self.thumb.setText("No pages")
        self.thumb.clicked.connect(lambda: self.open_requested.emit(self.chapter))
        layout.addWidget(self.thumb)

        self.name_label = QLabel(chapter.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFixedWidth(CARD_SIZE[0])
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        rename = menu.addAction("Rename")
        delete = menu.addAction("Delete")
        chosen = menu.exec(event.globalPos())
        if chosen == rename:
            new_name, ok = QInputDialog.getText(self, "Rename chapter", "Name:",
                                                text=self.chapter.name)
            if ok and new_name.strip():
                self.rename_requested.emit(self.chapter, new_name.strip())
        elif chosen == delete:
            reply = QMessageBox.question(
                self, "Delete chapter",
                f'Delete "{self.chapter.name}"? This removes its images and translations.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_requested.emit(self.chapter)


class ProjectWindow(QWidget):
    chapter_opened = pyqtSignal(object)
    chapter_add_requested = pyqtSignal()
    chapter_rename_requested = pyqtSignal(object, str)
    chapter_delete_requested = pyqtSignal(object)
    termbase_requested = pyqtSignal()
    memory_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    delete_project_requested = pyqtSignal()

    def __init__(self, project, thumbnail_path, parent=None):
        super().__init__(parent)
        self.get_thumbnail = thumbnail_path
        self.project = project
        self.setWindowTitle(f"KomiCAT - {project.project_name}")
        self.resize(760, 520)

        root = QVBoxLayout(self)
        root.setSpacing(16)

        # ---------- header: cover + title + tools ----------
        header = QHBoxLayout()
        header.setSpacing(20)

        self.cover_label = QLabel("No cover")
        self.cover_label.setObjectName("coverPreview")
        self.cover_label.setFixedSize(*COVER_SIZE)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignTop)

        info = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("projectTitle")
        self.subtitle_label = QLabel()
        self.memory_btn = QPushButton("Translation Memory")
        self.termbase_btn = QPushButton("Termbase")
        self.memory_btn.clicked.connect(self.memory_requested)
        self.termbase_btn.clicked.connect(self.termbase_requested)
        info.addWidget(self.title_label)
        info.addWidget(self.subtitle_label)
        info.addSpacing(8)
        info.addWidget(self.memory_btn)
        info.addWidget(self.termbase_btn)
        info.addStretch()
        header.addLayout(info, 1)
        root.addLayout(header)

        # ---------- chapters strip:  <  [cards...] [+]  > ----------
        strip = QHBoxLayout()
        self.left_btn = QPushButton("<")
        self.right_btn = QPushButton(">")
        for b in (self.left_btn, self.right_btn):
            b.setFixedWidth(28)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.left_btn.clicked.connect(lambda: self._scroll(-1))
        self.right_btn.clicked.connect(lambda: self._scroll(1))

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(CARD_SIZE[1] + 50)
        bar = self.scroll.horizontalScrollBar()
        bar.valueChanged.connect(self._update_arrows)
        bar.rangeChanged.connect(self._update_arrows)

        strip.addWidget(self.left_btn)
        strip.addWidget(self.scroll, 1)
        strip.addWidget(self.right_btn)
        root.addLayout(strip)
        root.addStretch()

        # ---------- footer ----------
        footer = QHBoxLayout()
        self.delete_btn = QPushButton("Delete Project")
        self.delete_btn.setObjectName("dangerButton")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn.clicked.connect(self._confirm_delete_project)
        self.edit_btn.clicked.connect(self.edit_requested)
        footer.addStretch()
        #footer.addWidget(self.delete_btn)
        #footer.addWidget(self.edit_btn)
        footer.addStretch()
        root.addLayout(footer)

        self.refresh()

    # ---------- content ----------
    def refresh(self):
        """Rebuild everything from the project. Call after adding, renaming or deleting."""
        p = self.project
        self.title_label.setText(p.series_name)
        self.subtitle_label.setText(f"{p.project_name}  ·  {p.target_language.upper()}")
        self.setWindowTitle(f"KomiCAT - {p.project_name}")
        print(p.cover)
        pix = _load_pixmap(Path(p.path) / p.cover if p.cover else None, COVER_SIZE)
        if pix:
            self.cover_label.setPixmap(pix)
        else:
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("No cover")

        # chapter cards
        content = QWidget()
        row = QHBoxLayout(content)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(16)
        for chapter in p.chapters:
            card = ChapterCard(chapter, self._chapter_thumb(chapter))
            card.open_requested.connect(self.chapter_opened)
            card.rename_requested.connect(self.chapter_rename_requested)
            card.delete_requested.connect(self.chapter_delete_requested)
            row.addWidget(card, alignment=Qt.AlignmentFlag.AlignTop)

        add_btn = QPushButton("+")
        add_btn.setObjectName("addChapterButton")
        add_btn.setFixedSize(60, 60)
        add_btn.setToolTip("Add chapter")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.chapter_add_requested)
        row.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        row.addStretch()

        self.scroll.setWidget(content)
        self._update_arrows()

    def _chapter_thumb(self, chapter):
        rel = self.get_thumbnail(chapter)
        return Path(self.project.path) / rel if rel else None

    # ---------- scrolling ----------
    def _scroll(self, direction):
        bar = self.scroll.horizontalScrollBar()
        bar.setValue(bar.value() + direction * (CARD_SIZE[0] + 16) * 2)

    def _update_arrows(self, *_):
        bar = self.scroll.horizontalScrollBar()
        self.left_btn.setEnabled(bar.value() > bar.minimum())
        self.right_btn.setEnabled(bar.value() < bar.maximum())

    # ---------- project deletion ----------
    def _confirm_delete_project(self):
        reply = QMessageBox.warning(
            self, "Delete project",
            f'Delete "{self.project.project_name}" and all its chapters?\n'
            "This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_project_requested.emit()