from pathlib import Path

from PyQt6.QtWidgets import (
    QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QMenu, QInputDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QMenu, QInputDialog, QMessageBox, QFrame, QLineEdit, QComboBox, QFileDialog
)
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




# code -> display name. Extend as needed.
SOURCE_LANGUAGES = {"jp": "Japanese"}
TARGET_LANGUAGES = {"en": "English", "es": "Spanish"}
ALL_LANGUAGES = {**SOURCE_LANGUAGES, **TARGET_LANGUAGES}


def _lang_name(code):
    return ALL_LANGUAGES.get(code, code.upper())


def _language_combo(languages):
    combo = QComboBox()
    for code, name in languages.items():
        combo.addItem(name, code)
    return combo


def _select_language(combo, code):
    idx = combo.findData(code)
    if idx < 0:       # old project with a code not in the list: add it so nothing is lost
        combo.addItem(_lang_name(code), code)
        idx = combo.count() - 1
    combo.setCurrentIndex(idx)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class HScrollArea(QScrollArea):
    """Horizontal scroll panel; the mouse wheel scrolls sideways."""
    def wheelEvent(self, event):
        bar = self.horizontalScrollBar()
        delta = event.angleDelta().y() or event.angleDelta().x()
        bar.setValue(bar.value() - delta)
        event.accept()


