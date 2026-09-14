from PyQt6.QtWidgets import QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent,  QTextCharFormat

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

class SourceTextEdit(QTextEdit):

    def __init__(self, jmdict=None, parent=None):
        super().__init__(parent)
        self.dictionary = jmdict
        self._popup = None

    """QTextEdit that ignores Tab and Shift+Tab to allow focus navigation"""
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            # Don't insert tab, let it propagate to parent for focus navigation
            event.ignore()
        else:
            super().keyPressEvent(event)

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

    
