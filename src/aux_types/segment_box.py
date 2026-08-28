from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QTextCursor, QTextCharFormat, QColor


class TabIgnoringTextEdit(QTextEdit):

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


class SegmentBox(QWidget):


    def __init__(self, spell_checker, logic_segment, initial_text_size=12):
        super().__init__()
        self.spell_checker = spell_checker
        self.on_focused = None  
        self.on_unfocused = None  
        self.segment = logic_segment
        self.text_size = initial_text_size
        self.initial_height = self.text_size * 2  

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        
        # TextEdit for Japanese text (editable)
        self.label = TabIgnoringTextEdit()
        self.label.setPlainText(self.segment.source_text)
        self.label.setReadOnly(False)
        self.label.setMinimumHeight(5)
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.label.textChanged.connect(self._adjust_label_height)
        self.label.focusInEvent = self._on_label_focus
        self.label.focusOutEvent = self._on_label_unfocus
        layout.addWidget(self.label)
        
        # Text area for translation
        self.text_area = TabIgnoringTextEdit(spell_checker=self.spell_checker)
        self.text_area.setMinimumHeight(5)
        self.text_area.setMaximumHeight(self.initial_height)
        self.text_area.setPlainText(self.segment.translation)
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.textChanged.connect(self._adjust_text_area_height)
        self.text_area.focusInEvent = self._on_text_area_focus
        self.text_area.focusOutEvent = self._on_text_area_unfocus  # Reuse unfocus for both
        layout.addWidget(self.text_area)
        
        # Set border style
        self.setStyleSheet("""
            SegmentBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                
                           
            }
        """)
        
        self.setLayout(layout)
        self.setMinimumHeight(5)
        
        # Adjust initial heights
        self._adjust_label_height()
    
    def set_japanese_text(self, text):
        self.label.setPlainText(text)
        self._adjust_label_height()
    
    def get_japanese_text(self):
        return self.label.toPlainText().strip()
    
    def get_translation(self):
        return self.text_area.toPlainText().strip()
    
    def set_translation(self, text):
        self.text_area.setPlainText(text)
        self._adjust_text_area_height()
    
    def _adjust_label_height(self):
        """Adjust label height to fit content"""
        doc_height = int(self.label.document().size().height())
        self.label.setMaximumHeight(max(20, min(doc_height + 4, 150)))
    
    def _adjust_text_area_height(self):
        """Adjust text_area height to fit content"""
        doc_height = int(self.text_area.document().size().height())
        self.text_area.setMaximumHeight(max(20, min(doc_height + 4, 200)))
    
    def _on_label_focus(self, event):
        self.segment.show_focus(True)
        QTextEdit.focusInEvent(self.label, event)


    def _on_label_unfocus(self, event):
        self.segment.show_focus(False)
        self.segment.source_text = self.get_japanese_text()
        print(f"Updated source text for segment {self.segment.nro}: {self.segment.source_text}")
        QTextEdit.focusOutEvent(self.label, event)
        

    def _on_text_area_focus(self, event):
        self.segment.show_focus(True)
        QTextEdit.focusInEvent(self.text_area, event)


    def _on_text_area_unfocus(self, event):
        self.segment.show_focus(False)
        
        QTextEdit.focusOutEvent(self.text_area, event)
        self.segment.translation = self.get_translation()
        print(f"Updated translation for segment {self.segment.nro}: {self.segment.translation}")
        self.check_spelling() 

    def zoom(self, new_size):
        self.text_size = new_size
        print(f"New text size: {self.text_size}")
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self._adjust_label_height()
        self._adjust_text_area_height()

    def check_spelling(self):
        if not self.get_translation().strip():  # Only check if there's text
            return
        """Check spelling of the translation text and highlight misspelled words."""
        text = self.get_translation()
        misspelled_words = self.spell_checker.get_misspelled_words(text)

        if misspelled_words:
            print(f"Misspelled words in segment {self.segment.nro}: {misspelled_words}")
 
            # Configure the underline format
            fmt = QTextCharFormat()
            fmt.setFontUnderline(True) 
            # Optional: Custom underline styling (like a red wavy spellcheck line)
            #fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            fmt.setUnderlineColor(QColor("red"))

            # Obtain document cursor
            doc = self.text_area.document()

            for word in misspelled_words:
                # Clear previous cursor adjustments and search from beginning
                cursor = QTextCursor(doc)
                while True:
                    # Find the next occurrence of the word
                    cursor = doc.find(word, cursor)
                    
                    # If no more matches are found, break loop
                    if cursor.isNull():
                        break
                        
                    # Apply formatting specifically to the matched cursor selection
                    cursor.mergeCharFormat(fmt)

            