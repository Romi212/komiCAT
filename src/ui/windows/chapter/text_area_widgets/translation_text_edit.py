from PyQt6.QtWidgets import QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent,  QTextCharFormat, QTextCursor, QTextDocument

class TranslationTextEdit(QTextEdit):

    def __init__(self, spell_checker=None, parent=None):
        super().__init__(parent)
        self.spell_checker = spell_checker
        self.misspelled_words = []


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
        ignore_action = menu.addAction("Ignore spelling")
        ignore_action.triggered.connect(lambda: self._ignore_word(word))
        add_dict_action = menu.addAction(f"Add '{word}' to dictionary")
        add_dict_action.triggered.connect(lambda: self._add_to_dictionary(word))

        menu.exec(global_pos)

    @staticmethod
    def _no_underline(fmt):
        fmt.setFontUnderline(False)
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.NoUnderline)
        return fmt
    def _reset_underlines(self):
        """Set the whole document back to 'no underline' before re-marking."""
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(self._no_underline(QTextCharFormat()))

    def _clear_underline(self, word):
        """Remove the underline from every occurrence of `word` and forget it as misspelled."""
        flags = (QTextDocument.FindFlag.FindCaseSensitively
                 | QTextDocument.FindFlag.FindWholeWords)
        fmt = self._no_underline(QTextCharFormat())

        doc_cursor = QTextCursor(self.document())
        doc_cursor.beginEditBlock()
        found = self.document().find(word, 0, flags)
        while not found.isNull():
            found.mergeCharFormat(fmt)
            found = self.document().find(word, found, flags)
        doc_cursor.endEditBlock()

        self.misspelled_words = [w for w in self.misspelled_words if w != word]

    def add_misspelled_word(self, word):
        self.misspelled_words.append(word)
        
    def _replace_word(self, cursor, replacement):
        # Begin edit block for undo/redo history
        old_word = cursor.selectedText().strip()
        cursor.beginEditBlock()
        fmt = self._no_underline(cursor.charFormat())   # keep font etc., drop underline
        cursor.insertText(replacement, fmt)             # inserted text gets the clean format
        cursor.endEditBlock()
        self.misspelled_words = [w for w in self.misspelled_words if w != old_word]

    def _ignore_word(self, word):
        self.spell_checker.ignore_word(word)
        self._clear_underline(word)

    def _add_to_dictionary(self, word):
        if hasattr(self.spell_checker, 'add_custom_word'):
            self.spell_checker.add_custom_word(word)
        self._clear_underline(word)

    def correct_spelling(self):
        text = self.toPlainText().strip()
        if not text:
            return False
        for word in self.misspelled_words:
            if word in text:
                return False
            self.misspelled_words.remove(word)
        return True