class ProjectWindow(QWidget):
    chapter_opened = pyqtSignal(object)
    chapter_add_requested = pyqtSignal()
    chapter_rename_requested = pyqtSignal(object, str)
    chapter_delete_requested = pyqtSignal(object)
    termbase_requested = pyqtSignal()
    memory_requested = pyqtSignal()
    # dict: series_name, translated_title, source_language, target_language, cover_path ("" = unchanged)
    edit_requested = pyqtSignal(dict,str)
    delete_project_requested = pyqtSignal()
    close_project_requested = pyqtSignal()

    def __init__(self, project, thumbnail_path, parent=None):
        super().__init__(parent)
        self.get_thumbnail = thumbnail_path
        self.project = project
        self.editing = False
        self._pending_cover = None
        self.setWindowTitle(f"KomiCAT - {project.project_name}")
        self.resize(760, 520)

        root = QVBoxLayout(self)
        root.setSpacing(16)

        # ---------- header ----------
        header = QHBoxLayout()
        header.setSpacing(20)

        self.cover_label = ClickableLabel("No cover")
        self.cover_label.setObjectName("coverPreview")
        self.cover_label.setFixedSize(*COVER_SIZE)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.clicked.connect(self._choose_cover)
        header.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignTop)

        info = QVBoxLayout()

        self.title_label = QLabel()
        self.title_label.setObjectName("projectTitle")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Manga title")
        self.title_edit.hide()

        # translated title: only visible in view mode if it has text
        self.translated_label = QLabel()
        self.translated_label.setObjectName("projectSubtitle")
        self.translated_label.hide()
        self.translated_edit = QLineEdit()
        self.translated_edit.setPlaceholderText("Translated title (optional)")
        self.translated_edit.hide()

        self.lang_label = QLabel()
        self.source_combo = _language_combo(SOURCE_LANGUAGES)
        self.target_combo = _language_combo(TARGET_LANGUAGES)
        self.arrow_label = QLabel("→")
        lang_row = QHBoxLayout()
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.source_combo)
        lang_row.addWidget(self.arrow_label)
        lang_row.addWidget(self.target_combo)
        lang_row.addStretch()
        for w in (self.source_combo, self.arrow_label, self.target_combo):
            w.hide()

        self.memory_btn = QPushButton("Translation Memory")
        self.termbase_btn = QPushButton("Termbase")
        self.memory_btn.clicked.connect(self.memory_requested)
        self.termbase_btn.clicked.connect(self.termbase_requested)
        tools_row = QHBoxLayout()
        tools_row.addWidget(self.memory_btn)
        tools_row.addWidget(self.termbase_btn)
        tools_row.addStretch()

        info.addWidget(self.title_label)
        info.addWidget(self.title_edit)
        info.addWidget(self.translated_label)
        info.addWidget(self.translated_edit)
        info.addLayout(lang_row)
        info.addSpacing(8)
        info.addLayout(tools_row)
        info.addStretch()
        header.addLayout(info, 1)
        root.addLayout(header)

        # ---------- chapters: horizontal scroll panel ----------
        self.scroll = HScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setFixedHeight(CARD_SIZE[1] + 75)   # thumbnail + name + scrollbar
        root.addWidget(self.scroll)
        root.addStretch()

        # ---------- footer ----------
        footer = QHBoxLayout()
        self.delete_btn = QPushButton("Delete Project")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self._confirm_delete_project)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        self.cancel_btn.hide()
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        footer.addStretch()
        # footer.addWidget(self.delete_btn)
        footer.addWidget(self.cancel_btn)
        footer.addWidget(self.edit_btn)
        footer.addStretch()
        root.addLayout(footer)

        self.refresh()

    # ---------- content ----------
    def refresh(self):
        self._refresh_header()
        self._rebuild_chapters()

    def set_project(self, project):
        """Use if the manager creates a new Project object instead of mutating the old one."""
        self.project = project
        self.refresh()

    def _translated_title(self):
        return getattr(self.project, "translated_series_name", "") or ""

    def _refresh_header(self):
        p = self.project
        self.title_label.setText(p.series_name)
        translated = self._translated_title()
        self.translated_label.setText(translated)
        self.translated_label.setVisible(bool(translated) and not self.editing)
        self.lang_label.setText(
            f"{_lang_name(p.source_language)}  →  {_lang_name(p.target_language)}")
        self.setWindowTitle(f"KomiCAT - {p.project_name}")
        if not self.editing:
            self._show_cover(Path(p.path) / p.cover if p.cover else None)

    def _rebuild_chapters(self):
        content = QWidget()
        row = QHBoxLayout(content)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(16)
        for chapter in self.project.chapters:
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

        self.scroll.setWidget(content)   # replaces and deletes the previous content

    def _show_cover(self, path):
        pix = _load_pixmap(path, COVER_SIZE)
        if pix:
            self.cover_label.setPixmap(pix)
        else:
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("No cover")

    def _chapter_thumb(self, chapter):
        rel = self.get_thumbnail(chapter)
        return Path(self.project.path) / rel if rel else None

    # ---------- edit mode ----------
    def _set_editing(self, editing):
        self.editing = editing
        p = self.project

        if editing:
            self.title_edit.setText(p.series_name)
            self.translated_edit.setText(self._translated_title())
            _select_language(self.source_combo, p.source_language)
            _select_language(self.target_combo, p.target_language)
        else:
            self._pending_cover = None

        self.title_label.setVisible(not editing)
        self.title_edit.setVisible(editing)
        self.translated_edit.setVisible(editing)
        self.lang_label.setVisible(not editing)
        for w in (self.source_combo, self.arrow_label, self.target_combo):
            w.setVisible(editing)
        self.cancel_btn.setVisible(editing)
        self.edit_btn.setText("Save changes" if editing else "Edit")
        self.cover_label.setCursor(Qt.CursorShape.PointingHandCursor if editing
                                   else Qt.CursorShape.ArrowCursor)
        self.cover_label.setToolTip("Click to change the cover" if editing else "")

        # handles translated_label visibility, labels and cover
        self._refresh_header()

    def _on_edit_clicked(self):
        if self.editing:
            self._save_edit()
        else:
            self._set_editing(True)

    def _cancel_edit(self):
        self._set_editing(False)

    def _choose_cover(self):
        if not self.editing:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose cover image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path:
            self._pending_cover = path
            self._show_cover(path)

    def _save_edit(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Missing title", "The manga title can't be empty.")
            return
        source = self.source_combo.currentData()
        target = self.target_combo.currentData()
        if source == target:
            QMessageBox.warning(self, "Languages",
                                "Source and target language must be different.")
            return

        data = {
            "series_name": title,
            "translated_title": self.translated_edit.text().strip(),
            "source_language": source,
            "target_language": target,
        }
        new_cover = self._pending_cover
        self._set_editing(False)
        self.edit_requested.emit(data, new_cover)   # manager saves synchronously...
        self._refresh_header()           # ...then the header shows the saved values
        if new_cover:
            # Keep showing what the user picked. This guarantees the preview
            # changes even if the manager stores the cover under another name,
            # replaces the Project object, or overwrites the same filename.
            # The next refresh() redraws it from project.cover anyway.
            self._show_cover(new_cover)
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

    def closeEvent(self, event):
        self.close_project_requested.emit()
        event.ignore()