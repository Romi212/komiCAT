from PyQt6.QtWidgets import QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent,  QTextCharFormat

class TranslationTextEdit(QTextEdit):

    def __init__(self, spell_checker=None, parent=None):
        super().__init__(parent)
        self.spell_checker = spell_checker

    """QTextEdit that ignores Tab and Shift+Tab to allow focus navigation"""
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            # Don't insert tab, let it propagate to parent for focus navigation
            event.ignore()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Let default double-click behavior run first so PyQt selects the word
        super().mouseDoubleClickEvent(event)
        
        if not self.spell_checker:
            return

        cursor = self.textCursor()
        selected_word = cursor.selectedText().strip()

        if not selected_word:
            return

        # Check if the clicked word is misspelled
        if not self.spell_checker.check_word(selected_word):
            suggestions = self.spell_checker.get_suggestions(selected_word)
            self._show_suggestions_menu(event.globalPosition().toPoint(), selected_word, suggestions, cursor)

    def _show_suggestions_menu(self, global_pos, word, suggestions, cursor):
        menu = QMenu(self)
        
        if suggestions:
            for correction in suggestions:
                action = menu.addAction(correction)
                # Connect action to replace the selected text with the correction
                action.triggered.connect(lambda checked, corr=correction, c=cursor: self._replace_word(c, corr))
        else:
            no_sugg = menu.addAction("No suggestions")
            no_sugg.setEnabled(False)

        menu.addSeparator()
        # Option to ignore or add to dictionary dynamically
        add_dict_action = menu.addAction(f"Add '{word}' to dictionary")
        add_dict_action.triggered.connect(lambda: self._add_to_dictionary(word))

        menu.exec(global_pos)

    def _replace_word(self, cursor, replacement):
        # Begin edit block for undo/redo history
        cursor.beginEditBlock()
        fmt = QTextCharFormat()
        fmt.setFontUnderline(False) 
        cursor.mergeCharFormat(fmt)
        cursor.insertText(replacement)
        cursor.endEditBlock()

    def _add_to_dictionary(self, word):
        if hasattr(self.spell_checker, 'add_custom_word'):
            self.spell_checker.add_custom_word(word)
            # Optionally re-trigger parent check_spelling if available
