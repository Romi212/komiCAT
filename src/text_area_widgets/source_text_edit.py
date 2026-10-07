from PyQt6.QtWidgets import QInputDialog, QLabel, QLineEdit, QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeyEvent,  QTextCharFormat, QTextCursor

from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeyEvent

class DictPopup(QWidget):
    """Floating popup container for displaying dictionary definitions."""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.browser = QTextBrowser(self)
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        
        # Style the popup square
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 6px;
            }
            QTextBrowser {
                border: none;
                background: transparent;
            }
        """)
        self.resize(320, 200)

    def show_definition(self, global_pos: QPoint, word,result):
        html_content = self._format_jmdict_result(word,result)
        self.browser.setHtml(html_content)
        # Position popup slightly below the double-clicked word
        self.move(global_pos + QPoint(0, 15))
        self.show()

    def _format_jmdict_result(self, word: str, result) -> str:
        """Formats Jamdict lookup entries into HTML for the QTextBrowser."""
        html_lines = [f"<h3 style='margin:0; color:#4a90e2;'>{word}</h3><hr/>"]
        
    
        for entry in result.entries:
            # FIX: Jamdict uses 'entry.kana', NOT 'entry.kana_forms'
            readings = ", ".join([r.text for r in getattr(entry, 'kana', [])])
            if readings:
                html_lines.append(f"<div><b>Reading:</b> {readings}</div>")
            
            # Senses / Definitions
            html_lines.append("<ol style='margin-left:-20px;'>")
            for sense in entry.senses:
                glosses = ", ".join([g.text for g in sense.gloss])
                pos = ", ".join([str(p) for p in sense.pos]) if sense.pos else ""
                pos_fmt = f" <i style='color:#aaa;'>({pos})</i>" if pos else ""
                html_lines.append(f"<li>{glosses}{pos_fmt}</li>")
            html_lines.append("</ol>")
        
        return "".join(html_lines)
class TermPopup(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)

    def show_term(self, global_pos, source_term, target_term):
        self.setText(f"{source_term} → {target_term}")
        self.adjustSize()
        self.move(global_pos + QPoint(10, 10))
        self.show()
class SourceTextEdit(QTextEdit):

    def __init__(self, jmdict=None, parent=None, termbase=None):
        super().__init__(parent)
        self.dictionary = jmdict
        self.termbase = termbase

        if self.termbase:
            self.termbase.panel.termbase_changed.connect(self.highlight_terms)

        self._popup = None
        self._term_matches = []
        self._hover_match = None

        self.setMouseTracking(True)
        self._term_popup = None

    def set_source_text(self, text):
        self.setPlainText(text)
        if self.termbase:
            self.highlight_terms()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        cursor = self.cursorForPosition(event.pos())
        pos = cursor.position()

        match = next(
            (m for m in self._term_matches if m[0] <= pos < m[1]),
            None
        )

        if match != self._hover_match:
            self._hover_match = match
            if match:
                self._show_term_popup(event.globalPosition().toPoint(), match)
            else:
                self._hide_term_popup()

    def leaveEvent(self, event):
        self._hover_match = None
        self._hide_term_popup()
        super().leaveEvent(event)

    def _show_term_popup(self, global_pos, match):
        start, end, source_term, target_term = match
        if self._term_popup is None:
            self._term_popup = TermPopup(self)
        self._term_popup.show_term(global_pos, source_term, target_term)

    def _hide_term_popup(self):
        if self._term_popup:
            self._term_popup.hide()
    """QTextEdit that ignores Tab and Shift+Tab to allow focus navigation
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            # Don't insert tab, let it propagate to parent for focus navigation
            event.ignore()
        else:
            super().keyPressEvent(event)"""

    def mouseReleaseEvent(self, event):
        # Let default double-click behavior run first so PyQt selects the word
        super().mouseReleaseEvent(event)
        # Only process on left-click release
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        if not self.dictionary:
            return

        cursor = self.textCursor()
        selected_word = cursor.selectedText().strip()

        if not selected_word:
            return

        entry = self.dictionary.lookup_jp(selected_word)
        if entry and entry.entries:
            cursor_rect = self.cursorRect(cursor)
            global_pos = self.viewport().mapToGlobal(cursor_rect.bottomLeft())
            self._show_entry_pop_up(global_pos, selected_word, entry)

    def _show_entry_pop_up(self, global_pos: QPoint, word, entry):
        # Re-use existing popup instance or create a new one
        if self._popup is None or not self._popup.isVisible():
            self._popup = DictPopup(self)
        self._popup.show_definition(global_pos, word, entry)

    def highlight_terms(self):
        text = self.toPlainText()
        self._term_matches = self.termbase.find_terms_in(text)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#6e2130"))
        fmt.setForeground(QColor("white"))

        # Clear previous term highlighting first
        clear_fmt = QTextCharFormat()
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(clear_fmt)

        for start, end, source_term, target_term in self._term_matches:
            cursor = QTextCursor(self.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)

    def remove_match(self, term_target):
        """Dims a term's highlight once the user has translated it correctly.
        term_target is the target_term (translation) associated with the match to dim."""
        matched = [m for m in self._term_matches if m[3] == term_target]
        if not matched:
            return

        dim_fmt = QTextCharFormat()
        dim_fmt.setBackground(QColor("transparent"))
        dim_fmt.setForeground(QColor())  # reset to default text color

        for start, end, source_term, target_term in matched:
            cursor = QTextCursor(self.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(dim_fmt)
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        cursor = self.textCursor()
        selected_word = cursor.selectedText().strip()

        if selected_word and self.termbase:
            menu.addSeparator()
            if self.termbase.source_in(selected_word):
                action = menu.addAction(f'"{selected_word}" already in termbase')
                action.setEnabled(False)
            else:
                action = menu.addAction(f'Add "{selected_word}" to termbase')
                action.triggered.connect(lambda: self._add_term(selected_word))

        menu.exec(event.globalPos())

    def _add_term(self, source_word):
        target_word, ok = QInputDialog.getText(
            self,
            "Add Termbase Entry",
            f'Translation for "{source_word}":',
            QLineEdit.EchoMode.Normal
        )
        if ok and target_word.strip():
            self.termbase.add_entry(source_word, target_word.strip())